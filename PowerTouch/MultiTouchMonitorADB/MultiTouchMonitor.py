import time

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from datetime import datetime
import shutil
from PowerTouch.MultiTouchMonitorADB.PlotHandler import TouchEventPlotHandler
from PowerTouch.MultiTouchMonitorADB.DataTemplate import Slot
import signal
import os
import shlex
import psutil
import warnings
from matplotlib.patches import Rectangle


class MultiTouchMonitor:
    def __init__(self, max_multi_touch=10, adb_path="C:/Users/zhuhu/Downloads/platform-ft5x06/adb"):
        # create the slots
        self._max_multi_touch = max_multi_touch
        self.slots = []
        for i in range(self._max_multi_touch):
            self.slots.append(Slot(slot_index=i))
        self._current_slot = None
        self._unsolved_touch = []
        self._unsolved_touch_lines = []

        self._parsed_tracking_id = [-1]
        self._all_tracking_id = []
        self._color_list = ['tab:green', 'tab:blue', 'tab:orange', 'tab:purple', 'tab:cyan', 'tab:olive', 'tab:gray',
                            'tab:brown', 'tab:pink', 'tab:red']

        # for communication
        self.adb_path = adb_path
        self.time_difference = None
        self._process_event = None

        # the data
        self.timestamps = []
        self.records = pd.DataFrame()
        self.statistic_click = pd.DataFrame()
        self.statistic_swipe = pd.DataFrame()
        self.statistic_touch_count = pd.DataFrame()

    # def setupPhoneCommunicationServer(self, ip='192.168.1.109', verbose=True):
    #     """
    #     set up the adb communication server by running "adb connect ip" command
    #     :param ip: The ip address of the smartphone
    #     :param verbose: if print the inputted command
    #     :return: None
    #     """
    #     connection = ' '.join(['connect', ip])
    #     cm1 = ' '.join([self.adb_path, connection])
    #     if verbose is True:
    #         print(cm1)
    #     subprocess.Popen(cm1)

    def initiatePhoneCommunication(self, verbose=True, file_index=0, event_path='D:/Code/PowerTouch',
                                   if_shell_communication=True):
        if if_shell_communication is True:
            command = "shell getevent -lt /dev/input/event1"
        else:
            command = "exec-out getevent -lt /dev/input/event1"
        events_path = os.path.join(event_path, 'event%d.txt' % file_index)
        events_path = events_path.replace('\\', '/')

        cm2 = ' '.join(["cmd", "/c", self.adb_path, command, '>', events_path])

        if verbose is True:
            print(cm2)
        self._process_event = subprocess.Popen(shlex.split(cm2), shell=False)

        if verbose is True:
            print('cmd.exe: pid', self._process_event.pid)

    def terminatePhoneCommunication(self, adb_server_pid=0, verbose=False):
        process_name = 'adb.exe'
        if adb_server_pid == 0:
            return 0

        # Iterate over the all the running process
        proc_obj_list = [procObj for procObj in psutil.process_iter() if process_name in procObj.name().lower()]

        if isinstance(adb_server_pid, list) is False:
            adb_server_pid = [adb_server_pid]

        # Kill the program
        for elem in proc_obj_list:
            if elem.pid in adb_server_pid:
                if verbose is True:
                    print("Keep:", elem)
            else:
                if verbose is True:
                    print("Kill:", elem)
                os.kill(elem.pid, signal.SIGTERM)
        self._process_event.kill()

    def checkPhoneConnection(self, verbose=True):
        command = "devices"
        cm = ' '.join([self.adb_path, command])
        p = subprocess.Popen(cm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        connected_devices, err = p.communicate()
        if len(err) != 0:
            raise ChildProcessError(err.decode("utf-8"))
        connected_devices = connected_devices.decode("utf-8")
        p.terminate()
        lines = re.split('\r*\n', connected_devices)
        lines = [i for i in lines if i]

        if len(lines) == 2:
            if verbose is True:
                print("ADB connected to: [%s]" % lines[1])
        else:
            raise ValueError('Cannot connect to the phone.')

    # def alignPhoneTiming(self, verbose=True):
    #     if verbose is True:
    #         print('Time Aligning:')
    #     command = "shell /data/local/tmp/gettime"
    #     cm = ' '.join([self.adb_path, command])
    #     p = subprocess.Popen(cm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     time_now = datetime.now().timestamp()  # this line must be here
    #     time_read, err = p.communicate()
    #     if len(err) != 0:
    #         raise ChildProcessError(err.decode("utf-8"))
    #
    #     time_read = time_read.decode("utf-8")
    #     p.terminate()
    #
    #     lines = re.split('\r*\n', time_read)
    #     realtime = [line for line in lines if "Realtime" in line][0]
    #     if verbose is True:
    #         print('\t%s' % realtime)
    #     realtime = float(re.findall(r"(\d+[,.]+\d+)", realtime)[0])
    #     monotonic_time = [line for line in lines if "Monotonic" in line][0]
    #     if verbose is True:
    #         print('\t%s' % monotonic_time)
    #     monotonic_time = float(re.findall(r"(\d+[,.]+\d+)", monotonic_time)[0])
    #     self.time_difference = time_now - monotonic_time
    #     if verbose is True:
    #         print('\tPC[%.9f] - PR[%.9f] = %.9f' % (time_now, realtime, time_now - realtime))
    #         print('\tPC[%.9f] - M[%.9f] = %.9f' % (time_now, monotonic_time, self.time_difference))

    def readPhoneBattery(self, verbose=False):
        command = "shell dumpsys battery"
        cm = ' '.join([self.adb_path, command])
        p = subprocess.Popen(cm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        battery_info, err = p.communicate()
        if len(err) != 0:
            raise ChildProcessError(err.decode("utf-8"))
        battery_info = battery_info.decode("utf-8")
        p.terminate()
        level = re.findall(r'level:[\s\d]+', battery_info)[0]
        level = float(re.findall(r'\d+', level)[0])
        usb_power = re.findall(r'USB.+', battery_info)[0]
        if 'true' in usb_power:
            usb_power = True
        else:
            usb_power = False
        if verbose is True:
            print('Phone Battery: [%.1f%%] [Charging:%s]' % (level, str(usb_power)))
        return level, usb_power

    def copyEventFile(self, event_file_path='../events.txt', copy_to='./'):
        shutil.copy2(event_file_path, ''.join([copy_to, 'events_', str(self.time_difference), '.txt']))
        return self.time_difference

    # def getTimeDifferenceFromFileName(self, file_name):
    #     value = re.findall(r'\d+\.\d+', file_name)
    #     if len(value) == 0:
    #         self.time_difference = None
    #     else:
    #         self.time_difference = float(value[0])
    #     return self.time_difference

    def parseEventFile(self, event_file_path='../events.txt', event_file_copy_to=None, verbose=True, save_raw_csv=None,
                       save_processed_csv=None):
        if event_file_copy_to is not None:
            shutil.copy2(event_file_path, event_file_copy_to)

        # read event files
        lines = []
        with open(event_file_path) as _f_read:
            for line in _f_read.readlines():
                if line.strip():
                    line_split = re.sub(r'[\[\]\n]+', '', line).split()
                    if len(line_split) == 4:
                        lines.append(line_split)
                    else:
                        warnings.warn('Incomplete packet:\n%s' % ''.join(line))

        if len(lines) == 0:
            return 0

        # split and parse the packets
        df_raw = pd.DataFrame(columns=['Time', 'Slot', 'ID', 'Tracking', 'Event', 'X', 'Y', 'Diameter', 'Pressure'])
        packet_index_previous = 0
        for i in range(len(lines)):

            if lines[i][2].lower() == 'ABS_MT_TRACKING_ID'.lower():
                self._all_tracking_id.append(self._32bStr2Int(lines[i][3]))

            if lines[i][1].lower() == 'EV_SYN'.lower():
                lines_packet = lines[packet_index_previous: i]
                if self.time_difference is None:
                    if float(lines[i][0]) not in self.timestamps:
                        self.timestamps.append(float(lines[i][0]))
                else:
                    if float(lines[i][0]) + self.time_difference not in self.timestamps:
                        self.timestamps.append(float(lines[i][0]) + self.time_difference)

                slot_index = []
                for j in range(len(lines_packet)):
                    if lines_packet[j][2].lower() == 'ABS_MT_SLOT'.lower():
                        slot_index.append(j)
                if len(slot_index) == 0:
                    slot_index.append(0)
                if slot_index[0] != 0:
                    slot_index.insert(0, 0)
                slot_index.append(len(lines_packet))
                for k in range(len(slot_index) - 1):
                    if slot_index[k] != slot_index[k + 1]:
                        df_raw = df_raw.append(self._parseSlot(lines_packet[slot_index[k]:slot_index[k + 1]]),
                                               ignore_index=True)
                    else:
                        pass
                packet_index_previous = i + 1

        # fill the slot information
        df_processed = df_raw.copy()
        df_processed = self._fill_slot_information(df_processed, current_slot=90)

        # fill the tracking id information
        df_processed = self._fill_tracking_information(df_processed)

        # get unsolved touches
        unsolved_touch = df_processed[df_processed['Tracking'].isnull() | (df_processed.Slot == 90)]

        # deal with unsolved touches
        if len(unsolved_touch) != 0:
            slot_list = unsolved_touch.Slot.to_numpy()
            slot_change_index = np.where(slot_list[:-1] != slot_list[1:])[0]
            if len(slot_change_index) == 0 and slot_list[0] == 90:  # totally no slot information
                df_processed = df_processed.replace({'Slot': 90}, 0)
                df_processed = self._fill_tracking_information(df_processed)
                pass
            elif 90 not in slot_list:  # there exists slot information
                pass
            elif len(slot_change_index) >= 1 and slot_list[0] == 90:
                df_processed = df_processed.replace({'Slot': 90}, unsolved_touch.iloc[slot_change_index[0] + 1])
                df_processed = self._fill_tracking_information(df_processed)
                pass
            else:
                print('\tNeed to deal with this.')
                print(unsolved_touch)
                raise ValueError

        # get unsolved touches
        df_processed = df_processed.replace({'Slot': 90}, np.nan)
        unsolved_touch = df_processed[df_processed['Tracking'].isnull() | (df_processed['Slot'].isnull())]

        if len(unsolved_touch) != 0:
            if len(unsolved_touch) >= 5 or len(unsolved_touch) / len(df_processed) >= 0.2:
                warnings.warn("\nNo Tracking information, dropped: %d (out of %d)" % (len(unsolved_touch),
                                                                                      len(df_processed)))
                print(unsolved_touch)
            else:
                print("\tNo Tracking information, dropped: %d (out of %d)" % (len(unsolved_touch),
                                                                              len(df_processed)))
                if verbose is True:
                    print(unsolved_touch)
            df_processed.drop(unsolved_touch.index, inplace=True)

        # fill the Event and other information
        id_list = list(set(df_processed.Tracking))
        for id in id_list:
            temp = df_processed[df_processed['Tracking'] == id]
            temp2 = temp.copy()
            reported_id = temp2.ID.to_numpy()
            if -1 in reported_id:
                index = 0
                x = np.nan
                y = np.nan
                diameter = np.nan
                pressure = np.nan
                for i, row in temp2.iterrows():
                    if index == 0:
                        temp2.loc[i, 'Event'] = 'New'
                    elif index + 1 == len(temp2):
                        temp2.loc[i, 'Event'] = 'Lift'
                    else:
                        temp2.loc[i, 'Event'] = 'Move'

                    if index + 1 != len(temp2):
                        if np.isnan(temp2.loc[i].X):
                            temp2.loc[i, 'X'] = x
                        else:
                            x = temp2.loc[i].X

                        if np.isnan(temp2.loc[i].Y):
                            temp2.loc[i, 'Y'] = y
                        else:
                            y = temp2.loc[i].Y

                        if np.isnan(temp2.loc[i].Diameter):
                            temp2.loc[i, 'Diameter'] = diameter
                        else:
                            diameter = temp2.loc[i].Diameter

                        if np.isnan(temp2.loc[i].Pressure):
                            temp2.loc[i, 'Pressure'] = pressure
                        else:
                            pressure = temp2.loc[i].Pressure
                    else:
                        temp2.loc[i, 'X'] = 0
                        temp2.loc[i, 'Y'] = 0
                        temp2.loc[i, 'Diameter'] = 0
                        temp2.loc[i, 'Pressure'] = 0
                    index += 1
                for i, row in temp2.iterrows():  # write back to main df
                    df_processed.loc[i] = row
            else:
                df_processed.drop(temp2.index, inplace=True)
                print("\tNo lift reported, dropped: %d" % len(temp2))
                if verbose is True:
                    print(temp2)
            pass

        # generate slot info
        self.records = df_processed.copy()
        slot_list = list(set(self.records['Slot']))

        self.timestamps = list(set(self.records['Time']))
        self.timestamps.sort()

        self._parsed_tracking_id = list(set(self.records['Tracking']))
        self._parsed_tracking_id.sort()

        for i in range(len(slot_list)):
            event_record = self.records[self.records.Slot == slot_list[i]]
            self.slots[int(slot_list[i])].addSlotRecordDataframe(event_record)
            self.slots[int(slot_list[i])].parseSlotRecordDataframe()

        if save_raw_csv is not None:
            df_raw.to_csv(''.join([save_raw_csv, 'events_raw', '.csv']), index=False)
        if save_processed_csv is not None:
            # compared with record, this file is used to debug the parser
            df_processed.to_csv(''.join([save_processed_csv, 'events_processed', '.csv']), index=False)

    @staticmethod
    def _fill_slot_information(touch_df, current_slot=90):
        for i, _ in touch_df.iterrows():
            if ~np.isnan(touch_df.loc[i].Slot):
                current_slot = touch_df.loc[i].Slot
            else:
                touch_df.loc[i].Slot = current_slot

        return touch_df

    @staticmethod
    def _fill_tracking_information(touch_df):
        slot_list = list(set(touch_df['Slot']))
        for slot in slot_list:
            if slot != 90:
                temp = touch_df[touch_df['Slot'] == slot]
                tracking = np.nan
                for i, _ in temp.iterrows():
                    if np.isnan(temp.loc[i].Tracking):
                        if np.isnan(tracking):
                            if ~np.isnan(temp.loc[i].ID) and temp.loc[i].ID != -1:
                                tracking = temp.loc[i].ID
                                temp.loc[i].Tracking = tracking
                        if ~np.isnan(tracking):
                            if np.isnan(temp.loc[i].ID):
                                temp.loc[i].ID = tracking
                            elif temp.loc[i].ID != -1:
                                tracking = temp.loc[i].ID
                            else:
                                pass
                            temp.loc[i].Tracking = tracking
                for i, row in temp.iterrows():  # write back to main df
                    touch_df.loc[i] = row
        return touch_df

    def _parseSlot(self, lines):
        timestamp = float(lines[0][0])
        if self.time_difference is not None:
            timestamp = timestamp + self.time_difference
        read_index = 0

        x = np.nan
        y = np.nan
        diameter = np.nan
        pressure = np.nan
        slot = np.nan
        tracking_id = np.nan
        if read_index != len(lines):
            for line in lines:
                if line[2].lower() == 'ABS_MT_SLOT'.lower():
                    slot = int(self._32bStr2Int(line[3]))
                elif line[2].lower() == 'ABS_MT_TRACKING_ID'.lower():
                    tracking_id = self._32bStr2Int(line[3])
                elif line[2].lower() == 'ABS_MT_POSITION_X'.lower():
                    x = self._32bStr2Int(line[3])
                elif line[2].lower() == 'ABS_MT_POSITION_Y'.lower():
                    y = self._32bStr2Int(line[3])
                elif line[2].lower() == 'ABS_MT_TOUCH_MAJOR'.lower():
                    diameter = self._32bStr2Int(line[3])
                elif line[2].lower() == 'ABS_MT_PRESSURE'.lower():
                    pressure = self._32bStr2Int(line[3])
                else:
                    # warnings.warn('Unknown line: %s' % ' '.join(line))
                    pass
        return {'ID': tracking_id, 'X': x, 'Y': y, 'Diameter': diameter, 'Pressure': pressure,
                'Time': timestamp, 'Slot': slot}

    @staticmethod
    def _twos_comp(val, bits=32):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val

    def _32bStr2Int(self, string, bits=16):
        return self._twos_comp(int(string, bits))

    def writeMultiTouchRecord2CSV(self, save_path='./'):
        filename = 'events'
        self.records.to_csv(''.join([save_path, filename, '.csv']), index=False)

    def readCSV2MultiTouchRecord(self, read_path='./', filename='events'):
        self.records = pd.read_csv(''.join([read_path, filename, '.csv']))

        # reset parameters
        self.statistic_swipe = pd.DataFrame()
        self.statistic_click = pd.DataFrame()
        self.statistic_touch_count = pd.DataFrame()
        self.timestamps = []
        self.slots = []
        for i in range(self._max_multi_touch):
            self.slots.append(Slot(slot_index=i))

        slot_list = list(set(self.records['Slot']))

        self.timestamps = list(set(self.records['Time']))
        self.timestamps.sort()

        self._parsed_tracking_id = list(set(self.records['Tracking']))
        self._parsed_tracking_id.sort()

        for i in range(len(slot_list)):
            event_record = self.records[self.records.Slot == slot_list[i]]
            self.slots[int(slot_list[i])].addSlotRecordDataframe(event_record)
            self.slots[int(slot_list[i])].parseSlotRecordDataframe()
        pass

    def compileMultiTouchStatistics(self):
        # combine the statistics of all slots
        dropped = 0
        total = 0
        processed = 0
        processed_new = 0

        for i in range(len(self.slots)):
            self.slots[i].compileSlotStatistics()
            self.statistic_click = self.statistic_click.append(self.slots[i].statistic_click)
            self.statistic_swipe = self.statistic_swipe.append(self.slots[i].statistic_swipe)
            dropped += len(np.unique(self.slots[i].record_dropped.Time.to_numpy()))
            total += len(np.unique(self.slots[i].record_full.Time.to_numpy()))
            processed += len(np.unique(self.slots[i].record.Time.to_numpy()))
            processed_new += len(np.unique(self.slots[i].record[self.slots[i].record['ID'] != -1].Time.to_numpy()))

        # count the click number
        self.statistic_touch_count = pd.DataFrame(columns=['Type', 'Number'])
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'Click',
                                                                        'Number': len(self.statistic_click)
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'Swipe',
                                                                        'Number': len(self.statistic_swipe)
                                                                        }, ignore_index=True)
        total_touches = len(self.statistic_swipe) + len(self.statistic_click)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'TotalTouches',
                                                                        'Number': total_touches
                                                                        }, ignore_index=True)
        if total_touches == 0:
            click_proportion = 0
            swipe_proportion = 0
        else:
            click_proportion = len(self.statistic_click) / total_touches
            swipe_proportion = len(self.statistic_swipe) / total_touches
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ClickProportion',
                                                                        'Number': click_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeProportion',
                                                                        'Number': swipe_proportion
                                                                        }, ignore_index=True)

        swipe_x_left = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'left'])
        swipe_x_right = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'right'])
        swipe_x_center = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'center'])
        swipe_y_up = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'up'])
        swipe_y_down = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'down'])
        swipe_y_center = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'center'])
        if len(self.statistic_swipe) == 0:
            swipe_x_left_proportion = 0
            swipe_x_right_proportion = 0
            swipe_x_center_proportion = 0
            swipe_y_up_proportion = 0
            swipe_y_down_proportion = 0
            swipe_y_center_proportion = 0
        else:
            swipe_x_left_proportion = swipe_x_left / len(self.statistic_swipe)
            swipe_x_right_proportion = swipe_x_right / len(self.statistic_swipe)
            swipe_x_center_proportion = swipe_x_center / len(self.statistic_swipe)
            swipe_y_up_proportion = swipe_y_up / len(self.statistic_swipe)
            swipe_y_down_proportion = swipe_y_down / len(self.statistic_swipe)
            swipe_y_center_proportion = swipe_y_center / len(self.statistic_swipe)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXLeft',
                                                                        'Number': swipe_x_left
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXRight',
                                                                        'Number': swipe_x_right
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXCenter',
                                                                        'Number': swipe_x_center
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXLeftProportion',
                                                                        'Number': swipe_x_left_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXRightProportion',
                                                                        'Number': swipe_x_right_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXCenterProportion',
                                                                        'Number': swipe_x_center_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYUp',
                                                                        'Number': swipe_y_up
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYDown',
                                                                        'Number': swipe_y_down
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYCenter',
                                                                        'Number': swipe_y_center
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYUpProportion',
                                                                        'Number': swipe_y_up_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYDownProportion',
                                                                        'Number': swipe_y_down_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYCenterProportion',
                                                                        'Number': swipe_y_center_proportion
                                                                        }, ignore_index=True)

        # count the events number
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'DroppedEvents',
                                                                        'Number': dropped
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'TotalEvents',
                                                                        'Number': total
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ProcessedEvents',
                                                                        'Number': processed
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ProcessedEventsOnlyNew',
                                                                        'Number': processed_new
                                                                        }, ignore_index=True)

    def writeMultiTouchStatistics2CSV(self, save_path='./', suffix='', prefix=''):
        self.statistic_click.to_csv(os.path.join(save_path, prefix + 'statistic_click' + suffix + '.csv'), index=False)
        self.statistic_swipe.to_csv(os.path.join(save_path, prefix + 'statistic_swipe' + suffix + '.csv'), index=False)
        self.statistic_touch_count.to_csv(os.path.join(save_path, prefix + 'statistic_touch_count' + suffix + '.csv'),
                                          index=False)

        # self.statistic_click.to_csv(''.join([save_path, 'click', suffix, '.csv']), index=False)
        # self.statistic_swipe.to_csv(''.join([save_path, 'nonclick', suffix, '.csv']), index=False)
        # self.statistic_touch_count.to_csv(''.join([save_path, 'eventNumber', suffix, '.csv']), index=False)

    def plotMultiTouch(self, time_delay=1, persistence=False, plot_circle=True, show_cross_mark=True):

        plt.ion()
        fig, axes = plt.subplots()
        # fig.set_figheight(10)
        # fig.set_figwidth(6.5)
        axes.set_xlim([0, 1080])
        axes.set_ylim([1920, 0])
        axes.set_aspect('equal')
        plt.tight_layout()
        touches = {}
        death_note = []
        axes.grid(color='darkgray', linestyle='--', linewidth=0.5)
        rows = np.linspace(0, 1920, 27)
        for i in range(len(rows)):
            axes.axhline(y=rows[i], color='tab:red', linewidth=0.5, linestyle='--')
            axes.text(1080, rows[i], str(i + 1), color='tab:red', va='center')
        plt.tight_layout()

        for time in self.timestamps:
            axes.set_title(time)

            # clear lifted touches
            if persistence is False:
                if len(death_note) != 0:
                    for deceased in death_note:
                        touches[deceased].clearTouch()
                        del touches[deceased]
                        death_note.remove(deceased)

            # plot slot touches
            for i in range(len(self.slots)):
                dataframe = self.slots[i].record.query('Time == @time')
                if dataframe.empty is True:
                    continue
                elif len(dataframe) == 1:
                    event = dataframe['Event'].values[0]
                    tracking_id = dataframe['Tracking'].values[0]
                    x = dataframe['X'].values[0]
                    y = dataframe['Y'].values[0]
                    diameter = dataframe['Diameter'].values[0]

                    if event == 'New':
                        touches[str(tracking_id)] = TouchEventPlotHandler(axes, slot_index=i,
                                                                          color_list=self._color_list)
                        touches[str(tracking_id)].plotNewTouch(timestamp=time, tracking_id=tracking_id, x=x, y=y,
                                                               diameter=diameter, plot_circle=plot_circle)
                    elif event == 'Move':
                        touches[str(tracking_id)].plotMoveTouch(timestamp=time, x=x, y=y, diameter=diameter,
                                                                plot_circle=plot_circle)
                    elif event == 'Lift':
                        if show_cross_mark is True:
                            touches[str(tracking_id)].plotLiftTouch(timestamp=time)
                        death_note.append(str(tracking_id))
                else:
                    raise ValueError("More than one row.")

            plt.draw()
            plt.pause(time_delay)


