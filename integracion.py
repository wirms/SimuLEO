import numpy as np
import matplotlib.pyplot as mpl
import cuaternios as cua
import Tkinter
from mision import *


class solido(object):
    
    def __init__(self):   #Inicializacion de estado inicial

        self.pos = np.array([[7000.,0,0]])
        self.vel = np.array([[0,7.54605329011,0]])
        self.t = np.array([[0.]])
        self.u1 = np.array([cua.verticallocal(self.pos[-1,:])])# Eje u1 cuerpo en globales

        self.propiedades = propiedades()        
        self.int = "AB4"
        self.At = 1.
        self.tmax = 1e4
        self.figura2D = mpl.Figure()
        self.figura3D = mpl.Figure()

    def setnombre(self,texto):
        self.propiedades.nombre = texto

    def setfigura2D(self,figura):
        self.figura2D = figura

    def setpos(self,x0):   #Cambio de posicion inicial   Necesario que xo sea un array tipo [[]]
        x0 = np.array([x0])
        self.pos = np.append(self.pos,x0,0)

    def reset(self):
        self.pos,self.vel, self.t=np.array([[6378.,0,0]]),np.array([[0,0,0]]), np.array([[0.]])

    def setvel(self,v0):   #Cambio de velocidad inicial
        v0 = np.array([v0])
        self.vel = np.append(self.vel,v0,0)

    def sett(self,t):
        t0 = np.array([t])
        self.t = np.append(self.t,t0,0)

    def setinicio(self,x0,v0):  #Cambio de posicion y velocidad iniciales
        self.pos=np.array([x0])
        self.vel=np.array([v0])

    def setu1(self,u):
        u = np.array([u])
        self.u1 = np.append(self.u1,u,0)

    
    def setintegrador(self, integrador):  #Cambio de metodo de integracion
        self.int = integrador
##############################################################
    def integrar(self,progreso):

        if self.int == "Parabolico":
            self.parabolico()

        elif self.int == "ParabolicoSimple":
            self.parabolicosimple()

        elif self.int == "RK4":


            At = self.At
            imax = int(np.ceil((self.tmax-self.t[-1,0])/self.At))
            if imax < 100:
                imax = 100
            tiempo = 0.        
            i=0


            while not self.parada():
            
                if i%(imax/100) ==0:
                    texto = "  Calculando "+ self.propiedades.nombre+" ...    " + str(i/(imax/100)) + " % "
                    progreso.set(texto,)

        
                

                y1 = self.rungekutta4(At,tiempo)

                

                self.setpos(self.pos[-1,:]+y1[0,:])
                self.setvel(self.vel[-1,:]+y1[1,:])
                self.sett(self.t[-1]+At)
                i=i+1

            texto = "  Completado"
            progreso.completado()
            
        elif self.int == "AB4":

            At = self.At
            imax = int(np.ceil((self.tmax-self.t[-1,0])/self.At))
            if imax < 100:
                imax = 100
            tiempo = 0.
            i=0

            for i in range(0,4):
                
                y1 = self.rungekutta4(At,tiempo)



                self.setpos(self.pos[-1,:]+y1[0,:])
                self.setvel(self.vel[-1,:]+y1[1,:])
                self.sett(self.t[-1]+At)
                i=i+1

            while not self.parada():

                if i%(imax/100) ==0:
                    texto = "  Calculando "+ self.propiedades.nombre+" ...    " + str(i/(imax/100)) + " % "
                    progreso.set(texto,)


                y1= self.adamsbashforth4(At)
                
                self.setpos(self.pos[-1,:]+y1[0,:])
                self.setvel(self.vel[-1,:]+y1[1,:])
                self.sett(self.t[-1]+At)
                i=i+1

            texto = "  Completado"
            progreso.completado()

        elif self.int == "PC4":

            At = self.At
            imax = int(np.ceil((self.tmax-self.t[-1,0])/self.At))
            if imax < 100:
                imax = 100
            tiempo = 0.
            i=0

            for i in range(0,3):
                
                y1 = self.rungekutta4(At,tiempo)



                self.setpos(self.pos[-1,:]+y1[0,:])
                self.setvel(self.vel[-1,:]+y1[1,:])
                self.sett(self.t[-1]+At)
                i=i+1

            while not self.parada():

                if i%(imax/100) ==0:
                    texto = "  Calculando "+ self.propiedades.nombre+" ...    " + str(i/(imax/100)) + " % "
                    progreso.set(texto,)


                y1= self.predictorcorrector4(At)
                
                self.setpos(self.pos[-1,:]+y1[0,:])
                self.setvel(self.vel[-1,:]+y1[1,:])
                self.sett(self.t[-1]+At)
                i=i+1

            texto = "  Completado"
            progreso.completado()
            
