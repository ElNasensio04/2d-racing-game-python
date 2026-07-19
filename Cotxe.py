

import numpy as np
import math
import random
from Tram import *               # Tram, TramCurva
from worldview.WPoint import WPoint


class Cotxe:
    """
    Representa un cotxe (jugador o enemic) que es mou per trams rectes i corbes.

    Atributs principals:
    - pos (WPoint): posició de la cantonada superior-esquerra del cotxe en coordenades del món.
    - w, h (float): amplada i alçada del cotxe.
    - v (float): velocitat (unitats per tick lògic).
    - direction (WPoint): direcció general (signe) en trams rectes.
    - player (bool): True si és el jugador, False si és un enemic.
    - tram (Tram o TramCurva): tram actual on es troba el cotxe.
    - angle (graus): orientació del cotxe per a pintar-lo.
    - carril (0/1): carril esquerre o dret.
    - immunitat (int): ticks restants en els que no pot col·lisionar.
    - i (int): índex del punt actual dins d’un TramCurva (per a seguir la corba).
    - spawn (WPoint): punt de reaparició.
    """

    CURVA_VMAX = 17  # màxima “velocitat efectiva” a corba.

    def __init__(self, x, y, w, h, v=10, dirx=1, diry=1, player=False):
        self.pos = WPoint(x, y)
        self.w = w
        self.h = h
        self.v = v
        self.direction = WPoint(dirx, diry)
        self.player = player

        self.tram = None        # s’assigna des de fora després de crear els trams
        self.angle = 0
        self.carril = 0

        self.immunitat = 0
        self.i = 0               # índex del punt dins d’un TramCurva
        self.punts=0

        # Canvi de carril automàtic només per a enemics
        if not self.player:
            self.ticks_per_canvi = 0
            self.interval_canvi = random.randint(10, 30)  # cada tick són ~0.05s 

    # ---------------------------------------------------------------------
    # Actualització de tram/orientació
    # ---------------------------------------------------------------------

    def actualitza_tram(self):
        """
        Comprova si el cotxe ha sortit del tram actual i, si cal, passa al següent tram
        mantenint una posició coherent (tant per a rectes com per a corbes).
        """
        if self.tram is None:
            return

        centro = WPoint(self.pos.x + self.w/2, self.pos.y + self.h/2)

        # --- TRAM RECTE ---
        if isinstance(self.tram, Tram):
            if not self.tram.punt_dins(centro):
                # treure del tram actual si hi és
                if self in self.tram.cotxes:
                    self.tram.cotxes.remove(self)

                nxt = self.tram.next_tram[self.carril]
                if nxt:
                    self.tram = nxt
                    self.tram.cotxes.append(self)

                    # Actualitzar posició/angle segons tipus de tram
                    if isinstance(nxt, TramCurva):
                        self.i = 0   # reset d'índex de corba
                        punts = nxt.carril0 if self.carril == 0 else nxt.carril1
                        p = punts[0]
                        self.pos.x = p.x - self.w/2
                        self.pos.y = p.y - self.h/2
                        dx = punts[1].x - punts[0].x
                        dy = punts[1].y - punts[0].y
                    else:
                        dx = nxt.p2.x - nxt.p1.x
                        dy = nxt.p2.y - nxt.p1.y

                    self.angle = math.degrees(math.atan2(dy, dx))

        # --- TRAM CORBA ---
        elif isinstance(self.tram, TramCurva):
            punts = self.tram.carril0 if self.carril == 0 else self.tram.carril1

            # si ha arribat al final de la corba , passa al següent tram
            if self.i >= len(punts) - 1:
                if self in self.tram.cotxes:
                    self.tram.cotxes.remove(self)

                nxt = self.tram.next_tram[self.carril]
                if nxt:
                    self.tram = nxt
                    self.i = 0
                    self.tram.cotxes.append(self)

                    # Angle segons nou tram
                    if isinstance(nxt, Tram):
                        dx = nxt.p2.x - nxt.p1.x
                        dy = nxt.p2.y - nxt.p1.y
                    else:
                        punts2 = nxt.carril0 if self.carril == 0 else nxt.carril1
                        dx = punts2[1].x - punts2[0].x
                        dy = punts2[1].y - punts2[0].y

                    self.angle = math.degrees(math.atan2(dy, dx))

    # ---------------------------------------------------------------------
    # Velocitat per al HUD
    # ---------------------------------------------------------------------

    def speed_hud(self):
        """
        Retorna la velocitat que ha de mostrar el velocímetre.
        A corba es limita a CURVA_VMAX; en recta retorna self.v.
        """
        if isinstance(self.tram, TramCurva):
            return min(self.v, self.CURVA_VMAX)
        return self.v

    # ---------------------------------------------------------------------
    # Moviment
    # ---------------------------------------------------------------------

    def mou_auto(self):
        """
        Mou el cotxe segons el tipus de tram:
        - En corbes: avança pel vector de punts del carril, amb velocitat capada amb V_CURVA_VMAX.
        - En rectes: avança segons la direcció del tram, corregint per l’equació del carril.
        També gestiona el canvi al següent tram quan acaba una corba.
        """
        if self.tram is None:
            return

        # ----------------- CORBA -----------------
        if isinstance(self.tram, TramCurva):
            v_eff = min(self.v, self.CURVA_VMAX)

            # avançar l'índex segons velocitat efectiva
            step_i = max(1, int(v_eff / 3))  # ajusta el divisor segons densitat de punts
            punts = self.tram.carril0 if self.carril == 0 else self.tram.carril1

            if self.player:
                self.i += step_i
            else:
                self.i -= step_i

            # si hem acabat la corba → saltar al següent tram
            if self.player:
                if self.i >= len(punts):
                    self.i = 0
                    if isinstance(self.tram.next_tram, list):
                        self.tram = self.tram.next_tram[self.carril]
                    else:
                        self.tram = self.tram.next_tram

                    if isinstance(self.tram, Tram):
                        eq = self.tram.eq_left if self.carril == 0 else self.tram.eq_right
                        if eq.getM() != math.inf:
                            cy = eq.getY(self.tram.p1.x)
                            self.pos.y = cy - self.h/2
                            self.pos.x = self.tram.p1.x - self.w/2
                        else:
                            cx = eq.getX(self.tram.p1.y)
                            self.pos.x = cx - self.w/2
                            self.pos.y = self.tram.p1.y - self.h/2
                    return
            else:
                if self.i < 0:
                    # enemic que ha finalitzat la corba en sentit contrari → reapareix al seu spawn
                    self.i = len(punts) - 1
                    self.pos.x = self.spawn.x
                    self.pos.y = self.spawn.y
                    self.v = random.randint(5, 20)
                    return

            # punt actual de la corba
            p = punts[self.i]

            # angle momentani (en funció del segment local)
            if self.player:
                if self.i > 0:
                    p0 = punts[self.i - 1]
                    dx = p.x - p0.x
                    dy = p.y - p0.y
                    self.angle = math.degrees(math.atan2(dy, dx))
            else:
                if self.i < len(punts) - 1:
                    p0 = punts[self.i + 1]
                    dx = p.x - p0.x
                    dy = p.y - p0.y
                    self.angle = math.degrees(math.atan2(dy, dx))

            # col·locació real del cotxe (la posició guarda cantonada superior-esquerra)
            self.pos.x = p.x - self.w/2
            self.pos.y = p.y - self.h/2

            self._lane_change_tick()
            return

        # ----------------- RECTE -----------------
        # equació del carril triat
        eq = self.tram.eq_left if self.carril == 0 else self.tram.eq_right

        # direcció del tram
        d = np.array(self.tram.direction)

        # invertir si el cotxe va en sentit contrari (segons signe de self.direction)
        if self.direction.x < 0 or self.direction.y < 0:
            d = -d

        step = self.v

        # avançar
        self.pos.x += d[0] * step
        self.pos.y += d[1] * step

        # corregir posició usant l’equació del carril
        cx = self.pos.x + self.w / 2
        cy = self.pos.y + self.h / 2

        # correcció segons orientació del tram
        if eq.getM() != math.inf:
            cy = eq.getY(cx)
            self.pos.y = cy - self.h / 2
        else:
            cx = eq.getX(cy)
            self.pos.x = cx - self.w / 2

        p_centro = WPoint(cx, cy)

        # jugador: no fem res més 
        if self.player:
            return

        # enemics: si surten de l’asfalt, reapareixen i canvien velocitat per fer-ho més entretingut
        if not self.tram.punt_dins(p_centro):
            self.pos.x = self.spawn.x
            self.pos.y = self.spawn.y
            self.v = random.randint(5, 20)
            return

        self._lane_change_tick()

    # ---------------------------------------------------------------------
    # Canvi de carril automàtic (enemics)
    # ---------------------------------------------------------------------

    def _lane_change_tick(self):
        """
        Controla el canvi de carril automàtic dels enemics amb un interval aleatori.
        El jugador no canvia carril automàticament.
        """
        if self.player:
            return

        self.ticks_per_canvi += 1
        if self.ticks_per_canvi >= self.interval_canvi:
            if random.random() < 0.75:  # 75% de probabilitat de canviar carril
                # En trams corbs, els punts de carrils estan alineats per índex → mantenim self.i
                self.canvia_carril()

            # reiniciar comptador i triar nou interval
            self.ticks_per_canvi = 0
            self.interval_canvi = random.randint(10, 30)

    def canvia_carril(self):
        """
        Alterna entre carril 0 i 1 mantenint la posició longitudinal.
        En corba, conserva l'índex self.i perquè ambdós carrils estan sincronitzats.
        """
        if self.tram is None:
            return

        # alternar carril
        nou_carril = 1 - self.carril

        # ----- Corba -----
        if isinstance(self.tram, TramCurva):
            punts_from = self.tram.carril0 if self.carril == 0 else self.tram.carril1
            punts_to   = self.tram.carril0 if nou_carril == 0 else self.tram.carril1
            if not punts_from or not punts_to:
                return

            # assegurar índex vàlid
            i = min(max(self.i, 0), len(punts_to) - 1)

            # reposicionar al punt equivalent de l’altre carril
            p = punts_to[i]
            self.pos.x = p.x - self.w/2
            self.pos.y = p.y - self.h/2

            # actualitzar angle local
            if i > 0:
                p0 = punts_to[i - 1]
                dx = p.x - p0.x
                dy = p.y - p0.y
                self.angle = math.degrees(math.atan2(dy, dx))
            elif len(punts_to) >= 2:
                dx = punts_to[1].x - punts_to[0].x
                dy = punts_to[1].y - punts_to[0].y
                self.angle = math.degrees(math.atan2(dy, dx))

            self.carril = nou_carril
            return

        # ----- Recte -----
        # vector del tram
        dx = self.tram.p2.x - self.tram.p1.x
        dy = self.tram.p2.y - self.tram.p1.y
        longitud = np.hypot(dx, dy)
        dir_unit = np.array([dx / longitud, dy / longitud])

        # vector perpendicular (lateral)
        nx = -dir_unit[1]
        ny = dir_unit[0]

        # meitat d’un carril
        w = self.tram.width / 4
        offset = -w if nou_carril == 0 else w

        # posició actual del centre del cotxe
        cx = self.pos.x + self.w / 2
        cy = self.pos.y + self.h / 2

        # projecció longitudinal del centre sobre el tram
        px = np.array([self.tram.p1.x, self.tram.p1.y])
        centro = np.array([cx, cy])
        v = centro - px
        longitud_proj = np.dot(v, dir_unit)

        # nova posició = inici + projecció longitudinal + desplaçament lateral
        new_cx = self.tram.p1.x + dir_unit[0]*longitud_proj + nx*offset
        new_cy = self.tram.p1.y + dir_unit[1]*longitud_proj + ny*offset

        # actualitzar posició real (cantonada superior-esquerra)
        self.pos.x = new_cx - self.w / 2
        self.pos.y = new_cy - self.h / 2

        self.carril = nou_carril

    # ---------------------------------------------------------------------
    # Dibuix
    # ---------------------------------------------------------------------

    def pinta(self, w, wv):
        """
        Dibuixa el cotxe al canvas (jugador en vermell, enemics en gris).
        Aplica una rotació segons self.angle.
        """
        cx = self.pos.x + self.w / 2
        cy = self.pos.y + self.h / 2
        rad = math.radians(self.angle)

        def rot(x, y):
            xr = x * math.cos(rad) - y * math.sin(rad) + cx
            yr = x * math.sin(rad) + y * math.cos(rad) + cy
            return wv.worldToView(WPoint(xr, yr))

        # cos del cotxe (rectangle)
        corners = [
            (-self.w/2, -self.h/2),
            ( self.w/2, -self.h/2),
            ( self.w/2,  self.h/2),
            (-self.w/2,  self.h/2)
        ]
        punts = []
        for x, y in corners:
            p = rot(x, y)
            punts.extend([p.x, p.y])

        
        if getattr(self, "player", False):
                # --- Colors base ---
            body_color = "#d71414"       # vermell McQueen
            bolt_fill = "#ffd200"        # groc rayo
            bolt_outline = "#ff8f00"     # contorn taronja del raig

            # Carrosseria (rectangle rotat original)
            w.create_polygon(punts, fill=body_color, outline="black", width=1, tags=("fg",))

            # Raig lateral simplificat (forma en zigzag suau)
            SX = 2
            SY = 1.6

            bolt = [
                (-self.w*0.20*SX,  self.h*0.06*SY),
                (-self.w*0.06*SX,  self.h*0.10*SY),
                ( self.w*0.00*SX,  self.h*0.02*SY),
                ( self.w*0.16*SX,  self.h*0.02*SY),
                ( self.w*0.02*SX, -self.h*0.08*SY),
                (-self.w*0.04*SX, -self.h*0.02*SY),
            ]
            bolt_pts = []
            for x, y in bolt:
                p = rot(x, y)
                bolt_pts.extend([p.x, p.y])
            w.create_polygon(bolt_pts, fill=bolt_fill, outline=bolt_outline, width=2, tags=("fg",))

            # Número 95 
            num_pos = rot(-self.w*0.05, self.h*0.06)
            font_size = max(20, int(self.h * 0.6))  
            w.create_text(num_pos.x + 1, num_pos.y + 1, text="95",
                        fill="black", font=("Arial", font_size, "bold"), tags=("fg",))
            w.create_text(num_pos.x, num_pos.y, text="95",
                        fill="#25241f", font=("Arial", font_size, "bold"), tags=("fg",))

            # Rodes simplificades: banda negra + toc de llanda blanca
            roda_pos = [
                (-self.w*0.35, -self.h*0.55),
                ( self.w*0.35, -self.h*0.55),
                (-self.w*0.35,  self.h*0.35),
                ( self.w*0.35,  self.h*0.35)
            ]
            tire_w = self.w*0.20  # longitud del traç de la roda
            for rx, ry in roda_pos:
                # banda negra
                r_out_l = rot(rx - tire_w/2, ry)
                r_out_r = rot(rx + tire_w/2, ry)
                w.create_line(r_out_l.x, r_out_l.y, r_out_r.x, r_out_r.y, width=5, fill="black", tags=("fg",))
                # llanda blanca (més fina, a sobre)
                r_in_l = rot(rx - tire_w*0.30, ry)
                r_in_r = rot(rx + tire_w*0.30, ry)
                w.create_line(r_in_l.x, r_in_l.y, r_in_r.x, r_in_r.y, width=2, fill="white", tags=("fg",))


        else:
            # --- Enemics ---
            w.create_polygon(punts, fill="#f2f2f2", outline="black", tags=("fg",))

            # Finestres
            win = [
                (-self.w*0.2, -self.h*0.25),
                ( self.w*0.2, -self.h*0.25),
                ( self.w*0.2,  self.h*0.25),
                (-self.w*0.2,  self.h*0.25)
            ]
            punts_win = []
            for x, y in win:
                p = rot(x, y)
                punts_win.extend([p.x, p.y])
            w.create_polygon(punts_win, fill="#9ecae1", outline="", tags=("fg",))  # blau clar

            # Morro
            m1 = rot(self.w/2, -self.h/4)
            m2 = rot(self.w/2,  self.h/4)
            w.create_line(m1.x, m1.y, m2.x, m2.y, width=3, tags=("fg",))

            # Rodes
            roda_pos = [
                (-self.w*0.35, -self.h*0.55),
                ( self.w*0.35, -self.h*0.55),
                (-self.w*0.35,  self.h*0.35),
                ( self.w*0.35,  self.h*0.35)
            ]
            for rx, ry in roda_pos:
                r1 = rot(rx - self.w*0.07, ry)
                r2 = rot(rx + self.w*0.07, ry)
                w.create_line(r1.x, r1.y, r2.x, r2.y, width=3, tags=("fg",))

    # ---------------------------------------------------------------------
    # Tick lògic i col·lisions
    # ---------------------------------------------------------------------

    def mou_tick(self):
        """
        Un tick de simulació del cotxe: baixa immunitat, es mou i actualitza tram.
        """
        prev_x=self.pos.x
        prev_y=self.pos.y

        if self.immunitat > 0:
            self.immunitat -= 1
        self.mou_auto()
        self.actualitza_tram()
        
        dx = self.pos.x - prev_x
        dy = self.pos.y - prev_y
        self.punts += math.hypot(dx, dy)
    
    def reset_punts(self):
        self.punts = 0.0

    def get_punts(self):
        return self.punts


    def colisiona_amb(self, altres, marge=5):
        """
        Comprova col·lisió AABB amb una llista d’altres cotxes.
        Retorna True si hi ha col·lisió i activa una finestra d’immunitat.
        """
        if self.immunitat > 0:
            return False  # està immunitzat

        # Centre del cotxe actual
        cx = self.pos.x + self.w / 2
        cy = self.pos.y + self.h / 2

        for o in altres:
            if o == self:
                continue

            # Centre de l’altre cotxe
            ox = o.pos.x + o.w / 2
            oy = o.pos.y + o.h / 2

            # Distància absoluta entre centres
            dist_x = abs(cx - ox)
            dist_y = abs(cy - oy)

            # Mida combinada menys marge
            limit_x = (self.w + o.w) / 2 - marge
            limit_y = (self.h + o.h) / 2 - marge

            if dist_x < limit_x and dist_y < limit_y:
                self.immunitat = 8
                return True  # hi ha col·lisió

        return False  # no hi ha col·lisió

    def agafa_cor(self, cors):
        """
        Revisa col·lisió amb cors . Si n’agafa algun:
        - marca el cor com a no viu
        - suma 1 vida (fins a un màxim de 3)
        Retorna True si n’ha agafat algun.
        """
        px1 = self.pos.x
        py1 = self.pos.y
        px2 = self.pos.x + self.w
        py2 = self.pos.y + self.h
        agafat = False

        for c in cors:
            if not c.viu:
                continue

            # El cor es pinta centrat 
            cx1 = c.pos.x - c.w/2
            cy1 = c.pos.y - c.h/2
            cx2 = cx1 + c.w
            cy2 = cy1 + c.h

            if (px1 < cx2 and px2 > cx1 and py1 < cy2 and py2 > cy1):
                c.viu = False
                self.vida += 1
                self.vida = min(self.vida, 3)
                agafat = True

        return agafat
    
    def guardar_pos(self):
        """Guarda l’estat actual com a punt de spawn."""
        self._spawn = {
            "pos": WPoint(self.pos.x, self.pos.y),
            "tram": self.tram,
            "carril": getattr(self, "carril", 0),
            "i": getattr(self, "i", 0),
            "angle": getattr(self, "angle", 0)
        }
    def restaurar_pos(self, velocitat=True):
        """Restaura l’estat des del punt de spawn guardat."""
        
        s = getattr(self, "_spawn", None)
        if s is None:
            # Si mai s’ha definit, fem servir l’estat actual com a spawn
            self.guardar_pos()
            s = self._spawn

        self.pos.x = s["pos"].x
        self.pos.y = s["pos"].y
        self.tram = s["tram"]
        self.carril = s["carril"]
        self.i = s["i"]
        self.angle = s["angle"]

        if velocitat:
            self.v = random.randint(5, 20)
        else:
            self.v = 0

        self.immunitat = 0
        self.vida = 1



