from SuperCharge.AnalogDiscovery.LogicAnalyzer import LogicAnalyzer
from SuperCharge.AnalogDiscovery.Oscilloscope import Oscilloscope
from SuperCharge.AnalogDiscovery.Device import AnalogDiscovery
import matplotlib.pyplot as plt

# phone = Nexus5()
# phone.setupOscilloscope()
# phone.startOscilloscope()
# phone.monitorOscilloscope()

ad2 = AnalogDiscovery()
fs = 900e3
trigger_level_mv = 1000

"""
Scope
"""
scope = Oscilloscope(ad2)
scope.setScopeSamplingFrequency(frequency=fs, verbose=True)
scope.setScopeBufferSize(size=8192, verbose=True)
scope.setScopeTriggerTimeout(timeout_s=3, verbose=True)

# set trigger
scope.setScopeTriggerLevel(level_mV=trigger_level_mv, verbose=True)
scope.setScopeTriggerHysteresis(hyst_mV=0, verbose=True)
scope.setScopeTriggerOnChannel(channel=1, verbose=True)
scope.setScopeTriggerEdge(if_RisingPositive=True, verbose=True)
scope.setScopeTriggerFilter(verbose=True)
scope.setScopeTriggerPosition(position_ms=4.2, verbose=True)
scope.setScopeTriggerHoldOff(holdoff_ms=0, verbose=True)

# set channel
scope.enableScopeChannel(channel_index=1, verbose=True)
scope.setScopeChannelRange(peak2peak=0.2, verbose=True)
scope.enableScopeChannel(channel_index=2, verbose=True)
scope.setScopeChannelRange(peak2peak=2, verbose=True)

"""
Logic analyzer
"""
logic = LogicAnalyzer(ad2)
logic.setAnalyzerBufferSize(verbose=True)
logic.setAnalyzerClockFrequency(frequency=fs / 2, verbose=True)
logic.setAnalyzerTriggerTimeout(timeout_s=3, verbose=True)
logic.setAnalyzerTriggerSource(if_analogin=True, if_RisingPositive=True, edge_rise_channels=0, verbose=True)
logic.setAnalyzerTriggerPosition(position_ms=4.2, verbose=True)
logic.setAnalyzerAcquisitionMode(mode=0, verbose=True)

"""
Plot
"""
scope.setScopeState(if_reconfigure=True, if_start=True)
logic.setAnalyzerState(if_reconfigure=True, if_start=True)

plt.ion()
fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex='all')
while True:
    state, trigger_flag = scope.getScopeState(verbose=False)
    state_l, trigger_flag_l = logic.getAnalyzerState(verbose=False)
    if state == 'Done':
        time1, data1 = scope.readScopeChannelData(channel_index=1)
        time2, data2 = scope.readScopeChannelData(channel_index=2)
        time3, data3 = logic.readAnalyzerData()
        # plt.gca().cla()  # optionally clear axes

        ax1.clear()
        ax1.plot(time1 * 1000, data1 * 1000)

        ax1.set_title('Channel 1, ' + trigger_flag)
        # ax1.set_xlabel('Time(ms)')
        ax1.set_ylabel('Voltage(mV)')
        ax1.set_xlim([time1[0] * 1000, time1[-1] * 1000])
        # ax1.set_ylim([-60, 60])
        ax1.axvline(x=0, color='r', linestyle='--')

        ax2.clear()
        ax2.plot(time2 * 1000, data2 * 1000)
        # ax2.set_title('Channel 2')
        # ax2.set_xlabel('Time(ms)')
        ax2.set_ylabel('Channel2: Voltage(mV)')
        # ax2.set_xlim([time2[0] * 1000, time2[-1] * 1000])
        # ax2.set_ylim([-60, 60])
        ax2.axvline(x=0, color='r', linestyle='--')

        # ax3.clear()
        # ax3.plot(time3 * 1000, data3)
        # ax3.set_title('Logic Analyzer')
        # ax3.set_xlabel('Time(ms)')
        # ax3.set_ylabel('Voltage')
        # ax3.set_xlim([time3[0] * 1000, time3[-1] * 1000])
        # ax3.axvline(x=0, color='r', linestyle='--')

        plt.draw()
        plt.pause(0.05)
        plt.tight_layout()
