
from tkinter import *
import time
import json
import keyboard
import random
import numpy as np         
import math                
from Cor import *          # Cor, spawn_cor (trams_corbs)
from Cotxe import *        # Cotxe
from Fons import *         # pintar_fons, draw_lives_hearts, draw_speedometer
from Tram import *         # Classe Tram , classe TramCurva, unir_trams_amb_corba
from Soroll import *       # reproduir_sense_bloquejar, so_xoc, so_cor
from MenuJoc import *      # MenuManager
from pathlib import Path
from worldview.VPoint import *
from worldview.WPoint import *
from worldview.WorldView import *


# ---------------------------------------------------------------------
# Lectura del circuit i cotxes des de JSON
# ---------------------------------------------------------------------
def lectura_json(fitxer):
    f=open(fitxer,"r")
    dades=json.load(f)

    cotxes = []
    trams = []

    # --- Crear trams rectes ---
    for s in dades["sections"]:
        pos = WPoint(s["position"]["x"], s["position"]["y"])
        dir = WPoint(s["direction"]["x"], s["direction"]["y"])
        tram = Tram(pos, dir, s["distance"], s["angle"])
        trams.append(tram)

    for t in trams:
        t.cotxes = []

    # ---------------------------------------------------------
    # Crear CORBES entre cada tram recte
    # ---------------------------------------------------------
    trams_corbs = []
    for t in trams:
        if not isinstance(t.next_tram, list):
            t.next_tram = [None, None]

    for i in range(len(trams)):
        t_actual = trams[i]
        t_seguent = trams[(i + 1) % len(trams)]

        tram_corba = unir_trams_amb_corba(t_actual, t_seguent, passos=100, ample=100)
        trams_corbs.append(tram_corba)

        if not isinstance(tram_corba.next_tram, list):
            tram_corba.next_tram = [None, None]

        # Enllaços carril 0/1 → corba → següent tram
        t_actual.next_tram[0] = tram_corba
        t_actual.next_tram[1] = tram_corba
        tram_corba.next_tram[0] = t_seguent
        tram_corba.next_tram[1] = t_seguent

    # Llista unificada de trams
    tots_trams = trams + trams_corbs

    # ---------------------------------------------------------
    # Crear COTXES des del JSON (1 jugador + 8 enemics (1 per tram))
    # ---------------------------------------------------------
    for idx, c in enumerate(dades["cars"]):
        dirx = c["direction"]["x"]
        diry = c["direction"]["y"]

        cotxe = Cotxe(
            c["start_position"]["x"],
            c["start_position"]["y"],
            c["width"],
            c["height"],
            dirx=dirx,
            diry=diry,
            player=c.get("player", False)
        )

        pos_centre = WPoint(cotxe.pos.x + cotxe.w/2,
                            cotxe.pos.y + cotxe.h/2)

        tram_assignat = None

        # Detectar tram on es troba el cotxe
        for t in tots_trams:
            if t.punt_dins(pos_centre):
                tram_assignat = t
                break

        if tram_assignat is None:
            # Fallback si cau fora: assignar per índex
            tram_assignat = tots_trams[idx % len(tots_trams)]

        cotxe.tram = tram_assignat

        # -----------------------------------------------------
        # Col·locació segons tipus de tram
        # -----------------------------------------------------

        # --- Jugador ---
        if c.get("player", False):
            tram_assignat.cotxes.append(cotxe)
            cotxe.v=random.randint(5,20)
            cotxe.carril = 0
            cotxe.i = 0

        # --- Enemics ---
        else:
            # ---------------------------------
            #  SI ÉS CORBA
            # ---------------------------------
            if isinstance(tram_assignat, TramCurva):
                cotxe.carril = random.choice([0, 1])
                punts = tram_assignat.carril0 if cotxe.carril == 0 else tram_assignat.carril1

                cotxe.i = len(punts) - 1
                p = punts[cotxe.i]

                cotxe.pos.x = p.x - cotxe.w/2
                cotxe.pos.y = p.y - cotxe.h/2

                if cotxe.i > 0:
                    p0 = punts[cotxe.i - 1]
                else:
                    p0 = punts[cotxe.i]

                dx = p.x - p0.x
                dy = p.y - p0.y

                cotxe.angle = math.degrees(math.atan2(dy, dx)) + 180

                cotxe.v = random.randint(5, 10)
                cotxe.spawn = WPoint(cotxe.pos.x, cotxe.pos.y)
                tram_assignat.cotxes.append(cotxe)

            # ---------------------------------
            # SI ÉS RECTE
            # ---------------------------------
            else:
                dx = tram_assignat.p2.x - tram_assignat.p1.x
                dy = tram_assignat.p2.y - tram_assignat.p1.y
                L = np.hypot(dx, dy)
                ux, uy = dx/L, dy/L

                enrere = 10
                cotxe.pos.x = tram_assignat.p2.x - ux*enrere - cotxe.w/2
                cotxe.pos.y = tram_assignat.p2.y - uy*enrere - cotxe.h/2
                cotxe.spawn = WPoint(cotxe.pos.x, cotxe.pos.y)
                cotxe.angle = math.degrees(math.atan2(dy, dx)) + 180
                cotxe.v = random.randint(6, 20)

            tram_assignat.cotxes.append(cotxe)

        cotxes.append(cotxe)

    return cotxes, trams, trams_corbs


