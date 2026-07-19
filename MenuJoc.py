


import time
from worldview.WPoint import WPoint

class MenuManager:
    """
    Gestiona els estats de la interfície (MENU, CONTROLS, GAME, GAMEOVER, PAUSA).
    """

    def __init__(self, tk, canvas, width=800, height=600,
                 pintar_fons_cb=None, on_restart_cb=None,
                 jugador=None, world_view=None, prev_pos_ref=None, cors_list_ref=None):

        self.tk = tk
        self.w = canvas
        self.W = width
        self.H = height

        # Callbacks i dependències de joc
        self.pintar_fons_cb = pintar_fons_cb
        self.on_restart_cb = on_restart_cb  
        self.c = jugador                     # Cotxe (jugador)
        self.wv = world_view                 # WorldView
        self.prev_pos = prev_pos_ref         # WPoint usat pel seguiment de càmera
        self.cors = cors_list_ref            # llista de cors (referència compartida)

        self.estat = "MENU"     # MENU | CONTROLS | GAME | GAMEOVER
        self.pausat = False
        self.botons = {}        # tag -> (x1, y1, x2, y2)
        self.tick = 0           

        # Vincular esdeveniments
        self.w.bind("<Button-1>", self._on_click)
        self.w.bind("<Key>", self._on_key)
        self.w.focus_set()

        if self.pintar_fons_cb:
            self.pintar_fons_cb(self.w, self.W, self.H)
            self.w.tag_lower("bg")

        # Pantalla inicial
        self.pintar_menu()

    # ===========================================================
    # Game Reset 
    # ===========================================================
    def reset_game_state(self, zoom=2.5):
        """
        Reinicia l'estat del joc per començar sempre des del mateix punt de spawn.
        """
        if self.c is None or self.wv is None or self.prev_pos is None or self.cors is None:
            # Si no ha estat injectat res, evita crash i surt
            print("[MenuManager] reset_game_state: dependències no establertes")
            return

        # --- Reset jugador (ENTITAT) ---
        if hasattr(self.c, "restaurar_pos"):
            self.c.restaurar_pos(velocitat=True)
        if hasattr(self.c, "reset_punts"):
            self.c.reset_punts()
        if hasattr(self.c, "immunitat"):
            self.c.immunitat = 0
        if hasattr(self.c, "vida"):
            self.c.vida = 1

        # --- Reset col·leccionables i comptadors ---
        self.cors[:] = []
        self.tick = 0

        # --- Recentrar càmera ---
        half_height = 200 / zoom
        half_width = half_height * (600 / 400)
        top = half_height * 1.8
        bot = half_height * 0.2

        if hasattr(self.wv, "recentrar"):
            self.wv.recentrar(WPoint(self.c.pos.x, self.c.pos.y), half_width, top, bot)

        # --- Reset referència per al seguiment de càmera ---
        self.prev_pos.x = self.c.pos.x
        self.prev_pos.y = self.c.pos.y

        # --- Neteja capes (coordinació UI) ---
        self.w.delete("fg")
        self.w.delete("pause")

    # ===========================================================
    # Helpers UI
    # ===========================================================

    def _netejar_ui(self):
        """Esborra tots els elements d'interfície i reinicia el registre de botons."""
        self.w.delete("ui")
        self.botons.clear()

    def _botó(self, x, y, w, h, text, tag, fill="#2a2a2a", fg="white"):
        """Crea un botó rectangular i registra la seva hitbox."""
        self.w.create_rectangle(
            x, y, x+w, y+h,
            fill=fill, outline="#555", width=2,
            tags=("ui", tag)
        )
        self.w.create_text(
            x+w/2, y+h/2,
            text=text, fill=fg,
            font=("Arial", 18, "bold"),
            tags=("ui", tag)
        )
        self.botons[tag] = (x, y, x+w, y+h)

    # ===========================================================
    # Pantalles
    # ===========================================================

    def pintar_menu(self):
        """Dibuixa el menú principal."""
        self._netejar_ui()

        self.w.create_text(
            self.W//2, 120,
            text="🏁 Rayo McQueen GAME",
            font=("Arial", 36, "bold"),
            fill="#ffffff", tags="ui"
        )
        self.w.create_text(
            self.W//2, 170,
            text="By Álvaro",
            font=("Arial", 14, "italic"),
            fill="#dddddd", tags="ui"
        )

        bx = self.W//2 - 100
        self._botó(bx, 240, 200, 50, "Start",     "btn_start", fill="#3a7adb")
        self._botó(bx, 310, 200, 50, "Controls",  "btn_controls", fill="#4caf50")
        self._botó(bx, 380, 200, 50, "Sortir",    "btn_exit", fill="#b43d3d")

        self.w.create_text(
            self.W//2, 460,
            text="Prem Esc per tornar al menú • P per pausar",
            font=("Arial", 12), fill="#eeeeee", tags="ui"
        )

    def pintar_controls(self):
        """Dibuixa la pantalla de controls."""
        self._netejar_ui()

        self.w.create_text(
            self.W//2, 120,
            text="Controls",
            font=("Arial", 28, "bold"),
            fill="#ffffff", tags="ui"
        )

        controls = [
            "A: Accelerar (+1)",
            "S: Frenar (-1)",
            "C: Canviar de carril",
            "P: Pausa",
            "Esc: Tornar al menú",
        ]

        y = 180
        for linia in controls:
            self.w.create_text(
                self.W//2, y,
                text=f"• {linia}",
                font=("Arial", 16),
                fill="#eeeeee", tags="ui"
            )
            y += 34

        self._botó(self.W//2 - 100, 420, 200, 50, "Back", "btn_back", fill="#666666")

    def pintar_overlay_pausa(self):
        """Mostra un overlay fosc indicant pausa."""
        self.w.create_rectangle(
            0, 0, self.W, self.H,
            fill="#000000",
            stipple="gray50",
            outline="",
            tags=("ui", "pause")
        )
        self.w.create_text(
            self.W//2, self.H//2 - 20,
            text="PAUSA",
            font=("Arial", 32, "bold"),
            fill="#ffffff",
            tags=("ui", "pause")
        )
        self.w.create_text(
            self.W//2, self.H//2 + 20,
            text="P per reprendre",
            font=("Arial", 16),
            fill="#ffffff",
            tags=("ui", "pause")
        )

    def pintar_gameover(self, score_text=""):
        """Mostra la pantalla de Game Over amb opcions."""
        self.estat = "GAMEOVER"
        self._netejar_ui()

        self.w.create_rectangle(
            0, 0, self.W, self.H,
            fill="#000000",
            stipple="gray50",
            outline="",
            tags="ui"
        )
        self.w.create_text(
            self.W//2, 180,
            text="GAME OVER :(",
            font=("Arial", 36, "bold"),
            fill="#ffffff", tags="ui"
        )

        if score_text:
            self.w.create_text(
                self.W//2, 230,
                text=score_text,
                font=("Arial", 16),
                fill="#f7f3f3", tags="ui"
            )

        bx = self.W//2 - 100
        self._botó(bx, 280, 200, 50, "Tornar a provar", "btn_retry", fill="#3a7adb")
        self._botó(bx, 350, 200, 50, "Menu", "btn_go_menu", fill="#666666")

    # ===========================================================
    # Esdeveniments
    # ===========================================================

    def _on_click(self, event):
        """Detecta clics sobre els botons i executa accions segons l'estat."""
        x, y = event.x, event.y

        for tag, (x1, y1, x2, y2) in self.botons.items():
            if x1 <= x <= x2 and y1 <= y <= y2:

                # --- MENU ---
                if self.estat == "MENU":
                    if tag == "btn_start":
                        # Reset intern
                        self.reset_game_state()
                        # Callback extern (si existeix)
                        if self.on_restart_cb:
                            self.on_restart_cb()
                        self.estat = "GAME"
                        self._netejar_ui()

                    elif tag == "btn_controls":
                        self.estat = "CONTROLS"
                        self.pintar_controls()

                    elif tag == "btn_exit":
                        self.tk.destroy()

                # --- CONTROLS ---
                elif self.estat == "CONTROLS":
                    if tag == "btn_back":
                        self.estat = "MENU"
                        self.pintar_menu()

                # --- GAMEOVER ---
                elif self.estat == "GAMEOVER":
                    if tag == "btn_retry":
                        # Reset intern
                        self.reset_game_state()
                        # Callback extern (si existeix)
                        if self.on_restart_cb:
                            self.on_restart_cb()
                        self.estat = "GAME"
                        self._netejar_ui()

                    elif tag == "btn_go_menu":
                        self.estat = "MENU"
                        self.pintar_menu()

                break

    def _on_key(self, event):
        """Gestor global de tecles (ESC, P, etc.)."""
        k = event.keysym.lower()

        if event.keysym == "Escape":
            if self.estat != "MENU":
                self.estat = "MENU"
                self._netejar_ui()
                self.pintar_menu()

        elif k == "p":
            if self.estat == "GAME":
                self.pausat = not self.pausat
                if self.pausat:
                    self.pintar_overlay_pausa()
                else:
                    self.w.delete("pause")

    # ===========================================================
    # Cicle d'actualització fora del joc
    # ===========================================================

    def tick_idle(self):
        """
        Crida quan NO estàs a GAME.
        Manté la UI reactiva sense executar la simulació.
        """
        self.w.update()
        time.sleep(0.016)  # ~60 FPS


