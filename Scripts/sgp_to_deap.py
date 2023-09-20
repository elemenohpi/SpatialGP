import eletility
import os


def parse_class_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Extract the class name from the file content
    class_name = code.split("class ")[1].split("(")[0]

    # Dynamically import the class from the file
    exec(code, globals())
    class_obj = globals()[class_name]

    # Instantiate the class
    instance = class_obj()

    # Get the return value of the "inputs" function
    inps = instance.inputs()

    # Find the equation assigned to the "measured" variable
    equation_start = code.index("measured = ")
    equation_end = code.index("\n", equation_start)
    eq = code[equation_start + len("measured = "):equation_end].strip()

    return inps, eq


def find_files(directory, key=""):
    path_list = []
    files = os.listdir(directory)
    for file in files:
        full_path = os.path.join(directory, file)
        if os.path.isdir(full_path):
            continue
        if key != "" and key not in file:
            continue
        if not full_path.endswith(".py"):
            continue
        path_list.append(full_path)

    return path_list


def get_operator_list(inputs, equation):
    operator_list = []
    tokens = equation.split(
        " ")  # still could have [] or () or could be a function taking variables such as math.exp(b)
    for token in tokens:
        if "(" not in token and ")" not in token:
            if "[" in token or "]" in token:
                continue
            elif token in inputs:
                continue
        elif ")" in token and "(" not in token:
            continue
        if "(" in token:
            token = token.split("(")[0]
        if token == "":
            continue
        try:
            float(token)
        except Exception as e:
            if token == "**":
                token = "*"
            if token == "math.pi":
                continue
            if "." in token:
                token = token.split(".")[1]
            operator_list.append(token)
    return set(operator_list)


def get_all_operators(files):
    all_operators = []
    for file in files:
        inputs, equation = parse_class_file(file)
        inputs = inputs.keys()
        operator_list = get_operator_list(inputs, equation)
        all_operators += operator_list
        pass
    all_operators = set(all_operators)
    return all_operators


def get_template(base):
    with open(base, "r") as template:
        lines = template.readlines()
    return lines


def add_argument_definition(tmplt, argument_definition_lines):
    index = -1
    for i, line in enumerate(tmplt):
        if "ARGUMENT_DEFINITION" in line:
            index = i

    if index == -1:
        print("ARGUMENT_DEFINITION not found in the template file")
        exit()

    tmplt = tmplt[:index - 1] + argument_definition_lines + tmplt[index + 1:]
    return tmplt


def generate_argument_definitions(inps):
    argument_definition_lines = []
    for index, inp in enumerate(inps):
        definition_line = f"pset.renameArguments(ARG{index}='{inp}')\n"
        argument_definition_lines.append(definition_line)
    return argument_definition_lines


def generate_equation_definition(inps, eq):
    inputs = ""
    for inp in inps:
        inputs += inp + ", "
    inputs = inputs[:-2]
    equation = ""
    equation += f"    sqerrors = []\n"
    equation += f"    for {inputs} in points:\n"
    equation += f"        sqerrors.append((func({inputs}) - ({eq}))**2)\n"
    return equation


def add_equation_definition(tmplt, equation_definition_line):
    index = -1
    for i, line in enumerate(tmplt):
        if "EQUATION_DEFINITION" in line:
            index = i

    if index == -1:
        print("EQUATION_DEFINITION not found in the template file")
        exit()

    tmplt = tmplt[:index - 1] + [equation_definition_line] + tmplt[index + 1:]
    return tmplt


def add_datahandler_definition(tmplt, inp_count):
    index = -1
    for i, line in enumerate(tmplt):
        if "DATAHANDLER_DEFINITION" in line:
            index = i

    if index == -1:
        print("DATAHANDLER_DEFINITION not found in the template file")
        exit()
    datahandler_definition_line = f"    data_handler = DataHandler('example_data.txt', {inp_count})\n"
    tmplt = tmplt[:index - 1] + [datahandler_definition_line] + tmplt[index + 1:]
    return tmplt


def add_points_definition(tmplt, inps_count):
    index = -1
    for i, line in enumerate(tmplt):
        if "POINTS_DEFINITION" in line:
            index = i

    if index == -1:
        print("POINTS_DEFINITION not found in the template file")
        exit()
    get_data_lines = ""
    for inp in range(inps_count):
        get_data_lines += "data_handler.get_data(1), "
    get_data_lines = get_data_lines[:-2]
    points_def_line = f"        points.append([{get_data_lines}])\n"
    tmplt = tmplt[:index - 1] + [points_def_line] + tmplt[index + 1:]
    return tmplt


def add_primitive_definition(tmplt, inps_count):
    index = -1
    for i, line in enumerate(tmplt):
        if "PRIMITIVE_DEFINITION" in line:
            index = i

    if index == -1:
        print("PRIMITIVE_DEFINITION not found in the template file")
        exit()
    primitive_definition_line = f"pset = gp.PrimitiveSet('MAIN', {inps_count})\n"
    tmplt = tmplt[:index - 1] + [primitive_definition_line] + tmplt[index + 1:]
    return tmplt


def write_deap_file(inps, eq, template, output, name):
    try:
        os.makedirs(output)
    except:
        pass

    argument_definition_lines = generate_argument_definitions(inps)
    template = add_argument_definition(template, argument_definition_lines)

    equation = generate_equation_definition(inps, eq)
    template = add_equation_definition(template, equation)

    template = add_datahandler_definition(template, len(inps))
    template = add_primitive_definition(template, len(inps))

    deap_code = add_points_definition(template, len(inps))

    path = os.path.join(output, name + ".py")

    with open(path, "w") as file:
        file.writelines(deap_code)


def sgp_to_deap(files, base, output):
    # all_operators = get_all_operators(files)
    template = get_template(base)
    for file in files:
        if os.name == "nt":
            file_name = file.split("\\")[1]
        else:
            file_name = file.split("/")[3]

        name = file_name.split(".")[0]

        inps, eq = parse_class_file(file)

        write_deap_file(inps, eq, template, output, name)
    pass


if __name__ == "__main__":
    path = "../Fitness/Feynman"
    template = "Template.txt"
    output = "DEAP_Files"
    files = find_files(path)
    sgp_to_deap(files, template, output)
    print(f"DEAP files successfully generated in {path}")
    # inputs, equations = parse_class_file("../Fitness/Feynman/I107.py")
    # print(inputs)
    # print(equations)