##############################################################
    def f(self, paso = -1, tiempo = 0., punto=0):    #De la ecuacion y' = f(t,y) con y = [[x],[x']]T


#Paso es el indice de la self.pos donde se calcula f
#Tiempo es el diferencial con self.t[paso]
#Punto es la diferencia entre el punto donde calcular f y self.pos[paso]
###################################################
        #Matriz    [x ]'   =   [x' ]    = [A   B]* [x ]
        #          [x']        [x'']      [C   D]  [x']


        if np.shape(punto) ==():
            punto = np.array([0,0,0])
            
            
        
            
        
        A = 0.
        B = 1.
        C = 0.         #Fuerzas dependientes de la posicion %%%%%%%%Mejorar??
        D = 0.         #Fuerzas dependientes de la velocidad %%%%%%%%Mejorar??
        
        x = self.pos[paso,:]+ punto[:]
        xp= self.vel[paso,:]
        
        
        matriz = np.array([A*x+B*xp])
        matriz1 = np.array([C*x+D*xp])
        
        matriz = np.append(matriz,matriz1,0)
        
####################################################
        # Fuerzas independientes
        
        fuerzas1 = np.array ([[0,0,0]])     
        fuerzas = self.sumafuerzas(x,xp)
        
        fuerzas = np.append(fuerzas1, fuerzas,0)
        
        f=matriz+fuerzas
        return f

    def sumafuerzas(self,x,v):
        if len(x) and len(v) == 3:
            pass

        else:
            return "Error en integracion/sumafuerzas, x y v deben tener tamano 3"   
        
        grav = gravedad(x)
        aero = self.resistencia(x,v)
        #empuje
        
        return grav + aero
    def resistencia(self,x,v):
        global escenario
        coefbal = self.propiedades.balistico
        r = np.sqrt(x[0]**2+x[1]**2+x[2]**2)
        lat,lon = xtogeo(x,0.)
        h = r - radiotierra(lat,lon)
        rho = escenario.atmosfera.densidad(h)         
        w = np.array([0.,0.,-7292115e-11]) #rad/s
        vatm = cua.productovectorial(w,x)
        vrel = np.array([v[0]+vatm[0],v[1]+vatm[1],v[2]+vatm[2]])
        
        res = -0.5*1000.*rho*vrel*np.sqrt(vrel[0]**2+vrel[1]**2+vrel[2]**2)/coefbal
        return res

    def parada(self):
        global escenario        
        if escenario.colisiones == "Si":
            if self.choquetierra():
                return True
        if self.paradatiempo():
            return True

    def paradatiempo(self):
        if self.t[-1,0] >= self.tmax:
            return True

    def choquetierra(self):
        x = self.pos[-1,:]
        radio = np.sqrt(x[0]**2+x[1]**2+x[2]**2)
        lat = np.arcsin(x[2]/radio)
        radiot= radiotierra(lat,geodes = 0) 
        if radio <= radiot:
            return True
        

    def integradorcutre(self):  
        At = 1.
        for i in range(1,10,1):
            mov = self.vel[-1,:]*At
            mov= self.pos[-1,:] + mov
            self.setpos(mov)
            self.setvel(self.vel[-1,:])

    def parabolicosimple(self):    #Integracion numerica mediante euler simple
        At=.001
        i=0
        while ((self.pos[-1,1])>=-20.):
            fuerza = np.array([[0.,-9.81,0.]])

            mov = np.array([self.vel[-1,:]])
            
            
            mov = np.append(mov,fuerza,0)
            self.setpos(self.pos[-1,:]+At*mov[0,:])
            self.setvel(self.vel[-1,:]+At*mov[1,:])
            self.sett(self.t[-1]+At)

            i = i+1
            if i>1000000:
                return "Parada de emergencia"
                    
    def parabolico(self):  #Ecuaciones del tiro parabolico

        tiempo = 0.
        At= .001
        i = 0

        while ((self.pos[-1,1])>=-20.):
            
            x = self.pos[0,0] + self.vel[0,0]*tiempo
            y = self.pos[0,1] + self.vel[0,1]*tiempo - 9.81*tiempo*tiempo/2.
            z = 0.

            vx = self.vel[0,0]
            vy = self.vel[0,1] - 9.81*tiempo
            vz = 0.

            vel = np.array([vx,vy,vz])
            mov = np.array([x,y,z])

            
            self.setpos(mov)
            self.setvel(vel)

            tiempo =tiempo + At

            i = i+1
            if i>1000000:
                return "Parada de emergencia"
    def predictorcorrector4(self,At):
        error = 1.
        i = 0
        y0 = self.adamsbashforth4(At)
        while i<30:
            y1 = self.adamsmoulton4(At,y0)
            error = np.sqrt((y1[0,0]-y0[0,0])**2+(y1[0,1]-y0[0,1])**2+(y1[0,2]-y0[0,2])**2+(y1[1,0]-y0[1,0])**2+(y1[1,1]-y0[1,1])**2+(y1[1,2]-y0[1,2])**2)/np.sqrt((y1[0,0])**2+(y1[0,1])**2+(y1[0,2])**2+(y1[1,0])**2+(y1[1,1])**2+(y1[1,2])**2)
            y0 = y1
            if error <1e-7:
                return y1              
            i = i+1
        return y1
    def adamsmoulton4(self,At,fpre):


        f0 = self.f(paso = -1)
        f1 = self.f(paso = -2)
        f2 = self.f(paso = -3)
        y1 = At*(9*fpre+19*f0-5*f1+f2)/24.
        return y1

    def rungekutta4(self,At,tiempo):
        
        k1 = self.f(paso = -1, tiempo = tiempo)
        k2 = self.f(paso = -1,tiempo=tiempo+At/2,punto=At*k1[0,:]/2)
        k3 = self.f(paso = -1,tiempo=tiempo+At/2,punto=At*k2[0,:]/2)
        k4 = self.f(paso = -1,tiempo=tiempo+At,punto=At*k3[0,:])
        y1 = At*(k1+2*k2+2*k3+k4)/6.
        return y1 


    def adamsbashforth4(self,At):    

        f0 = self.f(paso=-1)
        f1 = self.f(paso=-2)
        f2 = self.f(paso=-3)
        f3 = self.f(paso=-4)

        y1 = At*(55*f0-59*f1+37*f2-9*f3)/24.
        return y1


