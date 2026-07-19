
import random
import numpy as np
from Cor import *
from worldview.WPoint import *
from worldview.LinearEquation import *
from Bezier import *
import math

class Tram:
    def __init__(self, position, direction, distance, angle=0, width=100):
        self.p1 = position
        # direcció unitària del tram
        self.direction = np.array([direction.x, direction.y])
        self.direction = self.direction / np.linalg.norm(self.direction)

        # punt final calculat
        self.p2 = WPoint(
            self.p1.x + self.direction[0] * distance,
            self.p1.y + self.direction[1] * distance
        )

        self.distance = distance
        self.angle = angle
        self.width = width
        self.eq = LinearEquation(self.p1, self.p2)
        self._calcula_carrils()
        self.cotxes = []
        self.next_tram = [None, None]  # enllaç a següent tram per carril (0/1)
        self._calcula_poligon()

    def _calcula_poligon(self):
        """Calcula el polígon (asfalt) rectangular del tram recte."""
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        length = np.sqrt(dx*dx + dy*dy)
        if length == 0:  # evitar divisió per zero
            length = 1

        # normal unitària
        nx = -dy / length
        ny = dx / length
        w = self.width / 2

        left1  = WPoint(self.p1.x + nx*w, self.p1.y + ny*w)
        left2  = WPoint(self.p2.x + nx*w, self.p2.y + ny*w)
        right2 = WPoint(self.p2.x - nx*w, self.p2.y - ny*w)
        right1 = WPoint(self.p1.x - nx*w, self.p1.y - ny*w)

        self.poly = [left1, left2, right2, right1]

    def afegeix_cotxe(self, cotxe):
        """Afegeix un cotxe a aquest tram i l’hi assigna."""
        self.cotxes.append(cotxe)
        cotxe.tram = self

    def punt_dins(self, point: WPoint) -> bool:
        """
        Test de punt-dins-polígon (AABB -> ray casting) per saber si el punt
        cau dins de l’asfalt del tram.
        """
        x = point.x
        y = point.y
        poly = self.poly
        n = len(poly)
        inside = False
        p1x, p1y = poly[0].x, poly[0].y
        for i in range(n+1):
            p2x, p2y = poly[i % n].x, poly[i % n].y
            if ((p1y > y) != (p2y > y)) and (x < (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x):
                inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def get_carril_centro(self, index):
        """
        Retorna un punt al centre del carril 0 o 1 a l’inici del tram.
        Útil per col·locació inicial d’actors.
        """
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        longitud = np.hypot(dx, dy)
        nx = -dy / longitud
        ny = dx / longitud

        w = self.width / 4  # meitat d’un carril
        offset = -w if index == 0 else w

        cx = self.p1.x + nx * offset
        cy = self.p1.y + ny * offset
        return WPoint(cx, cy)

    def pinta(self, w, wv):
        """
        Pinta l’asfalt del tram recte i la línia central discontínua.
        """
        # --- Asfalt ---
        vp = [wv.worldToView(p) for p in self.poly]
        coords = []
        for v in vp:
            coords.extend([v.x, v.y])
        w.create_polygon(coords, fill="#555555", outline="black", tags=("fg",))

        # --- Línia central discontínua (carrils) ---
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        length = np.hypot(dx, dy)
        dir_unit = np.array([dx / length, dy / length])

        dash_len = 30   # longitud del traç pintat
        gap_len  = 20   # separació entre traços
        dist = 0

        while dist < length:
            p_ini = WPoint(
                self.p1.x + dir_unit[0] * dist,
                self.p1.y + dir_unit[1] * dist
            )
            dist += dash_len
            if dist > length:
                break
            p_fin = WPoint(
                self.p1.x + dir_unit[0] * dist,
                self.p1.y + dir_unit[1] * dist
            )
            dist += gap_len

            v1 = wv.worldToView(p_ini)
            v2 = wv.worldToView(p_fin)
            w.create_line(v1.x, v1.y, v2.x, v2.y, fill="white", width=2, tags=("fg",))

    def _calcula_carrils(self):
        """Calcula les rectes (equacions) dels dos carrils paral·lels al tram."""
        # vector direcció del tram
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        L = np.hypot(dx, dy)
        ux, uy = dx / L, dy / L

        # vector normal
        nx, ny = -uy, ux

        offset = self.width / 4  # meitat de carril

        # punts d'inici carrils
        p_left  = WPoint(self.p1.x - nx*offset, self.p1.y - ny*offset)
        p_right = WPoint(self.p1.x + nx*offset, self.p1.y + ny*offset)

        # equacions de carril
        self.eq_left  = LinearEquation(p_left,  WPoint(p_left.x  + dx, p_left.y  + dy))
        self.eq_right = LinearEquation(p_right, WPoint(p_right.x + dx, p_right.y + dy))

    def pinta_fletxa(self, w, wv, carril=0):
        """
        Pinta una fletxa curta al principi del tram indicant el sentit de circulació
        sobre el carril indicat (0 esquerra, 1 dreta).
        """
        # desplaçament lateral del carril
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        L = math.hypot(dx, dy)
        if L == 0:
            return
        ux, uy = dx / L, dy / L        # direcció del tram
        nx, ny = -uy, ux               # normal

        offset = self.width / 4
        if carril == 0:
            offset = -offset

        # punt inici de la fletxa (al principi del tram)
        start = WPoint(self.p1.x + nx * offset, self.p1.y + ny * offset)

        # punta de la fletxa
        tip = WPoint(start.x + ux * 30, start.y + uy * 30)

        vstart = wv.worldToView(start)
        vtip = wv.worldToView(tip)

        # pal
        w.create_line(vstart.x, vstart.y, vtip.x, vtip.y, width=4, tags=("fg",))

        # cap de fletxa
        ang = math.atan2(uy, ux)
        head = 8
        a = math.pi / 6

        p1 = (tip.x - head * math.cos(ang - a), tip.y - head * math.sin(ang - a))
        p2 = (tip.x - head * math.cos(ang + a), tip.y - head * math.sin(ang + a))

        vp1 = wv.worldToView(WPoint(*p1))
        vp2 = wv.worldToView(WPoint(*p2))

        w.create_line(vtip.x, vtip.y, vp1.x, vp1.y, width=4, tags=("fg",))
        w.create_line(vtip.x, vtip.y, vp2.x, vp2.y, width=4, tags=("fg",))
    def _spawn_en_tram_recte(self):
        """Genera un cor en un 'Tram Recte'"""
        d = self.distance
        carril = random.choice([0, 1])
        eq = self.eq_left if carril == 0 else self.eq_right

        # triem una posició al llarg del tram Recte
        k = random.randint(10, max(10, d - 10))
        x = self.p1.x + self.direction[0] * k
        if eq.getM() != math.inf:
            y = eq.getY(x)
        else:
            y = self.p1.y + self.direction[1] * k
            x = eq.getX(y)

        return Cor(self, WPoint(x, y))

class TramCurva:
    def __init__(self, punts, ample=100):
        """
        punts: llista de WPoint definint la corba (p. ex. Catmull/Bezier).
        ample: amplada total de l’asfalt (com als trams rectes).
        """

        self.punts = punts
        self.ample = ample
        self.cotxes = []                 # cotxes a la corba
        self.poly = []                   # polígon de l'asfalt
        self.next_tram = [None, None]    # enllaç següent (per carril)
        self.generar_poligon()
        self.carril0 = []   # esquerra
        self.carril1 = []   # dreta
        self.generar_carrils()  # genera carrils sobre l’asfalt corb

    def generar_poligon(self):
        """Construeix el polígon de l’asfalt a partir de la normal als punts de la corba."""
        left = []
        right = []

        for i in range(len(self.punts)):
            p = self.punts[i]

            # vector tangent (derivada aproximada)
            if i == 0:
                dx = self.punts[i+1].x - p.x
                dy = self.punts[i+1].y - p.y
            elif i == len(self.punts)-1:
                dx = p.x - self.punts[i-1].x
                dy = p.y - self.punts[i-1].y
            else:
                dx = self.punts[i+1].x - self.punts[i-1].x
                dy = self.punts[i+1].y - self.punts[i-1].y

            # normal unitària
            length = math.hypot(dx, dy) or 1
            nx = -dy / length
            ny = dx / length

            half = self.ample / 2
            left.append(WPoint(p.x + nx*half, p.y + ny*half))
            right.append(WPoint(p.x - nx*half, p.y - ny*half))

        # polígon: esquerra + dreta invertida
        self.poly = left + right[::-1]

    def punt_dins(self, point: WPoint) -> bool:
        """
        Test de punt-dins-polígon per l’asfalt corb.
        """
        x = point.x
        y = point.y
        poly = self.poly
        n = len(poly)
        inside = False
        p1x, p1y = poly[0].x, poly[0].y

        for i in range(n + 1):
            p2x, p2y = poly[i % n].x, poly[i % n].y
            if ((p1y > y) != (p2y > y)) and (x < (p2x - p1x)*(y - p1y) / (p2y - p1y) + p1x):
                inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def generar_carrils(self):
        """Construeix els dos carrils (0/1) desplaçats a banda i banda del centre de la corba."""
        if len(self.punts) < 2:
            print("Error: corba amb menys de 2 punts, no es poden generar carrils")
            return

        self.carril0 = []
        self.carril1 = []

        w = self.ample / 4   # igual que en rectes (meitat del carril)

        for i in range(len(self.punts)):
            p = self.punts[i]

            # tangent local
            if i == 0:
                dx = self.punts[i+1].x - p.x
                dy = self.punts[i+1].y - p.y
            elif i == len(self.punts)-1:
                dx = p.x - self.punts[i-1].x
                dy = p.y - self.punts[i-1].y
            else:
                dx = self.punts[i+1].x - self.punts[i-1].x
                dy = self.punts[i+1].y - self.punts[i-1].y

            # normal unitària
            length = math.hypot(dx, dy) or 1
            nx = -dy / length
            ny = dx / length

            # dos carrils
            self.carril0.append(WPoint(p.x + nx*(-w), p.y + ny*(-w)))  # esquerra
            self.carril1.append(WPoint(p.x + nx*( w), p.y + ny*( w)))  # dreta

    def longitud(self):
        """Longitud total aproximada de la corba (suma de segments entre punts consecutius)."""
        dist = 0
        for i in range(1, len(self.punts)):
            dx = self.punts[i].x - self.punts[i-1].x
            dy = self.punts[i].y - self.punts[i-1].y
            dist += math.hypot(dx, dy)
        return dist

    def get_carril_centro(self, index):
        """Retorna un punt aproximadament centrat al carril 0/1 al voltant del mig de la corba."""
        if len(self.punts) < 2:
            return self.punts[0]

        # punt central aproximat
        p_idx = len(self.punts)//2
        p = self.punts[p_idx]

        # tangent aproximada
        if p_idx < len(self.punts)-1:
            dx = self.punts[p_idx+1].x - p.x
            dy = self.punts[p_idx+1].y - p.y
        else:
            dx = p.x - self.punts[p_idx-1].x
            dy = p.y - self.punts[p_idx-1].y

        norm = math.hypot(dx, dy) or 1
        dx /= norm
        dy /= norm

        # normal
        nx = -dy
        ny = dx

        # offset segons carril
        w = self.ample / 4
        offset = -w if index == 0 else w

        return WPoint(p.x + nx*offset, p.y + ny*offset)

    def pinta(self, w, wv, color="#555555"):
        """
        Pinta l’asfalt i la línia central discontínua interpolada entre carrils.
        """
        if not self.poly:
            return

        # --- Asfalt ---
        punts_canvas = []
        for p in self.poly:
            v = wv.worldToView(p)
            punts_canvas.extend([v.x, v.y])
        w.create_polygon(punts_canvas, fill=color, outline="black", tags=("fg",))

        if not self.carril0 or not self.carril1:
            print("No hi ha carrils definits")
            return

        # --- Línia central discontínua ---
        coords = []
        for p0, p1 in zip(self.carril0, self.carril1):
            cx = (p0.x + p1.x) / 2
            cy = (p0.y + p1.y) / 2
            v = wv.worldToView(WPoint(cx, cy))
            coords.extend([v.x, v.y])

        if len(coords) >= 4:
            w.create_line(*coords, fill="white", width=2, dash=(30, 20), tags=("fg",))
    def _spawn_en_tram_corb(self):
        """
        Genera un cor sobre els trams corbs.
        """
        # Preferim carrils per centrar el cor
        if getattr(self, "carril0", None) and getattr(self, "carril1", None):
            n = min(len(self.carril0), len(self.carril1))
            if n >= 2:
                i = random.randint(1, n - 2)  # evita els extrems
                p0 = self.carril0[i]
                p1 = self.carril1[i]
                cx = (p0.x + p1.x) / 2.0
                cy = (p0.y + p1.y) / 2.0
            return Cor(self, WPoint(cx, cy))

        punts = getattr(self, "punts", None) 
    
        if punts and len(punts) >= 2:
            i = random.randint(1, len(punts) - 2)
            p = punts[i]
            return Cor(self, WPoint(p.x, p.y))

        return None
    
def spawn_cor(trams, trams_corbs, cors, p_curva=0.35):
    """
    Genera un cor en un tram aleatori.
    - p_curva: probabilitat d'usar un tram corb si n'hi ha (he posat 35% pq als corbs sembla que és més fàcil d'agafarlos).
    Afegeix el cor a la llista 'cors'.
    """
    usar_corba = bool(trams_corbs) and (random.random() < p_curva)

    if usar_corba:
        corba = random.choice(trams_corbs)
        cor = corba._spawn_en_tram_corb()
        if cor:
            cors.append(cor)
            return cor

    if trams:
        t = random.choice(trams)
        cor = t._spawn_en_tram_recte()
        cors.append(cor)
        return cor

    return None

def unir_trams_amb_corba(tram1, tram2, passos=200, ample=100):
    """
    Uneix dos trams rectes amb una corba suau (Bezier) i retorna un TramCurva.
    """
    # vectors direcció unitaris
    dx1, dy1 = tram1.direction[0], tram1.direction[1]
    dx2, dy2 = tram2.direction[0], tram2.direction[1]
    norm1 = math.hypot(dx1, dy1) or 1
    norm2 = math.hypot(dx2, dy2) or 1
    d0 = WPoint(dx1/norm1, dy1/norm1)
    d1 = WPoint(dx2/norm2, dy2/norm2)

    # punts extrems dels trams
    p0 = tram1.p2
    p1 = tram2.p1

    # generar corba central
    punts = curva_bezier(p0, d0, p1, d1, passos)

    # crear TramCurva amb punts
    corba = TramCurva(punts, ample=ample)
    corba.generar_carrils()
    return corba


