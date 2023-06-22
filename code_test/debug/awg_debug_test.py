from SuperCharge.AnalogDiscovery.WaveformGenerator import WaveformGenerator
from SuperCharge.AnalogDiscovery.Device import AnalogDiscovery

ad2 = AnalogDiscovery()
waveform = WaveformGenerator(ad2)

waveform.setWaveformChannelTriggerSource(channel_index=1, if_analogin=False, if_RisingPositive=True,
                                         if_selftrigger=False,
                                         verbose=True)
waveform.setWaveformChannelRunInfo(channel_index=1, runtime_us=0, delay_us=0, repeat_number=0, if_repeattrigger=True,
                                   verbose=True)
# waveform.enableWaveformChannelCarrier(channel_index=1)
# waveform.setWaveformChannelCarrierWave(channel_index=1, if_above_0=False)
# waveform.setWaveformTemplateFrequencySweep(verbose=True)
# waveform.enableWaveformChannelFM(channel_index=-1)
# waveform.getWaveformChannelInfo(channel_index=1)
waveform.setWaveformTemplateCustomPulseModulatedSine(pulse_relative_delay_list_us=[1e3, 8.3e3],
                                                     pulse_width_list_us=[200, 200], verbose=True)
# waveform.runWaveformChannel(channel_index=1, verbose=True)
# time.sleep(5)
# waveform.stopWaveformChannel(channel_index=1)
