import os
import re
import warnings

import numpy as np
import pandas as pd

from SuperCharge import Nexus5

experiments = [
    # '20220211-145318_Nexus5_1_TriggerRateSwipe_PiezoDriveMX200_60V_16ms_96ms_16ms_TC500',
    # '20220213-153600_Nexus5_1_TriggerRateSwipe_Double_PiezoDriveMX200_60V_16ms_96ms_16ms_TC500',
    '20220315-131503_Nexus5_3_ClickVerify_PiezoDriveMX200_60V_80ms_128ms_32ms_TC200'
]

data_path = 'D:\Data'

for experiment_name in experiments:
    print('=' * 80)
    print(experiment_name)
    print('=' * 80)
    print('-' * 50)
    print('Parse the event file')
    print('-' * 50)
    """
    Parse the event file
    """
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
                                                    if 'event' in file and '.txt' in file and os.path.isfile(
                                                            os.path.join(repeat_path, file)):
                                                        if os.path.getsize(os.path.join(repeat_path, file)) != 0:
                                                            phone = Nexus5(if_enableAD2=False)
                                                            print(index, freq, delay, repeat, file)
                                                            phone.screen.getTimeDifferenceFromFileName(file)
                                                            phone.screen.parseEventFile(
                                                                event_file_path=os.path.join(repeat_path, file),
                                                                verbose=False,
                                                                save_raw_csv=repeat_path + '/',
                                                                save_processed_csv=repeat_path + '/')
                                                            phone.monitorScreen_write2CSV(save_path=repeat_path + '/',
                                                                                          if_statistics=False)
                                                        else:
                                                            try:
                                                                os.remove(os.path.join(repeat_path, 'events.csv'))
                                                            except FileNotFoundError:
                                                                pass
                                                            try:
                                                                os.remove(os.path.join(repeat_path, 'click.csv'))
                                                            except FileNotFoundError:
                                                                pass
                                                            try:
                                                                os.remove(os.path.join(repeat_path, 'nonclick.csv'))
                                                            except FileNotFoundError:
                                                                pass
                                                index += 1
                                            else:
                                                # os.remove(repeat_path)
                                                pass

    print('')
    print('-' * 50)
    print('Generate statistics')
    print('-' * 50)
    """
    Generate statistics
    """

    experiment_list = os.listdir(data_path)
    for experiment in experiment_list:
        if experiment_name in experiment:
            experiment_path = os.path.join(data_path, experiment)
            if os.path.isdir(experiment_path):
                print(experiment_path)
                freq_list = os.listdir(experiment_path)

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
                                                skip_flag = False
                                                for file in files_list:
                                                    if 'event' in file and '.txt' in file and os.path.isfile(
                                                            os.path.join(repeat_path, file)):
                                                        if os.path.getsize(os.path.join(repeat_path, file)) == 0:
                                                            skip_flag = True
                                                            print(index, freq, delay, repeat, file, 'Skipped')
                                                        else:
                                                            skip_flag = False
                                                for file in files_list:
                                                    if 'events.csv' in file and skip_flag is False:
                                                        print(index, freq, delay, repeat, file)
                                                        phone = Nexus5(if_enableAD2=False)
                                                        phone.screen.readCSV2MultiTouchRecord(
                                                            read_path=repeat_path + '/')
                                                        phone.screen.compileMultiTouchStatistics()
                                                        phone.screen.writeMultiTouchStatistics2CSV(
                                                            save_path=repeat_path + '/')
                                                index += 1

    print('')
    print('-' * 50)
    print('Combine all statistics to one csv')
    print('-' * 50)
    """
    Combine all statistics to one csv
    """

    search_name_list = ['nonclick.csv', 'click.csv', 'events_processed.csv', 'events_raw.csv', 'eventNumber.csv']
    experiment_list = os.listdir(data_path)
    for search_name in search_name_list:
        for experiment in experiment_list:
            if experiment_name in experiment:
                experiment_path = os.path.join(data_path, experiment)
                if os.path.isdir(experiment_path):
                    df = pd.DataFrame()
                    index = 1
                    freq_list = os.listdir(experiment_path)
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
                                            repeat_number = len(repeat_list)
                                            for repeat in repeat_list:
                                                repeat_value = float(re.findall(r'\d+', repeat)[0])
                                                repeat_path = os.path.join(row_path, repeat)
                                                if os.path.isdir(repeat_path):
                                                    files_list = os.listdir(repeat_path)
                                                    for file in files_list:
                                                        if search_name == file:
                                                            click = pd.read_csv(os.path.join(repeat_path, file))
                                                            click['Repeat'] = repeat_value
                                                            click['Frequency'] = freq_value
                                                            click['TotalRepeat'] = repeat_number
                                                            click['HoldOff'] = delay_value
                                                            df = df.append(click)
                                                    index += 1
                    df.to_csv(os.path.join(data_path, experiment + '_' + search_name), index=False)

    warnings.warn('Done')
