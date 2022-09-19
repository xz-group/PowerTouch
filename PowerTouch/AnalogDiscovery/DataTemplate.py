import pandas as pd
import numpy as np
import re
from datetime import datetime


class AnalogDiscoveryDataFrame:
    def __init__(self, timestamp=None, analog_time=None, analog_ch1=None,
                 analog_ch2=None, digital_time=None,
                 digital_channels=None, trigger_flag=None,
                 trigger_count=None, trigger_rate=None):
        self.timestamp = timestamp
        self.trigger_flag = trigger_flag
        self.analog_time = analog_time
        self.digital_time = digital_time
        self.analog_channel_1 = analog_ch1
        self.analog_channel_2 = analog_ch2
        self.digital_channels = digital_channels
        self.trigger_count = trigger_count
        self.trigger_rate = trigger_rate

    def writeAnalogDiscoveryDataFrame(self, save_path='./'):
        data_analog = {"analog_time": self.analog_time,
                       "analog_channel_1": self.analog_channel_1,
                       "analog_channel_2": self.analog_channel_2}
        data_digital = {"digital_time": self.digital_time,
                        "digital_channel_0": self.digital_channels[0],
                        "digital_channel_1": self.digital_channels[1]}

        df_analog = pd.DataFrame(data_analog)
        df_digital = pd.DataFrame(data_digital)

        filename = [str(self.timestamp),
                    'TC%d' % self.trigger_count,
                    self.trigger_flag,
                    'TR%.2f' % self.trigger_rate]
        filename = '_'.join(filename)
        filename = filename.replace(':', ';')
        filename = filename.replace('.', 'p')
        df_analog.to_csv(save_path + filename + '_Analog' + '.csv', encoding='utf-8', index=False)
        df_digital.to_csv(save_path + filename + '_Digital' + '.csv', encoding='utf-8', index=False)

    def writeAnalogDiscoveryDataFrame_Combined(self):
        data_analog_ch1 = {"time": self.analog_time, "data": self.analog_channel_1, "type": "Analog_CH1",
                           'tc': self.trigger_count, 'tr': self.trigger_rate, 'tf': self.trigger_flag}
        data_analog_ch2 = {"time": self.analog_time, "data": self.analog_channel_2, "type": "Analog_CH2",
                           'tc': self.trigger_count, 'tr': self.trigger_rate, 'tf': self.trigger_flag}

        data_digital_ch0 = {"time": self.digital_time, "data": self.digital_channels[0], "type": "Digital_CH0",
                            'tc': self.trigger_count, 'tr': self.trigger_rate, 'tf': self.trigger_flag}
        data_digital_ch1 = {"time": self.digital_time, "data": self.digital_channels[1], "type": "Digital_CH1",
                            'tc': self.trigger_count, 'tr': self.trigger_rate, 'tf': self.trigger_flag}

        df_analog_ch1 = pd.DataFrame(data_analog_ch1)
        df_analog_ch2 = pd.DataFrame(data_analog_ch2)
        df_digital_ch0 = pd.DataFrame(data_digital_ch0)
        df_digital_ch1 = pd.DataFrame(data_digital_ch1)

        return pd.concat([df_analog_ch1, df_analog_ch2, df_digital_ch0, df_digital_ch1], ignore_index=True)

    def readAnalogDiscoveryDataFrame(self, read_path='./', analog_filename='', digital_filename=''):
        analog_filename_list = re.split(r'[_.]', analog_filename)
        digital_filename_list = re.split(r'[_.]', digital_filename)
        for i in range(len(analog_filename_list) - 2):
            if analog_filename_list[i] != digital_filename_list[i]:
                raise ValueError

        # read timestamp
        self.timestamp = datetime.strptime(analog_filename_list[0], '%Y-%m-%d %H;%M;%Sp%f')

        # read trigger count
        self.trigger_count = int(re.findall(r'\d+', analog_filename_list[1])[0])

        # read trigger flag
        self.trigger_flag = analog_filename_list[2]

        # read trigger rate
        analog_filename_list[3] = analog_filename_list[3].replace('p', '.')
        self.trigger_rate = float(re.findall(r'[\d.]+', analog_filename_list[3])[0])

        # read data
        df_analog = pd.read_csv(read_path + analog_filename, encoding='utf-8')
        self.analog_time = df_analog['analog_time'].to_numpy()
        self.analog_channel_1 = df_analog['analog_channel_1'].to_numpy()
        self.analog_channel_2 = df_analog['analog_channel_2'].to_numpy()

        df_digital = pd.read_csv(read_path + digital_filename, encoding='utf-8')
        self.digital_time = df_digital['digital_time'].to_numpy()
        self.digital_channels = np.array(
            [df_digital['digital_channel_0'].tolist(), df_digital['digital_channel_1'].tolist()])
