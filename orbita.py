import numpy as np
from integracion import *
import mision as mis
import cuaternios as cua
import math


def cross(a,b):     #Producto vectorial de dos vectores. Entrada numpy.array o lista
    if len(a) and len(b) == 3:

        i = a[1]*b[2] - a[2]*b[1]
        j = a[2]*b[0] - a[0]*b[2]
        k = a[0]*b[1] - a[1]*b[0]

        return np.array([i,j,k])


    else:

        return "Error orbita.operadores.cross, size de arrays distinto de 3 o clase de objeto incorrecta(numpy.array o list)"

def modulo(a):   #Modulo de orden 2 de un vector. Entrada numpy.array o lista

    a = np.array(a)

    return np.sqrt(np.dot(a,a))    



class orbita():    #Clase orbita, autocontenida



    def __init__(self):    #Inicializacion de parametros orbitales y constantes

        self.parametros = np.array([7000.,0.,0.,0.,0.,0.])
        self.constantes = np.array([398600.4418,1.,1.])   #Constantes necesarias # [GMR,,]
        self.propiedades = propiedadesorbita()
        self.pos = np.array([[]])

    def setnombre(self,nombre):
        self.propiedades.nombre = nombre



    def setorbita(self,a,e,i,ascension,argumentoper,trueanom):  #Cambio de parametros orbitales

        self.parametros = np.array([a,e,i,ascension,argumentoper,trueanom])


    def par2xv(self):    #Transformacion de parametros a posicion/velocidad

        p = self.parametros[0]*(1-self.parametros[1]**2)
        theta = self.parametros[5]*np.pi/180.
        r = p/(1.+self.parametros[1]*np.cos(theta))
                
        x= r*np.array([1.,0.,0.])
        z1 = np.array([0.,0.,1.])
        x1 = np.array([1.,0.,0.])
        giro1 = cua.ang2cua(z1,self.parametros[3])
        x1 = cua.giro(x1,z1,self.parametros[3])
        giro2 = cua.ang2cua(x1,self.parametros[2])
        z1 = cua.giro(z1,x1,self.parametros[2])
        giro3 = cua.ang2cua(z1,self.parametros[4])
        giro4 = cua.ang2cua(z1,self.parametros[5])

        giro = cua.pro(giro2,giro1)
        giro = cua.pro(giro3,giro)
        giro = cua.pro(giro4,giro)

        h = np.sqrt(p*self.constantes[0])
        v = np.array([self.constantes[0]*np.sin(theta)*self.parametros[1]/h, self.constantes[0]*(1.+self.parametros[1]*np.cos(theta))/h, 0.])

        x = cua.conv(x,giro)
        v = cua.conv(v,giro)        
        return x,v

    def periodo(self):
        T =  T = 2.0*np.pi*np.sqrt(self.parametros[0]**3.0/self.constantes[0])
        return T
    def plano(self):
        z1 = np.array([0.,0.,1.])
        x1 = np.array([1.,0.,0.])
        x1 = cua.giro(x1,z1,self.parametros[3])
        z1 = cua.giro(z1,x1,self.parametros[2])
        return z1
    def xv2par(self,pos,vel):   #Trasformacion de posicion/velocidad a parametros

        h = cross(pos,vel)    #Momento cinetico
        
        if modulo(h)<1e-6:
            return "Caida libre"

        e = -(pos/modulo(pos)) - (cross(h,vel)/self.constantes[0])   #Excentricidad
        

        Ener = np.dot(vel, vel)/2.0
        Ener = Ener - (self.constantes[0]/modulo(pos))   #Energia de la orbita

        if Ener >=0.:
            return "Orbita no eliptica"
            

        a = -self.constantes[0]/(2.0*Ener)   #Semieje mayor

        T = 2.0*np.pi*np.sqrt(a**3.0/self.constantes[0])  #Periodo
        
        
        u3 = h/modulo(h)

        if modulo(e) <=1e-6:    #Orbita circular, excentricidad nula

            if modulo(cross(u3,[0,0,1])) <=1e-6: #Orbita ecuatorial

                u1 = np.array([1.,0.,0.])
                anover = np.dot(pos,u1)/modulo(pos)                
                if abs(anover)>=1.:
                    anover = math.copysign(1.0, anover)                    
                trueanom = np.arccos(anover)
                
                self.parametros = np.array([a,0.,0.,0.,0.,trueanom*180./np.pi])

                return


            else:   #Circular general

                hproy = np.array([h[0],h[1],0.])

                n1 = cross([0,0,1],u3)    #Definicion del triedro perifocal
                n1 = n1/modulo(n1)      #u3 direccion h, u1 direccion e(Circular->Nodo ascendente)
                                        #u2 perpedicular a ambos
                u1 = n1
                u2 = cross(u3,u1)       #n1 direccion nodo ascendente            
                u2 = u2/modulo(u2)      #n2 perpendicular, contenido en el plano ecuatorial

                argumentoper = 0.   #Por orbita circular

                ascension = np.arccos(np.dot(n1,[1.,0.,0.]))  #Longitud recta del nodo ascendente

                sector = np.arcsin(np.dot(n1,[0.,1.,0.]))

                if sector <0.:
                    ascension = -ascension

                if ascension<0.:
                    ascension = 2.*np.pi + ascension

                

                i = np.arccos(np.dot([0,0,1],u3)) #Inclinacion

                


                anover = np.dot(pos,u1)/modulo(pos)                
                if abs(anover)>=1.:
                    anover = math.copysign(1.0, anover)                    
                trueanom = np.arccos(anover)  #Anomalia verdadera

                sector = np.arcsin(np.dot(pos,u2)/modulo(pos))

                if sector <0.:
                    trueanom = -trueanom

                if trueanom<0.:
                    trueanom = 2.*np.pi + trueanom
                    
                self.parametros = np.array([a,modulo(e),i*180./np.pi,ascension*180./np.pi,argumentoper*180./np.pi,trueanom*180./np.pi])

                return

        else:      #Eliptica          

            u1 = e/modulo(e)
            u3 = h/modulo(h)
            u2 = cross(u3,u1)
            n1 = cross([0.,0.,1.],u3)
            n1 = n1/modulo(n1)
            i = np.arccos(np.dot([0.,0.,1.],u3))

            
            if i<1e-6:   #Eliptica ecuatorial

                ascension = 0.
                
                argumentoper = np.arccos(np.dot(u1,n1))

                sector = np.arcsin(np.dot(cross(n1,u1),u3))

                if sector <0.:
                    argumentoper = -argumentoper  

                if argumentoper <0.:

                    argumentoper = 2.*np.pi + argumentoper
                             

                
                anover = np.dot(pos,u1)/modulo(pos)                
                if abs(anover)>=1.:
                    anover = math.copysign(1.0, anover)                    
                trueanom = np.arccos(anover)  #Anomalia verdadera

                sector = np.arcsin(np.dot(pos,u2)/modulo(pos))

                if sector <0.:
                    trueanom = -trueanom

                if trueanom<0.:
                    trueanom = 2.*np.pi + trueanom
                    
                self.parametros = np.array([a,modulo(e),i*180./np.pi,ascension*180./np.pi,argumentoper*180./np.pi,trueanom*180./np.pi])
                
                return

      
            else:   #Eliptica general

                
                ascension = np.arccos(np.dot(n1,[1.,0.,0.]))  #Longitud recta del nodo ascendente
                
                sector = np.arcsin(np.dot(n1,[0.,1.,0.]))

                if sector <0.:
                    ascension = -ascension

                if ascension<0.:
                    ascension = 2.*np.pi + ascension

                
                argumentoper = np.arccos(np.dot(u1,n1))
                
                sector = np.dot(cross(n1,u1),u3)
                
                if sector <0.:
                    argumentoper = -argumentoper

                if argumentoper <0.:

                    argumentoper = 2.*np.pi + argumentoper
                             
                anover = np.dot(pos,u1)/modulo(pos)                
                if abs(anover)>=1.:
                    anover = math.copysign(1.0, anover)                    
                trueanom = np.arccos(anover)  #Anomalia verdadera

                sector = np.arcsin(np.dot(pos,u2)/modulo(pos))

                if sector <0.:
                    trueanom = -trueanom

                if trueanom<0.:
                    trueanom = 2.*np.pi + trueanom
                    
                self.parametros = np.array([a,modulo(e),i*180./np.pi,ascension*180./np.pi,argumentoper*180./np.pi,trueanom*180./np.pi])
                
                return

    def xenorbita(self,x):
        
        npuntos = 1000
        Atheta = 400./npuntos        
        theta = 0.
        orbitatest = orbita()     
        while theta <=360.:            
            orbitatest.setorbita(self.parametros[0],self.parametros[1],self.parametros[2],self.parametros[3],self.parametros[4],theta)
            xtest,_ = orbitatest.par2xv()
            r = (x[0]-xtest[0])**2+(x[1]-xtest[1])**2+(x[2]-xtest[2])**2
            
            if r<=1.:
                return True,theta
            theta = theta+Atheta

        return False,0.
    
    def orbita(self):
        import cuaternios as cua

        npuntos = self.propiedades.resolucion
        Atheta = 400./npuntos
        p = self.parametros[0]*(1-self.parametros[1]**2)
        theta = Atheta

        r = p/(1+self.parametros[1])
        x = r * np.array([1.,0.,0.])

        z1 = np.array([0.,0.,1.])
        x1 = np.array([1.,0.,0.])
        giro1 = cua.ang2cua(z1,self.parametros[3])
        x1 = cua.giro(x1,z1,self.parametros[3])
        giro2 = cua.ang2cua(x1,self.parametros[2])
        z1 = cua.giro(z1,x1,self.parametros[2])
        giro3 = cua.ang2cua(z1,self.parametros[4])

        giro = cua.pro(giro3,giro2)
        giro = cua.pro(giro,giro1)

        x = cua.conv(x,giro)
        self.pos = np.array([x])



        while theta <=360.:
            
            r = p/(1+self.parametros[1]*np.cos(np.pi*theta/180))
            x = r * np.array([1.,0.,0.])
            z1 = np.array([0.,0.,1.])
            x = cua.giro(x,z1,theta)
            x = cua.conv(x,giro)
            x = np.array([x])
            
            self.pos = np.append(self.pos,x,0)
            theta = theta+ Atheta

