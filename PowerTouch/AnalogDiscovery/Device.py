import sys
from ctypes import cdll, c_int, create_string_buffer, byref
from PowerTouch.AnalogDiscovery.dwfconstants import DwfConstants


class AnalogDiscovery(DwfConstants):
    def __init__(self, verbose=True):
        self.dwf, self.hdwf = self.initiateDevice(verbose=verbose)
        self.channel = None

    def initiateDevice(self, verbose=False):
        if sys.platform.startswith("win"):
            dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            dwf = cdll.LoadLibrary("libdwf.so")

        # continue running after device close, prevent temperature drifts
        dwf.FDwfParamSet(c_int(4), c_int(0))  # 4 = DwfParamOnClose, 0 = continue 1 = stop 2 = shutdown

        # print DWF version
        version = create_string_buffer(16)
        dwf.FDwfGetVersion(version)
        if verbose:
            print("DWF Version: " + str(version.value))

        # open device
        hdwf = c_int()
        if verbose:
            print("Opening first device...")
        dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

        if hdwf.value == self.hdwfNone.value:
            raise Exception("failed to open device")
        else:
            if verbose:
                print("successfully opened device")

        return dwf, hdwf

    def closeDevice(self):
        self.dwf.FDwfDeviceCloseAll()
