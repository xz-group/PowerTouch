import pandas as pd


class PiezoDriveMX200Amplifier:
    def __init__(self):
        self.name = "PiezoDriveMX200"
        self.gain_list = pd.read_csv('D:/Code/SuperCharge/SuperCharge/Parameters/max200_gain.csv')
