import copy
import random
import math


def find_random_spatial_position(config):
    init_radius = float(config["init_radius"])
    if config["topology"] == "circle":
        return get_point_on_circle(init_radius)
    elif config["topology"] == "ring":
        return get_point_on_ring(init_radius)
    elif config["topology"] == "line":
        return get_point_on_line(init_radius)
    return None


def get_point_on_line(d):
    x = random.uniform(-d, d)  # Generate a random x-coordinate within the range [-d, d]
    y = 0  # Since the point lies on the x-axis, y-coordinate is 0
    return x, y


def get_point_on_ring(r):
    angle = 2 * math.pi * random.random()  # Generate a random angle between 0 and 2*pi
    x = r * math.cos(angle)  # Calculate x-coordinate
    y = r * math.sin(angle)  # Calculate y-coordinate
    return x, y


def get_point_on_circle(r):
    # Generate a random angle between 0 and 2pi
    theta = random.uniform(0, 2 * math.pi)
    # Generate a random radius between 0 and r
    s = r * math.sqrt(random.uniform(0, 1))
    # Calculate the x and y coordinates
    x = s * math.cos(theta)
    y = s * math.sin(theta)
    return x, y


def distance_to_pos(source_pos, pos):
    return math.sqrt((pos[0] - source_pos[0]) ** 2 + (pos[1] - source_pos[1]) ** 2)


########################################################################################################
def circle_crossover(a, b, config):
    init_radius = float(config["init_radius"])
    radius = int(init_radius / 2)
    rand_x, rand_y = find_random_spatial_position(config)
    a_inside_programs = []
    a_outside_programs = []
    b_inside_programs = []
    b_outside_programs = []
    a_output_programs = []
    b_output_programs = []
    max_program_size = int(config["lgp_size_max"])
    for program in a.programs:
        if not a.has_discrete_output:
            # The program does not have discrete outputs
            discrete_output_condition = True
        else:
            # The program has discrete outputs
            discrete_output_condition = not (program.program_type == "O")
            if program.program_type == "O":
                # Basically, we let individual A to have its own output programs without any changes
                a_output_programs.append(program)
        # This condition is set to be True if the program does not have discrete outputs or if the program type is I
        if discrete_output_condition:
            if distance_to_pos(program.pos, (rand_x, rand_y)) <= radius:
                a_inside_programs.append(program)
            else:
                a_outside_programs.append(program)
    for program in b.programs:
        if not b.has_discrete_output:
            discrete_output_condition = True
        else:
            discrete_output_condition = not (program.program_type == "O")
            if program.program_type == "O":
                b_output_programs.append(program)
        if discrete_output_condition:
            if distance_to_pos(program.pos, (rand_x, rand_y)) <= radius:
                b_inside_programs.append(program)
            else:
                b_outside_programs.append(program)

    indv_blueprint = type(a)
    prog_blueprint = type(a.programs[0])

    offspring_a = indv_blueprint(config, prog_blueprint)
    offspring_b = indv_blueprint(config, prog_blueprint)

    ab_inside_outside_programs = a_inside_programs + b_outside_programs
    ba_inside_outside_programs = a_outside_programs + b_inside_programs

    if len(ab_inside_outside_programs) > max_program_size:
        ab_inside_outside_programs = copy.deepcopy(ab_inside_outside_programs[:max_program_size - 1])

    if len(ba_inside_outside_programs) > max_program_size:
        ba_inside_outside_programs = copy.deepcopy(ba_inside_outside_programs[:max_program_size - 1])

    offspring_a.programs = ab_inside_outside_programs + a_output_programs
    offspring_b.programs = ba_inside_outside_programs + b_output_programs
    offspring_a = copy.deepcopy(offspring_a)
    offspring_b = copy.deepcopy(offspring_b)

    if len(offspring_a.programs) == 0:
        offspring_a = copy.deepcopy(a)
    elif len(offspring_b.programs) == 0:
        offspring_b = copy.deepcopy(b)

    return offspring_a, offspring_b

