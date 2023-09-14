# A script to check the average number of evolutionary generations logged in each experiment folder
# Link to the directories should be manually provided
import os

import pandas as pd

exp_path = "../../Results/F6"
key = ""

exp_dirs = os.listdir(exp_path)

for directory in exp_dirs:
    solved_files = {
        "gen": [],
        "file": []
    }

    incomplete_files = {
        "gen": [],
        "file": []
    }

    if key not in directory:
        continue
    directory_path = os.path.join(exp_path, directory)
    if os.path.isdir(directory_path):
        evo_path = os.path.join(directory_path, "Evo")
        evo_files = os.listdir(evo_path)
        for file in evo_files:
            if file.endswith(".csv"):
                file_path = os.path.join(evo_path, file)
                df = pd.read_csv(file_path)
                last_gen = df.iloc[-1]["gen"]
                best = df.iloc[-1]["best"]
                if best == 0:
                    solved = True
                else:
                    solved = False
                if solved:
                    min_index = df[df["best"] == 0].index.min()
                else:
                    min_index = "n/a"
                if solved:
                    solved_files["gen"].append(min_index)
                    solved_files["file"].append(file)
                if last_gen < 999:
                    incomplete_files["gen"].append(last_gen)
                    incomplete_files["file"].append(file)
                # print(f"File: {file} \tSolved: {solved} \tSolution Index: {min_index} \tBest Fitness: {best} "
                #       f"\tLast Gen: {last_gen}")
        solution_count = len(solved_files["gen"])
        incomplete_count = len(incomplete_files["gen"])
        if solution_count > 0:
            average_solution_gen = round(sum(solved_files["gen"]) / solution_count)
        else:
            average_solution_gen = "n/a"

        if incomplete_count > 0:
            average_incomplete_gen = round(sum(incomplete_files["gen"]) / incomplete_count)
        else:
            average_incomplete_gen = "n/a"

        min_solution_gen = "n/a"
        if len(solved_files["gen"]) > 0:
            min_solution_gen = min(solved_files['gen'])

        min_incomplete_gen = "n/a"
        if len(incomplete_files["gen"]) > 0:
            min_incomplete_gen = min(incomplete_files['gen'])
        print(f"Directory: {directory:<15} "
              f"\tSolution Count: {solution_count:<2} "
              f"\tAverage Solution Gen: {average_solution_gen:<4}"
              f"\tMin Solution Gen: {min_solution_gen:<4}"
              f"\tIncomplete Count: {incomplete_count:<2} "
              f"\tAverage Incomplete Gen: {average_incomplete_gen:<4}"
              f"\tMin Incomplete Gen: {min_incomplete_gen:<4}"
              )


