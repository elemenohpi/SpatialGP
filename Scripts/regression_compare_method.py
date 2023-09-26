import os


def list_directories(path, key):
    directories = []
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            directories.append(entry)
    parsed_directories = []
    for directory in directories:
        if key is not None:
            if key not in directory:
                continue
        parsed_directories.append(directory)
    return parsed_directories


def list_files(path):
    return os.listdir(path)


TGP_solved = []
LGP_solved = []
Old_SGP_solved = []
SGP_solved = []
total_problem_count = 0


def compare_experiments(path, gen):
    global total_problem_count
    fitness_list = []
    directories = list_directories(path, None)
    problems = {}
    for directory in directories:
        problem_name = directory.split("_")[-1]
        if problem_name not in list(problems.keys()):
            problems[problem_name] = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]  # total, (total_sgp, failed_sgp, solved_sgp) and for LGP and TGP
            total_problem_count += 1
        files = list_files(os.path.join(path, directory, "Evo"))
        for file in files:
            file_path = os.path.join(path, directory, "Evo", file)
            with open(file_path, "r") as evo:
                lines = evo.readlines()
                try:
                    goal_line = lines[gen]
                except IndexError:
                    method = directory.split("_")[0]
                    if "Feynman" in method:
                        problems[problem_name][0][1] += 1
                    elif "LGP" in method:
                        problems[problem_name][1][1] += 1
                    elif "TGP" in method:
                        problems[problem_name][2][1] += 1
                    elif "SGP" in method:
                        problems[problem_name][3][1] += 1
                    continue

                tokens = goal_line.replace(" ", "").split(",")
                try:
                    fitness_list.append([file_path, float(tokens[1])])
                except:
                    last_line = lines[-2]
                    tokens = last_line.replace(" ", "").split(",")
                    fitness_list.append([file_path, float(tokens[1])])
                method = directory.split("_")[0]
                if float(tokens[1]) == 0:
                    if "Feynman" in method:
                        problems[problem_name][0][2] += 1
                    elif "LGP" in method:
                        problems[problem_name][1][2] += 1
                    elif "TGP" in method:
                        problems[problem_name][2][2] += 1
                    elif "SGP" in method:
                        problems[problem_name][3][2] += 1
                if "Feynman" in method:
                    problems[problem_name][0][0] += 1
                elif "LGP" in method:
                    problems[problem_name][1][0] += 1
                elif "TGP" in method:
                    problems[problem_name][2][0] += 1
                elif "SGP" in method:
                    problems[problem_name][3][0] += 1
    sorted_list = sorted(fitness_list, key=lambda x: x[1])
    total_solved = 0
    avg_fitness = 0
    for element in sorted_list:
        # print(f"{element[1]} for {element[0]}")
        if float(element[1]) == 0:
            total_solved += 1
        avg_fitness += float(element[1])

    # print(f"Total solved: {total_solved}, avg_fitness: {avg_fitness/len(sorted_list)}")
    print("==========================================================================")
    for problem in problems:
        print(f"{problem} SGP=> total: {problems[problem][3][0]} solved: {problems[problem][3][2]} failed: {problems[problem][3][1]} ")
        print(
            f"{problem} OLD_SGP=> total: {problems[problem][0][0]} solved: {problems[problem][0][2]} failed: {problems[problem][0][1]} ")
        print(
            f"{problem} LGP=> total: {problems[problem][1][0]} solved: {problems[problem][1][2]} failed: {problems[problem][1][1]} ")
        print(
            f"{problem} TGP=> total: {problems[problem][2][0]} solved: {problems[problem][2][2]} failed: {problems[problem][2][1]} ")
        print("==========================================================================")
        if problems[problem][0][2] > 0:
            Old_SGP_solved.append(problem)
        if problems[problem][1][2] > 0:
            LGP_solved.append(problem)
        if problems[problem][2][2] > 0:
            TGP_solved.append(problem)
        if problems[problem][3][2] > 0:
            SGP_solved.append(problem)


if __name__ == "__main__":
    for i in range(1, 10):
        compare_experiments(f"../../Results/F{i}", 100)
    # compare_experiments("../../Results/F1/", 99)
    print("Problems solved by SGP:")
    [print(x, end=" ") for x in SGP_solved]
    print()
    print(f"Count: {len(SGP_solved)}")
    print("Problems solved by the Old SGP:")
    [print(x, end=" ") for x in Old_SGP_solved]
    print()
    print(f"Count: {len(Old_SGP_solved)}")
    print("Problems solved by LGP:")
    [print(x, end=" ") for x in LGP_solved]
    print()
    print(f"Count: {len(LGP_solved)}")
    print("Problems solved by TGP:")
    [print(x, end=" ") for x in TGP_solved]
    print()
    print(f"Count: {len(TGP_solved)}")
    print("Total problem count: ", total_problem_count)

# II242. Solved three times by LGP

# SGP is better: I276, II154, II155
