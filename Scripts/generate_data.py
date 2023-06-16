import random


def generate_example_data(per, total):
    for i in range(total):
        line = ""
        for _ in range(per):
            if i % 4 == 0:
                # integers
                val = random.randint(1, 20)
            elif i % 4 == 1:
                # no limit float
                val = (random.random() + 0.0001) * 20
            elif i % 4 == 2:
                # small floats
                val = random.random() + 0.0001
            elif i % 4 == 3:
                # mixed integer float
                if random.random() < 0.5:
                    val = random.randint(1, 20)
                else:
                    val = (random.random() + 0.0001) * 20
            line = line + str(round(val, 3)) + " "
        line = line[:-1] + "\n"
        # write to file
        with open("../Fitness/Feynman/example_data_gen.txt", "a") as f:
            f.write(line)


if __name__ == "__main__":
    generate_example_data(10, 100)