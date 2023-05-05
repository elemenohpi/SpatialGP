from abc import ABC, abstractmethod 


class AbstractPopulation(ABC):
    def __init__(self, config, individual_class, programs_class) -> None:
        pass

    @abstractmethod
    def generate_population(self):
        pass
