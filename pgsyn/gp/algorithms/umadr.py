'''
Author: He,Yifan
Date: 2022-02-17 21:09:40
LastEditors: He,Yifan
LastEditTime: 2022-02-18 20:55:30
'''


from typing import Optional, Tuple, Union

from pgsyn.gp.algorithms.base import SearchAlgorithm
from pgsyn.gp.evaluation import Evaluator
from pgsyn.gp.genome import GeneSpawner
from pgsyn.gp.individual import Individual
from pgsyn.gp.population import Population
from pgsyn.gp.selection import Selector
from pgsyn.gp.variation import VariationPipeline, AdditionMutation, DeletionMutation, ReplacementMutation
from pgsyn.knowledge.base import KnowledgeArchive
from pgsyn.push.program import ProgramSignature
from pgsyn.utils import DiscreteProbDistrib
from pgsyn.tap import tap


class UMADR(SearchAlgorithm):
    """Uniform Mutation by Addition and Deletion with Replacement Mutation

    INPUT: initial population X_0, knowledge archive K

    FOR t = 0 to t_max
        X_t+1 = {}
        FOR i = 1 to |X_t|
            p_i = lexicase_selection(X_t)
            o_i = addition_mutation(p_i, addition_rate)
            o_i = deletion_mutation(o_i, deletion_rate)
            k_i = random_selection(K)
            o_i = replacement_mutation(o_i, k_i, replacement_rate)
            X_t+1 = X_t+1 U {o_i}

    """

    def __init__(self,
                 signature: ProgramSignature,
                 evaluator: Evaluator,
                 spawner: GeneSpawner,
                 knowledge_archive: KnowledgeArchive = KnowledgeArchive(mode="empty"),
                 selection: Union[Selector, DiscreteProbDistrib, str] = "lexicase",
                 addition_rate: float = 0.09,
                 deletion_rate: float = 0.0826,
                 replacement_rate: float = 0.1,
                 population_size: int = 500,
                 max_generations: int = 100,
                 error_threshold: float = 0.0,
                 initial_genome_size: Tuple[int, int] = (10, 50),
                 max_genome_size: Optional[int] = None,
                 simplification_steps: int = 2000,
                 parallelism: Union[int, bool] = True,
                 **kwargs):

        super().__init__(
            signature=signature,
            evaluator=evaluator,
            spawner=spawner,
            population_size=population_size,
            max_generations=max_generations,
            error_threshold=error_threshold,
            initial_genome_size=initial_genome_size,
            max_genome_size=max_genome_size,
            simplification_steps=simplification_steps,
            parallelism=parallelism,
            **kwargs
        )

        self.knowledge_archive = knowledge_archive
        self.selection = selection
        self.variation = "umadr"
        self.selector = self.get_selector(selection)
        self.addition_rate = addition_rate
        self.deletion_rate = deletion_rate
        self.replacement_rate = replacement_rate
        self.op_umad = self.get_variation_op(VariationPipeline([
            AdditionMutation(addition_rate),
            DeletionMutation(deletion_rate)
        ]))
        self.op_r = self.get_variation_op(
            ReplacementMutation(replacement_rate)
        )

    def _make_child(self) -> Individual:
        parent_genomes = [p.genome for p in self.selector.select(self.population, n=self.op_umad.num_parents)]
        child_genome = self.op_umad.produce(parent_genomes,
                                            self.spawner,
                                            max_genome_size=self.max_genome_size)
        parent_genomes = [child_genome]
        child_genome = self.op_r.produce(parent_genomes,
                                         self.spawner,
                                         knowledge_archive=self.knowledge_archive,
                                         max_genome_size=self.max_genome_size)
        return Individual(child_genome, self.signature)

    @tap
    def step(self):
        """Perform one generation (step) of the genetic algorithm.

        The step method assumes an evaluated Population and performs parent
        selection and variation (producing children).

        """
        super().step()
        self.population = Population(
            [self._make_child() for _ in range(self.population_size)]
        )