class tierra():
    
    def __init__(self):
        self.mapa = "./graficos/mapamundi.png"
        self.tierra = np.array([[]])
        self.color = np.array([[]])

    def tierra3D(self):
        import Image
        
        imagen = Image.open(self.mapa)
        pixel = imagen.load()
        anch,alt = imagen.size
        anch = anch-1
        alt = alt-1
        lon,lat = -180,-90
        self.tierra=np.array([geotox(-90,-180)])
        color = [tuple(pixel[((180+lon)/360)*anch,((90-lat)/180)*alt])]          
        
        self.color= color
        while lat<=90:
            
            while lon<=180:
                
#                color = tuple(pixel[((180+lon)/360)*anch,((90-lat)/180)*alt])            
                
                
                x = np.array([geotox(lat,lon)])
##                print x, "   asdqawsdasdasd    ", color
                
                self.tierra=np.append(self.tierra,x,0)
                self.color.append(color)
                if abs(lat)>=90:
                    lon = lon+180
                elif abs(lat)>=80:
                    lon = lon+90
                elif abs(lat)>=60:
                    lon = lon+20
                elif abs(lat)>=50:
                    lon = lon+10
                else:
                    lon = lon+5
                
            lat = lat+5
            lon = -180
            
    def dibujartierra3D(self,ejes):
        import matplotlib as mpl
        #i = 0
        #while i < len(self.tierra):
            
        ejes.scatter(self.tierra[:,0],self.tierra[:,1],self.tierra[:,2],c = "lightgrey")  
            #
                
