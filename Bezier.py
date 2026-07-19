
from worldview.WPoint import *

def curva_bezier(p0, d0, p1, d1, pasos):
    # p0, p1 = WPoint inici i final
    # d0, d1 = WPoint direcció (vector unitari) de cada extrem
    # pasos = nombre de punts de la corba
    
    # Punts de control: extrems + tangents escalades
    scale = p0.distance(p1)/3  # escala dels vectors tangents
    c0 = p0
    c1 = WPoint(p0.x + d0.x*scale, p0.y + d0.y*scale)
    c2 = WPoint(p1.x - d1.x*scale, p1.y - d1.y*scale)
    c3 = p1

    punts = []
    for t in range(pasos+1):
        u = t/pasos
        x = (
            (1-u)**3*c0.x +
            3*(1-u)**2*u*c1.x +
            3*(1-u)*u**2*c2.x +
            u**3*c3.x
        )
        y = (
            (1-u)**3*c0.y +
            3*(1-u)**2*u*c1.y +
            3*(1-u)*u**2*c2.y +
            u**3*c3.y
        )
        punts.append(WPoint(x, y))
    return punts