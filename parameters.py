import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt


CHIP_RATE = 16  # this is chips per bit of data
SEQ_LEN = 64
DATA_BITRATE = 50  # this is baud rate of the data (not chip rate)
OVERSAMPLE_RATIO = 60  # this need to be integer (see below)
CARRIER_SAMPLERATE = CHIP_RATE * DATA_BITRATE * OVERSAMPLE_RATIO  # this should be an integer multiple of chip rate * data bitrate
CARRIER_CENTER = 3000
BW_LIMIT = 2500

PRN_SEED = 1


RX_CARRIER_CENTER = 3010
SRRC_BETA = 0.6
SRRC_N = 1


def srrc_pulse(beta, T, sps, N_sym):
    # Time vector
    t = np.arange(-N_sym*T, N_sym*T + T/sps, T/sps)
    pi = np.pi
    h = np.zeros_like(t)

    # General case
    denom = pi * t * (1 - (4 * beta * t / T)**2) / T
    num   = np.sin(pi * t * (1 - beta) / T) + \
            4 * beta * t / T * np.cos(pi * t * (1 + beta) / T)
    h = num / denom

    # Handle t == 0
    idx0 = np.isclose(t, 0.0)
    h[idx0] = (1 + beta*(4/pi - 1))

    # Handle |t| == T/(4*beta)
    if beta != 0:
        idx1 = np.isclose(np.abs(t), T/(4*beta))
        h[idx1] = (beta/np.sqrt(2)) * (
            (1 + 2/pi)*np.sin(pi/(4*beta)) +
            (1 - 2/pi)*np.cos(pi/(4*beta))
        )

    # Normalize energy
    h = h / np.sqrt(np.sum(h**2))

    return t, h

# asd, h = srrc_pulse(SRRC_BETA, 1, OVERSAMPLE_RATIO, SRRC_N)
# print(h)
# plt.plot(h)
# plt.show()