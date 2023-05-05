from abc import ABC, abstractmethod


class AbstractIndividual(ABC):
    def __init__(self, config, programs_class) -> None:
        self.fitness = 0
        pass

    @abstractmethod
    def init_random(self):
        pass
    pass

    @abstractmethod
    def individual_eval(self, inputs):
        pass
    pass