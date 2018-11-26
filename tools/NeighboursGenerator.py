from enum import Enum
import random
import sys


class Method(Enum):
    SwapNearest = 0
    SwapOne = 1
    Swap = 2
    InsertOne = 3
    Insert = 4
    InvertOne = 5
    Invert = 6
    Mixed = 7
    TwoOpt = 8
    ThreeOpt = 9


class NeighboursGenerator:
    def __init__(self, data):
        self.__method = Method.Invert
        self.__data = data
        self.__number_of_cities = data.__len__()

    def change_method(self, method):
        self.__method = method

    def get_method(self):
        return self.__method

    def in_tabu_list(self, path, tabu):
        for elem in tabu:
            if path in elem:
                return True
        return False

    def generate(self, path, tabu):
        parent_path = path.copy()
        index = parent_path.pop(-1)
        parent_path.pop(0)
        neighbours = []

        if self.__method == Method.SwapNearest:
            for i in range(1, parent_path.__len__()):
                neighbour = parent_path.copy()
                neighbour[i - 1], neighbour[i] = neighbour[i], neighbour[i - 1]
                neighbour = [index] + neighbour + [index]
                # if not self.in_tabu_list(neighbour, tabu):
                neighbour_cost = 0
                for j in range(1, neighbour.__len__()):
                    neighbour_cost += self.__data[neighbour[j - 1]][neighbour[j]]

                neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.SwapOne:
            swap_index = random.randrange(self.__number_of_cities - 1)
            for i in range(parent_path.__len__()):
                neighbour = parent_path.copy()
                neighbour[swap_index], neighbour[i] = neighbour[i], neighbour[swap_index]
                neighbour = [index] + neighbour + [index]
                # if not self.in_tabu_list(neighbour, tabu):
                neighbour_cost = 0
                for j in range(1, neighbour.__len__()):
                    neighbour_cost += self.__data[neighbour[j - 1]][neighbour[j]]

                neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.Swap:
            for i in range(parent_path.__len__()):
                for j in range(i + 1, parent_path.__len__()):
                    neighbour = parent_path.copy()
                    neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
                    neighbour = [index] + neighbour + [index]
                    # if not self.in_tabu_list(neighbour, tabu):
                    neighbour_cost = 0
                    for k in range(1, neighbour.__len__()):
                        neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

                    neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.InsertOne:
            insert_index = random.randrange(self.__number_of_cities - 1)
            for i in range(parent_path.__len__()):
                if i != insert_index:
                    neighbour = parent_path.copy()
                    item = neighbour.pop(insert_index)
                    neighbour.insert(i, item)
                    neighbour = [index] + neighbour + [index]
                    # if not self.in_tabu_list(neighbour, tabu):
                    neighbour_cost = 0
                    for k in range(1, neighbour.__len__()):
                        neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

                    neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.Insert:
            for i in range(parent_path.__len__()):
                for j in range(i + 1, parent_path.__len__()):
                    neighbour = parent_path.copy()
                    item = neighbour.pop(i)
                    neighbour.insert(j, item)
                    neighbour = [index] + neighbour + [index]
                    # if not self.in_tabu_list(neighbour, tabu):
                    neighbour_cost = 0
                    for k in range(1, neighbour.__len__()):
                        neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

                    neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.InvertOne:
            invert_index = random.randrange(self.__number_of_cities - 1)
            for i in range(parent_path.__len__()):
                if i != invert_index:
                    neighbour = parent_path.copy()
                    if i > invert_index:
                        neighbour[invert_index:i + 1] = reversed(neighbour[invert_index:i + 1])
                    elif i < invert_index:
                        neighbour[i:invert_index + 1] = reversed(neighbour[i:invert_index + 1])
                    neighbour = [index] + neighbour + [index]
                    # if not self.in_tabu_list(neighbour, tabu):
                    neighbour_cost = 0
                    for k in range(1, neighbour.__len__()):
                        neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

                    neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.Invert:
            for i in range(parent_path.__len__()):
                for j in range(i + 1, parent_path.__len__()):
                    neighbour = parent_path.copy()
                    neighbour[i:j + 1] = reversed(neighbour[i:j + 1])
                    neighbour = [index] + neighbour + [index]
                    # if not self.in_tabu_list(neighbour, tabu):
                    neighbour_cost = 0
                    for k in range(1, neighbour.__len__()):
                        neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

                    neighbours.append([neighbour, round(neighbour_cost, 2)])

        elif self.__method == Method.ThreeOpt:
            for i in range(parent_path.__len__()):
                for j in range(i + 1, parent_path.__len__()):
                    for k in range(j + 1, parent_path.__len__()):
                        neighbour = parent_path.copy()
                        neighbour[i:j + 1] = reversed(neighbour[i:j + 1])
                        neighbour[j:k + 1] = reversed(neighbour[j:k + 1])

                        neighbour = [index] + neighbour + [index]
                        # if not self.in_tabu_list(neighbour, tabu):
                        neighbour_cost = 0
                        for l in range(1, neighbour.__len__()):
                            neighbour_cost += self.__data[neighbour[l - 1]][neighbour[l]]

                        neighbours.append([neighbour, round(neighbour_cost, 2)])

        else:
            raise Exception("Method named " + self.__method.name + " doesn't exist.")

        return neighbours

    def generate_one(self, path, i=0, j=0):
        neighbour = path.copy()
        index = neighbour.pop(-1)
        neighbour.pop(0)

        while i == j:
            i = random.randrange(neighbour.__len__())
            j = random.randrange(neighbour.__len__())

        if self.__method == Method.SwapNearest:
            if i == 0:
                neighbour[i], neighbour[i + 1] = neighbour[i + 1], neighbour[i]
            else:
                neighbour[i - 1], neighbour[i] = neighbour[i], neighbour[i - 1]

            neighbour = [index] + neighbour + [index]
            neighbour_cost = 0
            for j in range(1, neighbour.__len__()):
                neighbour_cost += self.__data[neighbour[j - 1]][neighbour[j]]

        elif self.__method == Method.Swap:
            neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
            neighbour = [index] + neighbour + [index]
            neighbour_cost = 0
            for k in range(1, neighbour.__len__()):
                neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

        elif self.__method == Method.Insert:
            item = neighbour.pop(i)
            neighbour.insert(j, item)
            neighbour = [index] + neighbour + [index]
            neighbour_cost = 0
            for k in range(1, neighbour.__len__()):
                neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

        elif self.__method == Method.Invert:
            if i < j:
                neighbour[i:j + 1] = reversed(neighbour[i:j + 1])
            else:
                neighbour[j:i + 1] = reversed(neighbour[j:i + 1])
            neighbour = [index] + neighbour + [index]
            neighbour_cost = 0
            for k in range(1, neighbour.__len__()):
                neighbour_cost += self.__data[neighbour[k - 1]][neighbour[k]]

        elif self.__method == Method.Mixed:
            methods = [Method.Swap, Method.Insert, Method.Invert]
            neighbour = [index] + neighbour + [index]
            best_route = [[], sys.maxsize]
            for k in range(3):
                self.change_method(methods[k])
                temp = self.generate_one(neighbour, i, j)
                if temp[1] < best_route[1]:
                    best_route = temp
            neighbour = best_route[0]
            neighbour_cost = best_route[1]

        elif self.__method == Method.ThreeOpt:
            i = random.randrange(neighbour.__len__() - 2)
            j = random.randrange(i + 1, neighbour.__len__() - 1)
            k = random.randrange(j + 1, neighbour.__len__())

            neighbour[i:j + 1] = reversed(neighbour[i:j + 1])
            neighbour[j:k + 1] = reversed(neighbour[j:k + 1])

            neighbour = [index] + neighbour + [index]
            neighbour_cost = 0
            for l in range(1, neighbour.__len__()):
                neighbour_cost += self.__data[neighbour[l - 1]][neighbour[l]]

        else:
            raise Exception("Method named " + self.__method.name + " doesn't exist.")

        return [neighbour, round(neighbour_cost, 2)]
