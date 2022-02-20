'''
Author: He,Yifan
Date: 2022-02-16 20:52:46
LastEditors: He,Yifan
LastEditTime: 2022-02-18 20:40:58
'''


from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional

from functools import partial
from multiprocessing import Pool, Manager

from pgsyn.gp.evaluation import Evaluator
from pgsyn.gp.genome import GeneSpawner, GenomeSimplifier
from pgsyn.gp.individual import Individual
from pgsyn.gp.population import Population
from pgsyn.gp.selection import Selector, get_selector
from pgsyn.gp.variation import VariationOperator, get_variation_operator
from pgsyn.push.program import ProgramSignature
from pgsyn.utils import DiscreteProbDistrib
from pgsyn.tap import tap


class ParallelContext:
    """Holds the objects needed to coordinate parallelism."""

    def __init__(self,
                 spawner: GeneSpawner,
                 evaluator: Evaluator,
                 n_proc: Optional[int] = None):
        self.manager = Manager()
        self.ns = self.manager.Namespace()
        self.ns.spawner = spawner
        self.ns.evaluator = evaluator
        self.pool = None
        if n_proc is None:
            self.pool = Pool()
        else:
            self.pool = Pool(n_proc)

    def close(self):
        if self.pool is not None:
            self.pool.close()


def _spawn_individual(spawner, genome_size, program_signature: ProgramSignature, *args):
    return Individual(spawner.spawn_genome(genome_size), program_signature)


class SearchAlgorithm(ABC):
    """Base class for all search algorithms.

    Parameters
    ----------
    config : SearchConfiguration
        The configuration of the search algorithm.

    Attributes
    ----------
    config : SearchConfiguration
        The configuration of the search algorithm.
    generation : int
        The current generation, or iteration, of the search.
    best_seen : Individual
        The best Individual, with respect to total error, seen so far.
    population : Population
        The current Population of individuals.

    """

    def __init__(self,
                 signature: ProgramSignature,
                 evaluator: Evaluator,
                 spawner: GeneSpawner,
                 population_size: int = 500,
                 max_generations: int = 100,
                 error_threshold: float = 0.0,
                 initial_genome_size: Tuple[int, int] = (10, 50),
                 max_genome_size: int = None,
                 simplification_steps: int = 2000,
                 parallelism: Union[int, bool] = True,
                 **kwargs):
        self.signature = signature
        self.evaluator = evaluator
        self.spawner = spawner
        self.population_size = population_size
        self.max_generations = max_generations
        self.error_threshold = error_threshold
        self.initial_genome_size = initial_genome_size
        self.max_genome_size = max_genome_size
        self.simplification_steps = simplification_steps
        self.ext = kwargs

        self._p_context = self.get_parallel_context(parallelism, spawner, evaluator)
        self.generation = 0
        self.best_seen = None
        self.population = None
        self.init_population()

    def get_parallel_context(self, parallelism, spawner, evaluator):
        self.parallel_context = None
        if isinstance(parallelism, bool):
            if parallelism:
                self.parallel_context = ParallelContext(spawner, evaluator)
        elif parallelism > 1:
            self.parallel_context = ParallelContext(spawner, evaluator, parallelism)
        return self.parallel_context

    def get_selector(self, selection, **kwargs):
        if isinstance(selection, Selector):
            return DiscreteProbDistrib().add(selection, 1.0).sample()
        elif isinstance(selection, DiscreteProbDistrib):
            return selection.sample()
        else:
            selector = get_selector(selection, **kwargs)
            return DiscreteProbDistrib().add(selector, 1.0).sample()

    def get_variation_op(self, variation, **kwargs):
        if isinstance(variation, VariationOperator):
            return DiscreteProbDistrib().add(variation, 1.0).sample()
        elif isinstance(variation, DiscreteProbDistrib):
            return variation.sample()
        else:
            variation_op = get_variation_operator(variation, **kwargs)
            return DiscreteProbDistrib().add(variation_op, 1.0).sample()

    def init_population(self):
        """Initialize the population."""
        spawner = self.spawner
        init_gn_size = self.initial_genome_size
        pop_size = self.population_size
        signature = self.signature
        self.population = Population()
        if self._p_context is not None:
            gen_func = partial(_spawn_individual, self._p_context.ns.spawner, init_gn_size, signature)
            for indiv in self._p_context.pool.imap_unordered(gen_func, range(pop_size)):
                self.population.add(indiv)
        else:
            for i in range(pop_size):
                self.population.add(_spawn_individual(spawner, init_gn_size, signature))

    @tap
    @abstractmethod
    def step(self) -> bool:
        """Perform one generation (step) of the search.

        The step method should assume an evaluated Population, and must only
        perform parent selection and variation (producing children). The step
        method should modify the search algorithms population in-place, or
        assign a new Population to the population attribute.

        """
        pass

    def _full_step(self) -> bool:
        self.generation += 1
        if self._p_context is not None:
            self.population.p_evaluate(self._p_context.ns.evaluator, self._p_context.pool)
        else:
            self.population.evaluate(self.evaluator)

        best_this_gen = self.population.best()
        if self.best_seen is None or best_this_gen.total_error < self.best_seen.total_error:
            self.best_seen = best_this_gen
            if self.best_seen.total_error <= self.error_threshold:
                return False

        self.step()
        return True

    def is_solved(self) -> bool:
        """Return ``True`` if the search algorithm has found a solution or ``False`` otherwise."""
        return self.best_seen.total_error <= self.error_threshold

    @tap
    def run(self) -> Individual:
        """Run the algorithm until termination."""
        while self._full_step():
            if self.generation >= self.max_generations:
                break

        # Simplify the best individual for a better generalization and interpretation.
        simplifier = GenomeSimplifier(
            self.evaluator,
            self.signature
        )
        simp_genome, simp_error_vector = simplifier.simplify(
            self.best_seen.genome,
            self.best_seen.error_vector,
            self.simplification_steps
        )
        simplified_best = Individual(simp_genome, self.signature)
        simplified_best.error_vector = simp_error_vector
        self.best_seen = simplified_best
        return self.best_seen

    def tear_down(self):
        if self.parallel_context is not None:
            self.parallel_context.close()