def gravedad(x, overridemodelo = 0):  #Posicion en kilometros
    global escenario
    if overridemodelo == 0:
        modelo = escenario.modelogravedad
    else:
        modelo = overridemodelo
    h = np.sqrt(x[0]**2+x[1]**2+x[2]**2)
    
    fuerza = 398600.4418/(h*h)
    u = np.array([[-x[0]*fuerza/h,-x[1]*fuerza/h,-x[2]*fuerza/h]])
    if modelo == "Esferico":
        return u
    J2 = 1.082636e-3
    R = 6378.1363
    c = J2*398600.4418*R*R/2.
    pert0 = -3.*c*x[0]*(1.-5.*(x[2]/h)**2)/(h**5)
    pert1 = -3.*c*x[1]*(1.-5.*(x[2]/h)**2)/(h**5)
    pert2 = -3.*c*x[2]*(3.-5.*(x[2]/h)**2)/(h**5)
    upert = np.array([[u[0,0]+pert0,u[0,1]+pert1,u[0,2]+pert2]])
    if modelo == "J2":
        return upert
    if modelo =="SoloJ2":
        return np.array([[pert0,pert1,pert2]])

def xtogeo(x,t): #Trasnforma coordenadas absolutas en geograficas
    global escenario
    
    def eclat(lat,x,z,a,e):
        valor = x1*np.sin(lat)-z1*np.cos(lat)
        valor = valor-a*(e*e*np.sin(lat)*np.cos(lat)/np.sqrt(1-(e*np.sin(lat))**2))
        
        return valor
    def declat(lat,x,z,a,e):
        valor = x*np.cos(lat)-z*np.sin(lat)
        R=np.sqrt(1-(e*np.sin(lat))**2)
        valor =  valor-a*e*e*(np.cos(2*lat)/R+e*e*np.sin(2*lat)*np.sin(2*lat)/(4*(R**1.5)))
        return valor



    if isinstance(t,float) or isinstance(t,int):
        pass
    else:
        t = t[0]


    uxy = np.array([x[0],x[1],0])
    lat = cua.productoescalar(x,uxy)
    lat = lat/cua.norma(x)
    lat = lat/cua.norma(uxy)
    if lat>1.:
        lat = 1.
    lat = np.arccos(lat)
    
    if x[2] < 0 :
        lat = -lat
    #Primer paso de integracion, latitud geocentrica
    lat1= lat*180/np.pi

    v = np.array([1,0,0]) ###########Mejorar??
    lon = cua.productoescalar(uxy,v)    
    lon = lon/cua.norma(uxy)    
    lon = np.arccos(lon)    
    lon = lon*180/np.pi
    if x[1] < 0:
        lon = -lon
    
    lon = lon - girotierra(t)
    while lon >180.:
        lon = lon-360.
    while lon<-180.:
        lon = lon+360.
    
    if escenario.reptierra == "Esferica":
        lat =lat*180/np.pi
        return lat,lon

    elif escenario.reptierra == "WGS84":
        #Calculo de la latitud geodesica   $$$$$$$$$$$$$$$$$$Mejorar
        error = 1.
        a=6378.137
        f=298.257223563
        f=1./f
        e=np.sqrt(f*(2-f))
        x1 = np.sqrt(x[0]**2+x[1]**2)
        z1 = x[2]
        i=0
        lat = lat + e*e*np.sin(2.*lat)/2. + e**4*np.sin(2.*lat)*(1.+np.cos(2.*lat))/4.
        eps = eclat(lat,x1,z1,a,e)
        f1=declat(lat,x1,z1,a,e)
        lat1 = lat-eps/f1
        eps1= eclat(lat1,x1,z1,a,e)
        #print lat
        while abs(error)>=1.e-4: 
            if lat==0:
                error = abs(lat1-lat)
            else:
                error = abs(lat1-lat)/abs(lat)
            if error <= 1.e-4:
                lat = lat1
                break            
            if eps*eps1<0.:
                
                lattemp  = (lat+lat1)/2.                
                while lattemp>90.:
                    lattmep = lattemp-180.
                while lattemp<-90.:
                    lattemp = lattemp+180.
                epstemp = eclat(lattemp,x1,z1,a,e)
                #print "Cambio de signo", lat*180/3.141592,eps,lat1*180/3.141592,eps1,lattemp*180/3.141592,epstemp 
                if epstemp*eps <0:
                    lat1 = lattemp
                    eps1 = epstemp
                else:
                    lat = lattemp
                    eps = epstemp
            else:
                lat = lat1
                eps = eps1
                lat1 = lat-eps/f1                
                while lat1>90.:
                    lat1 = lat1-180.
                while lat1<-90.:
                    lat1 = lat1+180.
                eps1= eclat(lat1,x1,z1,a,e)
                
        lat = lat*180/np.pi
        while lat>90.:
            lat = lat-180.
        while lat<-90.:
            lat = lat+180.
        #print lat
        return np.array([lat,lon])

