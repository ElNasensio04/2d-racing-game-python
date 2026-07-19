#La carpeta base sempre és la mateixa per a tots els fitxers, així que si volem importar WPoint i VPoint, encara que aquest fitxer  
#estigui a la mateixa carpeta que WPoint i VPoint, hem d'indicar que està a la subcarpeta worldview
from worldview.WPoint import *
from worldview.VPoint import *

# --- Clase principal WorldView ---

class WorldView:
    """
    Classe que gestiona la finestra de Pantalla (VX/VY) i la finestra del Món (WX/WY), 
    amb mètodes per transformar punts entre tots dos sistemes de coordenades.
    """

    #Constructor que rep 2 WPoint i 2 VPoint
    def __init__(self, wMin, wMax, vMin, vMax):
        self.wMin = wMin
        self.wMax = wMax
        self.vMin = vMin
        self.vMax = vMax
       
    #Mostra totes les dades quan fem un print d'aun objecte d'aquesta classe
    def __repr__(self) :
        s = f"World=({self.wMin.x},{self.wMin.y}) a ({self.wMax.x},{self.wMax.y}) "
        s += f"View=({self.vMin.x},{self.vMin.y}) a ({self.vMax.x},{self.vMax.y})"
        return s

    # --- Transformacions -------------------

    #Transfromada Word to View  (món a pantalla)
    def worldToView(self, Wp: WPoint) -> VPoint:
        wy = self.wMax.y - Wp.y
       
        # Evitar divisions per zero si el món/finestra té mida 0
        scale_x = (self.vMax.x - self.vMin.x) / (self.wMax.x - self.wMin.x) if (self.wMax.x - self.wMin.x) != 0 else 0.0
        scale_y = (self.vMax.y - self.vMin.y) / (self.wMax.y - self.wMin.y) if (self.wMax.y - self.wMin.y) != 0 else 0.0

        vx = int((Wp.x - self.wMin.x) * scale_x + self.vMin.x)
        vy = int(wy * scale_y + self.vMin.y)
        return VPoint(vx, vy)

    #Permet transformar a partir de 2 valors x,y en lloc d'un WPoint 
    def worldToViewXY(self, x: float, y: float) -> VPoint:      
        return self.worldToView(WPoint(x, y))

    #Transfromada View to World (pantalla a món)
    def viewToWorld(self, Vp: VPoint) -> WPoint:
        vy = self.vMax.y - Vp.y

        denom_x = (self.vMax.x - self.vMin.x)
        denom_y = (self.vMax.y - self.vMin.y)

        wx = ((Vp.x - self.vMin.x) * (self.wMax.x - self.wMin.x) / denom_x) + self.wMin.x if denom_x != 0 else self.wMin.x
        wy = ((vy - self.vMin.y) * (self.wMax.y - self.wMin.y) / denom_y) + self.wMin.y if denom_y != 0 else self.wMin.y

        return WPoint(wx, wy)

    #Permet transformar a partir de 2 valors x,y en lloc d'un VPoint
    def viewToWorldXY(self, x: int, y: int) -> WPoint:
        return self.viewToWorld(VPoint(x, y))
    
    #Permet desplaçar la finestra del World (món)
    def translateWindow(self,dx,dy):
        self.wMin.x+=dx
        self.wMax.x+=dx
        self.wMin.y+=dy
        self.wMax.y+=dy
    
    def recentrar(self, center_wpoint: WPoint, half_width: float, top: float, bot: float):
        """
        Reposiciona la finestra del món al voltant d'un centre donat.
        half_width: meitat d'amplada de la vista (en coordenades de món)
        top/bot: extrems superior/inferior des del centre (en món)
        """
        self.wMin = WPoint(center_wpoint.x - half_width, center_wpoint.y - bot)
        self.wMax = WPoint(center_wpoint.x + half_width, center_wpoint.y + top)