import sys

from Operators.AbstractOperator import AbstractOperator


class OP_MOST_FREQUENT_VIAL(AbstractOperator):
    def __init__(self):
        super().__init__()
        pass

    def eval(self, game):
        return game.get_most_frequent_vial()

    @staticmethod
    def op_code():
        code = """
# returns a vial with the most frequent color  
def op_most_frequent_vial(game):
\treturn game.get_most_frequent_vial() 
"""
        return code

    def demands(self):
        return [
            "game",
        ]

    def products(self):
        return ["float"]

    def name(self):
        return "OP_MOST_FREQUENT_VIAL"

    def annotation(self):
        return "{} = op_most_frequent_vial({})"
