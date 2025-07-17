

class PFD:
    def __init__(self):
        self.prev_ref = 0
        self.prev_in = 0
        self.up = 0
        self.down = 0

    def update(self, ref, inp):
        # Detect rising edges
        ref_edge = ref > 0 and self.prev_ref <= 0
        in_edge = inp > 0 and self.prev_in <= 0

        # Latch UP and DOWN on their respective rising edges
        if ref_edge:
            self.up = 1
        if in_edge:
            self.down = 1

        # Reset both if both were set (AND gate)
        if self.up and self.down:
            self.up = 0
            self.down = 0

        # Save previous values
        self.prev_ref = ref
        self.prev_in = inp

        # Output is UP - DOWN, just like a charge pump would convert it
        return self.up - self.down