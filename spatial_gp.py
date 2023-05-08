import random

from eletility import Files
from eletility import Log
from eletility import Times


class SpatialGP:
    def __init__(self, config):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the initial state of an object.


    :param self: Represent the instance of the class
    :param config: Configure the system
    :return: Nothing
    :doc-author: Trelent
    """
        self.evolver = None
        self.evolver_class = None
        self.fitness_class = None
        self.interpreter_class = None
        self.population_class = None
        self.individual_class = None
        self.programs_class = None

        # configuring the program
        self.config = config

        # configure the random seed
        seed = int(config["seed"])
        random.seed(seed)

        # handlers
        self.Files = Files()
        self.Times = Times()

        # initialize the system
        self.init_system(config)

    def init_system(self, config):
        # config
        """
    The init_system function is used to initialize the system.
    It takes a dictionary as an argument, which contains all of the information needed to create each class.
    The function then imports each module and creates an instance of that class.

    :param self: Refer to the object itself
    :param config: Pass in the configuration file
    :return: Nothing
    :doc-author: Trelent
    """
        individual = config["individual"]
        population = config["population"]
        interpreter = config["interpreter"]
        fitness = config["fitness"]
        evolver = config["evolver"]
        programs = config["programs"]

        # Individual
        module = __import__("Individual." + individual)
        self.individual_class = getattr(getattr(module, individual), individual)
        # Population
        module = __import__("Population." + population)
        self.population_class = getattr(getattr(module, population), population)
        # Programs
        module = __import__("Programs." + programs)
        self.programs_class = getattr(getattr(module, programs), programs)
        # Interpreter
        module = __import__("Interpreter." + interpreter)
        self.interpreter_class = getattr(getattr(module, interpreter), interpreter)
        # Fitness
        module = __import__("Fitness." + fitness)
        tokens = fitness.split(".")
        if len(tokens) > 1:
            my_class = tokens[1]
            directory = tokens[0]
            temp_module = getattr(getattr(module, directory), my_class)
            self.fitness_class = getattr(temp_module, my_class)
        else:
            self.fitness_class = getattr(getattr(module, fitness), fitness)
        # Evolver
        module = __import__("Evolver." + evolver)
        self.evolver_class = getattr(getattr(module, evolver), evolver)

    def run(self):
        start_time = self.Times.now()

        pop_obj = self.population_class(self.config, self.individual_class, self.programs_class)
        fitness_obj = self.fitness_class()
        interpreter_obj = self.interpreter_class(self.config)

        pop_obj.generate_population()
        evolver_obj = self.evolver_class(self.config, pop_obj, fitness_obj, interpreter_obj)

        best_fitness = evolver_obj.run()
        print("manual exit")
        exit()
        end_time = self.Times.now()

        # return best_fitness
