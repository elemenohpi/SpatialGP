import importlib
import json


class ConfigHandler:
    def __init__(self, config):
        self.config = config

    def parse_function_set(self):
        operators = []
        try:
            packages = self.config["operators"].split(",")
        except (KeyError, TypeError, IndexError):
            raise Exception("Could not create a package list out of the operators specified in the config file. ")

        for package in packages:
            package = package.strip()
            try:
                modules = self.config[package].split(",")
            except (IndexError, KeyError):
                raise Exception("Package '{}' could not be found in the config file".format(package))

            for module in modules:
                module = module.strip()
                imported_class = importlib.import_module("Operators.{}".format(package))
                my_class = getattr(imported_class, module)
                obj = my_class()
                operators.append(obj)

        return operators

    def parse_inputs(self):
        return json.loads(self.config["inputs"])

    def parse_terminal_set(self):
        inputs = self.parse_inputs()
        constants = self.parse_constants()
        registers = self.parse_registers()
        terminal_set = inputs

        new_input_pool = {}
        for var_name in terminal_set:
            data_type = terminal_set[var_name]
            if data_type not in list(new_input_pool.keys()):
                new_input_pool[data_type] = []
            new_input_pool[data_type].append(var_name)

        terminal_set = new_input_pool

        if "float" not in terminal_set.keys():
            terminal_set["float"] = []

        for constant in constants:
            terminal_set["float"].append(constant)

        for register in registers:
            terminal_set["float"].append(register)

        return terminal_set

    def parse_constants(self):
        if self.config["constants"] != "None":
            constant_pool = self.config["constants"].replace(" ", "").split(",")
        else:
            constant_pool = []
        return constant_pool

    def parse_registers(self):
        input_registers = self.config["registers"]
        registers = {}
        if input_registers != "None":
            tokens = input_registers
            tokens = tokens.split("[")
            name = tokens[0]
            size = int(tokens[1][:len(tokens[1]) - 1])
            for i in range(size):
                new_name = name + str(i)
                registers[new_name] = 0
        return registers

    def parse_outputs(self):
        has_discrete_output = False
        try:
            output_pool = json.loads(self.config["outputs"])
        except json.decoder.JSONDecodeError:
            output_pool = self.config["outputs"].replace(" ", "").split(",")
            has_discrete_output = True

        new_output_pool = {}

        if type(output_pool) == dict:
            for var_name in output_pool:
                data_type = output_pool[var_name]
                if data_type not in new_output_pool.keys():
                    new_output_pool[data_type] = []
                new_output_pool[data_type].append(var_name)

            output_pool = new_output_pool
        elif type(output_pool) == list:
            pass
        else:
            raise ValueError("Outputs specified in the config file could not be processed.")

        return output_pool, has_discrete_output

