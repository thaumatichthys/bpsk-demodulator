

class ClockRecovery:
    # samples early and late, if one of the early or late ones is different from the rest, increase clock speed, and vice versa
    #   |           |
    #   |           |
    #   |           |
    #    -----------
    #     ^   ^   ^
    #    samples
    #
    #    sample at 4x sample rate, so distance D between samples, and distance D/2 between sample and edge

    def __init__(self, carrier_samplerate, symbol_rate):
        i= 1
        self.samples_per_symbol = (carrier_samplerate / symbol_rate)
        self.samples_per_update = int(self.samples_per_symbol / 3)
        self.samples_per_update_adjust = 0
        self.input_sample_counter = 0  # refers to the data samples from the wav file
        self.sample_sample_counter = 0  # counts up to 4, refers to the clock recovery sampling the input
        self.early = 0
        self.middle = 0
        self.late = 0
        self.output = -1

    def update(self, sample):
        if int(self.input_sample_counter) % (self.samples_per_update + self.samples_per_update_adjust) == 0:
            # update
            self.late = self.middle
            self.middle = self.early
            self.early = sample

            if self.sample_sample_counter % 3 == 0:
                if self.middle == self.early and self.late != self.middle:  # late sample is different
                    self.samples_per_update_adjust += 1
                    print("late")
                if self.middle == self.late and self.early != self.middle:  # early sample is different
                    self.samples_per_update_adjust += -1
                    print("early")
                self.output *= -1
            self.sample_sample_counter += 1
        self.input_sample_counter += 1
        return self.output


