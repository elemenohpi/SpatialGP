import copy
import math
import random
import time

from Individual.AbstractIndividual import AbstractIndividual
from Handlers.ConfigHandler import ConfigHandler


def distance_to_pos(source_pos, pos):
    return math.sqrt((pos[0] - source_pos[0]) ** 2 + (pos[1] - source_pos[1]) ** 2)


class BaseIndividual(AbstractIndividual):
    def __init__(self, config, programs_class):
        super().__init__(config, programs_class)
        self.analysis = False
        self.execution_info = []
        self.has_output = False
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
        self.internal_state = {}
        self.fitness_obj = config_handler.get_fitness_obj()

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
                # The program does not have discrete outputs
                discrete_output_condition = True
            else:
                # The program has discrete outputs
                discrete_output_condition = not (program.program_type == "O")
                if program.program_type == "O":
                    # Basically, we let individual A to have its own output programs without any changes
                    a_output_programs.append(program)
            # This condition is set to be True if the program does not have discrete outputs or if the program type is I
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
        offspring_a = BaseIndividual(self.config, self.programs_class)
        offspring_b = BaseIndividual(self.config, self.programs_class)

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

    def add_program(self):
        max_size = int(self.config["size_max"])
        radius = float(self.config["init_radius"])
        if len(self.programs) >= max_size:
            return
        program = self.programs_class(self.config)
        program.generate()
        program.pos = self.random_point_in_circle(radius)
        if not self.has_discrete_output:
            if random.random() < self.output_ratio:
                program.program_type = "O"
        self.programs.append(program)

    def evaluate(self, problem_inputs):
        self.initialize_memory(problem_inputs)

        current_program = None
        indv_return_value = None
        discrete_output = None

        # For analysis purposes only
        if self.analysis:
            self.execution_info.append([])
            for index, program in enumerate(self.programs):
                program.id = index

        # This is to make sure we don't change the programs permanently during evaluation
        programs_copy = copy.deepcopy(self.programs)
        execution_limit = 0
        execution_counter = 0

        if not self.has_discrete_output and not self.has_output:
            execution_limit = len(programs_copy)
        start_time = time.time()

        while True:
            if execution_limit > 0:
                if execution_counter >= execution_limit:
                    break
                else:
                    execution_counter += 1

            current_program = self.select_program(current_program, programs_copy)

            if current_program is None:
                # End, there are no more programs
                break

            if self.analysis:
                self.execution_info[-1].append(current_program.id)

            temp_output = current_program.program_eval(self.internal_state)

            # ToDo:: end and exit are not implemented in the output program
            if temp_output == "end":
                programs_copy.remove(current_program)
                continue

            if temp_output == "exit":
                break

            indv_return_value = temp_output

            if current_program.program_type == "O":
                discrete_output = current_program.discrete_output
                break

            elapsed_time = (time.time() - start_time) * 1000
            max_evaluation_time = float(self.config["max_evaluation_time"])
            if 0 < max_evaluation_time < elapsed_time:
                indv_return_value = None
                break

        if self.has_discrete_output:
            return discrete_output
        else:
            return self.parse_individual_outputs()

    def select_program(self, current_program, programs):
        if current_program is None:
            source_pos = (0, 0)
        else:
            source_pos = current_program.pos

        selected_program = None

        for index, program in enumerate(programs):
            candidate_cost = program.cost(source_pos, self.internal_state)
            # Continue to the next candidate if the system is loop-free and the program node is already visited
            if self.config["enable_loops"] == "False":
                if program.visit_count > 0:
                    continue
            # If the self-loop is False and the candidate is the current program, continue
            if self.config["self_loop"] == "False" and current_program == program:
                continue

            if selected_program is None:
                selected_program = program
                continue
            if candidate_cost < selected_program.cost(source_pos, self.internal_state):
                selected_program = program

        if selected_program is not None:
            selected_program.visit_count += 1
            selected_program.logged_cost = abs(selected_program.cost(source_pos, self.internal_state))

        return selected_program

    def initialize_memory(self, problem_inputs):
        self.internal_state = {}
        if not self.passes_input_sanity(problem_inputs):
            raise ValueError("The provided input list does not match the scheme specified in the problem/fitness file")

        config_handler = ConfigHandler(self.config)
        fitness_obj = config_handler.get_fitness_obj()
        input_scheme = fitness_obj.inputs()

        unique_variable_counter = 0
        for input_element in input_scheme:
            if self.is_array(input_element):
                for index in range(self.get_array_length(input_element)):
                    name = self.get_array_name(input_element)
                    self.internal_state[name + str(index)] = problem_inputs[unique_variable_counter][index]
            else:
                self.internal_state[input_element] = problem_inputs[unique_variable_counter]
            unique_variable_counter += 1

        self.internal_state.update(self.registers)
        if not self.has_discrete_output:
            for output in self.outputs.keys():
                self.internal_state[output] = 0
        pass

    def passes_input_sanity(self, problem_inputs):
        config_handler = ConfigHandler(self.config)
        fitness_obj = config_handler.get_fitness_obj()
        input_scheme = fitness_obj.inputs()
        if len(input_scheme) != len(problem_inputs):
            print(1)
            return False
        for index, input_element in enumerate(input_scheme.keys()):
            if self.is_array(input_element) and type(problem_inputs[index]) != list:
                return False
            elif self.is_array(input_element) and type(problem_inputs[index]) == list \
                    and len(problem_inputs[index]) != self.get_array_length(input_element):
                return False
            elif not self.is_array(input_element) and type(problem_inputs[index]) == list:
                return False
        return True

    def is_array(self, input_element):
        tokens = input_element.split("[")
        if len(tokens) > 1:
            return True
        else:
            return False

    def get_array_length(self, input_element):
        tokens = input_element.split("[")
        length = int(tokens[1].split("]")[0])
        return length

    def get_array_name(self, input_element):
        tokens = input_element.split("[")
        name = tokens[0]
        return name

    def parse_individual_outputs(self):
        config_handler = ConfigHandler(self.config)
        fitness_obj = config_handler.get_fitness_obj()
        output_scheme = fitness_obj.outputs()
        output_list = []
        for unique_output_index, output_element in enumerate(output_scheme):
            if self.is_array(output_element):
                output_list.append([])
                for index in range(self.get_array_length(output_element)):
                    name = self.get_array_name(output_element)
                    value = self.internal_state[name + str(index)]
                    output_list[unique_output_index].append(value)
            else:
                value = self.internal_state[output_element]
                output_list.append(value)
        if len(output_list) == 1 and not type(output_list[0]) == list:
            output_list = output_list[0]
        return output_list

    def get_programs_info(self):
        info_list = []
        for index, program in enumerate(self.programs):
            codes = program.tooltip_text()
            entry = [index, program.pos, codes]
            info_list.append(entry)
        return info_list

    def get_execution_info(self):
        config_handler = ConfigHandler(self.config)
        fitness_obj = config_handler.get_fitness_obj()
        self.execution_info = []
        self.analysis = True
        fitness = fitness_obj.evaluate(self)
        self.analysis = False
        return fitness, self.execution_info
