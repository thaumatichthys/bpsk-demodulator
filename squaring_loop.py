from pfd import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from iirfilter import *

LOOP_BW = 0.5
class SquaringLoop:
    def __init__(self, samplerate, carrier_freq, max_dev):
        if samplerate < (carrier_freq + max_dev) * 4:
            raise ValueError("The squaring loop doubles frequency, so your sample rate must be > 4*carrier freq")
        self.input_filter = IIR_BPF(4, samplerate, (carrier_freq - max_dev) * 2, (carrier_freq + max_dev) * 2)
        self.output_filter = IIR_BPF(4, samplerate, carrier_freq - max_dev, carrier_freq + max_dev)
        self.local_prev_state = -1
        self.out = 1
        self.carrier_freq = carrier_freq
        self.samplerate = samplerate
        self.max_dev = max_dev
        self.loop_correction = 0
        self.pfd = PFD()
        self.t = 0

        self.loop_filter = IIRFilter(LOOP_BW / samplerate)

    def update(self, input_val, lo_in):  # LO must be a clean sinusoid with zero DC offset.
        squared = input_val * input_val
        cleaned = self.input_filter.pushValue(squared)
        zero_cross = np.sign(cleaned)  # turns into square wave
        lo_in = lo_in * lo_in - 1/2  # this is very crude but whatever
        local = np.sign(lo_in)
        error = 0.00025 * (self.pfd.update(local, zero_cross))
        # error = 0.00015 * self.loop_filter.pushValue(self.pfd.update(local, zero_cross))
        self.loop_correction -= error

        if np.abs(self.loop_correction) > self.max_dev:
            self.loop_correction = self.max_dev * self.loop_correction / np.abs(self.loop_correction)
        return self.loop_correction



# test function

# samplerate, data = wavfile.read("output.wav")
# dut = SquaringLoop(samplerate, RX_CARRIER_CENTER, 20)
#
# duration = len(data) / samplerate
#
# times = np.linspace(0, duration, len(data))
#
# output = []
# loop_corr = []
# loop_correction = 0
#
# for i in range(len(data)):
#     input = data[i]
#     t = times[i]
#
#     lo = np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t)
#     loop_correction = dut.update(input, lo)
#
#
#     loop_corr.append(loop_correction)
#     output.append(lo)
#
#
#
# plt.plot(output)
# plt.plot(data)
# plt.plot(loop_corr)
# plt.show()