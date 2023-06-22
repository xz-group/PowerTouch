from SuperCharge.MultiTouchMonitorADB.MultiTouchMonitor import plotMultiTouchTiming
import os

# path = 'D:\Data/20220204-122418_FreqSweep_Nexus5_PiezoDriveMX200_40V_50kHz_500kHz_1kHz_3s/280000Hz\Row15\Repeat2'
path = 'H:\SuperCharge\data\processed/20220201-144538_FreqSweep_Nexus5_PiezoDriveMX200_60V_50kHz_500kHz_1kHz_3s/280000Hz\Row15\Repeat3'

timestamp_file = os.path.join(path, 'trigger_timestamps.csv')
click_file = os.path.join(path, 'click.csv')
non_click_file = os.path.join(path, 'nonclick.csv')

plotMultiTouchTiming(timestamp_file, click_file, non_click_file)
