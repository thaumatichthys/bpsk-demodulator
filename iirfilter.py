import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter


class IIRFilter:
    def __init__(self, cutoff_frac):  # cutoff as a frac of nyquist freq
        self.yvals = np.zeros(3)
        self.xvals = np.zeros(3)

        self.b, self.a = butter(2, cutoff_frac)
    def pushValue(self, new_value):
        self.xvals[0] = new_value
        # buterbrod
        # self.yvals[0] = (0.0675 * self.xvals[0] + 0.1349 * self.xvals[1] + 0.0675 * self.xvals[2] +
        #                  1.143 * self.yvals[1] - 0.4128 * self.yvals[2])
        self.yvals[0] = np.dot(self.xvals, self.b) - np.dot(self.yvals[1:], self.a[1:])
        # print(self.yvals[0])

        self.yvals[2] = self.yvals[1]
        self.yvals[1] = self.yvals[0]
        self.xvals[2] = self.xvals[1]
        self.xvals[1] = self.xvals[0]

        # for i in range(2):
        #     index = 2 - i
        #     self.yvals[index] = self.yvals[index - 1]
        #     self.xvals[index] = self.xvals[index - 1]

        return self.yvals[0]


class IIR_BPF:
    def __init__(self, order, samplerate, low, high):
        nyq = samplerate / 2
        low_frac = low / nyq
        high_frac = high / nyq
        self.order = order
        self.yvals = np.zeros(2 * order + 1)
        self.xvals = np.zeros(2 * order + 1)

        self.b, self.a = butter(N=order, Wn=[low_frac, high_frac], btype='bandpass')

    def pushValue(self, new_value):
        self.xvals[0] = new_value

        # H(e^jw) = b / a = Y / X
        # b * X = a * Y
        # b * X = a0y0 + an * yn
        # a0y0 = dot(b, X) - dot(a[1:], y[1:])

        self.yvals[0] = np.dot(self.xvals, self.b) - np.dot(self.yvals[1:], self.a[1:])

        for i in range(self.order * 2):
            index = self.order * 2 - i
            self.yvals[index] = self.yvals[index - 1]
            self.xvals[index] = self.xvals[index - 1]
        return self.yvals[0]

class FIRFilter:  # chatgpted
    def __init__(self, coeffs):
        """
        coeffs: list or np.array of FIR filter taps (h[0], h[1], ..., h[N])
        """
        self.coeffs = np.array(coeffs)[::-1]  # reverse for convolution order
        self.buffer = np.zeros(len(coeffs))

    def push(self, x):
        """
        Push a new sample in and get the filtered output.
        """
        self.buffer = np.roll(self.buffer, 1)
        self.buffer[0] = x
        y = np.dot(self.buffer, self.coeffs)
        return y

#
# print(butter(N=2, Wn=[.3, .6], btype='bandpass'))
# signal = np.zeros(10000)
# signal[0] = 1
#
# output = []
#
# # filter = IIRFilter(0.2)
# filter = IIR_BPF(4, 2, 0.4, 0.5)
# for i in range(len(signal)):
#     output.append(filter.pushValue(signal[i]))
#
# # plt.plot(output)
# plt.plot(abs(np.fft.rfft(output)))
# plt.show()