from tools.General.SolutionGenerator import *
from tools.Genetic.PopulationCreator import *
from tools.Genetic.Mutation import Mutation, Type as MType
from tools.FileLoader import *
from tools.KBHit import *
import sys
import matplotlib.pyplot as plt


class Selection(Enum):
    Tournament = 0
    Random = 1


class Genetic:
    def __init__(self, file, type_t):
        self.__loader = FileLoader()
        self.__loader.load(file, type_t)

        self.__keyboard = KBHit()

        self.__file = file
        self.__type_t = type_t

        self.__data = self.__loader.get_data()
        self.__best_route = []
        self.__best_cost = sys.maxsize
        self.__start_best = [None, None]

        self.__local_best_cost = sys.maxsize

        self.__solution = SolutionGenerator(self.__file, self.__type_t, self.__data)
        self.__generation = PopulationCreator(self.__data)
        self.__mutation = Mutation(self.__data)

        self.__radioactivity = 0
        self.__solution_in_time = []

    def calculate(self, iterations, population_size, mutation_type, mutation_reset, selection_type,
                  tournament_size=5, arg=0):

        population = []
        self.__solution.change_type(Type.Random)
        for i in range(population_size - 1):
            population.append(self.__solution.generate())

        self.__solution.change_type(Type.GreedyOne)
        actual_solution = self.__solution.generate()
        population.append(actual_solution)

        self.__best_route, self.__best_cost, self.__start_best = actual_solution[0], actual_solution[1], actual_solution

        # PLOTS INITIALIZE
        plot_data, plot_mutation, plot_number = self.plot_init(mutation_reset)

        self.__mutation.change_type(mutation_type)

        for i in range(iterations):
            self.__app_manager()
            self.__radioactivity = 0

            sorted_population = sorted(population, key=lambda x: x[1])
            sorted_population = sorted_population[:population_size]

            # PLOTS
            self.go_plot(sorted_population, plot_data, plot_mutation, plot_number)

            self.check_for_best(sorted_population[0])

            # TEST
            self.start_test(i)

            new_generation = []
            for _ in range(population_size):
                male = self.select_parent(population, selection_type, tournament_size)
                female = self.select_parent(population, selection_type, tournament_size)

                first_child, second_child = self.__generation.create(male[0], female[0])
                new_generation.extend([first_child, second_child])

            self.__mutation.mutation_routine(new_generation, self.__radioactivity + 1)

            if self.__mutation.get_mutation_chance() >= mutation_reset:
                population = new_generation
                population.append(self.__solution.generate())
                self.__local_best_cost = population[-1][1]
                self.__mutation.set_mutation_chance(0.001)
            else:
                population = new_generation + sorted_population

        print("\n\n")
        self.print_solution()

        # FOR ANALYZE

        # fig1 = plt.figure(1)
        # plt.plot(range(plot_data.__len__()), plot_data)
        # plt.xlabel("Generation")
        # plt.ylabel("Cost")
        # # plt.savefig("test/GeneticTest/data" + arg.__str__() + ".png")
        # plt.close(fig1)
        # fig2 = plt.figure(2)
        # plt.plot(plot_number, plot_mutation)
        # plt.xlabel("Mutation chance")
        # plt.ylabel("Number of good mutations")
        # # plt.savefig("test/GeneticTest/mutation" + arg.__str__() + ".png")
        # plt.close(fig2)
        # plt.show()

    @staticmethod
    def select_parent(population, selection, size):
        group = []
        if selection == Selection.Tournament:
            index = []
            while index.__len__() < size:
                rand = random.randrange(population.__len__())
                if rand not in index:
                    index.append(rand)
                    group.append(population[rand])

            group.sort(key=lambda x: x[1])

        elif selection == Selection.Random:
            parent_one = random.randrange(population.__len__())
            group.append(population[parent_one])

        else:
            raise Exception("Cannot find that kind of selection.")

        return group[0]

    def check_for_best(self, best_person):
        if best_person[1] < self.__local_best_cost:
            self.__local_best_cost = best_person[1]

            print("FOUND LOCAL BEST: " + best_person[0].__str__())
            print("COST: " + best_person[1].__str__())

            print("Mutation ratio: " + self.__mutation.get_ratio().__str__())

            if best_person[1] < self.__best_cost:
                self.__best_cost = best_person[1]
                self.__best_route = best_person[0]
                self.__radioactivity -= 20
                print("FOUND BEST: " + self.__best_route.__str__())
                print("COST: " + self.__best_cost.__str__())

            self.__radioactivity -= 8

    def __app_manager(self):
        if self.__keyboard.kbhit():
            key = ord(self.__keyboard.getch())
            if key == 32:
                print("Program paused")
                self.print_solution()
                while True:
                    key = ord(self.__keyboard.getch())
                    if key == 32:
                        print("Program resumed")
                        break
                    elif key == 27:
                        print("Program stopped")
                        self.print_solution()
                        exit(0)
            elif key == 27:
                print("Program stopped")
                self.print_solution()
                exit(0)

    def clear_values(self):
        self.__best_route = []
        self.__best_cost = sys.maxsize
        self.__start_best = [None, None]
        self.__local_best_cost = sys.maxsize
        self.__radioactivity = 0
        self.__solution_in_time = []

    def print_solution(self):
        print("Best route: " + self.__best_route.__str__())
        print("with cost: " + self.__best_cost.__str__())
        print("Start best: " + self.__start_best[0].__str__())
        print("with cost: " + self.__start_best[1].__str__())

    def get_population_number(self):
        return self.__loader.get_number_of_cities()

    def get_solution(self):
        return self.__best_cost, self.__best_route

    def get_solution_in_time(self):
        return self.__solution_in_time

    def get_data(self):
        return self.__data

    def plot_init(self, mutation_reset):
        plot_data = [self.__best_cost]
        plot_number = []
        number_creator = 0.001
        while number_creator <= mutation_reset:
            plot_number.append(number_creator)
            number_creator += 0.001
            number_creator = round(number_creator, 3)
        plot_mutation = [0] * plot_number.__len__()

        return plot_data, plot_mutation, plot_number

    def go_plot(self, sorted_population, plot_data, plot_mutation, plot_number):
        if sorted_population[0][1] < self.__local_best_cost:
            plot_mutation[plot_number.index(self.__mutation.get_mutation_chance())] += 1

        plot_data.append(sorted_population[0][1])

    def start_test(self, i):
        if (i + 1) % 500 == 0:
            self.__solution_in_time.append(self.__best_cost)


