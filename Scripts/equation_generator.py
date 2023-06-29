OPERATORS = ["*", "/", "-", "+", "(", ")", "math.cos", "math.sin", "math.tan", "**", "math.sqrt", "math.exp",
             "math.log"]


def better_is_numeric(str):
    try:
        i = int(str)
    except Exception as e:
        return False
    return True


def get_array_name(array):
    name = array.split("[")[0]
    return name


def get_array_size(array):
    tokens = array.split("[")
    size_str = tokens[1][:-1]
    return int(size_str)


def is_array(var):
    if len(var.split("[")) > 1:
        return True
    return False


def create_file(equation_name, equation, output_name, final_list):
    inputs_text = ""
    for index, var in enumerate(final_list):
        if index > 0:
            inputs_text += "            "
        inputs_text += f'"{var}": "float",\n'

    data_text = ""
    for index, var in enumerate(final_list):
        if index > 0:
            data_text += "            "
        if is_array(var):
            data_text += f'{get_array_name(var)} = self.data_handler.get_data({get_array_size(var)})\n'
        elif var == "pi":
            data_text += f'{var} = math.pi\n'
        else:
            data_text += f'{var} = self.data_handler.get_data(1)\n'

    sgp_inputs_text = ""
    for var in final_list:
        if is_array(var):
            sgp_inputs_text += f"{get_array_name(var)}, "
        else:
            sgp_inputs_text += f"{var}, "
    sgp_inputs_text = sgp_inputs_text[:-2]

    file_name = equation_name
    file_text = f"""
import math
import sys
import numpy as np
import warnings
from scipy import stats

from Fitness.AbstractFitness import AbstractFitness
from Handlers.DataHandler import DataHandler

# Suppress all warnings
warnings.filterwarnings("ignore")


class {equation_name}(AbstractFitness):

    def __init__(self) -> None:
        super().__init__()
        self.evaluation_method = "correlation"  # or rmse
        self.evaluation_count = 10
        self.data_handler = DataHandler("Fitness/Feynman/example_data.txt", self)

    def settings(self):
        return {{
            "optimization_goal": "min",
        }}

    def inputs(self):
        return {{
            {inputs_text}
        }}

    def outputs(self):
        return {{
            "{output_name}": "float"
        }}

    def evaluate(self, individual):
        self.data_handler.reset()
        sum_error_squared = 0
        predicted_results = []
        measured_results = []
        for i in range(self.evaluation_count):
            # ======================================STARTPROBLEM===============================================
            {data_text}
            inputs = [{sgp_inputs_text}]

            measured = {equation}
            # ======================================ENDPROBLEM===============================================
            measured_results.append(measured)
            try:
                output = individual.evaluate(inputs)
                predicted_results.append(output)
                error_squared = (measured - output) ** 2
            except OverflowError:
                error_squared = sys.float_info.max
            sum_error_squared += error_squared
        rmse = math.sqrt(sum_error_squared / self.evaluation_count)
        if self.evaluation_method == "rmse":
            return rmse
        elif self.evaluation_method == "correlation":
            if len(set(predicted_results)) <= 1 or len(predicted_results) != len(measured_results):
                return 10
            try:
                r = stats.pearsonr(measured_results, predicted_results)[0]
            except ValueError:
                return 10
            if math.isnan(r):
                return 10
            try:
                align = np.polyfit(predicted_results, measured_results, 1)
            except BaseException:
                align = [0, 0]

            sum_error_squared = 0
            for index, prediction in enumerate(predicted_results):
                prediction = prediction * align[0] + align[1]
                error_squared = (measured_results[index] - prediction) ** 2
                sum_error_squared += error_squared
            individual.rmse = math.sqrt(sum_error_squared / self.evaluation_count)
            return 1 - r ** 2

    """

    with open(f"../Fitness/Feynman/{file_name}.py", "w") as file:
        file.write(file_text)


def process_equation():
    global OPERATORS

    equation_name = input("Enter equation name: ")
    output_name = input("Enter output name: ")
    equation = input("Enter equation: ")
    variable_list = []

    spaced_equation = equation.replace("(", " ( ").replace(")", " ) ")
    tokens = spaced_equation.split(" ")

    for token in tokens:
        if better_is_numeric(token):
            continue
        else:
            if token in OPERATORS:
                continue
            else:
                variable_list.append(token)

    variable_set = set(variable_list)
    array_list = []
    final_list = []
    for variable in variable_set:
        tokens = variable.split("[")
        if len(tokens) > 1:
            array_list.append(variable)
        else:
            if variable != "":
                final_list.append(variable)

    array_info = {}
    for array in array_list:
        name = get_array_name(array)
        size = get_array_size(array)
        if name not in array_info.keys():
            array_info[name] = size
        else:
            if array_info[name] < size:
                array_info[name] = size

    for name in array_info:
        final_list.append(f"{name}[{array_info[name] + 1}]")

    create_file(equation_name, equation, output_name, final_list)


if __name__ == "__main__":
    process_equation()