# ---------------------------------------------------------------------
# Inicialització Tk / Canvas i món
# ---------------------------------------------------------------------
tk = Tk()
w = Canvas(tk, width=800, height=600)
w.pack()
tk.focus_force()

cotxes, trams, trams_corbs = lectura_json("carretera.json")

# Jugador (primer cotxe del JSON)
c = cotxes[0]
c.vida = 1

# Guardar SPAWN fix perquè sempre reaparegui al mateix lloc
c.guardar_pos()

# Finestra del món (segueix al jugador)

wv = WorldView(
    WPoint(c.pos.x , c.pos.y ),
    WPoint(c.pos.x , c.pos.y),
    VPoint(0, 0),
    VPoint(600, 400)
)

# Control
prev_pos = WPoint(c.pos.x, c.pos.y)
prev_c = False
prev_a = False
prev_s = False

cors = []
tick = 0

# ---------------------------------------------------------------------
# Fons i menú
# ---------------------------------------------------------------------
pintar_fons(w, 800, 600, tema="grass")  
w.tag_lower("bg")

Menu = MenuManager(
    tk, w, width=800, height=600,
    pintar_fons_cb=pintar_fons,           
    on_restart_cb=None,            
    jugador=c,
    world_view=wv,
    prev_pos_ref=prev_pos,
    cors_list_ref=cors
)



# ---------------------------------------------------------------------
# Bucle principal del joc
# ---------------------------------------------------------------------
while True:

    # Pauses/menú: mantenim UI reactiva sense simular
    if Menu.estat != "GAME":
        Menu.tick_idle()
        continue
    if Menu.pausat:
        Menu.tick_idle()
        continue

    # Neteja foreground
    w.delete("fg")

    # Moviment jugador 
    c.mou_tick()

    # Canviar carril
    pressed = keyboard.is_pressed("c")
    if pressed and not prev_c:
        c.canvia_carril()
    prev_c = pressed

    # Accelerar / frenar
    pressed_a = keyboard.is_pressed("a")
    if pressed_a and not prev_a:
        c.v += 1
    prev_a = pressed_a

    pressed_s = keyboard.is_pressed("s")
    if pressed_s and not prev_s:
        c.v = max(0, c.v - 1)
    prev_s = pressed_s

    #  Moviment enemics 
    for cc in cotxes[1:]:
        cc.mou_auto()

    #  Col·lisions amb enemics 
    enemics = cotxes[1:]
    if c.colisiona_amb(enemics):
        reproduir_sense_bloquejar(so_xoc)
        c.vida -= 1
        if c.vida <= 0:                      
            c.vida = 1
            Menu.pintar_gameover(score_text=f"Punts = {int(c.get_punts())}")
            continue

    # Càmera segueix el jugador
    dx = c.pos.x - prev_pos.x
    dy = c.pos.y - prev_pos.y
    wv.translateWindow(dx, dy)
    prev_pos.x = c.pos.x
    prev_pos.y = c.pos.y

    #  Pintar trams rectes 
    for t in trams:
        t.pinta(w, wv)
        t.pinta_fletxa(w, wv, 0)
        t.pinta_fletxa(w, wv, 1)

    #  Pintar corbes 
    for corba in trams_corbs:
        corba.pinta(w, wv)

    # Pintar cotxes 
    for cc in cotxes:
        cc.pinta(w, wv)

    # Spawn de cors 
    tick += 1
    if tick % 60 == 0 and c.vida < 3:       
        spawn_cor(trams, trams_corbs, cors, p_curva=0.35)
    for cor in cors:
        cor.pinta(w, wv)
    agafat = c.agafa_cor(cors)
    if agafat:
        reproduir_sense_bloquejar(so_cor)

    # Pintar UI (vides i velocímetre)
    draw_lives_hearts(w, x=520, y=10, vides=c.vida, max_vides=3, sep=28, tags=("fg",))

    speed_to_show = c.speed_hud()  # velocitat capada en corba
    draw_speedometer(
        w,
        x_br=800 - 10,  # cantonada inferior dreta
        y_br=600 - 10,
        r=90,
        speed=speed_to_show,
        vmax=50,        # escala màxima del joc 
        tags=("fg",)
    )

    w.update()
    time.sleep(0.05)
