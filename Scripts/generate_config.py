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


def find_files(directory, key):
    file_list = ""
    files = os.listdir(directory)
    for file in files:
        full_path = os.path.join(directory, file)
        print(full_path)

    pass


if __name__ == "__main__":
    path = "../Fitness/"
    key = ""
    find_files(path, key)
    # inputs, equations = parse_class_file("../Fitness/Feynman/I107.py")
    # print(inputs)
    # print(equations)
