

class PFD:
    def __init__(self):
        self.prev_ref = 0
        self.prev_in = 0
        self.up = 0
        self.down = 0

    def update(self, ref, inp):
        # Rising edges
        ref_edge = False
        if ref > 0 and self.prev_ref < 0:
            ref_edge = True
        in_edge = False
        if inp > 0 and self.prev_in < 0:
            in_edge = True
        # ref_edge = ref and not self.prev_ref
        # in_edge = inp and not self.prev_in

        if ref_edge:
            self.up = 1
            self.down = 0  # clear DOWN on REF edge
        if in_edge:
            self.down = 1
            self.up = 0  # clear UP on IN edge

        # Lock condition: both edges came
        if ref_edge and in_edge:
            self.up = 0
            self.down = 0

        self.prev_ref = ref
        self.prev_in = inp

        return self.up - self.down