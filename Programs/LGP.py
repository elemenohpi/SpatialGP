import copy
import random

from Programs.AbstractPrograms import AbstractPrograms
from Handlers.ConfigHandler import ConfigHandler
from retcon import Retcon


class LGP(AbstractPrograms):
    def __init__(self, config):
        super().__init__(config)
        config_handler = ConfigHandler(config)
        self.config = config
        init_min_size = int(config["init_lgp_size_min"])
        init_max_size = int(config["init_lgp_size_max"])
        self.program_size = random.randint(init_min_size, init_max_size)
        self.register_set = config_handler.parse_registers()
        self.function_set = config_handler.parse_function_set()
        self.terminal_set = config_handler.parse_terminal_set()
        self.outputs = config_handler.parse_outputs()
        self.statement_output_pool = self.create_statement_output_pool()
        self.statements = []


    #     self.warning_flag = True
    #     self.discrete_output = None
    #     self.selection_pool = None
    #     self.random_walk_step_size = int(self.config["random_walk_step_size"])
    #     self.cue_system = self.config["cue_system"]
    #     self.cue_init_radius = int(self.config["cue_init_radius"])
    #     self.lgp_max_size = int(self.config["cue_lgp_size_max"])
    #     self.revisit_penalty = float(self.config["cue_revisit_penalty"])
    #     self.visitable = True
    #     self.pos = ()

    #     self.visit_count = 0
    #     self.logged_cost = 0
    #     self.program_type = "I"  # or O
    #     self.init_input_selection_pool()
    #     self.init_lgp_output_selection_pool()
    #     if self.config["debug"] == "0":
    #         self.debug = False
    #     else:
    #         self.debug = True
    #
    # def init_input_selection_pool(self):
    #     self.selection_pool = copy.deepcopy(self.inputs)
    #     if "float" not in self.selection_pool.keys():
    #         self.selection_pool["float"] = []
    #     for constant in self.constants:
    #         self.selection_pool["float"].append(constant)
    #
    #     for register in self.registers:
    #         self.selection_pool["float"].append(register)
    #
    def create_statement_output_pool(self):
        statement_output_pool = {"float": []}
        for register in self.register_set:
            statement_output_pool["float"].append(register)
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

    # def cost(self, source_pos):
    #     global SHARED_memory
    #
    #     max_distance = math.sqrt(8 * self.cue_init_radius ** 2)  # math equation for max size
    #     max_complexity = self.lgp_max_size
    #     distance = distance_to_pos(source_pos, self.pos)
    #     if distance > max_distance:
    #         distance = max_distance
    #     complexity = len(self.statements)
    #
    #     if self.cue_system == "programmatical":
    #         # last element of the statements is the key to the value to be returned
    #         if self.statements[-1].__class__.__name__ == "Retcon":
    #             return_val = self.statements[-1].eval(SHARED_memory)
    #         elif self.statements[-1] == 0:
    #             return_val = 0
    #         elif self.statements[-1].isnumeric():
    #             return_val = float(self.statements[-1])
    #         else:
    #             return_val = SHARED_memory[self.statements[-1]]
    #     elif self.cue_system == "temporospatial":
    #         return_val = 0
    #     else:
    #         raise "Unknown cue_system: {}. Please edit the config file".format(self.cue_system)
    #     # normalized_distance = distance / max_distance
    #     # normalized_complexity = complexity / max_complexity
    #     # ln_normalized_distance = math.log(1+normalized_distance)
    #     # ln_normalized_complexity = math.log(1+normalized_complexity)
    #     # ln_return_value = math.log(1+abs(return_val))
    #     try:
    #         cost_formula = self.config["cost_formula"]
    #     except KeyError:
    #         raise KeyError("Config file does not contain a cost_formula field")
    #
    #     try:
    #         cost_value = eval(cost_formula)
    #     except OverflowError:
    #         cost_value = float("inf")
    #
    #     if cost_value < self.logged_cost:
    #         cost_value = self.logged_cost
    #
    #     if self.config["cue_enable_loops"] == "True":
    #         cost_value += (cost_value + 1) * self.visit_count * self.revisit_penalty
    #
    #     return abs(cost_value)
    #
    # def program_eval(self):
    #     global SHARED_memory
    #     program_output = None
    #     skip_next = False
    #     for statement in self.statements:
    #         if statement == self.statements[-1]:
    #             if statement == 0:
    #                 program_output = 0
    #             elif statement.__class__.__name__ == "Retcon":
    #                 program_output = statement.eval(SHARED_memory)
    #             elif statement.isnumeric():
    #                 program_output = float(statement)
    #             else:
    #                 program_output = SHARED_memory[statement]
    #             break
    #         if skip_next:
    #             skip_next = False
    #             continue
    #         input_set = self.construct_op_inputs_from_memory(statement.operands)
    #         statement_return = statement.eval(input_set)
    #         # skip is a valid output from operators. skip, skips the execution of the next operator.
    #         # None or skip does not update the shared memory
    #         if statement_return == "skip":
    #             skip_next = True
    #             continue
    #         if statement_return is None:
    #             continue
    #         if statement_return == "end":
    #             return "end"
    #         SHARED_memory[statement.outputs[0]] = statement_return
    #         pass
    #     return program_output
    #
    # def spatial_mutation(self):
    #     rand = random.random()
    #     unattended_chance = 0.5 # I should change this but this is for a later time
    #     if self.has_discrete_output:
    #         unattended_chance = 1
    #     if rand < unattended_chance:
    #         # change pos with step
    #         random_step_x = random.randint(-1 * self.random_walk_step_size, self.random_walk_step_size)
    #         random_step_y = random.randint(-1 * self.random_walk_step_size, self.random_walk_step_size)
    #         if abs(random_step_x + self.pos[0]) > self.cue_init_radius:
    #             random_step_x = 0
    #         if abs(self.pos[1] + random_step_y) > self.cue_init_radius:
    #             random_step_y = 0
    #         self.pos = (self.pos[0] + random_step_x, self.pos[1] + random_step_y)
    #     else:
    #         # change i/o
    #         if self.program_type == "O":
    #             self.program_type = "I"
    #         else:
    #             self.program_type = "O"
    #
    # def add_lgp_statement_mutation(self):
    #     if len(self.statements) < self.lgp_max_size:
    #         statement = self.generate_statement()
    #         if len(self.statements) < 2:
    #             random_index = 0
    #         else:
    #             random_index = random.randint(0, len(self.statements) - 2)
    #         self.statements.insert(random_index, statement)
    #
    # def remove_lgp_statement_mutation(self):
    #     if len(self.statements) > 1:
    #         random_index = random.randint(0, len(self.statements) - 2)
    #         del self.statements[random_index]
    #
    # def mutate_return_value(self):
    #     if self.statements[-1].__class__.__name__ == "Retcon":
    #         self.statements[-1].mutate()
    #     else:
    #         return_value_selection_pool = copy.deepcopy(self.output_selection_pool)
    #         for constant in self.constants:
    #             return_value_selection_pool["float"].append(constant)
    #
    #         if "float" in return_value_selection_pool.keys() and len(return_value_selection_pool["float"]) > 0:
    #             return_var = random.choice(return_value_selection_pool["float"])
    #         elif "int" in return_value_selection_pool.keys() and len(return_value_selection_pool["int"]) > 0:
    #             return_var = random.choice(return_value_selection_pool["int"])
    #         else:
    #             return_var = "0"
    #
    #         self.statements[-1] = return_var
    #
    # def change_operand_mutation(self, random_index):
    #     random_operand_index = random.randint(0, len(self.statements[random_index].demands()) - 1)
    #     operand = random.choice(
    #         self.selection_pool[self.statements[random_index].demands()[random_operand_index]])
    #     self.statements[random_index].operands[random_operand_index] = operand
    #
    # def change_output_mutation(self, random_index):
    #     if self.statements[random_index].products()[0] == "command" or self.statements[random_index].products()[0] == \
    #             "structural" or self.statements[random_index].products()[0] is None:
    #         return
    #     random_operand_index = random.randint(0, len(self.statements[random_index].products()) - 1)
    #     output = random.choice(
    #         self.output_selection_pool[self.statements[random_index].products()[random_operand_index]])
    #     self.statements[random_index].outputs[random_operand_index] = output
    #
    # def lgp_mutation(self):
    #     # add statement, remove statement, modify statement each have 33% chance
    #     rand = random.random()
    #     if rand <= 0.33:
    #         self.add_lgp_statement_mutation()
    #     elif rand <= 0.66:
    #         self.remove_lgp_statement_mutation()
    #     else:
    #         random_index = random.randint(0, len(self.statements) - 1)
    #         if random_index == len(self.statements) - 1:
    #             self.mutate_return_value()
    #         else:
    #             if random.random() < 0.5:
    #                 # change operand
    #                 if len(self.statements[random_index].demands()) > 0:
    #                     self.change_operand_mutation(random_index)
    #             else:
    #                 # change output
    #                 if len(self.statements[random_index].products()) > 0:
    #                     self.change_output_mutation(random_index)
    #     rand = random.random()
    #     ret_mut_chance = float(self.config["return_mutation_rate_increase_handle"])
    #     if rand < ret_mut_chance:
    #         self.mutate_return_value()
    #
    # @staticmethod
    # def construct_op_inputs_from_memory(operands):
    #     global SHARED_memory
    #     value_list = []
    #     for operand in operands:
    #         if operand.isnumeric():
    #             value_list.append(float(operand))
    #         else:
    #             try:
    #                 value_list.append(SHARED_memory[operand])
    #             except KeyError:
    #                 value_list.append(operand)
    #     return value_list

