'''
Author: He,Yifan
Date: 2022-02-17 01:06:47
LastEditors: He,Yifan
LastEditTime: 2022-02-19 21:57:06
'''


from typing import Callable
import numpy.random as random
import pandas as pd

from pgsyn.push.types import Char


def randchar(possible_values):
    idx = random.choice(len(possible_values))
    return Char(possible_values[idx])

def randint(possible_values):
    possible_values_ = [possible_values[0], possible_values[1]+1]
    return int(random.randint(*possible_values_))

def randfloat(possible_values):
    return float(random.uniform(*possible_values))

def erc_generator(possible_values, method, type_of_value: Callable = None):
    if type_of_value:
        return type_of_value(method(possible_values))
    else:
        return method(possible_values)

def load_psb(problem_name, path_to_dir, n_edge, n_random, output_types=None):
    path_to_random = f"{path_to_dir}/{problem_name}/{problem_name}-random.csv"
    path_to_edge = f"{path_to_dir}/{problem_name}/{problem_name}-edge.csv"
    df_edge = pd.read_csv(path_to_edge).sample(n=n_edge) if n_edge else pd.DataFrame()
    df_random = pd.read_csv(path_to_random).sample(n=n_random) if n_random else pd.DataFrame()
    df = pd.concat([df_edge, df_random])
    if output_types:
        df = df.astype(output_types)
    input_cols = []
    output_cols = []
    for col in df.columns:
        if "input" in col:
            input_cols.append(col)
        elif "output" in col:
            output_cols.append(col)
    inputs = df[input_cols]
    outputs = df[output_cols]
    return inputs, outputs


