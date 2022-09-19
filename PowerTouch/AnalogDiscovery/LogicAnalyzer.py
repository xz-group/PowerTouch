from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants
from ctypes import c_double, byref, c_int, c_ubyte, c_bool, c_uint, c_uint8
import numpy as np


class LogicAnalyzer(DwfConstants):
    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.dwf.FDwfDigitalInReset(self.hdwf)
        self.buffer_size = 4096
        self.reference = int(self.buffer_size / 2 - 1)
        self.frequency = 400e3
        self.position = 0
        self.time = None

    def getAnalyzerTitle(self, verbose=False):
        if verbose is True:
            print('')
            print('=' * 100)
            print('Logic Analyzer')
            print('=' * 100)

    def setAnalyzerClockFrequency(self, frequency=10e6, verbose=False):
        internal_clock_read = c_double()  # to verify the frequency
        self.dwf.FDwfDigitalInInternalClockInfo(self.hdwf, byref(internal_clock_read))

        divider = internal_clock_read.value / frequency
        divider = int(round(divider, 0))
        self.dwf.FDwfDigitalInDividerSet(self.hdwf, c_uint(divider))
        self.frequency = self.getAnalyzerClockFrequency(if_print=False)
        if verbose is True:
            self.getAnalyzerClockFrequency(if_print=True)

    def getAnalyzerClockFrequency(self, if_print=True):
        internal_clock_read = c_double()
        self.dwf.FDwfDigitalInInternalClockInfo(self.hdwf, byref(internal_clock_read))
        clock_source_read = c_int()
        self.dwf.FDwfDigitalInClockSourceGet(self.hdwf, byref(clock_source_read))
        if clock_source_read.value == self._DwfDigitalInClockSourceInternal.value:
            source = 'Internal'
        else:
            source = 'External'

        divider_read = c_uint()
        divider_max = c_uint()
        self.dwf.FDwfDigitalInDividerInfo(self.hdwf, byref(divider_max))
        self.dwf.FDwfDigitalInDividerGet(self.hdwf, byref(divider_read))
        if if_print is True:
            # print(source + " Clock frequency: %.1fMHz / %d = %.3fMHz." % (
            #     internal_clock_read.value / 1e6, divider_read.value,
            #     internal_clock_read.value / divider_read.value / 1e6))
            print(
                "Sampling Frequency: [%.1fKHz (%.3fMHz/%d)]." % (internal_clock_read.value / divider_read.value / 1e3,
                                                                 internal_clock_read.value / 1e6, divider_read.value))

        return internal_clock_read.value / divider_read.value

    def setAnalyzerBufferSize(self, size=4096, verbose=False):
        self.buffer_size = size
        self.dwf.FDwfDigitalInBufferSizeSet(self.hdwf, c_int(size))
        if verbose is True:
            self.getAnalyzerBufferSize()

    def getAnalyzerBufferSize(self):
        buffersize_read = c_int()  # to verify the buffer size
        buffersize_max = c_int()
        self.dwf.FDwfDigitalInBufferSizeGet(self.hdwf, byref(buffersize_read))
        self.dwf.FDwfDigitalInBufferSizeInfo(self.hdwf, byref(buffersize_max))
        # print("Buffer size: %d in [%d, %d]" % (
        #     buffersize_read.value, 0, buffersize_max.value))
        print("Buffer Size: [%d]." % (buffersize_read.value))
        return buffersize_read.value

    def setAnalyzerDataFormat(self, verbose=False):
        self.dwf.FDwfDigitalInSampleFormatSet(self.hdwf, c_int(8))  # 8bit per sample format
        # self.dwf.FDwfDigitalInInputOrderSet(self.hdwf, c_int(0))
        if verbose is True:
            self.getAnalyzerDataFormat()

    def getAnalyzerDataFormat(self):
        format = c_int()
        self.dwf.FDwfDigitalInSampleFormatGet(self.hdwf, byref(format))
        print("Sample Format: [%d bits]" % format.value)

    def setAnalyzerTriggerTimeout(self, timeout_s=0, verbose=False):
        # default disable auto trigger
        self.dwf.FDwfDigitalInTriggerAutoTimeoutSet(self.hdwf, c_double(timeout_s))
        if verbose is True:
            self.getAnalyzerTriggerTimeout()

    def getAnalyzerTriggerTimeout(self):
        timeout_read = c_double()
        timeout_max = c_double()
        timeout_min = c_double()
        timeout_steps = c_double()
        self.dwf.FDwfDigitalInTriggerAutoTimeoutGet(self.hdwf, byref(timeout_read))
        self.dwf.FDwfDigitalInTriggerAutoTimeoutInfo(self.hdwf, byref(timeout_min), byref(timeout_max),
                                                     byref(timeout_steps))

        if timeout_read.value == 0:
            print("Auto Trigger: [Disabled]")
        else:
            # print("Auto Trigger Enabled: %.1fs in [%.2fs, %.2fs]." % (
            #     timeout_read.value, timeout_min.value, timeout_max.value))
            print("Auto Trigger: [Enabled (%.1fs)]." % (timeout_read.value))

    def setAnalyzerTriggerSource(self, if_analogin=True, if_RisingPositive=True, level_low_channels=-1,
                                 level_high_channels=-1, edge_rise_channels=-1, edge_fall_channels=-1, verbose=False):
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

        if if_analogin is True:
            self.dwf.FDwfDigitalInTriggerSourceSet(self.hdwf, self._trigsrcDetectorAnalogIn)
            if if_RisingPositive is True:
                self.dwf.FDwfDigitalInTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeRise)
            else:
                self.dwf.FDwfDigitalInTriggerSlopeSet(self.hdwf, self._DwfTriggerSlopeFall)
        else:
            level_low = self._num2bits(level_low_channels)
            level_high = self._num2bits(level_high_channels)
            edge_fall = self._num2bits(edge_fall_channels)
            edge_rise = self._num2bits(edge_rise_channels)
            self.dwf.FDwfDigitalInTriggerSourceSet(self.hdwf, self._trigsrcDetectorDigitalIn)
            self.dwf.FDwfDigitalInTriggerSet(self.hdwf, level_low, level_high, edge_rise, edge_fall)

        if verbose is True:
            self.getAnalyzerTriggerSource()

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
            bits = c_uint(bits)
        return bits

    def getAnalyzerTriggerSource(self):
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

        self.dwf.FDwfDigitalInTriggerSourceGet(self.hdwf, byref(triggersoucre_read))
        if triggersoucre_read.value == self._trigsrcDetectorAnalogIn.value:
            triggercondition_read = c_int()
            self.dwf.FDwfDigitalInTriggerSlopeGet(self.hdwf, byref(triggercondition_read))
            if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
                condition = "Rising Edge"
            elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
                condition = "Falling Edge"
            else:
                condition = "Either Edge"
            print("Trigger on: [Analog Detector (%s)]." % condition)
        elif triggersoucre_read.value == self._trigsrcDetectorDigitalIn.value:
            print("Trigger on: [Digital Detector].")
            trigger_low = c_uint()
            trigger_high = c_uint()
            trigger_rise = c_uint()
            trigger_fall = c_uint()
            self.dwf.FDwfDigitalInTriggerGet(self.hdwf, byref(trigger_low), byref(trigger_high), byref(trigger_rise),
                                             byref(trigger_fall))

            # trigger_low_support = c_uint()
            # trigger_high_support = c_uint()
            # trigger_rise_support = c_uint()
            # trigger_fall_support = c_uint()
            # self.dwf.FDwfDigitalInTriggerInfo(self.hdwf, byref(trigger_low_support), byref(trigger_high_support),
            #                                   byref(trigger_rise_support),
            #                                   byref(trigger_fall_support))

            print("Trigger Condition:")
            print("Level low channels: " + str(self._bits2numbers(trigger_low)))
            print("Level high channels: " + str(self._bits2numbers(trigger_high)))
            print("Edge rise channels: " + str(self._bits2numbers(trigger_rise)))
            print("Edge fall channels: " + str(self._bits2numbers(trigger_fall)))
        else:
            print("Logic analyzer trigger on: Unknown.")

    @staticmethod
    def _bits2numbers(c_bits):
        bits = c_bits.value
        binary = format(bits, '016b')
        index = [15 - i for i, e in enumerate(binary) if e == '1']
        return index[::-1]

    def setAnalyzerState(self, if_reconfigure=True, if_start=True):
        self.dwf.FDwfDigitalInConfigure(self.hdwf, c_bool(if_reconfigure), c_bool(if_start))

    def getAnalyzerState(self, if_will_read_data=True, verbose=False):
        state_read = c_int()
        self.dwf.FDwfDigitalInStatus(self.hdwf, c_int(if_will_read_data), byref(state_read))
        auto_trigger_flag = c_uint()
        self.dwf.FDwfDigitalInStatusAutoTriggered(self.hdwf, byref(auto_trigger_flag))

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

        if if_will_read_data is True:
            will_read_data = 'True'
        else:
            will_read_data = 'False'

        # sample_left = c_double()
        # sample_valid = c_double()
        # self.dwf.FDwfDigitalInStatusSamplesLeft(self.hdwf, byref(sample_left))
        # self.dwf.FDwfDigitalInStatusSamplesValid(self.hdwf, byref(sample_valid))

        if auto_trigger_flag.value == self._false.value:
            trigger_flag = 'Normal'
            # trigger_flag = str(auto_trigger_flag.value)
        else:
            trigger_flag = "AutoTriggering"
            # trigger_flag = str(auto_trigger_flag.value)

        if verbose is True:
            print(
                'Analyzer state: ' + state + '; if will read data: ' + will_read_data + '; ' + trigger_flag + '.')
            # print('Buffer info: %d valid, %d left' % (sample_valid.value, sample_left.value))

        # return state, sample_valid.value, sample_left.value
        return state, trigger_flag

    def setAnalyzerAcquisitionMode(self, mode=0, verbose=False):
        """
        ACQMODE             int     Constant Capabilities
        acqmodeSingle       0       Perform a single buffer acquisition and rearm the instrument for next capture
                                    after the data is fetched to host using FDwfDigitalInStatus function.
                                    This is the default setting.
        acqmodeScanShift    1       Perform a continuous acquisition in FIFO style. The trigger setting is ignored. The
                                    last sample is at the end of buffer. The
                                    FDwfDigitalInStatusSamplesValid function is used to show the number
                                    of the acquired samples, which will grow until reaching the BufferSize. Then the
                                    waveform “picture” is shifted for every new sample.
        acqmodeScanScreen   2       Perform continuous acquisition circularly writing samples into the buffer. The
                                    trigger setting is ignored. The IndexWrite shows the buffer write position. This is
                                    similar to a heart monitor display.
        acqmodeRecord       3       Perform acquisition for length of time set by
                                    FDwfDigitalInRecordLengthSet.
        acqmodeSingle1      5       Perform a single buffer acquisition.

        """
        self.dwf.FDwfDigitalInAcquisitionModeSet(self.hdwf, c_int(mode))
        if verbose is True:
            self.getAnalyzerAcquisitionMode()

    def getAnalyzerAcquisitionMode(self, if_print=True):
        acquisition_mode = c_int()
        self.dwf.FDwfDigitalInAcquisitionModeGet(self.hdwf, byref(acquisition_mode))
        mode = ''
        if acquisition_mode.value == self._acqmodeSingle.value:
            mode = 'Repeated'
        elif acquisition_mode.value == self._acqmodeScanShift.value:
            mode = 'ScanShift'
        elif acquisition_mode.value == self._acqmodeScanScreen.value:
            mode = 'ScanScreen'
        elif acquisition_mode.value == self._acqmodeRecord.value:
            mode = 'Record'
        elif acquisition_mode.value == self._acqmodeSingle1.value:
            mode = 'Single'

        if if_print is True:
            print("Acquisition Mode: " + mode + '.')

    def setAnalyzerTriggerPosition(self, position_ms=0, verbose=False):
        self.reference = int(self.buffer_size / 2 - 1)
        time_tick = 1 / self.frequency
        self.reference = int(self.reference - int(position_ms / 1000 / time_tick) - 1)
        self.dwf.FDwfDigitalInTriggerPositionSet(self.hdwf, c_int(self.buffer_size - self.reference))

        self.position = position_ms / 1000
        if verbose is True:
            self.getAnalyzerTriggerPosition()

    def getAnalyzerTriggerPosition(self):
        position_read = c_uint()
        position_max = c_uint()
        self.dwf.FDwfDigitalInTriggerPositionGet(self.hdwf, byref(position_read))
        self.dwf.FDwfDigitalInTriggerPositionInfo(self.hdwf, byref(position_max))
        # print("Trigger Position: %.2fms (%d in [%d, %d])." % (self.position * 1000,
        #                                                       position_read.value, 0, self.buffer_size))
        print("Trigger Position: [%.2fms]." % (self.position * 1000))

    def readAnalyzerDataTime(self):
        if self.time is None:
            time_tick = 1 / self.frequency
            time = np.arange(0, self.buffer_size * time_tick, time_tick)
            time_zero = time[self.reference - 1]
            time2 = time - time_zero
            self.time = time2
        return self.time

    def readAnalyzerData(self, channel_number=1, verbose=False):
        data = (c_uint8 * self.buffer_size)()
        self.dwf.FDwfDigitalInStatusData(self.hdwf, data, len(data))  # read data

        data_raw = np.fromiter(data, dtype=np.uint8)
        data = np.expand_dims(data_raw, axis=1)
        data_bin = np.unpackbits(data, axis=1, count=channel_number, bitorder='little')
        return data_bin.transpose()
