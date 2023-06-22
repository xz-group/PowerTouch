from PowerTouch.AttackTemplate.Template import SmartPhoneTemplate
import numpy as np


class Nexus5(SmartPhoneTemplate):
    def __init__(self, if_enableAD2=True, if_enableSmartPhone=True, verbose=True):
        self.INITIAL_DELAY_US = 430
        self.SCAN_PULSE_US = 62
        self.SCAN_DELAY_US = 213.6
        self.FRAME_RATE = 120
        self.NUM_OF_ROWS = 27
        self.NUM_OF_COLS = 10
        self.SCAN_SENSE_WIDTH_US = self.SCAN_DELAY_US / self.NUM_OF_COLS
        SmartPhoneTemplate.__init__(self, if_enableAD2=if_enableAD2, if_enableSmartPhone=if_enableSmartPhone,
                                    verbose=verbose)

    def monitorAD2_compileAnimation(self, if_real_time=False, replay_interval_ms=0, frame_resolution_ms=1):
        marker_pulse_start_position = np.arange(self.INITIAL_DELAY_US,
                                                self.INITIAL_DELAY_US + 27 * (self.SCAN_DELAY_US + self.SCAN_PULSE_US),
                                                self.SCAN_PULSE_US + self.SCAN_DELAY_US)
        marker_pulse_width = self.SCAN_PULSE_US + self.SCAN_DELAY_US
        self.data_analyzer.compileAD2Animation(if_real_time=if_real_time, replay_interval_ms=replay_interval_ms,
                                               frame_resolution_ms=frame_resolution_ms,
                                               marker_pulse_start_position_ms=marker_pulse_start_position / 1e3,
                                               marker_pulse_width_ms=marker_pulse_width / 1e3)

    def setupAttackSinglePulse_byRow(self, target_row=13, verbose=True, freq=290e3, peak2peak=5, if_above_0=False,
                                     noise_channel=1, scope_trigger_holdoff_ms=10, scope_trigger_level_mv=30,
                                     additional_delay_us=0, attack_width_us=None):
        if attack_width_us is None:
            attack_width_us = self.SCAN_PULSE_US

        delay_us = self.INITIAL_DELAY_US + (self.SCAN_DELAY_US + self.SCAN_PULSE_US) * (
                target_row - 1) + additional_delay_us  # + self.SCAN_PULSE_US
        self.setupAttackSinglePulse(scope_trigger_level_mv=scope_trigger_level_mv,
                                    hysteresis_factor=0.8,
                                    sampling_frequency=800e3,
                                    scope_trigger_holdoff_ms=scope_trigger_holdoff_ms,
                                    verbose=verbose,
                                    scope_position_ms=4.5,
                                    attack_width_us=attack_width_us,
                                    relay_guard_us=500,
                                    relay_response_time=500,
                                    attack_delay_us=delay_us,
                                    noise_peak2peak=peak2peak,
                                    noise_frequency=freq,
                                    if_above_0=if_above_0, noise_channel=noise_channel)

    def setupAttackMultiplePulsesConsecutiveFrames_byRow(self,
                                                         scope_trigger_level_mv=30,
                                                         sampling_frequency=800e3,
                                                         scope_trigger_holdoff_ms=0.0,
                                                         verbose=True,
                                                         scope_position_ms=4.7,
                                                         row_list=None,
                                                         frame_index_difference=1,
                                                         additional_delay_us=0,
                                                         attack_pulse_width=None,
                                                         relay_guard_us=500,
                                                         relay_response_time=500,
                                                         noise_peak2peak=5,
                                                         noise_frequency=290e3,
                                                         hysteresis_factor=0.8,
                                                         channel_index=1,
                                                         if_above_0=True):
        if row_list is None:
            row_list = [5, 25]

        delay_list_us = []
        for i in range(len(row_list)):
            if i == 0:
                delay_list_us.append(self.INITIAL_DELAY_US + (self.SCAN_DELAY_US + self.SCAN_PULSE_US) * (
                        row_list[0] - 1) + additional_delay_us)  # + self.SCAN_PULSE_US
            else:
                delay_list_ = frame_index_difference / self.FRAME_RATE * 1e6 + (row_list[i] - row_list[i - 1]) * (
                        self.SCAN_DELAY_US + self.SCAN_PULSE_US)
                if delay_list_ <= 0:
                    raise ValueError(', '.join(row_list.append(str(frame_index_difference))))
                else:
                    delay_list_us.append(delay_list_)

        attack_delay_list_us = delay_list_us
        if attack_pulse_width is None:
            attack_width_list_us = [self.SCAN_PULSE_US] * len(row_list)
        else:
            attack_width_list_us = attack_pulse_width

        self.setupPowerSupply(voltage=5, verbose=verbose)
        self.startPowerSupply()

        self.setupOscilloscope(fs=sampling_frequency,
                               trigger_level_mv=scope_trigger_level_mv,
                               holdoff_ms=scope_trigger_holdoff_ms,
                               position_ms=scope_position_ms,
                               hysteresis_factor=hysteresis_factor,
                               verbose=verbose)
        self.setupLogicAnalyzer(fs=sampling_frequency / 2,
                                if_analogin=True,
                                edge_rise_channels=0,
                                position_ms=scope_position_ms,
                                verbose=verbose)
        self.setupWaveformGeneratorCustomModulation(if_analogin=True, if_RisingPositive=True, if_selftrigger=False,
                                                    attack_width_list_us=attack_width_list_us,
                                                    attack_delay_list_us=attack_delay_list_us,
                                                    peak2peak=noise_peak2peak, if_above_0=if_above_0, offset=0,
                                                    noise_frequency=noise_frequency,
                                                    idle_mode=0,
                                                    channel_index=channel_index,
                                                    verbose=verbose)
        self.setupPatternGeneratorCustom(if_analogin=True, if_RisingPositive=True, if_selftrigger=False,
                                         verbose=verbose,
                                         attack_width_list_us=attack_width_list_us,
                                         attack_delay_list_us=attack_delay_list_us,
                                         relay_guard_us=relay_guard_us,
                                         relay_response_time_us=relay_response_time)
