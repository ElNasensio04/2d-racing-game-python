
class VPoint:   #x,y són enters, ja que són pixels de pantalla
    def __init__(self,x,y):
        self.x=x
        self.y=y

        #Per mostrar els valors en cas de fer un print a un obejcte d'aquesta classe
    def __repr__(self):
        return f"({self.x},{self.y})"
    
