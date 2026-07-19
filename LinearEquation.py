
import math
from worldview.WPoint import *

class LinearEquation:
    def __init__(self, *args):
        if len(args) == 4:  # Constructor amb dos punts (x0, y0, x1, y1)
            x0, y0, x1, y1 = args
            self.m = math.inf if x0 == x1 else (y1 - y0) / (x1 - x0)
            self.b = math.inf if self.m==math.inf else y1 - self.m * x1
            self.x = x0 #ens guardem un punt per si de cas
            self.y = y0

        elif len(args) == 2 and isinstance(args[0], (int, float)):  # angle i WPoint
            angle, p = args
            if angle != (math.pi / 2) and angle != (3 * math.pi / 2):
                self.m = math.tan(angle)
            else:
                self.m = math.inf
            self.b = math.inf if self.m==math.inf else y1 - self.m * x1
            self.x = p.x #ens guardem un punt per si de cas
            self.y = p.y


        elif len(args) == 2 and isinstance(args[0], WPoint):  # dos WPoint
            p0, p1 = args
            self.m = math.inf if p0.x == p1.x else (p1.y - p0.y) / (p1.x - p0.x)
            self.b = math.inf if self.m==math.inf else p1.y - self.m * p1.x
            self.x = p1.x #ens guardem un punt per si de cas
            self.y = p1.y

    #retorna el valor de la X a partir d'una Y
    def getX(self, y):
        if self.m != math.inf and self.m != 0:
            return ((y - self.y) / self.m) + self.x
        else:
            return self.x

    #retorna el valor de la Y a partir d'una X
    def getY(self, x):
        if self.m == 0 or self.m == math.inf:
            return self.y
        else:
            return self.m * (x - self.x) + self.y

    #retorna la pendent
    def getM(self):
        return self.m

	# q és un objecte LinearEquation
    def intersection(self, q):	
        wp = WPoint()
        if self.m != q.m and self.m != math.inf and q.m != math.inf:
            wp.x = ((self.m * self.x - q.m * q.x - self.y + q.y) / (self.m - q.m))
            wp.y = q.m * (wp.x - q.x) + q.y
            return wp
        if self.m != math.inf and q.m == math.inf:
            wp.x = q.x
            wp.y = self.m * (wp.x - self.x) + self.y
            return wp
        if self.m == math.inf and q.m != math.inf:
            wp.x = self.x
            wp.y = q.m * (wp.x - q.x) + q.y
            return wp
        return None

	
    def getWPointFromDistance(self, distance, *args):
		# Variació 1:
		#
		# 				getWPointFromDistance(distance,direction,p)  
		#
		# Si passem direcció de la X i distància:  Calcula el punt d'intersecció d'una recta a partir d'una distància i una direcció
        if len(args) == 2 and isinstance(args[0], int):  # distance, direction, p
            direction, p = args
            wp = WPoint()
            if distance != 0:
                a = (self.m)**2 + 1
                b=-2*p.x-2 * self.m**2 * p.x
                c = (self.m)**2 * (self.x)**2 + 3 * self.y - 2 * self.m * self.x + \
                    2 * self.m * self.x * p.y - 2 * self.y * p.y + p.y**2 + p.x**2 - distance**2
                c=(1+self.m**2)*p.x**2-distance**2
                if (b**2 - 4 * a * c) >= 0:
                    wp.x = (-b + direction * math.sqrt(b**2 - 4 * a * c)) / (2 * a)
                    wp.y = self.m * (wp.x - self.x) + self.y
                else:
                    return None
            else:
                return p
            return wp

		# Variació 2:
		# 
		# 		getWPointFromDistance(distance,p,nearestPoint)
		# 
		# Calcula el punt d'intersecció d'una recta a partir d'una distància i el punt més proper 
        elif len(args) == 2 and isinstance(args[0], WPoint):  # distance, p, nearestPoint
            p, nearestPoint = args
            wp1, wp2 = WPoint(), WPoint()
            if self.m == math.inf:
                wp1.x, wp1.y = p.x, p.y - distance
                wp2.x, wp2.y = p.x, p.y + distance
                return wp1 if p.distance(wp1) < p.distance(wp2) else wp2
            if distance != 0:
                wp1=self.getWPointFromDistance(distance,1,p)
                wp2=self.getWPointFromDistance(distance,-1,p)
                return wp1 if nearestPoint.distance(wp1) < nearestPoint.distance(wp2) else wp2
                
            else:
                return p
        return None
