from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants
from ctypes import c_double, byref, c_int, c_ubyte, c_uint
import numpy as np


class WaveformGenerator(DwfConstants):
    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.dwf.FDwfAnalogOutReset(self.hdwf, c_int(-1))  # reset instrument parameters across all channels

    def getWaveformTitle(self, verbose=False):
        if verbose is True:
            print('')
            print('=' * 100)
            print('Arbitrary Function Generator')
            print('=' * 100)

    def setWaveformChannelTriggerSource(self, channel_index=1, if_analogin=False, if_selftrigger=True,
                                        if_RisingPositive=True,
                                        verbose=False):
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
            self.dwf.FDwfAnalogOutTriggerSourceSet(self.hdwf, c_int(channel_index - 1), self._trigsrcNone)
        elif if_analogin is True:
            self.dwf.FDwfAnalogOutTriggerSourceSet(self.hdwf, c_int(channel_index - 1), self._trigsrcDetectorAnalogIn)
            if if_RisingPositive is True:
                self.dwf.FDwfAnalogOutTriggerSlopeSet(self.hdwf, c_int(channel_index - 1), self._DwfTriggerSlopeRise)
            else:
                self.dwf.FDwfAnalogOutTriggerSlopeSet(self.hdwf, c_int(channel_index - 1), self._DwfTriggerSlopeFall)
        elif if_analogin is False:
            self.dwf.FDwfAnalogOutTriggerSourceSet(self.hdwf, c_int(channel_index - 1), self._trigsrcDetectorDigitalIn)
            if if_RisingPositive is True:
                self.dwf.FDwfAnalogOutTriggerSlopeSet(self.hdwf, c_int(channel_index - 1), self._DwfTriggerSlopeRise)
            else:
                self.dwf.FDwfAnalogOutTriggerSlopeSet(self.hdwf, c_int(channel_index - 1), self._DwfTriggerSlopeFall)

        if verbose is True:
            self.getWaveformChannelTriggerSource(channel_index=channel_index)

    def getWaveformChannelTriggerSource(self, channel_index=1):
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

        self.dwf.FDwfAnalogOutTriggerSourceGet(self.hdwf, c_int(channel_index - 1), byref(triggersoucre_read))
        if triggersoucre_read.value == self._trigsrcDetectorAnalogIn.value:
            triggercondition_read = c_int()
            self.dwf.FDwfAnalogOutTriggerSlopeGet(self.hdwf, c_int(channel_index - 1), byref(triggercondition_read))
            if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
                condition = "Rising Edge"
            elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
                condition = "Falling Edge"
            else:
                condition = "Either Edge"
            print("Channel [%d] Trigger on: [Analog Detector (%s)]." % (channel_index, condition))
        elif triggersoucre_read.value == self._trigsrcDetectorDigitalIn.value:
            triggercondition_read = c_int()
            self.dwf.FDwfAnalogOutTriggerSlopeGet(self.hdwf, c_int(channel_index - 1), byref(triggercondition_read))
            if triggercondition_read.value == self._DwfTriggerSlopeRise.value:
                condition = "Rising Edge"
            elif triggercondition_read.value == self._DwfTriggerSlopeFall.value:
                condition = "Falling Edge"
            else:
                condition = "Either Edge"
            print("Channel [%d] Trigger on: [Digital Detector (%s)]." % (channel_index, condition))
        elif triggersoucre_read.value == self._trigsrcNone.value:
            print("Channel [%d] Trigger on: [None]." % channel_index)
        else:
            print("Channel [%d] Trigger on: [Unknown]." % channel_index)

    def setWaveformChannelRunInfo(self, channel_index=1, delay_us=0, runtime_us=0, repeat_number=0,
                                  if_repeattrigger=True, verbose=False):
        self.dwf.FDwfAnalogOutRepeatSet(self.hdwf, c_int(channel_index - 1), c_uint(repeat_number))
        self.dwf.FDwfAnalogOutRunSet(self.hdwf, c_int(channel_index - 1), c_double(runtime_us / 1e6))
        self.dwf.FDwfAnalogOutWaitSet(self.hdwf, c_int(channel_index - 1), c_double(delay_us / 1e6))

        # set if can be triggered during the repeat
        if if_repeattrigger is True:
            self.dwf.FDwfAnalogOutRepeatTriggerSet(self.hdwf, c_int(channel_index - 1), self._true)
        else:
            self.dwf.FDwfAnalogOutRepeatTriggerSet(self.hdwf, c_int(channel_index - 1), self._false)

        if verbose is True:
            self.getWaveformChannelRunInfo(channel_index=channel_index)

    def getWaveformChannelRunInfo(self, channel_index=1):
        runtime_read = c_double()
        runtime_max = c_double()
        runtime_min = c_double()

        self.dwf.FDwfAnalogOutRunGet(self.hdwf, c_int(channel_index - 1), byref(runtime_read))
        self.dwf.FDwfAnalogOutRunInfo(self.hdwf, c_int(channel_index - 1), byref(runtime_min), byref(runtime_max))

        delay_read = c_double()
        delay_max = c_double()
        delay_min = c_double()

        self.dwf.FDwfAnalogOutWaitGet(self.hdwf, c_int(channel_index - 1), byref(delay_read))
        self.dwf.FDwfAnalogOutWaitInfo(self.hdwf, c_int(channel_index - 1), byref(delay_min), byref(delay_max))

        repeat_read = c_int()
        repeat_max = c_int()
        repeat_min = c_int()
        repeattrigger_read = c_int()

        self.dwf.FDwfAnalogOutRepeatGet(self.hdwf, c_int(channel_index - 1), byref(repeat_read))
        self.dwf.FDwfAnalogOutRepeatInfo(self.hdwf, c_int(channel_index - 1), byref(repeat_min), byref(repeat_max))
        self.dwf.FDwfAnalogOutRepeatTriggerGet(self.hdwf, c_int(channel_index - 1), byref(repeattrigger_read))

        if repeattrigger_read.value == self._true.value:
            print('Repeat Trigger: [Enabled].')
        elif repeattrigger_read.value == self._false.value:
            print('Repeat Trigger: [Disabled].')
        else:
            print('Repeat Trigger: [Unknown].')

        if repeat_read.value == 0:
            print("Repeat Number: [Infinite Repeats].")
        else:
            # print("Repeat Number: %d in [%d, %d]; " % (
            #     repeat_read.value, repeat_min.value, repeat_max.value) + state + '.')
            print("Repeat Number: [%d]." % repeat_read.value)

        print('Wait Time: [%.2fus].' % (delay_read.value * 1e6))

        if runtime_read.value == 0:
            print('Run Time: [Continuous].')
        else:
            # print('Run Time: %.2fus in [%.2es, %.2es].' % (
            #     runtime_read.value * 1e6, runtime_min.value, runtime_max.value))
            print('Run Time: [%.2fus].' % (runtime_read.value * 1e6))

    def setWaveformMasterChannel(self, channel_index=1, verbose=False):
        if channel_index == 1:
            self.dwf.FDwfAnalogOutMasterSet(self.hdwf, c_int(2 - 1), c_int(channel_index - 1))
        elif channel_index == 2:
            self.dwf.FDwfAnalogOutMasterSet(self.hdwf, c_int(1 - 1), c_int(channel_index - 1))
        else:
            self.dwf.FDwfAnalogOutMasterSet(self.hdwf, c_int(-1), c_int(channel_index - 1))
        if verbose is True:
            self.getWaveformMasterChannel()

    def getWaveformMasterChannel(self):
        for i in range(2):
            master_read = c_int()
            self.dwf.FDwfAnalogOutMasterGet(self.hdwf, c_int(i), byref(master_read))
            print('Channel %d is mastered by channel %d.' % (i + 1, master_read.value + 1))

    def runWaveformChannel(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, c_int(channel_index - 1), c_int(1))
        if verbose is True:
            self.getWaveformChannelState(channel_index=channel_index)

    def stopWaveformChannel(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, c_int(channel_index - 1), c_int(0))
        if verbose is True:
            self.getWaveformChannelState(channel_index=channel_index)

    def getWaveformChannelState(self, channel_index=1):
        state_read = c_ubyte()
        self.dwf.FDwfAnalogOutStatus(self.hdwf, c_int(channel_index - 1), byref(state_read))

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

        print("Waveform generator channel %d status:" % channel_index, state)

    def enableWaveformChannelCarrier(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeCarrier, self._true)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def disableWaveformChannelCarrier(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeCarrier,
                                            self._false)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def enableWaveformChannelFM(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeFM, self._true)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def disableWaveformChannelFM(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeFM, self._false)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def enableWaveformChannelAM(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeAM, self._true)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def disableWaveformChannelAM(self, channel_index=1, verbose=False):
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(channel_index - 1), self._AnalogOutNodeAM, self._false)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def getWaveformChannelInfo(self, channel_index=-1):
        number_channel = c_int()
        self.dwf.FDwfAnalogOutCount(self.hdwf, byref(number_channel))
        if channel_index == -1:
            channel_iter = [1, 2]
        else:
            channel_iter = [channel_index]

        for channel in channel_iter:
            print('-' * 50)
            print('Channel %d Configuration:' % channel)

            # read idle
            node_idle_read = c_int()
            self.dwf.FDwfAnalogOutIdleGet(self.hdwf, c_int(channel - 1), byref(node_idle_read))
            if node_idle_read.value == self._DwfAnalogOutIdleDisable.value:
                node_idle_read = 'Disable'
            elif node_idle_read.value == self._DwfAnalogOutIdleOffset.value:
                node_idle_read = 'Offset'
            elif node_idle_read.value == self._DwfAnalogOutIdleInitial.value:
                node_idle_read = 'Initial'
            else:
                node_idle_read = 'Unknown'

            print('\tIdle Output: [' + node_idle_read + '].')
            print('\tOutput Mode:')
            print("\t\t{:<10} {:<10} {:<20} {:<10} {:<10} {:<10} {:<10}"
                  .format('Node', 'Function', 'Frequency', 'Amplitude', 'Offset', 'Symmetry', 'Phase'))
            self._getWaveformChannelNodeInfo(channel_index=channel, node=self._AnalogOutNodeCarrier)
            self._getWaveformChannelNodeInfo(channel_index=channel, node=self._AnalogOutNodeFM)
            self._getWaveformChannelNodeInfo(channel_index=channel, node=self._AnalogOutNodeAM)

    def _getWaveformChannelNodeInfo(self, channel_index, node):
        if node.value == self._AnalogOutNodeCarrier.value:
            node_name = 'Carrier'
        elif node.value == self._AnalogOutNodeFM.value:
            node_name = 'FM'
        elif node.value == self._AnalogOutNodeAM.value:
            node_name = 'AM'
        else:
            node_name = 'Unknown'

        # read enable status
        node_enable_read = c_int()
        self.dwf.FDwfAnalogOutNodeEnableGet(self.hdwf, c_int(channel_index - 1), node, byref(node_enable_read))

        if node_enable_read.value == self._true.value:
            node_enable_read = 'Enabled'
            # read function
            node_function_read = c_ubyte()
            self.dwf.FDwfAnalogOutNodeFunctionGet(self.hdwf, c_int(channel_index - 1), node, byref(node_function_read))

            if node_function_read.value == self._funcDC.value:
                node_function_read = 'DC'
            elif node_function_read.value == self._funcSine.value:
                node_function_read = 'Sine'
            elif node_function_read.value == self._funcSquare.value:
                node_function_read = 'Square'
            elif node_function_read.value == self._funcTriangle.value:
                node_function_read = 'Triangle'
            elif node_function_read.value == self._funcRampUp.value:
                node_function_read = 'Ramp-Up'
            elif node_function_read.value == self._funcRampDown.value:
                node_function_read = 'Ramp-Down'
            elif node_function_read.value == self._funcNoise.value:
                node_function_read = 'RandomNoise'
            # elif node_function_read.value==self._funcPulse.value:
            # elif node_function_read.value==self._funcTrapezium.value:
            # elif node_function_read.value==self._funcSinePower.value:
            elif node_function_read.value == self._funcCustom.value:
                node_function_read = 'Custom'
            # elif node_function_read.value==self._funcPlay.value:
            else:
                node_function_read = 'Unknown'

            # read frequency
            node_frequency_read = c_double()
            node_frequency_max = c_double()
            node_frequency_min = c_double()
            self.dwf.FDwfAnalogOutNodeFrequencyInfo(self.hdwf, c_int(channel_index - 1), node,
                                                    byref(node_frequency_min), byref(node_frequency_max))
            self.dwf.FDwfAnalogOutNodeFrequencyGet(self.hdwf, c_int(channel_index - 1), node,
                                                   byref(node_frequency_read))
            node_frequency_read = node_frequency_read.value
            node_frequency_max = node_frequency_max.value
            node_frequency_min = node_frequency_min.value

            # read amplitude
            node_amplitude_read = c_double()
            node_amplitude_max = c_double()
            node_amplitude_min = c_double()
            self.dwf.FDwfAnalogOutNodeAmplitudeInfo(self.hdwf, c_int(channel_index - 1), node,
                                                    byref(node_amplitude_min), byref(node_amplitude_max))
            self.dwf.FDwfAnalogOutNodeAmplitudeGet(self.hdwf, c_int(channel_index - 1), node,
                                                   byref(node_amplitude_read))
            node_amplitude_read = node_amplitude_read.value
            node_amplitude_max = node_amplitude_max.value
            node_amplitude_min = node_amplitude_min.value

            # read offset
            node_offset_read = c_double()
            node_offset_max = c_double()
            node_offset_min = c_double()
            self.dwf.FDwfAnalogOutNodeOffsetInfo(self.hdwf, c_int(channel_index - 1), node,
                                                 byref(node_offset_min), byref(node_offset_max))
            self.dwf.FDwfAnalogOutNodeOffsetGet(self.hdwf, c_int(channel_index - 1), node, byref(node_offset_read))
            node_offset_read = node_offset_read.value
            node_offset_max = node_offset_max.value
            node_offset_min = node_offset_min.value

            # read symmetry
            node_symmetry_read = c_double()
            node_symmetry_max = c_double()
            node_symmetry_min = c_double()
            self.dwf.FDwfAnalogOutNodeSymmetryInfo(self.hdwf, c_int(channel_index - 1), node,
                                                   byref(node_symmetry_min), byref(node_symmetry_max))
            self.dwf.FDwfAnalogOutNodeSymmetryGet(self.hdwf, c_int(channel_index - 1), node, byref(node_symmetry_read))
            node_symmetry_read = node_symmetry_read.value
            node_symmetry_max = node_symmetry_max.value
            node_symmetry_min = node_symmetry_min.value

            # read phase
            node_phase_read = c_double()
            node_phase_max = c_double()
            node_phase_min = c_double()
            self.dwf.FDwfAnalogOutNodePhaseInfo(self.hdwf, c_int(channel_index - 1), node,
                                                byref(node_phase_min), byref(node_phase_max))
            self.dwf.FDwfAnalogOutNodePhaseGet(self.hdwf, c_int(channel_index - 1), node, byref(node_phase_read))
            node_phase_read = node_phase_read.value
            node_phase_max = node_phase_max.value
            node_phase_min = node_phase_min.value

            print("\t\t{:<10} {:<10} {:<20} {:<10} {:<10} {:<10} {:<10}"
                  .format('[' + node_name + ']', '[' + node_function_read + ']',
                          '[%.2e(%.1fus)]' % (node_frequency_read, 1 / node_frequency_read * 1e6),
                          '[%.2f]' % node_amplitude_read, '[%.2f]' % node_offset_read,
                          '[%.2f]' % node_symmetry_read, '[%.2f]' % node_phase_read))
        else:
            node_enable_read = 'Disabled'
            print("\t\t{:<10} {:<10}".format('[' + node_name + ']', '[' + node_enable_read + ']'))

    def setWaveformChannelCarrierWave(self, channel_index=1, func_name='Sine', freq=290e3, peak2peak=3.0,
                                      if_above_0=True, offset=0.0, symmetry=50, phase=0.0, idle_mode=0, verbose=False):
        # _DwfAnalogOutIdleDisable = c_int(0)
        # _DwfAnalogOutIdleOffset = c_int(1)
        # _DwfAnalogOutIdleInitial = c_int(2)
        self.dwf.FDwfAnalogOutIdleSet(self.hdwf, c_int(channel_index - 1), c_int(idle_mode))

        self._setWaveformChannelNodeWave(channel_index=channel_index, node=self._AnalogOutNodeCarrier,
                                         func_name=func_name, freq=freq, peak2peak=peak2peak,
                                         if_above_0=if_above_0, offset=offset, symmetry=symmetry, phase=phase)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def setWaveformChannelFMWave(self, channel_index=1, func_name='Sine', freq=290e3, peak2peak=3.0,
                                 if_above_0=True, offset=0, symmetry=50, phase=0, verbose=False):

        self._setWaveformChannelNodeWave(channel_index=channel_index, node=self._AnalogOutNodeFM,
                                         func_name=func_name, freq=freq, peak2peak=peak2peak,
                                         if_above_0=if_above_0, offset=offset, symmetry=symmetry, phase=phase)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def setWaveformChannelAMWave(self, channel_index=1, func_name='Sine', freq=290e3, peak2peak=3.0,
                                 if_above_0=True, offset=0.0, symmetry=50, phase=0.0, verbose=False):

        self._setWaveformChannelNodeWave(channel_index=channel_index, node=self._AnalogOutNodeAM,
                                         func_name=func_name, freq=freq, peak2peak=peak2peak,
                                         if_above_0=if_above_0, offset=offset, symmetry=symmetry, phase=phase)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def _setWaveformChannelNodeWave(self, channel_index, node, func_name, freq, peak2peak,
                                    if_above_0, offset, symmetry, phase):
        amplitude = peak2peak / 2.0
        if if_above_0 is True:
            offset = amplitude

        if func_name.lower() == 'dc':
            func = self._funcDC
        elif func_name.lower() == 'sine':
            func = self._funcSine
        elif func_name.lower() == 'square':
            func = self._funcSquare
        elif func_name.lower() == 'triangle':
            func = self._funcTriangle
        elif func_name.lower() == 'rampup':
            func = self._funcRampUp
        elif func_name.lower() == 'rampdown':
            func = self._funcRampDown
        elif func_name.lower() == 'noise':
            func = self._funcNoise
        elif func_name.lower() == 'custom':
            func = self._funcCustom
        else:
            func = self._funcDC

        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, c_int(channel_index - 1), node, func)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, c_int(channel_index - 1), node, c_double(freq))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, c_int(channel_index - 1), node, c_double(amplitude))
        self.dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, c_int(channel_index - 1), node, c_double(offset))
        self.dwf.FDwfAnalogOutNodeSymmetrySet(self.hdwf, c_int(channel_index - 1), node, c_double(symmetry))
        self.dwf.FDwfAnalogOutNodePhaseSet(self.hdwf, c_int(channel_index - 1), node, c_double(phase))
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, c_int(channel_index - 1), c_int(3))  # apply

    def setWaveformChannelNodeCustomData(self, channel_index=1, node=2, data=None):
        sample_size_min = c_uint()
        sample_size_max = c_uint()

        if node == 0:
            node = self._AnalogOutNodeCarrier
        elif node == 1:
            node = self._AnalogOutNodeFM
        elif node == 2:
            node = self._AnalogOutNodeAM

        self.dwf.FDwfAnalogOutNodeDataInfo(self.hdwf, c_int(channel_index - 1), node, byref(sample_size_min),
                                           byref(sample_size_max))

        if len(data) > sample_size_max.value or len(data) < sample_size_min.value:
            raise ValueError('The size of custom data is %d, outside the range of node %d: [%d,%d].' % (
                len(data), node, sample_size_min.value, sample_size_max.value))

        samples = (c_double * len(data))(*data)
        self.dwf.FDwfAnalogOutNodeDataSet(self.hdwf, c_int(channel_index - 1), node, samples, c_int(len(data)))

    def setWaveformTemplateFrequencySweep(self, channel_index=1, start_freq=200e3, stop_freq=300e3, sweep_time_us=24000,
                                          peak2peak=2,
                                          if_above_0=False, offset=0, idle_mode=0, verbose=False):
        hzStart = start_freq
        hzStop = stop_freq
        hzMid = (hzStart + hzStop) / 2

        self.enableWaveformChannelCarrier(channel_index=channel_index)
        self.setWaveformChannelCarrierWave(channel_index=channel_index, func_name='Sine', freq=hzMid,
                                           peak2peak=peak2peak, if_above_0=if_above_0, offset=offset,
                                           idle_mode=idle_mode)
        self.enableWaveformChannelFM(channel_index=channel_index)
        self.setWaveformChannelFMWave(channel_index=channel_index, func_name='RampUp',
                                      freq=1 / (sweep_time_us / 1e6),
                                      peak2peak=100.0 * (hzStop - hzStart) / hzMid,
                                      if_above_0=False,
                                      offset=0,
                                      symmetry=100)
        if verbose is True:
            self.getWaveformChannelInfo(channel_index=channel_index)

    def setWaveformTemplateCustomPulseModulatedSine(self, channel_index=1, sine_freq=290e3, peak2peak=2,
                                                    if_above_0=False, offset=0, idle_mode=0, pulse_width_list_us=None,
                                                    pulse_relative_delay_list_us=None, verbose=False):
        if isinstance(peak2peak, list) is True:  # if peak2peak is a list, then calculate the percentage for each pulse
            if len(peak2peak) != len(pulse_width_list_us):
                raise ValueError('peak2peak and pulse_width_list_us should have the same length.')
            peak2peak_list_percentage = np.array(peak2peak) / np.max(peak2peak)
            peak2peak = np.max(peak2peak)
        else:  # if peak2peak is a number, then assign the percentage to 1 for each pulse
            peak2peak_list_percentage = np.ones(len(pulse_width_list_us))

        if isinstance(sine_freq, list) is True:  # if sine_freq is a list, then calculate the percentage for each pulse
            if len(sine_freq) != len(pulse_width_list_us):
                raise ValueError('sine_freq and pulse_width_list_us should have the same length.')
            sine_freq_list_percentage = np.array(sine_freq) / np.max(sine_freq)
            sine_freq = np.max(sine_freq)
            fm_flag = True
            self.enableWaveformChannelFM(channel_index=channel_index)
        else:  # if sine_freq is a number, then assign the percentage to 1 for each pulse
            sine_freq_list_percentage = np.ones(len(pulse_width_list_us))
            fm_flag = False

        self.enableWaveformChannelCarrier(channel_index=channel_index)
        self.enableWaveformChannelAM(channel_index=channel_index)

        self.setWaveformChannelCarrierWave(channel_index=channel_index,
                                           func_name='Sine',
                                           freq=sine_freq,
                                           peak2peak=peak2peak,
                                           if_above_0=if_above_0,
                                           offset=offset,
                                           symmetry=50,
                                           phase=0,
                                           idle_mode=idle_mode,
                                           # _DwfAnalogOutIdleDisable = c_int(0)
                                           # _DwfAnalogOutIdleOffset = c_int(1)
                                           # _DwfAnalogOutIdleInitial = c_int(2)
                                           verbose=False)
        period = np.sum(pulse_relative_delay_list_us[1::]) + pulse_width_list_us[-1]
        sample_size = 2048
        amplitude_samples = self._generateCustomPulse(pulse_width_list_us=pulse_width_list_us,
                                                      pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                                      amplitude_list_percentage=peak2peak_list_percentage,
                                                      sample_size=sample_size)
        frequency_samples = self._generateCustomPulse(pulse_width_list_us=pulse_width_list_us,
                                                      pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                                      amplitude_list_percentage=sine_freq_list_percentage,
                                                      sample_size=sample_size)
        if verbose is True:
            self.getCustomPulseInfo(frequency=1 / (period / 1e6), pulse_width_list_us=pulse_width_list_us,
                                    pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                    data=amplitude_samples, type_name='amplitude')
            if fm_flag is True:
                self.getCustomPulseInfo(frequency=1 / (period / 1e6), pulse_width_list_us=pulse_width_list_us,
                                        pulse_relative_delay_list_us=pulse_relative_delay_list_us,
                                        data=frequency_samples, type_name='frequency')

        # setup FM waveform
        if fm_flag is True:
            self.setWaveformChannelFMWave(channel_index=channel_index,
                                          func_name='Custom',
                                          freq=1 / (period / 1e6),
                                          peak2peak=100,
                                          if_above_0=False,
                                          offset=-50,
                                          symmetry=50,
                                          phase=0,
                                          verbose=False)
            self.setWaveformChannelNodeCustomData(channel_index=channel_index, node=1, data=frequency_samples)

        # setup AM wave
        self.setWaveformChannelAMWave(channel_index=channel_index,
                                      func_name='Custom',
                                      freq=1 / (period / 1e6),
                                      peak2peak=100,
                                      if_above_0=False,
                                      offset=-50,
                                      symmetry=50,
                                      phase=0,
                                      verbose=verbose)
        self.setWaveformChannelNodeCustomData(channel_index=channel_index, node=2, data=amplitude_samples)


    @staticmethod
    def _generateCustomPulse(pulse_width_list_us, pulse_relative_delay_list_us, sample_size,
                             amplitude_list_percentage=None, if_change_at_end=True):
        if len(pulse_width_list_us) != len(pulse_relative_delay_list_us):
            raise ValueError
        if amplitude_list_percentage is None:
            amplitude_list_percentage = np.ones(len(pulse_width_list_us))
        else:
            if len(amplitude_list_percentage) != len(pulse_width_list_us):
                raise ValueError
            else:
                amplitude_list_percentage = np.array(amplitude_list_percentage)
                amplitude_list_percentage = amplitude_list_percentage * 2 - 1

        data = []
        pulse_relative_delay_list_us = pulse_relative_delay_list_us.copy()

        pulse_relative_delay_list_us[0] = 0
        period = np.sum(pulse_relative_delay_list_us) + pulse_width_list_us[-1]

        pulse_absolute_delay_list_us = np.cumsum(pulse_relative_delay_list_us)

        pulse_end_list_index = np.round(
            np.add(pulse_width_list_us, pulse_absolute_delay_list_us) / period * sample_size, 0).astype(int).tolist()
        pulse_start_delay_list_index = np.round(pulse_absolute_delay_list_us / period * sample_size, 0).astype(
            int).tolist()

        if if_change_at_end is True:
            for i in range(len(pulse_start_delay_list_index) - 1):
                data.extend(
                    [amplitude_list_percentage[i]] * (pulse_end_list_index[i] - pulse_start_delay_list_index[i]))
                data.extend([-1] * (pulse_start_delay_list_index[i + 1] - pulse_end_list_index[i]))
            data.extend([amplitude_list_percentage[-1]] * (pulse_end_list_index[-1] - pulse_start_delay_list_index[-1]))
        else:
            for i in range(len(pulse_start_delay_list_index) - 1):
                data.extend(
                    [amplitude_list_percentage[i]] * (pulse_end_list_index[i] - pulse_start_delay_list_index[i]))
                fill_size = int((pulse_start_delay_list_index[i + 1] - pulse_end_list_index[i]) / 2)
                data.extend([amplitude_list_percentage[i]] * fill_size)
                data.extend(amplitude_list_percentage[i + 1] * (
                        pulse_start_delay_list_index[i + 1] - pulse_end_list_index[i] - fill_size))
            data.extend([amplitude_list_percentage[-1]] * (pulse_end_list_index[-1] - pulse_start_delay_list_index[-1]))

        if len(data) != sample_size:
            raise ValueError(len(data), sample_size)

        return data

    def getCustomPulseInfo(self, frequency, pulse_width_list_us, pulse_relative_delay_list_us, data,
                           type_name='amplitude'):
        pulse_relative_delay_list_us = pulse_relative_delay_list_us.copy()
        period = 1 / frequency
        data = np.array(data)
        index = np.where(data[:-1] != data[1:])[0]
        index = np.insert(index, 0, 0)
        index = np.append(index, len(data))
        timing_us = index / len(data) * period * 1e6

        initial_delay = pulse_relative_delay_list_us[0]
        pulse_relative_delay_list_us[0] = 0

        print('-' * 50)
        print('Custom Pulse Data Configuration: [{}]'.format(type_name))
        print('\tFrequency: [%.3eHz].' % frequency)
        print('\tPeriod: [%.1fus].' % (period * 1e6))
        print('\tSample Size: [%d].' % len(data))
        print('\t\t{:<15} {:<25} {:<25} {:<10}'.format('PulseIndex', 'StartTime', 'Width', 'EndTime'))
        for i in range(int(len(timing_us) / 2)):
            if i == 0:
                print('\t\t{:<15} {:<25} {:<25} {:<10}'.format(str(i + 1),
                                                               '[%.1fus]' % (timing_us[int(i * 2)] + initial_delay),
                                                               '[%.1fus(ER:%.1fus)]' % (
                                                                   timing_us[i * 2 + 1] - timing_us[
                                                                       i * 2], timing_us[i * 2 + 1] - timing_us[
                                                                       i * 2] - pulse_width_list_us[i]),
                                                               '[%.1fus]' % (
                                                                       timing_us[int(i * 2) + 1] + initial_delay)))
            else:
                print('\t\t{:<15} {:<25} {:<25} {:<10}'.format(str(i + 1),
                                                               '[%.1fus(ER:%.1fus)]' % (
                                                                   timing_us[i * 2] + initial_delay,
                                                                   timing_us[i * 2] -
                                                                   timing_us[
                                                                       (i - 1) * 2] -
                                                                   pulse_relative_delay_list_us[
                                                                       i]),
                                                               '[%.1fus(ER:%.1fus)]' % (
                                                                   timing_us[i * 2 + 1] - timing_us[
                                                                       i * 2], timing_us[i * 2 + 1] - timing_us[
                                                                       i * 2] - pulse_width_list_us[i]),
                                                               '[%.1fus]' % (timing_us[i * 2 + 1] + initial_delay)))
