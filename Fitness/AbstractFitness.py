from abc import ABC, abstractmethod


class AbstractFitness(ABC):
    def __init__(self) -> None:
        pass

    def preprocess(self, indv):
        pass
    
    @abstractmethod
    def evaluate(self, indv):
        return -1

    def postprocess(self, indv):
        pass

    @abstractmethod
    def inputs(self):
        pass

    @abstractmethod
    def outputs(self):
        pass

    @abstractmethod
    def settings(self):
        pass
