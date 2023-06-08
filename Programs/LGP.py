import copy
import math
import random

from Programs.AbstractPrograms import AbstractPrograms
from Handlers.ConfigHandler import ConfigHandler
from retcon import Retcon


class LGP(AbstractPrograms):
    def __init__(self, config):
        super().__init__(config)
        self.visit_count = 0
        self.highest_cost = 0
        config_handler = ConfigHandler(config)
        self.config = config
        init_min_size = int(config["init_lgp_size_min"])
        init_max_size = int(config["init_lgp_size_max"])
        self.revisit_penalty = float(config["revisit_penalty"])
        self.program_size = random.randint(init_min_size, init_max_size)
        self.register_set = config_handler.parse_registers()
        self.function_set = config_handler.parse_function_set()
        self.terminal_set = config_handler.parse_terminal_set()
        self.has_discrete_output = config_handler.has_discrete_outputs()
        self.outputs = config_handler.parse_outputs()

        self.statement_output_pool = self.create_statement_output_pool()

        self.statements = []
        self.program_type = "I"

    def create_statement_output_pool(self):
        statement_output_pool = {"float": []}
        for register in self.register_set:
            statement_output_pool["float"].append(register)
        if not self.has_discrete_output:
            for output in self.outputs:
                statement_output_pool["float"].append(output)
        return statement_output_pool

    def generate_statement(self):
        if len(self.function_set) < 1:
            raise ValueError("Empty function set.")
        op = None
        while len(self.function_set) > 0:
            random_index = random.randint(0, len(self.function_set) - 1)
            op = copy.deepcopy(self.function_set[random_index])
            success_flag = True
            for demand in op.demands():
                if demand not in self.terminal_set.keys():
                    del self.function_set[random_index]
                    success_flag = False
                    break
                operand = random.choice(self.terminal_set[demand])
                op.operands.append(operand)
            if not success_flag:
                continue

            if op.products()[0] is None or op.products()[0] == "command" or op.products()[0] == "structural":
                break

            for product in op.products():
                if product not in self.statement_output_pool.keys():
                    del self.function_set[random_index]
                    success_flag = False
                    break
                output = random.choice(self.statement_output_pool[product])
                op.outputs.append(output)
            if success_flag:
                break
        if op is None:
            raise ValueError("There are no suitable function/terminal match to generate LGP statements.")
        return op

    def generate(self):
        for i in range(self.program_size):
            op = self.generate_statement()
            self.statements.append(op)
        return_value_selection_pool = {"float": []}

        if "float" in self.terminal_set.keys():
            return_value_selection_pool["float"] = copy.deepcopy(self.terminal_set["float"])
        if "int" in self.terminal_set.keys():
            # lets treat floats and ints equally
            return_value_selection_pool["float"] += copy.deepcopy(self.terminal_set["int"])

        if int(self.config["conditional_return"]) <= 0:
            if len(return_value_selection_pool["float"]) > 0:
                return_var = random.choice(return_value_selection_pool["float"])
            else:
                raise ValueError("No int or float variables to return.")
            self.statements.append(return_var)
        else:
            retcon_operator = Retcon(int(self.config["conditional_return"]),
                                     int(self.config["conditional_return_depth"]), return_value_selection_pool)
            retcon_operator.generate()
            self.statements.append(retcon_operator)

    def add_indent(self, program_txt: str):
        indent = "\t"
        indented_program_txt = program_txt.replace("\n", "\n\t")
        indented_program_txt = indent + indented_program_txt
        return indented_program_txt

    def lgp_mutation(self):
        # add statement, remove statement, modify statement each have 33% chance
        rand = random.random()
        if rand <= 0.33:
            self.add_lgp_statement_mutation()
        elif rand <= 0.66:
            self.remove_lgp_statement_mutation()
        else:
            random_index = random.randint(0, len(self.statements) - 1)
            if random_index == len(self.statements) - 1:
                self.mutate_return_value()
            else:
                if random.random() < 0.5:
                    # change operand
                    if len(self.statements[random_index].demands()) > 0:
                        self.change_operand_mutation(random_index)
                else:
                    # change output
                    if len(self.statements[random_index].products()) > 0:
                        self.change_output_mutation(random_index)
        rand = random.random()
        ret_mut_chance = float(self.config["return_mutation_rate_increase_handle"])
        if rand < ret_mut_chance:
            self.mutate_return_value()

    def add_lgp_statement_mutation(self):
        if len(self.statements) < int(self.config["lgp_size_max"]):
            statement = self.generate_statement()
            if len(self.statements) < 2:
                random_index = 0
            else:
                random_index = random.randint(0, len(self.statements) - 2)
            self.statements.insert(random_index, statement)

    def remove_lgp_statement_mutation(self):
        if len(self.statements) > 1:
            random_index = random.randint(0, len(self.statements) - 2)
            del self.statements[random_index]

    def mutate_return_value(self):
        if self.statements[-1].__class__.__name__ == "Retcon":
            self.statements[-1].mutate()
        else:
            return_value_selection_pool = copy.deepcopy(self.terminal_set)
            # ToDo:: At some point I had an exit() here but I removed it because I felt like this code should be fine
            if "float" in return_value_selection_pool.keys() and len(return_value_selection_pool["float"]) > 0:
                return_var = random.choice(return_value_selection_pool["float"])
            elif "int" in return_value_selection_pool.keys() and len(return_value_selection_pool["int"]) > 0:
                return_var = random.choice(return_value_selection_pool["int"])
            else:
                return_var = "0"

            self.statements[-1] = return_var

    def change_operand_mutation(self, random_index):
        selection_pool = copy.deepcopy(self.terminal_set)
        random_operand_index = random.randint(0, len(self.statements[random_index].demands()) - 1)
        operand = random.choice(
            selection_pool[self.statements[random_index].demands()[random_operand_index]])
        self.statements[random_index].operands[random_operand_index] = operand

    def change_output_mutation(self, random_index):
        output_selection_pool = copy.deepcopy(self.terminal_set)
        if self.statements[random_index].products()[0] == "command" or self.statements[random_index].products()[0] == \
                "structural" or self.statements[random_index].products()[0] is None:
            return
        random_operand_index = random.randint(0, len(self.statements[random_index].products()) - 1)
        output = random.choice(
            output_selection_pool[self.statements[random_index].products()[random_operand_index]])
        self.statements[random_index].outputs[random_operand_index] = output

    def distance_to_pos(self, source_pos, pos):
        return math.sqrt((pos[0] - source_pos[0]) ** 2 + (pos[1] - source_pos[1]) ** 2)

    def find_random_spatial_position(self):
        init_radius = float(self.config["init_radius"])
        if self.config["topology"] == "circle":
            return self.get_point_on_circle(init_radius)
        elif self.config["topology"] == "ring":
            return self.get_point_on_ring(init_radius)
        elif self.config["topology"] == "line":
            return self.get_point_on_line(init_radius)
        return None

    def get_point_on_line(self, d):
        x = random.uniform(-d, d)  # Generate a random x-coordinate within the range [-d, d]
        y = 0  # Since the point lies on the x-axis, y-coordinate is 0
        return x, y

    def get_point_on_ring(self, r):
        angle = 2 * math.pi * random.random()  # Generate a random angle between 0 and 2*pi
        x = r * math.cos(angle)  # Calculate x-coordinate
        y = r * math.sin(angle)  # Calculate y-coordinate
        return x, y

    def get_point_on_circle(self, r):
        # Generate a random angle between 0 and 2pi
        theta = random.uniform(0, 2 * math.pi)
        # Generate a random radius between 0 and r
        s = r * math.sqrt(random.uniform(0, 1))
        # Calculate the x and y coordinates
        x = s * math.cos(theta)
        y = s * math.sin(theta)
        return x, y

    def spatial_mutation(self):
        # The commented code is for the random walk approach. Possibly this should be removed
        # random_step_size = int(self.config["random_walk_step_size"])
        radius = float(self.config["init_radius"])
        rand = random.random()
        if rand < 0.5 or self.has_discrete_output:
            # change pos
            # random_step_x = random.randint(-1 * random_step_size, random_step_size)
            # random_step_y = random.randint(-1 * random_step_size, random_step_size)
            # new_pos = (random_step_x + self.pos[0], self.pos[1] + random_step_y)
            # if not self.distance_to_pos((0, 0), new_pos) > radius:
            #     self.pos = (self.pos[0] + random_step_x, self.pos[1] + random_step_y)
            new_pos = self.find_random_spatial_position()
            self.pos = new_pos
        else:
            # change i/o
            if self.program_type == "O":
                self.program_type = "I"
            else:
                self.program_type = "O"

    def cost(self, source_pos, internal_memory):
        max_distance = 2 * float(self.config["init_radius"])
        max_length = int(self.config["lgp_size_max"])
        distance = self.distance_to_pos(source_pos, self.pos)
        if distance > max_distance:
            raise ValueError("This shouldn't be possible. There must be a bug that allows for programs to get out of "
                             "the specified radius")
        length = len(self.statements)
        return_val = None
        if self.statements[-1].__class__.__name__ == "Retcon":
            return_val = self.statements[-1].eval(internal_memory)
        else:
            try:
                return_val = float(self.statements[-1])
            except ValueError:
                return_val = internal_memory[self.statements[-1]]

        try:
            cost_formula = self.config["cost_formula"]
        except KeyError:
            raise KeyError("Config file does not contain a cost_formula field")

        try:
            cost_value = eval(cost_formula)
        except Exception as e:
            raise Exception("The following error occurred when calculating the program cost: ", e)
        
        if cost_value < self.highest_cost:
            cost_value = self.highest_cost

        if self.config["enable_loops"] == "True":
            cost_value += (cost_value + 1) * self.visit_count * self.revisit_penalty

        return abs(cost_value)

    def program_eval(self, internal_state):
        program_output = None
        skip_next = False
        for statement in self.statements:
            if statement == self.statements[-1]:
                if statement.__class__.__name__ == "Retcon":
                    program_output = statement.eval(internal_state)
                else:
                    try:
                        program_output = float(statement)
                    except ValueError:
                        program_output = internal_state[statement]
                break
            if skip_next:
                skip_next = False
                continue
            input_set = self.get_operand_value(statement.operands, internal_state)
            statement_return = statement.eval(input_set)
            # skip is a valid output from operators. skip, skips the execution of the next operator.
            # None or skip does not update the shared memory
            if statement_return == "skip":
                skip_next = True
                continue
            if statement_return is None:
                continue
            if statement_return == "end":
                return "end"
            internal_state[statement.outputs[0]] = statement_return
            pass
        return program_output

    def get_operand_value(self, operands, internal_state):
        value_list = []
        for operand in operands:
            try:
                value = float(operand)
                value_list.append(value)
            except ValueError:
                try:
                    value_list.append(internal_state[operand])
                except KeyError:
                    raise KeyError(f"Variable {operand} is not numerical and does not exist in the internal state "
                                   f"memory")
        return value_list

    def annotation(self):
        annotation = ""
        indent = "\t"
        for index, statement in enumerate(self.statements):
            if index == len(self.statements) - 1:
                # Return Statement
                indent = "\t"
                if statement.__class__.__name__ == "Retcon":
                    annotation += self.add_indent(statement.annotate())
                else:
                    annotation += indent + "return " + repr(statement)
            else:
                annotation += indent + statement.annotate() + "\n"
                if statement.products()[0] == "structural":
                    indent += "\t"
                elif len(indent) > len("\t"):  # normal instruction
                    indent = "\t"

            if index is len(self.statements) - 2 and statement.products()[0] == "structural":
                annotation += indent + "pass\n"

        return annotation

    def tooltip_text(self):
        annotation = ""
        for index, statement in enumerate(self.statements):
            if index == len(self.statements) - 1:
                # Return Statement
                if statement.__class__.__name__ == "Retcon":
                    annotation += statement.annotate()
                else:
                    annotation += "return " + repr(statement)
            else:
                annotation += statement.annotate() + "\n"

        return annotation
