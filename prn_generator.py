import numpy as np


class PRNG:
    def __init__(self, samplerate, seed, seq_length, data_bitrate, chip_coeff):
        self.sample_rate = samplerate
        # self.seed = seed
        self.seq_len = seq_length  # number of chips
        self.data_bitrate = data_bitrate
        self.chip_coeff = chip_coeff  # number of chips per data bit

        self.phase_samples = 0  # phase in the unit of samples.
        self.samples_per_chip = int(samplerate / (chip_coeff * data_bitrate))
        self.samples_per_seq = self.samples_per_chip * seq_length

        np.random.seed(seed)
        self.prn_sequence = np.random.randint(0, 2, self.samples_per_seq)
        print(self.prn_sequence[0:10])

    def getSample0(self):  # runs every sample of signal
        rounded_index = int(self.phase_samples / self.samples_per_chip)
        output = self.prn_sequence[rounded_index]
        return output

    def getSample45(self):  # runs every sample of signal, returns signal quarter period phase advanced
        rounded_index = int(self.phase_samples / self.samples_per_chip) + int(self.samples_per_chip / 8)
        output = self.prn_sequence[rounded_index]
        return output

    def getSampleMinus45(self):  # runs every sample of signal, returns signal quarter period phase advanced
        rounded_index = int(self.phase_samples / self.samples_per_chip) - int(self.samples_per_chip / 8)
        output = self.prn_sequence[rounded_index]
        return output

    def advancePhase(self):
        self.phase_samples += 1
        while self.phase_samples < 0:
            self.phase_samples += self.samples_per_seq
        while self.phase_samples >= self.samples_per_seq:
            self.phase_samples -= self.samples_per_seq
    def advancePhaseHalfPeriod(self):
        self.phase_samples += int(self.samples_per_chip / 2)

    def advancePhaseSamples(self, samples):
        self.phase_samples += int(samples - 1)
        self.advancePhase()