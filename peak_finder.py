import numpy as np

class PeakFinder:
    def __init__(self, seq_len, min_above_average):
        self.seq_len = seq_len
        self.max_val = 0
        self.max_index = -1
        self.buf = np.zeros(seq_len)
        self.current_addr = 0
        self.min_above_average = min_above_average

    def pushValue(self, value):
        self.buf = np.roll(self.buf, 1)  # shift everything right by 1
        self.buf[0] = value

        if value > self.max_val:
            self.max_val = value
            self.max_index = self.current_addr

        # go through an entire cycle, and find max value if it is good enough.
        if self.current_addr >= self.seq_len - 1:
            current_address = self.current_addr
            self.current_addr = 0
            # remove max value
            self.buf[self.max_index] = 0
            average = np.sum(self.buf) / self.seq_len
            if self.max_val > average * self.min_above_average:
                 # return self.max_index
                # compute number of indices past
                delta = self.max_index - current_address
                return True, delta
        self.current_addr += 1
        return False, 0