class propiedadesorbita():

    def __init__(self):
        self.nombre = ""
        self.color = "b"
        self.resolucion = 200
  

class base():
    def __init__(self):

        self.pos = np.array([[6378.,0,0]])
        self.t = np.array([0.])
        self.lat = 0.
        self.lon = 0.
        self.propiedades = propiedadesbase()
    listabases = {}

    def setnombre(self,nombre):

        self.propiedades.nombre = nombre

class propiedadesbase():
    def __init__(self):
        self.nombre = ""
        self.color = "b"

        
class sensor():
    def __init__(self):
        self.objeto = ""
        self.propiedades = propiedadessensor()
        self.pos = np.array([[6978.,0,0]])
        self.t = np.array([[0.]])
        self.vector  = np.array([-1.,0.,0.])
        self.semiangulo = 15.
        self.resolucion = 5.
        self.dmax = 1000.
        self.actitud = "Nadir"
    def setnombre(self,nombre):
        self.propiedades.nombre = nombre
    def calcvector(self,x):
        if self.actitud == "Nadir":
            lat,lon = xtogeo(x,0.)
            nadir = geotox(lat,lon)
            vector = np.array([nadir[0]-x[0],nadir[1]-x[1],nadir[2]-x[2]])
            vector = vector/np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
            return vector
        elif self.actitud == "Cenit":
            lat,lon = xtogeo(x,0.)
            nadir = geotox(lat,lon)
            vector = np.array([nadir[0]-x[0],nadir[1]-x[1],nadir[2]-x[2]])
            vector = -vector/np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
            return vector
        elif self.actitud == "Direccion fija":
            return self.vector
            
            
    def nadir(self):
        lat,lon = xtogeo(self.pos[0,:],self.t[0,0])
        nadir = geotox(lat,lon,t=self.t[0,0])
        vector = np.array([nadir[0]-self.pos[0,0],nadir[1]-self.pos[0,1],nadir[2]-self.pos[0,2]])
        vector = vector/np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
        self.vector = vector
    def cenit(self):
        lat,lon = xtogeo(self.pos[0,:],0.)
        nadir = geotox(lat,lon)
        vector = np.array([nadir[0]-self.pos[0,0],nadir[1]-self.pos[0,1],nadir[2]-self.pos[0,2]])
        if np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)>=1.:
            vector = -vector/np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
        else:
            vector = nadir/np.sqrt(nadir[0]**2+nadir[1]**2+nadir[2]**2)
        self.vector = vector
    def cono(self):
        lista = np.array([[]])
        vector2 = np.array([-self.pos[0,1],self.pos[0,0],0])
        vector2 = vector2/np.sqrt(vector2[0]**2+vector2[1]**2+vector2[2]**2)
        
        vector = cua.giro(self.vector,vector2, self.semiangulo)        
        punto = self.rayo(vector)
        punto = np.array([punto])
        lista = punto
        for i in range(0,int(360./self.resolucion)):
            
            vector = cua.giro(vector,self.vector,self.resolucion)
            
            punto = self.rayo(vector)
            punto = np.array([punto])
            
            lista= np.append(lista,punto,0)
        return lista

    def traza(self):
        lat,lon=xtogeo(self.pos[0,:],self.t[0,0])
        lonsub = lon
        latsub = lat
        tiempo=self.t[0,0]
        posicion=self.pos[0,:]
        subsat = geotox(lat,lon,tiempo)        
        z=np.array([0.,0.,1.])
        puntoant=np.array([subsat[0],subsat[1],subsat[2]])
        listapuntos = np.array([puntoant])
        maxlat=0
        maxlon=0

        #Calculo del maximo semiangulo visible en horizontal, para la representacion
        maximolon=0.
        i=0
        while i==0:
                punto=np.array(cua.giro(puntoant,z,0.5))
                maximolon=maximolon+0.5
                vector= posicion-punto
                puntoant=punto
