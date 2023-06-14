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

    def get_fitness_obj(self):
        fitness = self.config["fitness"]
        module = __import__("Fitness." + fitness)
        tokens = fitness.split(".")
        if len(tokens) > 1:
            my_class = tokens[1]
            directory = tokens[0]
            temp_module = getattr(getattr(module, directory), my_class)
            fitness_class = getattr(temp_module, my_class)
        else:
            fitness_class = getattr(getattr(module, fitness), fitness)
        return fitness_class()

    def parse_inputs(self):
        parsed_inputs = {}
        fitness_obj = self.get_fitness_obj()
        inputs = fitness_obj.inputs()
        for element in inputs.keys():
            tokens = element.split("[")
            if len(tokens) > 1:
                # We have an array input
                name = tokens[0]
                if name == "out" or name == "reg":
                    raise ValueError("The variable names 'out' and 'reg' are reserved for internal outputs and "
                                     "registers, respectively. Please specify a different name in the problem/fitness "
                                     "file.")
                size = int(tokens[1].split("]")[0])
                for i in range(size):
                    parsed_inputs[name+str(i)] = inputs[element]
            else:
                # We have a single input
                if element == "out" or element == "reg":
                    raise ValueError("The variable names 'out' and 'reg' are reserved for internal outputs and "
                                     "registers, respectively. Please specify a different name in the problem/fitness "
                                     "file.")
                parsed_inputs[element] = inputs[element]
        return parsed_inputs

    def parse_terminal_set(self):
        inputs = self.parse_inputs()
        constants = self.parse_constants()
        registers = self.parse_registers()
        terminal_set = inputs
        if not self.has_discrete_outputs():
            outputs = self.parse_outputs()
        else:
            outputs = {}
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

        # ToDo:: Isn't there any case in which we still want to have this?
        # for output in outputs:
        #     if outputs[output] in terminal_set.keys():
        #         terminal_set[outputs[output]].append(output)
        #     else:
        #         terminal_set[outputs[output]] = output
        return terminal_set

    def parse_constants(self):
        if self.config["constants"].lower() != "none":
            constant_pool = self.config["constants"].replace(" ", "").split(",")
        else:
            constant_pool = []
        return constant_pool

    def parse_registers(self):
        count = int(self.config["registers"])
        registers = {}
        for i in range(count):
            name = "reg" + str(i)
            registers[name] = 0
        return registers

    def parse_outputs(self):
        fitness_obj = self.get_fitness_obj()
        outputs = fitness_obj.outputs()
        if type(outputs) == list:
            # Discrete outputs
            return outputs
        elif type(outputs) == dict:
            # Normal outputs
            parsed_outputs = {}
            for element in outputs.keys():
                tokens = element.split("[")
                if len(tokens) > 1:
                    # We have an array output
                    name = tokens[0]
                    if name == "out" or name == "reg":
                        raise ValueError("The variable names 'out' and 'reg' are reserved for internal outputs and "
                                         "registers, respectively. Please specify a different name in the "
                                         "problem/fitness file.")
                    size = int(tokens[1].split("]")[0])
                    for i in range(size):
                        parsed_outputs[name + str(i)] = outputs[element]
                else:
                    # We have a single output
                    if element == "out" or element == "reg":
                        raise ValueError("The variable names 'out' and 'reg' are reserved for internal outputs and "
                                         "registers, respectively. Please specify a different name in the "
                                         "problem/fitness file.")
                    parsed_outputs[element] = outputs[element]
            pass
        else:
            raise ValueError("Unknown data structure used to specify the outputs in the fitness class.")
        return parsed_outputs

    def has_discrete_outputs(self):
        has_discrete_output = None
        fitness_obj = self.get_fitness_obj()
        outputs = fitness_obj.outputs()
        if type(outputs) == list:
            has_discrete_output = True
        elif type(outputs) == dict:
            has_discrete_output = False
        else:
            raise ValueError("Unknown data structure used to specify the outputs in the fitness class.")
        return has_discrete_output
