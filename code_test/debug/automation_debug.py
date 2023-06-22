from ga_exploration.RunExperiment import GetParameterRange_Nexus5

GetParameterRange_Nexus5(attack_per_N_frames=2,
                         pulse_delay_list_us=[4300],
                         pulse_width_list_us=[100])

# RunExperiment_Nexus5(generation=1, individual=5,
#                      peak2peak=40, frequency_kHz=280, attack_per_N_frames=2,
#                      number_of_pulses=1,
#                      pulse_delay_list_us=[4300],
#                      pulse_width_list_us=[100],
#                      adb_server_pid=20796,
#                      phone_index=1, trigger_count=200, repeat_number=3,scope_trigger_level_mv=25)
