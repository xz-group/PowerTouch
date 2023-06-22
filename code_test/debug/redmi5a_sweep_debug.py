import warnings

from SuperCharge.AttackTemplate.Nexus5 import Nexus5
import numpy as np
from datetime import datetime
import os
import time
import pandas as pd

# experiment parameters
freq_start = 150  # KHz
freq_stop = 350  # KHz
freq_step = 5  # KHz
attack_row_list = [7]

hold_off_frame_N_start = 3  # hold off frame = 2*N+1
hold_off_frame_N_stop = 3
hold_off_frame_N_step = 2

trigger_count = 200

repeat = 3
data_save_dir = 'D:/Data/'
phone = 'Nexus5'
phone_index = 3
noise_real_peak2peak = 60
amplifier = 'PiezoDriveMX200'
verbose = False
adb_server_pid = 18492
gain_list = pd.read_csv('/SuperCharge/Parameters/max200_gain.csv')
continue_previous = False
previous_path = 'D:\Data/20220222-224543_Nexus5_1_TriggerRateSwipe_Double_PiezoDriveMX200_40V_16ms_96ms_16ms_TC500'


def gen_file_name(file_index=1):
    event_file_path = 'D:/Code/SuperCharge/event%d.txt' % file_index
    return event_file_path


# generate parameters
now = datetime.now()
freq_list = np.arange(freq_start, freq_stop, freq_step)
hold_off_N_list = np.arange(hold_off_frame_N_start, hold_off_frame_N_stop, hold_off_frame_N_step)
hold_off_N_list = np.append(hold_off_N_list, hold_off_frame_N_stop)
hold_off_start_ms = (hold_off_frame_N_start + 1) * 16
hold_off_stop_ms = (hold_off_frame_N_stop + 1) * 16
hold_off_step_ms = hold_off_frame_N_step * 16

print('=' * 100)
print('Trigger Rate Sweep Experiment.')
print(str(now))
print('Phone: %s, Index: %d' % (phone, phone_index))
print('AFG Noise Peak2Peak: %.1fV' % noise_real_peak2peak)
print('Amplifier: %s' % amplifier)
print('Experiment trigger rate N: [%d (%.1fms), %d (%.1fms)] with %d (%.1fms) step (%d points).' % (
    hold_off_frame_N_start, hold_off_start_ms, hold_off_frame_N_stop, hold_off_step_ms,
    hold_off_frame_N_step, hold_off_step_ms, len(hold_off_N_list)))
print('Attack Rows (%d points):' % len(attack_row_list), attack_row_list)
print('Repeat: %d.' % repeat)
print('Trigger Count per Experiment: %d.' % trigger_count)
print('=' * 100)

# run
if continue_previous is True:
    path = previous_path
    # os.mkdir(path)
else:
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    directory = '_'.join(
        [timestamp, phone, str(phone_index), 'ClickVerify', amplifier, '%dV' % noise_real_peak2peak,
         '%dms' % hold_off_start_ms, '%dms' % hold_off_stop_ms, '%dms' % hold_off_step_ms,
         'TC%d' % trigger_count])
    path = os.path.join(data_save_dir, directory)
    os.mkdir(path)

print('Parent folder:', path)
index = 0

