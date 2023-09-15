# This script takes a path to a directory of experiments, goes through every experiment folder
# and if it finds individual pickled objects, it converts them to a population file and removes the individual files
import os
import pickle


def validate_path(path):
    contents = os.listdir(path)
    if "Error" in contents and "Evo" in contents and "Object" in contents and "Population" in contents and \
            "Slurm" in contents and "Subs" in contents:
        return True
    return False


def remove_extra_dirs(path):
    os.removedirs(os.path.join(path, "Error"))
    os.removedirs(os.path.join(path, "Executable"))
    os.removedirs(os.path.join(path, "Object"))
    os.removedirs(os.path.join(path, "Subs"))


def convert(path):
    # takes a path as input, checks if the folder is an experiment with the old SGP format which had individuals saved
    # instead of the population or not, then deletes the unnecessary data and converts the individuals to a single pop
    if not validate_path(path):
        return
    # remove_extra_dirs(path)
    population_path = os.path.join(path, "Population")
    population_dirs = os.listdir(population_path)
    for P in population_dirs:
        P_path = os.path.join(population_path, P)
        individuals = os.listdir(P_path)
        for file in individuals:
            if not file.endswith(".sgp"):
                continue
            file_path = os.path.join(P_path, file)
            content = open(file_path, "rb")
            individual = pickle.load(content)
            pass
            exit()



experiments = "../HPCC_Experiments/"
key = "Topology_circle_mutation_med_high_single"

if __name__ == "__main__":
    directories = os.listdir(experiments)
    for directory in directories:
        if not os.path.isdir(os.path.join(experiments, directory)):
            continue
        if key not in directory:
            continue
        convert(os.path.join(experiments, directory))
