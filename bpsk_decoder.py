import numpy as np
from parameters import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
from iirfilter import *

samplerate, data = wavfile.read("output.wav")

duration = len(data) / samplerate

times = np.linspace(0, duration, len(data))

i_filt = IIRFilter(0.1)
q_filt = IIRFilter(0.1)


output = []
loop_correction = 0

baseband = []

asd, h = srrc_pulse(SRRC_BETA, 1, OVERSAMPLE_RATIO / 2, SRRC_N)

srrc_filt_i = FIRFilter(h)
srrc_filt_q = FIRFilter(h)

for i in range(len(times)):
    # giant loop
    t = times[i]

    input = data[i]

    # costas loop
    i_sig_nosrrc = i_filt.pushValue(input * np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))
    q_sig_nosrrc = q_filt.pushValue(input * np.sin(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))

    # SRRC filter
    i_sig = srrc_filt_i.push(i_sig_nosrrc)
    q_sig = srrc_filt_q.push(q_sig_nosrrc)
    i_sig = np.arctan(i_sig * 1000)
    q_sig = np.arctan(q_sig * 1000)
    # end SRRC

    constellation_error = i_sig * q_sig  # no loop filter required! (apart from an integrator)
    # apply scaling function (makes loop converge faster)
    constellation_error = np.arctan(constellation_error)
    # loop filter (integrator)
    loop_correction += -0.00025 * constellation_error
    # end of costas loop demodulator

    output.append(loop_correction)

    baseband.append(i_sig)




print(samplerate)

# plt.plot(abs(np.fft.rfft(baseband)))
# plt.plot(np.cos(2 * np.pi * CARRIER_CENTER * times))
plt.plot(baseband)
plt.plot(output)
plt.show()