##                if maxlon>=180.:
##                    temp= geotox(lat,180.,tiempo)
##                    puntoant=np.array([temp[0],temp[1],temp[2]])
                if cua.productoescalar(vector,-punto)>0.:
                    i=1
                    
        
        #Se divide el circulo en tres arcos, sentido contrario a las aguajs del reloj
        # De la horizontal hacia el este, hacia arriba
        # De la vertical norte hasta la sur
        # De la vertical sur hasta la norte

        #Primer arco
        while maxlat==0:
            while (maxlon+lonsub)<180.+maximolon:
                punto=np.array(cua.giro(puntoant,z,0.5))
                maxlon=maxlon+0.5
                vector= posicion-punto
                puntoant=punto
##                if maxlon>=180.:
##                    temp= geotox(lat,180.,tiempo)
##                    puntoant=np.array([temp[0],temp[1],temp[2]])
                if cua.productoescalar(vector,-punto)>0.:
                    maxlon=400.
                
                
            
            listapuntos = np.append(listapuntos,np.array([puntoant]),0)
            lat=lat+0.5
            maxlon=0.
            punto=geotox(lat,lonsub,tiempo)            
            vector= posicion-punto
            if cua.productoescalar(vector,-punto)>0.:
                listapuntos=np.append(listapuntos,np.array([puntoant]),0)               
                maxlat=1
            elif lat>90:
                maxlat=1
            puntoant=punto


        maxlat=0
        maxlon=0

        #Segundo arco
        while maxlat==0:
            while maxlon+lonsub>-180.-maximolon:
                punto=np.array(cua.giro(puntoant,z,-0.5))
                maxlon=maxlon-0.5
                vector= posicion-punto
                puntoant=punto