def geotox(lat,lon, t=0):#Transforma coordenadas geograficas en absolutas,sobre la tierra
    
    u=np.array([1.,0.,0.])
    lon = lon + girotierra(t)
    radio, lat = radiotierra(lat,geodes=1,geocen=1)
    u1 = np.array([0.,0.,1.])
    u2 = cua.giro(u,u1,lon-90.)
    u = cua.giro(u,u1,lon)
    u = cua.giro(u,u2,lat)
    u = radio*np.array(u)
    
    
    return u

def trayectoriageo(x,t):  #Transforma una trayectoria en su traza

    i = 1
    imax = len(x)
    traza = np.array([xtogeo(x[0,:],t[0,0])])    
    while i <imax:
        posgeo = np.array([xtogeo(x[i,:],t[i,0])])        
        posgeo[0,1] = posgeo[0,1]        
        while posgeo[0,1] < -180:
            posgeo[0,1] = posgeo[0,1] + 360
        traza = np.append(traza,posgeo,0)        
        i = i+1    
    i = 1
    i0 = 0
    j=1
    trazas = []
    while i<imax:        
        if traza[i,1] * traza[i-1,1] < -100:            
            trazas.append(traza[i0:i,:])
            i0 = i
            j = j+1
        i = i+1
    trazas.append(traza[i0:i,:])    
    return trazas, j

