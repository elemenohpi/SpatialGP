import math
import random

from Individual.AbstractIndividual import AbstractIndividual
from Handlers.ConfigHandler import ConfigHandler


class BaseIndividual(AbstractIndividual):
    def __init__(self, config, programs_class):
        super().__init__(config, programs_class)
        self.config = config
        self.programs_class = programs_class
        self.init_size_min = int(self.config["init_size_min"])
        self.init_size_max = int(self.config["init_size_max"])
        self.init_lgp_size_min = int(self.config["init_lgp_size_min"])
        self.init_lgp_size_max = int(self.config["init_lgp_size_max"])
        self.init_radius = int(self.config["init_radius"])
        self.output_ratio = float(self.config["output_ratio"])
        self.programs = []
        config_handler = ConfigHandler(config)
        self.outputs = config_handler.parse_outputs()
        self.has_discrete_output = config_handler.has_discrete_outputs()

    def individual_eval(self, inputs):
        pass

    def init_random(self):
        program_count = random.randint(self.init_size_min, self.init_size_max)

        for i in range(program_count):
            program = self.programs_class(self.config)
            program.generate()
            program.pos = self.random_point_in_circle(self.init_radius)
            if not self.has_discrete_output:
                if random.random() < self.output_ratio:
                    program.program_type = "O"
            self.programs.append(program)

        if self.has_discrete_output:
            for possible_discrete_output in self.outputs:
                program = self.programs_class(self.config)
                program.program_type = "O"
                program.discrete_output = possible_discrete_output
                program.generate()
                program.pos = self.random_point_in_circle(self.init_radius)
                self.programs.append(program)

    def random_point_in_circle(self, r):
        # Generate a random angle between 0 and 2pi
        theta = random.uniform(0, 2 * math.pi)
        # Generate a random radius between 0 and r
        s = r * math.sqrt(random.uniform(0, 1))
        # Calculate the x and y coordinates
        x = s * math.cos(theta)
        y = s * math.sin(theta)
        return x, y