##                if maxlon<=-180.:
##                    temp= geotox(lat,180.,tiempo)
##                    puntoant=np.array([temp[0],temp[1],temp[2]])
                if cua.productoescalar(vector,-punto)>0.:
                    maxlon=-400.
                
                
            
            listapuntos = np.append(listapuntos,np.array([puntoant]),0)
            lat=lat-0.5
            maxlon=0.
            punto=geotox(lat,lon,tiempo)
            
            vector= posicion-punto
            if cua.productoescalar(vector,-punto)>0.:
                listapuntos=np.append(listapuntos,np.array([puntoant]),0)               
                maxlat=1
            elif lat<-90:
                maxlat=1
            puntoant=punto

        
        maxlat=0
        maxlon=0
        listapuntos[0,:]=listapuntos[1,:]

        #Tercer arco
        while maxlat==0:
            while maxlon+lonsub<180.+maximolon:
                punto=np.array(cua.giro(puntoant,z,0.5))
                
                vector= posicion-punto
                maxlon=maxlon+0.5
                puntoant=punto
##                if maxlon>=180.:
##                    temp= geotox(lat,180.,tiempo)
##                    puntoant=np.array([temp[0],temp[1],temp[2]])
                if cua.productoescalar(vector,-punto)>0.:
                    maxlon=400.
                
            
            listapuntos = np.append(listapuntos,np.array([puntoant]),0)
            lat=lat+0.5
            maxlon=0
            punto=geotox(lat,lon,tiempo)
            puntoant=punto
            vector= posicion-punto
            if cua.productoescalar(vector,-punto)>0.:
                listapuntos=np.append(listapuntos,np.array([puntoant]),0)               
                maxlat=1
            elif lat>90:
                maxlat=1
            elif lat-latsub>=0.:
                maxlat=1
            puntoant=punto
            
            
            
        return listapuntos
            
        
        
            
        
        
    def rayo(self,vector):
        lat = xtogeo(self.pos[0,:],0)
        dist = np.sqrt(self.pos[0,0]**2+self.pos[0,1]**2+self.pos[0,2]**2) - radiotierra(lat[0])
        punto = self.pos[0]
        if dist>self.dmax:
            punto=self.puntorayo(vector,self.dmax)
        while dist< self.dmax:
            
            punto = self.puntorayo(vector,dist)
            if intersecciontierra(punto):
                return punto
            
            dist = dist+1.
        
        return punto

    def puntorayo(self, vector, par):
        par = np.array([par])
        #print self.pos[0,:] ,par,vector,self.pos[0,:] + par*vector
        return self.pos[0,:] + par*vector
    def actualizar(self,objetos):
        if self.objeto == "":
            pass
        else:
            self.pos = np.array([objetos[self.objeto].pos[-1,:]])
            self.t = np.array([objetos[self.objeto].t[-1]])
        
        
        
        if self.actitud == "Nadir":            
            self.nadir()
        elif self.actitud == "Cenit":            
            self.cenit()
    def dibujar(self,ejes2D,ejes3D):        
        listapuntos = self.cono()
        
        self.dibujartrazacono(ejes2D,listapuntos)
        self.dibujarcono(ejes3D, listapuntos)
    def dibujartraza(self,ejes2D):        
        listapuntostraza=self.traza()
        self.dibujartrazacono(ejes2D,listapuntostraza,estilo="-.")
        
    def dibujarcono(self,ejes,listapuntos):
        for i in range(0,len(listapuntos)):
            x = [self.pos[0,0],listapuntos[i,0]]
            y = [self.pos[0,1],listapuntos[i,1]]
            z = [self.pos[0,2],listapuntos[i,2]]
            ejes.plot(xs = x, ys = y, zs = z, color = self.propiedades.color,linestyle = ":")
                       
    def dibujartrazacono(self,mapa,listapuntos, estilo=":"):
        
        listat = self.t
        for i in range(1, len(listapuntos)):            
            listat = np.append(listat, self.t,0)
        
        proy, ntrazas = trayectoriageo(listapuntos,listat)   
        i = 0

            
        while (i < ntrazas):
        
            a = proy[i]
            #mapa.plot(a[:,1],a[:,0],color = color,latlon = "True") #Si dibujas el mapa cada vez
            mapa.plot(a[:,1],a[:,0],color = self.propiedades.color,linestyle = estilo) #Si cargas el mapa desde imagen
            i = i+1
    