def girotierra(t):
    global escenario
    tiempoi = escenario.tiempo
    JD = juliana(tiempoi) + t/86400.
    D = JD - 2451545.
    JD0 = np.floor(JD)
    if JD-JD0>=0.5:
        JD0=JD0+0.5
    elif JD-JD0<0.5:
        JD0=JD0-0.5        
    D0 = JD0-2451545.

    H=(JD-JD0)*24.
    
    GMST = 6.697374558 + 0.06570982441908*D0 + 1.00273790935*H + 0.000026*((int(D/36525))**2) # En horas, formula completa

##    GMST1 = 18.697374558 + 24.06570982441908*D # Formula simplificada
    while GMST>24.:
        GMST = GMST-24.
    while GMST<0.:
        GMST = GMST+24.
    GMST = GMST*360./24.
        
    

    
##    w = 7292115e-11 #rad/s
##    ang = w*t
##    ang = ang*180/np.pi + GMST
##    while ang>360.:
##        ang = ang-360.
##    return ang
    return GMST

    
def dibujartraza(x,t,color,mapa):

    
    b , ntrazas = trayectoriageo(x,t)  
    i = 0    
    while (i < ntrazas):
        
        a = b[i]
        #mapa.plot(a[:,1],a[:,0],color = color,latlon = "True") #Si dibujas el mapa cada vez
        mapa.plot(a[:,1],a[:,0],color = color) #Si cargas el mapa desde imagen
        i = i+1

def mapa():
    from mpl_toolkits.basemap import Basemap
    
    # lon_0, lat_0 are the center point of the projection.
    # resolution = 'l' means use low resolution coastlines.
    m = Basemap(projection='ortho',lon_0=-105,lat_0=40,resolution='l')
    m.drawcoastlines()
    m.fillcontinents(color='white',lakecolor="grey")
    m.drawmapboundary(fill_color='grey')
    m.drawcountries(color = "k")
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,120.,30.))
    m.drawmeridians(np.arange(0.,420.,60.))
    
    
    mpl.show()

def radiotierra(lat, geodes=1, geocen=0): #geodes indica si es latitud geodesica. Geocen indica si tiene que devolver ademas la gocentrica
    global escenario

    if escenario.reptierra == "Esferica":
        if geocen==1:
            return 6378., lat
        else:
            return 6378.
       
    lat = lat*np.pi/180.
    a=6378.137
    f=298.257223563
    f=1./f
    e=np.sqrt(f*(2-f))

    if geodes == 0:
        r = a*np.sqrt(1.-e**2)/np.sqrt(1-e*e*np.cos(lat)*np.cos(lat))
        if geocen==1:
            return r, lat*180/np.pi
        else:
            return r

    x0 = a*np.cos(lat)/np.sqrt(1.-(e*np.sin(lat))**2)
    z0 = a*np.sin(lat)*(1-e**2)/np.sqrt(1.-(e*np.sin(lat))**2)
    
    radio = np.sqrt(x0**2+z0**2)
    if geocen ==1:
        latcen = 180*np.arccos(x0/radio)/np.pi
        if z0<0:
            latcen = -latcen
        
        return radio,latcen
    else:
        return radio


