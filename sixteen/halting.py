# -*- coding: utf-8 -*-


class LoopDetecting(object):
    "Ill-informed attempts at solving the halting problem."
    # this gets turned into True if we suspect the program is looping.
    stop = False

    def is_looping(self):
        if self.stop:
            return True
        else:
            # if it's sub pc, 1, it's a loop...
            if self.RAM[self.registers["PC"]] == 0x85c3:
                self.stop = True
            else:
                # if it's something like :loop set pc, loop, it's a loop
                first = self.RAM[self.registers["PC"]]
                # handle over/underflow.
                if self.registers["PC"] + 1 > len(self.RAM) - 1:
                    second = self.RAM[0]
                else:
                    second = self.RAM[self.registers["PC"] + 1]
                if first == 0x7dc1 and second == self.registers["PC"]:
                    self.stop = True
            return self.stop

