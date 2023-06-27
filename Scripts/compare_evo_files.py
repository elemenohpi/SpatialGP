import os


def list_directories(path, key):
    directories = []
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            directories.append(entry)
    parsed_directories = []
    for directory in directories:
        if key is not None:
            if key not in directory:
                continue
        parsed_directories.append(directory)
    return parsed_directories


def list_files(path):
    return os.listdir(path)


def compare_experiments(path, goal):
    fitness_list = []
    directories = list_directories(path, None)
    for directory in directories:
        files = list_files(os.path.join(path, directory, "Evo"))
        for file in files:
            file_path = os.path.join(path, directory, "Evo", file)
            with open(file_path, "r") as evo:
                lines = evo.readlines()
                last_line = lines[-1]
                tokens = last_line.replace(" ", "").split(",")
                fitness_list.append([file_path, float(tokens[1])])
    sorted_list = sorted(fitness_list, key=lambda x: x[1])
    for element in sorted_list:
        print(f"{element[1]} for {element[0]}")


if __name__ == "__main__":
    compare_experiments("../../HPCC_Experiments/Tuning", "min")


