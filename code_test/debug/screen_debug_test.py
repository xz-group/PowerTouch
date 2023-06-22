from SuperCharge.AttackTemplate.Nexus5 import Nexus5
import time
import matplotlib.pyplot as plt

def gen_file_name(file_index=1):
    event_file_path = 'D:/Code/SuperCharge/event%d.txt' % file_index
    return event_file_path

# path = 'D:\Data/20220217-103607_Nexus5_1_RowSwipe_Consecutive_PiezoDriveMX200_60V_48ms_96ms_16ms_250kHz_350kHz_5kHz_RowConfig4_TC500/300000Hz/80ms\Row5_to_Row22\Repeat5'

phone = Nexus5(if_enableAD2=False)
phone.screen.initiatePhoneCommunication(if_shell_communication=False)
time.sleep(5)
phone.screen.terminatePhoneCommunication(adb_server_pid=4880)
phone.screen.parseEventFile(event_file_path=gen_file_name(0))
phone.screen.writeMultiTouchRecord2CSV()
# phone.screen.readCSV2MultiTouchRecord(read_path=path+'/', filename='events')
phone.data_analyzer.addTouchScreenDataFrame(phone.screen.slots, phone.screen.timestamps)
phone.data_analyzer.compileScreenAnimation(persistence=True, replay_interval_ms=10, if_real_time=False)
plt.show()

# phone.monitorScreen_readFromEventFile()
# phone.monitorScreen_compileAnimation()


# phone.screen.compileMultiTouchStatistics()
