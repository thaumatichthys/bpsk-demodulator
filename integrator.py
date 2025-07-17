import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter


class Integrator:
    def __init__(self):
        self.accumulator = 0
    def accumulate(self, new_value):
        self.accumulator += new_value

    def dumpValue(self):
        val = self.accumulator
        self.accumulator = 0
        return val

    def getValue(self):
        return self.accumulator

class Derivator:
    def __init__(self):
        self.previous = 0

    def pushValue(self, value):
        prev = self.previous
        self.previous = value
        return value - prev