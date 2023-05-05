from Fitness.AbstractFitness import AbstractFitness


class EmptyProblem(AbstractFitness):
    def preprocess(self, indv):
        pass

    def evaluate(self, indv):
        pass

    def postprocess(self, indv):
        pass