class propiedadessensor():
    def __init__ (self):
        self.nombre = ""
        self.color = "b"

def intersecciontierra(x):
    radio = np.sqrt(x[0]**2+x[1]**2+x[2]**2)
    pos = xtogeo(x,0.)
    radiot= radiotierra(pos[0])
    
    if radiot-radio<=1.:
        return True
    else:
        return False
def interseccionorbitas(orbita1, orbita2):
    u1 = orbita1.plano()
    u2 = orbita2.plano()
    vector = cross(u1,u2)
    if np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)< 1e-8: #orbitas coplanarias
        listaang  = []
        listaang2 = []
        
        p1 = orbita1.parametros[0]*(1.-orbita1.parametros[1]**2)
        p2 = orbita2.parametros[0]*(1.-orbita2.parametros[1]**2)
        apo1 = orbita1.parametros[0]*(1.+orbita1.parametros[1])
        apo2 = orbita2.parametros[0]*(1.+orbita2.parametros[1])
        peri1 = orbita1.parametros[0]*(1.-orbita1.parametros[1])
        peri2 = orbita2.parametros[0]*(1.-orbita2.parametros[1])
        r = max(peri1,peri2)
        if apo1<peri2 or apo2 <peri1:
            return [],[]

        theta = 0.
        Atheta = 360./10000
        theta1 = theta-orbita1.parametros[4]
        theta2 = theta-orbita2.parametros[4]
        signo = p1/(1.+orbita1.parametros[1]*np.cos(np.pi*theta1/180.))-p2/(1.+orbita2.parametros[1]*np.cos(np.pi*theta2/180.))

        if orbita1.parametros[1]<1e-8 and orbita2.parametros[1]<1e-8:
            return [],[]

        elif orbita2.parametros[1]<1e-8:
            theta1 = np.arccos(((p1/r)-1.)/orbita1.parametros[1])*180./np.pi
            listaang.append(theta1)
            theta2 = theta1+orbita1.parametros[4]
            listaang2.append(theta2)

        elif orbita1.parametros[1]<1e-8:
            theta2 = np.arccos(((p2/r)-1.)/orbita2.parametros[1])*180./np.pi
            thetasum2 = theta2 + orbita2.parametros[4]
            theta1 = thetasum2 - orbita1.parametros[4]
            listaang.append(theta1)
            listaang2.append(theta2)
            
        while theta<=360.:
            
            theta1 = theta-orbita1.parametros[4]
            theta2 = theta-orbita2.parametros[4]
            r1 = p1/(1.+orbita1.parametros[1]*np.cos(np.pi*theta1/180.))
            r2 = p2/(1.+orbita2.parametros[1]*np.cos(np.pi*theta2/180.))
            if signo*(r1-r2)<=0.:
                listaang.append(theta1)
                listaang2.append(theta2)
            signo = r1-r2
            theta = theta+Atheta

        return listaang, listaang2
    x1 = np.array([1.,0.,0.])
    z1 = np.array([0.,0.,1.])
    x1 = cua.giro(x1,z1,orbita1.parametros[3])

    ang = np.dot(vector,x1)/(modulo(vector)*modulo(x1))
    if ang>= 1.:
        ang=1.
    if ang<=-1:
        ang=-1.
    ang = np.arccos(ang)
    sector = np.arcsin(np.dot(vector,x1))
    ang = ang*180./np.pi
    if sector <0.:
        ang = -ang
    ang = ang-orbita1.parametros[4]
    while ang<0.:
        ang = 360. + ang
    orbitatest = orbita()
    orbitatest.setorbita(orbita1.parametros[0],orbita1.parametros[1],orbita1.parametros[2],orbita1.parametros[3],orbita1.parametros[4],ang)
    posicion1,_ = orbitatest.par2xv()
    en1, ang1 = orbita2.xenorbita(posicion1)
    angcomp = ang+180.
    if ang>360.:
        angcomp = angcomp-360.
    orbitatest.setorbita(orbita1.parametros[0],orbita1.parametros[1],orbita1.parametros[2],orbita1.parametros[3],orbita1.parametros[4],angcomp)
    posicion2,_ = orbitatest.par2xv()
    en2, ang2 = orbita2.xenorbita(posicion2)
    if en1 and en2:
        return [ang,angcomp],[ang1,ang2]
    elif en1:
        return [ang],[ang1]
    elif en2:
        return [angcomp],[ang2]
    else:
        return [],[]
