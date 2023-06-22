import numpy as np
import pandas as pd
import pygad
import csv
import os
from os.path import exists
from datetime import datetime
from sklearn.metrics import mean_absolute_error
import statistics
from PowerTouch.Automation.GeneticAlgorithm import GeneticAlgorithm

# warnings.filterwarnings("ignore")

# 1280 x 720
# TX horizontal
# unknown scanning method
# FT5435 digitizer
# *#*#64663#*#*

controlled_x_column = 5
expected_total_columns = 10

tap_region = 'lower'

def fitness_function(df_eventNumber, df_clicks, df_swipes, save_path):
    resolution_y = 1280
    resolution_x = 720

    resolution_number = 2
    if tap_region == 'lower':
        controlled_y_upper_bound = resolution_y / resolution_number * 1
        controlled_y_lower_bound = resolution_y / resolution_number * 0
    else:
        controlled_y_upper_bound = resolution_y / resolution_number * 2
        controlled_y_lower_bound = resolution_y / resolution_number * 1

    controlled_x = resolution_x / expected_total_columns * controlled_x_column

    if df_clicks is not None:
        # get click
        click_x_list = df_clicks['X'].to_numpy()
        click_y_list = df_clicks['Y'].to_numpy()
        click_num = len(df_clicks)
        mean_absolute_error_x = mean_absolute_error(np.full(np.shape(click_x_list), controlled_x), click_x_list)
        std_x = statistics.pstdev(click_x_list)

        click_y_list = click_y_list[click_y_list <= controlled_y_upper_bound]
        click_y_list = click_y_list[click_y_list >= controlled_y_lower_bound]

        # get swipe
        if df_swipes is not None:
            swipe_num = len(df_swipes)
        else:
            swipe_num = 0

        # get prop
        fitness_click_prop = click_num / (swipe_num + click_num)

        # calculate fitness
        hit_bonus = len(click_y_list)
        hit_penalty = click_num - len(click_y_list)
        error_score_x = ga.normalized_sigmoid_fkt(100, -0.05, mean_absolute_error_x)
        error_score = error_score_x
        std_score_x = ga.normalized_sigmoid_fkt(-0.5, 10, -std_x / 100)
        std_score = std_score_x
        num_score = np.log10(click_num)
        proportion_score = ga.normalized_sigmoid_fkt(.7, 20, fitness_click_prop)
        fitness = (hit_bonus - hit_penalty) * (std_score + error_score) * num_score * proportion_score
        print('')
        print('hit_bonus:', hit_bonus)
        print('hit_penalty:', hit_penalty)
        print('error_score_y: %.3f,' % error_score, 'error_mean_y: %.3f' % mean_absolute_error_x)
        print('  std_score_y: %.3f,' % std_score, 'std: %.3f' % std_x)
        print('   num_score: %.3f,' % num_score, 'num: %d' % click_num)
        print('  prop_score: %.3f,' % proportion_score, 'proportion: %.3f' % fitness_click_prop)
        print('     fitness: %.5f' % fitness)

    else:
        fitness = 0
        error_score = 0
        std_score = 0
        num_score = 0
        proportion_score = 0
        hit_bonus = 0
        hit_penalty = 0

    _ = {'Fitness': fitness,'hit_bonus': hit_bonus, 'hit_penalty': hit_penalty,
         'ErrorScore': error_score, 'StdScore': std_score,
         'NumberScore': num_score, 'PropScore': proportion_score}

    df = pd.DataFrame(_, index=[1])
    df.to_csv(os.path.join(save_path, 'scores.csv'), index=False)
    return fitness


# GA instance
ga = GeneticAlgorithm()
ga.setHardwareParameters(adb_server_pid=[4880], phone_index=1, phone_name='Redmi5A', frame_rate=115,
                         attack_template=ga.attackTemplate_default, sampling_frequency=400e3,
                         scope_position_ms=10, if_shell_communication=False,
                         data_save_dir='D:/Code/SuperCharge_Experiment_HZ/data_temp',
                         if_save_ad2_timestamp=False, if_save_figure=True, trigger_rate_error_threshold=5,
                         if_above_0=False, hysteresis_factor=0.1, relay_response_time=500, relay_guard_us=500,
                         scope_trigger_level_mv=-540, if_RisingPositive=False, screen_x_lim=(0, 720),
                         screen_y_lim=(1280, 0),
                         noise_channel=2, INITIAL_DELAY_US=None
                         )
ga.setHyperParameters(fitness_function=fitness_function,
                      target_description=['YTapRow5'+tap_region, 'ClickOnly', 'ClickNum'],
                      repeat_number=1, trigger_count=200,
                      maximum_pulse_num=3, minimum_pulse_num=1,
                      num_generations=50, sol_per_pop=50,
                      parent_selection_type='tournament', parent_selection_K_tournament=3,
                      num_parents_mating=20, keep_parents=0,
                      crossover_type="uniform", crossover_probability=0.5, growth_aging_probability=0.2,
                      mutation_type='random', mutation_probability=0.2, mutation_by_replacement=True,
                      save_topN=20,
                      stop_criteria=None,
                      continue_ga_run=None, minimum_fit_score=-10000,
                      maximum_frame_num=12, minimum_frame_num=4, step_frame_num=1,
                      maximum_pulse_width_us=2000, minimum_pulse_width_us=1, step_pulse_width_us=1,
                      maximum_pulse_delay_us=3000, minimum_pulse_delay_us=1, step_pulse_delay_us=1,
                      maximum_amplitude_V=80, minimum_amplitude_V=20, step_amplitude_V=1,
                      maximum_frequency_kHZ=499, minimum_frequency_kHZ=100, step_frequency_kHZ=1,
                      if_unified_amplitude=False, if_unified_frequency=False,
                      mutation_num_genes=None,
                      mutation_percent_genes='default', random_mutation_min_val=-1.0, random_mutation_max_val=1.0,
                      allow_duplicate_genes=True, suppress_warnings=False, save_best_solutions=False,
                      delay_after_gen=0, save_solutions=True,
                      genotype_template=None, geno2pheno_template=None)
ga.run()
ga.compileGAResults()
