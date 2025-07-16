import numpy as np
from scipy.signal import butter, filtfilt


CHIP_RATE = 16  # this is chips per bit of data
SEQ_LEN = 64
DATA_BITRATE = 50  # this is baud rate of the data (not chip rate)
CARRIER_SAMPLERATE = CHIP_RATE * DATA_BITRATE * 60  # this should be an integer multiple of chip rate * data bitrate
CARRIER_CENTER = 3000
BW_LIMIT = 2500

PRN_SEED = 1


RX_CARRIER_CENTER = 3004

def lowpass_filter(data, samplerate, cutoff, order=8):
    """
    Lowpass Butterworth filter.

    Args:
        data (array-like): The input signal.
        samplerate (float): Sampling frequency in Hz.
        cutoff (float): Cutoff frequency in Hz.
        order (int): Filter order (default 8).

    Returns:
        ndarray: Filtered signal.
    """
    nyquist = 0.5 * samplerate
    norm_cutoff = cutoff / nyquist
    b, a = butter(order, norm_cutoff, btype='low')
    filtered = filtfilt(b, a, data)
    return filtered