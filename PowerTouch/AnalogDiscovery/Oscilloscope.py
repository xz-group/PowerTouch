from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants
from ctypes import c_double, byref, c_int, c_ubyte, c_bool, c_byte
import numpy as np
import warnings


class Oscilloscope(DwfConstants):

    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.dwf.FDwfAnalogInReset(self.hdwf)
        self.buffer_size = 8192
        self.frequency = 800e3
        self.position = 0
        self.time = None

    def getScopeTitle(self, verbose=False):
        if verbose is True:
            print('')
            print('=' * 100)
            print('Oscilloscope')
            print('=' * 100)

    def setScopeSamplingFrequency(self, frequency=800e3, verbose=False):
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(frequency))
        self.frequency = frequency
        if verbose is True:
            self.getScopeSamplingFrequency()

    def getScopeSamplingFrequency(self):
        frequency_read = c_double()  # to verify the frequency
        self.dwf.FDwfAnalogInFrequencyGet(self.hdwf, byref(frequency_read))
        print("Sampling Frequency: [%.1f KHz]" % (frequency_read.value / 1000))
        return frequency_read.value

    def setScopeBufferSize(self, size=8192, verbose=False):
        self.buffer_size = size
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(size))
        if verbose is True:
            self.getScopeBufferSize()

    def getScopeBufferSize(self):
        buffersize_read = c_int()  # to verify the buffer size
        buffersize_min = c_int()
        buffersize_max = c_int()
        self.dwf.FDwfAnalogInBufferSizeGet(self.hdwf, byref(buffersize_read))
        self.dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, byref(buffersize_min), byref(buffersize_max))
        # print("Buffer Size: %d in [%d, %d]" % (
        #     buffersize_read.value, buffersize_min.value, buffersize_max.value))
        print("Buffer Size: [%d]" % buffersize_read.value)
        return buffersize_read.value

    def enableScopeChannel(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(channel_index - 1), self._true)
        if verbose is True:
            self.getScopeChannelEnableStatus(channel_index)

    def getScopeChannelEnableStatus(self, channel_index=1):
        enable_status = c_int()
        channel_count = c_int()
        self.dwf.FDwfAnalogInChannelEnableGet(self.hdwf, c_int(channel_index - 1), byref(enable_status))
        self.dwf.FDwfAnalogInChannelCount(self.hdwf, byref(channel_count))
        print('-' * 20)
        if enable_status.value == self._true.value:
            # print("Channel %d/%d Enabled" % (channel_index, channel_count.value))
            print("Channel %d: [Enabled]" % (channel_index))
        else:
            # print("Channel %d/%d Disabled" % (channel_index, channel_count.value))
            print("Channel %d: [Disabled]" % (channel_index))

    def disableScopeChannel(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(channel_index - 1), self._false)
        if verbose is True:
            self.getScopeChannelEnableStatus(channel_index)

    def setScopeChannelRange(self, channel_index=1, peak2peak=0.2, verbose=False):
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(channel_index - 1), c_double(peak2peak * 2))
        if verbose is True:
            self.getScopeChannelRange(channel_index)

    def getScopeChannelRange(self, channel_index=1):
        range_read = c_double()
        channel_count = c_int()
        self.dwf.FDwfAnalogInChannelCount(self.hdwf, byref(channel_count))
        self.dwf.FDwfAnalogInChannelRangeGet(self.hdwf, c_int(channel_index - 1), byref(range_read))
        if range_read.value > 10:
            print("Channel %d Range: [%.1fV (Low gain mode)]" % (channel_index, range_read.value))
        else:
            print(
                "Channel %d Range: [%.1fV (High gain mode)]" % (channel_index, range_read.value))

    def setScopeTriggerOnChannel(self, channel=1, verbose=False):
        self.dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, self._trigsrcDetectorAnalogIn)  # one of the analog in channels
        self.dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, c_int(channel - 1))
        if verbose is True:
            self.getScopeTriggerOnChannel()

    def getScopeTriggerOnChannel(self):
        """
        TRIGSRC                     BYTE    Trigger Source Function
        trigsrcDetectorAnalogIn     2       Trigger detector on analog in channels.

        :return:
        """
        triggersoucre_read = c_ubyte()
        triggerchannel_read = c_int()
        triggerchannel_min = c_int()
        triggerchannel_max = c_int()
        self.dwf.FDwfAnalogInTriggerSourceGet(self.hdwf, byref(triggersoucre_read))
        self.dwf.FDwfAnalogInTriggerChannelGet(self.hdwf, byref(triggerchannel_read))
        self.dwf.FDwfAnalogInTriggerChannelInfo(self.hdwf, byref(triggerchannel_min), byref(triggerchannel_max))
        if triggersoucre_read.value == self._trigsrcDetectorAnalogIn.value:
            # print("Trigger Detector on [Analog Channel %d] in [%d, %d]." % (
            #     triggerchannel_read.value + 1, triggerchannel_min.value + 1, triggerchannel_max.value + 1))
            print("Trigger Detector on [Analog Channel %d]." % (triggerchannel_read.value + 1))

    def setScopeTriggerLevel(self, level_mV=30, verbose=False):
        self.dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(level_mV / 1000))
        if verbose is True:
            self.getScopeTriggerLevel()

    def getScopeTriggerLevel(self):
        level_read = c_double()
        level_max = c_double()
        level_min = c_double()
        level_steps = c_double()
        self.dwf.FDwfAnalogInTriggerLevelGet(self.hdwf, byref(level_read))
        self.dwf.FDwfAnalogInTriggerLevelInfo(self.hdwf, byref(level_min), byref(level_max), byref(level_steps))
        # print("Trigger Level: %.2fmV in [%.1fV, %.1fV]." % (
        #     level_read.value * 1000, level_min.value, level_max.value))
        print("Trigger Level: [%.2fmV]." % (level_read.value * 1000))

    def setScopeTriggerPosition(self, position_ms=0, verbose=False):
        self.dwf.FDwfAnalogInTriggerPositionSet(self.hdwf, c_double(position_ms / 1000))
        self.position = position_ms / 1000
        if verbose is True:
            self.getScopeTriggerPosition()

    def getScopeTriggerPosition(self):
        position_read = c_double()
        position_max = c_double()
        position_min = c_double()
        position_steps = c_double()
        self.dwf.FDwfAnalogInTriggerPositionGet(self.hdwf, byref(position_read))
        self.dwf.FDwfAnalogInTriggerPositionInfo(self.hdwf, byref(position_min), byref(position_max),
                                                 byref(position_steps))
        # print("Trigger Position: %.2fms in [%.1fs, %.1fs]." % (
        #     position_read.value * 1000, position_min.value, position_max.value))
        print("Trigger Position: [%.2fms]." % (position_read.value * 1000))

    def setScopeTriggerTimeout(self, timeout_s=0, verbose=False):
        # default disable auto trigger
        self.dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, c_double(timeout_s))
        if verbose is True:
            self.getScopeTriggerTimeout()

    def getScopeTriggerTimeout(self):
        timeout_read = c_double()
        timeout_max = c_double()
        timeout_min = c_double()
        timeout_steps = c_double()
        self.dwf.FDwfAnalogInTriggerAutoTimeoutGet(self.hdwf, byref(timeout_read))
        self.dwf.FDwfAnalogInTriggerAutoTimeoutInfo(self.hdwf, byref(timeout_min), byref(timeout_max),
                                                    byref(timeout_steps))

        if timeout_read.value == 0:
            print("Auto Trigger: [Disabled]")
        else:
            # print("Auto Trigger Enabled: %.1fs in [%.2fs, %.2fs]." % (
            #     timeout_read.value, timeout_min.value, timeout_max.value))
            print("Auto Trigger: [Enabled (%.1fs)]." % (timeout_read.value))

    def setScopeTriggerEdge(self, if_RisingPositive=True, verbose=False):
        self.dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, self._trigtypeEdge)
        if if_RisingPositive is True:
            self.dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, self._DwfTriggerSlopeRise)
        else:
            self.dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, self._DwfTriggerSlopeFall)
        if verbose is True:
            self.getScopeTriggerEdge()

    def getScopeTriggerEdge(self):
        triggertype_read = c_int()
        triggercondition_read = c_int()
        self.dwf.FDwfAnalogInTriggerTypeGet(self.hdwf, byref(triggertype_read))
        self.dwf.FDwfAnalogInTriggerConditionGet(self.hdwf, byref(triggercondition_read))
        if triggertype_read.value == self._trigtypeEdge.value:
            type = "Edge"
        else:
            type = "Non-Edge"

        if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
            condition = "Rising"
        elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
            condition = "Falling"
        else:
            condition = "Either"

        print("Trigger on [" + " ".join([condition, type]) + '].')

    def setScopeTriggerHysteresis(self, hyst_mV=25, verbose=False):
        self.dwf.FDwfAnalogInTriggerHysteresisSet(self.hdwf, c_double(hyst_mV / 1000))
        if verbose is True:
            self.getScopeTriggerHysteresis()

    def getScopeTriggerHysteresis(self):
        hyst_read = c_double()
        self.dwf.FDwfAnalogInTriggerHysteresisGet(self.hdwf, byref(hyst_read))
        print("Trigger Hysteresis: [%.2fmV]." % (hyst_read.value * 1000))

    def setScopeTriggerHoldOff(self, holdoff_ms=0, verbose=False):
        holdoff_max = c_double()
        holdoff_min = c_double()
        holdoff_steps = c_double()
        self.dwf.FDwfAnalogInTriggerHoldOffInfo(self.hdwf, byref(holdoff_min), byref(holdoff_max),
                                                byref(holdoff_steps))
        if holdoff_ms / 1000 > holdoff_max.value:
            warnings.warn(
                'Required hold off time %.3fs exceed maximum hold off time %.3f' % (
                    holdoff_ms / 1000, holdoff_max.value))
        self.dwf.FDwfAnalogInTriggerHoldOffSet(self.hdwf, c_double(holdoff_ms / 1000))
        if verbose is True:
            self.getScopeTriggerHoldOff()

    def getScopeTriggerHoldOff(self):
        holdoff_read = c_double()
        holdoff_max = c_double()
        holdoff_min = c_double()
        holdoff_steps = c_double()
        self.dwf.FDwfAnalogInTriggerHoldOffGet(self.hdwf, byref(holdoff_read))
        self.dwf.FDwfAnalogInTriggerHoldOffInfo(self.hdwf, byref(holdoff_min), byref(holdoff_max),
                                                byref(holdoff_steps))
        # print("Trigger holdoff: %.1fms in [%.1fs, %.1fs]." % (
        #     holdoff_read.value * 1000, holdoff_min.value, holdoff_max.value))
        print("Trigger Holdoff: [%.1fms]." % (holdoff_read.value * 1000))

    def setScopeState(self, if_reconfigure=True, if_start=True):
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_bool(if_reconfigure), c_bool(if_start))

    def getScopeState(self, if_will_read_data=True, verbose=False):
        state_read = c_byte()
        self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(if_will_read_data), byref(state_read))
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
        # self.dwf.FDwfAnalogInStatusSamplesLeft(self.hdwf, byref(sample_left))
        # self.dwf.FDwfAnalogInStatusSamplesValid(self.hdwf, byref(sample_valid))

        auto_trigger_flag = c_int()
        self.dwf.FDwfAnalogInStatusAutoTriggered(self.hdwf, byref(auto_trigger_flag))
        if auto_trigger_flag.value == self._true.value:
            trigger_flag = "AutoTriggering"
        else:
            trigger_flag = 'Normal'

        if verbose is True:
            print(
                'Scope state: ' + state + '; if will read data: ' + will_read_data + '; ' + trigger_flag + '.')
            # print('Buffer info: %d valid, %d left' % (sample_valid.value, sample_left.value))

        # return state, sample_valid.value, sample_left.value
        return state, trigger_flag

    def readScopeChannelDataTime(self):
        if self.time is None:
            time_tick = 1 / self.frequency
            time = np.arange(-self.buffer_size * time_tick / 2, self.buffer_size * time_tick / 2, time_tick)
            time = time + self.position
            self.time = time
        return self.time

    def readScopeChannelData(self, channel_index=1, verbose=False):
        data = (c_double * self.buffer_size)()
        self.dwf.FDwfAnalogInStatusData(self.hdwf, c_int(channel_index - 1), data, len(data))
        data = np.fromiter(data, dtype=np.float)

        return data

    def setScopeChannelFilter(self, channel_index=-1, filter_index=1, verbose=False):
        """
        FILTER          int     Constant Capabilities
        filterDecimate  0       Store every Nth ADC conversion, where N = ADC frequency /acquisition frequency.
        filterAverage   1       Store the average of N ADC conversions.
        filterMinMax    2       Store interleaved, the minimum and maximum values, of 2xN conversions.
        """
        if channel_index == -1:  # set all channels
            self.dwf.FDwfAnalogInChannelFilterSet(self.hdwf, c_int(channel_index), c_int(filter_index))
            if verbose is True:
                self.getScopeChannelFilter(1)
                self.getScopeChannelFilter(2)
        else:
            self.dwf.FDwfAnalogInChannelFilterSet(self.hdwf, c_int(channel_index - 1), c_int(filter_index))
            if verbose is True:
                self.getScopeChannelFilter(channel_index)

    def getScopeChannelFilter(self, channel_index=1):
        filter_read = c_int()
        self.dwf.FDwfAnalogInChannelFilterGet(self.hdwf, c_int(channel_index - 1), byref(filter_read))
        filter_type = ''
        if filter_read.value == self._filterDecimate.value:
            filter_type = 'Decimate (Store every Nth ADC conversion, where N = ADC frequency /acquisition frequency)'
        elif filter_read.value == self._filterAverage.value:
            filter_type = 'Average (Store the average of N ADC conversions)'
        elif filter_read.value == self._filterMinMax.value:
            filter_type = 'MinMax (Store interleaved, the minimum and maximum values, of 2xN conversions)'
        print('Channel %d acquisition filter: ' % channel_index + filter_type + '.')

    def setScopeTriggerFilter(self, filter_index=1, verbose=False):
        """
        FILTER          int     Constant Capabilities
        filterDecimate  0       Store every Nth ADC conversion, where N = ADC frequency /acquisition frequency.
        filterAverage   1       Store the average of N ADC conversions.
        filterMinMax    2       Store interleaved, the minimum and maximum values, of 2xN conversions.
        """
        self.dwf.FDwfAnalogInTriggerFilterSet(self.hdwf, c_int(filter_index))
        if verbose is True:
            self.getScopeTriggerFilter()

    def getScopeTriggerFilter(self):
        filter_read = c_int()
        self.dwf.FDwfAnalogInTriggerFilterGet(self.hdwf, byref(filter_read))
        filter_type = ''
        if filter_read.value == self._filterDecimate.value:
            filter_type = 'Decimate (Store every Nth ADC conversion, where N = ADC frequency /acquisition frequency)'
        elif filter_read.value == self._filterAverage.value:
            filter_type = 'Average (Store the average of N ADC conversions)'
        elif filter_read.value == self._filterMinMax.value:
            filter_type = 'MinMax (Store interleaved, the minimum and maximum values, of 2xN conversions)'
        print('Trigger Filter: [' + filter_type + '].')

    def setScopeAcquisitionMode(self, mode=0, verbose=False):
        """
        ACQMODE             int     Constant Capabilities
        acqmodeSingle       0       Perform a single buffer acquisition and rearm the instrument for next capture
                                    after the data is fetched to host using FDwfAnalogInStatus function.
                                    This is the default setting.
        acqmodeScanShift    1       Perform a continuous acquisition in FIFO style. The trigger setting is ignored. The
                                    last sample is at the end of buffer. The
                                    FDwfAnalogInStatusSamplesValid function is used to show the number
                                    of the acquired samples, which will grow until reaching the BufferSize. Then the
                                    waveform “picture” is shifted for every new sample.
        acqmodeScanScreen   2       Perform continuous acquisition circularly writing samples into the buffer. The
                                    trigger setting is ignored. The IndexWrite shows the buffer write position. This is
                                    similar to a heart monitor display.
        acqmodeRecord       3       Perform acquisition for length of time set by
                                    FDwfAnalogInRecordLengthSet.
        acqmodeSingle1      5       Perform a single buffer acquisition.

        """
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, c_int(mode))
        if verbose is True:
            self.getScopeAcquisitionMode()

    def getScopeAcquisitionMode(self, if_print=True):
        acquisition_mode = c_int()
        self.dwf.FDwfAnalogInAcquisitionModeGet(self.hdwf, byref(acquisition_mode))
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
