from abc import ABC, abstractmethod


class AbstractPrograms(ABC):
    def __init__(self, config) -> None:
        self.pos = None
        # discrete_output is only set if the system is working with discrete outputs. Otherwise, this is ignored
        self.discrete_output = None
        pass

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def cost(self, pos, memory):
        pass
