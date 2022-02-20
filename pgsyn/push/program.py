'''
Author: He,Yifan
Date: 2022-02-18 16:06:00
LastEditors: He,Yifan
LastEditTime: 2022-02-18 16:35:56
'''


from pyrsistent import PRecord, field

from pgsyn.push.config import PushConfig
from pgsyn.push.atoms import CodeBlock
from pgsyn.utils import Saveable


class ProgramSignature(PRecord):
    """A specification of a Push program.

    Attributes
    ----------
    arity : int
        The number of inputs that the program will take.
    output_stacks : List[str]
        The names of the stack(s) which the output values will be pulled from after program execution.
    push_config : PushConfig
        The configuration of the PushInterpreter to use when executing the program.

    """

    arity = field(type=int, mandatory=True)
    output_stacks = field(type=list, mandatory=True)
    push_config = field(type=PushConfig, mandatory=True, initial=PushConfig())


class Program(Saveable, PRecord):
    """A Push program containing all information needed to run the code with consistent behavior.

    Attributes
    ----------
    code : CodeBlock
        The Push code expressing the logic of the program.
    signature : ProgramSignature
        The specification of the program and the configuration of the Push interpreter that it was evolved under.

    """

    code = field(type=CodeBlock, mandatory=True)
    signature = field(type=ProgramSignature, mandatory=True)

    def pretty_str(self) -> str:
        """Generate a simple string representation of the program's code."""
        return self.code.pretty_str()