if __name__ == "__main__":
    alg = Genetic("test/TSP/gr137.tsp", "COORDS_GEO")
    pop_size = 100
    # Iterations, Population size, Mutation type, Mutation_reset (chance), Selection type, Tournament size, Plot number
    # alg.calculate(5000, pop_size, MType.Invert, 0.05, Selection.Tournament, int(pop_size * 0.12))

    analyze_points = 10
    result = open("test/GeneticTest/Wyniki.txt", "w+")
    result.write("--[500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]--\n")
    result.write("-------------------GENETIC-INVERT-TOURNAMENT-------------------\n")
    avg_cost = [0] * analyze_points
    for k in range(10):
        alg.calculate(5000, pop_size, MType.Invert, 0.05, Selection.Tournament, int(pop_size*0.12), k)
        costs = alg.get_solution_in_time()
        for l in range(costs.__len__()):
            avg_cost[l] += costs[l]
        result.write(costs.__str__() + "\n")
        alg.clear_values()
    result.write("-----------------------------AVG-----------------------------\n")
    for elem in avg_cost:
        elem = elem / 10
    result.write(avg_cost.__str__() + "\n\n")
    avg_cost = [0] * analyze_points
    result.write("-------------------GENETIC-INVERT-RANDOM-------------------\n")
    for k in range(10, 20):
        alg.calculate(5000, pop_size, MType.Invert, 0.05, Selection.Random, int(pop_size * 0.12), k)
        costs = alg.get_solution_in_time()
        for l in range(costs.__len__()):
            avg_cost[l] += costs[l]
        result.write(costs.__str__() + "\n")
        alg.clear_values()
    result.write("-----------------------------AVG-----------------------------\n")
    for elem in avg_cost:
        elem = elem / 10
    result.write(avg_cost.__str__() + "\n\n")
    avg_cost = [0] * analyze_points
    result.write("-------------------GENETIC-SWAP-TOURNAMENT-------------------\n")
    for k in range(20, 30):
        alg.calculate(5000, pop_size, MType.SwapOne, 0.05, Selection.Tournament, int(pop_size * 0.12), k)
        costs = alg.get_solution_in_time()
        for l in range(costs.__len__()):
            avg_cost[l] += costs[l]
        result.write(costs.__str__() + "\n")
        alg.clear_values()
    result.write("-----------------------------AVG-----------------------------\n")
    for elem in avg_cost:
        elem = elem / 10
    result.write(avg_cost.__str__() + "\n\n")
    avg_cost = [0] * analyze_points
    result.write("-------------------GENETIC-SWAP-RANDOM-------------------\n")
    for k in range(30, 40):
        alg.calculate(5000, pop_size, MType.SwapOne, 0.05, Selection.Random, int(pop_size * 0.12), k)
        costs = alg.get_solution_in_time()
        for l in range(costs.__len__()):
            avg_cost[l] += costs[l]
        result.write(costs.__str__() + "\n")
        alg.clear_values()
    result.write("-----------------------------AVG-----------------------------\n")
    for elem in avg_cost:
        elem = elem / 10
    result.write(avg_cost.__str__() + "\n\n")
    result.close()
