from os import walk
from os import path
import os
import re
import pandas as pd
import shutil

# data_save_dir = 'D:/Code/SuperCharge/data_temp'
data_save_dir = 'D:/Data/data_temp'
# ga_run_name = '20220303-164732_YMean_YStd_ClickOnly_ClickNumber_Nexus5_3'
# ga_run_name = '20220304-094616_YMean_YStd_ClickOnly_ClickNumber_Nexus5_1'
# ga_run_name = '20220316-153141_YDirectionUp_YClean_SwipeOnly_SwipeNumber_Nexus5_3'
ga_run_name = '20220318-134612_YDirectionDown_YClean_SwipeOnly_SwipeNumber_Nexus5_3'
selected_folder_name = 'selected'
top = 20

# remove files in selected
selected_path = path.join(data_save_dir, ga_run_name, selected_folder_name)
selected_exist = path.exists(selected_path)
if selected_exist:
    shutil.rmtree(selected_path, ignore_errors=True, onerror=None)
os.mkdir(selected_path)

# read the dir list
all_solutions = pd.DataFrame()
(_, individual_list, _) = next(walk(path.join(data_save_dir, ga_run_name)), ([], [], []))
for individual in individual_list:
    if selected_folder_name != individual:
        string = re.split('[_]', individual)
        print(string)
        string_new = string[0:4] + [string[5]] + string[-2:]
        print(string_new)
        os.rename(os.path.join(data_save_dir, ga_run_name, individual),
                  os.path.join(data_save_dir, ga_run_name, '_'.join(string_new)))