for i in range(len(freq_list)):
    print('-' * 50)
    print('%d/%d: %.1fKhz' % (i + 1, len(freq_list), freq_list[i]))

    path_freq = os.path.join(path, '%dHz' % (freq_list[i] * 1e3))
    print('Frequency folder:', path_freq)
    os.mkdir(path_freq)

    for m in range(len(hold_off_N_list)):
        print('-' * 50)
        print(
            '%d/%d: N = %d (%.1fms)' % (m + 1, len(hold_off_N_list), hold_off_N_list[m], (hold_off_N_list[m] + 1) * 16))

        path_hold_off = os.path.join(path_freq, '%dms' % ((hold_off_N_list[m] + 1) * 16))
        print('Hold off folder:', path_hold_off)
        os.mkdir(path_hold_off)

        average_start = datetime.now()
        for j in range(len(attack_row_list)):
            print('Attack %d/%d Row: %d' % (j + 1, len(attack_row_list), attack_row_list[j]))

            path_row = os.path.join(path_hold_off, 'Row%d' % attack_row_list[j])
            print('Row folder:', path_row)
            os.mkdir(path_row)

            for k in range(repeat):

                print('')
                print('Repeat %d/%d.' % (k + 1, repeat))
                path_repeat = os.path.join(path_row, 'Repeat%d' % (k + 1))
                print('Repeat folder:', path_repeat)
                os.mkdir(path_repeat)
                while True:
                    print('')
                    print('Repeat %d/%d.' % (k + 1, repeat))
                    phone = Nexus5(verbose=verbose)
                    gain = gain_list.loc[gain_list.Frequency == freq_list[i] * 1e3, 'RealGain'].item()
                    print('Gain:', gain)
                    hold_off_ms = (hold_off_N_list[m] * 2 + 1) * 8 + 7
                    # phone.setupAttackSinglePulse_byRow(target_row=attack_row_list[j], verbose=verbose,
                    #                                    freq=freq_list[i] * 1e3,
                    #                                    peak2peak=noise_real_peak2peak / gain, if_above_0=False,
                    #                                    noise_channel=2, scope_trigger_holdoff_ms=hold_off_ms)
                    target_row = attack_row_list[j]
                    delay_us = phone.INITIAL_DELAY_US + (phone.SCAN_DELAY_US + phone.SCAN_PULSE_US) * (
                            target_row - 2)
                    phone.setupAttackArbitraryPulses(scope_trigger_level_mv=30,
                                                     sampling_frequency=800e3,
                                                     scope_trigger_holdoff_ms=hold_off_ms,
                                                     verbose=verbose,
                                                     scope_position_ms=4.7,
                                                     attack_width_list_us=[3*(phone.SCAN_PULSE_US+phone.SCAN_DELAY_US)],
                                                     attack_delay_list_us=[delay_us],
                                                     relay_guard_us=500,
                                                     relay_response_time=500,
                                                     noise_peak2peak=noise_real_peak2peak / gain,
                                                     noise_frequency=freq_list[i] * 1e3,
                                                     hysteresis_factor=0.8,
                                                     channel_index=2,
                                                     if_above_0=False)
                    phone.runAll(verbose=verbose, file_index=index, noise_channel=2, align_timing=False)
                    tr, flag = phone.monitorAD2_saveData_byTriggerCount(trigger_count_max=trigger_count, verbose=False)
                    phone.stopAll(adb_server_pid=adb_server_pid)
                    print('Trigger flag:', flag)
                    print('Trigger rate: %.1f' % tr)
                    if flag != "Normal":
                        raise ConnectionError('Screen closed. Please restart the screen.')

                    # check if the system is stable
                    if abs(tr - 1 / ((hold_off_N_list[m] + 1) * 16 / 1000)) <= 5:
                        # phone.monitorAD2_compileAnimation()
                        phone.monitorAD2_write2CSV(save_path=path_repeat + '/', if_write_original_file=False)
                        print('Event file size:', os.path.getsize(gen_file_name(file_index=index)))
                        # phone.screen.copyEventFile(event_file_path=gen_file_name(file_index=index),
                        #                            copy_to=path_repeat + '/')
                        phone.monitorScreen_readFromEventFile(event_file_path=gen_file_name(file_index=index),
                                                              verbose=verbose,
                                                              copy_path=path_repeat + '/')
                        phone.monitorScreen_write2CSV(save_path=path_repeat + '/',
                                                                             if_statistics=False)
                        # number_of_touches = len(phone.screen.records)
                        # try:
                        #     all = num_click + num_swipe
                        #     print('Number of touch events: %d, Click %d (%.2f), Swipe %d (%.2f)' % (number_of_touches,
                        #                                                                             num_click,
                        #                                                                             num_click / all,
                        #                                                                             num_swipe,
                        #                                                                             num_swipe / all))
                        # except ZeroDivisionError:
                        #     print('Number of touch events: %d, Click %d (%.2f), Swipe %d (%.2f)' % (number_of_touches,
                        #                                                                             num_click,
                        #                                                                             0,
                        #                                                                             num_swipe,
                        #                                                                             0))
                        break
                    else:
                        print('Trigger rate cannot meet requirement: %.1f!' % (
                                1 / ((hold_off_N_list[m] + 1) * 16 / 1000)))
                        print('-' * 10)

        ran = (datetime.now() - now).total_seconds() / 60
        average = (datetime.now() - average_start).total_seconds() / 60
        remain = average * (len(freq_list) - i) * (len(hold_off_N_list) - m)
        print('Running: %.2fmin' % ran)
        print('Remaining: %.2fmin' % remain)
        print('-' * 50)
        print('')
