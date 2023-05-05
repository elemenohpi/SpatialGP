from Evolver.AbstractEvolver import AbstractEvolver


class BaseEvolver(AbstractEvolver):
    def __init__(self, config, pop_obj, fitness_obj, interpreter_obj) -> None:
        super().__init__(config, pop_obj, fitness_obj, interpreter_obj)
        self.pop = None
        self.pop_obj = pop_obj
        self.config = config
        self.runs = int(self.config["generations"])
        self.fitness_obj = fitness_obj
        self.interpreter_obj = interpreter_obj
        self.tournament_size = int(self.config["tournament_size"])
        self.elitism = int(self.config["elitism"])

    def run(self):
        raise NotImplementedError("not implemented")
        pass
