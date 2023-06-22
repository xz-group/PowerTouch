import os.path

import pandas as pd

from SuperCharge.Automation.GeneticAlgorithm import GeneticAlgorithm
import numpy as np
import statistics
from sklearn.metrics import mean_absolute_error
import random


def _genoType2phenoType(geno_type):
    pheno_type = [geno_type[0], geno_type[1], int(geno_type[2]), int(str(bin(int(geno_type[3])))[2:].count('1'))]

    # get delay and width list
    delay = []
    width = []
    pulse_num = int((len(geno_type) - len(pheno_type)) / 2)
    for i in range(pulse_num):
        delay.append(geno_type[4 + i * 2])
        width.append(geno_type[4 + i * 2 + 1])

    # get the pulse information
    pulse_enable_bits = str(bin(int(geno_type[3])))[2:]
    pulse_delay = []
    pulse_width = []
    delay_previous = 0
    for i in range(len(pulse_enable_bits)):
        if pulse_enable_bits[i] == '1':
            pulse_width.append(width[i])
            pulse_delay.append(delay[i] + delay_previous)
            delay_previous = 0
        else:
            delay_previous += delay[i]
    pheno_type.append(pulse_delay)
    pheno_type.append(pulse_width)

    return pheno_type


maximum_pulse_num = 5
minimum_pulse_num = 1

# Set the range of the gene space
pulse_enable_bits_maximum = 2 ** maximum_pulse_num
pulse_enable_bits_minimum = 2 ** maximum_pulse_num - 2 ** (maximum_pulse_num - minimum_pulse_num)
_gene_space = [{'low': 30, 'step': 1, 'high': 80},  # peak2peak voltage
               {'low': 100, 'step': 1, 'high': 400},  # frequency
               {'low': 2, 'step': 2, 'high': 16},  # attackPerNFrame
               {'low': pulse_enable_bits_minimum, 'step': 1, 'high': pulse_enable_bits_maximum},  # number of pulses
               {'low': 200, 'step': 1, 'high': 8000},  # pulse 1 delay
               {'low': 1, 'step': 1, 'high': 2000}]  # pulse 1 width
for i in range(maximum_pulse_num - 1):  # pulse i-th delay and width
    _gene_space.extend([{'low': 1, 'step': 1, 'high': 16000},  # pulse delay
                        {'low': 1, 'step': 1, 'high': 8000}])  # pulse width

geno_type = []
for dictionary in _gene_space:
    geno_type.append(random.choice(np.arange(dictionary['low'], dictionary['high'], dictionary['step'])))

_genoType2phenoType(geno_type)
