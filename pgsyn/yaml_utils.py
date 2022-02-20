'''
Author: He,Yifan
Date: 2022-02-20 14:07:19
LastEditors: He,Yifan
LastEditTime: 2022-02-20 15:00:37
'''

import yaml

from pgsyn.push.atoms import Closer, Input, InstructionMeta
from pgsyn.push.instructions import core_instructions
from pgsyn.push.type_library import PushTypeLibrary
from pgsyn.push.types import Char

def get_instruction_by_str(s: str):
    for i in core_instructions(PushTypeLibrary()):
        if s == i.name:
            return InstructionMeta(name=i.name, code_blocks=i.code_blocks)

def closer_constructor(loader, node):
    return Closer()

def char_constructor(loader, node):
    char = loader.construct_scalar(node)
    return Char(char)

def visible_constructor(loader, node):
    return '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

def visible_plus_constructor(loader, node):
    return '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\n\t'

def instructionmeta_constructor(loader, node):
    name = loader.construct_scalar(node)
    return get_instruction_by_str(name)

def input_constructor(loader, node):
    input_index = int(loader.construct_scalar(node))
    return Input(input_index=input_index)

def register_yaml_constructors():
    yaml.add_constructor(Closer.yaml_tag, closer_constructor)
    yaml.add_constructor(Char.yaml_tag, char_constructor)
    yaml.add_constructor(u"!visible", visible_constructor)
    yaml.add_constructor(u"!visible+", visible_plus_constructor)
    yaml.add_constructor(InstructionMeta.yaml_tag, instructionmeta_constructor)
    yaml.add_constructor(Input.yaml_tag, input_constructor)
