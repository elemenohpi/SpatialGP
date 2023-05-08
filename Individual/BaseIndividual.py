import copy
import math
import random

from Individual.AbstractIndividual import AbstractIndividual
from Handlers.ConfigHandler import ConfigHandler


def distance_to_pos(source_pos, pos):
    return math.sqrt((pos[0] - source_pos[0]) ** 2 + (pos[1] - source_pos[1]) ** 2)


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
        self.inputs = config_handler.parse_inputs()
        self.registers = config_handler.parse_registers()
        self.functions = config_handler.parse_function_set()
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

    def get_annotation(self):
        model_annotation = ""
        import_txt = "debug = 0\n\nimport math\n\n"
        model_annotation += import_txt
        inputs_txt = self.generate_inputs_txt()
        register_txt = self.generate_register_txt()
        model_annotation += inputs_txt + "\n" + register_txt + "\n\n"
        globals_txt = self.generate_globals_txt()

        model_annotation += "# Operator Function Definitions"
        operators_def_txt = self.generate_operators_def_txt()
        model_annotation += operators_def_txt + "\n"

        model_annotation += "# Individual Program Definitions\n"
        for index, program in enumerate(self.programs):
            program_txt = self.generate_programs_txt(index, program, globals_txt)
            class_txt = "class P{}:\n".format(index)
            cost = len(program.statements)
            pos = program.pos
            return_var = program.statements[-1]
            program_type = program.program_type
            discrete_output = program.discrete_output
            cost_pos_txt = self.generate_method_attribute_text(cost, pos, return_var, program_type, discrete_output)
            full_program = class_txt + self.add_indent(cost_pos_txt) + \
                           "\n\n" + self.add_indent(program_txt)
            model_annotation += full_program + "\n\n\n"

        model_annotation += "# QGP Interpreter\n"
        model_annotation += self.generate_interpreter_txt(globals_txt)
        model_annotation += "\n\nrun()\n"
        return model_annotation

    def generate_method_attribute_text(self, cost: int, pos: tuple, return_var, ptype, discrete_output):
        if return_var.__class__.__name__ == "Retcon":
            return_var = return_var.annotate()
            cost_pos_txt = "discrete_output = '{}'\ntype = '{}'\nreturn_var = \"\"\"{}\"\"\"\ncomplexity = {}\n" \
                           "pos = {}\nvisit_count = 0"\
                .format(discrete_output, ptype, return_var, cost, str(pos))
        else:
            cost_pos_txt = "discrete_output = '{}'\ntype = '{}'\nreturn_var = '{}'\ncomplexity = {}\npos = {}\n" \
                           "visit_count = 0"\
                .format(discrete_output, ptype, return_var, cost, str(pos))
        return cost_pos_txt

    def add_indent(self, program_txt: str):
        indent = "\t"
        indented_program_txt = program_txt.replace("\n", "\n\t")
        indented_program_txt = indent + indented_program_txt
        return indented_program_txt

    def generate_inputs_txt(self):
        inputs_txt = "# Input Definition\n"
        for item in self.inputs:
            inputs_txt += "{} = None\n".format(item)
        return inputs_txt

    def generate_register_txt(self):
        register_txt = "# Register Definition\n"
        for register in self.registers:
            register_txt += "{} = {}\n".format(register, self.registers[register])
        return register_txt

    def generate_globals_txt(self):
        global_txt = "global "
        for index, item in enumerate(self.inputs):
            global_txt += item
            global_txt += ", "
        if len(self.registers) < 1:
            global_txt = global_txt[:-1]
        for index, register in enumerate(self.registers):
            global_txt += register
            if index != len(self.registers) - 1:
                global_txt += ", "

        return global_txt

    def generate_operators_def_txt(self):
        operators_def_txt = ""
        for operator in self.functions:
            operators_def_txt += operator.op_code() + "\n"
        return operators_def_txt

    def generate_interpreter_helpers_txt(self):
        select_program = ("\n\n"
                          "def select_program(current_program):\n"
                          "\tglobal program_objects, enable_loops, debug\n"
                          "\tif current_program is None:\n"
                          "\t\tsource = (0, 0)\n"
                          "\telse:\n"
                          "\t\tsource = current_program.pos\n"
                          "\tselected_program = None\n"
                          "\tselected_cost = None\n"
                          "\tfor program in program_objects:\n"
                          "\t\tdest = program.pos\n"
                          "\t\tprogram_cost = cost(source, dest, program.complexity, program.return_var, program.visit_count)\n"
                          "\t\tif program_cost == float(\"inf\") or program_cost == float(\"nan\"):\n"
                          "\t\t\treturn None\n"
                          "\t\tif program == current_program:\n"
                          "\t\t\tcontinue\n"
                          "\t\tif not enable_loops:\n"
                          "\t\t\tif program.visit_count > 0:\n"
                          "\t\t\t\tcontinue\n"
                          "\t\tif selected_program is None:\n"
                          "\t\t\tselected_program = program\n"
                          "\t\t\tselected_cost = program_cost\n"
                          "\t\t\tcontinue\n"
                          "\t\tif program_cost < selected_cost:\n"
                          "\t\t\tselected_program = program\n"
                          "\t\t\tselected_cost = program_cost\n"
                          "\tif debug == 1:\n"
                          "\t\tprint(selected_program.__class__.__name__, \"selected\")\n"
                          "\tif selected_program is not None:\n"
                          "\t\tselected_program.visit_count += 1\n"
                          "\treturn selected_program        \n"
                          "")
        distance_function = ("\n\n"
                             "def distance_to_pos(source, dest):\n"
                             "\treturn math.sqrt((dest[0] - source[0]) ** 2 + (dest[1] - source[1]) ** 2)        \n"
                             "")

        cost_formula = self.config["cost_formula"]

        cost_function = (
                "\n\n"
                "def cost(source, dest, complexity, return_var, visit_count):\n"
                "\tglobal max_complexity, max_distance, cue_system, enable_loops, revisit_penalty\n"
                "\tdistance = distance_to_pos(source, dest)\n"
                "\tnormalized_distance = distance / max_distance\n"
                "\tnormalized_complexity = complexity / max_complexity\n"
                "\tif cue_system == \"programmatical\":\n"
                "\t\ttry:\n"
                "\t\t\treturn_val = eval(return_var)\n"
                "\t\texcept SyntaxError:\n"
                "\t\t\treturn_var = str(return_var)\n"
                "\t\t\treturn_var = return_var.replace('\\n\\t', '\\n')\n"
                "\t\t\treturn_var = return_var.replace(\"\\t\\t\", \"\\t\")\n"
                "\t\t\treturn_var = return_var.replace(\"return \", \"program_output = \")\n"
                "\t\t\texec_locals = {}\n"
                "\t\t\texec(return_var, globals(), exec_locals)\n"
                "\t\t\treturn_val = exec_locals['program_output']\n"
                "\telif cue_system == \"temporospatial\":\n"
                "\t\treturn_val = 0\n"
                "\telse:\n"
                "\t\traise \"Unknown Cue System\"\n"
                "\tcost_value = " + cost_formula + "\n"
                                                   "\tif enable_loops:\n"
                                                   "\t\tcost_value += (cost_value + 1) * visit_count * revisit_penalty\n"
                                                   "\treturn abs(cost_value)\n\n"
                                                   ""
        )

        reset_function = self.generate_reset_txt()

        return select_program + distance_function + cost_function + reset_function

    def generate_interpreter_txt(self, globals_txt):
        # Setting up visit counts
        interpreter_txt = ""
        lgp_max_size = int(self.config["lgp_size_max"])
        cue_init_radius = int(self.config["init_radius"])
        max_distance = math.sqrt(8 * cue_init_radius ** 2)  # math equation for max size
        max_complexity = lgp_max_size
        system_mode = self.config["system_mode"]
        enable_loops = self.config["enable_loops"]
        revisit_penalty = self.config["revisit_penalty"]
        has_output = False
        for program in self.programs:
            if program.program_type == "O":
                has_output = True
        program_count = len(self.programs)
        discrete_output = str(self.has_discrete_output)
        interpreter_txt += "discrete_output = {}\nrevisit_penalty = {}\nmax_distance = {}\nmax_complexity = {}\n" \
                           "cue_system = '{}'\nenable_loops = {}\nhas_output = {}\n".format(
            discrete_output, revisit_penalty, max_distance, max_complexity, system_mode, enable_loops,
            has_output)

        object_creation_txt = "# noinspection PyListCreation\nprogram_objects = []\n"
        for index, _ in enumerate(self.programs):
            object_creation_txt += "program_objects.append(P{}())\n".format(index)

        interpreter_txt += "\n" + object_creation_txt

        interpreter_txt += self.generate_interpreter_helpers_txt()
        loop_txt = "program_output = None\n\n\n"
        loop_txt += "def run():\n"
        loop_txt += "\treset()\n\t"
        loop_txt += self.generate_globals_txt() + ", program_output\n"
        for item in self.inputs:
            loop_txt += "\t{} = {}(input('Enter {}:'))\n".format(item, self.inputs[item], item)

        loop_txt += "\tcurrent_p = None\n\tprogram_output = None\n"
        if not has_output:
            loop_txt += "\tfor _ in range({}):".format(program_count)
        else:
            loop_txt += "\twhile True:"
        loop_txt += ("\n"
                     "\t\tcurrent_p = select_program(current_p)\n"
                     "\t\tif current_p is None:\n"
                     "\t\t\tbreak\n"
                     "\t\tfunction_name = current_p.__class__.__name__.lower()\n"
                     "\t\tprogram_output = eval(\"current_p.{}()\".format(function_name))\n"
                     "\t\tif current_p.type == \"O\":\n"
                     "\t\t\tbreak\n"
                     "\tif discrete_output:\n"
                     "\t\tprint(current_p.discrete_output)\n"
                     "\telse:\n"
                     "\t\tprint('Output:', eval(str(program_output)))\n"
                     "")
        interpreter_txt += "\n" + loop_txt
        return interpreter_txt

    def generate_reset_txt(self):
        reset_txt = "\ndef reset():\n"
        global_vars = "\t" + self.generate_globals_txt() + "\n"
        reset_visit_counts = "\tfor program in program_objects:\n" \
                             "\t\tprogram.visit_count = 0"
        reset_registers = "\n"
        for register in self.registers:
            reset_registers += "\t{} = 0\n".format(register)
        reset_txt += global_vars + reset_visit_counts + reset_registers + "\n"
        return reset_txt

    def generate_programs_txt(self, index, program, global_txt):
        full_program_txt = ""
        full_program_txt += "def p{}(self):\n".format(index)
        full_program_txt += "\t" + global_txt + "\n"
        full_program_txt += program.annotation()
        return full_program_txt

    def crossover(self, parent_b):
        radius = int(self.init_radius / 2)
        rand_x, rand_y = self.random_point_in_circle(radius)
        a_inside_programs = []
        a_outside_programs = []
        b_inside_programs = []
        b_outside_programs = []
        a_output_programs = []
        b_output_programs = []
        max_program_size = int(self.config["lgp_size_max"])
        for program in self.programs:
            if not self.has_discrete_output:
                discrete_output_condition = True
            else:
                discrete_output_condition = not (program.program_type == "O")
                if program.program_type == "O":
                    a_output_programs.append(program)
            if discrete_output_condition:
                if distance_to_pos(program.pos, (rand_x, rand_y)) <= radius:
                    a_inside_programs.append(program)
                else:
                    a_outside_programs.append(program)
        for program in parent_b.programs:
            if not self.has_discrete_output:
                discrete_output_condition = True
            else:
                discrete_output_condition = not (program.program_type == "O")
                if program.program_type == "O":
                    b_output_programs.append(program)
            if discrete_output_condition:
                if distance_to_pos(program.pos, (rand_x, rand_y)) <= radius:
                    b_inside_programs.append(program)
                else:
                    b_outside_programs.append(program)
        offspring_a = self.programs_class(self.config)
        offspring_b = self.programs_class(self.config)

        ab_inside_outside_programs = a_inside_programs + b_outside_programs
        ba_inside_outside_programs = a_outside_programs + b_inside_programs

        if len(ab_inside_outside_programs) > max_program_size:
            ab_inside_outside_programs = copy.deepcopy(ab_inside_outside_programs[:max_program_size - 1])

        if len(ba_inside_outside_programs) > max_program_size:
            ba_inside_outside_programs = copy.deepcopy(ba_inside_outside_programs[:max_program_size - 1])

        offspring_a.programs = ab_inside_outside_programs + a_output_programs
        offspring_b.programs = ba_inside_outside_programs + b_output_programs
        offspring_a = copy.deepcopy(offspring_a)
        offspring_b = copy.deepcopy(offspring_b)

        return offspring_a, offspring_b
