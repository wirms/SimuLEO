import numpy as np
def ang2cua(v,theta,rad=0):

    
    if rad==0:
        theta = theta * np.pi/180
    elif rad==1:
        pass
    else:
        return "Error en cuaternios/ang2cua, rad debe ser 0 o 1"

    if len(v) == 3:
        pass
    else:
        return "Error en cuaternios/ang2cua, v debe ser una lista de 3 elementos"
    theta=theta/2
    
    modv = norma(v)
    q=[0,0,0,0]
    q[0] = np.cos(theta)
    q[1] = np.sin(theta)* v[0]/modv
    q[2] = np.sin(theta)* v[1]/modv
    q[3] = np.sin(theta)* v[2]/modv
    
    modq = norma(q)
    
    if modq <=1e-8:
        pass
    else:
        for i in range(0,4):
            
            q[i] = q[i]/modq
         
    return q

def pro(p,q):
#Producto de dos cuaterniones, producto de Hamilton

    if len(p) and len(q) == 4:
        pass
    else:
        return "Error en cuaternios/pro, deben ser dos cuaternios de 4 elementos"
    u=[0,0,0,0]
    u[0] = p[0]*q[0] - p[1]*q[1] - p[2]*q[2] - p[3]*q[3]
    u[1] = p[0]*q[1] + p[1]*q[0] + p[2]*q[3] - p[3]*q[2]
    u[2] = p[0]*q[2] + p[2]*q[0] + p[3]*q[1] - p[1]*q[3]
    u[3] = p[0]*q[3] + p[3]*q[0] + p[1]*q[2] - p[2]*q[1]

    return u
def conj(q):
    if len(q)==4:
        pass
    else:
        return "Error en cuaternios/conj, debe ser una lista de 4 elementos"

    r = [0,0,0,0]
    r[0], r[1],r[2],r[3] = q[0],-q[1],-q[2],-q[3]
    return r

def norma(q):
    if len(q) == 4:
        norma = q[0]**2+q[1]**2+q[2]**2+q[3]**2
    elif len(q) ==3:
        norma = np.sqrt(q[0]**2+q[1]**2+q[2]**2)
    else:
        return "Error en cuaternios/norma, debe ser una lista de 4 elementos"

    
    return norma

def conv(v,q):
    p = [0,v[0],v[1],v[2]]
       

    p1 = pro(p,conj(q))
    p1 = pro(q,p1)

    if len(p1) == 4:
        p1 = [p1[1],p1[2],p1[3]]
        
    return p1

def giro(u,v,theta): #Giro de u, theta grados alrrededor de v
    q = ang2cua(v,theta)
    u1 = conv(u,q)
    return u1
def girar(u,q):
    v = conv(u,q)
    return [v[1],v[2],v[3]]

def giro2cua(u,v): #Giro necesario para llevar u a v

    theta = (u[0]*v[0] + u[1]*v[1] + u[2]*v[2])
    theta = theta/norma(u)
    theta = theta/norma(v)
    
    theta = np.arccos(theta)
    
    
    g = [0,0,0]
    g[0] = u[1]*v[2] - u[2]*v[1]
    g[1] = u[2]*v[0] - u[0]*v[2]
    g[2] = u[0]*v[1] - u[1]*v[0]
    modg =  norma(g)
    for i in range(0,3):
        g[i] = g[i]/modg
    
    q=ang2cua(g,theta,rad=1)
    return q

def verticallocal(x):
    
    modv = norma(x)
    
    v = np.array([x[0]/modv,x[1]/modv,x[2]/modv])
    return v
def productovectorial(u,v):

    if len(u) and len(v) == 3:
        pass
    else:
        return "Error en cuaternios/productovectorial, los dos vectores deben ser una lista de 3 elementos"
    
    
    
    g0 = u[1]*v[2] - u[2]*v[1]
    g1 = u[2]*v[0] - u[0]*v[2]
    g2 = u[0]*v[1] - u[1]*v[0]
    g= np.array([g0,g1,g2])
    return g

def productoescalar(u,v):

    pro = u[0]*v[0] + u[1]*v[1] + u[2]*v[2]
    return pro
##############################################







