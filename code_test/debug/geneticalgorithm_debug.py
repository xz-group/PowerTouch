import os.path

import pandas as pd

from SuperCharge.Automation.GeneticAlgorithm import GeneticAlgorithm
import numpy as np
import statistics
from sklearn.metrics import mean_absolute_error


def fitness_function(df_eventNumber, df_clicks, df_swipes, save_path):
    controlled_y_row = 15
    controlled_y = 1920 / 28 * controlled_y_row
    controlled_x = 1080 / 2  # mid points

    if df_clicks is not None:
        # get click
        click_x_list = df_clicks['X'].to_numpy()
        click_y_list = df_clicks['Y'].to_numpy()
        click_num = len(df_clicks)
        mean_absolute_error_x = mean_absolute_error(np.full(np.shape(click_x_list), controlled_x), click_x_list)
        mean_absolute_error_y = mean_absolute_error(np.full(np.shape(click_y_list), controlled_y), click_y_list)
        std_y = statistics.pstdev(click_y_list)
        std_x = statistics.pstdev(click_x_list)

        # get swipe
        if df_swipes is not None:
            swipe_num = len(df_swipes)
        else:
            swipe_num = 0

        # get prop
        fitness_click_prop = click_num / (swipe_num + click_num)

        # calculate fitness
        error_score_y = 300 / (mean_absolute_error_x + 0.1)
        error_score_x = 100 / (mean_absolute_error_y + 0.1)
        error_score = error_score_x + error_score_y
        std_score_y = ga.normalized_sigmoid_fkt(-0.5, 10, -std_y / 100)
        std_score_x = ga.normalized_sigmoid_fkt(-0.2, 20, -std_x / 200)
        num_score = np.log10(click_num)
        proportion_score = ga.normalized_sigmoid_fkt(.7, 20, fitness_click_prop)
        fitness = error_score * (std_score_y + std_score_x + proportion_score) * num_score
        print('')
        print('error_score_y: %.3f,' % error_score_y, 'error_mean_y: %.3f' % mean_absolute_error_x)
        print('error_score_x: %.3f,' % error_score_x, 'error_mean_x: %.3f' % mean_absolute_error_y)
        print('  std_score_y: %.3f,' % std_score_y, 'std: %.3f' % std_y)
        print('  std_score_x: %.3f,' % std_score_x, 'std: %.3f' % std_x)
        print('   num_score: %.3f,' % num_score, 'num: %d' % click_num)
        print('  prop_score: %.3f,' % proportion_score, 'proportion: %.3f' % fitness_click_prop)
        print('     fitness: %.5f' % fitness)

    else:
        fitness = 0
        error_score_x = 0
        error_score_y = 0
        std_score_y = 0
        std_score_x = 0
        num_score = 0
        proportion_score = 0

    _ = {'Fitness': fitness, 'ErrorScoreX': error_score_x, 'StdScoreX': std_score_x,
         'ErrorScoreY': error_score_y, 'StdScoreY': std_score_y,
         'NumberScore': num_score, 'PropScore': proportion_score}
    df = pd.DataFrame(_, index=[1])
    df.to_csv(os.path.join(save_path, 'scores.csv'), index=False)
    return fitness


ga = GeneticAlgorithm()
ga.setHardwareParameters(adb_server_pid=18492, phone_index=3, phone_name='Nexus5',
                         attack_template=ga.attackTemplate_default,
                         parameter_validate_template=ga.parameterValidateTemplate_Nexus5)
ga.setHyperParameters(fitness_function=fitness_function, target_description=['test'], trigger_count=200,
                      num_generations=10, sol_per_pop=10, maximum_pulse_num=5,
                      continue_ga_run='20220323-234428_test_Nexus5_3_TC200_Rpt1_SG2')
# ga.run()
ga.compileGAResults(data_save_dir='/data_temp',
                    ga_run_name='20220323-234428_test_Nexus5_3_TC200_Rpt1_SG10', save_top_N=20)
