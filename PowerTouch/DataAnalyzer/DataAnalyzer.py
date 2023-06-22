import warnings

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.gridspec import GridSpec
from os import walk
import re
from PowerTouch.AnalogDiscovery.DataTemplate import AnalogDiscoveryDataFrame
from PowerTouch.MultiTouchMonitorADB.PlotHandler import TouchEventPlotHandler
import pandas as pd
import random


class DataAnalyzer:
    def __init__(self):

        # analog discovery 2
        self.ad2_data = []
        self.ad2_frame_time_list = []
        self._ad2_frame_time_list_extend = []
        self.ad2_trigger_rate = []
        self._ad2_frame_update_index_list = []
        self._ad2_axs = None
        self._ad2_frame_current_timestamp = 0
        self._ad2_frame_current_analog_time = []
        self._ad2_frame_current_analog_ch1 = []
        self._ad2_frame_current_analog_ch2 = []
        self._ad2_frame_current_digital_time = []
        self._ad2_frame_current_digital_channels = [[], []]
        self._ad2_frame_current_trigger_flag = 'None'
        self._ad2_frame_current_trigger_count = 0
        self._ad2_frame_current_trigger_rate = 0
        self._marker_pulse_start_position_ms = None
        self._marker_pulse_width_ms = None

        # screen
        self.screen_frame_time_list = []
        self._screen_frame_time_list_extend = []
        self._screen_frame_update_index_list = []
        self.screen_data = []
        self._screen_axs = None
        self._screen_touches = {}
        self._screen_death_note = []
        self._screen_color_list = ['tab:green', 'tab:blue', 'tab:orange', 'tab:purple', 'tab:cyan', 'tab:olive',
                                   'tab:gray',
                                   'tab:brown', 'tab:pink', 'tab:red']

        # animation
        self._ani_ad2 = None
        self._ani_screen = None
        self._ani_all = None

    """
    ##########################################
    Add data
    ##########################################
    """

    def addAnalogDiscoveryDataFrame(self, timestamp, analog_time, analog_ch1, analog_ch2, digital_time,
                                    digital_channels, trigger_flag, trigger_count, trigger_rate):
        self.ad2_data.append(
            AnalogDiscoveryDataFrame(timestamp=timestamp, analog_time=analog_time, analog_ch1=analog_ch1,
                                     analog_ch2=analog_ch2, digital_time=digital_time,
                                     digital_channels=digital_channels, trigger_flag=trigger_flag,
                                     trigger_count=trigger_count, trigger_rate=trigger_rate))
        self.ad2_frame_time_list.append(timestamp.timestamp())
        self.ad2_trigger_rate.append(trigger_rate)

    def addTouchScreenDataFrame(self, slots_data, timestamp_list):
        self.screen_data = slots_data
        self.screen_frame_time_list = timestamp_list

    """
    ##########################################
    Save data to file
    ##########################################
    """

    def writeAnalogDiscoveryDataFrameSeries(self, save_path='./'):
        for data in self.ad2_data:
            data.writeAnalogDiscoveryDataFrame(save_path=save_path)

    def writeAnalogDiscoveryDataFrameSeries_Compressed(self, save_path='./'):
        overall = pd.DataFrame()
        for data in self.ad2_data:
            df = data.writeAnalogDiscoveryDataFrame_Combined()
            overall = overall + df

    def writeAnalogDiscoveryTimeStamps(self, save_path='./', index=None):
        df = pd.DataFrame({'time': self.ad2_frame_time_list, 'triggerRate': self.ad2_trigger_rate})
        if index is None:
            df.to_csv(''.join([save_path, 'trigger_timestamps', '.csv']))
        else:
            df.to_csv(''.join([save_path, 'trigger_timestamps', str(index), '.csv']))

    def readAnalogDiscoveryDataFrame(self, read_path='./'):
        filenames = next(walk(read_path), (None, None, []))[2]
        filenames = [file for file in filenames if '.csv' in file]
        filenames.sort(key=self._num_sort)
        for i in range(int(len(filenames) / 2)):
            ad_frame = AnalogDiscoveryDataFrame()
            ad_frame.readAnalogDiscoveryDataFrame(read_path=read_path,
                                                  analog_filename=filenames[i * 2],
                                                  digital_filename=filenames[i * 2 + 1])
            self.ad2_data.append(ad_frame)
            self.ad2_frame_time_list.append(ad_frame.timestamp.timestamp())
            self.ad2_trigger_rate.append(ad_frame.trigger_rate)

    @staticmethod
    def _num_sort(string):
        score = int(re.findall(r'\d+', re.findall(r'TC\d+', string)[0])[0])
        if 'Digital' in string:
            score += 0.5
        return score

    """
    ##########################################
    Analog discovery 2 Animation 
    ##########################################
    """

    def createAD2FramePlotAnimation(self, frame_index):
        # frame_index is the default argument

        if frame_index in self._ad2_frame_update_index_list:
            real_frame_index = self._ad2_frame_update_index_list.index(frame_index)
            self._ad2_frame_current_timestamp = self.ad2_data[real_frame_index].timestamp
            self._ad2_frame_current_analog_time = self.ad2_data[real_frame_index].analog_time
            self._ad2_frame_current_analog_ch1 = self.ad2_data[real_frame_index].analog_channel_1
            self._ad2_frame_current_analog_ch2 = self.ad2_data[real_frame_index].analog_channel_2
            self._ad2_frame_current_digital_time = self.ad2_data[real_frame_index].digital_time
            self._ad2_frame_current_digital_channels = self.ad2_data[real_frame_index].digital_channels
            self._ad2_frame_current_trigger_flag = self.ad2_data[real_frame_index].trigger_flag
            self._ad2_frame_current_trigger_count = self.ad2_data[real_frame_index].trigger_count
            self._ad2_frame_current_trigger_rate = self.ad2_data[real_frame_index].trigger_rate
        timestamp = self._ad2_frame_current_timestamp
        analog_time = self._ad2_frame_current_analog_time
        analog_ch1 = self._ad2_frame_current_analog_ch1
        analog_ch2 = self._ad2_frame_current_analog_ch2
        digital_time = self._ad2_frame_current_digital_time
        digital_channels = self._ad2_frame_current_digital_channels
        trigger_flag = self._ad2_frame_current_trigger_flag
        trigger_count = self._ad2_frame_current_trigger_count
        trigger_rate = self._ad2_frame_current_trigger_rate

        # print(frame_index, '/', len(ad2_data))
        artiest = []

        text = [str(frame_index) + '/' + str(len(self._ad2_frame_time_list_extend)),
                "%.3fms" % ((self._ad2_frame_time_list_extend[frame_index] - self._ad2_frame_time_list_extend[
                    0]) * 1e3),
                trigger_flag, 'TR:%.1fsps, TC:%d' % (trigger_rate, trigger_count), str(timestamp)]
        info = self._ad2_axs[0].text(-.4, -60, ' | '.join(text),
                                     bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")
        artiest.append(info)

        for i in range(len(self._ad2_axs)):
            if i == 0:
                line, = self._ad2_axs[i].plot(analog_time * 1000, analog_ch1 * 1000, color='tab:blue')
                artiest.append(line)
                self._ad2_axs[i].set_title('Oscilloscope CH1 (Smartphone Screen)')
                self._ad2_axs[i].set_ylabel('Voltage(mV)')
                self._ad2_axs[i].set_ylim([-70, 70])
                self._ad2_axs[i].minorticks_on()
                self._ad2_axs[i].grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
                self._ad2_axs[i].grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
                self._ad2_axs[i].axvline(x=0, color='tab:red', linestyle='--')

                if self._marker_pulse_start_position_ms is not None:
                    self._ad2_axs[i].vlines(x=self._marker_pulse_start_position_ms,
                                            ymin=0, ymax=65,
                                            colors='tab:purple', ls=':')
                    for k in range(len(self._marker_pulse_start_position_ms)):
                        pos = self._marker_pulse_start_position_ms[k] + self._marker_pulse_width_ms * 0.3
                        self._ad2_axs[i].text(pos, 50, str(k + 1), color='tab:purple', ha='left')

            elif i == 1:
                line, = self._ad2_axs[i].plot(analog_time * 1000, analog_ch2, color='tab:orange')
                artiest.append(line)
                self._ad2_axs[i].set_title('Oscilloscope Ch2 (Waveform Generator)')
                self._ad2_axs[i].set_ylabel('Voltage(V)')
                # self._ad2_axs[i].set_ylim([-60e-3, 60e-3])
                self._ad2_axs[i].minorticks_on()
                self._ad2_axs[i].grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
                self._ad2_axs[i].grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
                self._ad2_axs[i].axvline(x=0, color='tab:red', linestyle='--')
                self._ad2_axs[i].relim()
                self._ad2_axs[i].autoscale_view()

            else:
                line, = self._ad2_axs[i].plot(digital_time * 1000, digital_channels[i - 2], color='tab:green')
                artiest.append(line)
                self._ad2_axs[i].set_title('Logic Analyzer Ch%d (Relay %d Control)' % (i - 2, i - 2))
                self._ad2_axs[i].set_ylabel('State')
                self._ad2_axs[i].set_ylim([-0.1, 1.1])
                self._ad2_axs[i].minorticks_on()
                self._ad2_axs[i].grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5, axis='x')
                self._ad2_axs[i].grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4, axis='x')
                self._ad2_axs[i].axvline(x=0, color='tab:red', linestyle='--')

            if i == len(self._ad2_axs) - 1:
                self._ad2_axs[i].set_xlabel('Time(ms)')
                self._ad2_axs[i].set_xlim([analog_time[0] * 1000, analog_time[-1] * 1000])

        return artiest

    def compileAD2Animation(self, replay_interval_ms=1, frame_resolution_ms=1, if_real_time=False,
                            marker_pulse_start_position_ms=None,
                            marker_pulse_width_ms=None):
        digital_channel_number = 2
        analog_channel_number = 2
        self._marker_pulse_start_position_ms = marker_pulse_start_position_ms
        self._marker_pulse_width_ms = marker_pulse_width_ms

        # calculate extended frame time list
        if if_real_time is True:
            start_time = self.ad2_frame_time_list[0]
            stop_time = self.ad2_frame_time_list[-1]
            self._ad2_frame_time_list_extend = np.arange(start_time, stop_time, frame_resolution_ms / 1e3).tolist()
        else:
            self._ad2_frame_time_list_extend = self.ad2_frame_time_list

        print('Number of frames: AD2 %d > %d.' % (len(self._ad2_frame_time_list_extend),
                                                  len(self.ad2_frame_time_list)))

        # calculate when to update the frame
        self._ad2_frame_update_index_list = []
        for i in range(len(self.ad2_frame_time_list)):
            time_real = self.ad2_frame_time_list[i]
            for j in range(len(self._ad2_frame_time_list_extend)):
                if len(self._ad2_frame_update_index_list) != 0:
                    if j < self._ad2_frame_update_index_list[-1]:
                        continue
                time_pre = self._ad2_frame_time_list_extend[j]
                if j == len(self._ad2_frame_time_list_extend) - 1:
                    if time_pre <= time_real:
                        self._ad2_frame_update_index_list.append(j)
                else:
                    time_post = self._ad2_frame_time_list_extend[j + 1]
                    if time_pre <= time_real < time_post:
                        self._ad2_frame_update_index_list.append(j)
                        break

        # create a figure
        fig, self._ad2_axs = plt.subplots(digital_channel_number + analog_channel_number, 1, sharex='all',
                                          figsize=(13, 8), gridspec_kw={'height_ratios': [3, 2, 1, 1]})

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.08, top=0.95, left=0.08, hspace=0.4)

        if replay_interval_ms <= 0:
            replay_interval_ms = round(1 / np.average(self.ad2_trigger_rate) * 1e3, 0)

        self._ani_ad2 = animation.FuncAnimation(fig, self.createAD2FramePlotAnimation, blit=True,
                                                interval=replay_interval_ms, repeat=True,
                                                frames=len(self._ad2_frame_time_list_extend))

        plt.show()

    def plotAD2Frame(self, frame_index=0, if_random=False, file_name='', marker_pulse_start_position_ms=None,
                     marker_pulse_width_ms=None, additional_info=None, if_show=False, if_save=True):

        self._marker_pulse_start_position_ms = marker_pulse_start_position_ms
        self._marker_pulse_width_ms = marker_pulse_width_ms

        # draw basic frame
        fig, (ax1, ax2, dx1, dx2) = plt.subplots(2 + 2, 1, sharex='all',
                                                 figsize=(12, 7),
                                                 gridspec_kw={'height_ratios': [3, 2, 1, 1]})

        # get data
        if len(self.ad2_data) == 0:
            warnings.warn('Zero length ad2_data.')
            return 0
        if if_random is True:
            frame_index = random.randint(0, len(self.ad2_data) - 1)
        else:
            if frame_index > len(self.ad2_data) or frame_index < 0:
                raise ValueError(frame_index)

        start = self.ad2_frame_time_list[0]
        now = self.ad2_frame_time_list[frame_index]
        trigger_rate = self.ad2_data[frame_index].trigger_rate
        trigger_flag = self.ad2_data[frame_index].trigger_flag
        trigger_count = self.ad2_data[frame_index].trigger_count

        # print info
        text = ["%.3fs" % (now - start), trigger_flag, 'TR:%.1fsps' % trigger_rate,
                'TC:%d' % trigger_count,
                str(self.ad2_data[frame_index].timestamp)]
        info = ax1.text(-.4, -60, ' | '.join(text), bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")

        if additional_info is not None:
            info2 = ax2.text(-.4, 5, ' | '.join(additional_info),
                             bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5},
                             ha="left")

        # read data
        ad2_analog_ch1_data = self.ad2_data[frame_index].analog_channel_1 * 1000
        ad2_analog_ch2_data = self.ad2_data[frame_index].analog_channel_2
        ad2_analog_time = self.ad2_data[frame_index].analog_time * 1000
        ad2_digital_chs_data = self.ad2_data[frame_index].digital_channels
        ad2_digital_time = self.ad2_data[frame_index].digital_time * 1000

        ad2_analog_ch1_line, = ax1.plot(ad2_analog_time, ad2_analog_ch1_data, color='tab:blue')
        ax1.set_title('Oscilloscope CH1 (Smartphone Screen)')
        ax1.set_ylabel('Voltage(mV)')
        ax1.set_xlim(ad2_analog_time[0], ad2_analog_time[-1])
        # ax1.set_ylim([-70, 70])
        ax1.minorticks_on()
        ax1.grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
        ax1.grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
        ax1.axvline(x=0, color='tab:red', linestyle='--')
        if self._marker_pulse_start_position_ms is not None:
            ax1.vlines(x=self._marker_pulse_start_position_ms,
                       ymin=0, ymax=65,
                       colors='tab:purple', ls=':')
            for k in range(len(self._marker_pulse_start_position_ms)):
                pos = self._marker_pulse_start_position_ms[k] + self._marker_pulse_width_ms * 0.3
                ax1.text(pos, 50, str(k + 1), color='tab:purple', ha='left')

        ad2_analog_ch2_line, = ax2.plot(ad2_analog_time, ad2_analog_ch2_data, color='tab:orange')
        ax2.set_title('Oscilloscope Ch2 (Waveform Generator)')
        ax2.set_ylabel('Voltage(V)')
        # ax2.set_ylim([-60, 60])
        ax2.minorticks_on()
        ax2.grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
        ax2.grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
        ax2.axvline(x=0, color='tab:red', linestyle='--')
        # ax2.set_xlabel('Time(ms)')

        channel_number = 2
        ad2_digital_chs_lines = [None] * channel_number
        axs = [dx1, dx2]
        for i in range(len(axs)):
            ad2_digital_chs_lines[i], = axs[i].plot(ad2_digital_time, ad2_digital_chs_data[i], color='tab:green')
            axs[i].set_title('Logic Analyzer Ch%d' % i)
            axs[i].set_ylabel('State')
            axs[i].set_ylim([-0.1, 1.1])
            # Turn on the minor TICKS, which are required for the minor GRID
            axs[i].minorticks_on()
            axs[i].grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5, axis='x')
            axs[i].grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4, axis='x')
            axs[i].axvline(x=0, color='tab:red', linestyle='--')
            if i == channel_number - 1:
                axs[i].set_xlabel('Time(ms)')

        plt.tight_layout()
        if if_show is True:
            plt.show()
        if if_save is True:
            plt.savefig("%s.png" % file_name)
            plt.close(fig)

    """
    ##########################################
    Screen Animation 
    ##########################################
    """

    def createScreenFramePlotAnimation(self, frame_index, plot_circle, show_cross_mark, persistence):

        if frame_index == 0:
            self._screen_touches = {}
            self._screen_death_note = []

        if len(self._screen_death_note) != 0:
            for deceased in self._screen_death_note:
                self._screen_touches[deceased].clearTouch()
                del self._screen_touches[deceased]
                self._screen_death_note.remove(deceased)

        text = [str(frame_index) + ' / ' + str(len(self._screen_frame_time_list_extend)),
                "%.3fms" % ((self._screen_frame_time_list_extend[frame_index] - self._screen_frame_time_list_extend[
                    0]) * 1e3)]
        info = self._screen_axs.text(20, 100, ' | '.join(text),
                                     bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")
        self._screen_axs.set_title('Touches on the Screen')

        # update frame
        if frame_index in self._screen_frame_update_index_list:
            real_frame_index = self._screen_frame_update_index_list.index(frame_index)
            time = self.screen_frame_time_list[real_frame_index]

            # plot slot touches
            for i in range(len(self.screen_data)):
                dataframe = self.screen_data[i].record.query('Time == @time')
                if dataframe.empty is True:
                    continue
                elif len(dataframe) == 1:
                    event = dataframe['Event'].values[0]
                    tracking_id = dataframe['Tracking'].values[0]
                    x = dataframe['X'].values[0]
                    y = dataframe['Y'].values[0]
                    diameter = dataframe['Diameter'].values[0]

                    if event == 'New':
                        self._screen_touches[str(tracking_id)] = TouchEventPlotHandler(self._screen_axs, slot_index=i,
                                                                                       color_list=self._screen_color_list)
                        self._screen_touches[str(tracking_id)].plotNewTouch(timestamp=time, tracking_id=tracking_id,
                                                                            x=x, y=y,
                                                                            diameter=diameter,
                                                                            plot_circle=plot_circle)
                    elif event == 'Move':
                        self._screen_touches[str(tracking_id)].plotMoveTouch(timestamp=time, x=x, y=y,
                                                                             diameter=diameter,
                                                                             plot_circle=plot_circle)
                    elif event == 'Lift':
                        if show_cross_mark is True:
                            self._screen_touches[str(tracking_id)].plotLiftTouch(timestamp=time)
                        if persistence is False:
                            self._screen_death_note.append(str(tracking_id))
        arts = []
        for key, touch in self._screen_touches.items():
            arts.extend(touch.returnArtist())

        return arts + [info]

    def compileScreenAnimation(self, persistence=False, plot_circle=True, show_cross_mark=True, replay_interval_ms=1,
                               frame_resolution_ms=1, if_real_time=False, repeat=True):

        # calculate extended frame time list
        if if_real_time is True:
            start_time = self.screen_frame_time_list[0]
            stop_time = self.screen_frame_time_list[-1]
            self._screen_frame_time_list_extend = np.arange(start_time, stop_time, frame_resolution_ms / 1e3).tolist()
        else:
            self._screen_frame_time_list_extend = self.screen_frame_time_list

        print('Number of frames: Screen %d > %d.' % (len(self._screen_frame_time_list_extend),
                                                     len(self.screen_frame_time_list)))
        # calculate when to update the frame
        self._screen_frame_update_index_list = []
        for i in range(len(self.screen_frame_time_list)):
            time_real = self.screen_frame_time_list[i]
            for j in range(len(self._screen_frame_time_list_extend)):
                if len(self._screen_frame_update_index_list) != 0:
                    if j < self._screen_frame_update_index_list[-1]:
                        continue
                time_pre = self._screen_frame_time_list_extend[j]
                if j == len(self._screen_frame_time_list_extend) - 1:
                    if time_pre <= time_real:
                        self._screen_frame_update_index_list.append(j)
                else:
                    time_post = self._screen_frame_time_list_extend[j + 1]
                    if time_pre <= time_real < time_post:
                        self._screen_frame_update_index_list.append(j)
                        break

        fig, self._screen_axs = plt.subplots(figsize=(13, 8))
        self._screen_axs.set_xlim([0, 1080])
        self._screen_axs.set_ylim([1920, 0])
        self._screen_axs.set_aspect('equal')
        self._screen_axs.grid(color='darkgray', linestyle='--', linewidth=0.5)
        rows = np.linspace(0, 1920, 27)
        # rows = np.delete(rows, [0, -1])
        for i in range(len(rows)):
            self._screen_axs.axhline(y=rows[i], color='tab:red', linewidth=0.5, linestyle='--')
            self._screen_axs.text(1080, rows[i], str(i + 1), color='tab:red', va='center')
        plt.tight_layout()

        self._ani_screen = animation.FuncAnimation(fig, self.createScreenFramePlotAnimation,
                                                   fargs=(plot_circle, show_cross_mark, persistence),
                                                   blit=True,
                                                   interval=replay_interval_ms, repeat=repeat,
                                                   frames=len(self._screen_frame_time_list_extend))

        # plt.show()

    def plotScreenFrame(self, file_name='', show_cross_mark=False, plot_circle=True, additional_info=None, if_save=True,
                        if_show=False, x_lim=(0, 1080), y_lim=(1920, 0)):

        fig, axes = plt.subplots()
        fig.set_figheight(10)
        fig.set_figwidth(6.5)
        axes.set_xlim([x_lim[0], x_lim[1]])
        axes.set_ylim([y_lim[0], y_lim[1]])
        axes.set_aspect('equal')
        plt.tight_layout()
        touches = {}
        death_note = []
        axes.grid(color='darkgray', linestyle='--', linewidth=0.5)
        # rows = np.linspace(0, 1920, 27)
        # for i in range(len(rows)):
        #     axes.axhline(y=rows[i], color='tab:red', linewidth=0.5, linestyle='--')
        #     axes.text(1080, rows[i], str(i + 1), color='tab:red', va='center')
        # plt.tight_layout()

        if additional_info is not None:
            info2 = axes.text(0, 100, ' | '.join(additional_info),
                              bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5},
                              ha="left")

        for time in self.screen_frame_time_list:
            # plot slot touches
            for i in range(len(self.screen_data)):
                dataframe = self.screen_data[i].record.query('Time == @time')
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
                                                                          color_list=self._screen_color_list)
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
        if if_show is True:
            plt.show()
        if if_save is True:
            plt.savefig("%s.png" % file_name)
            plt.close(fig)

    """
    ##########################################
    All Animation 
    ##########################################
    """

    def createAllFramePlot(self, frame_index, plot_circle, show_cross_mark,
                           persistence):
        arts1 = self.createAD2FramePlotAnimation(frame_index)
        arts2 = self.createScreenFramePlotAnimation(frame_index, plot_circle, show_cross_mark,
                                                    persistence)
        return arts1 + arts2

    def compileAllAnimation(self, persistence=False, plot_circle=True, show_cross_mark=True, replay_interval_ms=1,
                            frame_resolution_ms=1, if_real_time=False):
        # todo: need to test the functionality
        self._ad2_frame_time_list_extend = self.screen_frame_time_list + self.ad2_frame_time_list
        self._ad2_frame_time_list_extend.sort()

        # calculate extended frame time list
        if if_real_time is True:
            start_time = self._ad2_frame_time_list_extend[0]
            stop_time = self._ad2_frame_time_list_extend[-1]
            self._ad2_frame_time_list_extend = np.arange(start_time, stop_time, frame_resolution_ms / 1e3).tolist()

        self._screen_frame_time_list_extend = self._ad2_frame_time_list_extend

        # calculate when to update the frame - ad2
        self._ad2_frame_update_index_list = []
        for i in range(len(self.ad2_frame_time_list)):
            time_real = self.ad2_frame_time_list[i]
            for j in range(len(self._ad2_frame_time_list_extend)):
                if len(self._ad2_frame_update_index_list) != 0:
                    if j < self._ad2_frame_update_index_list[-1]:
                        continue
                time_pre = self._ad2_frame_time_list_extend[j]
                if j == len(self._ad2_frame_time_list_extend) - 1:
                    if time_pre <= time_real:
                        self._ad2_frame_update_index_list.append(j)
                else:
                    time_post = self._ad2_frame_time_list_extend[j + 1]
                    if time_pre <= time_real < time_post:
                        self._ad2_frame_update_index_list.append(j)
                        break

        # calculate when to update the frame - screen
        self._screen_frame_update_index_list = []
        for i in range(len(self.screen_frame_time_list)):
            time_real = self.screen_frame_time_list[i]
            for j in range(len(self._screen_frame_time_list_extend)):
                if len(self._screen_frame_update_index_list) != 0:
                    if j < self._screen_frame_update_index_list[-1]:
                        continue
                time_pre = self._screen_frame_time_list_extend[j]
                if j == len(self._screen_frame_time_list_extend) - 1:
                    if time_pre <= time_real:
                        self._screen_frame_update_index_list.append(j)
                else:
                    time_post = self._screen_frame_time_list_extend[j + 1]
                    if time_pre <= time_real < time_post:
                        self._screen_frame_update_index_list.append(j)
                        break

        frame_info = 'Number of frames: All (AD2 %d, Screen %d) > (AD2 %d, Screen %d).' % (
            len(self._ad2_frame_time_list_extend),
            len(self._screen_frame_time_list_extend),
            len(self._ad2_frame_update_index_list),
            len(self._screen_frame_update_index_list))
        print(frame_info)

        # create a figure
        fig = plt.figure(constrained_layout=False)
        gs = GridSpec(6, 5, figure=fig)
        analog_ax1 = fig.add_subplot(gs[0:2, 0:3])
        analog_ax2 = fig.add_subplot(gs[2:4, 0:3])
        digital_ax0 = fig.add_subplot(gs[4:5, 0:3])
        digital_ax1 = fig.add_subplot(gs[5:, 0:3])
        screen_ax = fig.add_subplot(gs[:, 3:])
        self._ad2_axs = [analog_ax1, analog_ax2, digital_ax0, digital_ax1]
        digital_ax1.get_shared_x_axes().join(analog_ax1, analog_ax2, digital_ax0, digital_ax1)
        self._screen_axs = screen_ax
        self._screen_axs.set_xlim([0, 1080])
        self._screen_axs.set_ylim([1920, 0])
        self._screen_axs.set_aspect('equal')
        self._screen_axs.grid(color='darkgray', linestyle='--', linewidth=0.5)
        rows = np.linspace(0, 1920, 27)
        for i in range(len(rows)):
            self._screen_axs.axhline(y=rows[i], color='tab:red', linewidth=0.5, linestyle='--')
            self._screen_axs.text(1080, rows[i], str(i + 1), color='tab:red', va='center')
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.08, top=0.95, left=0.08, hspace=0.4)

        if replay_interval_ms <= 0:
            replay_interval_ms = round(1 / np.average(self.ad2_trigger_rate) * 1e3, 0)

        self._ani_all = animation.FuncAnimation(fig, self.createAllFramePlot,
                                                fargs=(plot_circle, show_cross_mark,
                                                       persistence), blit=True,
                                                interval=replay_interval_ms, repeat=True,
                                                frames=len(self._ad2_frame_time_list_extend))

        # plt.show()
