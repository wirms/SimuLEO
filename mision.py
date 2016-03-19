# -*- coding: cp1252 -*-
import atmosfera as atm
import integracion
import numpy as np
import cuaternios as cua

class prescenario():
    def __init__(self):
        self.reptierra = "Esferica"
        self.modeloatmosfera = "No"
        self.modelogravedad = "Esferico"
        self.colisiones = "Si"
        self.atmosfera = atm.atmosfera()
        self.actualizar()
        self.tiempo = [2015,6,21,12,00,00]
        self.ultimospuntos = 100000
        self.puntos = 1
        self.conosensor = "Si"
        self.maximosensor = "Si"

    def actualizar(self):
        
        self.atmosfera.setmodelo(self.modeloatmosfera)
        self.atmosfera.actualizar()



class lanzamiento():
    def __init__(self):
        self.propiedades = propiedadeslanzamiento()
        self.orbitafinal = ""
        self.posicioninicial = ""
        self.lanzador = ""
        self.maniobra = ""
class propiedadeslanzamiento():
    def __init__(self):
        self.nombre = ""
        self.color= "b"
        self.tipo = "lamzamiento"

def visibilidad(pos1, pos2,h=0.):
    import numpy as np
    if np.sqrt(pos2[0]**2+pos2[1]**2+pos2[2]**2) < np.sqrt(pos1[0]**2+pos1[1]**2+pos1[2]**2):
        postemp = pos2
        pos2 = pos1
        pos1 = postemp
    
    vector = np.array([pos2[0]-pos1[0],pos2[1]-pos1[1],pos2[2]-pos1[2]])
    dist = np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
    rmax = np.sqrt(pos1[0]**2+pos1[1]**2+pos1[2]**2)
    vector = vector/dist
    dist = min(dist,1.5*np.sqrt(rmax**2+7000.**2))    
    a = 0.
    Aa = dist/1000
    if np.sqrt(pos2[0]**2+pos2[1]**2+pos2[2]**2)>100000.:
        Aa=100.
    
    vis = True
    rant = rmax
    #print pos1,pos2
    while a<dist:
        x = pos1 + a*vector
        radio = np.sqrt(x[0]**2+x[1]**2+x[2]**2)
        latgeocen = np.arcsin(x[2]/radio)*180./np.pi
        if radio>=7000. and radio>rant:
            break
        elif radio>=7000.:
            pass
        else:
            radiot = integracion.radiotierra(latgeocen, geodes=0) + h
            if radio-radiot<=-Aa:
                vis = False
                break
        rant = radio
        a = a+Aa

    return vis 
        
def restatiempos(t1,t2,segundos = 1):
    ###t1 y t2 lista/array simple de 6. Segundos = 0 para que devuelva array de 6. Segundos = 2 para que devuelva dias julianos
    
    JD2 = juliana(t2)
    JD1 = juliana(t1)
    At = JD2-JD1
    if segundos==0:
        pass
    elif segundos==1:
        return At*86400
    elif segundos==2:
        return At
        
    
def sumatiempos(t1,t2):
    ###t1 lista de 6, t2 segundos
    dias = int(t2/86400)

def juliana(t):
    import math
    #t lista de 6 numeros   año/mes/dia/hora/min/seg
#    JD2 = 367*t[0] - int(7*(t[0]+int((t[1]+9)/12))/4.) + int(275*t[1]/9.) + t[2] + 1721013.5 + (t[3])/24. + t[4]/1440. + t[5]/86400. - math.copysign(0.5,100*t[0]+t[1]-190002.5) + 0.5
##    a = int(14-t[1]/12)
##    y = t[0] + 4800 - a
##    m = t[1] + 12*a-3
##    JDN = t[2] + int((153*m+2)/5) + 365*y + int(y/4) - int(y/100) + int(y/400) - 32045
##    JD1 = JDN + (t[3]-12)/24. + t[4]/1440. + t[5]/86400.
    if t[1] == 1 or t[1] == 2:
        ano = t[0]-1
        mes = t[1] + 12
    else:
        ano=t[0]
        mes=t[1]
    B = (2-int(ano/100.)+ int((int(ano/100.))/4.))
    
    JD = int(365.25*(ano+4716)) + int(30.6001*(mes + 1)) + t[2] +(t[3])/24. + t[4]/1440. + t[5]/86400. + B - 1524.5
    if JD <2299160:
        JD = int(365.25*(ano+4716)) + int(30.6001*(mes + 1)) + t[2] +(t[3])/24. + t[4]/1440. + t[5]/86400. - 1524.5
##    
    #print JD, JD2, #JD1

    return JD

def posicionsol(JD):  #Algoritmo de www.psa.es/sdg/sunpos.htm
    dJD = JD - 2451545.
    dOmega = 2.1429 - 0.0010394594*dJD
    dMeanLongitude = 4.8950630 + 0.017202791698*dJD
    dMeanAnomaly =  6.2400600 + 0.0172019699*dJD
    dEclipticLongitude = dMeanLongitude + 0.03341607*np.sin(dMeanAnomaly) + 0.00034894*np.sin(2.*dMeanAnomaly) - 0.0001134 - 0.0000203*np.sin(dOmega)
    dEclipticObliquity = 0.4090928 - 6.2140e-9*dJD + 0.0000396*np.cos(dOmega)

    
    R = (1.00014 - 0.01671*np.cos(dMeanAnomaly) - 0.00014*np.cos(2.*dMeanAnomaly))* 149597870700. 

    dY=np.cos(dEclipticObliquity)*np.sin(dEclipticLongitude)
    dX=np.cos(dEclipticLongitude)
    ascensionrecta= np.arctan(dY/dX)
    while ascensionrecta<0.:
        ascensionrecta=ascensionrecta+2*np.pi    
    declinacion= np.arcsin(np.sin(dEclipticObliquity)*np.sin(dEclipticLongitude))

    ascensionrecta=ascensionrecta*180./np.pi
    declinacion=declinacion*180/np.pi
    u=np.array([R,0.,0.])
    u1=np.array([0.,-1.,0.])
    u3=np.array([0.,0.,1.])

    u=cua.giro(u,u1,declinacion)
    u=cua.giro(u,u3,ascensionrecta)

    
    return u
    
    



    
    
