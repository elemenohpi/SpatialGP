import os.path
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt

from Individual.BaseIndividual import BaseIndividual


class Localization:
    def __init__(self, config):
        self.output_path = config["localization_file"]
        self.data = []
        self.config = config
        self.init_files()

    def init_files(self):
        with open(self.output_path, "w") as file:
            file.truncate()

    def write_log(self, log):
        with open(self.output_path, "a") as file:
            file.write(log)

    def save(self, pop: list[BaseIndividual]):
        for individual in pop:
            pos_str = ""
            for program in individual.programs:
                if program.pos in individual.executed_programs:
                    pos_str += "*"
                pos_str += repr(program.pos) + " "
            pos_str = pos_str[:-1] + "\n"
            self.write_log(pos_str)
        self.write_log("\n")


class RepData:
    def __init__(self):
        self.all_data = []
        self.executed_data = []

    def get_all_localization_info(self, epsilon, min_samples):
        cluster_info = []
        for gen in self.all_data:
            sum_clusters_per_gen = 0
            for indv in gen:
                db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(indv)
                cluster_set = list(set(db.labels_))
                if -1 in cluster_set:
                    cluster_set.remove(-1)
                cluster_count = len(cluster_set)
                sum_clusters_per_gen += cluster_count
            print(sum_clusters_per_gen / len(gen))
            cluster_info.append(sum_clusters_per_gen / len(gen))
        return cluster_info

    def get_executed_localization_info(self, epsilon, min_samples):
        cluster_info = []
        for gen in self.executed_data:
            sum_clusters_per_gen = 0
            for indv in gen:
                db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(indv)
                cluster_set = list(set(db.labels_))
                if -1 in cluster_set:
                    cluster_set.remove(-1)
                cluster_count = len(cluster_set)
                sum_clusters_per_gen += cluster_count
            print(sum_clusters_per_gen / len(gen))
            cluster_info.append(sum_clusters_per_gen / len(gen))
        return cluster_info


class Analysis:
    def __init__(self, epsilon, min_sample):
        self.epsilon = epsilon
        self.min_sample = min_sample

    def analyze_experiment(self, exp_path):
        runs = os.listdir(exp_path)
        all_runs = []
        all_executed_runs = []
        for run in runs:
            if "a40" not in run or "lgp" in run:
                continue
            run_path = os.path.join(exp_path, run)
            print(f"-----------------RUN: {run_path}")
            loc_file_path = os.path.join(run_path, "Location")
            rep_files = os.listdir(loc_file_path)
            run_info = []
            executed_run_info = []
            for index, rep_file in enumerate(rep_files):
                full_file_path = os.path.join(loc_file_path, rep_file)
                rep = self.load(full_file_path)
                print(f"{index + 1}/{len(rep_files)} results for: ", full_file_path)
                localization_info = rep.get_all_localization_info(self.epsilon, self.min_sample)
                print("Executed:")
                executed_localization_info = rep.get_executed_localization_info(self.epsilon, self.min_sample)
                run_info.append(localization_info)
                executed_run_info.append(executed_localization_info)
            zip_str = "zip("
            for info in range(len(run_info)):
                zip_str += f"run_info[{info}], "
            zip_str = zip_str[:-2] + ")"
            zip_str_executed = "zip("
            for info in range(len(executed_run_info)):
                zip_str_executed += f"executed_run_info[{info}], "
            zip_str_executed = zip_str_executed[:-2] + ")"
            average_for_run = [sum(x) / len(x) for x in eval(zip_str)]
            average_for_run_executed = [sum(x) / len(x) for x in eval(zip_str_executed)]
            all_runs.append(average_for_run)
            all_executed_runs.append(average_for_run_executed)
            plt.plot(average_for_run, label=f"{run}")
        plt.xlabel('Generations')
        plt.ylabel('Cluster Frequency')
        plt.title('Comparison of Localized Clusters among Different Configurations of SGP')
        plt.legend()
        plt.show()
        plt.clf()
        plt.close()

        for run in all_executed_runs:
            plt.plot(run, label=f"n/a")
        plt.xlabel('Generations')
        plt.ylabel('Cluster Frequency')
        plt.title('Comparison of Localized Clusters among Different Configurations of SGP (EXECUTED ONLY)')
        plt.legend()
        plt.show()
        plt.close()

    def load(self, path):
        if not os.path.exists(path):
            raise ValueError("Wrong input path value")
        with open(path, "r") as file:
            lines = file.readlines()
        rep = self.to_rep(lines)
        return rep

    def to_rep(self, lines):
        rep = RepData()
        executed_gen_data = []
        all_gen_data = []
        for line in lines:
            if len(line) > 2:
                line = line[:-1]
            executed_program_locs = []
            all_program_locs = []
            if line != "\n":
                tokens = line.split(" ")
                for index, token in enumerate(tokens):
                    if index % 2 == 1:
                        continue
                    elif token == "":
                        continue
                    elif token[0] == "*":
                        # executed
                        temp_token = token[1:] + tokens[index + 1]
                        executed_program_locs.append(eval(temp_token))
                        all_program_locs.append(eval(temp_token))
                        continue
                    # all programs
                    temp_token = token + tokens[index + 1]
                    all_program_locs.append(eval(temp_token))
                executed_gen_data.append(executed_program_locs)
                all_gen_data.append(all_program_locs)
            else:
                rep.executed_data.append(executed_gen_data)
                rep.all_data.append(all_gen_data)
                executed_gen_data = []
                all_gen_data = []
        return rep


if __name__ == "__main__":
    path = "../../HPCC_Experiments/Localization"
    analysis_handler = Analysis(epsilon=60, min_sample=2)
    analysis_handler.analyze_experiment(path)

    pass