def dibujarorbita(x,t,color,ax):

    mpl.axis("off")
        
    ax.mouse_init()
    ax.set_axis_off()
    ax._axis3don = False

    max_range = np.array([abs(x[:,0].max())+abs(-x[:,0].min()), abs(x[:,1].max())+abs(-x[:,1].min()), abs(x[:,2].max())+abs(-x[:,2].min())]).max()/2.0
    max_range = max(max_range,8000.)


    ax.set_xlim( - max_range, max_range)
    ax.set_ylim( - max_range, max_range)
    ax.set_zlim( - max_range, max_range)

    ax.plot(xs=x[:,0],ys=x[:,1],zs=x[:,2],color = color)
    
    i=1
    imax = len(x)
    j=0
    apo = x[0,:]
    peri = x[0,:]
    asc = np.array([[0,0,0]])
    des = np.array([[0,0,0]])
    while i<imax:

        if cua.norma(x[i,:])> cua.norma(apo):
            apo = x[i,:]
        if cua.norma(x[i,:])< cua.norma(peri):
            peri = x[i,:]    

        if x[i,2]*x[i-1,2] < 0. and x[i,2]<0:
            des[0,:] = x[i,:]
            j = j+1
            

        if x[i,2]*x[i-1,2] < 0. and x[i,2]>0:            
            asc[0,:] = x[i,:]
            j=j+1
        i = i+1

    if cua.norma(apo)-cua.norma(peri)<=1.:
        apo=np.array([0,0,0])
        peri=np.array([0,0,0])
    
    asc = np.append(asc,np.array([[0.,0.,0.]]),0)
    des = np.append(des,np.array([[0.,0.,0.]]),0)

    ax.scatter(apo[0],apo[1],apo[2],color = color,marker="^")
    ax.scatter(peri[0],peri[1],peri[2],color = color,marker="v")
   
    ax.plot(asc[:,0],asc[:,1],asc[:,2],color = color, linestyle = "--")
    ax.plot(des[:,0],des[:,1],des[:,2],color = color, linestyle = "-.")
    mpl.axis("off")    


class propiedades(solido):

    def __init__(self):

        
        self.nombre = ""
        self.color = "b"
        self.masa = 1.0
        self.masacombustible = 0.0
        self.empuje = np.array([0,0,0])  #Empuje en ejes cuerpo
        self.consumo = 0.0
        self.etapa = 1
        self.netapas = 1
        self.tipo = "solido"
        self.balistico = 30.


        

    def actualizar(self,At):  #Funcion que reune todas las actualizaciones de propiedades
        
        self.actualizarmasa(At)
        self.actualizarconsumo()
        self.actualizarempuje()
        
    def actualizarmasa(self, At):
        self.masa = self.masa - At*self.consumo

    def actualizarconsumo(self):
        pass
    def actualziarempuje(self):
        pass
def compartirescenario(escenarioori):
    global escenario
    escenario = escenarioori

######################################### Pruebas
#a = solido()
##
#u0 = np.array([6900.,0.,0.])
#v0 = np.array([0,0,8.])
##
##
##lat, lon = 0.,-90
##print geotox(lat,lon)


#a.setinicio(u0,v0)
#a.setintegrador("AB4")
#a.integrar(None)
##
##
####
#dibujartraza(a.pos,a.t,"b")
##dibujarorbita(a.pos,a.t,"r")
##
###########Plot en 2D
##
##mpl.plot(a.pos[:,1],a.pos[:,0])
##mpl.show()
##
##
###########Plot en 3D
##
##from mpl_toolkits.mplot3d import Axes3D
##fig = mpl.figure()
##ax = fig.add_subplot(111, projection='3d')
###mpl.axis("off")
##
##
##ax.plot(xs=a.pos[:,0],ys=a.pos[:,1],zs=a.pos[:,2])
##
##mpl.show()
##




