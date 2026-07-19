

import random
import math
from worldview.WPoint import *


# ---- Fons xulo, estàtic i sense dependències (Tkinter) ----

def _tema_colors(tema):
    tema = (tema or "grass").lower()
    if tema == "asphalt":
        return {
            "base_top":   "#4c4c50",  # degradat a dalt
            "base_bot":   "#2f2f33",  # degradat a baix
            "texture":    "#5a5a60",  # diagonals suaus
            "vignette":   "#000000",  # vora enfosquit
            "kerb_r":     "#d9463b",  # vorada vermella
            "kerb_w":     "#f3f3f3"   # vorada blanca
        }
    elif tema == "desert":
        return {
            "base_top":   "#e6cf9b",
            "base_bot":   "#d4b879",
            "texture":    "#e3c88d",
            "vignette":   "#000000",
            "kerb_r":     "#c9433a",
            "kerb_w":     "#f3efe6"
        }
    # per defecte: herba
    return {
        "base_top":   "#74c56b",
        "base_bot":   "#58ad5b",
        "texture":    "#88d67f",
        "vignette":   "#000000",
        "kerb_r":     "#e4574f",
        "kerb_w":     "#ffffff"
    }

def pintar_fons(canvas, ample=800, alt=600, tema="grass", amb_vorada=True):

    colors = _tema_colors(tema)

    #  Degradat vertical suau (interpolant entre base_top -> base_bot)
    #   Per estalviar crides de dibuix, ho fem cada 2px
    import re
    def hex_to_rgb(hx):
        m = re.fullmatch(r"#([0-9a-fA-F]{6})", hx)
        v = int(m.group(1), 16)
        return ((v >> 16) & 255, (v >> 8) & 255, v & 255)

    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    r1, g1, b1 = hex_to_rgb(colors["base_top"])
    r2, g2, b2 = hex_to_rgb(colors["base_bot"])
    step = 2
    for y in range(0, alt, step):
        t = y / max(1, alt - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        canvas.create_rectangle(0, y, ample, y + step, fill=rgb_to_hex(r, g, b), outline="", tags=("bg",))

    # Textura diagonal fixa (sense random): línies fines amb separació regular
    # Molt subtil perquè no distragui. 
    sep = 40
    col_tex = colors["texture"]
    for x in range(-alt, ample, sep):
        canvas.create_line(x, 0, x + alt, alt, fill=col_tex, width=1, tags=("bg",))

    # Vinyeta: enfosquim vores amb rectangles i 'stipple' (simula transparència)
    vora = min(ample, alt) // 8  # amplada de la banda fosca
    # dalt
    canvas.create_rectangle(0, 0, ample, vora, fill=colors["vignette"], outline="",
                            stipple="gray25", tags=("bg",))
    # baix
    canvas.create_rectangle(0, alt - vora, ample, alt, fill=colors["vignette"], outline="",
                            stipple="gray25", tags=("bg",))
    # esquerra
    canvas.create_rectangle(0, 0, vora, alt, fill=colors["vignette"], outline="",
                            stipple="gray25", tags=("bg",))
    # dreta
    canvas.create_rectangle(ample - vora, 0, ample, alt, fill=colors["vignette"], outline="",
                            stipple="gray25", tags=("bg",))

    #  Vorada fixa al voltant (opcional): segments vermells/blancs estil circuit
    if amb_vorada:
        seg = 30     # longitud de cada bloc
        gruix = 10   # gruix de la vorada
        col_r = colors["kerb_r"]
        col_w = colors["kerb_w"]

        # Dalt
        toggle = False
        for x in range(0, ample, seg):
            canvas.create_rectangle(x, 0, min(x + seg, ample), gruix,
                                    fill=(col_r if toggle else col_w), outline="", tags=("bg",))
            toggle = not toggle
        # Baix
        toggle = False
        for x in range(0, ample, seg):
            canvas.create_rectangle(x, alt - gruix, min(x + seg, ample), alt,
                                    fill=(col_r if toggle else col_w), outline="", tags=("bg",))
            toggle = not toggle
        # Esquerra
        toggle = False
        for y in range(0, alt, seg):
            canvas.create_rectangle(0, y, gruix, min(y + seg, alt),
                                    fill=(col_r if toggle else col_w), outline="", tags=("bg",))
            toggle = not toggle
        # Dreta
        toggle = False
        for y in range(0, alt, seg):
            canvas.create_rectangle(ample - gruix, y, ample, min(y + seg, alt),
                                    fill=(col_r if toggle else col_w), outline="", tags=("bg",))
            toggle = not toggle

    # envia tot el fons al nivell més baix
    canvas.tag_lower("bg")


def draw_lives_hearts(canvas, x=520, y=10, vides=3, max_vides=3, sep=28, tags=("fg",)):
    """
    Dibuixa cors plens/buits en línia.
    """
    # Fons discret
    canvas.create_rectangle(x - 12, y - 6, x + sep * max_vides, y + 28,
                            fill="#1b1b1b", outline="#383838", width=2, tags=tags)
    for i in range(max_vides):
        cx = x + i * sep
        cy = y + 10
        s = 9
        fill = "#ff4d4d" if i < vides else "#2a2a2a"
        outline = "#d93030" if i < vides else "#555555"
        canvas.create_oval(cx - s, cy - s, cx,     cy,     fill=fill, outline=outline, width=1, tags=tags)
        canvas.create_oval(cx,     cy - s, cx + s, cy,     fill=fill, outline=outline, width=1, tags=tags)
        canvas.create_polygon(cx - s, cy, cx + s, cy, cx, cy + s * 1.2,
                              fill=fill, outline=outline, width=1, tags=tags)


def draw_speedometer(canvas, x_br, y_br, r, speed, vmax=20, tags=("fg",)):
    """
    Dibuixa un velocímetre semicircular a la cantonada inferior dreta.
    - x_br, y_br: cantonada inferior dreta on es troba el semicercle.
    - r: radi total del semicercle.
    - speed: velocitat actual (es limita a [0, vmax]).
    - vmax: velocitat màxima per mapar l’agulla.
    - tags: tags del Canvas per poder esborrar-lo (fem servir "fg").
    """
    # Limitar velocitat
    speed = max(0, min(speed, vmax))

    # Semicercle superior recolzat a baix a la dreta
    cx = x_br - r
    cy = y_br - r
    bbox = (cx - r, cy - r, cx + r, cy + r)

    # Ombra suau
    canvas.create_arc(bbox, start=180, extent=-180, style="arc",
                      outline="#000000", width=12, tags=tags)

    # Base gris fosca
    canvas.create_arc(bbox, start=180, extent=-180, style="arc",
                      outline="#2a2a2a", width=10, tags=tags)

    # Segments de color (verd → groc → vermell)
    def seg(f0, f1, color):
        # f0/f1 en [0,1] mapats a 180°→0°
        a0 = 180 - f0 * 180
        a1 = 180 - f1 * 180
        extent = a1 - a0  # negatiu per sentit horari
        canvas.create_arc(bbox, start=a0, extent=extent, style="arc",
                          outline=color, width=10, tags=tags)

    seg(0.00, 0.60, "#4caf50")  # 0–60%
    seg(0.60, 0.85, "#ffc107")  # 60–85%
    seg(0.85, 1.00, "#f44336")  # 85–100%

    # Marques (ticks) i números
    n_ticks = 6  # 0%, 20%, ..., 100%
    for i in range(n_ticks + 1):
        f = i / n_ticks
        ang = math.radians(180 - f * 180)  # 180°→0°
        r1 = r - 6
        r2 = r - (18 if i % 3 == 0 else 12)  # més llargues a 0/50/100
        x1 = cx + r1 * math.cos(ang)
        y1 = cy - r1 * math.sin(ang)
        x2 = cx + r2 * math.cos(ang)
        y2 = cy - r2 * math.sin(ang)
        canvas.create_line(x1, y1, x2, y2, fill="#dddddd", width=2, tags=tags)

        # Etiquetes als ticks grans
        if i % 3 == 0:
            val = int(f * vmax)
            lx = cx + (r - 28) * math.cos(ang)
            ly = cy - (r - 28) * math.sin(ang)
            canvas.create_text(lx, ly, text=str(val), font=("Arial", 9, "bold"),
                               fill="#bbbbbb", tags=tags)

    # Agulla
    f = speed / vmax
    ang = math.radians(180 - f * 180)
    needle_len = r - 24
    nx = cx + needle_len * math.cos(ang)
    ny = cy - needle_len * math.sin(ang)
    canvas.create_line(cx, cy, nx, ny, fill="#ff5252", width=3, tags=tags)

    # Eix de l’agulla
    canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                       fill="#222222", outline="#888888", width=2, tags=tags)

    # Lectura numèrica
    canvas.create_text(cx, cy + 20, text=f"{int(round(speed))}",
                       font=("Arial", 14, "bold"), fill="#ffffff", tags=tags)
    canvas.create_text(cx, cy + 36, text="VEL", font=("Arial", 9),
                       fill="#aaaaaa", tags=tags)






