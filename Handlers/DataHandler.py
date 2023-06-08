import os


class DataHandler:
    def __init__(self, file_name):
        self.counter = -1
        if not os.path.isfile(file_name):
            raise ValueError(f"{file_name} does not exist.")
        self.file_name = file_name

    def get_line(self):
        self.counter += 1
        with open(self.file_name, 'r') as file:
            for i, line in enumerate(file):
                if i == self.counter:
                    return line
        return None

    def get_data(self, n):
        line = self.get_line()
        if line is None:
            raise AttributeError(f"There are not enough lines in file {self.file_name} to retrieve the requested data.")
        tokens = line.split(" ")
        if len(tokens) < n:
            raise AttributeError(f"There are not enough data in a line in file {self.file_name} to retrieve the "
                                 f"requested data")
        data_list = []
        for token in tokens:
            data_list.append(float(token))
            if len(data_list) == n:
                return data_list


