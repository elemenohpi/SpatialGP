# This script takes a path to a directory of experiments, goes through every experiment folder
# and if it finds individual pickled objects, it converts them to a population file and removes the individual files
import _pickle
import os
import pickle
import shutil

from Population import BasePopulation
from Individual import BaseIndividual
from Programs import LGP


def validate_path(path):
    contents = os.listdir(path)
    if "Error" in contents and "Evo" in contents and "Object" in contents and "Population" in contents and \
            "Slurm" in contents and "Subs" in contents:
        return True
    return False


def remove_extra_dirs(path):
    shutil.rmtree(os.path.join(path, "Error"))
    shutil.rmtree(os.path.join(path, "Executable"))
    shutil.rmtree(os.path.join(path, "Object"))
    shutil.rmtree(os.path.join(path, "Subs"))


def convert(path):
    # takes a path as input, checks if the folder is an experiment with the old SGP format which had individuals saved
    # instead of the population or not, then deletes the unnecessary data and converts the individuals to a single pop
    if not validate_path(path):
        return
    remove_extra_dirs(path)
    population_path = os.path.join(path, "Population")
    population_dirs = os.listdir(population_path)
    for P in population_dirs:
        P_path = os.path.join(population_path, P)
        individuals = os.listdir(P_path)
        individuals = sorted(individuals)
        pop_obj = None
        for file in individuals:
            if not file.endswith(".sgp"):
                continue
            file_path = os.path.join(P_path, file)
            with open(file_path, "rb") as content:
                failed = False
                try:
                    individual = pickle.load(content)
                except (_pickle.UnpicklingError, EOFError):
                    print(f"Failed to load: {file_path}")
                    failed = True
                if not pop_obj and not failed:
                    pop_obj = BasePopulation.BasePopulation(individual.config, BaseIndividual.BaseIndividual, LGP.LGP)
                    try:
                        pop_obj.generation = individual.generation
                    except AttributeError:
                        pop_obj.generation = -1
                    pop_obj.pop = []
                    pop_obj.pop.append(individual)
                elif pop_obj:
                    pop_obj.pop.append(individual)
        with open(os.path.join(P_path, "pop.sgp"), 'wb') as object_file:
            pickle.dump(pop_obj, object_file)
            print(f"{P} done")
        for file in individuals:
            if not file.endswith(".sgp"):
                continue
            if file == "pop.sgp":
                continue
            os.remove(os.path.join(P_path, file))


experiments = "../../Results/F10"
key = ""

if __name__ == "__main__":
    directories = os.listdir(experiments)
    for directory in directories:
        if not os.path.isdir(os.path.join(experiments, directory)):
            continue
        if key not in directory:
            continue
        convert(os.path.join(experiments, directory))
