import numpy as np
from parameters import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
from iirfilter import *
from pfd import *

samplerate, data = wavfile.read("output.wav")

duration = len(data) / samplerate

times = np.linspace(0, duration, len(data))


lpf = IIRFilter(1/100)


output = []
loop_correction = 0

pfd = PFD()

dummy = 0

baseband = []

for i in range(len(times)):
    t = times[i]

    #input = data[i]
    input = np.cos(2 * np.pi * (CARRIER_CENTER) * t)

    rectangled = np.sign(input)

    local = np.sign(np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))

    error = 0.0002 * (pfd.update(local, rectangled))

    loop_correction -= error


    baseband.append(loop_correction)




print(samplerate)

# plt.plot(abs(np.fft.rfft(baseband)))
# plt.plot(np.cos(2 * np.pi * CARRIER_CENTER * times))
plt.plot(baseband)
plt.plot(output)
plt.show()

