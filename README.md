# PowerTouch

A Genetic Algorithm-based framework that can automatically generate `wired ghost touch attacks` given security objectives (e.g., types and locations of desired ghost touches).

## About this work

To be updated.  

For more details, please refer to our **ICCAD'22** paper: [_PowerTouch: A Security Objective-Guided Automation Framework
for Generating Wired Ghost Touch Attacks on Touchscreens_](ICCAD2022_PowerTouch.pdf).

## Dependencies

### Software Dependencies

* Standard packages: `ctypes`, `numpy`, `re`, `datetime`, `pandas`, `warnings`, `matplotlib`, `statistics`, `time`


* Python Genetic Algorithm Library: [PyGAD](https://pygad.readthedocs.io/en/latest/)
  ```bash
  pip install pygad
  ```

* Android Debug Bridge (ADB): [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools).
  > Currently, the framework only supports Android devices. We will add support for iOS devices in the future.


* Clone this repository
  ```bash
  git clone https://github.com/xz-group/PowerTouch.git
  ```

### Hardware Dependencies

* `All-in-one USB instrument`: [Analog Discovery 2](https://digilent.com/shop/analog-discovery-2-100ms-s-usb-oscilloscope-logic-analyzer-and-variable-power-supply/) 
with [BNC Adapter board](https://digilent.com/shop/bnc-adapter-for-analog-discovery/).

  * Five instruments are implemented in Analog Discovery 2 for this framework: 
    * `oscilloscope`: to capture the TX excitation signal of the touchscreen and monitor the generated noise signal.
    * `waveform generator`: to generate the noise signal.
    * `pattern generator`: to generate digital control signals for the relays on the customized noise injection PCB.
    * `logic analyzer`: to monitor the above digital control signals.
    * `power supply`: to power the customized noise injection PCB.


* `High-voltage amplifier module`: we use [MX200 Piezo Driver](https://www.piezodrive.com/modules/mx200-high-performance-piezo-driver/) for this project.
  But any high-voltage amplifier module that can generate minimum 60Vpp signal with 500kHz bandwidth should work.
  >   The bandwidth of MX200 is 200KHz also. We extend the bandwidth to around 500KHz by calibrating the gain of the amplifier. See [here]() for details.


* Our `customized noise injection PCB`: source design files are available in [hardware](./hardware) folder.
  ![pcb](./hardware/main_front.png)


* `Power supply`: this is used to power the high-voltage amplifier module and charge the smartphone (if enable charging the phone feature). We use [Keithley 2231A-30-3 Triple-channel DC Power Supply](https://www.tek.com/en/products/keithley/dc-power-supplies/2220-2230-2231-series).


## File Structure
 * `hardware`: contains the hardware files for the PowerTouch framework
 * `PowerTouch`: contains the source code for the PowerTouch framework


## How to Use

To be updated.


## Citation

If you use this framework for your research, please cite our [ICCAD'22 paper](ICCAD2022_PowerTouch.pdf):

```
To be updated
```

## Contact Information

If you have any questions regarding using this framework, please feel free to contact us at [zhuhuifeng@wustl.edu](mailto:zhuhuifeng@wustl.edu).

## Roadmap
- [ ] To be updated

## Version History

* 0.1
  * Initial Release

## License

This framework is licensed under the `GNU3` License - see the [LICENSE.md](LICENSE) file for details
