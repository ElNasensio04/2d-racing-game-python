

import winsound
import threading

def reproduir_sense_bloquejar(func):
    """
    Executa una funció de so en un fil separat perquè no bloquegi el joc.
    Útil per reproduir sons mentre el bucle principal segueix funcionant.
    """
    threading.Thread(target=func).start()

def so_xoc():
    """
    So curt i sec per indicar un xoc (col·lisió).
    Cada tupla és (freqüència Hz, duració ms).
    """
    beats = [
        (300, 50),
        (200, 50),
        (250, 50)
    ]
    for freq, dur in beats:
        winsound.Beep(freq, dur)

def so_cor():
    """
    So més agut i agradable per indicar que s'ha recollit un cor.
    """
    beats = [
        (600, 50),
        (700, 50),
        (800, 50)
    ]
    for freq, dur in beats:
        winsound.Beep(freq, dur)

