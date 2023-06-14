import copy
import pickle


class TranslationHandler:
    def __init__(self):
        pass

    def formulize_individual(self, path_to_model):
        pickled_object = open(path_to_model, "rb")
        model_object = pickle.load(pickled_object)

        simplified_model = self.simplify_individual(model_object)

        fitness, execution_info, additional_info = model_object.get_execution_info()
        s_fitness, s_execution_info, s_additional_info = simplified_model.get_execution_info()

        print("################ Simplification Step ################")
        print(f"Original Fitness: {fitness} Simplified Fitness: {s_fitness}")
        print(f"Original Execution Info: {execution_info} Simplified Fitness: {s_execution_info}")
        print(f"Original Add Info: {additional_info} Simplified Add Info: {s_additional_info}")
        print(
            f"Original Program Count: {len(model_object.programs)} Simplified Program Count: "
            f"{len(simplified_model.programs)}")

        print("\n################ Sequencing Step ################")
        statements = self.sequence_model(s_execution_info, simplified_model)

        for statement in statements:
            print(statement.annotate())

    def simplify_individual(self, model):
        model_class = type(model)
        program_class = type(model.programs[0])
        simplified_model = model_class(model.config, program_class)

        fitness, execution_info, additional_info = model.get_execution_info()
        effective_programs = execution_info[0]

        for program_index in effective_programs:
            simplified_model.programs.append(model.programs[program_index])

        simplified_model = self.simplify_statements(simplified_model)
        return simplified_model

    def simplify_statements(self, model):
        simplified_model = copy.deepcopy(model)
        for program in simplified_model.programs:
            program.statements = [program.statements[-1]]

        for p_index, program in enumerate(model.programs):
            for s_index, statement in enumerate(program.statements):
                if statement == program.statements[-1]:
                    continue
                copycat = copy.deepcopy(model)
                del copycat.programs[p_index].statements[s_index]
                fitness, _, _ = model.get_execution_info()
                n_fitness, _, _ = copycat.get_execution_info()
                if fitness != n_fitness:
                    simplified_model.programs[p_index].statements.insert(
                        len(simplified_model.programs[p_index].statements) - 1, statement)

        return simplified_model

    def sequence_model(self, s_execution_info, simplified_model):
        statements = []
        for program_index in s_execution_info[0]:
            for statement in simplified_model.programs[program_index].statements:
                if statement != simplified_model.programs[program_index].statements[-1]:
                    statements.append(statement)
        return statements


if __name__ == "__main__":
    path = "../Output/Population/model_0.sgp"
    handler = TranslationHandler()
    handler.formulize_individual(path)
