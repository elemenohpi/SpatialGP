from Population.AbstractPopulation import AbstractPopulation


class BasePopulation(AbstractPopulation):
    def __init__(self, config, individual_class, programs_class) -> None:
        super().__init__(config, individual_class, programs_class)
        self.pop = None
        self.individual_class = individual_class
        self.config = config
        self.programs_class = programs_class

    def generate_population(self):
        pop_size = int(self.config["population_size"])
        self.pop = []
        for i in range(pop_size):
            individual = self.individual_class(self.config, self.programs_class)
            individual.init_random()
            individual.individual_index = i
            self.pop.append(individual)
