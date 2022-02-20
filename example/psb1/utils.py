'''
Author: He,Yifan
Date: 2022-02-17 01:06:47
LastEditors: He,Yifan
LastEditTime: 2022-02-21 00:12:09
'''


from random import choice
from typing import Callable
import numpy.random as random
import pandas as pd

from pgsyn.push.types import Char, IntVector, BoolVector, FloatVector, CharVector, StrVector


def randint(possible_values):
    possible_values_ = [possible_values[0], possible_values[1]+1]
    return int(random.randint(*possible_values_))

def randbool(possible_values=None):
    return bool(random.randint(0, 2))

def randfloat(possible_values):
    return float(random.uniform(*possible_values))

def randchar(possible_values):
    idx = random.choice(len(possible_values))
    return Char(possible_values[idx])

def randstr(possible_values):
    idx = random.choice(len(possible_values))
    return possible_values[idx]

def randinput_replace_space_with_newline(possible_values=None):
    """
    The input string will not have tabs or newlines, but may have multiple
    spaces in a row. It will have maximum length of 20 characters.
    """
    possible_values_ = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    length = random.randint(1, 21)
    input_str = ""
    for _ in range(length):
        if random.random() < 0.2:
            input_str += " "
        else:
            input_str += possible_values_[random.choice(len(possible_values_))]
    return input_str

def erc_generator(method, possible_values, type_of_value: Callable = None):
    if type_of_value:
        return type_of_value(method(possible_values))
    else:
        return method(possible_values)

def load_psb(problem_name, path_to_dir, n_edge, n_random, io_types=None):
    path_to_random = f"{path_to_dir}/{problem_name}/{problem_name}-random.csv"
    path_to_edge = f"{path_to_dir}/{problem_name}/{problem_name}-edge.csv"
    df_edge = pd.read_csv(path_to_edge).sample(n=n_edge) if n_edge else pd.DataFrame()
    df_random = pd.read_csv(path_to_random).sample(n=n_random) if n_random else pd.DataFrame()
    df = pd.concat([df_edge, df_random])
    for io, type_ in io_types.items():
        if type_ in ["int", "bool", "float", "str"]:
            df = df.astype({io:type_})
        elif type_ == "char":
            df[io] = pd.Series([Char(item) for item in df[io]])
        elif type_ == "vector_int":
            df[io] = pd.Series([IntVector(item) for item in df[io]])
        elif type_ == "vector_bool":
            df[io] = pd.Series([BoolVector(item) for item in df[io]])
        elif type_ == "vector_float":
            df[io] = pd.Series([FloatVector(item) for item in df[io]])
        elif type_ == "vector_char":
            df[io] = pd.Series([CharVector(item) for item in df[io]])
        elif type_ == "vector_str":
            df[io] = pd.Series([StrVector(item) for item in df[io]])
        else:
            raise Exception(f"Cannot find a proper PushType for tag {type_}.")

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


