import argparse
import datetime
import os
import pickle
import random
import shutil
from os import listdir
from os.path import isfile, join
from subprocess import call

import paramiko

from eletility import ConfigParser, Files
from Handlers.VisualizationHandler import VisualizationHandler
from spatial_gp import SpatialGP


def main():
    """
The main function of the program.

:return: Nothing
:doc-author: Trelent
"""
    print("Spatial Genetic Programming Version 2.0")
    args = parse_arguments()
    manage_args(args)


def parse_arguments():
    """
The parse_arguments function is used to parse the command line arguments.
The function takes no parameters and returns a Namespace object containing the parsed arguments.


:return: A namespace object
:doc-author: Trelent
"""
    parser = argparse.ArgumentParser(
        description='Spatial Genetic Programming. Command line options are meant to be used to override config '
                    'parameters in the config.ini file and/or to specify the type of the experiment')
    parser.add_argument("-hpcc", help="Runs the application as an experiment on HPCC", action='store_true')
    parser.add_argument("-validateConfig", help="Tests the validity of all config files in a directory")
    parser.add_argument("-hpccExperiment", help="Same as -hpcc but takes config directory instead", action='store_true')
    parser.add_argument("-seed", help="The random seed")
    parser.add_argument("-config", help="Config file to operate with")
    parser.add_argument("-output", help="Path to the output file")
    parser.add_argument("-pickle", help="Path to the pickled object")
    parser.add_argument("-evo", help="Path to the evolutionary output")
    parser.add_argument("-generations", help="Number of generations")
    parser.add_argument("-compare", help="Compares the evo files and returns some stats about the best run. "
                                         "Uses the optimization goal specified in the config.ini file")
    parser.add_argument("-analyze", help="Analyzes a given pickled model")
    parser.add_argument("-test_model", help="Tests a given model")
    parser.add_argument("-save_output", help="Saves the current experiment files in Output", action='store_true')
    parser.add_argument("-pop_save_path", help="Path to where the population pickle files are saved")
    parser.add_argument("-download_hpcc", help="Downloads experiment files from HPCC", action='store_true')
    args = parser.parse_args()
    return args


def analyze_model(path_to_model):
    vis_handler = VisualizationHandler()
    vis_handler.analyze_model(path_to_model)


def test_model(path):
    pickled_object = open(path, "rb")
    model_object = pickle.load(pickled_object)
    inputs = model_object.fitness_obj.inputs()
    manual_inputs = []
    print("Please enter the values for the following inputs:")
    for inp in inputs:
        if model_object.is_array(inp):
            inp_array = []
            name = model_object.get_array_name(inp)
            length = model_object.get_array_length(inp)
            for i in range(length):
                inp_value = float(input(f"{name}[{length}]: "))
                inp_array.append(inp_value)
            manual_inputs.append(inp_array)
        else:
            inp_value = float(input(f"{inp}: "))
            manual_inputs.append(inp_value)
    output = model_object.evaluate(manual_inputs)
    print("Output:\n", output)


def save_files():
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Format the date and time as a string
    timestamp = current_datetime.strftime("%Y-%m-%d %H-%M-%S")
    directory = f'Saved Experiments/{timestamp}'
    os.makedirs(directory)
    copy_directory_contents("Output/", directory)


def copy_directory_contents(source_dir, destination_dir):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Get the list of files and directories in the source directory
    contents = os.listdir(source_dir)

    # Copy each file and directory to the destination directory
    for item in contents:
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)
        if os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)


