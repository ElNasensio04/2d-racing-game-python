from worldview.LinearEquation import *
from worldview.WPoint import *
from worldview.WorldView import *


#################################################################
#   LinearEquation
#################################################################

#Creem 2 punts i la seva equació
p1=WPoint(0,0)
p2=WPoint(200,0)
q1=LinearEquation(p1,p2)

#Exemple de com obtenir la coord. X a partir de la Y.
print("La coordenada X de Y=50 és:",q1.getX(50))

#Creem us altres 2 punts i la seva equació
p3=WPoint(100,100)
p4=WPoint(100,200)
q2=LinearEquation(p3,p4)

#Calculem el seu punt d'intersecció
p5=q1.intersection(q2)
print(p5)   #mostra per pantalla el que retorna la funció __repr__

#Punts a distància 20, direcció +1 a partir de p2 (punt de la recta)
p6=q1.getWPointFromDistance(20,1,p2)
print(p6)

#Creem una altra recta
p3_1=WPoint(0,0)
p3_2=WPoint(100,100)
q3=LinearEquation(p3_1,p3_2)    # pendent de -45º

p_nearest=WPoint(110,100)
p7=q3.getWPointFromDistance(10,p3_2,p_nearest)  #Punt a distància 10 a partir de p3_2 que pertanyi a la recta. Per escollir quin dels 2 que poden ser, escollim el més proper a p_nearest
print(p7)


#################################################################
#   WorldToView
#################################################################

#Dimensions de la finestra a la pantalla (en píxels)
vmin=VPoint(0,0)
vmax=VPoint(600,600)
#dimensions de la finestra de visualització del món. De tot el món, volem veure només la finestra (1200,1200) a (1300,1300)
wmin=WPoint(1200,1200)
wmax=WPoint(1300,1400)

#Definim l'objecte que servirà per treballar
wv=WorldView(wmin,wmax,vmin,vmax)

#Per treballar, s'ha de transformar cada punt individualment.
#Així, pel cotxe s'haurien de transformar cadascun dels 4 punts que defineixen un cotxe.
print(wv.worldToView(WPoint(0,0)))   #Aquest punt està clarament fora de la pantalla
print(wv.worldToView(WPoint(1250,1200)))    #Aquest punt està a dins de la pantalla: x al mig i la y a sota del tot
