import math
from Interpreter.AbstractInterpreter import AbstractInterpreter
import copy

# compatibility_dict = {
#     float: [int, float],
# }


class BaseInterpreter(AbstractInterpreter):
    def modelize(self, individual):
        pass

    def __init__(self, config) -> None:
        super().__init__(config)