class maniobra():
    def __init__(self):
        self.propiedades = propiedadesmaniobra()
        self.pos = np.array([0.,0.,0.])
        self.Av = np.array([0.,0.,0.])
        self.orbitainicial = ""
        self.orbitafinal = ""
        self.posicioninicial = np.array([0.,0.,0.])
        self.posicionfinal = np.array([0.,0.,0.])
        self.anoini = 0.
        self.anofin = 0.
        self.velocidadinicial = np.array([0.,0.,0.])
        self.velocidadfinal = np.array([0.,0.,0.])

        self.impulsoesp = ""
        self.mi = 1.
        self.consumo = 0.
class propiedadesmaniobra():
    def __init__(self):
        self.nombre = ""
        self.color = "b"
def dibujarmaniobra3D(maniobra,ejes):
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d
    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
            FancyArrowPatch.draw(self, renderer)            
    escala = 0.25*max(maniobra.pos)/max(maniobra.Av)
    flecha = Arrow3D([maniobra.pos[0],maniobra.pos[0]+escala*maniobra.Av[0]],[maniobra.pos[1],maniobra.pos[1]+escala*maniobra.Av[1]],
                     [maniobra.pos[2],maniobra.pos[2]+escala*maniobra.Av[2]],
                     mutation_scale = 20, lw = 3, arrowstyle = "-|>", color = maniobra.propiedades.color)
    ejes.add_artist(flecha)
    
###########################################

