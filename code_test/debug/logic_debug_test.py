from SuperCharge.AnalogDiscovery.LogicAnalyzer import LogicAnalyzer
from SuperCharge.AnalogDiscovery.Device import AnalogDiscovery
import matplotlib.pyplot as plt

ad2 = AnalogDiscovery()
fs = 400e3
trigger_level_mv = 1000

"""
Logic analyzer
"""
logic = LogicAnalyzer(ad2)
logic.setAnalyzerBufferSize(size=4096, verbose=True)
logic.setAnalyzerClockFrequency(frequency=fs, verbose=True)
logic.setAnalyzerTriggerTimeout(timeout_s=1, verbose=True)
logic.setAnalyzerTriggerSource(if_analogin=False, if_RisingPositive=True, edge_rise_channels=0, verbose=True)
logic.setAnalyzerTriggerPosition(position_ms=4.2, verbose=True)
logic.setAnalyzerAcquisitionMode(mode=0, verbose=True)
logic.setAnalyzerDataFormat(verbose=True)

"""
Plot
"""
logic.setAnalyzerState(if_reconfigure=True, if_start=True)

plt.ion()

while True:
    state, trigger_flag = logic.getAnalyzerState(verbose=False)
    if state == 'Done':
        data3 = logic.readAnalyzerData(channel_number=2)
        time3 = logic.readAnalyzerDataTime()

        plt.gca().cla()
        plt.plot(time3 * 1000, data3[0])
        plt.title('Channel 1, ' + trigger_flag)
        plt.axvline(x=0, color='r', linestyle='--')
        plt.draw()
        plt.tight_layout()
        plt.pause(0.05)
