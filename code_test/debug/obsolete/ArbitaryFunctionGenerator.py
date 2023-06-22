from ctypes import c_int, c_bool, c_double, c_ubyte, byref
from SuperCharge.AnalogDiscovery.dwfconstants import DwfConstants


class ArbitraryFunctionGenerator(DwfConstants):
    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.channel = None

    def run(self):
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, self.channel, c_int(1))

    def stop(self):
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, self.channel, c_int(0))

    def apply(self):
        """
        Starts or stops the instrument. Value 3 will apply the configuration dynamically without changing the
        state of the instrument. With channel index -1, each enabled Analog Out channel will be configured.
        :return: None
        """
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, self.channel, c_int(3))

    def getIfRunning(self):
        state = c_ubyte()
        self.dwf.FDwfAnalogOutStatus(self.hdwf, self.channel, byref(state))
        if state.value == self._DwfStateRunning.value:
            return True
        elif state.value == self._DwfStateDone.value:
            return False


class FrequencySweep(ArbitraryFunctionGenerator):
    def __init__(self, channel=1):
        ArbitraryFunctionGenerator.__init__(self)
        self.channel = c_int(channel - 1)

    def setParameters(self, start_freq, stop_freq, sweep_time, peak2peak, if_low_value_is_zero=False):
        hzStart = start_freq
        hzStop = stop_freq
        hzMid = (hzStart + hzStop) / 2
        self._secSweep = sweep_time
        amplitude = peak2peak / 2
        if if_low_value_is_zero is False:
            offset = 0
        else:
            offset = amplitude

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, self._funcSine)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(hzMid))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier,
                                               c_double(amplitude))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(offset))

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeFM, self._funcRampUp)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeFM,
                                               c_double(1.0 / self._secSweep))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeFM,
                                               c_double(100.0 * (hzStop - hzMid) / hzMid))
        self.dwf.FDwfAnalogOutNodeSymmetrySet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_double(100))

    def runTime(self, time=None, wait=0, repeat=1):
        if time is None:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(self._secSweep))
        else:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(time))
        self.dwf.FDwfAnalogOutWaitSet(self.hdwf, self.channel, wait)
        self.dwf.FDwfAnalogOutRepeatSet(self.hdwf, self.channel, c_int(repeat))


class FmModulator(ArbitraryFunctionGenerator):
    def __init__(self, channel=1):
        ArbitraryFunctionGenerator.__init__(self)
        self.channel = c_int(channel - 1)

    def setParameters(self, start_freq, stop_freq, fm_freq, peak2peak, data, if_low_value_is_zero=False):
        hzStart = start_freq
        hzStop = stop_freq
        hzMid = (hzStart + hzStop) / 2

        cSamples = len(data)
        rgdSamples = (c_double * cSamples)()
        # The samples are double precision floating point values (rgdData) normalized to ±1.
        for i in range(0, len(rgdSamples)):
            hz = hzMid + (hzStop - hzMid) * data[i]
            rgdSamples[i] = (hz - hzMid) / hzMid

        self._secSweep = 1 / fm_freq
        amplitude = peak2peak / 2
        if if_low_value_is_zero is False:
            offset = 0
        else:
            offset = amplitude

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, self._funcSine)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(hzMid))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier,
                                               c_double(amplitude))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(offset))

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeFM, self._funcCustom)
        self.dwf.FDwfAnalogOutNodeDataSet(self.hdwf, self.channel, self._AnalogOutNodeFM, rgdSamples, c_int(cSamples))
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeFM,
                                               c_double(fm_freq))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_double(100))
        self.dwf.FDwfAnalogOutNodeSymmetrySet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_double(50))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, self.channel, self._AnalogOutNodeFM, c_double(0))

    def runTime(self, time=None, wait=0, repeat=1):
        if time is None:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(self._secSweep))
        else:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(time))
        self.dwf.FDwfAnalogOutWaitSet(self.hdwf, self.channel, wait)
        self.dwf.FDwfAnalogOutRepeatSet(self.hdwf, self.channel, c_int(repeat))

    def getCustomFMDataLimitation(self):
        sample_min = c_int()
        sample_max = c_int()
        self.dwf.FDwfAnalogOutNodeDataInfo(self.hdwf, self.channel, self._AnalogOutNodeFM, byref(sample_min),
                                           byref(sample_max))
        # print(sample_min.value, sample_max.value)
        return sample_min.value, sample_max.value


class FrequencyDwell(ArbitraryFunctionGenerator):
    def __init__(self, channel=1):
        ArbitraryFunctionGenerator.__init__(self)
        self.channel = c_int(channel - 1)

    def setParameters(self, freq, peak2peak, if_low_value_is_zero=False):
        hzMid = freq
        self._secSweep = 1 / freq
        amplitude = peak2peak / 2
        if if_low_value_is_zero is False:
            offset = 0
        else:
            offset = amplitude

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, self._funcSine)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(hzMid))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier,
                                               c_double(amplitude))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(offset))

    def runTime(self, time=None, wait=0, repeat=1):
        if time is None:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(self._secSweep))
        else:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(time))
        self.dwf.FDwfAnalogOutWaitSet(self.hdwf, self.channel, wait)
        self.dwf.FDwfAnalogOutRepeatSet(self.hdwf, self.channel, c_int(repeat))


class FrequencyDwellFeedback(ArbitraryFunctionGenerator):
    def __init__(self, channel=1):
        ArbitraryFunctionGenerator.__init__(self)
        self.channel = c_int(channel - 1)

    def setParameters(self, freq, peak2peak, if_low_value_is_zero=False):
        hzMid = freq
        self._secSweep = 1 / freq
        amplitude = peak2peak / 2
        if if_low_value_is_zero is False:
            offset = 0
        else:
            offset = amplitude

        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_bool(True))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, self._funcSine)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(hzMid))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier,
                                               c_double(amplitude))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, self.channel, self._AnalogOutNodeCarrier, c_double(offset))

    def runTime(self, time=None, wait=0, repeat=1):
        if time is None:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(self._secSweep))
        else:
            self.dwf.FDwfAnalogOutRunSet(self.hdwf, self.channel, c_double(time))
        self.dwf.FDwfAnalogOutWaitSet(self.hdwf, self.channel, wait)
        self.dwf.FDwfAnalogOutRepeatSet(self.hdwf, self.channel, c_int(repeat))
