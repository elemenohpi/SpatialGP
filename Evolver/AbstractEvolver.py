from abc import abstractmethod, ABC


class AbstractEvolver(ABC):
    def __init__(self, config, pop_obj, fitness_obj, interpreter_obj):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def crossover(self, a, b):
        pass
