# -*- coding: cp1252 -*-
from numpy import *

class atmosfera():


    def __init__(self):
        ## Metodo de inicializacion de la variable tipo atmosfera
        ## Inicializa las variables necesarias

        self.modelo="Jacchia"

        self.ISA = 0 #Correccion de temperatura en grados ej: ISA +5 -> 5
        self.estado = 0 #Estado de vientos 0=Calma 1=

        self.SL=[1.225, 101325, 288.15] # Densidad/presion/temperatura a nivel del mar

        self.T = []
        self.P = []
        self.rho = []
        self.h = []
        self.actualizar()

    def setISA(self,correcion):
        ## Metodo implicito para cambiar la correccion en temperatura a la atmosfera ISA standard
        self.ISA = correccion


    def setestado(self,viento):
        ## Metodo implicito para cambiar el modelo de vientos de la atmosfera
        if viento == "Calma":
            self.estado=0
        elif viento == "Ligero":
            self.estado =1

    def setmodelo(self,modelo):
        ## Metodo implicito para cambiar el modelo de atmosfera

        self.modelo= modelo

    def actualizar(self):

        if self.modelo == "Jacchia":
            self.modeloJacchia()

    def densidad(self,h):
        if self.modelo == "No":
            return 0.
        elif self.modelo == "ISA":
            _, rho, _,_ =self.modeloISA(h)
            return rho*self.SL[0]
        elif self.modelo == "Jaccia":
            
            if h>=self.h[-1]:
                return 0.
            elif h<=self.h[0]:
                return 1.225
            hsup = int(ceil(h))
            hinf = int(floor(h))
            
            Ax = h-hinf

            Ay = self.rho[hsup] - self.rho[hinf]* Ax
            return self.rho[hinf]+ Ay
    def presion(self,h):
        
        if self.modelo == "No":
            return 0.
        elif self.modelo == "ISA":
            _, _, presion,_ =self.modeloISA(h)
            return presion*self.SL[1]
        elif self.modelo == "Jacchia":
            
            hsup = int(ceil(h))
            hinf = int(floor(h))
            Ax = h-hinf

            Ay = self.P[hsup] - self.P[hinf]* Ax
            return self.P[hinf]+ Ay
    def temperatura(self,h):
        if self.modelo == "No":
            return 0.
        elif self.modelo == "ISA":
            _, _, _,temp =self.modeloISA(h)
            return temp*self.SL[2]
        elif self.modelo == "Jacchia":
            
            hsup = int(ceil(h))
            hinf = int(floor(h))
            Ax = h-hinf

            Ay = self.T[hsup] - self.T[hinf]* Ax
            return self.T[hinf]+ Ay


    def modeloJacchia(self):
        import matplotlib.pyplot as plt
        Z = []
        CH = []
        T = []
        CN2 = []
        CO2 = []
        CO = []
        CAr = []
        CHe = []
        CM = []
        WM = []
        E6P = zeros(11)
        E5M = zeros(11)
        wm0,wmN2,wmO2,wmO,wmAr,wmHe,wmH,qN2,qO2,qAr,qHe =28.96,28.0134,31.9988,15.9994,39.948,4.0026,1.0079,0.78110,0.20955,0.009343,0.000005242
        Tinf = 1000.
        for i in range(0,1001):
            Z.append(0)
            CH.append(0)
            T.append(0)
            CN2.append(0)
            CO2.append(0)
            CO.append(0)
            CAr.append(0)
            CHe.append(0)
            CM.append(0)
            WM.append(0)
            

            Z[i] = i
            CH[i] = 0
            
            if i<=85:
                h = Z[i]*6369.0/(Z[i]+6369.)
                if i<=32:
                    if i<=11:
                        hbase = 0.0
                        pbase = 1.0
                        tbase = 288.15
                        tgrad = -6.5
                        T[i] = tbase + tgrad*(h-hbase)
                        x = (tbase/T[i])**(34.163195/tgrad)
                    elif i<=20:
                        hbase = 11
                        pbase = 2.233611e-1
                        tbase = 216.65
                        tgrad = 0
                        T[i] = tbase
                        x = exp(-34.163195*(h-hbase)/tbase)
                    else:
                        hbase = 20.
                        pbase = 5.403295e-2
                        tbase = 216.65
                        tgrad = 1
                        T[i] = tbase + tgrad*(h-hbase)
                        x = (tbase/T[i])**(34.163195/tgrad)
                elif i<=51:
                    if i<=47:
                        hbase = 32
                        pbase = 8.5666784e-3
                        tbase = 228.65
                        tgrad = 2.8
                        T[i] = tbase + tgrad*(h-hbase)
                        x = (tbase/T[i])**(34.163195/tgrad)
                    else:
                        hbase = 47.
                        pbase = 1.0945601e-3
                        tbase = 270.65
                        tgrad = 0
                        T[i] = tbase
                        x = exp(-34.163195*(h-hbase)/tbase)
                elif i<=71:
                    hbase = 51.
                    pbase = 6.6063531e-4
                    tbase = 270.65
                    tgrad = -2.8
                    T[i] = tbase + tgrad*(h-hbase)
                    x = (tbase/T[i])**(34.163195/tgrad)
                else:
                    hbase = 71.
                    pbase = 3.9046834e-5
                    tbase = 214.65
                    tgrad = -2.
                    T[i] = tbase + tgrad*(h-hbase)
                    x = (tbase/T[i])**(34.163195/tgrad)

                CM[i] = 2.547e19*(288.15/T[i])*pbase*x
                y = 10.**(-3.7469+(i-85)*(0.226434-(i-85)*5.945e-3))
                x = 1- y
                WM[i] = wm0*x
                CN2[i] = qN2*CM[i]
                CO[i] = 2.*y*CM[i]
                CO2[i] = (x*qO2-y)*CM[i]
                CAr[i] = qAr*CM[i]
                CHe[i] = qHe*CM[i]
                CH[i] = 0


            elif i<=89:
                T[i] = 188.
                y = 10.**(-3.7469+(i-85)*(0.226434-(i-85)*5.945e-3))
                WM[i] = wm0 * (1-y)
                CM[i] = CM[i-1]*(T[i-1]/T[i])*(WM[i]/WM[i-1])*exp(-0.5897446*((WM[i-1]/T[i-1])*(1+Z[i-1]/6356.766)**(-2) + (WM[i]/T[i])*(1+Z[i]/6356.766)**(-2)))
                y = 10.**(-3.7469+(i-85)*(0.226434-(i-85)*5.945e-3))
                x = 1- y
                WM[i] = wm0*x
                CN2[i] = qN2*CM[i]
                CO[i] = 2.*y*CM[i]
                CO2[i] = (x*qO2-y)*CM[i]
                CAr[i] = qAr*CM[i]
                CHe[i] = qHe*CM[i]
                CH[i] = 0

            else:
                if i<=90.:
                    T[i] = 188.
                elif Tinf <188.1:
                    T[i] = 188.
                else:
                    x = 0.0045 * (Tinf-188.)
                    Tx = 188.+110.5*log(x+sqrt(x*x+1.))
                    Gx = (pi/2)*1.9*(Tx-188.)/(125.-90.)
                    if i<=125:
                        T[i] = Tx + ((Tx-188.)/(pi/2))*arctan((Gx/(Tx-188.))*(Z[i]-125.)*(1.+1.7*((Z[i]-125.)/(Z[i]-90.))**2))
                    else:
                        T[i] = Tx + ((Tinf-Tx)/(pi/2))*arctan((Gx/(Tinf-Tx))*(Z[i]-125.)*(1.+5.5e-5*(Z[i]-125.)**2))
                if i<=100:
                    x = i-90.
                    E5M[i-90] = 28.89122 + x*(-2.82071e-2 + x*(-6.59924e-3 + x*(-3.39574e-4 + x*(6.19256e-5 + x*(-1.84796e-6)))))
                    if i<= 90:
                        E6P[0] = 7.145e13*T[90]
                    else:
                        G0 = (1+Z[i-1]/6356.766)**(-2)
                        G1 = (1+Z[i]  /6356.766)**(-2)
                        E6P[i-90] = E6P[i-91]*exp(-0.5897446*(G1*E5M[i-90]/T[i] + G0*E5M[i-91]/T[i-1]))
                    x = E5M[i-90]/wm0
                    y = E6P[i-90]/T[i]
                    CN2[i] = qN2*y*x
                    CO[i] = 2.*(1.-x)*y
                    CO2[i] = (x*(1.+qO2)-1.)*y
                    CAr[i] = qAr*y*x
                    CHe[i] = qHe*y*x
                    CH[i] = 0
                else:
                    G0 = (1+Z[i-1]/6356.766)**(-2)
                    G1 = (1+Z[i]/6356.766)**(-2)
                    x =  0.5897446*( G1/T[i] + G0/T[i-1] )
                    y = T[i-1]/T[i]
                    CN2[i] = CN2[i-1]*y*exp(-wmN2*x)
                    CO2[i] = CO2[i-1]*y*exp(-wmO2*x)
                    CO[i]  =  CO[i-1]*y*exp(-wmO*x)
                    CAr[i] = CAr[i-1]*y*exp(-wmAr*x)
                    CHe[i] = CHe[i-1]*(y**0.62)*exp(-wmHe*x)
                    CH[i] = 0
            
            
        for i in range(90,1001):  #Correcciones empiricas Jacchia 1977

            CO2[i] = CO2[i]*( 10.0**(-0.07*(1.0+tanh(0.18*(Z[i]-111.0)))) )
            CO[i] = CO[i]*( 10.0**(-0.24*exp(-0.009*(Z[i]-97.7)**2)) )
            CM[i] = CN2[i]+CO2[i]+CO[i]+CAr[i]+CHe[i]+CH[i]
            WM[i] = ( wmN2*CN2[i]+wmO2*CO2[i]+wmO*CO[i]+wmAr*CAr[i]+wmHe*CHe[i]+wmH*CH[i] ) / CM[i]


        phid00 = 10.0**( 6.9 + 28.9*Tinf**(-0.25) ) / 2.e20
        phid00 = phid00 * 5.24e2
        H_500 = 10.0**( -0.06 + 28.9*Tinf**(-0.25) )
        for i in range(150,1001):
            phid0 = phid00/sqrt(T[i])
            WM[i] = wmH*0.5897446*( (1.0+Z[i]/6356.766)**(-2) )/ T[i] + phid0
            CM[i] = CM[i]*phid0
          
        y = WM[150]
        WM[150] = 0
        for i in range(151,1001):
            x = WM[i-1] + (y+WM[i])
            y = WM[i]
            WM[i] = x
          
        for i in range(150,1001):
            WM[i] = exp( WM[i] ) * ( T[i]/T[150] )**0.75
            CM[i] = WM[i]*CM[i]
          
        y = CM[150]
        CM[150] = 0
        for i in range(151,1001):
            x = CM[i-1] + 0.5*(y+CM[i])
            y = CM[i]
            CM[i] = x
          

        for i in range(150,1001):
            CH[i] = ( WM[500]/WM[i] ) * (H_500 - (CM[i]-CM[500]) )
          
          
        for i in range(150,1001):
            CM[i] = CN2[i]+CO2[i]+CO[i]+CAr[i]+CHe[i]+CH[i]
            WM[i] = ( wmN2*CN2[i]+wmO2*CO2[i]+wmO*CO[i]+wmAr*CAr[i]+wmHe*CHe[i]+wmH*CH[i] ) / CM[i]
        for i in range(0,1001):
            self.T.append(0)
            self.P.append(0)
            self.rho.append(0)
            self.h.append(0)
            self.T[i] = T[i]
            self.rho[i] = CM[i]*WM[i]*1000/6.02214e23
            self.P[i] = self.rho[i]* 8.3144621 *1000* self.T[i]/WM[i]
            self.h[i] = Z[i]


        




    def modeloISA(self,x):
        ## Calcula la densidad del modelo de atmosfera ISA

        if x>= 86.0:          #######Atmosfera alta, sacado del atmos76.f de pdas.com
                                    #Funciones evaluatecubic, kinetic temperature


            
            def EvaluateCubic(a,fa,fpa,b,fb,fpb,u):  #Evalua un polinomio cubico definido por la funcion y su primera derivada en dos puntos
                d = (fb-fa)/(b-a)
                t = (u-a)/(b-a)
                p = 1.0-t
                fu = p*fa + t*fb - p*t*(b-a)*(p*(d-fpa)-t*(d-fpb))
                return fu


            def KineticTemperature(z):   #Halla la temepratura cinetica para altuas mayores de 86 Km

                Z7, Z8, Z9, Z10, Z11, Z12 = 86.0,91.0,110.0,12.0,500.0,1000.0
                T7, T8, T9, T10, T11, T12 = 186.8673, 186.8673, 240.0,360.0,999.2356,1000.0
                C1, C2, C3, C4, TC = -76.3232, 19.9429,12.0,0.01875,263.1905
                REARTH = 6356.766

                if z <= Z8:
                    t = T7
                elif z< Z9:
                    xx = (z-Z8)/C2
                    yy = sqrt(1.0-xx*xx)
                    t= TC + C1*yy
                elif z <= Z10:
                    t = T9 + C3*(z-Z9)

                else:
                    xx = (REARTH + Z10)/(REARTH+z)
                    yy = (T12-T10)*exp(-C4*(z-Z10)*xx)
                    t = T12-yy

                return t

            
            Ztab = [86.,  93., 100., 107., 114.,121., 128., 135., 142., 150.,160., 170., 180., 190., 200.,250., 300., 400.,500., 600., 700., 800., 1000.]
            Ptab = [3.7338e-1, 1.0801e-1, 3.2011e-2, 1.0751E-2, 4.4473e-3,2.3402e-3, 1.4183e-3, 9.3572e-4, 6.5297e-4, 4.5422e-4,3.0397e-4, 2.1212e-4, 1.5273e-4, 1.1267e-4, 8.4743e-5,2.4767e-5, 8.7704e-6, 1.4518e-6,3.0236e-7, 8.2130e-8, 3.1908e-8, 1.7036e-8, 7.5138e-9]
            RHOtab = [6.9579e-06, 1.9997e-06, 5.6041e-07, 1.6426E-07, 4.9752e-08,1.9768e-08, 9.7173e-09, 5.4652e-09, 3.3580e-09, 2.0757e-09,1.2332e-09, 7.8155e-10, 5.1944e-10, 3.5808e-10, 2.5409e-10,6.0732e-11, 1.9160e-11, 2.8031e-12,5.2159e-13, 1.1369e-13, 3.0698e-14, 1.1361e-14, 3.5614e-15]
            LOGP = [-0.985159,  -2.225531,  -3.441676,  -4.532756,  -5.415458,-6.057519,  -6.558296,  -6.974194,  -7.333980,  -7.696929,-8.098581,  -8.458359,  -8.786839,  -9.091047,  -9.375888,-10.605998, -11.644128, -13.442706, -15.011647, -16.314962,-17.260408, -17.887938, -18.706524]
            DLOGPDZ = [-11.875633, -13.122514, -14.394597, -15.621816, -16.816216,  -17.739201, -18.449358, -19.024864, -19.511921, -19.992968,  -20.513653, -20.969742, -21.378269, -21.750265, -22.093332,  -23.524549, -24.678196, -26.600296, -28.281895, -29.805302,  -31.114578, -32.108589, -33.268623]
            LOGRHO = [-0.177700,  -0.176950,  -0.167294,  -0.142686,  -0.107868,  -0.079313,  -0.064668,  -0.054876,  -0.048264,  -0.042767,  -0.037847,  -0.034273,  -0.031539,  -0.029378,  -0.027663,  -0.022218,  -0.019561,  -0.016734,  -0.014530,  -0.011315,  -0.007673,  -0.005181,  -0.003500]
            DLOGRHODZ = [-0.177900,  -0.180782,  -0.178528,  -0.176236,  -0.154366,  -0.113750,  -0.090551,  -0.075044,  -0.064657,  -0.056087,  -0.048485,  -0.043005,  -0.038879,  -0.035637,  -0.033094,  -0.025162,  -0.021349,  -0.017682,  -0.016035,  -0.014330,  -0.011626,  -0.008265,  -0.004200]
            NTAB = 22

            if x >= Ztab[NTAB]: #Elimina alturas mayores que 1000
                delta = 1.0e-20
                sigma = 1.0e-21
                theta = 1000.0/self.SL[2]
                return [x,sigma, delta,theta]



            i = 0
            while(i<=NTAB):
                if Ztab[i] < x:
                    i = i+1
                else:
                    break
            i = i-1


            p=exp(EvaluateCubic(Ztab[i],LOGP[i],DLOGPDZ[i],Ztab[i+1],LOGP[i+1],DLOGPDZ[i+1], x))
            delta=p/self.SL[1]
            rho=exp(EvaluateCubic(Ztab[i],LOGRHO[i],DLOGRHODZ[i],Ztab[i+1],LOGRHO[i+1],DLOGRHODZ[i+1], x))
            sigma=rho/self.SL[0]
            theta=KineticTemperature(x)/self.SL[2]
                        


            return [x, sigma, delta, theta]
                


        else:
            REARTH = 6369.0 #Radio de la tierra
            GMR = 34.163195  #Constante de los gases
            NTAB=8  #tamaño de las tablas/capas de la atmosfera baja

            htab = (0.0,11.0,20.0,32.0,47.0,51.0,71.0,84.852)   #Tabla de alturas geopotenciales
            ttab = (288.15,216.65,216.65,228.65,270.65,270.65,214.65,186.946)  #Tabla de temperaturas
            ptab = (1.0, 2.233611E-1, 5.403295E-2, 8.5666784E-3, 1.0945601E-3, 6.6063531E-4, 3.9046834E-5, 3.68501E-6) #Tabla de presiones, referidas a P0
            gtab = (-6.5, 0.0, 1.0, 2.8, 0.0, -2.8, -2.0, 0.0) #Tabla de gradientes de temperatura

            if x<=1e-6:
                return [0.,1.,1.,1.]
            
            h = x*REARTH/ (x+REARTH)  #Altura geopotencial

            #Busqueda de la altura en htab
            i = 0
            while(i<=size(htab)):
                if htab[i] < h:
                    i = i+1
                else:
                    break
            i = i-1
            
            
            
            tgrad = gtab[i]
            tbase = ttab[i]
            deltah = h-htab[i]
            tlocal = tbase +tgrad*deltah
            theta = tlocal /self.SL[2]

            if tgrad== 0.0:
                delta = ptab[i]*exp(-GMR*deltah/tbase)
            else:
                delta = ptab[i]*(tbase/tlocal)**(GMR/tgrad)
            sigma = delta/theta
            return [x, sigma,delta,theta]
         
    def atmosfera(self,h):   #Calcula la densidad teniendo en cuenta el modelo de atmosfera
        if self.modelo == "ISA":
            y = self.modeloISA(h)
            return [h, y[1]*self.SL[0], y[2]*self.SL[1], y[3]*self.SL[2]]
            
        elif self.modelo == "No":

             return [h,0.0,0.0,0.0]

        elif self.modelo == "Jacchia":
            return [h,self.densidad(h), self.presion(h),self.temperatura(h)]

    def perfiles(self,hmin,hmax):
        import matplotlib.pyplot as plt
        h = linspace(hmin,hmax,hmax+1-hmin)
        rho = linspace(0,0,hmax+1-hmin)
        T = linspace(0,0,hmax+1-hmin)
        P = linspace(0,0,hmax+1-hmin)
        i=0
        for i in range(hmin,hmax):
            
            _,rho[i],P[i],T[i] = self.atmosfera(h[i])

        plt.subplot(1,3,1)
        plt.plot(T,h,"r")
        plt.xlabel("Temperatura (K)")
        plt.ylabel("Altura (Km)")
        #plt.xticks([0,50,100,150,200,250,300],[0,"",100,"",200,"",300])


        plt.subplot(1,3,2)
        plt.plot(rho,h,"g")
        plt.xlabel("Densidad (Kg/m3)")
        plt.xticks([0,0.2,0.4,0.6,0.8,1.0,1.2,1.4],[0,"","","","",1.,"",""])

        plt.subplot(1,3,3)
        plt.plot(P,h)
        plt.xlabel("Presion (Pa)")
        plt.xticks([0,25000,50000,75000,100000], [0,"",50000,"",100000])
        
        plt.show()
        
                


        
        
############Pruebas        

#a = atmosfera()
#a.perfiles(0,1000)

