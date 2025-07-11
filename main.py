import numpy as np
import matplotlib.pyplot as plt
import numpy.random
from scipy.io import wavfile
from parameters import *

# data_length = int(32 * SEQ_LEN / CHIP_RATE)
# data_input = np.random.randint(0, 2, data_length)
input_text = "hello hello" # "a wrinkle in falkland by margaret thatcher, an account of britdain"

data_input = np.unpackbits(np.frombuffer(input_text.encode("utf-8"), dtype=np.uint8))
data_length = len(data_input)

num_seqs = np.ceil(data_length * CHIP_RATE / SEQ_LEN)
data_input_upsampled = np.repeat(data_input, CHIP_RATE)

length_padding = int(num_seqs * SEQ_LEN - len(data_input_upsampled))
if length_padding > 0:
    data_input_upsampled_padded = np.concat((data_input_upsampled, np.zeros(length_padding, dtype=int)))
else:
    data_input_upsampled_padded = data_input_upsampled

numpy.random.seed(1)
prn_sequence = np.random.randint(0, 2, SEQ_LEN)
prn_length = num_seqs * SEQ_LEN
prn_total = np.tile(prn_sequence, int(prn_length / SEQ_LEN))
dsss_bits = np.bitwise_xor(prn_total, data_input_upsampled_padded)
dsss_bits_upsampled = np.repeat(dsss_bits, int(CARRIER_SAMPLERATE / (CHIP_RATE * DATA_BITRATE)))
duration = len(data_input_upsampled_padded) / DATA_BITRATE / CHIP_RATE
t = np.linspace(0, duration, int(CARRIER_SAMPLERATE * duration))
signal_out = np.cos(t * 2*np.pi * CARRIER_CENTER) * (2 * dsss_bits_upsampled - 1)

wavfile.write("output.wav", CARRIER_SAMPLERATE, signal_out)


plt.plot(np.abs(np.fft.rfft(signal_out)))
plt.show()


print(data_input)
