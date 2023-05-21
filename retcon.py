import copy
import random
import sys


class Retcon:

    def __init__(self, condition_count, condition_depth, selection_pool):
        if condition_depth < 1:
            raise ValueError("Condition depth should be at least 1 or else should be disabled")
        self.conditionals = [">", "<", "==", "True", "False", "<=", ">="]
        self.connectors = ["and", "or"]
        self.statements = []
        self.condition_count = condition_count
        self.condition_depth = condition_depth
        self.selection_pool = selection_pool
        selection_pool = []
        for key in self.selection_pool:
            selection_pool += self.selection_pool[key]
        self.selection_pool = selection_pool

    def generate(self):
        for i in range(self.condition_depth):
            for j in range(self.condition_count):
                operator = random.choice(self.conditionals)
                if operator == "True" or operator == "False":
                    self.statements.append(operator)
                    if j == self.condition_count - 1:
                        ret_val = random.choice(self.selection_pool)
                        self.statements.append(ret_val)
                else:
                    operand1 = random.choice(self.selection_pool)
                    operand2 = random.choice(self.selection_pool)
                    self.statements += [operand1, operator, operand2]
                    if j == self.condition_count - 1:
                        ret_val = random.choice(self.selection_pool)
                        self.statements.append(ret_val)
                if self.condition_count > 1 and j != self.condition_count - 1:
                    connector = random.choice(self.connectors)
                    self.statements.append(connector)

            if i == self.condition_depth - 1:
                self.statements.append(random.choice(self.selection_pool))

    def eval(self, shared_memory):
        statement_counter = 0
        for i in range(self.condition_depth):
            condition_string = ""
            j = 0
            while j < self.condition_count:
                candidate = self.statements[statement_counter]
                if candidate in self.selection_pool:
                    op1 = candidate
                    conditional = self.statements[statement_counter+1]
                    op2 = self.statements[statement_counter+2]
                    if op1 in shared_memory.keys():
                        op1 = shared_memory[op1]
                    if op2 in shared_memory.keys():
                        op2 = shared_memory[op2]
                    condition_string += " {} {} {}".format(op1, conditional, op2)
                    statement_counter += 3
                elif candidate in self.connectors:
                    condition_string += " " + candidate
                    statement_counter += 1
                    j -= 1
                elif candidate in self.conditionals and (candidate == "True" or candidate == "False"):
                    condition_string += " " + candidate
                    statement_counter += 1
                else:
                    raise ValueError("Unknown candidate: ", candidate)
                j += 1
            try:
                if eval(condition_string):
                    ret_val = self.statements[statement_counter]
                    if ret_val in shared_memory.keys():
                        ret_val = shared_memory[ret_val]
                    return float(ret_val)
                else:
                    statement_counter += 1
            except Exception as e:
                msg = f'Condition string error: "{condition_string}"\nMessage: {e}'
                raise Exception(msg)
            if i == self.condition_depth - 1:
                ret_val = self.statements[statement_counter]
                if ret_val in shared_memory.keys():
                    ret_val = shared_memory[ret_val]
                return float(ret_val)
        raise SyntaxError("unreachable statement")

    def mutate(self):
        index = random.randint(0, len(self.statements) - 1)
        candidate = self.statements[index]
        if candidate in self.connectors:
            replacement = random.choice(self.connectors)
        elif candidate in self.selection_pool:
            replacement = random.choice(self.selection_pool)
        elif candidate in self.conditionals:
            replacement = random.choice(self.conditionals)
            if candidate == "True" or candidate == "False":
                if replacement == "True" or replacement == "False":
                    # no change to replacement or the statements list is required because both need same operand count
                    pass
                else:
                    op1 = random.choice(self.selection_pool)
                    op2 = random.choice(self.selection_pool)
                    temp_list = copy.deepcopy(self.statements[:index]) + [op1, replacement, op2] + copy.deepcopy(self.statements[index+1:])
                    self.statements = copy.deepcopy(temp_list)
                    return
            else:
                if replacement == "True" or replacement == "False":
                    self.statements = self.statements[:index-1] + [replacement] + self.statements[index+2:]
                    return
                else:
                    # no change to replacement or the statements list is required because both need same operand count
                    pass
        else:
            print(candidate)
            raise "Unknown candidate type"

        self.statements[index] = replacement

    def annotate(self):
        annotation = "if"
        statement_counter = 0
        for i in range(self.condition_depth):
            condition_string = ""
            j = 0
            while j < self.condition_count:
                candidate = self.statements[statement_counter]
                if candidate in self.selection_pool:
                    op1 = candidate
                    conditional = self.statements[statement_counter + 1]
                    op2 = self.statements[statement_counter + 2]
                    condition_string += " {} {} {}".format(op1, conditional, op2)
                    statement_counter += 3
                elif candidate in self.connectors:
                    condition_string += " " + candidate
                    statement_counter += 1
                    j -= 1
                elif candidate in self.conditionals and (candidate == "True" or candidate == "False"):
                    condition_string += " " + candidate
                    statement_counter += 1
                else:
                    print("unknown candidate: ", candidate)
                    exit()
                j += 1

            annotation += condition_string + ":\n\t"
            annotation += "return " + self.statements[statement_counter] + "\n"
            statement_counter += 1

            if statement_counter == len(self.statements) - 1:
                annotation += "else:\n\t" + "return " + self.statements[statement_counter] + "\n"
                return annotation
            else:
                annotation += "elif"
        print(self.statements)
        raise "unreachable statement"
