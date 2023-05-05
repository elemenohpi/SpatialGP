from abc import ABC, abstractmethod


class AbstractPrograms(ABC):
    def __init__(self, config) -> None:
        pass

    @abstractmethod
    def generate(self):
        pass
