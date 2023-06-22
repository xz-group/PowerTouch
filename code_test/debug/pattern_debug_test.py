from SuperCharge.AnalogDiscovery.PatternGenerator import PatternGenerator
from SuperCharge.AnalogDiscovery.Device import AnalogDiscovery

ad2 = AnalogDiscovery()
pattern = PatternGenerator(ad2)

# pattern.setPatternTriggerSource(if_analogin=False, if_RisingPositive=True, if_selftrigger=True, verbose=True)
# pattern.setPatternRepeat(repeat_number=0, if_repeattrigger=True, verbose=True)
# pattern.enablePatternChannel(channel_index=[0, 1], idle_state=-1, output_mode=0, verbose=True)
# pattern.setPatternWaveformCustom(channel_index=0,
#                                  pulse_relative_delay_list_us=[1e3, 800, 2e3],
#                                  pulse_width_list_us=[100, 150, 200], verbose=True)

# pattern.setPatternWaveformPulse(channel_index=0, pulse_state=1, pulse_width_us=100, delay_us=1.3e3, clock_divider=10,
#                                 verbose=False)
# pattern.setPatternWaveformPulse(channel_index=1, pulse_state=0, pulse_width_us=200, delay_us=1.25e3, clock_divider=10,
#                                 verbose=False)
# pattern.getPatternWaveformPulse()
# pattern.runPatternGenerator(verbose=True)
# time.sleep(10)
# pattern.stopPatternGenerator(verbose=True)
pattern.setPatternConstantHigh(channel_index=[0, 3])
input()
pattern.resetPatternConstant()

ad2.closeDevice()
