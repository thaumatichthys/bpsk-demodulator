import numpy as np
from scipy.signal import butter, filtfilt


CHIP_RATE = 16  # this is chips per bit of data
SEQ_LEN = 64
DATA_BITRATE = 50  # this is baud rate of the data (not chip rate)
OVERSAMPLE_RATIO = 60  # this need to be integer (see below)
CARRIER_SAMPLERATE = CHIP_RATE * DATA_BITRATE * OVERSAMPLE_RATIO  # this should be an integer multiple of chip rate * data bitrate
CARRIER_CENTER = 3000
BW_LIMIT = 2500

PRN_SEED = 1


RX_CARRIER_CENTER = 3010
SRRC_BETA = 1
SRRC_N = 4


def srrc_pulse(beta, T, sps, N):
    """
    Generate Square Root Raised Cosine (SRRC) filter impulse response.

    Parameters:
    - beta: roll-off factor (0 to 1)
    - T: symbol period (can be 1 if normalized)
    - sps: samples per symbol (oversampling factor)
    - N: number of symbols on each side (filter length = 2*N*sps + 1)

    Returns:
    - t: time vector
    - h: impulse response of SRRC filter
    """
    t = np.arange(-N * T, N * T + T / sps, T / sps)
    h = np.zeros_like(t)

    for i in range(len(t)):
        if t[i] == 0.0:
            h[i] = 1.0 - beta + (4 * beta / np.pi)
        elif abs(t[i]) == T / (4 * beta):
            h[i] = (beta / np.sqrt(2)) * (
                    (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) +
                    (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta))
            )
        else:
            h[i] = (np.sin(np.pi * t[i] * (1 - beta) / T) +
                    4 * beta * t[i] / T * np.cos(np.pi * t[i] * (1 + beta) / T)) / \
                   (np.pi * t[i] * (1 - (4 * beta * t[i] / T) ** 2) / T)

    # Normalize energy
    h = h / np.sqrt(np.sum(h ** 2))

    return t, h