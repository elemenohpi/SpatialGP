import os
import pandas as pd


def read_deap_file(path_to_file):
    with open(path_to_file, "r") as my_file:
        lines = my_file.readlines()
        del(lines[:3])
        gen = []
        avg = []
        best = []
        avg_size = []
        best_size = []
        for line in lines:
            tokens = line.split("\t")
            if len(tokens) < 5:
                continue
            gen.append(tokens[0].strip())
            avg.append(tokens[2].strip())
            best.append(tokens[5].strip())
            avg_size.append(tokens[8].strip())
            best_size.append(tokens[11].strip())
    return zip(gen, avg, best, avg_size, best_size)


def write_evo_file(file_data, out_path):
    with open(out_path, "w") as out_file:
        out_file.write("gen,best,avg,best_size,avg_size\n")
        for gen, avg, best, avg_size, best_size in file_data:
            line = f"{gen}, {best}, {avg}, {best_size}, {avg_size}\n"
            out_file.write(line)
    pass


def create_output_path(path_to_file):
    base_name = os.path.basename(path_to_file)
    dir_name = os.path.dirname(path_to_file)
    dir_name = dir_name[:-5] + "Evo"
    name = base_name.split(".")[0]
    try:
        os.makedirs(dir_name)
    except:
        pass
    out_path = os.path.join(dir_name, name) + ".csv"
    return out_path


class DEAPtoEvo:
    def __init__(self, path, key):
        self.path = path
        self.key = key
        self.root_directory_files = self.list_dirs()

    def list_dirs(self):
        key_directories = []
        dirs = os.listdir(self.path)
        for directory in dirs:
            if self.key in directory:
                key_directories.append(os.path.join(self.path, directory))
        return key_directories

    def convert(self):
        for directory in self.root_directory_files:
            directory = os.path.join(directory, "Slurm")
            files = os.listdir(directory)
            for file in files:
                path_to_file = os.path.join(directory, file)
                if path_to_file.endswith(".txt"):
                    file_data = read_deap_file(path_to_file)
                    path_to_out = create_output_path(path_to_file)
                    write_evo_file(file_data, path_to_out)
        pass


if __name__ == "__main__":
    # path = input("Enter directory: ")
    # key = input("Enter key: ")
    my_path = "../../Results/Compressed/setare"
    # my_path = "../../Results/"
    my_key = ""

    # all_folders = os.listdir(my_path)
    # for folder in all_folders:
    #     if "F" in folder:
    #         path_to_exp = os.path.join(my_path, folder)
    #         deap_to_evo = DEAPtoEvo(path_to_exp, my_key)
    #         deap_to_evo.convert()
    #         print(path_to_exp, "done")
    deap_to_evo = DEAPtoEvo(my_path, my_key)
    deap_to_evo.convert()

