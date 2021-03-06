import time

from tools.General.NeighboursGenerator import *
from tools.General.SolutionGenerator import *
from tools.KBHit import *


class Diversification(Enum):
    Constant = 0
    Fixed = 1
    Memory = 2


class Cycle(Enum):
    AspirationOnly = 0
    WithWeakerNeighbours = 1


class TabuSearch:
    def __init__(self, file, type_t):
        self.__loader = FileLoader()
        self.__loader.load(file, type_t)

        self.__keyboard = KBHit()

        self.__file = file
        self.__type_t = type_t

        self.__data = self.__loader.get_data()
        self.__best_route = []
        self.__best_cost = sys.maxsize
        self.__start_best = []

        # Generator sasiedztwa
        self.__neighbours = NeighboursGenerator(self.__data)

        # Generator rozwiazania
        self.__solution = SolutionGenerator(self.__file, self.__type_t, self.__data)

        # Lista tabu
        self.__tabu_list = []
        self.__cadence = self.__loader.get_number_of_cities() * 3

        # Dla wyjscia z cykli
        self.__weaker_neighbour = -1
        self.__new_best_iterator = 0

        # Dywersyfikacja
        self.__size_of_search = 6
        self.__timer = 0

        # Pamiec dlugoderminowa
        self.__memory = []
        self.__memory_length = self.__loader.get_number_of_cities()

    def calculate(self, type_t, method, cycle, diversification, iterations):
        print("Starting...\n")

        self.__neighbours.change_method(method)
        self.__solution.change_type(type_t)

        route = self.__solution.generate()
        self.__best_route, self.__best_cost = route[0], route[1]
        self.__start_best = route.copy()

        cadence = self.__cadence

        print("Start best: " + route[0].__str__())
        print("with cost: " + route[1].__str__())

        break_time = self.__loader.get_number_of_cities() / 15

        print("\nAlgorithm has been started.\n")
        self.__timer = time.time()
        for i in range(iterations):
            self.__app_manager()

            if (time.time() - self.__timer) > break_time:
                route = self.reset(diversification)
            self.__tabu_list.append([route, cadence])
            route, cadence = self.check_neighbours(route[0], cycle)
            self.tabu_list_routine()

        print("\n")
        self.print_solution()
        print("\n")

    def check_neighbours(self, path, cycle):

        neighbours = self.__neighbours.generate(path, self.__tabu_list)
        neighbours.sort(key=lambda x: x[1])

        # print(self.__size_of_search)

        best_neighbour = None

        for neighbour in neighbours:
            if not self.__neighbours.in_tabu_list(neighbour, self.__tabu_list):
                best_neighbour = neighbour
                break

        print("LOCAL BEST: " + best_neighbour.__str__())

        if not best_neighbour:
            best_neighbour = neighbours[0]

        self.check_for_best(best_neighbour)
        self.long_term_memory(best_neighbour)

        cadence = self.__cadence

        # Po spelnieniu kryterium nastepuje przelamanie cyklu (zwiekszenie obszaru przeszukiwan)
        # Tutaj nastepuje po okreslonej ilosci iteracji bez poprawy
        if self.__new_best_iterator > self.__loader.get_number_of_cities() * 2:
            return self.cycle_breaker(neighbours, cadence, cycle)

        return best_neighbour, cadence

    def check_for_best(self, best_neighbour):
        if best_neighbour[1] < self.__best_cost:
            self.__best_cost = best_neighbour[1]
            self.__best_route = best_neighbour[0]

            self.__weaker_neighbour = -1
            self.__new_best_iterator = 0

            if self.__size_of_search > 6:
                self.__size_of_search = 3

            self.__timer = time.time()

            print("FOUND: " + self.__best_route.__str__())
            print("COST: " + self.__best_cost.__str__())

    def long_term_memory(self, route):
        if self.__memory.__len__() == self.__memory_length:
            self.__memory.sort(key=lambda x: x[1], reverse=True)
            if route[1] < self.__memory[0][1]:
                if route not in self.__memory:
                    self.__memory[0] = route
                    self.__new_best_iterator -= 1
                    self.__timer = time.time()
                else:
                    self.__new_best_iterator += 1
            else:
                self.__new_best_iterator += 1
        else:
            self.__memory.append(route)
            self.__timer = time.time()

    # ---------------------------  CYCLE BREAKER  ---------------------------

    def cycle_breaker(self, neighbours, cadence, cycle):
        if cycle == Cycle.WithWeakerNeighbours:
            return self.weaker_neighbours_and_aspiration(neighbours, cadence)
        elif cycle == Cycle.AspirationOnly:
            return self.aspiration_criterion(neighbours, cadence)

    def weaker_neighbours_and_aspiration(self, neighbours, cadence):
        # Biore gorsze sasiedztwo niezaleznie czy jest w tabu czy nie
        self.__weaker_neighbour += 1
        if self.__weaker_neighbour >= neighbours.__len__():
            self.__weaker_neighbour = 0
        self.__new_best_iterator = self.__loader.get_number_of_cities()
        return neighbours[self.__weaker_neighbour], cadence

    def aspiration_criterion(self, neighbours, cadence):
        self.__new_best_iterator = 0
        tabu_sorted = sorted(self.__tabu_list, key=lambda x: x[0][1])
        if tabu_sorted[0][0][1] < neighbours[0][1]:
            return tabu_sorted[0][0], cadence
        else:
            return neighbours[0], cadence

    # --------------------------------  END  --------------------------------

    def tabu_list_routine(self):
        for tabu_elem in self.__tabu_list:
            tabu_elem[1] -= 1
            if tabu_elem[1] == 0:
                self.__tabu_list.remove(tabu_elem)

    def reset(self, diversification):
        self.__weaker_neighbour = -1
        self.__new_best_iterator = 0
        self.__timer = time.time()

        if diversification == Diversification.Memory:
            return self.__memory[random.randrange(self.__memory.__len__())]
        elif diversification == Diversification.Constant:
            return self.__solution.generate()
        elif diversification == Diversification.Fixed:
            if self.__memory_length > self.__loader.get_number_of_cities():
                self.__memory_length = self.__loader.get_number_of_cities()
                self.__memory = self.__memory[self.__memory_length:]
            if self.__size_of_search > 10:
                self.__size_of_search = 0
            if self.__size_of_search > 7:
                self.__memory_length = self.__memory_length * 2
                self.__solution.change_type(Type.Random)
                route = self.__solution.generate()
            elif self.__size_of_search > 5:
                self.__solution.change_type(Type.GreedyOne)
                route = self.__solution.generate()
            else:
                route = self.__memory[random.randrange(self.__memory.__len__())]

            self.__size_of_search += 1
            return route

        raise Exception("Diversification method named " + diversification.name + " doesn't exist.")

    def __app_manager(self):
        if self.__keyboard.kbhit():
            key = ord(self.__keyboard.getch())
            if key == 32:
                print("\nProgram paused\n")
                self.print_solution()
                while True:
                    key = ord(self.__keyboard.getch())
                    if key == 32:
                        print("\nProgram resumed\n")
                        break
                    elif key == 27:
                        print("\nProgram stopped\n")
                        self.print_solution()
                        exit(0)
            elif key == 27:
                print("\nProgram stopped\n")
                self.print_solution()
                exit(0)

    def clear_values(self):
        self.__best_route = []
        self.__best_cost = sys.maxsize
        self.__start_best = []

        # Lista tabu
        self.__tabu_list = []

        # Dla wyjscia z cykli
        self.__weaker_neighbour = -1
        self.__new_best_iterator = 0

        # Dywersyfikacja
        self.__size_of_search = 6
        self.__timer = 0

        # Pamiec dlugoderminowa
        self.__memory = []
        self.__memory_length = self.__loader.get_number_of_cities()

    def print_solution(self):
        print("Best route: " + self.__best_route.__str__())
        print("with cost: " + self.__best_cost.__str__())
        print("Start best: " + self.__start_best[0].__str__())
        print("with cost: " + self.__start_best[1].__str__())

    def get_solution(self):
        return self.__best_cost, self.__best_route

    def get_data(self):
        return self.__data


if __name__ == "__main__":
    tabu = TabuSearch("test/TSP/pr439.tsp", "COORDS_EUC")
    # TYPE: GREEDY/RANDOM, METHOD: SWAP NEAREST/SWAP WITH OTHERS
    # CYCLE: WITH WEAKER NEIGHBOURS/ASPIRATION ONLY
    # DIVERSIFICATION: FIXED/CONSTANT/MEMORY
    # ITERATIONS: NUMBER
    tm = time.time()
    tabu.calculate(Type.Greedy, Method.InvertOne, Cycle.AspirationOnly, Diversification.Fixed, 3000)
    tm = time.time() - tm
    print("Processing time: " + tm.__str__())
