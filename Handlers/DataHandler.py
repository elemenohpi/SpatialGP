import os


class DataHandler:
    def __init__(self, file_name, fitness_obj):
        self.counter = 0

        if not os.path.isfile(file_name):
            raise ValueError(f"{file_name} does not exist.")

        self.fitness_obj = fitness_obj
        self.data = self.read_data(file_name)

    def get_data(self, n):
        return_data = self.data[self.counter:self.counter+n]
        self.counter += n
        if len(return_data) == 1:
            return return_data[0]
        return return_data

    def read_data(self, file_path):
        data_size = self.calculate_data_size()
        numbers = []

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    numbers += [float(num) for num in line.split()]
                if len(numbers) >= data_size:
                    numbers = numbers[:data_size]
                    break

        return numbers

    def is_array(self, input_element):
        tokens = input_element.split("[")
        if len(tokens) > 1:
            return True
        else:
            return False

    def get_array_length(self, input_element):
        tokens = input_element.split("[")
        length = int(tokens[1].split("]")[0])
        return length

    def calculate_data_size(self):
        input_scheme = self.fitness_obj.inputs()
        evaluation_count = self.fitness_obj.evaluation_count
        per_evaluation_data = 0
        for element in input_scheme:
            if self.is_array(element):
                per_evaluation_data += self.get_array_length(element)
            else:
                per_evaluation_data += 1
        data_size = per_evaluation_data * evaluation_count
        return data_size

    def reset(self):
        self.counter = 0
