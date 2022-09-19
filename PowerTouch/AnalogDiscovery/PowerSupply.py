from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants
from ctypes import c_double, byref, c_int


class PowerSupply(DwfConstants):
    def __init__(self, DwfInstance):
        self.dwf = DwfInstance.dwf
        self.hdwf = DwfInstance.hdwf
        self.voltage = 0

    def getPowerTitle(self, verbose=False):
        if verbose is True:
            print('')
            print('=' * 100)
            print('Power Supply')
            print('=' * 100)

    def setSupplyVoltage(self, voltage=5.0):
        self.voltage = voltage
        # set up analog IO channel nodes
        # enable positive supply
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(0), c_int(0), self._true)
        # disable negative supply
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(1), c_int(0), self._false)

        # set positive supply voltage to 5 V
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(0), c_int(1), c_double(voltage))

    def enablePowerSupply(self):
        # master enable
        self.dwf.FDwfAnalogIOEnableSet(self.hdwf, self._true)
        print("Power Supply: [%.1fV Enabled]." % self.voltage)

    def disablePowerSupply(self):
        self.dwf.FDwfAnalogIOEnableSet(self.hdwf, self._false)
        print("Power Supply: [%.1fV Disabled]." % self.voltage)

    def monitorPowerSupply(self, verbose=True):
        # fetch analogIO status from device
        self.dwf.FDwfAnalogIOStatus(self.hdwf)

        # supply monitor
        supply_voltage = c_double()
        supply_current = c_double()
        self.dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, c_int(2), c_int(0), byref(supply_voltage))
        self.dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, c_int(2), c_int(1), byref(supply_current))
        voltage = supply_voltage.value
        current = supply_current.value
        if verbose is True:
            print("USB: %.3f V / %.3f A." % (voltage, current))
        return voltage, current
