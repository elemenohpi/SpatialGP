import copy
import pickle
import random

import eletility

from Evolver.AbstractEvolver import AbstractEvolver


class BaseEvolver(AbstractEvolver):
    def __init__(self, config, pop_obj, fitness_obj, interpreter_obj) -> None:
        super().__init__(config, pop_obj, fitness_obj, interpreter_obj)
        self.pop = pop_obj.pop
        self.config = config
        self.generations = int(self.config["generations"])
        self.fitness_obj = fitness_obj
        self.interpreter_obj = interpreter_obj
        self.tournament_size = int(self.config["tournament_size"])
        self.elitism = int(self.config["elitism"])
        self.save_annotation = self.config["save_annotation"]
        self.Files = eletility.Files()
        self.Log = eletility.Log()

    def run(self):

        for generation in range(self.generations):
            log_msg = "\t{}: ".format(generation)
            average_fitness = self.update_population_fitness()
            self.sort_population()
            self.save_pop()
            average_length = 0
            for individual in self.pop:
                average_length += len(individual.programs)
            average_length /= len(self.pop)

            log_msg += "Best Fitness: {}, Average Fitness: {}, Best Individual Size: {}, Average Model Size: {}".\
                format(self.pop[0].fitness, average_fitness, len(self.pop[0].programs), average_length)

            save_log_msg = "{}, {}, {}, {}".format(self.pop[0].fitness, average_fitness, len(self.pop[0].programs),
                                                   average_length)

            if self.save_annotation == "True":
                best_individual_annotation = self.pop[0].get_annotation()
                self.save_best(best_individual_annotation)

            self.save_log(generation, save_log_msg)
            self.Log.I(log_msg)
            if generation == self.generations - 1:
                break
            self.tournament()

        try:
            self.pickle_best(self.pop[0])
        except TypeError:
            pass

        top_right = 0
        bottom_right = 0
        bottom_left = 0
        top_left = 0
        for model in self.pop:
            for program in model.programs:
                if program.pos[0] >= 0 and program.pos[1] >= 0:
                    top_right += 1
                elif program.pos[0] >= 0 and program.pos[1] < 0:
                    bottom_right += 1
                elif program.pos[0] < 0 and program.pos[1] < 0:
                    bottom_left += 1
                elif program.pos[0] < 0 and program.pos[1] >= 0:
                    top_left += 1
        print("Final Positional Counts -> top_right:", top_right, "bot_right:", bottom_right, "bot_left:", bottom_left,
              "top_left:", top_left)
        return self.pop[0].fitness

    def update_population_fitness(self):
        sum_fitness = 0
        for index, individual in enumerate(self.pop):
            # The following lines are meant to be used to speed up the evaluation process slightly with the cost of
            # sacrificing modularity to a small degree
            if not individual.has_discrete_output:
                individual.has_output = False
                for program in individual.programs:
                    if program.program_type == "O":
                        individual.has_output = True
                        break

            fitness = self.fitness_obj.evaluate(individual)

            self.pop[index].fitness = fitness
            sum_fitness += fitness
        return sum_fitness/len(self.pop)

    def sort_population(self):
        settings = self.fitness_obj.settings()
        optimization_goal = settings["optimization_goal"]
        if optimization_goal == "min":
            order = False
        elif optimization_goal == "max":
            order = True
        else:
            raise "Unknown optimization goal"
        self.pop.sort(key=lambda x: x.fitness, reverse=order)

    def update_elite_list(self, elites, new_elite):
        return elites

    def save_best(self, annotation):
        destination = self.config["best_program"]
        disclaimer = "# This code is a generated/synthesized QGP model/program\n# =================================" \
                     "=========== \n\n"
        self.Files.writeTruncate(destination, disclaimer + annotation)

    def save_log(self, gen, log):
        destination = self.config["evo_file"]
        if gen == 0:
            title = "gen,best,avg,best_size,avg_size\n"
            self.Files.writeTruncate(destination, title + repr(gen) + ", " + log + "\n")
        else:
            self.Files.writeLine(destination, repr(gen) + ", " + log)

    def sort_tournament(self, tournament):
        settings = self.fitness_obj.settings()
        optimization_goal = settings["optimization_goal"]
        if optimization_goal == "min":
            order = False
        elif optimization_goal == "max":
            order = True
        else:
            raise "Unknown optimization goal"
        tournament.sort(key=lambda x: x.fitness, reverse=order)
        return tournament

    def tournament(self):
        new_pop = []
        if self.elitism >= 1:
            new_pop = copy.deepcopy(self.pop[:self.elitism])

        for i, indv in enumerate(new_pop):
            indv.individual_index = i

        while len(new_pop) < len(self.pop):
            tournament_list = []
            for i in range(self.tournament_size):
                tournament_list.append(random.choice(self.pop))
            sorted_tournament = self.sort_tournament(tournament_list)
            parent_a, parent_b = copy.deepcopy(sorted_tournament[0]), copy.deepcopy(sorted_tournament[1])

            if random.random() < float(self.config["crossover_rate"]):
                offspring_a, offspring_b = parent_a.crossover(parent_b)
            else:
                offspring_a, offspring_b = parent_a, parent_b

            self.mutate_individual(offspring_b)
            self.mutate_individual(offspring_a)

            offspring_a.individual_index = len(new_pop)
            new_pop.append(offspring_a)
            offspring_b.individual_index = len(new_pop)
            new_pop.append(offspring_b)
        self.pop = copy.deepcopy(new_pop)

    def mutate_individual(self, individual):
        rand = random.random()
        if rand < float(self.config["structural_mutation_rate"]):
            # Structural mutation
            rand = random.random()
            if rand < 0.5:
                if len(individual.programs) <= int(self.config["lgp_size_max"]):
                    individual.add_program()
            else:
                if len(individual.programs) > 1:
                    random_index = random.randint(0, len(individual.programs) - 1)
                    if individual.programs[random_index].program_type != "O":
                        del individual.programs[random_index]
        for program in individual.programs:
            rand = random.random()
            if rand < float(self.config["lgp_mutation_rate"]):
                program.lgp_mutation()
            if rand < float(self.config["structural_mutation_rate"]):
                program.spatial_mutation()
        pass

    def pickle_best(self, obj):
        destination = self.config["best_object"]
        with open(destination, 'wb') as object_file:
            pickle.dump(obj, object_file)

    def pickle_object(self, obj, title):
        destination = title
        with open(destination, 'wb') as object_file:
            pickle.dump(obj, object_file)

    def save_pop(self):
        for index, individual in enumerate(self.pop):
            pop_save_path = self.config["pop_save_path"]
            if pop_save_path[-1] != "/":
                pop_save_path += "/"
            destination = pop_save_path + "model_" + str(index) + ".sgp"
            self.pickle_object(individual, destination)



