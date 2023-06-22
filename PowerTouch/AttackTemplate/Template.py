from PowerTouch.AnalogDiscovery.Device import AnalogDiscovery
from PowerTouch.AnalogDiscovery.Oscilloscope import Oscilloscope
from PowerTouch.AnalogDiscovery.LogicAnalyzer import LogicAnalyzer
from PowerTouch.AnalogDiscovery.PatternGenerator import PatternGenerator
from PowerTouch.AnalogDiscovery.PowerSupply import PowerSupply
from PowerTouch.AnalogDiscovery.WaveformGenerator import WaveformGenerator
from PowerTouch.MultiTouchMonitorADB.MultiTouchMonitor import MultiTouchMonitor
from PowerTouch.TouchMonitorFlutter.TouchMonitor import TouchMonitor
from PowerTouch.DataAnalyzer.DataAnalyzer import DataAnalyzer
from datetime import datetime
import matplotlib.pyplot as plt
import time
from statistics import mean
import numpy as np


class SmartPhoneTemplate(object):
    def __init__(self, if_enableAD2=True, if_enableSmartPhone=True, verbose=True):
        if if_enableAD2 is True:
            self.ad2 = AnalogDiscovery(verbose=verbose)
            self.scope = Oscilloscope(self.ad2)
            self.logic = LogicAnalyzer(self.ad2)
            self.pattern = PatternGenerator(self.ad2)
            self.power = PowerSupply(self.ad2)
            self.waveform = WaveformGenerator(self.ad2)
            self._auto_timeout = None
            self._position_ms = None
            self._fs = None
            self._if_fs_analog = None
        if if_enableSmartPhone is True:
            self.screen = MultiTouchMonitor()
        self.data_analyzer = DataAnalyzer()

    """
    ##########################################
    Power Supply
    ##########################################
    """

    def setupPowerSupply(self, voltage=5, verbose=False):
        self.power.getPowerTitle(verbose=verbose)
        self.power.setSupplyVoltage(voltage=voltage)

    def startPowerSupply(self):
        self.power.enablePowerSupply()

    def stopPowerSupply(self):
        self.power.disablePowerSupply()

    """
    ##########################################
    Oscilloscope
    ##########################################
    """

    def setupOscilloscope(self, fs=800e3, trigger_level_mv=30,
                          hysteresis_factor=0.8, holdoff_ms=0.0,
                          position_ms=4.2, verbose=False,
                          buffer_size=8192, if_RisingPositive=True,
                          trigger_channel=1, auto_timeout_s=1,
                          ch1_peak2peak=0.2, ch2_peak2peak=2):

        if self._position_ms is None:
            self._position_ms = position_ms

        if self._fs is not None:
            if self._if_fs_analog is True:
                self._fs = fs
            else:
                fs = self._fs * 2
        else:
            self._fs = fs
            self._if_fs_analog = True

        # print title
        self.scope.getScopeTitle(verbose=verbose)

        # set oscilloscope
        self.scope.setScopeSamplingFrequency(frequency=fs, verbose=verbose)
        self.scope.setScopeBufferSize(size=buffer_size, verbose=verbose)
        if self._auto_timeout is None:
            self._auto_timeout = auto_timeout_s
        self.scope.setScopeTriggerTimeout(timeout_s=self._auto_timeout, verbose=verbose)

        # set trigger
        self.scope.setScopeTriggerOnChannel(channel=trigger_channel, verbose=verbose)
        self.scope.setScopeTriggerEdge(if_RisingPositive=if_RisingPositive, verbose=verbose)
        self.scope.setScopeTriggerPosition(position_ms=self._position_ms, verbose=verbose)
        self.scope.setScopeTriggerLevel(level_mV=trigger_level_mv, verbose=verbose)
        self.scope.setScopeTriggerHysteresis(hyst_mV=trigger_level_mv * hysteresis_factor, verbose=verbose)
        self.scope.setScopeTriggerHoldOff(holdoff_ms=holdoff_ms, verbose=verbose)
        self.scope.setScopeTriggerFilter(verbose=verbose)

        # set channel
        self.scope.enableScopeChannel(channel_index=1, verbose=verbose)
        self.scope.setScopeChannelRange(peak2peak=ch1_peak2peak, verbose=verbose)
        self.scope.enableScopeChannel(channel_index=2, verbose=verbose)
        self.scope.setScopeChannelRange(peak2peak=ch2_peak2peak, verbose=verbose)

    def startOscilloscope(self):
        self.scope.setScopeState(if_reconfigure=True, if_start=True)

    def monitorOscilloscope(self, runtime=None):
        plt.ion()
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all')
        info = ax1.text(-.4, -60, "", bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")

        ad2_analog_ch1_line, = ax1.plot([], [], color='tab:blue')
        ax1.set_title('Oscilloscope CH1 (Smartphone Screen)')
        ax1.set_ylabel('Voltage(mV)')
        ax1.set_ylim([-70, 70])
        ax1.minorticks_on()
        ax1.grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
        ax1.grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
        ax1.axvline(x=0, color='tab:red', linestyle='--')

        ad2_analog_ch2_line, = ax2.plot([], [], color='tab:orange')
        ax2.set_title('Oscilloscope Ch2 (Waveform Generator)')
        ax2.set_ylabel('Voltage(V)')
        # ax2.set_ylim([-60, 60])
        ax2.minorticks_on()
        ax2.grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
        ax2.grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
        ax2.axvline(x=0, color='tab:red', linestyle='--')
        ax2.set_xlabel('Time(ms)')
        plt.tight_layout()

        # to calculate trigger rate
        start = datetime.now()
        elapsed = 0
        trigger_rate_average = 5
        trigger_time_list = []
        trigger_time_first = None
        trigger_count = 0
        trigger_rate = 0

        while True:
            now = datetime.now()
            if runtime is not None:
                if elapsed > runtime:
                    break
                elapsed = (now - start).total_seconds()

            state, trigger_flag = self.scope.getScopeState(verbose=False)
            if state == 'Done':
                # calculate trigger rate
                if trigger_time_first is None:
                    trigger_time_first = now
                else:
                    diff = (now - trigger_time_first).total_seconds()
                    trigger_time_first = now
                    if len(trigger_time_list) > trigger_rate_average:
                        trigger_time_list.pop(0)
                    trigger_time_list.append(diff)
                    trigger_rate = 1 / mean(trigger_time_list)

                # count trigger times
                trigger_count += 1

                # print info
                text = ["%.3fs" % ((now - start).total_seconds()),
                        trigger_flag, 'TR:%.1fsps' % trigger_rate, 'TC:%d' % trigger_count, str(now)]
                info.set_text(' | '.join(text))

                # read data
                ad2_analog_ch1_data = self.scope.readScopeChannelData(channel_index=1)
                ad2_analog_ch2_data = self.scope.readScopeChannelData(channel_index=2)
                ad2_analog_time = self.scope.readScopeChannelDataTime()

                ad2_analog_ch1_line.set_data(ad2_analog_time * 1000, ad2_analog_ch1_data * 1000)
                ad2_analog_ch2_line.set_data(ad2_analog_time * 1000, ad2_analog_ch2_data)
                ax2.ignore_existing_data_limits = True
                ax2.relim()
                ax2.autoscale_view()
                ax2.set_xlim([ad2_analog_time[0] * 1000, ad2_analog_time[-1] * 1000])
                fig.canvas.draw()
                fig.canvas.flush_events()
                # alternatively you could use
                # plt.pause(0.000000000001)

    """
    ##########################################
    Logic Analyzer
    ##########################################
    """

    def setupLogicAnalyzer(self, fs=400e3, if_analogin=False, edge_rise_channels=0, position_ms=4.2, verbose=False,
                           buffer_size=4096, auto_timeout_s=1, if_RisingPositive=True, ):

        if self._position_ms is None:
            self._position_ms = position_ms

        if self._fs is not None:
            if self._if_fs_analog is True:
                fs = self._fs / 2
            else:
                self._fs = fs
        else:
            self._fs = fs
            self._if_fs_analog = False

        # print title
        self.logic.getAnalyzerTitle(verbose=verbose)

        # set logic analyzer
        self.logic.setAnalyzerClockFrequency(frequency=fs, verbose=verbose)
        self.logic.setAnalyzerBufferSize(size=buffer_size, verbose=verbose)

        # set trigger
        if self._auto_timeout is None:
            self._auto_timeout = auto_timeout_s
        self.logic.setAnalyzerTriggerTimeout(timeout_s=self._auto_timeout, verbose=verbose)
        self.logic.setAnalyzerTriggerSource(if_analogin=if_analogin, if_RisingPositive=if_RisingPositive,
                                            edge_rise_channels=edge_rise_channels, verbose=verbose)

        self.logic.setAnalyzerTriggerPosition(position_ms=self._position_ms, verbose=verbose)
        self.logic.setAnalyzerDataFormat(verbose=verbose)

    def startLogicAnalyzer(self):
        self.logic.setAnalyzerState(if_reconfigure=True, if_start=True)

    def monitorLogicAnalyzer(self, channel_number=2, runtime=None):
        plt.ion()
        fig, axs = plt.subplots(channel_number, 1, sharex='all')
        ad2_digital_chs_lines = [None] * channel_number

        info = axs[0].text(-.4, 0.2, "", bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")
        for i in range(len(axs)):
            ad2_digital_chs_lines[i], = axs[i].plot([], [], color='tab:green')
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

        # to calculate trigger rate
        start = datetime.now()
        elapsed = 0
        trigger_rate_average = 5
        trigger_time_list = []
        trigger_time_first = None
        trigger_count = 0
        trigger_rate = 0
        state_previous = None
        now = None

        while True:
            if runtime is not None:
                if elapsed > runtime:
                    break
                elapsed = (datetime.now() - start).total_seconds()

            state, trigger_flag = self.logic.getAnalyzerState(verbose=False)
            if state_previous == 'Armed' and state == 'Running':
                now = datetime.now()
            state_previous = state

            if state == 'Done':
                # calculate trigger rate
                if trigger_time_first is None:
                    trigger_time_first = now
                else:
                    diff = (now - trigger_time_first).total_seconds()
                    trigger_time_first = now
                    if len(trigger_time_list) > trigger_rate_average:
                        trigger_time_list.pop(0)
                    trigger_time_list.append(diff)
                    trigger_rate = 1 / mean(trigger_time_list)

                # count trigger times
                trigger_count += 1

                # print info
                text = ["%.3fs" % ((now - start).total_seconds()),
                        trigger_flag, 'TR:%.1fsps' % trigger_rate, 'TC:%d' % trigger_count, str(now)]
                info.set_text(' | '.join(text))

                # read data
                ad2_digital_chs_data = self.logic.readAnalyzerData(channel_number=channel_number)
                ad2_digital_time = self.logic.readAnalyzerDataTime()

                for i in range(len(axs)):
                    ad2_digital_chs_lines[i].set_data(ad2_digital_time * 1000, ad2_digital_chs_data[i])
                    if i == channel_number - 1:
                        axs[i].set_xlim([ad2_digital_time[0] * 1000, ad2_digital_time[-1] * 1000])

                fig.canvas.draw()
                fig.canvas.flush_events()

    """
    ##########################################
    Waveform Generator
    ##########################################
    """

    def setupWaveformGeneratorBasic(self, if_analogin=True, if_RisingPositive=True, if_selftrigger=False, verbose=False,
                                    attack_width_us=200, attack_delay_us=1.3e3, peak2peak=2, if_above_0=True, offset=0,
                                    noise_frequency=290e3, function_name='Sine', channel_index=1,
                                    symmetry=50, phase=0, idle_mode=2):
        self.waveform.getWaveformTitle(verbose=verbose)
        self.waveform.setWaveformChannelTriggerSource(channel_index=channel_index,
                                                      if_analogin=if_analogin,
                                                      if_RisingPositive=if_RisingPositive,
                                                      if_selftrigger=if_selftrigger,
                                                      verbose=verbose)
        self.waveform.enableWaveformChannelCarrier(channel_index=channel_index)
        self.waveform.setWaveformChannelRunInfo(channel_index=channel_index,
                                                runtime_us=attack_width_us,
                                                delay_us=attack_delay_us,
                                                repeat_number=0,
                                                if_repeattrigger=True,
                                                verbose=verbose)
        self.waveform.setWaveformChannelCarrierWave(channel_index=channel_index,
                                                    func_name=function_name,
                                                    freq=noise_frequency,
                                                    peak2peak=peak2peak,
                                                    if_above_0=if_above_0,
                                                    offset=offset,
                                                    symmetry=symmetry,
                                                    phase=phase,
                                                    idle_mode=idle_mode,
                                                    # _DwfAnalogOutIdleDisable = c_int(0)
                                                    # _DwfAnalogOutIdleOffset = c_int(1)
                                                    # _DwfAnalogOutIdleInitial = c_int(2)
                                                    verbose=verbose)

    def setupWaveformGeneratorCustomModulation(self, if_analogin=True, if_RisingPositive=True, if_selftrigger=False,
                                               attack_width_list_us=None, attack_delay_list_us=None,
                                               peak2peak=2, if_above_0=True, offset=0,
                                               noise_frequency=290e3,
                                               idle_mode=0,
                                               channel_index=1,
                                               verbose=False):

        if attack_delay_list_us is None:
            attack_delay_list_us = [1.3e3, 6e3]
        if attack_width_list_us is None:
            attack_width_list_us = [200, 200]

        runtime = np.sum(attack_delay_list_us[1::]) + attack_width_list_us[-1]

        self.waveform.getWaveformTitle(verbose=verbose)

        # set trigger
        self.waveform.setWaveformChannelTriggerSource(channel_index=channel_index,
                                                      if_analogin=if_analogin,
                                                      if_RisingPositive=if_RisingPositive,
                                                      if_selftrigger=if_selftrigger,
                                                      verbose=verbose)
        self.waveform.setWaveformChannelRunInfo(channel_index=channel_index,
                                                runtime_us=runtime,
                                                delay_us=attack_delay_list_us[0],
                                                repeat_number=0,
                                                if_repeattrigger=True,
                                                verbose=verbose)

        # set signal
        self.waveform.setWaveformTemplateCustomPulseModulatedSine(channel_index=channel_index,
                                                                  sine_freq=noise_frequency,
                                                                  peak2peak=peak2peak,
                                                                  if_above_0=if_above_0,
                                                                  offset=offset,
                                                                  idle_mode=idle_mode,
                                                                  pulse_relative_delay_list_us=attack_delay_list_us,
                                                                  pulse_width_list_us=attack_width_list_us,
                                                                  verbose=verbose)

    def startWaveformGenerator(self, channel_index=1):
        self.waveform.runWaveformChannel(channel_index=channel_index, verbose=False)

    def stopWaveformGenerator(self, channel_index=1):
        self.waveform.stopWaveformChannel(channel_index=channel_index, verbose=False)

    """
    ##########################################
    Pattern Generator
    ##########################################
    """

    def setupPatternGeneratorBasic(self, if_analogin=False, if_RisingPositive=True, if_selftrigger=True, verbose=False,
                                   attack_width_us=200, relay_guard_us=500, relay_response_time_us=500,
                                   attack_delay_us=1.3e3, trigger_guard_us=100):

        self.pattern.getPatternTitle(verbose=verbose)
        self.pattern.resetParameter()
        self.pattern.setPatternTriggerSource(if_analogin=if_analogin, if_RisingPositive=if_RisingPositive,
                                             if_selftrigger=if_selftrigger, verbose=verbose)
        self.pattern.setPatternRepeat(repeat_number=0, if_repeattrigger=True, verbose=verbose)
        self.pattern.enablePatternChannel(channel_index=[0, 1], idle_state=-1, output_mode=0, verbose=verbose)

        if attack_delay_us - relay_guard_us - relay_response_time_us <= trigger_guard_us:  # for attacking 1st and 2nd row
            correct_offset = relay_guard_us + relay_response_time_us - (attack_delay_us - trigger_guard_us)
            relay_guard_us_offset = correct_offset * relay_guard_us / (relay_guard_us + relay_response_time_us)
            relay_response_time_us_offset = correct_offset * relay_response_time_us / (
                    relay_guard_us + relay_response_time_us)
            relay_guard_us = relay_guard_us - relay_guard_us_offset
            relay_response_time_us = relay_response_time_us - relay_response_time_us_offset
            print("[Attack delay cannot satisfy Relay/Trigger Guard and Relay Response Time.][Guard Fixed.] ")

        self.pattern.setPatternWaveformPulse(channel_index=0, pulse_state=0,
                                             pulse_width_us=attack_width_us + relay_guard_us * 2 + 2 * relay_response_time_us,
                                             delay_us=attack_delay_us - relay_guard_us - relay_response_time_us,
                                             clock_divider=100,
                                             verbose=False)
        self.pattern.setPatternWaveformPulse(channel_index=1, pulse_state=1,
                                             pulse_width_us=attack_width_us + 2 * relay_response_time_us,
                                             delay_us=attack_delay_us - relay_response_time_us,
                                             clock_divider=100,
                                             verbose=False)
        if verbose is True:
            self.pattern.getPatternWaveformPulse()

    def setupPatternGeneratorCustom(self, if_analogin=False, if_RisingPositive=True, if_selftrigger=True, verbose=False,
                                    attack_width_list_us=None, attack_delay_list_us=None,
                                    relay_guard_us=500, relay_response_time_us=500, trigger_guard_us=100):

        self.pattern.getPatternTitle(verbose=verbose)
        self.pattern.resetParameter()
        self.pattern.setPatternTriggerSource(if_analogin=if_analogin, if_RisingPositive=if_RisingPositive,
                                             if_selftrigger=if_selftrigger, verbose=verbose)
        self.pattern.setPatternRepeat(repeat_number=0, if_repeattrigger=True, verbose=verbose)
        self.pattern.enablePatternChannel(channel_index=[0, 1], idle_state=-1, output_mode=0, verbose=verbose)

        low_pulse_width_list_us, low_pulse_delay_list_us = self._generatePatternPulses(
            pulse_width_list=attack_width_list_us,
            pulse_delay_list=attack_delay_list_us,
            guard1=relay_guard_us,
            guard2=relay_response_time_us,
            trigger_guard=trigger_guard_us)
        high_pulse_width_list_us, high_pulse_delay_list_us = self._generatePatternPulses(
            pulse_width_list=attack_width_list_us,
            pulse_delay_list=attack_delay_list_us,
            guard1=0,
            guard2=relay_response_time_us,
            trigger_guard=trigger_guard_us)

        if len(low_pulse_width_list_us) == 1 and len(high_pulse_width_list_us) == 1:
            self.pattern.setPatternWaveformPulse(channel_index=0, pulse_state=0,
                                                 pulse_width_us=low_pulse_width_list_us[0],
                                                 delay_us=low_pulse_delay_list_us[0],
                                                 clock_divider=100,
                                                 verbose=verbose)
            self.pattern.setPatternWaveformPulse(channel_index=1, pulse_state=1,
                                                 pulse_width_us=high_pulse_width_list_us[0],
                                                 delay_us=high_pulse_delay_list_us[0],
                                                 clock_divider=100,
                                                 verbose=verbose)
        else:
            self.pattern.setPatternWaveformCustom(channel_index=0, pulse_state=0,
                                                  pulse_relative_delay_list_us=low_pulse_delay_list_us,
                                                  pulse_width_list_us=low_pulse_width_list_us,
                                                  verbose=verbose)
            self.pattern.setPatternWaveformCustom(channel_index=1, pulse_state=1,
                                                  pulse_relative_delay_list_us=high_pulse_delay_list_us,
                                                  pulse_width_list_us=high_pulse_width_list_us,
                                                  verbose=verbose)

    @staticmethod
    def _generatePatternPulses(pulse_width_list, pulse_delay_list, guard1=0, guard2=0, trigger_guard=100):
        pulse_delay_list = np.array(pulse_delay_list.copy())
        pulse_width_list = np.array(pulse_width_list.copy())
        attack_absolute_start_list_us = np.cumsum(pulse_delay_list)
        attack_absolute_end_list_us = attack_absolute_start_list_us + pulse_width_list

        # combine close pulses
        drop_end_list = []
        drop_start_list = []
        pulse_absolute_start_list_us = attack_absolute_start_list_us - guard1 - guard2
        pulse_absolute_end_list_us = attack_absolute_end_list_us + guard1 + guard2
        for i in range(len(pulse_absolute_end_list_us) - 1):
            if pulse_absolute_end_list_us[i] + trigger_guard >= pulse_absolute_start_list_us[i + 1]:
                drop_end_list.append(i)
                drop_start_list.append(i + 1)

        pulse_absolute_end_list_us_new = np.delete(pulse_absolute_end_list_us, drop_end_list)
        pulse_absolute_start_list_us_new = np.delete(pulse_absolute_start_list_us, drop_start_list)

        # for attacking 1st and 2nd row
        if pulse_absolute_start_list_us_new[0] <= trigger_guard:
            pulse_absolute_start_list_us_new[0] = trigger_guard
            print("[Attack delay cannot satisfy Relay/Trigger Guard and Relay Response Time.][Guard Fixed.] ")

        pulse_width_list_new = (pulse_absolute_end_list_us_new - pulse_absolute_start_list_us_new)
        pulse_delay_list_new = np.diff(np.insert(pulse_absolute_start_list_us_new, 0, 0))

        if len(pulse_delay_list_new) != len(pulse_width_list_new):
            raise ValueError

        return pulse_width_list_new, pulse_delay_list_new

    def startPatternGenerator(self, verbose=False):
        self.pattern.runPatternGenerator(verbose=verbose)

    def stopPatternGenerator(self, verbose=False):
        self.pattern.stopPatternGenerator(verbose=verbose)

    """
    ##########################################
    AD2 Overall
    ##########################################
    """

    def monitorAD2_byRunTime(self, runtime=None):
        plt.ion()
        fig, (ax1, ax2, dx1, dx2) = plt.subplots(2 + 2, 1, sharex='all',
                                                 figsize=(12, 7),
                                                 gridspec_kw={'height_ratios': [3, 2, 1, 1]})

        info = ax1.text(-.4, -60, "", bbox={'facecolor': 'tab:olive', 'alpha': 0.5, 'pad': 5}, ha="left")

        ad2_analog_ch1_line, = ax1.plot([], [], color='tab:blue')
        ax1.set_title('Oscilloscope CH1 (Smartphone Screen)')
        ax1.set_ylabel('Voltage(mV)')
        ax1.set_ylim([-70, 70])
        ax1.minorticks_on()
        ax1.grid(b=True, which='major', color='gray', linestyle='--', linewidth=0.5)
        ax1.grid(b=True, which='minor', color='darkgrey', linestyle='--', linewidth=0.4)
        ax1.axvline(x=0, color='tab:red', linestyle='--')

        ad2_analog_ch2_line, = ax2.plot([], [], color='tab:orange')
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
            ad2_digital_chs_lines[i], = axs[i].plot([], [], color='tab:green')
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

        # to calculate trigger rate
        start = datetime.now()
        elapsed = 0
        trigger_rate_average = 5
        trigger_time_list = []
        trigger_time_first = None
        trigger_count = 0
        trigger_rate = 0
        state_previous = None
        now = None

        while True:
            if runtime is not None:
                if elapsed > runtime:
                    break
                elapsed = (datetime.now() - start).total_seconds()

            state, trigger_flag = self.scope.getScopeState(verbose=False)
            if state_previous == 'Armed' and state == 'Running':
                now = datetime.now()
            state_previous = state

            _, _ = self.logic.getAnalyzerState(verbose=False, if_will_read_data=True)

            # print(state)
            if state == 'Done':
                if trigger_flag == 'AutoTriggering':
                    now = datetime.now()
                # calculate trigger rate
                if trigger_time_first is None:
                    trigger_time_first = now
                else:
                    diff = (now - trigger_time_first).total_seconds()
                    trigger_time_first = now
                    if len(trigger_time_list) > trigger_rate_average:
                        trigger_time_list.pop(0)
                    trigger_time_list.append(diff)
                    trigger_rate = 1 / mean(trigger_time_list)

                # count trigger times
                trigger_count += 1

                # print info
                text = ["%.3fs" % ((now - start).total_seconds()),
                        trigger_flag, 'TR:%.1fsps' % trigger_rate, 'TC:%d' % trigger_count, str(now)]
                info.set_text(' | '.join(text))

                # read data
                ad2_analog_ch1_data = self.scope.readScopeChannelData(channel_index=1)
                ad2_analog_ch2_data = self.scope.readScopeChannelData(channel_index=2)
                ad2_analog_time = self.scope.readScopeChannelDataTime()
                ad2_digital_chs_data = self.logic.readAnalyzerData(channel_number=channel_number)
                ad2_digital_time = self.logic.readAnalyzerDataTime()

                ad2_analog_ch1_line.set_data(ad2_analog_time * 1000, ad2_analog_ch1_data * 1000)
                ad2_analog_ch2_line.set_data(ad2_analog_time * 1000, ad2_analog_ch2_data)
                ax2.ignore_existing_data_limits = True
                ax2.relim()
                ax2.autoscale_view()
                # ax2.set_xlim([ad2_analog_time[0] * 1000, ad2_analog_time[-1] * 1000])

                for i in range(len(axs)):
                    ad2_digital_chs_lines[i].set_data(ad2_digital_time * 1000, ad2_digital_chs_data[i])
                    # if i == channel_number - 1:
                    #     axs[i].set_xlim([ad2_digital_time[0] * 1000, ad2_digital_time[-1]* 1000])

                fig.canvas.draw()
                fig.canvas.flush_events()
                # alternatively you could use
                # plt.pause(0.000000000001)

    def monitorAD2_saveData_byRunTime(self, verbose=False, runtime=None):
        start = time.time()
        elapsed = 0
        trigger_rate_average = 5
        trigger_time_list = []
        trigger_time_first = None
        trigger_count = 0
        trigger_rate = 0
        state_previous = None
        now = None

        while True:
            if runtime is not None:
                if elapsed > runtime:
                    break
                elapsed = time.time() - start
            state, trigger_flag = self.scope.getScopeState(verbose=False, if_will_read_data=True)

            if state_previous == 'Armed' and state == 'Running':
                now = datetime.now()
            state_previous = state
            _, _ = self.logic.getAnalyzerState(verbose=False, if_will_read_data=True)
            if state == 'Done':
                # calculate trigger rate
                if trigger_flag == 'AutoTriggering':
                    now = datetime.now()
                if now is None:
                    continue
                if trigger_time_first is None:
                    trigger_time_first = now
                else:
                    diff = (now - trigger_time_first).total_seconds()
                    trigger_time_first = now
                    if len(trigger_time_list) > trigger_rate_average:
                        trigger_time_list.pop(0)
                    trigger_time_list.append(diff)
                    try:
                        trigger_rate = 1 / mean(trigger_time_list)
                    except ZeroDivisionError:
                        trigger_rate = 0

                # count trigger times
                trigger_count += 1

                if verbose is True:
                    print(trigger_flag + ', TR:%.1f' % trigger_rate + ', TC:%d' % trigger_count + ', ' + str(now))

                self.data_analyzer.addAnalogDiscoveryDataFrame(timestamp=now,
                                                               analog_ch1=self.scope.readScopeChannelData(
                                                                   channel_index=1),
                                                               analog_ch2=self.scope.readScopeChannelData(
                                                                   channel_index=2),
                                                               analog_time=self.scope.readScopeChannelDataTime(),
                                                               digital_channels=self.logic.readAnalyzerData(
                                                                   channel_number=2),
                                                               digital_time=self.logic.readAnalyzerDataTime(),
                                                               trigger_flag=trigger_flag,
                                                               trigger_count=trigger_count,
                                                               trigger_rate=trigger_rate)
        return trigger_rate, trigger_flag

    def monitorAD2_saveData_byTriggerCount(self, verbose=False, trigger_count_max=None):
        trigger_rate_average = 5
        trigger_time_list = []
        trigger_time_first = None
        trigger_count = 0
        trigger_rate = 0
        state_previous = None
        now = None

        while True:
            if trigger_count_max is not None:
                if trigger_count >= trigger_count_max:
                    break
            state, trigger_flag = self.scope.getScopeState(verbose=False, if_will_read_data=True)

            if state_previous == 'Armed' and state == 'Running':
                now = datetime.now()

            state_previous = state
            _, _ = self.logic.getAnalyzerState(verbose=False, if_will_read_data=True)
            if state == 'Done':
                # calculate trigger rate
                if trigger_flag == 'AutoTriggering':
                    now = datetime.now()
                if now is None:
                    continue
                if trigger_time_first is None:
                    trigger_time_first = now
                else:
                    diff = (now - trigger_time_first).total_seconds()
                    trigger_time_first = now
                    if len(trigger_time_list) > trigger_rate_average:
                        trigger_time_list.pop(0)
                    trigger_time_list.append(diff)
                    try:
                        trigger_rate = 1 / mean(trigger_time_list)
                    except ZeroDivisionError:
                        trigger_rate = 0

                # count trigger times
                trigger_count += 1

                if verbose is True:
                    print(trigger_flag + ', TR:%.1f' % trigger_rate + ', TC:%d' % trigger_count + ', ' + str(now))

                self.data_analyzer.addAnalogDiscoveryDataFrame(timestamp=now,
                                                               analog_ch1=self.scope.readScopeChannelData(
                                                                   channel_index=1),
                                                               analog_ch2=self.scope.readScopeChannelData(
                                                                   channel_index=2),
                                                               analog_time=self.scope.readScopeChannelDataTime(),
                                                               digital_channels=self.logic.readAnalyzerData(
                                                                   channel_number=2),
                                                               digital_time=self.logic.readAnalyzerDataTime(),
                                                               trigger_flag=trigger_flag,
                                                               trigger_count=trigger_count,
                                                               trigger_rate=trigger_rate)
        return trigger_rate, trigger_flag

    def monitorAD2_compileAnimation(self, if_real_time=False, replay_interval_ms=0):
        self.data_analyzer.compileAD2Animation(if_real_time=if_real_time, replay_interval_ms=replay_interval_ms)

    def monitorAD2_write2CSV(self, save_path='./', index=None, if_write_original_file=True):
        if if_write_original_file is True:
            self.data_analyzer.writeAnalogDiscoveryDataFrameSeries(save_path=save_path)
        self.data_analyzer.writeAnalogDiscoveryTimeStamps(save_path=save_path, index=index)

    def setupAttackSinglePulse(self,
                               scope_trigger_level_mv=30,
                               sampling_frequency=800e3,
                               scope_trigger_holdoff_ms=0.0,
                               verbose=True,
                               scope_position_ms=4.7,
                               attack_width_us=200,
                               relay_guard_us=500,
                               relay_response_time=500,
                               attack_delay_us=1.3e3,
                               noise_peak2peak=5,
                               noise_frequency=290e3,
                               hysteresis_factor=0.8,
                               if_above_0=True,
                               noise_channel=1,
                               offset=0,
                               if_RisingPositive=True):
        # all together
        self.setupPowerSupply(voltage=5, verbose=verbose)
        self.startPowerSupply()

        self.setupOscilloscope(fs=sampling_frequency,
                               trigger_level_mv=scope_trigger_level_mv,
                               holdoff_ms=scope_trigger_holdoff_ms,
                               position_ms=scope_position_ms,
                               hysteresis_factor=hysteresis_factor,
                               verbose=verbose)
        self.setupLogicAnalyzer(fs=sampling_frequency / 2,
                                if_analogin=True,
                                edge_rise_channels=0,
                                position_ms=scope_position_ms,
                                verbose=verbose)
        self.setupPatternGeneratorBasic(if_analogin=True,
                                        if_RisingPositive=if_RisingPositive,
                                        if_selftrigger=False,
                                        verbose=verbose,
                                        attack_width_us=attack_width_us,
                                        relay_guard_us=relay_guard_us,
                                        relay_response_time_us=relay_response_time,
                                        attack_delay_us=attack_delay_us)

        self.setupWaveformGeneratorBasic(if_analogin=True,
                                         if_RisingPositive=if_RisingPositive,
                                         if_selftrigger=False,
                                         verbose=verbose,
                                         attack_width_us=attack_width_us,
                                         attack_delay_us=attack_delay_us,
                                         peak2peak=noise_peak2peak,
                                         if_above_0=if_above_0,
                                         offset=offset,
                                         noise_frequency=noise_frequency, channel_index=noise_channel)

    def setupAttackArbitraryPulses(self,
                                   scope_trigger_level_mv=30,
                                   sampling_frequency=800e3,
                                   scope_trigger_holdoff_ms=0.0,
                                   verbose=True,
                                   scope_position_ms=4.7,
                                   attack_width_list_us=None,
                                   attack_delay_list_us=None,
                                   relay_guard_us=500,
                                   relay_response_time=500,
                                   noise_peak2peak=5,
                                   noise_frequency=290e3,
                                   hysteresis_factor=0.8,
                                   channel_index=1,
                                   if_above_0=True,
                                   offset=0,
                                   if_RisingPositive=True):
        self.setupPowerSupply(voltage=5, verbose=verbose)
        self.startPowerSupply()

        self.setupOscilloscope(fs=sampling_frequency,
                               trigger_level_mv=scope_trigger_level_mv,
                               holdoff_ms=scope_trigger_holdoff_ms,
                               position_ms=scope_position_ms,
                               hysteresis_factor=hysteresis_factor,
                               verbose=verbose)
        self.setupLogicAnalyzer(fs=sampling_frequency / 2,
                                if_analogin=True,
                                edge_rise_channels=0,
                                position_ms=scope_position_ms,
                                verbose=verbose)
        self.setupWaveformGeneratorCustomModulation(if_analogin=True, if_RisingPositive=if_RisingPositive,
                                                    if_selftrigger=False,
                                                    attack_width_list_us=attack_width_list_us,
                                                    attack_delay_list_us=attack_delay_list_us,
                                                    peak2peak=noise_peak2peak, if_above_0=if_above_0, offset=offset,
                                                    noise_frequency=noise_frequency,
                                                    idle_mode=0,
                                                    channel_index=channel_index,
                                                    verbose=verbose)
        self.setupPatternGeneratorCustom(if_analogin=True, if_RisingPositive=if_RisingPositive, if_selftrigger=False,
                                         verbose=verbose,
                                         attack_width_list_us=attack_width_list_us,
                                         attack_delay_list_us=attack_delay_list_us,
                                         relay_guard_us=relay_guard_us,
                                         relay_response_time_us=relay_response_time)

    """
    ##########################################
    Screen
    ##########################################
    """

    def chargePhoneIfNeeded(self, low_threshold=5, high_threshold=98, charging_control_channel=[2, 3]):
        print("\nChecking if need to charge phone:")
        level, charging_flag = self.screen.readPhoneBattery(verbose=True)
        if level <= low_threshold:
            print('Battery [lower] than threshold [%.1f%%].' % low_threshold)
            print('[Start Charging...]')
            self.setupPowerSupply(voltage=5)
            self.startPowerSupply()
            self.pattern.setPatternConstantHigh(channel_index=charging_control_channel, verbose=True)
            time.sleep(5)
            while level < high_threshold:
                level, charging_flag = self.screen.readPhoneBattery(verbose=False)
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(current_time, '[%.1f%%]' % level, '(Target: [%.1f%%])' % high_threshold)
                if charging_flag is False:
                    raise ValueError('The phone cannot be charged.')
                time.sleep(60)
            print('[Finish Charging.]')
            self.pattern.resetPatternConstant(verbose=False)
            self.stopPowerSupply()
            self.screen.readPhoneBattery(verbose=True)
            print('Resuming Program...\n\n')
        else:
            print('Battery [higher] than threshold [%.1f%%]. [No need to charge.]' % low_threshold)
        self.ad2.closeDevice()

    def startChargingPhone(self, charging_control_channel=[2, 3]):

        print('[Start Charging...]')
        # self.ad2.initiateDevice(verbose=False)
        self.setupPowerSupply(voltage=5)
        self.pattern.resetPatternConstant(verbose=False)
        self.pattern.setPatternConstantHigh(channel_index=charging_control_channel, verbose=True)
        self.startPowerSupply()

    def stopChargingPhone(self):
        print('[Stop Charging.]')
        self.pattern.resetPatternConstant(verbose=True)
        self.stopPowerSupply()
        # self.screen.readPhoneBattery(verbose=True)
        self.ad2.closeDevice()

    def startScreen(self, verbose=True, file_index=0, align_timing=True, if_shell_communication=True):
        self.screen.checkPhoneConnection(verbose=verbose)
        self.screen.readPhoneBattery(verbose=verbose)
        if align_timing:
            self.screen.alignPhoneTiming(verbose=verbose)
        self.screen.initiatePhoneCommunication(verbose=verbose, file_index=file_index,
                                               if_shell_communication=if_shell_communication)

    def stopScreen(self, adb_server_pid=0):
        self.screen.terminatePhoneCommunication(adb_server_pid=adb_server_pid)

    def monitorScreen(self, time_delay=1, persistence=False, plot_circle=True, show_cross_mark=True):
        self.screen.plotMultiTouch(time_delay=time_delay, persistence=persistence, plot_circle=plot_circle,
                                   show_cross_mark=show_cross_mark)

    def monitorScreen_readFromEventFile(self, event_file_path='../events.txt', verbose=False,
                                        copy_path=None, save_raw_csv=None, save_processed_csv=None):
        self.screen.parseEventFile(event_file_path=event_file_path, verbose=verbose, event_file_copy_to=copy_path,
                                   save_raw_csv=save_raw_csv,
                                   save_processed_csv=save_processed_csv)
        self.data_analyzer.addTouchScreenDataFrame(self.screen.slots, self.screen.timestamps)

    def monitorScreen_write2CSV(self, save_path='./', if_statistics=True):
        self.screen.writeMultiTouchRecord2CSV(save_path=save_path)
        if if_statistics is True:
            self.screen.compileMultiTouchStatistics()
            self.screen.writeMultiTouchStatistics2CSV(save_path=save_path)

    def monitorScreen_compileAnimation(self, persistence=False, plot_circle=True, show_cross_mark=True,
                                       replay_interval_ms=1,
                                       frame_resolution_ms=1, if_real_time=False, repeat=True):
        self.data_analyzer.compileScreenAnimation(persistence=persistence, plot_circle=plot_circle,
                                                  show_cross_mark=show_cross_mark,
                                                  replay_interval_ms=replay_interval_ms,
                                                  frame_resolution_ms=frame_resolution_ms,
                                                  if_real_time=if_real_time, repeat=repeat)

    """
    ##########################################
    All Together
    ##########################################
    """

    def stopAll(self, adb_server_pid=0, if_close_device=True, awg_channel=2):
        self.stopWaveformGenerator(channel_index=awg_channel)
        self.stopPatternGenerator()
        self.stopPowerSupply()
        if if_close_device is True:
            self.ad2.closeDevice()
        time.sleep(1)
        self.stopScreen(adb_server_pid=adb_server_pid)

    def runAll(self, verbose=True, file_index=1, noise_channel=1, align_timing=True, if_shell_communication=False):
        self.startPowerSupply()
        self.startScreen(verbose=verbose, file_index=file_index, align_timing=align_timing,
                         if_shell_communication=if_shell_communication)
        time.sleep(1)
        self.startPatternGenerator()
        time.sleep(1)
        self.startOscilloscope()
        time.sleep(0.1)
        self.startLogicAnalyzer()
        self.startWaveformGenerator(channel_index=noise_channel)
