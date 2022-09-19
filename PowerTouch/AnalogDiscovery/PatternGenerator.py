from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants
from ctypes import c_double, byref, c_int, c_ubyte, c_uint, c_uint16, c_uint32
import numpy as np


class PatternGenerator(DwfConstants):
    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.dwf.FDwfDigitalOutReset(self.hdwf)
        self.run_time = None
        self.wait_time_floor = None

    def resetParameter(self):
        self.run_time = None
        self.wait_time_floor = None

    def getPatternTitle(self, verbose=False):
        if verbose is True:
            print('')
            print('=' * 100)
            print('Pattern Generator')
            print('=' * 100)

    def setPatternTriggerSource(self, if_analogin=False, if_selftrigger=True, if_RisingPositive=True, verbose=False):
        """
        TRIGSRC                     BYTE    Trigger Source Function
        trigsrcNone                 0       The trigger pin is high impedance, input. This is the default setting.
        trigsrcPC                   1       Trigger from PC, this can be used to synchronously start multiple instruments.
        trigsrcDetectorAnalogIn     2       Trigger detector on analog in channels.
        trigsrcDetectorDigitalIn    3       Trigger on digital input channels.
        trigsrcAnalogIn             4       Trigger on device instruments, these output high when running.
        trigsrcDigitalIn            5       Trigger on device instruments, these output high when running.
        trigsrcDigitalOut           6       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut1           7       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut2           8       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut3           9       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut4           10      Trigger on device instruments, these output high when running.
        trigsrcExternal1            11      External trigger signal.
        trigsrcExternal2            12      External trigger signal.
        trigsrcExternal3            13      External trigger signal.
        trigsrcExternal4            14      External trigger signal.
        """
        if if_selftrigger is True:
            self.dwf.FDwfDigitalOutTriggerSourceSet(self.hdwf, self._trigsrcNone)
        elif if_analogin is True:
            self.dwf.FDwfDigitalOutTriggerSourceSet(self.hdwf, self._trigsrcDetectorAnalogIn)
            if if_RisingPositive is True:
                self.dwf.FDwfDigitalOutTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeRise)
            else:
                self.dwf.FDwfDigitalOutTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeFall)
        elif if_analogin is False:
            self.dwf.FDwfDigitalOutTriggerSourceSet(self.hdwf, self._trigsrcDetectorDigitalIn)
            if if_RisingPositive is True:
                self.dwf.FDwfDigitalOutTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeRise)
            else:
                self.dwf.FDwfDigitalOutTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeFall)

        if verbose is True:
            self.getPatternTriggerSource()

    def getPatternTriggerSource(self):
        """
        TRIGSRC                     BYTE    Trigger Source Function
        trigsrcNone                 0       The trigger pin is high impedance, input. This is the default setting.
        trigsrcPC                   1       Trigger from PC, this can be used to synchronously start multiple instruments.
        trigsrcDetectorAnalogIn     2       Trigger detector on analog in channels.
        trigsrcDetectorDigitalIn    3       Trigger on digital input channels.
        trigsrcAnalogIn             4       Trigger on device instruments, these output high when running.
        trigsrcDigitalIn            5       Trigger on device instruments, these output high when running.
        trigsrcDigitalOut           6       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut1           7       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut2           8       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut3           9       Trigger on device instruments, these output high when running.
        trigsrcAnalogOut4           10      Trigger on device instruments, these output high when running.
        trigsrcExternal1            11      External trigger signal.
        trigsrcExternal2            12      External trigger signal.
        trigsrcExternal3            13      External trigger signal.
        trigsrcExternal4            14      External trigger signal.
        """
        triggersoucre_read = c_ubyte()

        self.dwf.FDwfDigitalOutTriggerSourceGet(self.hdwf, byref(triggersoucre_read))
        if triggersoucre_read.value == self._trigsrcDetectorAnalogIn.value:
            triggercondition_read = c_int()
            self.dwf.FDwfDigitalOutTriggerSlopeGet(self.hdwf, byref(triggercondition_read))
            if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
                condition = "Rising Edge"
            elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
                condition = "Falling Edge"
            else:
                condition = "Either Edge"
            print("Trigger on: [Analog Detector (%s)]." % condition)
        elif triggersoucre_read.value == self._trigsrcDetectorDigitalIn.value:
            triggercondition_read = c_int()
            self.dwf.FDwfDigitalOutTriggerSlopeGet(self.hdwf, byref(triggercondition_read))
            if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
                condition = "Rising Edge"
            elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
                condition = "Falling Edge"
            else:
                condition = "Either Edge"
            print("Trigger on: [Digital Detector (%s)]." % condition)
        elif triggersoucre_read.value == self._trigsrcNone.value:
            print("Trigger on: [None].")
        else:
            print("Trigger on: [Unknown].")

    def setPatternRepeat(self, repeat_number=0, if_repeattrigger=True, verbose=False):
        self.dwf.FDwfDigitalOutRepeatSet(self.hdwf, c_uint(repeat_number))

        # set if can be triggered during the repeat
        if if_repeattrigger is True:
            self.dwf.FDwfDigitalOutRepeatTriggerSet(self.hdwf, self._true)
        else:
            self.dwf.FDwfDigitalOutRepeatTriggerSet(self.hdwf, self._false)

        if verbose is True:
            self.getPatternRepeat()

    def getPatternRepeat(self):
        repeat_read = c_uint16()
        repeat_max = c_uint()
        repeat_min = c_uint()
        repeattrigger_read = c_int()

        self.dwf.FDwfDigitalOutRepeatGet(self.hdwf, byref(repeat_read))
        self.dwf.FDwfDigitalOutRepeatInfo(self.hdwf, byref(repeat_min), byref(repeat_max))
        self.dwf.FDwfDigitalOutRepeatTriggerGet(self.hdwf, byref(repeattrigger_read))
        if repeattrigger_read.value == self._true.value:
            print('Repeat Trigger: [Enabled].')
        elif repeattrigger_read.value == self._false.value:
            print('Repeat Trigger: [Disabled].')
        else:
            print('Repeat Trigger: [Unknown].')

        if repeat_read.value == 0:
            print("Repeat Number: [Infinite repeats].")
        else:
            # print("Repeat Number: %d in [%d, %d]; " % (
            #     repeat_read.value, repeat_min.value, repeat_max.value) + state + '.')
            print("Repeat Number: [%d]." % repeat_read.value)

    def enablePatternChannel(self, channel_index=-1, idle_state=0, output_mode=0, verbose=False):

        if isinstance(channel_index, list) is False:
            if channel_index == -1:
                bits = range(0, 16)
            else:
                bits = [channel_index]
        else:
            bits = channel_index

        if idle_state == -1:
            idle_state_set = self._DwfDigitalOutIdleInit
        elif idle_state == 0:
            idle_state_set = self._DwfDigitalOutIdleLow
        elif idle_state == 1:
            idle_state_set = self._DwfDigitalOutIdleHigh
        else:
            idle_state_set = self._DwfDigitalOutIdleZet

        if output_mode == 0:
            output_mode_set = self._DwfDigitalOutOutputPushPull
        elif output_mode == 1:
            output_mode_set = self._DwfDigitalOutOutputOpenDrain
        elif output_mode == 2:
            output_mode_set = self._DwfDigitalOutOutputOpenSource
        elif output_mode == 3:
            output_mode_set = self._DwfDigitalOutOutputThreeState
        else:
            output_mode_set = self._DwfDigitalOutOutputPushPull

        for channel in bits:
            self.dwf.FDwfDigitalOutEnableSet(self.hdwf, c_int(channel), self._true)
            self.dwf.FDwfDigitalOutOutputSet(self.hdwf, c_int(channel), output_mode_set)
            self.dwf.FDwfDigitalOutIdleSet(self.hdwf, c_int(channel), idle_state_set)

            if verbose is True:
                self.getPatternChannelEnableInfo(channel=channel)

    def getPatternChannelEnableInfo(self, channel=-1):
        if channel == -1:
            number_of_channels = c_int()
            self.dwf.FDwfDigitalOutCount(self.hdwf, byref(number_of_channels))
            channel_list = range(number_of_channels.value)
        else:
            channel_list = [channel]

        for i in channel_list:
            enable_state_read = c_int()
            self.dwf.FDwfDigitalOutEnableGet(self.hdwf, c_int(i), byref(enable_state_read))
            if enable_state_read.value == self._true.value:
                # enable_state = 'Enabled'

                output_mode_read = c_int()
                self.dwf.FDwfDigitalOutOutputGet(self.hdwf, c_int(i), byref(output_mode_read))
                if output_mode_read.value == self._DwfDigitalOutOutputPushPull.value:
                    output_mode = 'Push Pull (0)'
                elif output_mode_read.value == self._DwfDigitalOutOutputOpenDrain.value:
                    output_mode = 'Open Drain (1)'
                elif output_mode_read.value == self._DwfDigitalOutOutputOpenSource.value:
                    output_mode = 'Open Source (2)'
                elif output_mode_read.value == self._DwfDigitalOutOutputThreeState.value:
                    output_mode = 'Three State (3)'
                else:
                    output_mode = 'Unknown'

                idle_value_read = c_int()
                self.dwf.FDwfDigitalOutIdleGet(self.hdwf, c_int(i), byref(idle_value_read))
                if idle_value_read.value == self._DwfDigitalOutIdleInit.value:
                    idle_value = 'Init (-1)'
                elif idle_value_read.value == self._DwfDigitalOutIdleLow.value:
                    idle_value = 'Low (0)'
                elif idle_value_read.value == self._DwfDigitalOutIdleHigh.value:
                    idle_value = 'High (1)'
                elif idle_value_read.value == self._DwfDigitalOutIdleZet.value:
                    idle_value = 'Z (2)'
                else:
                    idle_value = 'Unknown'

                print('Channel %d: [Enabled].' % i)
                print('\tOutput Type: [' + output_mode + '].')
                print('\tIdle Output: [' + idle_value + '].')
            else:
                print('Channel %d: [Disabled].' % i)

    def setPatternWaveformPulse(self, channel_index=-1, pulse_state=1, pulse_width_us=100,
                                delay_us=100, clock_divider=100, verbose=False):

        if isinstance(channel_index, list) is False:
            if channel_index == -1:
                bits = range(0, 16)
            else:
                bits = [channel_index]
        else:
            bits = channel_index

        for channel in bits:
            # output type
            self.dwf.FDwfDigitalOutTypeSet(self.hdwf, c_int(channel), self._DwfDigitalOutTypePulse)

            # divider
            self.dwf.FDwfDigitalOutDividerInitSet(self.hdwf, c_int(channel), c_uint(0))
            self.dwf.FDwfDigitalOutDividerSet(self.hdwf, c_int(channel), c_uint(clock_divider))
            divider_read = c_uint()
            self.dwf.FDwfDigitalOutDividerGet(self.hdwf, c_int(channel), byref(divider_read))
            divider_read = divider_read.value
            internal_frequency = c_double()
            self.dwf.FDwfDigitalOutInternalClockInfo(self.hdwf, byref(internal_frequency))
            internal_frequency = internal_frequency.value
            time_resolution = 1 / (internal_frequency / divider_read)

            # wait
            wait_resolution_us = 50
            wait_floor = round(delay_us // wait_resolution_us, 0)
            wait_modular = round(delay_us % wait_resolution_us, 0)
            if wait_modular == 0:
                wait_floor = wait_floor - 1

            if self.wait_time_floor is None:
                self.wait_time_floor = wait_floor
            elif wait_floor >= self.wait_time_floor:
                pass
            else:
                raise Warning('Current wait_time_floor is smaller than previous one. Put it before previous one.')

            if self.wait_time_floor == 0:
                # self.dwf.FDwfDigitalOutWaitSet(self.hdwf, c_double(0))
                pass
            else:
                self.dwf.FDwfDigitalOutWaitSet(self.hdwf, c_double(self.wait_time_floor * wait_resolution_us / 1e6))
            delay_us_remaining = delay_us - self.wait_time_floor * wait_resolution_us

            # pulse initial
            if pulse_state == 1:
                self.dwf.FDwfDigitalOutCounterInitSet(self.hdwf, c_int(channel), self._false, c_uint(0))
            elif pulse_state == 0:
                self.dwf.FDwfDigitalOutCounterInitSet(self.hdwf, c_int(channel), self._true, c_uint(0))

            # pulse width and remaining delay
            delay_count = int(delay_us_remaining / 1e6 / time_resolution)
            pulse_width_count = int(pulse_width_us / 1e6 / time_resolution)

            counter_min = c_uint()
            counter_max = c_uint()
            self.dwf.FDwfDigitalOutCounterInfo(self.hdwf, c_int(channel), byref(counter_min), byref(counter_max))
            if delay_count > counter_max.value or pulse_width_count > counter_max.value:
                raise ValueError('Pattern generator channel %d exceed maximum value.' % channel)

            if pulse_state == 1:
                self.dwf.FDwfDigitalOutCounterSet(self.hdwf, c_int(channel), c_uint(delay_count),
                                                  c_uint(pulse_width_count))
            elif pulse_state == 0:
                self.dwf.FDwfDigitalOutCounterSet(self.hdwf, c_int(channel), c_uint(pulse_width_count),
                                                  c_uint(delay_count))

            # run time
            if self.run_time is None:
                self.run_time = pulse_width_us / 1e6 + delay_us_remaining / 1e6
            else:
                run_time = pulse_width_us / 1e6 + delay_us_remaining / 1e6
                if run_time > self.run_time:
                    self.run_time = run_time
            self.dwf.FDwfDigitalOutRunSet(self.hdwf, c_double(self.run_time))

            if verbose is True:
                self.getPatternWaveformPulse(channel=channel)

    def getPatternWaveformPulse(self, channel=-1):
        internal_frequency = c_double()
        self.dwf.FDwfDigitalOutInternalClockInfo(self.hdwf, byref(internal_frequency))
        internal_frequency = internal_frequency.value

        run_time = c_double()
        self.dwf.FDwfDigitalOutRunGet(self.hdwf, byref(run_time))
        run_time = run_time.value

        wait_time = c_double()
        self.dwf.FDwfDigitalOutWaitGet(self.hdwf, byref(wait_time))
        wait_time = wait_time.value

        if channel == -1:
            number_of_channels = c_int()
            self.dwf.FDwfDigitalOutCount(self.hdwf, byref(number_of_channels))
            channel_list = range(number_of_channels.value)
        else:
            channel_list = [channel]

        for i in channel_list:

            enable_state_read = c_int()
            self.dwf.FDwfDigitalOutEnableGet(self.hdwf, c_int(i), byref(enable_state_read))

            if enable_state_read.value == self._true.value:
                print('-' * 50)
                divider_init = c_uint()
                self.dwf.FDwfDigitalOutDividerInitGet(self.hdwf, c_int(i), byref(divider_init))
                divider_init = divider_init.value

                divider = c_uint()
                self.dwf.FDwfDigitalOutDividerGet(self.hdwf, c_int(i), byref(divider))
                divider = divider.value

                initial_state = c_int()
                counter_init = c_uint()
                self.dwf.FDwfDigitalOutCounterInitGet(self.hdwf, c_int(i), byref(initial_state),
                                                      byref(counter_init))
                initial_state = initial_state.value
                counter_init = counter_init.value

                counter_high = c_uint()
                counter_low = c_uint()
                self.dwf.FDwfDigitalOutCounterGet(self.hdwf, c_int(i), byref(counter_low), byref(counter_high))
                counter_high = counter_high.value
                counter_low = counter_low.value

                time_resolution = 1 / (internal_frequency / divider)
                period = time_resolution * (counter_low + counter_high)

                output_type = c_int()
                self.dwf.FDwfDigitalOutTypeGet(self.hdwf, c_int(i), byref(output_type))

                if initial_state == 0:
                    delay = wait_time + time_resolution * counter_low
                    width = time_resolution * counter_high
                else:
                    delay = wait_time + time_resolution * counter_high
                    width = time_resolution * counter_low

                # print
                if round(run_time, 8) == round(period, 8):
                    state = '(Auto Runtime)'
                else:
                    state = '(Period: %.2fus, Remaining: %.2fus)' % (period * 1e6, (run_time - period) * 1e6)
                    if run_time - period >= delay - wait_time:
                        raise Warning('run_time-period >= delay-wait_time_floor!')
                # print('Internal frequency: %.1fMHz.' % (internal_frequency / 1e6))

                print('Channel %d Configuration:' % i)
                print('\tTime Resolution: [%.2fus (%.1fMHz/%d)].' % (
                    time_resolution * 1e6, internal_frequency / 1e6, divider))
                print('\tWait Time: [%.2fus].' % (wait_time * 1e6))
                print('\tRun Time: [%.2fus ' % (run_time * 1e6) + state + '].')

                if initial_state == 0:
                    pulse_type = 'High Pulse'
                elif initial_state == 1:
                    pulse_type = 'Low Pulse'
                else:
                    pulse_type = 'Unknown Pulse Type'

                if output_type.value == self._DwfDigitalOutTypePulse.value:
                    print('\tOutput Mode:')
                    # print('\t\tPulse ' + pulse_type + ' Delay=%.2fus, Finish=%.2fus, Width=%.2fus)' % (
                    #     delay * 1e6, (delay + width) * 1e6, width * 1e6))
                    print("\t\t{:<10} {:<20} {:<15} {:<15} {:<15}"
                          .format("Type", "Shape",
                                  'Delay',
                                  'Finish',
                                  'Width'))
                    print("\t\t{:<10} {:<20} {:<15} {:<15} {:<15}"
                          .format("[Pulse]", '[' + pulse_type + ']',
                                  '[%.2fus]' % (delay * 1e6),
                                  '[%.2fus]' % ((delay + width) * 1e6),
                                  '[%.2fus]' % (width * 1e6)))
                else:
                    print('\tUnknown mode.')

                if divider_init == 0 and counter_init == 0:
                    print('\tDividerInit/CounterInit Value 0: [Confirmed].')
                else:
                    print('\tDividerInit Value: [%d]; \tCounterInit Value: [%d].' % (
                        divider_init,
                        counter_init
                    ))

                print('\tCounter: [Low: %d (%.2fus)] [High: %d (%.2fus)].' % (
                    counter_low,
                    counter_low * time_resolution * 1e6,
                    counter_high,
                    counter_high * time_resolution * 1e6
                ))

    def setPatternWaveformCustom(self, channel_index=-1, pulse_state=1, pulse_width_list_us=None,
                                 pulse_relative_delay_list_us=None, verbose=False):
        if isinstance(channel_index, list) is False:
            if channel_index == -1:
                bits = range(0, 16)
            else:
                bits = [channel_index]
        else:
            bits = channel_index

        for channel in bits:
            # output type
            self.dwf.FDwfDigitalOutTypeSet(self.hdwf, c_uint(channel), self._DwfDigitalOutTypeCustom)

            # wait
            delay_us = pulse_relative_delay_list_us[0]
            wait_resolution_us = 100
            wait_floor = round(delay_us // wait_resolution_us, 0)
            wait_modular = round(delay_us % wait_resolution_us, 0)
            if wait_modular == 0:
                wait_floor = wait_floor - 1

            if self.wait_time_floor is None:
                self.wait_time_floor = wait_floor
            elif wait_floor >= self.wait_time_floor:
                pass
            else:
                raise Warning('Current wait_time_floor is smaller than previous one. Put it before precious one.')

            if self.wait_time_floor == 0:
                # self.dwf.FDwfDigitalOutWaitSet(self.hdwf, c_double(0))
                pass
            else:
                self.dwf.FDwfDigitalOutWaitSet(self.hdwf, c_double(self.wait_time_floor * wait_resolution_us / 1e6))
            delay_us_remaining = delay_us - self.wait_time_floor * wait_resolution_us
            pulse_relative_delay_list_us[0] = delay_us_remaining

            # divider (sample rate)
            period = np.sum(pulse_relative_delay_list_us) + pulse_width_list_us[-1]

            # run time
            if self.run_time is None:
                self.run_time = period / 1e6
            else:
                run_time = period / 1e6
                if run_time > self.run_time:
                    self.run_time = run_time
            self.dwf.FDwfDigitalOutRunSet(self.hdwf, c_double(self.run_time))

            sample_size_max = c_uint()
            self.dwf.FDwfDigitalOutDataInfo(self.hdwf, c_int(channel_index), byref(sample_size_max))
            sample_size_max = sample_size_max.value
            time_resolution_float = self.run_time / sample_size_max

            internal_frequency = c_double()
            self.dwf.FDwfDigitalOutInternalClockInfo(self.hdwf, byref(internal_frequency))
            internal_frequency = internal_frequency.value

            clock_divider_float = time_resolution_float * internal_frequency
            clock_divider = int(np.ceil(clock_divider_float))

            self.dwf.FDwfDigitalOutDividerInitSet(self.hdwf, c_int(channel), c_uint(0))
            self.dwf.FDwfDigitalOutDividerSet(self.hdwf, c_int(channel), c_uint(clock_divider))
            divider_read = c_uint()
            self.dwf.FDwfDigitalOutDividerGet(self.hdwf, c_int(channel), byref(divider_read))
            divider_read = divider_read.value

            time_resolution = 1 / (internal_frequency / divider_read)

            # generate data
            data = self._generateCustomPulse(pulse_width_list_us=pulse_width_list_us,
                                             pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                             sample_size_max=sample_size_max,
                                             time_resolution=time_resolution,
                                             pulse_state=pulse_state)

            samples = (c_ubyte * ((len(data) + 7) >> 3))(0)  # how many bytes we need to fit this many bits, len/8
            for i in range(len(data)):  # array to bits in byte array
                if data[i] != 0:
                    samples[i >> 3] |= 1 << (i & 7)

            self.dwf.FDwfDigitalOutDataSet(self.hdwf, c_int(channel_index), byref(samples), c_int(len(data)))

            if verbose is True:
                self.getPatternWaveformCustom(channel=channel, data=data,
                                              pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                              pulse_width_list_us=pulse_width_list_us)

    def getPatternWaveformCustom(self, pulse_width_list_us, pulse_relative_delay_list_us, data, channel=-1):

        internal_frequency = c_double()
        self.dwf.FDwfDigitalOutInternalClockInfo(self.hdwf, byref(internal_frequency))
        internal_frequency = internal_frequency.value

        run_time = c_double()
        self.dwf.FDwfDigitalOutRunGet(self.hdwf, byref(run_time))
        run_time = run_time.value * 1e6

        wait_time = c_double()
        self.dwf.FDwfDigitalOutWaitGet(self.hdwf, byref(wait_time))
        wait_time = wait_time.value * 1e6
        if wait_time > 2814749767106:
            wait_time = 0

        if channel == -1:
            number_of_channels = c_int()
            self.dwf.FDwfDigitalOutCount(self.hdwf, byref(number_of_channels))
            channel_list = range(number_of_channels.value)
        else:
            channel_list = [channel]

        for i in channel_list:

            enable_state_read = c_int()
            self.dwf.FDwfDigitalOutEnableGet(self.hdwf, c_int(i), byref(enable_state_read))

            if enable_state_read.value == self._true.value:
                print('-' * 50)
                divider_init = c_uint()
                self.dwf.FDwfDigitalOutDividerInitGet(self.hdwf, c_int(i), byref(divider_init))
                divider_init = divider_init.value

                divider = c_uint()
                self.dwf.FDwfDigitalOutDividerGet(self.hdwf, c_int(i), byref(divider))
                divider = divider.value

                time_resolution = 1 / (internal_frequency / divider)
                period = np.sum(pulse_relative_delay_list_us) + pulse_width_list_us[-1]
                pulse_relative_delay_list_us = pulse_relative_delay_list_us.copy()
                pulse_absolute_delay_list_us = np.cumsum(pulse_relative_delay_list_us)

                output_type = c_int()
                self.dwf.FDwfDigitalOutTypeGet(self.hdwf, c_int(i), byref(output_type))

                # parse data
                data = np.array(data)
                index = np.where(data[:-1] != data[1:])[0]
                index = np.insert(index, 0, 0)
                index = np.append(index, len(data))
                timing_us = index / len(data) * period
                timing_us = timing_us[1::]

                delay = pulse_relative_delay_list_us[0] + wait_time
                # print
                if round(run_time, 8) == round(period, 8):
                    state = '(Auto Runtime)'
                else:
                    state = '(Period: %.2fus, Remaining: %.2fus)' % (period, (run_time - period))
                    # if run_time - period >= delay - wait_time:
                    #     raise Warning('run_time-period >= delay-wait_time_floor!')
                # print('Internal frequency: %.1fMHz.' % (internal_frequency / 1e6))

                print('Channel %d Configuration:' % i)
                print('\tTime Resolution: [%.2fus (%.1fMHz/%d)].' % (
                    time_resolution * 1e6, internal_frequency / 1e6, divider))
                print('\tWait Time: [%.2fus].' % wait_time)
                print('\tRun Time: [%.2fus ' % run_time + state + '].')
                print('\tSample Size: [%d].' % len(data))

                initial_state = data[0]
                if initial_state == 0:
                    pulse_type = 'High Pulse'
                elif initial_state == 1:
                    pulse_type = 'Low Pulse'
                else:
                    pulse_type = 'Unknown Pulse Type'
                print('\tPulse Type: [%s]' % pulse_type)

                if output_type.value == self._DwfDigitalOutTypeCustom.value:
                    print('\tCustom Data Output Mode:')
                    print('\t\t{:<15} {:<25} {:<25} {:<10}'.format('PulseIndex', 'StartTime', 'Width', 'EndTime'))
                    for i in range(int(len(timing_us) / 2)):
                        print('\t\t{:<15} {:<25} {:<25} {:<10}'.format(str(i + 1),
                                                                       '[%.1fus(ER:%.1fus)]' % (timing_us[i * 2],
                                                                                                timing_us[i * 2] -
                                                                                                pulse_absolute_delay_list_us[
                                                                                                    i]),
                                                                       '[%.1fus(ER:%.1fus)]' % (
                                                                           timing_us[i * 2 + 1] - timing_us[i * 2],
                                                                           timing_us[i * 2 + 1] - timing_us[i * 2] -
                                                                           pulse_width_list_us[i]),
                                                                       '[%.1fus]' % timing_us[i * 2 + 1]))
                else:
                    print('\tUnknown mode.')

                if divider_init == 0:
                    print('\tDividerInit Value 0: [Confirmed].')
                else:
                    print('\tDividerInit Value: [%d].' % divider_init)

    def _generateCustomPulse(self, pulse_width_list_us, pulse_relative_delay_list_us, sample_size_max, time_resolution,
                             pulse_state):
        if len(pulse_width_list_us) != len(pulse_relative_delay_list_us):
            raise ValueError

        data = []
        pulse_relative_delay_list_us = pulse_relative_delay_list_us.copy()
        pulse_absolute_delay_list_us = np.cumsum(pulse_relative_delay_list_us)

        pulse_end_list_index = np.round(
            np.add(pulse_width_list_us, pulse_absolute_delay_list_us) / (time_resolution * 1e6), 0).astype(int).tolist()
        pulse_start_delay_list_index = np.round(pulse_absolute_delay_list_us / (time_resolution * 1e6), 0).astype(
            int).tolist()

        if pulse_state == 1:
            idle_value = 0
            pulse_value = 1
        else:
            idle_value = 1
            pulse_value = 0

        data.extend([idle_value] * pulse_start_delay_list_index[0])
        for i in range(len(pulse_start_delay_list_index) - 1):
            data.extend([pulse_value] * (pulse_end_list_index[i] - pulse_start_delay_list_index[i]))
            data.extend([idle_value] * (pulse_start_delay_list_index[i + 1] - pulse_end_list_index[i]))
        data.extend([pulse_value] * (pulse_end_list_index[-1] - pulse_start_delay_list_index[-1]))

        if len(data) > sample_size_max:
            raise ValueError(len(data), sample_size_max)

        return data

    @staticmethod
    def _num2bits(numbers):
        if isinstance(numbers, list) is False:
            if numbers == -1:
                bits = c_uint(0)
            else:
                bits = c_uint(1 << numbers)
        else:
            bits = 0
            for number in numbers:
                bits = bits | 1 << number
            # bits = c_uint(bits)
        return bits

    @staticmethod
    def _bits2numbers(c_bits):
        bits = c_bits.value
        binary = format(bits, '016b')
        index = [15 - i for i, e in enumerate(binary) if e == '1']
        return index[::-1]

    def setPatternConstantHigh(self, channel_index=-1, verbose=True):
        if isinstance(channel_index, list) is False:
            if channel_index == -1:
                numbers = range(0, 16)
            else:
                numbers = [channel_index]
        else:
            numbers = channel_index

        bits = self._num2bits(numbers)

        # resets and configures all digital IO instrument parameters to default values.
        self.dwf.FDwfDigitalIOReset(self.hdwf)

        # enable output/mask on IO pins.
        self.dwf.FDwfDigitalIOOutputEnableSet(self.hdwf, c_int(bits))
        # set value on enabled IO pins
        self.dwf.FDwfDigitalIOOutputSet(self.hdwf, c_int(bits))

        if verbose is True:
            self.getPatternConstantOutput()

    def resetPatternConstant(self, verbose=True):
        # resets and configures all digital IO instrument parameters to default values.
        self.dwf.FDwfDigitalIOReset(self.hdwf)
        if verbose is True:
            self.getPatternConstantOutput()

    def getPatternConstantOutput(self):
        digital_io_output_read = c_uint32()

        # fetch digital IO information from the device
        self.dwf.FDwfDigitalIOStatus(self.hdwf)
        # read state of all pins, regardless of output enable
        self.dwf.FDwfDigitalIOInputStatus(self.hdwf, byref(digital_io_output_read))

        enabled_channels = self._bits2numbers(digital_io_output_read)
        if len(enabled_channels) == 0:
            print("Digital IO: [Disabled]")
        else:
            print("Digital IO: [High]-" + str(enabled_channels))

    def runPatternGenerator(self, verbose=False):
        self.dwf.FDwfDigitalOutConfigure(self.hdwf, self._true)
        if verbose is True:
            state_read = c_ubyte()
            self.dwf.FDwfDigitalOutStatus(self.hdwf, byref(state_read))

            state = ''
            if state_read.value == self._DwfStateReady.value:
                state = 'Ready'
            elif state_read.value == self._DwfStateDone.value:
                state = 'Done'
            elif state_read.value == self._DwfStateRunning.value:
                state = 'Running'
            elif state_read.value == self._DwfStateWait.value:
                state = 'Wait'
            elif state_read.value == self._DwfStateConfig.value:
                state = 'Config'
            elif state_read.value == self._DwfStatePrefill.value:
                state = 'Prefill'
            elif state_read.value == self._DwfStateArmed.value:
                state = 'Armed'
            elif state_read.value == self._DwfStateTriggered.value:
                state = 'Triggered'

            print("Pattern Generator Status:", state)

    def stopPatternGenerator(self, verbose=False):
        self.dwf.FDwfDigitalOutReset(self.hdwf)
        self.dwf.FDwfDigitalOutConfigure(self.hdwf, self._false)
        if verbose is True:
            state_read = c_ubyte()
            self.dwf.FDwfDigitalOutStatus(self.hdwf, byref(state_read))

            state = ''
            if state_read.value == self._DwfStateReady.value:
                state = 'Ready'
            elif state_read.value == self._DwfStateDone.value:
                state = 'Done'
            elif state_read.value == self._DwfStateRunning.value:
                state = 'Running'
            elif state_read.value == self._DwfStateWait.value:
                state = 'Wait'
            elif state_read.value == self._DwfStateConfig.value:
                state = 'Config'
            elif state_read.value == self._DwfStatePrefill.value:
                state = 'Prefill'
            elif state_read.value == self._DwfStateArmed.value:
                state = 'Armed'
            elif state_read.value == self._DwfStateTriggered.value:
                state = 'Triggered'

            print("Pattern Generator Status:", state)
