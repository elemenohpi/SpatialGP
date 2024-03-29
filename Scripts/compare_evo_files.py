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


def compare_experiments(path, gen):
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
                try:
                    fitness_list.append([file_path, float(tokens[1])])
                except:
                    last_line = lines[-2]
                    tokens = last_line.replace(" ", "").split(",")
                    fitness_list.append([file_path, float(tokens[1])])
    sorted_list = sorted(fitness_list, key=lambda x: x[1])
    total_solved = 0
    avg_fitness = 0
    for element in sorted_list:
        print(f"{element[1]} for {element[0]}")
        if float(element[1]) == 0:
            total_solved += 1
        avg_fitness += float(element[1])

    print(f"Total solved: {total_solved}, avg_fitness: {avg_fitness/len(sorted_list)}")


if __name__ == "__main__":
    compare_experiments("../../Results/Compressed/all_conf", "min")


