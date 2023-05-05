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

    def run(self):
        best_individual = None
        elites = [None for _ in range(self.elitism)]

        for generation in range(self.generations):
            log_msg = "\t{}: ".format(generation)
            avg_fitness = self.update_population_fitness()
            exit("manual")
            self.sort_population()

            elites = copy.deepcopy(self.pop[0:self.elitism])
            if best_individual is None or elites[0].fitness != best_individual.fitness:
                best_individual = copy.deepcopy(elites[0])
                if self.config["make_viz_data"] == "True":
                    self.log_individual_for_visualization(best_individual)
                self.best_indv_change_counter += 1
            avg_fitness /= len(self.pop)

            alen = 0
            for indv in self.pop:
                alen += len(indv.programs)
            alen /= len(self.pop)

            log_msg += "best Fitness: {}, info1: {}, info2: {}, avg: {}, blen: {}, alen: {}".format(elites[0].fitness,
                                                                                                    elites[0].rvalue,
                                                                                                    elites[0].rmse,
                                                                                                    avg_fitness, len(
                    elites[0].programs), alen)
            save_log_msg = "{}, {}, {}, {}".format(elites[0].fitness, elites[0].rvalue, elites[0].rmse, avg_fitness)
            # ToDo:: Save the best individual
            best_individual_annotation = elites[0].annotate_program()

            self.save_best(best_individual_annotation)
            self.save_log(gen, save_log_msg)
            self.Log.I(log_msg)
            # for elite in elites:
            #     self.Log.Yprint(elite.fitness)
            # print()

            self.tournament(elites)
            # for indv in self.pop:
            #     print(indv.fitness, end=" ")
            #     if indv.fitness == 0:
            #         self.Log.Rprint("wtf?")
            # print()
        # best_individual.annotate_program(True)
        try:
            self.pickle_object(best_individual)
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
        if elites[0] is not None:
            return elites[0].fitness
        return None

    def update_population_fitness(self):
        sum_fitness = 0
        for index, individual in enumerate(self.pop):
            try:
                fitness, rvalue, rmse = self.fitness_obj.evaluate(individual)
                exit("manual")
            except OverflowError:
                print("overflow error")
                # ToDo:: fix this
                if self.config["optimization_goal"] == "min":
                    fitness = sys.float_info.max
                    rvalue = 0
                    rmse = 0
                elif self.config["optimization_goal"] == "max":
                    fitness = sys.float_info.max * -1
                    rvalue = 0
                    rmse = 0
                else:
                    raise "Unknown optimization goal"
            # misleading naming convention
            # print(fitness, rvalue, rmse)
            self.pop[index].fitness = fitness
            self.pop[index].rvalue = rvalue
            self.pop[index].rmse = rmse
            sum_fitness += fitness

        # print(datetime.datetime.now() - start)
        return sum_fitness

