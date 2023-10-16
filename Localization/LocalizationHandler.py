import os.path

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


class Analysis:
    def __init__(self):
        pass

    def load(self, path):
        if not os.path.exists(path):
            raise ValueError("Wrong input path value")
        with open(path, "r") as file:
            lines = file.readlines()
            gens = self.to_gens(lines)

    def to_gens(self, lines):
        gens = []

        return gens


if __name__ == "__main__":
    pass

