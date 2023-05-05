from abc import ABC, abstractmethod


class AbstractInterpreter(ABC):
    def __init__(self, config) -> None:
        super().__init__()

    @abstractmethod
    def modelize(self, individual):
        pass

    