def plotMultiTouchTiming(timestamp_file, click_file, non_click_file):
    time_list = []
    slot_list = []

    timestamp = pd.read_csv(timestamp_file, index_col=0)
    time_reference = timestamp.iloc[0].time
    time_r = timestamp.time.to_numpy() - time_reference
    timestamp['timeR'] = time_r
    time_list.extend(timestamp.timeR)

    click = pd.read_csv(click_file)
    time_r = click.StartTime.to_numpy() - time_reference
    click['StartTimeR'] = time_r
    time_list.extend(click.StartTimeR)
    time_r = click.EndTime.to_numpy() - time_reference
    click['EndTimeR'] = time_r
    time_list.extend(click.EndTimeR)
    slot_list.extend(click.Slot)

    non_click = pd.read_csv(non_click_file)
    time_r = non_click.StartTime.to_numpy() - time_reference
    non_click['StartTimeR'] = time_r
    time_list.extend(non_click.StartTimeR)
    time_r = non_click.EndTime.to_numpy() - time_reference
    non_click['EndTimeR'] = time_r
    time_list.extend(non_click.EndTimeR)
    slot_list.extend(non_click.Slot)
    pass

    fig, ax = plt.subplots()

    for i, row in click.iterrows():
        # add rectangle to plot
        ax.add_patch(Rectangle((row.StartTimeR, row.Slot - 0.45), row.EndTimeR - row.StartTimeR, 0.9,
                               facecolor='blue',
                               fill=True,
                               lw=1))
    for i, row in non_click.iterrows():
        # add rectangle to plot
        ax.add_patch(Rectangle((row.StartTimeR, row.Slot - 0.45), row.EndTimeR - row.StartTimeR, 0.9,
                               facecolor='green',
                               fill=True,
                               lw=1))

    # display plot
    ax.hlines(y=range(int(min(slot_list)), int(max(slot_list)) + 1), xmin=min(time_list), xmax=max(time_list),
              linewidth=1,
              color='gray', linestyles='--')
    ax.vlines(x=timestamp.timeR, ymin=min(slot_list) - 1, ymax=max(slot_list) + 1, linewidth=0.5, color='r',
              linestyles='--')
    plt.xlim([min(time_list), max(time_list)])
    plt.xlabel('Time(s)')
    plt.ylabel('Slot Index')
    plt.title('Blue:click, Green:swipe, Red lines: AD2 Trigger TimeStamp')
    # plt.grid()
    plt.ylim([min(slot_list) - 1, max(slot_list) + 1])
    plt.tight_layout()
    plt.show()
    pass
