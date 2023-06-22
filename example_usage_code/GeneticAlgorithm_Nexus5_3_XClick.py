import os.path

import pandas as pd

from PowerTouch.Automation.GeneticAlgorithm import GeneticAlgorithm
import numpy as np
import statistics
from sklearn.metrics import mean_absolute_error
from itertools import groupby

tap_region = 'left'


def fitness_function(df_eventNumber, df_clicks, df_swipes, save_path):
    resolution_number = 2
    controlled_y_row = 15
    controlled_y = 1920 / 28 * controlled_y_row
    if tap_region == 'left':
        controlled_x_upper_bound = 1080 / resolution_number * 1
        controlled_x_lower_bound = 1080 / resolution_number * 0
    else:
        controlled_x_upper_bound = 1080 / resolution_number * 2
        controlled_x_lower_bound = 1080 / resolution_number * 1

    if df_clicks is not None:
        # get click
        click_x_list = df_clicks['X'].to_numpy()
        click_y_list = df_clicks['Y'].to_numpy()
        click_num = len(df_clicks)
        click_x_list = click_x_list[click_x_list <= controlled_x_upper_bound]
        click_x_list = click_x_list[click_x_list >= controlled_x_lower_bound]

        # get swipe
        if df_swipes is not None:
            swipe_num = len(df_swipes)
        else:
            swipe_num = 0

        # get prop
        fitness_click_prop = click_num / (swipe_num + click_num)

        # calculate fitness
        hit_bonus = len(click_x_list)
        hit_penalty = click_num - len(click_x_list)
        num_score = np.log10(click_num)
        proportion_score = ga.normalized_sigmoid_fkt(.7, 20, fitness_click_prop)
        mean_absolute_error_y = mean_absolute_error(np.full(np.shape(click_y_list), controlled_y), click_y_list)
        error_score_y = ga.normalized_sigmoid_fkt(-0.5, 10, -mean_absolute_error_y / 500)
        std_y = statistics.pstdev(click_y_list)
        error_score = error_score_y
        std_score_y = ga.normalized_sigmoid_fkt(-0.5, 10, -std_y / 200)
        fitness = (hit_bonus - hit_penalty) * proportion_score * (error_score + std_score_y) * num_score
        print('')
        print('hit_bonus:', hit_bonus)
        print('hit_penalty:', hit_penalty)
        print('   num_score: %.3f,' % num_score, 'num: %d' % click_num)
        print('  prop_score: %.3f,' % proportion_score, 'proportion: %.3f' % fitness_click_prop)
        print('error_score: %.3f,' % error_score, 'error: %.3f' % mean_absolute_error_y)
        print('std_score: %.3f,' % std_score_y, 'std: %.3f' % std_y)
        print('     fitness: %.5f' % fitness)

    else:
        fitness = -10000
        hit_bonus = 0
        hit_penalty = 0
        num_score = 0
        proportion_score = 0

    _ = {'Fitness': fitness, 'hit_bonus': hit_bonus, 'hit_penalty': hit_penalty,
         'NumberScore': num_score, 'PropScore': proportion_score}

    df = pd.DataFrame(_, index=[1])
    df.to_csv(os.path.join(save_path, 'scores.csv'), index=False)
    return fitness


_PHONE_NAME = 'Nexus5'
_INITIAL_DELAY_US = 430
_SCAN_PULSE_US = 62
_SCAN_DELAY_US = 213.6
_FRAME_RATE = 120
_FRAME_PERIOD_MS = 1 / _FRAME_RATE * 1e3
_NUM_OF_ROWS = 27

ga = GeneticAlgorithm()
# ga.tuneScore()
ga.setHardwareParameters(adb_server_pid=[4880], phone_index=3, phone_name='Nexus5',
                         attack_template=ga.attackTemplate_default,
                         frame_rate=_FRAME_RATE, sampling_frequency=400e3,
                         scope_position_ms=10, INITIAL_DELAY_US=None,
                         data_save_dir='D:/Code/SuperCharge_Experiment_HZ/data_temp')
ga.setHyperParameters(fitness_function=fitness_function,
                      target_description=['XHit2Regions', tap_region, 'ClickOnly', 'ClickNumber'],
                      repeat_number=1, trigger_count=150,
                      maximum_pulse_num=3, minimum_pulse_num=1,
                      num_generations=50, sol_per_pop=50,
                      parent_selection_type='tournament', parent_selection_K_tournament=3,
                      num_parents_mating=20, keep_parents=0,
                      crossover_type="uniform", crossover_probability=0.5, growth_aging_probability=0.2,
                      mutation_type='random', mutation_probability=0.2, mutation_by_replacement=True,
                      save_topN=20,
                      stop_criteria=None,
                      continue_ga_run='20220511-135436_XHit2Regions_right_ClickOnly_ClickNumber_PhN-Nexus5_Idx3_TC150_Rpt1_SG18',
                      minimum_fit_score=-10000,
                      maximum_frame_num=12, minimum_frame_num=4, step_frame_num=2,
                      maximum_pulse_width_us=3000, minimum_pulse_width_us=5, step_pulse_width_us=1,
                      maximum_pulse_delay_us=8000, minimum_pulse_delay_us=5, step_pulse_delay_us=1,
                      maximum_amplitude_V=80, minimum_amplitude_V=40, step_amplitude_V=1,
                      maximum_frequency_kHZ=499, minimum_frequency_kHZ=100, step_frequency_kHZ=1,
                      if_unified_amplitude=False, if_unified_frequency=False,
                      mutation_num_genes=None,
                      mutation_percent_genes='default', random_mutation_min_val=-1.0, random_mutation_max_val=1.0,

                      allow_duplicate_genes=True, suppress_warnings=False, save_best_solutions=False,
                      delay_after_gen=0, save_solutions=True,
                      genotype_template=None, geno2pheno_template=None)
# ga.debug_mode = True
ga.run()
ga.compileGAResults()
# ga.compileGAResults(data_save_dir='D:/Code/SuperCharge_Experiment_HZ/data_temp',
#                     ga_run_name='20220510-133528_XHit2Regions_left_ClickOnly_ClickNumber_PhN-Nexus5_Idx3_TC150_Rpt1_SG22',
#                     save_top_N=150)