def download_hpcc():
    # # ToDo:: Implement
    # raise NotImplementedError("Not Implemented")
    username = input("Username: ")
    password = input("Username: ")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("hpcc.msu.edu", port=22, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.get("~/SpatialGP/Output/", "D:/Projects/SGP/SpatialGP/Saved Experiments/")
    sftp.close()
    ssh.close()


def manage_args(args):
    """
The manage_args function is the main entry point for the SpatialGP program.
It handles all of the command line arguments and calls other functions as needed.


:param args: Parse the command line arguments
:return: Nothing
:doc-author: Trelent
"""
    config_file = "config.ini"
    if args.config:
        config_file = args.config

    configparser = ConfigParser()
    config = configparser.read(config_file)

    # Random seed
    if args.seed:
        config["seed"] = args.seed
    random.seed(int(config["seed"]))

    # Number of generations
    if args.generations:
        config["generations"] = args.generations

    # best program output file
    if args.output:
        config["best_program"] = args.output

    # pickle output file
    if args.pickle:
        config["best_object"] = args.pickle

    # evo output file
    if args.evo:
        config["evo_file"] = args.evo

    if args.pop_save_path:
        config["pop_save_path"] = args.pop_save_path

    # Run an HPCC experiment with a single config file
    if args.hpcc:
        hpcc_single()
    # Run HPCC experiments with multiple config files
    elif args.hpccExperiment:
        hpcc_experiment()
    # Validate config
    elif args.validateConfig:
        validate_configs(args.test)
    # Compare Evo output files
    elif args.compare:
        compare_evo(args.compare, config)
    elif args.analyze:
        analyze_model(args.analyze)
    elif args.test_model:
        test_model(args.test_model)
    elif args.save_output:
        save_files()
    elif args.download_hpcc:
        download_hpcc()
    # Run SpatialGP
    else:
        sgp = SpatialGP(config)
        best_fitness = sgp.run()


def compare_evo(path, config):
    """
The compare_evo function takes in a path to the directory containing all of the evolution files, and a config dictionary.
It then iterates through each file in that directory, and finds the best fitness value for each file. It then prints out
the name of that file, along with its generation number, fitness value (best), rvalue (best), rmse (best) and average
fitness values.

:param path: Specify the directory where the files are located
:param config: Specify the optimization goal
:return: The best individual in the population
:doc-author: Trelent
"""
    goal = config["optimization_goal"]
    files = [f for f in listdir(path) if isfile(join(path, f))]
    best_info = []
    best_fitness = None
    best_rmse = None
    for file in files:
        if file.split(".")[-1] != "csv":
            continue
        with open(join(path, file), 'r') as f:
            last_line = f.readlines()[-1]
        gen, fitness, rvalue, rmse, avg = last_line.split(",")
        print(file, gen, fitness, rvalue, rmse, avg)
        if goal == "max" and (best_fitness is None or float(best_fitness) < float(fitness)):
            best_info = [file, gen, fitness, rvalue, rmse, avg]
            best_fitness = fitness
        elif goal == "min" and (best_fitness is None or float(best_fitness) >= float(fitness)):
            if best_fitness is not None and float(best_fitness) == float(fitness):
                if rmse > best_rmse:
                    continue
            best_info = [file, gen, fitness, rvalue, rmse, avg]
            best_fitness = fitness
            best_rmse = rmse
    print("best: ", best_info)


def validate_configs(path):
    """
The validate_configs function is used to test the validity of all configuration files in a given directory.
It will run each config file for 3 generations and report whether or not it was successful.


:param path: Specify the directory where the config files are located
:return: A report of which config files passed and failed the test
:doc-author: Trelent
"""
    report = ""
    config_directory = [f for f in listdir(path) if isfile(join(path, f))]
    for config_file in config_directory:
        if config_file.split(".")[-1] != "ini":
            continue
        configparser = ConfigParser()
        config_path = join(path, config_file)
        config = configparser.read(config_path)
        config["generations"] = "3"
        try:
            print("\nTesting", config_file)
            sgp = SpatialGP(config)
            best_fitness = sgp.run()
            report += "{} test OK\n".format(config_file)
        except:
            report += "{} test FAIL\n".format(config_file)
    print("\nTest Report:\n")
    print(report)


def hpcc_experiment():
    """
The hpcc_experiment function is a wrapper for the hpcc function. It allows you to run multiple experiments
with different config files, all with the same settings (reps, hours, generations). The only thing that changes is the
config file and title of each experiment. This makes it easy to run many experiments at once without having to
manually change any parameters.

:return: Nothing
:doc-author: Trelent
"""
    title = input("Experiment title (will be appended by the config name): ")
    hours = int(input("Job time (in hours): "))
    reps = int(input("Number of reps: "))
    generations = int(input("Number of generations: "))
    seed = int(input("Starting seed: "))
    config = input("Config directory: ")
    print("Title: {}, Reps: {}, Hours: {}, Gens: {}, Starting Seed: {}, Config: {}".format(title, reps, hours,
                                                                                           generations, seed, config))
    confirm = input("Do you confirm these settings? YES to continue ")
    if confirm != "YES":
        print("Exiting...")
        exit()
    config_files = [f for f in listdir(config) if isfile(join(config, f))]
    for config_file in config_files:
        if config_file.split(".")[-1] != "ini":
            continue
        new_title = title + "_" + config_file.split(".")[0]
        config_path = join(config, config_file)
        hpcc(reps, hours, generations, seed, new_title, config_path)


def hpcc_single():
    """
    The hpcc_single function is a wrapper for the hpcc function. It prompts the user for input and then calls hpcc
    with those parameters.

:return: The following:
:doc-author: Trelent
"""
    title = input("Experiment title: ")
    hours = int(input("Job time (in hours): "))
    reps = int(input("Number of reps: "))
    generations = int(input("Number of generations: "))
    seed = int(input("Starting seed: "))
    config = input("Config file: ")

    print(
        "Title: {}, Reps: {}, Hours: {}, Gens: {}, Starting Seed: {}, Config: {}".format(title, reps, hours,
                                                                                         generations, seed, config))
    confirm = input("Do you confirm these settings? YES to continue ")
    if confirm != "YES":
        print("Exiting...")
        exit()
    hpcc(reps, hours, generations, seed, title, config)


def hpcc(reps, hours, generations, seed, title, config):
    """
        The hpcc function is used to create a series of slurm files that can be submitted to the hpcc. The function takes
        in the following arguments: reps - The number of repetitions for each experiment.  This will result in 'reps'
        number of slurm files being created and submitted. hours - The maximum amount of time (in hours) that each job
        should run on the hpcc before it is killed by SLURM.  This value must be an integer between 1 and 24 inclusive,
        or else an error will occur when submitting jobs to SLURM via sbatch command line tool.

    :param reps: Determine how many times the experiment will be run
    :param hours: Set the time limit of each job
    :param generations: Specify the number of generations to be performed
    :param seed: Set the seed for the random number generator
    :param title: Create a folder with the same name
    :param config: Specify the config file that you want to use
    :return: A list of the slurm files that were submitted
    :doc-author: Trelent
    """
    file_handler = Files()
    # create a folder
    try:
        os.mkdir("Output/{}".format(title))
        os.mkdir("Output/{}/Error".format(title))
        os.mkdir("Output/{}/Slurm".format(title))
        os.mkdir("Output/{}/Evo".format(title))
        os.mkdir("Output/{}/Population".format(title))
        for rep in range(reps):
            os.mkdir("Output/{}/Population/P{}".format(title, rep))
        os.mkdir("Output/{}/Object".format(title))
        os.mkdir("Output/{}/Executable".format(title))
        os.mkdir("Output/{}/Subs".format(title))
    except FileExistsError:
        pass
    destination = "Output/{}/{}.ini".format(title, title)
    content = "#Overridden Settings:\n#reps = {}\n#hours = {}\n#generations = {}\n#seed = {}\n\n".format(reps, hours,
                                                                                                         generations,
                                                                                                         seed)
    with open(config, "r") as f:
        content += f.read()
    file_handler.writeTruncate(destination, content)

    for i in range(reps):
        filename = "Output/{}/Subs/{}.sb".format(title, i)
        file = open(filename, "w")
        file.write("#!/bin/bash --login\n")
        file.write("\n########## SBATCH Lines for Resource Request ##########\n\n")
        file.write(
            "#SBATCH --time={}:02:00             # limit of wall clock time - how long the job will run (same as -t)\n"
            .format(hours))
        file.write(
            "#SBATCH --nodes=1                   # number of different nodes - could be an exact number or a range of "
            "nodes (same as -N)\n")
        file.write(
            "#SBATCH --ntasks=1                  # number of tasks - how many tasks (nodes) that you require (same as "
            "-n)\n")
        file.write("#SBATCH --cpus-per-task=1           # number of CPUs (or cores) per task (same as -c)\n")
        file.write(
            "#SBATCH --mem-per-cpu=8G            # memory required per allocated CPU (or core) - amount of memory (in "
            "bytes)\n")
        file.write(
            "#SBATCH --job-name {}_{}      # you can give your job a name for easier identification (same as -J)\n"
            "".format(title, i))
        file.write(
            "#SBATCH --error=Output/{}/Error/{}_{}.err      # you can give your job a name for easier identification "
            "(same as -J)\n".format(
                title, title, i))
        file.write(
            "#SBATCH --output=Output/{}/Slurm/{}_{}.txt      # you can give your job a name for easier identification "
            "(same as -J)\n".format(
                title, title, i))

        # SBATCH --error=%j.err
        file.write("\n########## Command Lines to Run ##########\n\n")
        file.write("module purge")
        file.write("module load Conda/3")
        file.write("conda activate SpatialGP")
        current_file_path = os.path.abspath(__file__)
        directory_name = os.path.dirname(current_file_path)
        file.write("cd ~/{}\n".format(directory_name))
        # file.write("module load GCC/6.4.0-2.28 OpenMPI  ### load necessary modules, e.g\n")
        output = "Output/{}/Executable/exec_{}.py".format(title, i)
        pickleo = "Output/{}/Object/pickled_{}.sgp".format(title, i)
        evo = "Output/{}/Evo/evo_{}.csv".format(title, i)
        pop_save_path = f"Output/{title}/Population/P{i}/"
        file.write(
            "srun -n 1 python run.py -generations {} -output {} -pickle {} -evo {} -seed {} -pop_save_path {} -config "
            "{}\n".format(
                generations, output, pickleo, evo, seed + i, pop_save_path, config))
        file.write(
            "scontrol show job Output/{}/Slurm/$SLURM_JOB_ID     ### write job information to output file".format(
                title))
        file.close()
        call(["sbatch", "Output/{}/Subs/{}.sb".format(title, i)])


if __name__ == "__main__":
    main()
