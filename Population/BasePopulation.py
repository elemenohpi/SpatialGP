import os
import pickle

from Population.AbstractPopulation import AbstractPopulation


class BasePopulation(AbstractPopulation):
    def __init__(self, config, individual_class, programs_class) -> None:
        super().__init__(config, individual_class, programs_class)
        self.pop = None
        self.individual_class = individual_class
        self.config = config
        self.programs_class = programs_class
        self.generation = -1

    def generate_population(self):
        pop_size = int(self.config["population_size"])
        self.pop = []
        for i in range(pop_size):
            individual = self.individual_class(self.config, self.programs_class)
            individual.init_random()
            individual.individual_index = i
            self.pop.append(individual)

    def load_population(self):
        print("Checkpointing is ON. Attempting to load an existing population.")
        pop_size = int(self.config["population_size"])
        pop_save_path = self.config["pop_save_path"]
        self.pop = []
        for i in range(pop_size):
            potential_file_path = os.path.join(pop_save_path, f"model_{i}.sgp")
            if os.path.exists(potential_file_path):
                with open(potential_file_path, "rb") as pickled_file:
                    loaded_individual = pickle.load(pickled_file)
                print(f"Individual {potential_file_path} was successfully loaded.")
                self.pop.append(loaded_individual)
                pass
            else:
                print(f"WARNING: {potential_file_path} does not exist and therefore is randomly initialized.")
                individual = self.individual_class(self.config, self.programs_class)
                individual.init_random()
                individual.individual_index = i
                self.pop.append(individual)

