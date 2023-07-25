import random
from multiprocessing import Pool


def mutate(config, model):
    rand = random.random()
    if rand < float(config["structural_mutation_rate"]):
        # Add program
        if len(model.programs) <= int(config["lgp_size_max"]):
            model.add_program()
    rand = random.random()
    if rand < float(config["structural_mutation_rate"]):
        # Remove program
        if len(model.programs) > 1:
            random_index = random.randint(0, len(model.programs) - 1)
            if model.programs[random_index].program_type != "O":
                del model.programs[random_index]

    for program in model.programs:
        program.lgp_mutation()
        program.spatial_mutation()
        # rand = random.random()
        # if rand < float(config["lgp_mutation_rate"]):
        #     program.lgp_mutation()
        # rand = random.random()
        # if rand < float(config["structural_mutation_rate"]):
        #     program.spatial_mutation()






