import operator
import math
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp
from Regression.DataHandler import DataHandler


# Define new functions
def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


# Define new functions
def protectedSqrt(val):
    try:
        return math.sqrt(val)
    except Exception as e:
        return 1


# Define new functions
def protectedLog(val):
    try:
        return math.log(val)
    except Exception as e:
        return 0


pset = gp.PrimitiveSet('MAIN', 4)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(math.exp, 1)
pset.addPrimitive(math.sin, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(protectedSqrt, 1)
pset.addPrimitive(protectedLog, 1)
pset.addTerminal(1, "1")
pset.addTerminal(2, "2")
pset.addTerminal(3, "3")
pset.addTerminal(5, "4")
pset.addTerminal(-1, "5")

# ############################# Arguments
# pset.renameArguments(ARG0='u')
pset.renameArguments(ARG0='e')
pset.renameArguments(ARG1='d')
pset.renameArguments(ARG2='pi')
pset.renameArguments(ARG3='q')
# ############################# End Arguments

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)


toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, points):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared error between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    sqerrors = []
    for e, d, pi, q in points:
        sqerrors.append((func(e, d, pi, q) - (3 / 5 * q ** 2 / (4 * pi * e * d)))**2)
    return math.fsum(sqerrors) / len(points),


def calc_points():
    points = []
    data_handler = DataHandler('example_data.txt', 4)
    for i in range(30):
        points.append([data_handler.get_data(1), data_handler.get_data(1), data_handler.get_data(1), data_handler.get_data(1)])
    return points


toolbox.register("evaluate", evalSymbReg, points=calc_points())
toolbox.register("select", tools.selTournament, tournsize=10)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


def main():
    random.seed(100)

    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(10)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)

    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats=mstats,
                                   halloffame=hof, verbose=True)
    # print log
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    print(hof[0])
