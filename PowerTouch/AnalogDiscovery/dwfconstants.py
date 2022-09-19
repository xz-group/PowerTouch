from ctypes import *

class DwfConstants:
    # device handle
    # HDWF
    hdwfNone = c_int(0)

    # device enumeration filters
    _enumfilterAll = c_int(0)
    _enumfilterEExplorer = c_int(1)
    _enumfilterDiscovery = c_int(2)
    _enumfilterDiscovery2 = c_int(3)
    _enumfilterDDiscovery = c_int(4)

    # device ID
    _devidEExplorer = c_int(1)
    _devidDiscovery = c_int(2)
    _devidDiscovery2 = c_int(3)
    _devidDDiscovery = c_int(4)

    # device version
    _devverEExplorerC = c_int(2)
    _devverEExplorerE = c_int(4)
    _devverEExplorerF = c_int(5)
    _devverDiscoveryA = c_int(1)
    _devverDiscoveryB = c_int(2)
    _devverDiscoveryC = c_int(3)

    # trigger source
    _trigsrcNone = c_ubyte(0)
    _trigsrcPC = c_ubyte(1)
    _trigsrcDetectorAnalogIn = c_ubyte(2)
    _trigsrcDetectorDigitalIn = c_ubyte(3)
    _trigsrcAnalogIn = c_ubyte(4)
    _trigsrcDigitalIn = c_ubyte(5)
    _trigsrcDigitalOut = c_ubyte(6)
    _trigsrcAnalogOut1 = c_ubyte(7)
    _trigsrcAnalogOut2 = c_ubyte(8)
    _trigsrcAnalogOut3 = c_ubyte(9)
    _trigsrcAnalogOut4 = c_ubyte(10)
    _trigsrcExternal1 = c_ubyte(11)
    _trigsrcExternal2 = c_ubyte(12)
    _trigsrcExternal3 = c_ubyte(13)
    _trigsrcExternal4 = c_ubyte(14)
    _trigsrcHigh = c_ubyte(15)
    _trigsrcLow = c_ubyte(16)

    # instrument states
    _DwfStateReady = c_ubyte(0)
    _DwfStateConfig = c_ubyte(4)
    _DwfStatePrefill = c_ubyte(5)
    _DwfStateArmed = c_ubyte(1)
    _DwfStateWait = c_ubyte(7)
    _DwfStateTriggered = c_ubyte(3)
    _DwfStateRunning = c_ubyte(3)
    _DwfStateDone = c_ubyte(2)

    # DwfEnumConfigInfo
    _DECIAnalogInChannelCount = c_int(1)
    _DECIAnalogOutChannelCount = c_int(2)
    _DECIAnalogIOChannelCount = c_int(3)
    _DECIDigitalInChannelCount = c_int(4)
    _DECIDigitalOutChannelCount = c_int(5)
    _DECIDigitalIOChannelCount = c_int(6)
    _DECIAnalogInBufferSize = c_int(7)
    _DECIAnalogOutBufferSize = c_int(8)
    _DECIDigitalInBufferSize = c_int(9)
    _DECIDigitalOutBufferSize = c_int(10)

    # acquisition modes:
    _acqmodeSingle = c_int(0)
    _acqmodeScanShift = c_int(1)
    _acqmodeScanScreen = c_int(2)
    _acqmodeRecord = c_int(3)
    _acqmodeOvers = c_int(4)
    _acqmodeSingle1 = c_int(5)

    # analog acquisition filter:
    _filterDecimate = c_int(0)
    _filterAverage = c_int(1)
    _filterMinMax = c_int(2)

    # analog in trigger mode:
    _trigtypeEdge = c_int(0)
    _trigtypePulse = c_int(1)
    _trigtypeTransition = c_int(2)

    # trigger slope:
    _DwfTriggerSlopeRise = c_int(0)
    _DwfTriggerSlopeFall = c_int(1)
    _DwfTriggerSlopeEither = c_int(2)

    # trigger length condition
    _triglenLess = c_int(0)
    _triglenTimeout = c_int(1)
    _triglenMore = c_int(2)

    # error codes for the functions:
    _dwfercNoErc = c_int(0)  # No error occurred
    _dwfercUnknownError = c_int(1)  # API waiting on pending API timed out
    _dwfercApiLockTimeout = c_int(2)  # API waiting on pending API timed out
    _dwfercAlreadyOpened = c_int(3)  # Device already opened
    _dwfercNotSupported = c_int(4)  # Device not supported
    _dwfercInvalidParameter0 = c_int(16)  # Invalid parameter sent in API call
    _dwfercInvalidParameter1 = c_int(17)  # Invalid parameter sent in API call
    _dwfercInvalidParameter2 = c_int(18)  # Invalid parameter sent in API call
    _dwfercInvalidParameter3 = c_int(19)  # Invalid parameter sent in API call
    _dwfercInvalidParameter4 = c_int(20)  # Invalid parameter sent in API call

    # analog out signal types
    _funcDC = c_ubyte(0)
    _funcSine = c_ubyte(1)
    _funcSquare = c_ubyte(2)
    _funcTriangle = c_ubyte(3)
    _funcRampUp = c_ubyte(4)
    _funcRampDown = c_ubyte(5)
    _funcNoise = c_ubyte(6)
    _funcPulse = c_ubyte(7)
    _funcTrapezium = c_ubyte(8)
    _funcSinePower = c_ubyte(9)
    _funcCustom = c_ubyte(30)
    _funcPlay = c_ubyte(31)

    # analog io channel node types
    _analogioEnable = c_ubyte(1)
    _analogioVoltage = c_ubyte(2)
    _analogioCurrent = c_ubyte(3)
    _analogioPower = c_ubyte(4)
    _analogioTemperature = c_ubyte(5)

    _AnalogOutNodeCarrier = c_int(0)
    _AnalogOutNodeFM = c_int(1)
    _AnalogOutNodeAM = c_int(2)

    _DwfAnalogOutIdleDisable = c_int(0)
    _DwfAnalogOutIdleOffset = c_int(1)
    _DwfAnalogOutIdleInitial = c_int(2)

    _DwfDigitalInClockSourceInternal = c_int(0)
    _DwfDigitalInClockSourceExternal = c_int(1)

    _DwfDigitalInSampleModeSimple = c_int(0)
    # alternate samples: noise|sample|noise|sample|...
    # where noise is more than 1 transition between 2 samples
    _DwfDigitalInSampleModeNoise = c_int(1)

    _DwfDigitalOutOutputPushPull = c_int(0)
    _DwfDigitalOutOutputOpenDrain = c_int(1)
    _DwfDigitalOutOutputOpenSource = c_int(2)
    _DwfDigitalOutOutputThreeState = c_int(3)

    _DwfDigitalOutTypePulse = c_int(0)
    _DwfDigitalOutTypeCustom = c_int(1)
    _DwfDigitalOutTypeRandom = c_int(2)
    _DwfDigitalOutTypeROM = c_int(3)

    _DwfDigitalOutIdleInit = c_int(0)
    _DwfDigitalOutIdleLow = c_int(1)
    _DwfDigitalOutIdleHigh = c_int(2)
    _DwfDigitalOutIdleZet = c_int(3)

    _DwfAnalogImpedanceImpedance = c_int(0)
    _DwfAnalogImpedanceImpedancePhase = c_int(1)
    _DwfAnalogImpedanceResistance = c_int(2)
    _DwfAnalogImpedanceReactance = c_int(3)
    _DwfAnalogImpedanceAdmittance = c_int(4)
    _DwfAnalogImpedanceAdmittancePhase = c_int(5)
    _DwfAnalogImpedanceConductance = c_int(6)
    _DwfAnalogImpedanceSusceptance = c_int(7)
    _DwfAnalogImpedanceSeriesCapactance = c_int(8)
    _DwfAnalogImpedanceParallelCapacitance = c_int(9)
    _DwfAnalogImpedanceSeriesInductance = c_int(10)
    _DwfAnalogImpedanceParallelInductance = c_int(11)
    _DwfAnalogImpedanceDissipation = c_int(12)
    _DwfAnalogImpedanceQuality = c_int(13)

    _DwfParamUsbPower = c_int(2)  # 1 keep the USB power enabled even when AUX is connected, Analog Discovery 2
    _DwfParamLedBrightness = c_int(3)  # LED brightness 0 ... 100%, Digital Discovery
    _DwfParamOnClose = c_int(4)  # 0 continue, 1 stop, 2 shutdown
    _DwfParamAudioOut = c_int(5)  # 0 disable / 1 enable audio output, Analog Discovery 1, 2
    _DwfParamUsbLimit = c_int(6)  # 0..1000 mA USB power limit, -1 no limit, Analog Discovery 1, 2

    # others
    _true = c_int(True)
    _false = c_int(False)

    # obsolate
    # STS
    _stsRdy = c_ubyte(0)
    _stsArm = c_ubyte(1)
    _stsDone = c_ubyte(2)
    _stsTrig = c_ubyte(3)
    _stsCfg = c_ubyte(4)
    _stsPrefill = c_ubyte(5)
    _stsNotDone = c_ubyte(6)
    _stsTrigDly = c_ubyte(7)
    _stsError = c_ubyte(8)
    _stsBusy = c_ubyte(9)
    _stsStop = c_ubyte(10)

    # TRIGCOND
    _trigcondRisingPositive = c_int(0)
    _trigcondFallingNegative = c_int(1)
