from SuperCharge.AnalogDiscovery.WaveformGenerator import WaveformGenerator
from SuperCharge.AnalogDiscovery.Device import AnalogDiscovery

ad2 = AnalogDiscovery()
waveform = WaveformGenerator(ad2)

waveform.setWaveformChannelTriggerSource(channel_index=1, if_analogin=False, if_RisingPositive=True,
                                         if_selftrigger=True, verbose=True)
waveform.setWaveformChannelRunInfo(channel_index=1, runtime_us=0, delay_us=1e3, repeat_number=0, if_repeattrigger=True,
                                   verbose=True)
# waveform.enableWaveformChannelCarrier(channel_index=1)
# waveform.setWaveformChannelCarrierWave(channel_index=1, if_above_0=False)
# waveform.setWaveformTemplateFrequencySweep(verbose=True)
# waveform.enableWaveformChannelFM(channel_index=-1)
# waveform.getWaveformChannelInfo(channel_index=1)
waveform.setWaveformTemplateCustomPulseModulatedSine(channel_index=1, peak2peak=[4, 2, 3, 1],
                                                     sine_freq=[200e3, 100e3, 150e3, 50e3],
                                                     pulse_relative_delay_list_us=[1e3, 200, 200, 200],
                                                     pulse_width_list_us=[150, 150, 150, 150], verbose=True)
waveform.runWaveformChannel(channel_index=1, verbose=True)
# time.sleep(5)
# waveform.stopWaveformChannel(channel_index=1)
