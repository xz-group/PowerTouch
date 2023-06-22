import time

from PowerTouch.AttackTemplate.Nexus5 import Nexus5
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import pygad
import shutil
import os
import re
from os.path import exists
from datetime import datetime


class GeneticAlgorithm(object):
    def __init__(self):
        self.if_unified_amplitude = False
        self.if_unified_frequency = False
        self.geno2pheno_template = None
        self.minimum_pulse_num = None
        self.maximum_pulse_num = None
        self.ga_run_name = None
        self.trigger_count = 0
        self.repeat_number = 0
        self.topN = None
        self._target_description = None
        self._fitness_function = None
        self.num_generations = None
        self.sol_per_pop = None
        self.num_parents_mating = None
        self.parent_selection_type = None
        self.parent_selection_K_tournament = None
        self.keep_parents = None
        self.crossover_type = None
        self.crossover_probability = None
        self.mutation_type = None
        self.mutation_num_genes = None
        self.mutation_probability = None
        self.mutation_by_replacement = None
        self.mutation_percent_genes = None
        self.random_mutation_min_val = None
        self.random_mutation_max_val = None
        self.allow_duplicate_genes = None
        self.save_solutions = True
        self.delay_after_gen = 0.0
        self.save_best_solutions = None
        self.suppress_warnings = False
        self.stop_criteria = None
        self.saved_ga_instance = None
        self.num_genes = None
        self.gene_space = None
        self.if_continuous = None
        self._adb_server_pid = None
        self.data_save_dir = None
        self.event_file_path = None
        self.phone_index = 0
        self.phone_name = None
        self._attack_template = None
        self.noise_channel = None
        self.scope_trigger_level_mv = None
        self.sampling_frequency = None
        self.noise_offset = None
        self.scope_position_ms = None
        self.relay_guard_us = None
        self.relay_response_time = None
        self.hysteresis_factor = None
        self.if_above_0 = None
        self.trigger_rate_error_threshold = None
        self.if_save_figure = None
        self.if_save_ad2_timestamp = None
        self._generation_offset = 0
        self.df_all_previous = pd.DataFrame()
        self._last_generation_fitness = []
        self.minimum_fit_score = 0.0
        self.frame_rate = 0
        self.INITIAL_DELAY_US = None
        self.SCAN_PULSE_US = None
        self.SCAN_DELAY_US = None
        self.NUM_OF_ROWS = None
        self.maximum_frame_num = None
        self.minimum_frame_num = None
        self.step_frame_num = None
        self.maximum_pulse_width_us = None
        self.minimum_pulse_width_us = None
        self.step_pulse_width_us = None
        self.maximum_pulse_delay_us = None
        self.minimum_pulse_delay_us = None
        self.step_pulse_delay_us = None
        self.maximum_amplitude_V = None
        self.minimum_amplitude_V = None
        self.step_amplitude_V = None
        self.maximum_frequency_kHZ = None
        self.minimum_frequency_kHZ = None
        self.step_frequency_kHZ = None
        self.genotype_template = None
        self.debug_mode = False
        self.if_RisingPositive = None
        self.if_shell_communication = None

    def setHardwareParameters(self, adb_server_pid, phone_index, phone_name, frame_rate,
                              attack_template,
                              data_save_dir='D:/Code/PowerTouch/data_temp', event_file_path='D:/Code/PowerTouch',
                              if_save_ad2_timestamp=False, if_save_figure=True, if_RisingPositive=True,
                              trigger_rate_error_threshold=5, if_shell_communication=True,
                              if_above_0=False, hysteresis_factor=0.8, relay_response_time=500, relay_guard_us=500,
                              scope_position_ms=4.7, offset=0, sampling_frequency=800e3, scope_trigger_level_mv=25,
                              noise_channel=2, INITIAL_DELAY_US=430, SCAN_PULSE_US=62, SCAN_DELAY_US=213.6,
                              NUM_OF_ROWS=27, screen_x_lim=(0, 1080), screen_y_lim=(1920, 0)):
        self._adb_server_pid = adb_server_pid
        self.data_save_dir = data_save_dir
        self.event_file_path = event_file_path
        self.phone_index = phone_index
        self.phone_name = phone_name
        self._attack_template = attack_template
        self.noise_channel = noise_channel
        self.scope_trigger_level_mv = scope_trigger_level_mv
        self.sampling_frequency = sampling_frequency
        self.noise_offset = offset
        self.scope_position_ms = scope_position_ms
        self.relay_guard_us = relay_guard_us
        self.relay_response_time = relay_response_time
        self.hysteresis_factor = hysteresis_factor
        self.if_above_0 = if_above_0
        self.if_RisingPositive = if_RisingPositive
        self.if_shell_communication = if_shell_communication
        self.trigger_rate_error_threshold = trigger_rate_error_threshold
        self.if_save_figure = if_save_figure
        self.if_save_ad2_timestamp = if_save_ad2_timestamp
        self.frame_rate = frame_rate
        self.screen_x_lim = screen_x_lim
        self.screen_y_lim = screen_y_lim
        self.INITIAL_DELAY_US = INITIAL_DELAY_US
        self.SCAN_PULSE_US = SCAN_PULSE_US
        self.SCAN_DELAY_US = SCAN_DELAY_US
        self.NUM_OF_ROWS = NUM_OF_ROWS

        # todo: add input to change the phase

    def setHyperParameters(self, fitness_function, target_description,
                           repeat_number=1, trigger_count=500,
                           maximum_pulse_num=5, minimum_pulse_num=1,
                           maximum_frame_num=12, minimum_frame_num=4, step_frame_num=2,
                           maximum_pulse_width_us=3000, minimum_pulse_width_us=1, step_pulse_width_us=1,
                           maximum_pulse_delay_us=8000, minimum_pulse_delay_us=1, step_pulse_delay_us=1,
                           maximum_amplitude_V=80, minimum_amplitude_V=20, step_amplitude_V=1,
                           maximum_frequency_kHZ=499, minimum_frequency_kHZ=100, step_frequency_kHZ=1,
                           num_generations=50, sol_per_pop=50,
                           parent_selection_type='sss', parent_selection_K_tournament=3,
                           num_parents_mating=7, keep_parents=-1,
                           if_unified_amplitude=False, if_unified_frequency=False,
                           crossover_type='single_point', crossover_probability=None,
                           mutation_type='random', mutation_num_genes=None,
                           mutation_probability=None, mutation_by_replacement=False,
                           mutation_percent_genes='default', random_mutation_min_val=-1.0, random_mutation_max_val=1.0,
                           growth_aging_probability=0.1,
                           allow_duplicate_genes=True,
                           save_topN=20,
                           stop_criteria=None, suppress_warnings=False, save_best_solutions=False,
                           delay_after_gen=0, save_solutions=True,
                           continue_ga_run=None, minimum_fit_score=0.0,
                           genotype_template=None, geno2pheno_template=None):

        # overall
        self.ga_run_name = ''
        self.minimum_fit_score = minimum_fit_score
        self.trigger_count = trigger_count
        self.repeat_number = repeat_number
        self.topN = save_topN  # save results of top N individual
        self._target_description = '_'.join(target_description)
        self._fitness_function = fitness_function
        self.maximum_pulse_num = maximum_pulse_num
        self.minimum_pulse_num = minimum_pulse_num
        self.maximum_frame_num = maximum_frame_num
        self.minimum_frame_num = minimum_frame_num
        self.step_frame_num = step_frame_num
        self.maximum_pulse_width_us = maximum_pulse_width_us
        self.minimum_pulse_width_us = minimum_pulse_width_us
        self.step_pulse_width_us = step_pulse_width_us
        self.maximum_pulse_delay_us = maximum_pulse_delay_us
        self.minimum_pulse_delay_us = minimum_pulse_delay_us
        self.step_pulse_delay_us = step_pulse_delay_us
        self.maximum_amplitude_V = maximum_amplitude_V
        self.minimum_amplitude_V = minimum_amplitude_V
        self.step_amplitude_V = step_amplitude_V
        self.maximum_frequency_kHZ = maximum_frequency_kHZ
        self.minimum_frequency_kHZ = minimum_frequency_kHZ
        self.step_frequency_kHZ = step_frequency_kHZ
        self.if_unified_amplitude = if_unified_amplitude
        self.if_unified_frequency = if_unified_frequency
        self.geno2pheno_template = geno2pheno_template
        self.genotype_template = genotype_template

        # number of generations and number of solutions in each generation
        self.num_generations = num_generations
        self.sol_per_pop = sol_per_pop  # Number of solutions in the population. default 50

        # parent selection
        self.num_parents_mating = num_parents_mating
        self.parent_selection_type = parent_selection_type
        self.parent_selection_K_tournament = parent_selection_K_tournament
        self.keep_parents = keep_parents

        # crossover
        self.crossover_type = crossover_type
        self.crossover_probability = crossover_probability

        # mutation
        self.mutation_type = mutation_type
        self.mutation_num_genes = mutation_num_genes
        self.mutation_probability = mutation_probability
        self.mutation_by_replacement = mutation_by_replacement
        self.mutation_percent_genes = mutation_percent_genes
        self.random_mutation_min_val = random_mutation_min_val
        self.random_mutation_max_val = random_mutation_max_val

        # growth and aging
        self.growth_aging_probability = growth_aging_probability

        # genotype
        self.allow_duplicate_genes = allow_duplicate_genes

        # others
        self.save_solutions = save_solutions
        self.delay_after_gen = delay_after_gen
        self.save_best_solutions = save_best_solutions
        self.suppress_warnings = suppress_warnings
        self.stop_criteria = stop_criteria

        # generate search space
        self._defineGenotypeSearchSpace(genotype_template=genotype_template)

        # load previous ga run is specified
        if continue_ga_run is not None:
            self.saved_ga_instance = continue_ga_run  # no '.pkl' here
            self.if_continuous = True
        else:
            self.saved_ga_instance = ''
            self.if_continuous = False

    def _defineGenotypeSearchSpace(self, genotype_template=None):
        if genotype_template is None:  # use default
            gene_space = [{'low': self.minimum_frame_num,
                           'step': self.step_frame_num,
                           'high': self.maximum_frame_num}]  # attackPerNFrame
            if self.if_unified_amplitude is True:
                gene_space.append({'low': self.minimum_amplitude_V,
                                   'step': self.step_amplitude_V,
                                   'high': self.maximum_amplitude_V})
            if self.if_unified_frequency is True:
                gene_space.append({'low': self.minimum_frequency_kHZ,
                                   'step': self.step_frequency_kHZ,
                                   'high': self.maximum_frequency_kHZ})
            gene_ = []
            for i in range(self.maximum_pulse_num):  # pulse i-th amplitude, frequency, delay, and width

                if self.if_unified_amplitude is False:
                    gene_.append({'low': self.minimum_amplitude_V,
                                  'step': self.step_amplitude_V,
                                  'high': self.maximum_amplitude_V})
                if self.if_unified_frequency is False:
                    gene_.append({'low': self.minimum_frequency_kHZ,
                                  'step': self.step_frequency_kHZ,
                                  'high': self.maximum_frequency_kHZ})
                gene_.extend([{'low': self.minimum_pulse_delay_us,
                               'step': self.step_pulse_delay_us,
                               'high': self.maximum_pulse_delay_us},  # pulse i delay
                              {'low': self.minimum_pulse_width_us,
                               'step': self.step_pulse_width_us,
                               'high': self.maximum_pulse_width_us}])  # pulse i width
            gene_space.extend(gene_)
            self.gene_space = gene_space
            self.num_genes = len(gene_space)
        else:
            self.gene_space, self.num_genes = genotype_template()

    def _genoType2phenoType(self, geno_type, individual):
        # target phenotype format:
        # [attackPerNFrame, Pulse_number, PulseAmplitude_list, PulseFrequency_list, PulseDelay_list, PulseWidth_list]
        # Note that PulseDelay is relative to previous pulse start point

        if self.geno2pheno_template is None:
            # get delay and width list
            geno_type = geno_type[geno_type != -1]  # remove placeholder (-1)
            try:
                pulse_num = self.offspring_num_pulse[individual]
                offset = 0
                if self.if_unified_amplitude is True:
                    offset += 1
                if self.if_unified_frequency is True:
                    offset += 1

                geno_type_size = 1 + offset + pulse_num * (4 - offset)
                if geno_type_size != len(geno_type):
                    raise ValueError('geno_type_size != len(geno_type)')
            except AttributeError:
                warnings.warn('offspring_num_pulse is not defined. Passing...')

            # initialize
            delay = []
            width = []
            amplitude = []
            frequency = []

            # calculate parameter offset
            offset = 0
            if self.if_unified_amplitude is True:
                offset += 1
            if self.if_unified_frequency is True:
                offset += 1

            # get pulse number
            pulse_num = int((len(geno_type) - offset - 1) / (4 - offset))

            shift = 0
            if self.if_unified_amplitude is True:
                amplitude = [geno_type[1]] * pulse_num
                shift += 1
            if self.if_unified_frequency is True:
                frequency = [geno_type[1 + shift]] * pulse_num
                shift += 1

            # get delay and width list
            for i in range(pulse_num):
                if self.if_unified_amplitude is False and self.if_unified_frequency is False:
                    amplitude.append(geno_type[offset + 1 + i * (4 - offset)])
                    frequency.append(geno_type[offset + 1 + i * (4 - offset) + 1])
                    delay.append(geno_type[offset + 1 + i * (4 - offset) + 2])
                    width.append(geno_type[offset + 1 + i * (4 - offset) + 3])
                elif self.if_unified_amplitude is False or self.if_unified_frequency is False:
                    if self.if_unified_amplitude is False:
                        amplitude.append(geno_type[offset + 1 + i * (4 - offset)])
                    if self.if_unified_frequency is False:
                        frequency.append(geno_type[offset + 1 + i * (4 - offset)])
                    delay.append(geno_type[offset + 1 + i * (4 - offset) + shift])
                    width.append(geno_type[offset + 1 + i * (4 - offset) + 1 + shift])
                else:
                    delay.append(geno_type[offset + 1 + i * (4 - offset)])
                    width.append(geno_type[offset + 1 + i * (4 - offset) + 1])

            # calculate the delay
            if pulse_num > 1:
                delay_since_last_start = [delay[0]] + [delay[i] + width[i - 1] for i in range(1, pulse_num)]
            else:
                delay_since_last_start = delay

            pheno_type = [geno_type[0], pulse_num, amplitude, frequency, delay_since_last_start, width]
        else:
            pheno_type = self.geno2pheno_template(geno_type)

        return pheno_type

    def _generate_initial_population(self):
        offset = 0
        if self.if_unified_amplitude is True:
            offset += 1
        if self.if_unified_frequency is True:
            offset += 1

        population = np.full((self.sol_per_pop, self.maximum_pulse_num * (4 - offset) + 1 + offset), -1)
        self.offspring_num_pulse = np.zeros(self.sol_per_pop)
        for sol_idx in range(self.sol_per_pop):
            num_pulses = np.random.randint(self.minimum_pulse_num, self.maximum_pulse_num + 1)

            self.offspring_num_pulse[sol_idx] = num_pulses
            num_genes = num_pulses * (4 - offset) + 1 + offset
            for gene_idx in range(num_genes):
                if type(self.gene_space[gene_idx]) is dict:
                    if 'step' in self.gene_space[gene_idx].keys():
                        population[sol_idx, gene_idx] = np.asarray(
                            np.random.choice(np.arange(start=self.gene_space[gene_idx]['low'],
                                                       stop=self.gene_space[gene_idx]['high'],
                                                       step=self.gene_space[gene_idx]['step']),
                                             size=1))[0]
                    else:
                        population[sol_idx, gene_idx] = np.asarray(
                            np.random.uniform(low=self.gene_space[gene_idx]['low'],
                                              high=self.gene_space[gene_idx]['high'],
                                              size=1))[0]
        return population

    def _initiateGAInstance(self):
        global on_start_wrapper
        global on_generation_wrapper
        global calculate_population_fitness_wrapper
        global growth_aging_func_wrapper
        global crossover_func_wrapper

        def on_start_wrapper(ga_instance):
            return self._on_start(ga_instance)

        def on_generation_wrapper(ga_instance):
            return self._on_generation(ga_instance)

        def calculate_population_fitness_wrapper(geno_type, individual):
            return self._calculate_population_fitness(geno_type, individual)

        def growth_aging_func_wrapper(offspring, ga_instance):
            return self._growth_aging_func(offspring, ga_instance)

        def crossover_func_wrapper(parents, offspring_size, ga_instance):
            return self._crossover_func(parents, offspring_size, ga_instance)

        if self.if_continuous is True:  # if previous ga run name is specified
            self.ga_instance = pygad.load(self.saved_ga_instance)

            # calculate the remaining generations then update parameter in ga_instance
            self.ga_instance.num_generations = self.ga_instance.num_generations - self.ga_instance.generations_completed
            self.ga_instance.generations_completed = 0

            # load last_generation_fitness
            self._last_generation_fitness = self.ga_instance.last_generation_fitness

        else:
            self.ga_instance = pygad.GA(num_generations=self.num_generations, sol_per_pop=self.sol_per_pop,
                                        initial_population=self._generate_initial_population(),
                                        # parent selection
                                        num_parents_mating=self.num_parents_mating,
                                        keep_parents=self.keep_parents,
                                        parent_selection_type=self.parent_selection_type,
                                        K_tournament=self.parent_selection_K_tournament,
                                        # crossover
                                        crossover_type=crossover_func_wrapper,
                                        crossover_probability=self.crossover_probability,
                                        # mutation
                                        mutation_type=self.mutation_type,
                                        mutation_num_genes=self.mutation_num_genes,
                                        mutation_probability=self.mutation_probability,
                                        mutation_by_replacement=self.mutation_by_replacement,
                                        mutation_percent_genes=self.mutation_percent_genes,
                                        random_mutation_min_val=self.random_mutation_min_val,
                                        random_mutation_max_val=self.random_mutation_max_val,
                                        # genotype
                                        gene_space=self.gene_space,
                                        num_genes=self.num_genes,
                                        allow_duplicate_genes=self.allow_duplicate_genes,
                                        # functions
                                        fitness_func=calculate_population_fitness_wrapper, on_parents=None,
                                        on_generation=on_generation_wrapper, on_start=on_start_wrapper,
                                        on_fitness=None, on_crossover=None, on_mutation=growth_aging_func_wrapper,
                                        on_stop=None,
                                        # others
                                        save_solutions=self.save_solutions,
                                        delay_after_gen=self.delay_after_gen,
                                        save_best_solutions=self.save_best_solutions,
                                        suppress_warnings=self.suppress_warnings,
                                        stop_criteria=self.stop_criteria
                                        )

    def _on_start(self, ga_instance):  # create a folder and update the dir before running GA
        if self.if_continuous is False:
            print('Start Running GA:')
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            self.ga_run_name = '_'.join(
                [timestamp, self._target_description, 'PhN-' + self.phone_name, 'Idx%d' % self.phone_index,
                 'TC%d' % self.trigger_count,
                 'Rpt%d' % self.repeat_number])  # put optimization target description here
            self.ga_save_dir = os.path.join(self.data_save_dir, self.ga_run_name)
            os.mkdir(self.ga_save_dir)  # create folder for each ga run
        else:
            print('Continue Running GA:')
            # load previous df
            segments = re.split('_', self.saved_ga_instance)
            self.ga_run_name = '_'.join([_ for _ in segments if 'SG' not in _])  # remove the state flag
            print('Instance File Name: %s.pkl' % self.saved_ga_instance)
            print('GA Run Name: %s' % self.ga_run_name)

            self.ga_save_dir = os.path.join(self.data_save_dir, self.ga_run_name)
            self.df_all_previous = pd.read_csv(os.path.join(self.ga_save_dir, 'all_solutions.csv'))
            self._generation_offset = max(self.df_all_previous['Generation'])  # in case one ga needs multiple segments

        print(self.ga_save_dir)
        print('\n\n' + '=' * 95)
        print("Generation = {generation}".format(generation=self._generation_offset + 1))
        print('=' * 95)

    def _calculate_population_fitness(self, geno_type, individual):
        # interpret gene
        pheno_type = self._genoType2phenoType(geno_type, individual)

        # skip the overlapped generation 0 when continue previous run
        if self.if_continuous is True and self.ga_instance.generations_completed == 0:
            fitness_score = self._last_generation_fitness[individual]
            return fitness_score

        generation = self.ga_instance.generations_completed + self._generation_offset
        print('\n\nGen%d-%d' % (generation, individual))

        if self.debug_mode is True:
            print('Debug Mode:')
            print('Geno Type: %s' % geno_type)
            print('Generation: %d' % generation)
            print('Individual: %d' % individual)
            print('Pheno Type: %s' % pheno_type)
            print('peak2peak=', pheno_type[2])  # peak2peak
            print('frequency_kHz=', pheno_type[3])  # frequency kHz
            print('attack_per_N_frames=', pheno_type[0])  # attackPerNFrame
            print('number_of_pulses=', pheno_type[1])  # numberOfPulses
            print('pulse_delay_list_us=', pheno_type[4])  # pulseDelayListUs
            print('pulse_width_list_us=', pheno_type[5])
            # return np.random.rand()

        # [attackPerNFrame, Pulse_number, PulseAmplitude_list, PulseFrequency_list, PulseDelay_list, PulseWidth_list]
        csv_folder_name = self._attack_template(generation=generation, individual=individual,
                                                # phenotype
                                                peak2peak=pheno_type[2],  # peak2peak
                                                frequency_kHz=pheno_type[3],  # frequency kHz
                                                attack_per_N_frames=pheno_type[0],  # attackPerNFrame
                                                number_of_pulses=pheno_type[1],  # numberOfPulses
                                                pulse_delay_list_us=pheno_type[4],  # pulseDelayListUs
                                                pulse_width_list_us=pheno_type[5],  # pulseWidthListUs
                                                # hardware configuration
                                                adb_server_pid=self._adb_server_pid,
                                                phone_index=self.phone_index,
                                                trigger_count=self.trigger_count, repeat_number=self.repeat_number,
                                                data_save_dir=self.ga_save_dir, verbose_depth_level=1,
                                                noise_channel=self.noise_channel,
                                                scope_trigger_level_mv=self.scope_trigger_level_mv,
                                                sampling_frequency=self.sampling_frequency, offset=self.noise_offset,
                                                scope_position_ms=self.scope_position_ms,
                                                relay_guard_us=self.relay_guard_us,
                                                relay_response_time=self.relay_response_time,
                                                hysteresis_factor=self.hysteresis_factor,
                                                if_above_0=self.if_above_0,
                                                if_shell_communication=self.if_shell_communication,
                                                trigger_rate_error_threshold=self.trigger_rate_error_threshold,
                                                if_save_figure=self.if_save_figure,
                                                if_save_ad2_timestamp=self.if_save_ad2_timestamp,
                                                if_RisingPositive=self.if_RisingPositive,
                                                frame_rate=self.frame_rate,
                                                phone_name=self.phone_name,
                                                screen_x_lim=self.screen_x_lim,
                                                screen_y_lim=self.screen_y_lim,
                                                _INITIAL_DELAY_US=self.INITIAL_DELAY_US,
                                                _SCAN_PULSE_US=self.SCAN_PULSE_US,
                                                _SCAN_DELAY_US=self.SCAN_DELAY_US,
                                                _NUM_OF_ROWS=self.NUM_OF_ROWS
                                                )

        # Read results files
        prefixes = '-'.join(['Gen' + str(generation) + '-' + str(individual)])
        click_file_name = os.path.join(self.ga_save_dir, csv_folder_name, '_'.join([prefixes, 'click.csv']))
        swipe_file_name = os.path.join(self.ga_save_dir, csv_folder_name, '_'.join([prefixes, 'nonclick.csv']))
        event_file_name = os.path.join(self.ga_save_dir, csv_folder_name, '_'.join([prefixes, 'eventNumber.csv']))
        if exists(click_file_name):
            df_clicks = pd.read_csv(click_file_name)
        else:
            df_clicks = None

        if exists(swipe_file_name):
            df_swipes = pd.read_csv(swipe_file_name)
        else:
            df_swipes = None

        if exists(event_file_name):
            df_eventNumber = pd.read_csv(event_file_name)
        else:
            df_eventNumber = None

        # Calculate fitness score
        fitness_score = self._fitness_function(df_eventNumber, df_clicks, df_swipes,
                                               save_path=os.path.join(self.ga_save_dir, csv_folder_name))

        segment = re.split('_', csv_folder_name)
        segment.insert(1, 'F%.5f' % fitness_score)

        os.rename(os.path.join(self.ga_save_dir, csv_folder_name),
                  os.path.join(self.ga_save_dir, '_'.join(segment)))
        return fitness_score

    def _crossover_func(self, parents, offspring_size, ga_instance):
        offset = 0
        if self.if_unified_amplitude is True:
            offset += 1
        if self.if_unified_frequency is True:
            offset += 1

        parents_grouped = []
        # group pulses into segments
        for i in range(len(parents)):
            pg_ = [parents[i][j] for j in range(offset + 1)]
            num_pulse = (len(parents[i]) - 1 - offset) / (4 - offset)
            for j in range(int(num_pulse)):
                pg_.extend([i + j / 100])
            pg_ = np.array(pg_)
            parents_grouped.append(pg_)

        parents_grouped = np.array(parents_grouped)
        offspring_size_grouped = (offspring_size[0], np.shape(parents_grouped)[1])

        # do crossover
        if self.crossover_type == "single_point":
            offspring = ga_instance.single_point_crossover(parents_grouped, offspring_size_grouped)
        elif self.crossover_type == "two_points":
            offspring = ga_instance.two_points_crossover(parents_grouped, offspring_size_grouped)
        elif self.crossover_type == "uniform":
            offspring = ga_instance.uniform_crossover(parents_grouped, offspring_size_grouped)
        elif self.crossover_type == "scattered":
            offspring = ga_instance.scattered_crossover(parents_grouped, offspring_size_grouped)

        # ungroup offspring
        offspring_ungrouped = []
        self.offspring_num_pulse = []
        for i in range(len(offspring)):
            _ = offspring[i]
            ofp_ug_ = [_[j] for j in range(offset + 1)]
            _ = _[offset + 1:]
            for j in range(len(_)):
                number = _[j]
                index = (int(number // 1), int((number % 1) * 101))
                start = index[1] * (4 - offset) + offset + 1
                end = start + (4 - offset)
                ofp_ug_.extend(parents[index[0]][start:end])
            # remove placeholders, if any
            ofp_ug_ = [i for i in ofp_ug_ if i != -1]
            # get the number of pulses
            self.offspring_num_pulse.append((len(ofp_ug_) - offset - 1) // (4 - offset))
            if len(ofp_ug_) < offspring_size[1]:
                ofp_ug_.extend([-1] * (offspring_size[1] - len(ofp_ug_)))

            offspring_ungrouped.append(np.array(ofp_ug_))
        offspring_ungrouped = np.array(offspring_ungrouped)
        return offspring_ungrouped

    def _growth_aging_func(self, ga_instance, offspring):
        offset = 0
        if self.if_unified_amplitude is True:
            offset += 1
        if self.if_unified_frequency is True:
            offset += 1

        # generate probability list
        growth_aging_probs = np.random.random(size=offspring.shape[0])
        growth_aging_flags = [np.random.choice(['growth', 'aging'], p=[0.5, 0.5]) for _ in range(offspring.shape[0])]

        offspring_grew_aged = []
        for i in range(len(offspring)):
            offspring_ = list(offspring[i])
            # clean offspring
            num_pulse = self.offspring_num_pulse[i]
            offspring_ = offspring_[:offset + 1 + num_pulse * (4 - offset)]
            # grow or aging
            if growth_aging_probs[i] < self.growth_aging_probability:
                if growth_aging_flags[i] == 'growth':
                    if num_pulse < self.maximum_pulse_num:
                        self.offspring_num_pulse[i] += 1
                        if self.if_unified_amplitude is False:
                            offspring_.append(np.random.choice(np.arange(start=self.minimum_amplitude_V,
                                                                         stop=self.maximum_amplitude_V,
                                                                         step=self.step_amplitude_V),
                                                               size=1)[0])
                        if self.if_unified_frequency is False:
                            offspring_.append(np.random.choice(np.arange(start=self.minimum_frequency_kHZ,
                                                                         stop=self.maximum_frequency_kHZ,
                                                                         step=self.step_frequency_kHZ),
                                                               size=1)[0])
                        offspring_.append(np.random.choice(np.arange(start=self.minimum_pulse_delay_us,
                                                                     stop=self.maximum_pulse_delay_us,
                                                                     step=self.step_pulse_delay_us),
                                                           size=1)[0])
                        offspring_.append(np.random.choice(np.arange(start=self.minimum_pulse_width_us,
                                                                     stop=self.maximum_pulse_width_us,
                                                                     step=self.step_pulse_width_us),
                                                           size=1)[0])
                if growth_aging_flags[i] == 'aging':
                    if num_pulse > self.minimum_pulse_num:
                        self.offspring_num_pulse[i] -= 1
                        offspring_[-(4 - offset):] = []
            # padding with placeholder (-1)
            if len(offspring_) < offspring.shape[1]:
                offspring_.extend([-1] * (offspring.shape[1] - len(offspring_)))
            offspring_ = np.array(offspring_)
            offspring_grew_aged.append(offspring_)

        offspring_grew_aged = np.array(offspring_grew_aged)
        ga_instance.last_generation_offspring_mutation = offspring_grew_aged

        return offspring_grew_aged

    def _on_generation(self, ga_instance):  # save results after each generation
        print('Saving results...')
        fitness_value = ga_instance.solutions_fitness.copy()
        fitness_value.extend(ga_instance.last_generation_fitness)
        fitness_value = np.array(fitness_value)
        solutions = np.array(ga_instance.solutions.copy())

        if self.if_continuous is True:  # skip the overlapped generation 0
            fitness_value = fitness_value[ga_instance.sol_per_pop:]
            solutions = solutions[ga_instance.sol_per_pop:]

        if ga_instance.generations_completed == 0:
            raise ValueError(ga_instance.generations_completed)

        if len(fitness_value) != len(solutions):
            raise ValueError(len(fitness_value), len(solutions))

        if max(ga_instance.last_generation_fitness) == self.minimum_fit_score:  # terminate on bad generation
            print('Terminate on bad generation without saving generation %d' % (
                    ga_instance.generations_completed + self._generation_offset))
            return 'stop'
        else:

            # save all results
            print('Save to csv...')
            index_all = range(len(solutions))
            gen_all, idx_all = np.divmod(index_all, np.full(np.shape(index_all), ga_instance.sol_per_pop))
            if self.if_continuous is True:
                gen_all = gen_all + 1
            self.df_all = pd.DataFrame(solutions, columns=['Gene%d' % g for g in range(ga_instance.num_genes)])  # fixme
            self.df_all['Fitness'] = fitness_value
            self.df_all['Generation'] = gen_all + self._generation_offset
            self.df_all['Individual'] = idx_all
            if self.if_continuous is True:
                self.df_all = pd.concat([self.df_all_previous, self.df_all], ignore_index=True, sort=False)
            self.df_all.to_csv(os.path.join(self.ga_save_dir, 'all_solutions.csv'), index=False)

            # save top results
            self.df_top = self.df_all.sort_values(by='Fitness', ascending=False)
            self.df_top.reset_index(inplace=True)
            self.df_top = self.df_top.head(self.topN)
            self.df_top.to_csv(os.path.join(self.ga_save_dir, 'best_results.csv'), index=False)
            print(self.df_top.head(len(self.df_top)))
            print('\nSave GA Instance...')
            if exists('./' + self.saved_ga_instance + '.pkl'):
                os.remove('./' + self.saved_ga_instance + '.pkl')

            self.saved_ga_instance = self.ga_run_name + '_SG%d' % (
                    ga_instance.generations_completed + self._generation_offset)
            ga_instance.save(self.saved_ga_instance)

        print('\n\n' + '=' * 95)
        print("Generation = {generation}".format(
            generation=ga_instance.generations_completed + self._generation_offset + 1))

    def _on_stop(self, ga_instance, last_population_fitness):
        if exists('./' + self.saved_ga_instance + '.pkl'):
            os.remove('./' + self.saved_ga_instance + '.pkl')

        self.saved_ga_instance = self.ga_run_name + '_SG%dF' % ga_instance.generations_completed
        ga_instance.save(self.saved_ga_instance)

    def run(self):
        # Running the GA to optimize the parameters of the function.
        self._initiateGAInstance()
        self.ga_instance.run()

    def attackTemplate_default(self, generation, individual, peak2peak, frequency_kHz, attack_per_N_frames,
                               number_of_pulses,
                               pulse_delay_list_us,
                               pulse_width_list_us, adb_server_pid, phone_index, trigger_count=500, repeat_number=5,
                               data_save_dir='D:/Code/PowerTouch/data_temp', verbose_depth_level=1, noise_channel=2,
                               scope_trigger_level_mv=30, sampling_frequency=800e3, offset=0,
                               scope_position_ms=4.7, relay_guard_us=500, relay_response_time=500,
                               hysteresis_factor=0.8, if_above_0=False, trigger_rate_error_threshold=5,
                               if_save_figure=True, if_shell_communication=True,
                               if_save_ad2_timestamp=True, if_RisingPositive=True,
                               frame_rate=120, screen_x_lim=(0, 1080), screen_y_lim=(1920, 0),
                               phone_name='Nexus5',
                               _INITIAL_DELAY_US=430,
                               _SCAN_PULSE_US=62,
                               _SCAN_DELAY_US=213.6,
                               _NUM_OF_ROWS=27):
        """

        :param generation: The genetic algorithm parameter, is used to name the experiment.
        :param individual: The genetic algorithm parameter, is used to name the experiment.
        :param peak2peak: The peak to peak voltage of injected noise. Must smaller than 80V.
        :param frequency_kHz: The frequency of the injected noise. Must between 50K-499K.
        :param attack_per_N_frames:
        :param number_of_pulses:
        :param pulse_delay_list_us: The relative delay between two pulses.
        :param pulse_width_list_us:
        :param adb_server_pid:
        :param phone_index: Used to identify experimenting on which phone
        :param trigger_count:
        :param repeat_number:
        :param data_save_dir:
        :param verbose_depth_level: 0 - no info printed. 1 - basic info. 2 - more detailed info. 3 - all info
        :param noise_channel: AWG output channel of AD2. Do not change.
        :param scope_trigger_level_mv: The trigger level of the oscilloscope.
        :param sampling_frequency: Do not change.
        :param offset: Do not change.
        :param scope_position_ms: Just affect the generated figure. Do not change.
        :param relay_guard_us: Do not change.
        :param relay_response_time: Do not change.
        :param hysteresis_factor:
        :param if_above_0: Do not change.
        :param trigger_rate_error_threshold:
        :param if_save_figure:
        :param if_save_ad2_timestamp:
        :return: The name of the experiment (i.e., the name of the folder that contains the results).
        """
        _PHONE_NAME = phone_name
        _INITIAL_DELAY_US = _INITIAL_DELAY_US
        _SCAN_PULSE_US = _SCAN_PULSE_US
        _SCAN_DELAY_US = _SCAN_DELAY_US
        _FRAME_RATE = frame_rate
        _FRAME_PERIOD_MS = 1 / _FRAME_RATE * 1e3
        _NUM_OF_ROWS = _NUM_OF_ROWS

        verbose = [False] * 3
        for i in range(verbose_depth_level):
            verbose[i] = True

        experiment_name = 'Gen%d-%d' % (generation, individual)

        # calculate hold off time according to attack_per_N_frames
        hold_off_ms = (attack_per_N_frames - 1) * _FRAME_PERIOD_MS + 7
        # time.sleep(10)  # fixme: wait for the phone to be ready
        # check the if the input parameters are valid
        # if attack_per_N_frames < 2:
        #     raise ValueError("'attack_per_N_frames' must be greater than 2, current value is %d." % attack_per_N_frames)
        #
        # if attack_per_N_frames % 2 != 0:
        #     raise ValueError("'attack_per_N_frames' must be an even number, current value is %d." % attack_per_N_frames)

        if isinstance(frequency_kHz, list) or isinstance(peak2peak, list):
            if isinstance(peak2peak, list) is False:
                raise ValueError("'peak2peak' must be a list, current value is %s." % peak2peak)
            if isinstance(frequency_kHz, list) is False:
                raise ValueError("'frequency_kHz' must be a list, current value is %s." % frequency_kHz)
            if len(frequency_kHz) != len(peak2peak) != len(pulse_delay_list_us) != len(pulse_width_list_us):
                raise ValueError(
                    "'frequency_kHz', 'peak2peak', 'pulse_delay_list_us', 'pulse_width_list_us' must have the same length.")
        else:
            peak2peak = [peak2peak] * number_of_pulses
            frequency_kHz = [frequency_kHz] * number_of_pulses

        for i in range(len(frequency_kHz)):
            if frequency_kHz[i] < 50 or frequency_kHz[i] > 499:
                raise ValueError("'frequency_kHz' must be between 50 and 499, current value is %d." % frequency_kHz[i])

        for i in range(len(peak2peak)):
            if peak2peak[i] > 80:
                raise ValueError("'peak2peak' must be smaller than 80, current value is %d." % peak2peak[i])

        if number_of_pulses != len(pulse_delay_list_us) or number_of_pulses != len(pulse_width_list_us):
            raise ValueError(
                "'number_of_pulses' (%d) doesn't match the length of 'pulse_delay_list_us' (%d) or 'pulse_width_list_us' (%d)." % (
                    number_of_pulses, len(pulse_delay_list_us), len(pulse_width_list_us)))

        if abs(offset) > 5:
            raise ValueError("'offset' is out of range (%dV, %dV), current value is  %.1fV." % (-5, 5, offset))

        _absolute_delay = np.cumsum(pulse_delay_list_us)

        if number_of_pulses != 1:
            for i in range(number_of_pulses - 1):
                if pulse_width_list_us[i] + _absolute_delay[i] >= _absolute_delay[i + 1]:
                    raise ValueError(
                        'Pulse %d (start@%.1fus, end@%.1fus) overlaps with Pulse %d (start@%.1fus, end@@%.1fus)' % (
                            i + 1, _absolute_delay[i], pulse_width_list_us[i] + _absolute_delay[i], i + 2,
                            _absolute_delay[i + 1],
                            _absolute_delay[i + 1] + pulse_width_list_us[i + 1]))
        if _absolute_delay[-1] + pulse_width_list_us[-1] >= hold_off_ms * 1e3:
            # raise ValueError('Injected pulses end @%.1fus, hold off time end @%.1fus, system is not stable.' % (
            #     _absolute_delay[-1] + pulse_width_list_us[-1], hold_off_ms * 1e3))
            warnings.warn('Injected pulses end @%.1fus, hold off time end @%.1fus, system is not stable.' % (
                _absolute_delay[-1] + pulse_width_list_us[-1], hold_off_ms * 1e3))
            # return experiment_name

        # check the battery
        phone = Nexus5(verbose=False)
        phone.chargePhoneIfNeeded(low_threshold=5, high_threshold=95)

        # read the gain list of PiezoDriveMX200 amplifier
        gain_list = pd.read_csv('D:/Code/PowerTouch/PowerTouch/Parameters/max200_gain.csv')

        # make dir for the experiment
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        pulse_info = []
        for i in range(number_of_pulses):
            pulse_info.append('P%dD%dusW%dusA%dvF%dkhz' % (i + 1, pulse_delay_list_us[i], pulse_width_list_us[i],
                                                           peak2peak[i], frequency_kHz[i]))
        pulse_info = ''.join(pulse_info)

        # experiment_name = '_'.join(
        #     ['Gen%d-%d' % (generation, individual), 'AtkP%dFrm' % attack_per_N_frames, pulse_info])

        path_main = os.path.join(data_save_dir, experiment_name)
        os.mkdir(path_main)
        print('=' * 50)
        print(experiment_name)
        print('AttackPer: %dFrames' % attack_per_N_frames)
        for i in range(number_of_pulses):
            print('Pulse%d: Delay-%1.fus, Width-%.1fus, Peak2Peak-%dV, Frequency-%dkHz' % (i + 1,
                                                                                           pulse_delay_list_us[i],
                                                                                           pulse_width_list_us[i],
                                                                                           peak2peak[i],
                                                                                           frequency_kHz[i]))

        # run experiment
        click = pd.DataFrame()
        event_number = pd.DataFrame()
        events_processed = pd.DataFrame()
        swipe = pd.DataFrame()

        for k in range(repeat_number):
            # path_repeat = os.path.join(path_main, 'Repeat%d' % (k + 1))
            # print('Repeat folder:', path_repeat)
            # os.mkdir(path_repeat)
            path_repeat = path_main
            trigger_rate_iteration_count = 0
            auto_trigger_iteration_count = 0

            while True:
                if verbose[0]:
                    print('')
                    print('Repeat %d/%d.' % (k + 1, repeat_number))
                phone = Nexus5(verbose=verbose[1])

                # calculate the calibrated gain according to the frequency
                gain = []
                for freq in frequency_kHz:
                    frequency_kHz_round = round(freq)
                    gain.append(gain_list.loc[gain_list.Frequency == frequency_kHz_round * 1e3, 'RealGain'].item())
                if verbose[0]:
                    print('Calibrated gain:', gain)

                amplitude_list = np.array(peak2peak) / np.array(gain)
                frequency_list = np.array(frequency_kHz) * 1e3
                amplitude_list = amplitude_list.tolist()
                frequency_list = frequency_list.tolist()

                # set up parameters
                if number_of_pulses == 1:
                    phone.setupAttackSinglePulse(scope_trigger_level_mv=scope_trigger_level_mv,
                                                 sampling_frequency=sampling_frequency,
                                                 scope_trigger_holdoff_ms=hold_off_ms,
                                                 verbose=verbose[2],
                                                 scope_position_ms=scope_position_ms,
                                                 attack_width_us=pulse_width_list_us[0],
                                                 relay_guard_us=relay_guard_us,
                                                 relay_response_time=relay_response_time,
                                                 attack_delay_us=pulse_delay_list_us[0],
                                                 noise_peak2peak=amplitude_list[0],
                                                 noise_frequency=frequency_list[0],
                                                 hysteresis_factor=hysteresis_factor,
                                                 if_above_0=if_above_0,
                                                 noise_channel=noise_channel,
                                                 offset=offset,
                                                 if_RisingPositive=if_RisingPositive)
                else:
                    phone.setupAttackArbitraryPulses(scope_trigger_level_mv=scope_trigger_level_mv,
                                                     sampling_frequency=sampling_frequency,
                                                     scope_trigger_holdoff_ms=hold_off_ms,
                                                     verbose=verbose[2],
                                                     scope_position_ms=scope_position_ms,
                                                     attack_width_list_us=pulse_width_list_us,
                                                     attack_delay_list_us=pulse_delay_list_us,
                                                     relay_guard_us=relay_guard_us,
                                                     relay_response_time=relay_response_time,
                                                     noise_peak2peak=amplitude_list,
                                                     noise_frequency=frequency_list,
                                                     hysteresis_factor=hysteresis_factor,
                                                     channel_index=noise_channel,
                                                     if_above_0=if_above_0,
                                                     offset=offset,
                                                     if_RisingPositive=if_RisingPositive)

                # run attack
                if self.debug_mode is True:
                    print('Dbug mode is on. Skipping attack.')
                    phone.stopAll(adb_server_pid=0, if_close_device=True)
                    return experiment_name
                phone.runAll(verbose=verbose[1], file_index=k + 1, noise_channel=noise_channel, align_timing=False,
                             if_shell_communication=if_shell_communication)
                trigger_rate, trigger_flag = phone.monitorAD2_saveData_byTriggerCount(trigger_count_max=trigger_count,
                                                                                      verbose=verbose[2])
                phone.stopAll(adb_server_pid=adb_server_pid, if_close_device=True)
                # phone.startChargingPhone()  # charge the phone while processing
                if verbose[0]:
                    print('Trigger flag:', trigger_flag)
                    print('Trigger rate: %.1f' % trigger_rate)

                # check if the system is stable
                if abs(trigger_rate - 1 / (
                        attack_per_N_frames * _FRAME_PERIOD_MS * 1e-3)) <= trigger_rate_error_threshold:
                    if trigger_flag != "Normal":
                        # raise ConnectionError('Screen closed. Please restart the screen.')
                        warnings.warn('Screen closed. Please restart the screen.')

                    # write ad2 timestamps, parse event files, and compile statistics if the system is stable
                    if if_save_ad2_timestamp is True:
                        phone.monitorAD2_write2CSV(save_path=path_repeat + '/', if_write_original_file=False,
                                                   index=k + 1)
                    if verbose[0]:
                        print('Event file size:', os.path.getsize(self._get_original_event_file_name(file_index=k + 1)))

                    phone.monitorScreen_readFromEventFile(
                        event_file_path=self._get_original_event_file_name(file_index=k + 1),
                        verbose=verbose[1],
                        copy_path=path_repeat + '/')
                    phone.screen.compileMultiTouchStatistics()

                    click_temp = phone.screen.statistic_click.copy()
                    click_temp['Repeat'] = k + 1
                    click_temp['OneAttackPerNFrames'] = attack_per_N_frames
                    click_temp['NumberOfPulses'] = number_of_pulses
                    click_temp['PulseInfo'] = pulse_info
                    click_temp['TotalRepeat'] = repeat_number
                    click_temp['PhoneName'] = _PHONE_NAME
                    click_temp['PhoneIndex'] = phone_index
                    click_temp['TriggerCount'] = trigger_count

                    event_number_temp = phone.screen.statistic_touch_count.copy()
                    event_number_temp['Repeat'] = k + 1
                    event_number_temp['OneAttackPerNFrames'] = attack_per_N_frames
                    event_number_temp['NumberOfPulses'] = number_of_pulses
                    event_number_temp['PulseInfo'] = pulse_info
                    event_number_temp['PhoneName'] = _PHONE_NAME
                    event_number_temp['PhoneIndex'] = phone_index
                    event_number_temp['TriggerCount'] = trigger_count

                    swipe_temp = phone.screen.statistic_swipe.copy()
                    swipe_temp['Repeat'] = k + 1
                    swipe_temp['OneAttackPerNFrames'] = attack_per_N_frames
                    swipe_temp['NumberOfPulses'] = number_of_pulses
                    swipe_temp['PulseInfo'] = pulse_info
                    swipe_temp['PhoneName'] = _PHONE_NAME
                    swipe_temp['PhoneIndex'] = phone_index
                    swipe_temp['TriggerCount'] = trigger_count

                    events_processed_temp = phone.screen.records.copy()
                    events_processed_temp['Repeat'] = k + 1
                    events_processed_temp['OneAttackPerNFrames'] = attack_per_N_frames
                    events_processed_temp['NumberOfPulses'] = number_of_pulses
                    events_processed_temp['PulseInfo'] = pulse_info
                    events_processed_temp['PhoneName'] = _PHONE_NAME
                    events_processed_temp['PhoneIndex'] = phone_index
                    events_processed_temp['TriggerCount'] = trigger_count

                    click = click.append(click_temp, ignore_index=True)
                    swipe = swipe.append(swipe_temp, ignore_index=True)
                    event_number = event_number.append(event_number_temp, ignore_index=True)
                    events_processed = events_processed.append(events_processed_temp, ignore_index=True)

                    if if_save_figure is True:
                        info = ['Gen%d-%d' % (generation, individual),
                                'AtkP%dFrm' % attack_per_N_frames,
                                pulse_info]
                        if _INITIAL_DELAY_US is not None and _SCAN_DELAY_US is not None and _SCAN_PULSE_US is not None and _NUM_OF_ROWS is not None:
                            marker_pulse_start_position = np.arange(_INITIAL_DELAY_US,
                                                                    _INITIAL_DELAY_US + _NUM_OF_ROWS * (
                                                                            _SCAN_DELAY_US + _SCAN_PULSE_US),
                                                                    _SCAN_PULSE_US + _SCAN_DELAY_US)
                            marker_pulse_width = _SCAN_PULSE_US + _SCAN_DELAY_US
                            phone.data_analyzer.plotAD2Frame(if_random=True,
                                                             file_name=path_repeat + '/ad2_frame%d' % (k + 1),
                                                             marker_pulse_start_position_ms=marker_pulse_start_position / 1e3,
                                                             marker_pulse_width_ms=marker_pulse_width / 1e3,
                                                             additional_info=info)
                        else:
                            phone.data_analyzer.plotAD2Frame(if_random=True,
                                                             file_name=path_repeat + '/ad2_frame%d' % (k + 1),
                                                             additional_info=info)
                        if os.path.getsize(self._get_original_event_file_name(file_index=k + 1)) != 0:
                            phone.data_analyzer.plotScreenFrame(file_name=path_repeat + '/screen_frame%d' % (k + 1),
                                                                show_cross_mark=False, plot_circle=True,
                                                                additional_info=info, x_lim=screen_x_lim,
                                                                y_lim=screen_y_lim)
                    # phone.stopChargingPhone()  # stop charging the phone and close ad2
                    break
                else:  # re-run if not stable
                    warnings.warn('Repeat %d/%d: Trigger rate cannot meet requirement: %.1f! Trigger Rate Iter %d' % (
                        k + 1, repeat_number, 1 / (attack_per_N_frames * _FRAME_PERIOD_MS * 1e-3),
                        trigger_rate_iteration_count))
                    # phone.stopChargingPhone()  # stop charging the phone and close ad2
                    if trigger_rate_iteration_count > 2:
                        break
                    trigger_rate_iteration_count += 1
                    if trigger_flag != "Normal":
                        warnings.warn('Screen closed. Please restart the screen.')
                        # time.sleep(10)
                        auto_trigger_iteration_count += 1
                        if auto_trigger_iteration_count > 5:
                            raise ConnectionError('Screen closed. Please restart the screen.')
                        return experiment_name

        # write to csv
        if len(click) != 0:
            click.to_csv(os.path.join(path_main, 'Gen%d-%d_click.csv' % (generation, individual)), index=False)
        if len(swipe) != 0:
            swipe.to_csv(os.path.join(path_main, 'Gen%d-%d_nonclick.csv' % (generation, individual)), index=False)
        if len(event_number) != 0:
            event_number.to_csv(os.path.join(path_main, 'Gen%d-%d_eventNumber.csv' % (generation, individual)),
                                index=False)
        if len(events_processed) != 0:
            events_processed.to_csv(os.path.join(path_main, 'Gen%d-%d_events_processed.csv' % (generation, individual)),
                                    index=False)

        return experiment_name

    def _get_original_event_file_name(self, file_index=1):
        event_file_path = self.event_file_path + '/event%d.txt' % file_index
        return event_file_path

    def compileGAResults(self, data_save_dir=None, ga_run_name=None, save_top_N=None, maximum_num_pulses=2):
        if data_save_dir is not None:
            self.data_save_dir = data_save_dir
        if ga_run_name is not None:
            segments = re.split('_', ga_run_name)
            self.ga_run_name = '_'.join([_ for _ in segments if 'SG' not in _])  # remove the state flag
        if save_top_N is not None:
            self.topN = save_top_N

        # read ga run name
        string = re.split('_', self.ga_run_name)
        ga_dict = {}
        for segment in string:
            if 'PhN-' in segment:
                ga_dict['PhoneName'] = re.split('-', segment)[1]
            elif 'Idx' in segment:
                ga_dict['PhoneIndex'] = int(re.findall(r'[\d.]+', segment)[0])
            elif 'TC' in segment:
                ga_dict['TriggerCount'] = int(re.findall(r'[\d.]+', segment)[0])
            elif 'Rpt' in segment:
                ga_dict['Repeat'] = int(re.findall(r'[\d.]+', segment)[0])

        selected_folder_name = 'selected'
        # remove files in selected
        selected_path = os.path.join(self.data_save_dir, self.ga_run_name, selected_folder_name)
        selected_exist = os.path.exists(selected_path)
        if selected_exist:
            shutil.rmtree(selected_path, ignore_errors=True, onerror=None)
        os.mkdir(selected_path)

        # read the dir list
        all_solutions = pd.DataFrame()
        (_, individual_list, _) = next(os.walk(os.path.join(self.data_save_dir, self.ga_run_name)), ([], [], []))
        for individual in individual_list:
            if selected_folder_name != individual:
                string = re.split('_', individual)
                ind_dict = {'IndividualPath': os.path.join(self.data_save_dir, self.ga_run_name, individual),
                            'IndividualName': individual.replace('.', 'p')}
                for segment in string:
                    if "Gen" in segment:
                        generation = re.findall(r'\d+', segment)
                        ind_dict['Generation'] = int(generation[0])
                        ind_dict['Individual'] = int(generation[1])
                    # elif "AtkP" in segment:
                    #     ind_dict['AtkPNFrames'] = int(re.findall(r'[\d.]+', segment)[0])
                    # elif "PN" in segment:
                    #     ind_dict['PulseNumber'] = int(re.findall(r'[\d.]+', segment)[0])
                    # elif 'P' in segment and 'W' in segment and 'D' in segment and 'A' in segment and 'F' in segment:
                    #     pulse_info = re.split(r'P', segment)
                    #     pulse_info = list(filter(None, pulse_info))
                    #     ind_dict['PulseNumber'] = len(pulse_info)
                    #     for pulse in pulse_info:
                    #         values = re.findall(r'[\d.]+', pulse)
                    #         ind_dict['P' + values[0] + '-DelayUS'] = float(values[1])
                    #         ind_dict['P' + values[0] + '-WidthUS'] = float(values[2])
                    #         ind_dict['P' + values[0] + '-Amplitude'] = float(values[3])
                    #         ind_dict['P' + values[0] + '-FrequencyKHz'] = float(values[4])

                ind_dict.update(ga_dict)
                try:
                    df_scores = pd.read_csv(
                        os.path.join(self.data_save_dir, self.ga_run_name, individual, 'scores.csv'))
                except FileNotFoundError:
                    fitness = [_ for _ in string if 'F' in _][0]
                    fitness = float(re.findall(r'[-\d.]+', fitness)[0])
                    df_scores = pd.DataFrame([[fitness]], columns=['Fitness'])

                # read statistical information

                file_list = os.listdir(os.path.join(self.data_save_dir, self.ga_run_name, individual))
                event_number_file_name = [name for name in file_list if "eventNumber" in name]
                if len(event_number_file_name) == 0:
                    event_number_file_name = [name for name in file_list if "statistic_touch_count" in name]
                if len(event_number_file_name) != 0:
                    for file_name in event_number_file_name:
                        # event_number_file_name = event_number_file_name[0]
                        event_number = pd.read_csv(
                            os.path.join(self.data_save_dir, self.ga_run_name, individual, file_name))


                        pulse_info = event_number['PulseInfo'][0]
                        # get pulse number and information

                        ind_dict['PulseInfo'] = pulse_info
                        pulse_info = re.split(r'P', pulse_info)
                        pulse_info = list(filter(None, pulse_info))
                        ind_dict['PulseNumber'] = len(pulse_info)
                        ind_dict['AtkPNFrames'] = int(event_number['OneAttackPerNFrames'][0])
                        for pulse in pulse_info:
                            values = re.findall(r'[\d.]+', pulse)
                            pulse_number = int(values[0])
                            ind_dict['P' + values[0] + '-DelayUS'] = float(values[1])
                            ind_dict['P' + values[0] + '-WidthUS'] = float(values[2])
                            ind_dict['P' + values[0] + '-Amplitude'] = float(values[3])
                            ind_dict['P' + values[0] + '-FrequencyKHz'] = float(values[4])
                        if pulse_number < maximum_num_pulses:
                            for i in range(maximum_num_pulses - pulse_number):
                                ind_dict['P' + str(pulse_number + i + 1) + '-DelayUS'] = 0
                                ind_dict['P' + str(pulse_number + i + 1) + '-WidthUS'] = 0
                                ind_dict['P' + str(pulse_number + i + 1) + '-Amplitude'] = 0
                                ind_dict['P' + str(pulse_number + i + 1) + '-FrequencyKHz'] = 0

                        event_number = event_number.pivot(index='Repeat', columns='Type', values='Number')
                        event_number = pd.DataFrame(event_number.mean()).T
                        solution = pd.DataFrame(ind_dict, index=[0])
                        solution = pd.concat([solution, event_number, df_scores], axis=1)
                        if len(solution.columns) != len(all_solutions.columns):
                            # find the missing columns
                            missing_columns = [column for column in all_solutions.columns if
                                               column not in solution.columns]
                            for column in missing_columns:
                                solution[column] = 0
                            solution = solution.iloc[0].to_dict()
                        try:
                            all_solutions = all_solutions.append(solution, ignore_index=True)
                            # all_solutions = pd.concat([all_solutions, solution], axis=0)
                        except AssertionError:
                            fitness = df_scores['Fitness'][0]
                            if fitness != 0:
                                print(generation, fitness)

                else:
                    if len(file_list) != 2:
                        # warnings.warn('No eventNumber file found in Gen{}-{}'.format(generation[0], generation[1]))
                        print('No eventNumber file found in Gen{}-{}'.format(generation[0], generation[1]))

        all_solutions.sort_values(by=['Generation', 'Individual'], inplace=True)
        all_solutions.fillna(0, inplace=True)

        # generate two csv files
        best_solutions = all_solutions.sort_values(by=['Fitness'], ascending=False)
        best_solutions = best_solutions.head(self.topN).reset_index()

        all_solutions.to_csv(os.path.join(self.data_save_dir, self.ga_run_name, 'all_solutions_processed.csv'),
                             index=False)
        best_solutions.to_csv(os.path.join(self.data_save_dir, self.ga_run_name, 'best_solutions_processed.csv'),
                              index=False)

        # copy the good individuals to the selected folder
        for index, row in best_solutions.iterrows():
            src = row['IndividualPath'].replace('\\', '/')
            dst = selected_path + '/' + str(index) + '_' + str(row['Generation']) + '-' + str(row['Individual'])
            dst = dst.replace('\\', '/')
            shutil.copytree(src, dst)

    @staticmethod
    def normalized_sigmoid_fkt(a, b, x):
        """
        Returns array of a horizontal mirrored normalized sigmoid function
        output between 0 and 1
        Function parameters a = center; b = width
        """
        s = 1 / (1 + np.exp(b * (a - x)))
        return s

    def tuneScore(self):
        # for click only Y control purpose
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2)
        plt.subplots_adjust(wspace=.5)
        plt.subplots_adjust(hspace=.5)

        error_threshold = 300
        fitness_error_mean = np.linspace(10, 500, 1000)
        error_score = error_threshold / (fitness_error_mean + 0.1)
        ax1.plot(fitness_error_mean, error_score)
        ax1.axvline(x=error_threshold, color='tab:red', linestyle='--')
        ax1.text(error_threshold + 10, 3, 'th=%.1f\n(func: th/x)' % (error_threshold),
                 color='tab:red', ha="left")
        ax1.set_title('Error Score Y')
        ax1.set_ylabel('error_score_y')
        ax1.set_xlabel('y_error_mean (pixels)')
        ax1.grid()

        fitness_std = np.linspace(0, 200, 1000)
        std_threshold = 0.5
        shrink_factor = 100
        std_score = self.normalized_sigmoid_fkt(-std_threshold, 10, -fitness_std / shrink_factor)
        ax2.plot(fitness_std, std_score)
        ax2.axvline(x=std_threshold * shrink_factor, color='tab:red', linestyle='--')
        ax2.text(std_threshold * shrink_factor + 10, 0.5, 'th=%.1f\n(func: sigmoid)' % (std_threshold * shrink_factor),
                 color='tab:red', ha="left")
        ax2.set_title('Standard Variation Score Y')
        ax2.set_ylabel('std_score_y')
        ax2.set_xlabel('y_std (pixels)')
        ax2.grid()

        fitness_click_num = np.linspace(1, 200, 1000)
        num_score = np.log10(fitness_click_num)
        ax3.plot(fitness_click_num, num_score)
        ax3.axvline(x=10, color='tab:red', linestyle='--')
        ax3.text(10 + 10, 0.7, 'th=%.1f (func: log10)' % (10),
                 color='tab:red', ha="left")
        ax3.set_title('Click Number Score')
        ax3.set_ylabel('num_score')
        ax3.set_xlabel('click_num')
        ax3.grid()

        fitness_click_prop = np.linspace(0, 1, 1000)
        proportion_threshold = 0.7
        proportion_score = self.normalized_sigmoid_fkt(proportion_threshold, 20, fitness_click_prop)
        ax4.plot(fitness_click_prop, proportion_score)
        ax4.axvline(x=proportion_threshold, color='tab:red', linestyle='--')
        ax4.text(proportion_threshold - 0.1, 0.5, 'th=%.1f\n(func: sigmoid)' % (proportion_threshold),
                 color='tab:red', ha="right")
        ax4.set_title('Click Proportion Score')
        ax4.set_ylabel('proportion_score')
        ax4.set_xlabel('click_proportion')
        ax4.grid()
        plt.suptitle('fitness = error_score * (std_score + proportion_score) * num_score', size=15)

        error_threshold = 150
        fitness_error_mean = np.linspace(10, 500, 500)
        error_score = error_threshold / (fitness_error_mean + 0.1)
        ax5.plot(fitness_error_mean, error_score)
        ax5.axvline(x=error_threshold, color='tab:red', linestyle='--')
        ax5.text(error_threshold + 10, 3, 'th=%.1f\n(func: th/x)' % (error_threshold),
                 color='tab:red', ha="left")
        ax5.set_title('Error Score X')
        ax5.set_ylabel('error_score_x')
        ax5.set_xlabel('x_error_mean (pixels)')
        ax5.grid()

        fitness_std = np.linspace(0, 500, 500)
        std_threshold = 1
        shrink_factor = 200
        std_score = self.normalized_sigmoid_fkt(-std_threshold, 5, -fitness_std / shrink_factor)
        ax6.plot(fitness_std, std_score)
        ax6.axvline(x=std_threshold * shrink_factor, color='tab:red', linestyle='--')
        ax6.text(std_threshold * shrink_factor + 10, 0.5, 'th=%.1f\n(func: sigmoid)' % (std_threshold * shrink_factor),
                 color='tab:red', ha="left")
        ax6.set_title('Standard Variation Score X')
        ax6.set_ylabel('std_score_x')
        ax6.set_xlabel('x_std (pixels)')
        ax6.grid()

        # fitness_ = error_score * (std_score + proportion_score) * num_score

        plt.show()

        """
        """

        # # for swipe only Y direction control purpose
        # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        # plt.subplots_adjust(wspace=.5)
        # plt.subplots_adjust(hspace=.5)
        #
        # fitness_click_num = np.linspace(1, 200, 1000)
        # num_score = np.log10(fitness_click_num)
        # ax1.plot(fitness_click_num, num_score)
        # ax1.axvline(x=10, color='tab:red', linestyle='--')
        # ax1.text(10 + 10, 0.7, 'th=%.1f (func: log10)' % (10),
        #          color='tab:red', ha="left")
        # ax1.set_title('Swipe Number Score')
        # ax1.set_ylabel('num_score')
        # ax1.set_xlabel('swipe_num')
        # ax1.grid()
        #
        # fitness_swipe_prop = np.linspace(0, 1, 1000)
        # proportion_threshold = 0.55
        # clean_score = normalized_sigmoid_fkt(proportion_threshold, 10, fitness_swipe_prop)
        # ax2.plot(fitness_swipe_prop, clean_score)
        # ax2.axvline(x=proportion_threshold, color='tab:red', linestyle='--')
        # ax2.text(proportion_threshold - 0.1, 0.5, 'th=%.2f\n(func: sigmoid)' % (proportion_threshold),
        #          color='tab:red', ha="right")
        # ax2.set_title('Swipe Proportion Score')
        # ax2.set_ylabel('proportion_score')
        # ax2.set_xlabel('swipe_proportion')
        # ax2.grid()
        #
        # fitness_swipe_clean = np.linspace(0, 1, 1000)
        # proportion_threshold = 0.7
        # proportion_score = normalized_sigmoid_fkt(proportion_threshold, 20, fitness_swipe_clean)
        # ax3.plot(fitness_swipe_clean, proportion_score)
        # ax3.axvline(x=proportion_threshold, color='tab:red', linestyle='--')
        # ax3.text(proportion_threshold - 0.1, 0.5, 'th=%.1f\n(func: sigmoid)' % (proportion_threshold),
        #          color='tab:red', ha="right")
        # ax3.set_title('Correct Swipe Proportion Score')
        # ax3.set_ylabel('clean_score')
        # ax3.set_xlabel('correct_swipe_proportion')
        # ax3.grid()
        #
        # plt.suptitle('fitness = (proportion_score + 10 * clean_score) * num_score', size=15)
        #
        # fitness_ = (proportion_score + 10 * clean_score) * num_score
        #
        # plt.show()
