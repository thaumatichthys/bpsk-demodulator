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

        return self.yvals[0]

# signal = np.zeros(10000)
# signal[0] = 1
#
# output = []
#
# filter = IIRFilter(0.02)
# for i in range(len(signal)):
#     output.append(filter.pushValue(signal[i]))
#
# # plt.plot(output)
# plt.plot(abs(np.fft.rfft(output)))
# plt.show()