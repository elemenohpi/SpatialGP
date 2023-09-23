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


def get_base_config(base):
    configparser = eletility.ConfigParser()
    config = configparser.read(base)
    return config


def write_new_config(config, output, title):
    try:
        os.makedirs(output)
    except:
        pass
    configparser = eletility.ConfigParser()
    configparser.write(config, output + "//" + title + ".ini")
    pass


def parse_register_count(file):
    inps, eq = parse_class_file(file)
    return str(len(inps) + 2)


def create_config(files, base, output):
    # all_operators = get_all_operators(files)
    base_config = get_base_config(base)
    for file in files:
        if os.name == "nt":
            file_name = file.split("\\")[1]
            directory = file.split("\\")[0]
        else:
            file_name = file.split("/")[3]
            directory = os.path.join(file.split("/")[0], file.split("/")[1], file.split("/")[2])

        subdir = ""
        try:
            subdir = directory.split("/")[2]
        except:
            pass
        name = file_name.split(".")[0]
        fitness = name
        if subdir != "":
            fitness = f"{subdir}.{name}"
        file_config = base_config
        file_config["fitness"] = fitness
        file_config["registers"] = parse_register_count(file)
        write_new_config(file_config, output, name)
    pass


if __name__ == "__main__":
    path = "../Fitness/Feynman3"
    key = ""
    base = "../Configs/ParamConf2/II242-10.ini"
    output = "../Configs/SGP3"
    files = find_files(path, key)
    create_config(files, base, output)
    print(f"Configs successfully generated in {output}")
    # inputs, equations = parse_class_file("../Fitness/Feynman/I107.py")
    # print(inputs)
    # print(equations)

