import math

class WPoint:
    def __init__(self, x=0.0, y=0.0):   #Podem cridar al contructor sense passar cap paràmetre fent el punt (0,0)
        self.x = x
        self.y = y

    #Calcula la distància entre 2 WPoint's
    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    #Per mostrar els valors en cas de fer un print a un obejcte d'aquesta classe
    def __repr__(self):
        return f"({self.x},{self.y})"