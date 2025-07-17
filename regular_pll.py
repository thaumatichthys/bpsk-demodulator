import numpy as np
from parameters import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
from iirfilter import *
from pfd import *

samplerate, data = wavfile.read("output.wav")

duration = len(data) / samplerate

times = np.linspace(0, duration, len(data))

MAX_DEVIATION = 50
input_filter = IIR_BPF(4, CARRIER_SAMPLERATE, RX_CARRIER_CENTER - MAX_DEVIATION, RX_CARRIER_CENTER + MAX_DEVIATION)

output = []
loop_correction = 0

pfd = PFD()

dummy = 0

baseband = []
print(times)
for i in range(len(times)):
    t = times[i]

    input = data[i]
    # input = np.sin(2 * np.pi * (CARRIER_CENTER) * t)

    input = input_filter.pushValue(input * input)

    rectangled = np.sign(input)

    local = np.sign(np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))

    error = 0.0001 * (pfd.update(local, rectangled))

    loop_correction -= error

    if np.abs(loop_correction) > MAX_DEVIATION:
        loop_correction = MAX_DEVIATION * loop_correction / np.abs(loop_correction)

    baseband.append(loop_correction)




print(samplerate)

# plt.plot(abs(np.fft.rfft(baseband)))
# plt.plot(np.cos(2 * np.pi * CARRIER_CENTER * times))
plt.plot(baseband)
plt.plot(output)
plt.show()

