'''
Author: He,Yifan
Date: 2022-02-18 16:06:00
LastEditors: He,Yifan
LastEditTime: 2022-02-18 16:31:37
'''


from pgsyn.push.instruction import SimpleInstruction
from pgsyn.push.type_library import PushTypeLibrary


# Printing instructions

def _wrap(x):
    return str(x),


def _wrap_and_newline(x):
    return str(x) + "\n",


def instructions(type_library: PushTypeLibrary):
    """Return all core printing instructions."""
    i = []

    for push_type in type_library.keys():
        i.append(SimpleInstruction(
            "print_{t}".format(t=push_type),
            _wrap,
            input_stacks=[push_type],
            output_stacks=["stdout"],
            code_blocks=0,
            docstring="Prints the top {t}.".format(t=push_type)
        )),
        i.append(SimpleInstruction(
            "println_{t}".format(t=push_type),
            _wrap_and_newline,
            input_stacks=[push_type],
            output_stacks=["stdout"],
            code_blocks=0,
            docstring="Prints the top {t}.".format(t=push_type)
        ))
    return i
