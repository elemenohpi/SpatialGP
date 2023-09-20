import os
import numpy as np


class UsefulDataHandler:
    def __init__(self):
        self.Thi = None
        self.Tco = None
        self.up = None
        self.Vc = None
        self.uc = None
        self.uh = None
        self.counter = 0

    def read_data(self, file):
        if not os.path.isfile(file):
            raise ValueError(f"{file} does not exist.")
        data = np.loadtxt(file, delimiter=',')
        self.uc = data[:, 0]
        self.uh = data[:, 1]
        self.up = data[:, 2]
        self.Vc = data[:, 3]
        self.Tco = data[:, 4]
        self.Thi = data[:, 5]

    def get_data(self):
        return_array = [self.uc[self.counter], self.uh[self.counter], self.up[self.counter], self.Vc[self.counter],
                        self.Tco[self.counter], self.Thi[self.counter]]
        self.counter += 1
        return return_array

    def get_length(self):
        return len(self.uc)

    def reset(self):
        self.counter = 0

