import json
import random

from Individual.AbstractIndividual import AbstractIndividual


class BaseIndividual(AbstractIndividual):
    def __init__(self, config, programs_class):
        super().__init__(config, programs_class)
        self.config = config
        self.programs_class = programs_class
        self.init_size_min = int(self.config["init_size_min"])
        self.init_size_max = int(self.config["init_size_max"])
        self.init_lgp_size_min = int(self.config["init_lgp_size_min"])
        self.init_lgp_size_max = int(self.config["init_lgp_size_max"])

    # def manage_output_type(self):
    #     try:
    #         self.output_pool = json.loads(self.config["outputs"])
    #     except json.decoder.JSONDecodeError:
    #         self.output_pool = self.config["outputs"].replace(" ", "").split(",")
    #         self.has_discrete_output = True

    def individual_eval(self, inputs):
        pass

    def init_random(self):
        program_count = random.randint(self.init_size_min, self.init_size_max)

        for i in range(program_count):
            program = self.programs_class(self.config)
            program.generate()
            x = random.randint(-1 * self.cue_init_radius, self.cue_init_radius)
            y = random.randint(-1 * self.cue_init_radius, self.cue_init_radius)
            program.pos = (x, y)

            self.programs.append(program)
        if self.has_discrete_output:
            for possible_discrete_output in self.output_pool:
                program = CueProgram(self.config, self.input_pool, self.constant_pool, self.operator_pool,
                                     self.output_pool,
                                     self.registers, self.has_discrete_output
                                     )
                program.program_type = "O"
                program.discrete_output = possible_discrete_output
                program_size = random.randint(self.cue_init_lgp_size_min, self.cue_init_lgp_size_max)
                program.generate(program_size)
                x = random.randint(-1 * self.cue_init_radius, self.cue_init_radius)
                y = random.randint(-1 * self.cue_init_radius, self.cue_init_radius)
                program.pos = (x, y)
                self.programs.append(program)
