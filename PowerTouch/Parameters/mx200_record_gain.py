from PowerTouch.AttackTemplate.Template import SmartPhoneTemplate
import numpy as np

start_freq_lim = 50e3
stop_freq_lim = 500e3
step = 1e3
peak2peak = 60
expected_gian = 20

freq = np.arange(start_freq_lim, stop_freq_lim, step)
np.append(freq, stop_freq_lim)

phone = SmartPhoneTemplate(if_enableSmartPhone=False)

csv_file = open("max200_gain.csv", "w")
csv_file.write("Frequency,ExpectedPeak2Peak,RealPeak2Peak,RealGain\n")
realPeak2peak = 0

for i in range(len(freq)):
    phone.setupWaveformGeneratorBasic(if_analogin=True, if_RisingPositive=True, if_selftrigger=True, verbose=False,
                                      attack_width_us=0, attack_delay_us=0, peak2peak=peak2peak / expected_gian,
                                      if_above_0=False, offset=0,
                                      noise_frequency=freq[i], function_name='Sine', channel_index=2,
                                      symmetry=50, phase=0.0, idle_mode=0)
    phone.startWaveformGenerator(channel_index=2)

    realPeak2peak = input('Get the real peak2peak from OSC:') or realPeak2peak
    phone.stopWaveformGenerator(channel_index=2)
    realPeak2peak = float(realPeak2peak)
    realGain = realPeak2peak / (peak2peak / expected_gian)
    # print("Frequency\tExpectedPeak2Peak\tRealPeak2Peak\tRealGain")
    string = '%.1f,%.2f,%.2f,%.5f\n' % (freq[i], peak2peak, realPeak2peak, realGain)
    print(string)
    csv_file.write(string)

csv_file.close()
