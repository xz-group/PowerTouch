from SuperCharge.TouchMonitorFlutter.TouchMonitor import TouchMonitor
import time

monitor = TouchMonitor()
monitor.initiateServer()
monitor.startServer()
time.sleep(5)
monitor.stopServer()