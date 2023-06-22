import numpy as np
import pygad
import numpy
import matplotlib.pyplot as plt
import pandas as pd


class test:
    def fitness_func(self, solution, solution_idx):
        print("\tfitness_func(generation = %d, solution_idx = %d)" % (
            self.ga_instance.generations_completed, solution_idx))
        # print('\t\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\t\tlen(ga_instance.solutions)', len(ga_instance.solutions))
        output = numpy.sum(solution * self.function_inputs)
        fitness = 1.0 / (numpy.abs(output - self.desired_output) + 0.000001)
        return fitness

    def on_start(self, ga_instance):
        if self.if_continuous is True:  # load data
            pass
        print("on_start(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))

    def on_fitness(self, ga_instance, population_fitness):
        print("on_fitness(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))
        # print(ga_instance.last_generation_fitness)
        # print(ga_instance.generations_completed)
        # print('')

    def on_parents(self, ga_instance, selected_parents):
        print("on_parents(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))
        # print(ga_instance.last_generation_fitness[-5:])
        # if ga_instance.generations_completed == 0:
        #     on_generation(ga_instance)
        fitness = numpy.array(ga_instance.solutions_fitness)
        solutions = numpy.array(ga_instance.solutions)
        index = numpy.argsort(fitness)[::-1][:10]
        top_fitness = fitness[index]
        top_solutions = solutions[index]
        gen, idx = numpy.divmod(index, numpy.full(numpy.shape(index), ga_instance.sol_per_pop))
        df = pd.DataFrame(top_solutions, columns=['Gene%d' % i for i in range(ga_instance.num_genes)])
        df['Fitness'] = top_fitness
        df['Generation'] = gen
        df['Individual'] = idx
        # print(df.head(len(df)))
        pass

    def on_crossover(self, ga_instance, offspring_crossover):
        print("on_crossover(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))

    def on_mutation(self, ga_instance, offspring_mutation):
        print("on_mutation(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))

    def on_generation(self, ga_instance):
        print('on_generation(generation = %d)' % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))
        # print(ga_instance.last_generation_fitness)
        # if ga_instance.generations_completed == 3:
        #     ga_instance.save('test')
        #     return 'stop'
        # print('')

    def on_stop(self, ga_instance, last_population_fitness):
        # input()
        print("on_stop(generation = %d)" % ga_instance.generations_completed)
        # print('\tlen(ga_instance.solutions_fitness)', len(ga_instance.solutions_fitness))
        # print('\tlen(ga_instance.solutions)', len(ga_instance.solutions))

    def __init__(self):
        self.if_continuous = True
        self.ga_instance = None

        self.function_inputs = [4, -2, 3.5, 5, -11, -4.7]
        self.desired_output = 44
        pd.set_option('display.max_columns', None)

        global fitness_func
        global on_gen

        def fitness_func(sol, idx):
            return self.fitness_func(sol, idx)

        def on_gen(ga):
            return self.on_generation(ga)

        self.ga_instance = pygad.GA(num_generations=5,
                                    num_parents_mating=2,
                                    fitness_func=fitness_func,
                                    mutation_num_genes=2,
                                    save_solutions=True,
                                    save_best_solutions=False,
                                    sol_per_pop=5,
                                    keep_parents=0,
                                    parent_selection_type='tournament',
                                    num_genes=len(self.function_inputs),
                                    # on_start=lambda arg1: self.on_start(arg1),
                                    # on_fitness=lambda arg1, arg2: self.on_fitness(arg1, arg2),
                                    # on_parents=lambda arg1, arg2: self.on_parents(arg1, arg2),
                                    on_generation=on_gen,
                                    # on_mutation=lambda arg1, arg2: self.on_mutation(arg1, arg2),
                                    # on_crossover=lambda arg1, arg2: self.on_crossover(arg1, arg2),
                                    # on_stop=lambda arg1, arg2: self.on_stop(arg1, arg2)
                                    )

        if self.if_continuous:
            self.ga_instance = pygad.load('test')
            # best_solutions = ga_instance.best_solutions  # Holds the best solution in each generation.
            # best_solutions_fitness = ga_instance.best_solutions_fitness  # A list holding the fitness value of the best solution for each generation.
            # solutions = ga_instance.solutions  # Holds the solutions in each generation.
            # solutions_fitness = ga_instance.solutions_fitness
            # generation_offset = ga_instance.generations_completed

        self.ga_instance.run()


# ga_instance.plot_genes(solutions='best')
# solution = ga_instance.best_solutions[ga_instance.best_solution_generation]
test_ga = test()
