from SuperCharge.AttackTemplate.Nexus5 import Nexus5

phone = Nexus5()
phone.chargePhoneIfNeeded(low_threshold=98,high_threshold=100)
# phone.startScreen(verbose=True)
# phone.setupPowerSupply()
# phone.startPowerSupply()
# phone.pattern.setPatternConstantHigh(channel_index=[2,3])
# input()
# phone.setupAttackSinglePulse_byRow(target_row=23)
# phone.runAll()
# phone.monitorAD2_saveData_byRunTime(runtime=1, verbose=True)
# phone.stopAll()
# #
# phone.data_analyzer.writeAnalogDiscoveryDataFrameSeries()
# phone.data_analyzer.readAnalogDiscoveryDataFrame()
# phone.data_analyzer.compileAD2Animation(replay_interval_ms=0)
# phone.monitorAD2_compileAnimation(replay_interval_ms=0, frame_resolution_ms=1, if_real_time=False)
#
# phone.monitorScreen_readFromEventFile()
# # phone.monitorScreen_compileAnimation(replay_interval_ms=100, frame_resolution_ms=10, if_real_time=False,
# #                                      persistence=False)
# phone.monitorScreen_compileAnimation(replay_interval_ms=100, frame_resolution_ms=10, if_real_time=False,
#                                      persistence=True)

# phone.data_analyzer.compileAllAnimation(replay_interval_ms=1, persistence=True)
