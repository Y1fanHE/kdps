'''
Author: He,Yifan
Date: 2022-02-17 19:35:51
LastEditors: He,Yifan
LastEditTime: 2022-02-20 15:18:54
'''


from typing import Sequence, Union
import numpy as np
from numpy.random import randint

from pgsyn.gp.genome import Genome
from pgsyn.push.atoms import Closer, Input, InstructionMeta
from pgsyn.push.type_library import PushTypeLibrary, infer_literal
from pgsyn.push.types import BoolVector, Char, CharVector, FloatVector, IntVector, StrVector


def from_yaml(yml: Sequence):
    genome = Genome()
    for item in yml:
        if isinstance(item, (Closer, InstructionMeta, Input)):
            gene = item
        elif isinstance(item, (str, int, float, bool, Char)):
            gene = infer_literal(val=item, type_library=PushTypeLibrary())
        elif isinstance(item, Sequence):
            if all([isinstance(sub_item, int) for sub_item in item]):
                gene = infer_literal(val=IntVector(item), type_library=PushTypeLibrary())
            elif all([isinstance(sub_item, bool) for sub_item in item]):
                gene = infer_literal(val=BoolVector(item), type_library=PushTypeLibrary())
            elif all([isinstance(sub_item, float) for sub_item in item]):
                gene = infer_literal(val=FloatVector(item), type_library=PushTypeLibrary())
            elif all([isinstance(sub_item, Char) for sub_item in item]):
                gene = infer_literal(val=CharVector(item), type_library=PushTypeLibrary())
            elif all([isinstance(sub_item, str) for sub_item in item]):
                gene = infer_literal(val=StrVector(item), type_library=PushTypeLibrary())
            else:
                raise Exception(f"Cannot find PushType for token {item}.")
        genome = genome.append(gene)
    return genome


class KnowledgeArchive:
    """Knowledge Archive.
    
    """

    def __init__(self,
                 mode: Union[str, bool] = "incode",
                 **kwargs):
        self.genome_set = []
        if not mode:
            self.genome_set = [Genome()]
        elif mode == "empty":
            self.genome_set = [Genome()]
        elif mode == "file":
            self.genome_set = np.load(kwargs.get("path"), allow_pickle=True)
        elif mode == "incode":
            self.genome_set = kwargs.get("genome_set")
        elif mode == "yaml":
            self.genome_set = [from_yaml(i) for i in kwargs.get("genome_set")]
        elif mode == "random":
            self.spawner = kwargs.get("spawner")
            min_genome_length, max_genome_length = kwargs.get("genome_length")
            genome_set_size = kwargs.get("genome_set_size")
            self.genome_set = self.random_genome_set(genome_set_size, min_genome_length, max_genome_length)
        else:
            pass

    def spawn_genome(self):
        return self.genome_set[randint(0, len(self.genome_set))]

    def random_genome_set(self, genome_set_size: int, min_genome_length: int, max_genome_length: int):
        genome_set = []
        for _ in range(genome_set_size):
            genome_length = randint(min_genome_length, max_genome_length+1)
            genome = self.spawner.spawn_genome(size=genome_length)
            genome_set.append(genome)
        return genome_set

    @property
    def pretty_str(self):
        lst = [str(genome) for genome in self.genome_set]
        return "\n".join(lst)
