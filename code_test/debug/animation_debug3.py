import os
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from SuperCharge import Nexus5

experiments = [
    '20220217-103607_Nexus5_1_RowSwipe_Consecutive_PiezoDriveMX200_60V_48ms_96ms_16ms_250kHz_350kHz_5kHz_RowConfig4_TC500'
]

data_path = 'D:\Data'

for experiment_name in experiments:
    print('=' * 80)
    print(experiment_name)
    print('=' * 80)
    experiment_list = os.listdir(data_path)
    for experiment in experiment_list:
        if experiment_name in experiment:
            experiment_path = os.path.join(data_path, experiment)
            if os.path.isdir(experiment_path):
                print(experiment_path)
                freq_list = os.listdir(experiment_path)
                freq_list.sort()
                index = 1
                for freq in freq_list:
                    freq_value = float(re.findall(r'\d+', freq)[0])
                    freq_path = os.path.join(experiment_path, freq)
                    if os.path.isdir(freq_path):
                        delay_list = os.listdir(freq_path)
                        for delay in delay_list:
                            delay_value = float(re.findall(r'\d+', delay)[0])
                            delay_path = os.path.join(freq_path, delay)
                            if os.path.isdir(delay_path):
                                row_list = os.listdir(delay_path)
                                for row in row_list:
                                    row_path = os.path.join(delay_path, row)
                                    if os.path.isdir(row_path):
                                        repeat_list = os.listdir(row_path)
                                        for repeat in repeat_list:
                                            repeat_path = os.path.join(row_path, repeat)
                                            if os.path.isdir(repeat_path):
                                                files_list = os.listdir(repeat_path)
                                                for file in files_list:
                                                    if 'events.csv' in file and os.path.isfile(
                                                            os.path.join(repeat_path, file)):
                                                        if os.path.getsize(os.path.join(repeat_path, file)) != 0:
                                                            phone = Nexus5(if_enableAD2=False)
                                                            phone.screen.readCSV2MultiTouchRecord(
                                                                read_path=repeat_path + '/',
                                                                filename='events')
                                                            phone.data_analyzer.addTouchScreenDataFrame(
                                                                phone.screen.slots, phone.screen.timestamps)
                                                            phone.data_analyzer.compileScreenAnimation(persistence=True,
                                                                                                       replay_interval_ms=10,
                                                                                                       if_real_time=False,
                                                                                                       show_cross_mark=False)
                                                            fig = plt.gcf()
                                                            fig.canvas.set_window_title(
                                                                ', '.join([freq, delay, row, repeat]))
                                                            plt.show()
