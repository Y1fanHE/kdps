'''
Author: He,Yifan
Date: 2022-02-16 20:02:10
LastEditors: He,Yifan
LastEditTime: 2022-02-20 19:59:55
'''


from functools import partial
import os
import time
import numpy as np
import yaml
import sys

from pgsyn.gp.estimators import PushEstimator
from pgsyn.gp.genome import GeneSpawner
from pgsyn.knowledge.base import KnowledgeArchive
from pgsyn.push.config import PushConfig
from pgsyn.push.instruction_set import InstructionSet
from pgsyn.yaml_utils import register_yaml_constructors

from utils import erc_generator, load_psb
from utils import randchar, randfloat, randint, randbool, randstr
from utils import randinput_replace_space_with_newline


def get_psb(problem_filename):
    dat = yaml.unsafe_load(open(problem_filename))
    problem = dat.get("PROBLEM")
    problem_name = problem.get("name")
    path_to_root = problem.get("path_to_root")
    n_train_edge = problem.get("train").get("edge", 0)
    n_train_random = problem.get("train").get("random", 100)
    n_test_edge = problem.get("test").get("edge", 0)
    n_test_random = problem.get("test").get("random", 1000)
    io_types = problem.get("io_types")
    X_train, y_train = load_psb(problem_name, path_to_root, n_train_edge, n_train_random, io_types)
    X_test, y_test = load_psb(problem_name, path_to_root, n_test_edge, n_test_random, io_types)
    return X_train, y_train, X_test, y_test

def get_erc_generators(problem):
    methods = {
        "randint": randint,
        "randfloat": randfloat,
        "randchar": randchar,
        "randbool": randbool,
        "randinput_replace_space_with_newline": randinput_replace_space_with_newline,
    }
    erc_generators = []
    for key, value in problem.items():
        if key[:3] == "erc":
            possible_values = value.get("range", None)
            method_str = value.get("method")
            method = methods.get(method_str)
            erc_generators.append(partial(erc_generator, method, possible_values))
    return erc_generators

def get_spawner(problem):
    n_inputs = problem.get("n_inputs")
    stacks = problem.get("stacks", ["exec", "int", "bool", "float", "char", "str", "stdout"])
    spawner = GeneSpawner(
        n_inputs=n_inputs,
        instruction_set=InstructionSet().register_core_by_stack(set(stacks)),
        literals=problem.get("literals", []),
        erc_generators=get_erc_generators(problem),
    )
    return spawner

def get_knowledge_archive(problem, ka, name):
    kwargs = ka.get(name, {"mode": "empty"})
    knowledge_archive = KnowledgeArchive(spawner=get_spawner(problem), **kwargs)
    return knowledge_archive

def get_estimator(problem_filename, pushgp_filename):
    dat = yaml.unsafe_load(open(problem_filename))
    problem = dat.get("PROBLEM")
    ka = dat.get("KNOWLEDGE_ARCHIVE")
    dat = yaml.unsafe_load(open(pushgp_filename))
    pushgp = dat.get("PUSHGP")

    search = pushgp.get("search", "UMAD")
    last_str_from_stdout = problem.get("last_str_from_stdout", False)
    push_config = PushConfig(step_limit=problem.get("step_limit", 500),
                            runtime_limit=problem.get("runtime_limit", 10),
                            growth_cap=problem.get("growth_cap", 500),
                            collection_size_cap=problem.get("collection_size_cap", 1000),
                            numeric_magnitude_limit=problem.get("numeric_magnitude_limit", 1e12))
    interpreter = pushgp.get("interpreter", "default")
    verbose = pushgp.get("verbose", 2)
    spawner = get_spawner(problem)
    error_threshold = problem.get("error_threshold", 0)
    initial_genome_size = problem.get("initial_genome_size", [10, 50])
    max_genome_size = problem.get("max_genome_size")
    simplification_steps = problem.get("simplification_steps", 2000)
    kwargs = pushgp.get(search)
    kwargs.update({"knowledge_archive": get_knowledge_archive(problem, ka, kwargs.get("ka"))})
    est = PushEstimator(
        search=search,
        last_str_from_stdout=last_str_from_stdout,
        interpreter=interpreter,
        push_config=push_config,
        verbose=verbose,
        spawner=spawner,
        error_threshold = error_threshold,
        initial_genome_size = initial_genome_size,
        max_genome_size = max_genome_size,
        simplification_steps = simplification_steps,
        **kwargs
    )
    return est


if __name__ == "__main__":

    register_yaml_constructors()

    path_to_dir = os.getcwd()

    _, problem_yml, algorithm_yml = sys.argv
    if problem_yml[-4:] != ".yml":
        problem_yml += ".yml"
    if algorithm_yml[-4:] != ".yml":
        algorithm_yml += ".yml"

    est = get_estimator(path_to_dir+"/problem_cfg/"+problem_yml,
                        path_to_dir+"/algorithm_cfg/"+algorithm_yml)

    X_train, y_train, X_test, y_test = get_psb(path_to_dir+"/problem_cfg/"+problem_yml)

    start = time.time()
    est.fit(X=X_train, y=y_train)
    end = time.time()
    print("========================================")
    print("post-evolution stats")
    print("========================================")
    print("Runtime: ", end - start)
    print("Test Error: ", np.sum(est.score(X_test, y_test)))
