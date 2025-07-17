import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt


CHIP_RATE = 64  # this is chips per bit of data
SEQ_LEN = 64
DATA_BITRATE = 100  # this is baud rate of the data (not chip rate)
OVERSAMPLE_RATIO = 8  # this need to be integer (see below)
CARRIER_SAMPLERATE = CHIP_RATE * DATA_BITRATE * OVERSAMPLE_RATIO  # this should be an integer multiple of chip rate * data bitrate
CARRIER_CENTER = 6000
BW_LIMIT = 2500

PRN_SEED = 1


RX_CARRIER_CENTER = 6002
PLL_MAX_DEVIATION = 50
RAISED_COSINE_BETA = 0.6
RAISED_COSINE_N = 1

PEAK_FINDER_MIN_ABOVE_AVERAGE = 3


def raised_cosine(beta, T, sps, N_sym):
    t = np.arange(-N_sym * T, N_sym * T + T / sps, T / sps)
    pi = np.pi

    # Precompute to avoid div0
    x = t / T
    four_beta_x = 2 * beta * x

    # Main formula: h(t) = sinc(x) * cos(pi beta x) / (1 - (2 beta x)^2)
    h = np.sinc(x) * np.cos(pi * beta * x) / (1 - four_beta_x ** 2)

    # Handle t == 0
    idx0 = np.isclose(t, 0.0)
    h[idx0] = 1.0

    # Handle |t| == T/(2β)
    if beta != 0:
        idx1 = np.isclose(np.abs(t), T / (2 * beta))
        # limit: h(T/(2β)) = (β/2) * sinc(1/(2β))
        val = (beta / 2) * np.sinc(1 / (2 * beta))
        h[idx1] = val

    # Normalize to unit energy
    h = h / np.sqrt(np.sum(h ** 2))

    return t, h

# asd, h = srrc_pulse(SRRC_BETA, 1, OVERSAMPLE_RATIO, SRRC_N)
# print(h)
# plt.plot(h)
# plt.show()