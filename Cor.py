
from worldview.WPoint import *
import math
import random

class Cor:
    def __init__(self, tram, pos):
        self.tram = tram
        self.pos = pos      # WPoint
        self.w = 18
        self.h = 18
        self.viu = True  # si és recollit, passa a False

    def pinta(self, w, wv):
        """Pinta el cor si està viu."""
        if not self.viu:
            return
        p = wv.worldToView(self.pos)
        x = p.x
        y = p.y
        s = 15  # mida

        # cor dibuix animat amb tag 'fg'
        w.create_oval(x - s, y - s, x,     y,     fill="red", outline="red", tags=("fg",)) #rodona
        w.create_oval(x,     y - s, x + s, y,     fill="red", outline="red", tags=("fg",)) #rodona
        w.create_polygon(   #triangle a sota
            x - s, y,
            x + s, y,
            x,     y + s*1.5,
            fill="red", outline="red", tags=("fg",)
        )
