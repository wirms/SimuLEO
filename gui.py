# -*- coding: UTF-8 -*-
import matplotlib.pyplot as mpl
import matplotlib as mmpl

from integracion import *
from orbita import *
import mision as mis


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.misc import imread

from Tkinter import *
import ttk
import tkMessageBox
mmpl.use("TkAgg")
root = Tk()
#w, h = root.winfo_screenwidth(), root.winfo_screenheight()   #Para ventana maximizada
#root.geometry("%dx%d+0+0" % (w, h))
#root.overrideredirect(1)   #Quita la barra superior y la de inicio
toplevel = root.winfo_toplevel()    #Ventana maximizada bien
toplevel.wm_state("zoomed")
#root.attributes("-fullscreen", True)  #Otra ventana maximizada


def cerrarprograma():
    if tkMessageBox.askokcancel(title=" ¿Salir? ",message= " ¿Está seguro de que desea salir? "):
        root.quit()
        root.destroy()
root.protocol("WM_DELETE_WINDOW", lambda:cerrarprograma())

objetos = {}
dibujarobjetos = []
escenario = mis.prescenario()


class barrastatus(Frame):  #Barra de estado inferior
    def __init__ (self, master):
        Frame.__init__(self,master)
        self.label = Label(self,bd=1,relief=FLAT,bg="grey",anchor=W)
        self.label.pack(fill=X)

    def set(self,texto,*args):
        self.label.config(text=texto)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
    def completado(self):
        self.set("    Completado")
        root.after(10000,self.clear)
        
  
framebase = ttk.Frame(root)  #Toda la ventana, menos la barra de menus y la barra de estado

areabotones1 = ttk.Frame(framebase,relief= "sunken") #Area superior para los botones
areabotones2 = ttk.Frame(framebase,relief= "sunken")
areadibujo = ttk.Frame(framebase)
areaarbol = ttk.Frame(framebase)


barramenu = Menu(root)
menuarchivo = Menu(barramenu)
menuarchivo.add_command(label=" Nueva mision ",command = lambda:nuevamision())
menuarchivo.add_command(label=" Abrir ",command = lambda:abrir())
menuarchivo.add_separator()
menuarchivo.add_command(label = " Guardar ", command = lambda: guardar())
menuarchivo.add_command(label = " Guardar como ",command = lambda:guardarcomo())
menuarchivo.add_separator()
menuarchivo.add_command(label = " Cerrar ",command = cerrarprograma)
barramenu.add_cascade(menu=menuarchivo, label= "Mision")

menuanadir = Menu(barramenu)
menuanadir.add_command(label = " Añadir solido ", command = lambda:botonnuevosolido())
menuanadir.add_command(label = " Añadir orbita ", command = lambda:botonnuevaorbita())
menuanadir.add_command(label = " Añadir base ", command = lambda:botonnuevabase())
menuanadir.add_command(label = " Añadir sensor ", command = lambda:botonnuevosensor())
barramenu.add_cascade(menu = menuanadir, label = " Insertar ") 

menuopciones = Menu(barramenu)
menuopciones.add_command(label=  " Resultados ",command = lambda:ventanaresultados())
menuopciones.add_command(label = " Asistente de maniobras ", command = lambda:ventanamaniobras.mostrar())
menuopciones.add_command(label = " Asistente de visibilidad ",command = lambda:ventanavisibilidad.mostrar())
menuopciones.add_separator()
menuopciones.add_command(label = " Parametros ",command = lambda: ventanaopciones())
barramenu.add_cascade(menu = menuopciones, label = "Herramientas")
root.config(menu=barramenu)



def nuevamision():
    global objetos,objetoactual,nombremision,dibujarobjetos

    if tkMessageBox.askokcancel(title = " ¿Está seguro? ", message= " Se perderan todos los datos no guardados "):
        objetos = {}
        objetoactual = ""
        dibujarobjetos = []
        actualizararbol()
        actualizarcanvas()
        nombremision = ""
nombremision = ""

def guardarconfig():
    global escenario
    config = open("./archivos/config.cfg","w")
    config.write("Tierra= "+escenario.reptierra+"\n")
    config.write("Atmosfera= "+escenario.modeloatmosfera+"\n")
    config.write("Gravedad= "+escenario.modelogravedad+"\n")
    config.write("Colisiones= "+escenario.colisiones+"\n")
    config.write("Tiempo= "+str(escenario.tiempo)+"\n")
    config.write("Puntos= "+str(escenario.puntos)+"\n")
    config.write("Ultimospuntos= "+str(escenario.ultimospuntos)+"\n")
    config.write("Conosensor= "+escenario.conosensor+"\n")
    config.write("Maximosensor= "+escenario.maximosensor+"\n")

def cargarconfig():
    global escenario
    config = open("./archivos/config.cfg","r")
    def leer(archivo):
        texto = config.readline()
        texto = texto.split("= ")
        texto = texto[1]
        texto = texto.rstrip("\n")
        return texto
    escenario.reptierra = leer(config)
    escenario.modeloatmosfera = leer(config)
    escenario.atmosfera.modelo = escenario.modeloatmosfera
    escenario.modelogravedad = leer(config)
    escenario.colisiones = leer(config)
    tiempo = leer(config)
    tiempo = tiempo.strip("[]")
    tiempo = tiempo.split(", ")
    for i in range(0,6):
        tiempo[i] = int(float(tiempo[i]))
    escenario.tiempo = tiempo
    escenario.puntos = int(float(leer(config)))
    escenario.ultimospuntos = int(float(leer(config)))
    escenario.conosensor= leer(config)
    escenario.maximosensor= leer(config)

    
    compartirescenario(escenario)

cargarconfig()
    
def guardar():
    
    class escritorarchivos():
        global objetos,dibujarobjetos
        def __init__(self,archivo):
            self.archivo = open(archivo,"w")
            self.escribir()
        def e(self,texto):
            texto = str(texto)
            self.archivo.write(texto+"\n")            
        def encabezado(self):
            self.e("$$$Archivo de mision$$$ " + nombremision)
            self.e("Objetos= "+str(len(objetos)))
        def esolido(self,solido):
            self.e("$$$Objeto tipo solido$$$")
            self.e("Nombre= "+solido.propiedades.nombre)
            self.e("Color= "+solido.propiedades.color)
            if solido.propiedades.nombre in dibujarobjetos:
                self.e("Oculto= 0")
            else:
                self.e("Oculto= 1")
            self.e("Tiempo  Posicion   Velocidad")
            i = 0
            while i<len(solido.pos):
                texto = str(solido.t[i]) + "   " + str(solido.pos[i,:]) + "   " + str(solido.vel[i,:])
                self.e(texto)
                i = i+1                         
            self.e("$$$Fin de objeto$$$")

        def eorbita(self,orbita):
            self.e("$$$Objeto tipo orbita$$$")
            self.e("Nombre= "+orbita.propiedades.nombre)
            self.e("Color= "+orbita.propiedades.color)
            if orbita.propiedades.nombre in dibujarobjetos:
                self.e("Oculto= 0")
            else:
                self.e("Oculto= 1")
                self.e("Parametros")
            self.e("a= " +str(orbita.parametros[0]))
            self.e("e= " +str(orbita.parametros[1]))
            self.e("i= " +str(orbita.parametros[2]))
            self.e("ascrec= " +str(orbita.parametros[3]))
            self.e("argper= " +str(orbita.parametros[4]))
            self.e("$$$Fin de objeto$$$")
            
        def ebase(self,base):
            self.e("$$$Objeto tipo base$$$")
            self.e("Nombre= "+base.propiedades.nombre)
            self.e("Color= "+base.propiedades.color)
            if base.propiedades.nombre in dibujarobjetos:
                self.e("Oculto= 0")
            else:
                self.e("Oculto= 1")
            self.e("Posicion")
            self.e(base.pos[0,:])
            self.e("$$$Fin de objeto$$$")
        
        def escribir(self):
            self.encabezado()
            for objeto in objetos:
                if isinstance(objetos[objeto],solido):
                    self.esolido(objetos[objeto])
                elif isinstance(objetos[objeto],orbita):
                    self.eorbita(objetos[objeto])
                elif isinstance(objetos[objeto],base):
                    self.ebase(objetos[objeto])
            self.e("$$$Fin de archivo$$$")
            self.archivo.close()
            
    global objetos,nombremision,barrastatus
    
    if nombremision == "":

        guardarcomo()
        return
    barrastatus.set("Guardando...")
    escritor = escritorarchivos(nombremision)
    barrastatus.completado()

def guardarcomo():
    import tkFileDialog
    global nombremision

    nombremision = tkFileDialog.asksaveasfilename(defaultextension = ".mis",filetypes = [("Archivos de mision",".mis")] ,initialdir = "./archivos",initialfile = "Nueva mision.mis")
    guardar()
def abrir():
    import tkFileDialog
    global nombremision,objetoactual
    nuevamision()
    nombremision = tkFileDialog.askopenfilename(defaultextension = ".mis",filetypes = [("Archivos de mision",".mis")] ,initialdir = "./archivos")
    
    class interpretearchivos():
        global objetos, dibujarobjetos,barrastatus
        def __init__(self,archivo):
            self.archivo = open(archivo,"r")
            self.interprete()

        def r(self):
            texto = self.archivo.readline()
            texto = texto.split("= ")
            texto = texto[1]
            texto = texto.rstrip("\n")
            return texto

        def interprete(self):
            barrastatus.set("Abriendo...")
            self.archivo.readline()
            self.archivo.readline()
            fin=0
            while fin==0:
                texto = self.archivo.readline()
                
                
                if texto == "$$$Objeto tipo solido$$$\n":
                    self.leersolido()
                elif texto == "$$$Objeto tipo orbita$$$\n":
                    self.leerorbita()
                elif texto == "$$$Objeto tipo base$$$\n":
                    pass
                elif texto == "$$$Fin de archivo$$$\n":
                    return
            barrastatus.set("Actualizando...")
            
        def leersolido(self):
            global objetos, dibujarobjetos
            objetotemp = solido()                        
            objetotemp.propiedades.nombre = self.r()                        
            objetotemp.propiedades.color = self.r()
            
            texto = self.archivo.readline()
            if texto == "Oculto= 0":
                dibujarobjetos.append(objetotemp.propiedades.nombre)
            self.r()
            fin = 0
            while fin ==0:
                texto = self.r()
                if texto[0:2]=="$$$":
                    return
                texto.split("= ")
                texto.strip("][")
                print texto
        def leerorbita(self):
            global objetos, dibujarobjetos
            objetotemp = orbita()           
            objetotemp.propiedades.nombre = self.r()                        
            objetotemp.propiedades.color = self.r()            
            texto = self.archivo.readline()
            if texto == "Oculto= 0\n":
                dibujarobjetos.append(objetotemp.propiedades.nombre)
            objetotemp.parametros[0] = float(self.r())                        
            objetotemp.parametros[1] = float(self.r())                        
            objetotemp.parametros[2] = float(self.r())            
            objetotemp.parametros[3] = float(self.r())            
            objetotemp.parametros[4] = float(self.r())
            self.archivo.readline()

            objetotemp.orbita()
            objetos.update({objetotemp.propiedades.nombre:objetotemp})
            
    objetoactual=""
    interprete = interpretearchivos(nombremision)
    actualizararbol()
    
    actualizarcanvas()
    barrastatus.completado()

def ventanaopciones():
    global escenario
    ventanaop = Toplevel(root)
    ventanaop.title(" Opciones de escenario ")
    geometria = "350x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
    ventanaop.geometry(geometria)
    framebotones = ttk.Frame(ventanaop)
    botonaplicar = ttk.Button(framebotones, text = " Aplicar ", command = lambda: aplicar())
    botoncancelar = ttk.Button(framebotones, text = " Cancelar ", command = lambda:cancelar())
    botonaceptar = ttk.Button(framebotones, text = " Aceptar ", command = lambda:aceptar())
    notebook = ttk.Notebook(ventanaop)
    frameescenario = ttk.Frame(notebook)    
    notebook.add(frameescenario, text = " Escenario ")
    framerep = ttk.Frame(notebook)
    notebook.add(framerep, text = " Representacion ")
    notebook.pack(side = TOP, fill = BOTH, expand = 1)
    framebotones.pack(side=BOTTOM, expand = 0, fill = X)
    botoncancelar.pack(side=RIGHT)
    botonaplicar.pack(side=RIGHT)
    botonaceptar.pack(side=RIGHT)

    valortierra = StringVar()  
    labeltierra = ttk.Label(frameescenario, text = " Tierra ")
    tierraesferica = ttk.Radiobutton(frameescenario, text = "Esferica", variable = valortierra, value = "Esferica")
    tierraWGS84 = ttk.Radiobutton(frameescenario, text = "Elipsoide WGS84", variable = valortierra, value = "WGS84")
    if  escenario.reptierra =="Esferica":
        tierraesferica.invoke()
    elif escenario.reptierra == "WGS84":
        tierraWGS84.invoke()
        
    valoratmosfera = StringVar()        
    labelatmosfera = ttk.Label(frameescenario, text = " Atmósfera ")
    atmosferades = ttk.Radiobutton(frameescenario, text = "Sin atmósfera", variable = valoratmosfera, value = "No")
    atmosferaJC = ttk.Radiobutton(frameescenario, text = "Jacchia", variable = valoratmosfera, value = "Jaccia")
    if escenario.modeloatmosfera == "No":
        atmosferades.invoke()
    elif escenario.modeloatmosfera == "Jaccia":
        atmosferaJC.invoke()

    valorcolisiones = StringVar()
    labelcolisiones = ttk.Label(frameescenario, text = " Colisiones ")
    sincolisiones = ttk.Radiobutton(frameescenario, text = "No", variable = valorcolisiones, value = "No")
    concolisiones = ttk.Radiobutton(frameescenario, text = "Activadas", variable = valorcolisiones, value = "Si")
    if escenario.colisiones == "No":
        sincolisiones.invoke()
    elif escenario.colisiones == "Si":
        concolisiones.invoke()

    valorgravedad = StringVar()
    labelmodelograv = ttk.Label(frameescenario, text = " Modelo gravitatorio ")
    gravesferico = ttk.Radiobutton(frameescenario, text = " Esferico ", variable = valorgravedad, value = "Esferico")
    gravJ2 = ttk.Radiobutton(frameescenario, text = "J2", variable = valorgravedad, value = "J2")
    if escenario.modelogravedad == "Esferico":
        gravesferico.invoke()
    elif escenario.modelogravedad == "J2":
        gravJ2.invoke()

    frametiempo = ttk.Frame(frameescenario)
    labeltiempo = ttk.Label(frametiempo, text = " Tiempo inicial ")
    labelh = ttk.Label(frametiempo, text = "h:")
    labelm = ttk.Label(frametiempo, text = "m:")
    labels = ttk.Label(frametiempo, text = "s   UTC    ")
    entradah = Entry(frametiempo,width = 2)
    entradam = Entry(frametiempo,width = 2)
    entradas = Entry(frametiempo,width = 2)
    entradah.insert(0,escenario.tiempo[3])
    entradam.insert(0,escenario.tiempo[4])
    entradas.insert(0,escenario.tiempo[5])
    labelfecha = ttk.Label(frametiempo, text = " dd/mm/yyyy ")
    entradad = Entry(frametiempo,width = 2)
    entradames = Entry(frametiempo, width = 2)
    entradaa = Entry(frametiempo, width = 4)
    entradad.insert(0,escenario.tiempo[2])
    entradames.insert(0,escenario.tiempo[1])
    entradaa.insert(0,escenario.tiempo[0])
    labelsep = ttk.Label(frametiempo,text = "/")
    labelsep2 = ttk.Label(frametiempo, text = "/")
    labelsep3 = ttk.Label(frametiempo, text = "    ")

    labelpuntos = ttk.Label(framerep, text =" Representar objetos cada ")
    entradapuntos = Spinbox(framerep,values = (1,10,100), width = 7)
    entradapuntos.delete(0,"end")
    entradapuntos.insert(0,escenario.puntos)
    labelcadapuntos = ttk.Label(framerep, text = " puntos")
    labelultimos = ttk.Label(framerep, text = " Representar desde los ultimos ")
    entradaultimos = Spinbox(framerep, values = (1000,10000,100000,1000000), width = 7)
    entradaultimos.delete(0,"end")
    entradaultimos.insert(0,escenario.ultimospuntos)
    labelultimospuntos = ttk.Label(framerep, text = " puntos")
    valorconosensor = StringVar()
    entradaconosensor=ttk.Checkbutton(framerep, text = " Dibujar los sensores ", var=valorconosensor,onvalue="Si", offvalue="No")
    if escenario.conosensor=="Si":
        entradaconosensor.invoke()
    valormaximosensor = StringVar()
    entradamaximosensor=ttk.Checkbutton(framerep, text = " Dibujar la maxima visibilidad de los sensores ", var=valormaximosensor, onvalue="Si", offvalue="No")
    if escenario.maximosensor=="Si":
        entradamaximosensor.invoke()

    
    labeltierra.grid(row = 0, column = 0, sticky = (N,S,E,W),columnspan = 2)
    tierraesferica.grid(row = 1, column = 0, sticky = W)
    tierraWGS84.grid(row = 1, column = 1, sticky = W)
    labelatmosfera.grid(row = 2, column = 0, sticky = (N,S,E,W), columnspan = 2)
    atmosferades.grid(row = 3, column = 0, sticky = W)
    atmosferaJC.grid(row = 3, column = 1, sticky = W)
    labelcolisiones.grid(row = 4, column = 0, sticky = (N,S,E,W), columnspan = 2)
    sincolisiones.grid(row = 5, column = 0, sticky = W)
    concolisiones.grid(row = 5, column = 1, sticky = W)
    labelmodelograv.grid(row = 6, column = 0, sticky = (N,S,E,W), columnspan = 2)
    gravesferico.grid(row = 7, column = 0, sticky = W)
    gravJ2.grid(row = 7, column = 1, sticky = W)
    frametiempo.grid(row = 8, column = 0, columnspan = 2, sticky = (N,S,E,W))
    labeltiempo.grid(row = 0, column = 0, columnspan = 10, sticky = W)
    labelh.grid(row = 1, column = 1)
    labelm.grid(row = 1, column = 3)
    labels.grid(row = 1, column = 5)
    entradah.grid(row = 1, column = 0)
    entradam.grid(row = 1, column = 2)
    entradas.grid(row = 1, column = 4)
    labelfecha.grid(row = 0, column = 7, columnspan = 10)
    entradad.grid(row = 1, column = 7)
    labelsep.grid(row = 1, column = 8)
    entradames.grid(row = 1, column = 9)
    labelsep2.grid(row = 1, column = 10)
    entradaa.grid(row = 1, column = 11)
    labelsep3.grid(row = 1, column = 6)

    labelpuntos.grid(row = 0, column = 0)
    entradapuntos.grid(row = 0, column = 1)
    labelcadapuntos.grid(row = 0, column = 2)
    labelultimos.grid(row = 1, column = 0)
    entradaultimos.grid(row = 1, column = 1)
    labelultimospuntos.grid(row = 1, column = 2)
    entradaconosensor.grid(row = 2, column = 0, columnspan=2)
    entradamaximosensor.grid(row =3, column = 0, columnspan=2)
                             
    

    
    
    def aceptar():
        aplicar()
        cancelar()
        actualizarcanvas()
    def aplicar():
        global escenario
        escenario.modeloatmosfera = valoratmosfera.get()
        escenario.reptierra = valortierra.get()
        escenario.colisiones = valorcolisiones.get()
        escenario.modelogravedad = valorgravedad.get()
        escenario.tiempo = [float(entradaa.get()),float(entradames.get()),float(entradad.get()),float(entradah.get()),float(entradam.get()),float(entradas.get())]
        escenario.puntos = int(float(entradapuntos.get()))
        escenario.ultimospuntos = int(float(entradaultimos.get()))
        escenario.conosensor = valorconosensor.get()
        escenario.maximosensor = valormaximosensor.get()
        guardarconfig()
    def cancelar():
        ventanaop.destroy()



def ventanaresultados():
    global objetos,barrastatus,escenario
    ventanares = Toplevel(root)
    ventanares.title(" Resultados ")
    geometria =str(root.winfo_screenwidth())+"x"+str(root.winfo_screenheight()/2)+"+0+"+ str(root.winfo_screenheight()/2 - 300) 
    ventanares.geometry(geometria)
    framearchivo = ttk.Frame(ventanares)
    frameobjetos = ttk.Frame(ventanares)
    framebotones = ttk.Frame(ventanares)
    botoncancelar = ttk.Button(framebotones, text = " Cancelar ", command = lambda:cancelar())
    botonaceptar = ttk.Button(framebotones, text = " Aceptar ", command = lambda:aceptar())
    def aceptar():
        import tkMessageBox, subprocess
        nombrearchivo = archivo.get()
        if nombrearchivo == "":
            tkMessageBox.showinfo("Nombre de archivo no encontrado","Elija un archivo",parent = ventanares)
            return
        barrastatus.set("Guardando resultados...")
        por=0
        nombrearchivo = open(nombrearchivo,"w")
        nombrearchivo.write("\n")
        nombrearchivo.write("Archivo de resultados"+"\n")
        nombrearchivo.write("Fecha inicial:    "+str(escenario.tiempo[2])+"/"+str(escenario.tiempo[1])+"/"+str(escenario.tiempo[0])+"   "+str(escenario.tiempo[3])+":"+str(escenario.tiempo[4])+":"+str(escenario.tiempo[5])+"   UTC")
        nombrearchivo.write("\n")
        nombrearchivo.write("---------------------------------------------------------------------------------------\n")
        nombrearchivo.write("---------------------------------------------------------------------------------------\n")
        for objeto in objetos:

            if isinstance(objetos[objeto],solido):
                i=0
                nombrearchivo.write(str(objeto)+ ", clase solido\n")
                nombrearchivo.write("\n")
                total=0
                for j in range(0,len(listaresultados[objeto])):                    
                    total=total+listaresultados[objeto][j].get()
                total = total-listaresultados[objeto][5].get()
               
                if total==0:
                    pass
                else:
                    
                    #Primera linea cabecera objeto
                    if listaresultados[objeto][0].get() == 1:
                        nombrearchivo.write("Tiempo (s)".ljust(16))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][1].get() == 1:
                        nombrearchivo.write("Posicion (Km)".ljust(54))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][2].get() == 1:
                        nombrearchivo.write("Velocidad (Km/s)".ljust(54))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][3].get() == 1:
                        nombrearchivo.write("Punto subsatelite (Grados)".ljust(35))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][4].get() == 1:
                        nombrearchivo.write("Orbita prevista (Km, grados)".ljust(111))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][6].get() == 1:
                        nombrearchivo.write("Aceleración (Km/s2)".ljust(54))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][7].get() == 1:
                        nombrearchivo.write("Aceleración de perturbación (Km/s2)".ljust(54))
                        nombrearchivo.write("   ")

                        
                    nombrearchivo.write("\n")
                    #Segunda linea
                    if listaresultados[objeto][0].get() == 1:
                        nombrearchivo.write("".ljust(16))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][1].get() == 1:
                        nombrearchivo.write("X".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Y".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Z".ljust(16))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][2].get() == 1:
                        nombrearchivo.write("Vx".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Vy".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Vz".ljust(16))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][3].get() == 1:
                        nombrearchivo.write("Latitud".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Longitud".ljust(16))
                        nombrearchivo.write("   ")
                        
                    if listaresultados[objeto][4].get() == 1:
                        nombrearchivo.write("Semieje mayor".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Excentricidad".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Inclinacion".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("Longitud nodo asc".ljust(16))
                        nombrearchivo.write("  ")
                        nombrearchivo.write("Argumento perigeo".ljust(16))
                        nombrearchivo.write("  ")
                        nombrearchivo.write("Anomalia verdadera".ljust(16))
                        nombrearchivo.write("")

                    if listaresultados[objeto][6].get() == 1:
                        nombrearchivo.write("ax".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("ay".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("az".ljust(16))
                        nombrearchivo.write("   ")
                    if listaresultados[objeto][7].get() == 1:
                        nombrearchivo.write("ax".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("ay".ljust(16))
                        nombrearchivo.write("   ")
                        nombrearchivo.write("az".ljust(16))
                        nombrearchivo.write("   ")

                    
                    nombrearchivo.write("\n")
                    nombrearchivo.write("___________________________________________________________________________________________\n")
                    frecuencia = listaresultados[objeto][5].get()
                    while i<len(objetos[objeto].pos):
                        if i%frecuencia == 0:

                            if listaresultados[objeto][0].get() == 1:
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].t[i,0]))
                                nombrearchivo.write("   ")
                            if listaresultados[objeto][1].get() == 1:
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].pos[i,0]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].pos[i,1]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].pos[i,2]))
                                nombrearchivo.write("   ")
                            if listaresultados[objeto][2].get() == 1:
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].vel[i,0]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].vel[i,1]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(objetos[objeto].vel[i,2]))
                                nombrearchivo.write("   ")
                            if listaresultados[objeto][3].get() == 1:
                                lat,lon = xtogeo(objetos[objeto].pos[i,:],objetos[objeto].t[i,:])
                                
                                nombrearchivo.write("{:<16f}".format(lat))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(lon))
                                nombrearchivo.write("   ")
                            if listaresultados[objeto][4].get() == 1:
                                orb = orbita()
                                orb.xv2par(objetos[objeto].pos[i,:],objetos[objeto].vel[i,:])
                                par = orb.parametros
                                nombrearchivo.write("{:<16f}".format(par[0]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(par[1]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(par[2]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(par[3]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(par[4]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16f}".format(par[5]))
                                nombrearchivo.write("   ")

                            if listaresultados[objeto][6].get() == 1:
                                fuerzas = objetos[objeto].sumafuerzas(objetos[objeto].pos[i,:],objetos[objeto].vel[i,:])
                                
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,0]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,1]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,2]))
                                nombrearchivo.write("   ")
                            if listaresultados[objeto][7].get() == 1:
                                
                                fuerzas = objetos[objeto].sumafuerzas(objetos[objeto].pos[i,:],objetos[objeto].vel[i,:])
                                fuerzasgrav = gravedad(objetos[objeto].pos[i,:],overridemodelo = "Esferico")
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,0]-fuerzasgrav[0,0]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,1]-fuerzasgrav[0,1]))
                                nombrearchivo.write("   ")
                                nombrearchivo.write("{:<16e}".format(fuerzas[0,2]-fuerzasgrav[0,2]))
                                nombrearchivo.write("   ")
                                
                            nombrearchivo.write("\n")
                        i = i+1
                nombrearchivo.write("---------------------------------------------------------------------------------------\n")
            Apor = 100/len(objetos)
            por = por + Apor
            barrastatus.set("Guardando resultados..."+str(por)+"%")










        nombrearchivo.close()
        
        barrastatus.completado()
        if abrirarchivo.get()==1:
            subprocess.Popen(archivo.get())
        cancelar()
    def cancelar():
        ventanares.destroy()

    labelarchivo = ttk.Label(framearchivo, text = " Guardar resultados en... ")
    entradaarchivo = ttk.Entry(framearchivo,width = 100)
    botonarchivo = ttk.Button(framearchivo, command = lambda:elegirarchivo(), text = "...")
    archivo = StringVar()
    abrirarchivo = IntVar()
    botonabrirarchivo = Checkbutton(framearchivo,text = "Abrir archivo al acabar",variable = abrirarchivo)
    def elegirarchivo():
        import tkFileDialog
        archivo.set(tkFileDialog.asksaveasfilename(parent = ventanares,defaultextension = ".txt",filetypes = [("Archivo de texto",".txt")] ,initialdir = "./archivos",initialfile = "Resultados.txt"))
        entradaarchivo.delete(0, END)
        entradaarchivo.insert(0,archivo.get())

    framearchivo.pack(side = TOP, fill = X)
    framebotones.pack(side=BOTTOM)
    frameobjetos.pack(side = TOP, fill = BOTH, expand = 0)    
    botoncancelar.pack(side=RIGHT)
    botonaceptar.pack(side=RIGHT)
    labelarchivo.grid(row = 0,column = 0)
    entradaarchivo.grid(row = 0,column = 1)
    botonarchivo.grid(row = 0,column = 2)
    #botonabrirarchivo.grid(row = 0, column = 3)

    class filasatelite():
        def __init__(self,nombre,marco):
            self.nombre = nombre
            self.posicion = IntVar()
            self.botonposicion = Checkbutton(marco, indicatoron=0,text = "Posicion", variable = self.posicion)
            self.tiempo = IntVar()
            self.botontiempo = Checkbutton(marco, indicatoron=0,text = "Tiempo", variable = self.tiempo)
            self.velocidad = IntVar()
            self.botonvelocidad = Checkbutton(marco, indicatoron=0,text = "Velocidad", variable = self.velocidad)
            self.subsat = IntVar()
            self.botonsubsat = Checkbutton(marco, indicatoron=0,text = "Punto subsatélite",variable = self.subsat)
            self.orbita = IntVar()
            self.botonorbita = Checkbutton(marco,indicatoron=0, text = "Orbita",variable = self.orbita)
            self.frecuencia = IntVar()
            self.frecuencia.set(1)
            self.marcofrec = ttk.Frame(marco)
            #icono1 = BitmapImage(file="graficos//iconos//prueba.xbm")
            iconosep = PhotoImage(file = "graficos/iconos/icono10x20.gif")
            #self.boton1 = ttk.Radiobutton(self.marcofrec,image = (icono1, "selected",icono1),command = lambda:cambioestado(self.boton1),variable = self.frecuencia,value = 1, style = "Demo.TButton")
            self.boton1 = Radiobutton(self.marcofrec, text = "0", variable = self.frecuencia, indicatoron = 0,value = 1)
            self.boton10 = Radiobutton(self.marcofrec,text = "1",variable = self.frecuencia, indicatoron = 0,value = 10)
            self.boton100 = Radiobutton(self.marcofrec,text = "2",variable = self.frecuencia, indicatoron = 0,value = 100)
            self.boton1000 = Radiobutton(self.marcofrec,text = "3",variable = self.frecuencia, indicatoron = 0,value = 1000)
            self.sep = ttk.Label(self.marcofrec, image = iconosep)
            def cambioestado(boton):
                if boton.instate(("selected",)):
                    boton["style"] = "Demo.Toolbutton"
                else:
                    boton["style"] = "Debom.TButton"
            self.fuerzas = IntVar()
            self.botonfuerzas = Checkbutton( marco, indicatoron = 0, text = "Aceleración", variable = self.fuerzas)
            self.pert = IntVar()
            self.botonpert = Checkbutton( marco, indicatoron=0, text = "Acc. de pert.", variable = self.pert)
            
            
        def mostrar(self):
            self.botonposicion.grid(row = 1, column = 2)
            self.botontiempo.grid(row = 1, column = 1)
            self.botonvelocidad.grid(row = 1, column = 3)
            self.botonsubsat.grid(row = 1, column = 4)
            self.botonorbita.grid(row = 1, column = 5)
            self.marcofrec.grid(row = 1, column = 0)
            self.boton1.grid(row = 1, column = 0)
            self.boton10.grid(row = 1, column = 1)
            self.boton100.grid(row = 1, column = 2)
            self.boton1000.grid(row = 1, column = 3)
            self.sep.grid(row = 1, column = 4)
            self.botonfuerzas.grid(row = 1, column = 6)
            self.botonpert.grid(row = 1, column = 7)

        def variables(self):
            lista = [self.tiempo,self.posicion,self.velocidad,self.subsat,self.orbita,self.frecuencia,self.fuerzas,self.pert]
            return lista
    class filaorbita():
        def __init__(self,nombre,marco):
            self.nombre = nombre
            self.parametros = IntVar()
            self.puntos = IntVar()
            self.botonparametros = Checkbutton(marco, indicatoron=0,text = "Parametros", variable = self.parametros)
            self.botonpuntos = Checkbutton(marco, indicatoron=0,text = "Puntos", variable = self.puntos)
        def mostrar(self):
            self.botonparametros.grid(row = 1, column = 0)
            self.botonpuntos.grid(row = 1, column = 1)
        def variables(self):
            lista = [self.parametros,self.puntos]
            return lista
    class filabase():
        def __init__(self,nombre,marco):
            self.nombre = nombre
        def mostrar(self):
            pass
        def variables(self):
            return []
            
    if len(objetos)==0:
        labelvacio = ttk.Label(frameobjetos, text = " No hay objetos ")
        labelvacio.grid(row = 0, column = 0)
    i = 0
    listaresultados = {}
    for objeto in objetos:
        marco = ttk.Frame(frameobjetos)
        labelnombre = ttk.Label(marco, text = objetos[objeto].propiedades.nombre)
        labelnombre.grid(row = 0, column = 0, columnspan = 5)
        
        if isinstance(objetos[objeto],solido):        
            muestraobjeto = filasatelite(objetos[objeto].propiedades.nombre,marco)
        elif isinstance(objetos[objeto],orbita):        
            muestraobjeto = filaorbita(objetos[objeto].propiedades.nombre,marco)        
        muestraobjeto.mostrar()
        marco.grid(row = i, column = 0)
        listaresultados.update({objetos[objeto].propiedades.nombre:muestraobjeto.variables()})
        
        i = i+1


def ventanalanzamiento():
    global objetos
    ventanalanz = Toplevel(root)
    ventanalanz.title(" Crear lanzamiento " )
    geometria = "500x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
    ventanalanz.geometry(geometria)
    framebotones = ttk.Frame(ventanalanz)
    framelanzamiento = ttk.Frame(ventanalanz)
    botonlanzar = ttk.Button(framebotones, text = " Lanzar ")

    labellanzador = ttk.Label(framelanzamiento,text = " Lanzador ")
    entradalanzador = ttk.Combobox(framelanzamiento)
    labelorbita = ttk.Label (framelanzamiento, text =  " Orbitas ")
    entradaorbita = ttk.Combobox(framelanzamiento)
    labelbase = ttk.Label(framelanzamiento, text = " Base ")
    entradabase = ttk.Combobox(framelanzamiento)
    listalanzadores = []
    listaorbitas = []
    listabases = []
    for objeto in objetos:
        if isinstance(objetos[objeto],solido):
            listalanzadores.append(objeto)
        elif isinstance(objetos[objeto],orbita):
            listaorbitas.append(objeto)
        elif isinstance(objetos[objeto],base):
            listabases.append(objeto)
    entradalanzador["values"] = listalanzadores
    entradaorbita["values"] = listaorbitas
    entradabase["values"] = listabases



    labellanzador.grid(row=0,column = 0)
    entradalanzador.grid(row = 0, column = 1)
    labelorbita.grid(row = 1, column = 0)
    entradaorbita.grid(row = 1, column = 1)
    labelbase.grid(row = 2, column = 0)
    entradabase.grid(row = 2, column = 1)
    botonlanzar.pack()
    framebotones.pack(side = BOTTOM, fill = X)
    framelanzamiento.pack(side = TOP, expand = 1, fill = BOTH) 
    
class ventanaasismaniobras():
    def __init__(self):
        pass
    def mostrar(self):
        ventanaman = Toplevel(root)
        self.ventana = ventanaman
        ventanaman.title(" Asistente de maniobras " )
        geometria = "500x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
        ventanaman.geometry(geometria)
        framebotones = ttk.Frame(ventanaman)
        framecosas = ttk.Frame(ventanaman)
        notebook = ttk.Notebook(framecosas)
        framemani = ttk.Frame(notebook)
        framemotor = ttk.Frame(notebook)
        frameopciones = ttk.Frame(notebook)
        notebook.add(framemani, text = " Maniobra ")
        #notebook.add(framemotor, text = " Motor ")
        notebook.add(frameopciones, text = " Opciones ")
        notebook.pack(side = TOP, fill = BOTH)

        self.maniobra(framemani)
        self.motor(framemotor)
        self.opciones(frameopciones)

        botonaceptar = ttk.Button(framebotones, text = " Aceptar ", command = self.aceptar)
        botoncancelar = ttk.Button(framebotones, text = " Cancelar ", command = self.cancelar)

        framecosas.pack(side = TOP, fill = BOTH)
        framebotones.pack(side=BOTTOM)           
        botoncancelar.pack(side=RIGHT)
        botonaceptar.pack(side=RIGHT)
    def maniobra(self, frame):
        global objetos
        labelorbita1 = ttk.Label(frame, text = " Orbita inicial ")
        self.entradaorbita1 = ttk.Combobox(frame)
        labelorbita2 = ttk.Label(frame, text = " Orbita final ")
        self.entradaorbita2 = ttk.Combobox(frame)
        lista = []
        for objeto in objetos:
            if isinstance(objetos[objeto], orbita):
                lista.append(objeto)
        self.entradaorbita1["values"] = lista
        self.entradaorbita2["values"] = lista

        labeltipo = ttk.Label(frame, text = " Tipo de maniobra ")
        self.entradatipo = ttk.Combobox(frame)
        self.entradatipo["values"] = ["Maniobra puntual", "Impulso puntual"]
        frametipo = ttk.Frame(frame)
        def cambiotipo(event):
            frametipo = ttk.Frame(frame)
            tipo = self.entradatipo.get()
            if tipo == "Maniobra puntual":
                manpunt(frametipo)
            elif tipo == "Minimo combustible":
                manmincomb(frametipo)
            elif tipo == "Minimo tiempo de viaje":
                manmint(frametipo)
            elif tipo == "Maniobra continua":
                mancont(frametipo)
            elif tipo == "Tiempo de viaje fijo":
                mantfijo(frametipo)
            elif tipo == "Impulso puntual":
                imppunt(frametipo)
            frametipo.grid(row = 3, column = 0, columnspan = 10)
        self.entradatipo.bind("<<ComboboxSelected>>", cambiotipo)
        def manpunt(frame):
            orb1 = objetos[self.entradaorbita1.get()]
            orb2 = objetos[self.entradaorbita2.get()]
            listaang1,listaang2 =  interseccionorbitas(orb1,orb2)
            
            if len(listaang1) == 0:
                labelnohaypuntos = ttk.Label(frame, text = "No se puede realizar la maniobra")
                labelnohaypuntos.grid(row = 1, column = 0, columnspan = 2)
            else:
                labelpunto = ttk.Label(frame, text = " Anomalia verdadera de la maniobra")
                self.entradapunto = ttk.Combobox(frame)
                lista = []
                for i in range(0,len(listaang1)):
                    listaang1[i] = round(listaang1[i],4)
                    listaang2[i] = round(listaang2[i],4)
                for angulo in listaang1:
                    lista.append(str(angulo))
                    
                self.entradapunto["values"] = lista
                self.listaang1 = listaang1
                self.listaang2 = listaang2

                labelpunto.grid(row = 1, column = 0)
                self.entradapunto.grid(row = 1, column = 1)

        def imppunt(frame):
            labelanomaliaverdadera = ttk.Label(frame,text = " Anomalia verdadera inicial")
            self.entradaanomaliaverdadera = ttk.Entry(frame)

            labelcomponentesimpulso = ttk.Label(frame, text = "Componentes del impulso")
            labelposigrado = ttk.Label(frame, text = "Posigrado")
            labelnormal = ttk.Label(frame, text = "Normal")
            labelradial = ttk.Label(frame, text = "Radial")
            self.entradaposigrado = ttk.Entry(frame)
            self.entradanormal = ttk.Entry(frame)
            self.entradaradial=ttk.Entry(frame)

            labelunidadesanomalia = ttk.Label(frame, text = "   grados")
            labelunidadesvelocidad = ttk.Label(frame, text = "   Km/s")

            labelanomaliaverdadera.grid(row=1, column =0)
            self.entradaanomaliaverdadera.grid(row = 1, column=1)
            labelunidadesanomalia.grid(row = 1, column = 2)

            labelcomponentesimpulso.grid(row = 3, column = 0)
            labelposigrado.grid(row = 2, column = 1)
            labelnormal.grid(row = 3, column = 1)
            labelradial.grid(row = 4, column = 1)
            self.entradaposigrado.grid(row = 2, column = 2)
            self.entradanormal.grid(row = 3, column = 2)
            self.entradaradial.grid(row = 4, column = 2)
            labelunidadesvelocidad.grid(row = 3, column = 3)
                
        def manmincomb(frame):
            pass
        def manmint(frame):
            pass
        def mancont(frame):
            pass
        def mantfijo(frame):
            pass           
            
        labelorbita1.grid(row = 0, column = 0, sticky = E)
        self.entradaorbita1.grid(row = 0, column = 1,sticky = W)
        labelorbita2.grid(row = 1, column = 0,sticky = E)
        self.entradaorbita2.grid(row = 1, column = 1)
        labeltipo.grid(row = 2, column = 0,sticky = W)
        self.entradatipo.grid(row = 2, column = 1, sticky = E)
        frametipo.grid(row = 3, column = 0, columnspan = 2, sticky = (N,S,E,W))
    def manpunt(self):
        global objetos
        orbita1 = objetos[self.entradaorbita1.get()]
        orbita2 = objetos[self.entradaorbita2.get()]
        ang1 = float(self.entradapunto.get())
        
        indice = self.listaang1.index(ang1)
        
        ang2 = self.listaang2[indice]

        orbita1.parametros[5]=ang1
        x1, v1 = orbita1.par2xv()
        orbita2.parametros[5]= ang2
        x2,v2 = orbita2.par2xv()

        man = maniobra()
        man.pos = x1
        man.orbitainicial = orbita1
        man.orbitafinal = orbita2
        man.Av = np.array([v2[0]-v1[0],v2[1]-v1[1],v2[2]-v1[2]])
        man.propiedades.nombre =orbita1.propiedades.nombre + " -> " + orbita2.propiedades.nombre
        man.propiedades.color = orbita1.propiedades.color
        man.posicioninicial = x1
        man.posicionfinal = x2
        man.anoini = ang1
        man.anofin = ang2
        man.velocidadinicial = v1
        man.velocidadfinal = v2
        
        self.maniobrapuntual = man
        
    def manmincomb(self):
        pass
    def manmint(self):
        pass
    def mancont(self):
        pass
    def mantfijo(self):
        pass
    def imppunt(self):
        global objetos
        orbita1 = objetos[self.entradaorbita1.get()]
        if self.entradaanomaliaverdadera.get()=="":
            punto = 0.
        else:
            punto = float(self.entradaanomaliaverdadera.get())
        if self.entradaposigrado.get()=="":
            v1 = 0.
        else:
            v1=float(self.entradaposigrado.get())
        if self.entradanormal.get()=="":
            v2 = 0.
        else:
            v2=float(self.entradanormal.get())
        if self.entradaradial.get()=="":
            v3 = 0.
        else:
            v3=float(self.entradaradial.get())        
        
        orbitatest=orbita1
        orbitatest.parametros[5]=punto
        x,v=orbitatest.par2xv()

        u1=v/np.sqrt(v[0]**2+v[1]**2+v[2]**2)
        h=orbitatest.plano()
        u2=h/np.sqrt(h[0]**2+h[1]**2+h[2]**2)
        u3=cua.productovectorial(u2,u1)

        vfinal = v + v1*u1 + v2*u2 + v3*u3
        orbitafinal=orbita()
        orbitafinal.xv2par(x,vfinal)

        man=maniobra()
        man.pos = x
        man.orbitainicial = orbitatest
        man.orbitafinal = orbitafinal
        man.Av = np.array([vfinal[0]-v[0],vfinal[1]-v[1],vfinal[2]-v[2]])
        man.propiedades.nombre = "Impulso desde " + orbitatest.propiedades.nombre
        man.propiedades.color = orbitatest.propiedades.color
        man.posicioninicial = x
        man.posicionfinal = x
        man.anoini = punto
        man.anofin = orbitafinal.parametros[5]
        man.velocidadinicial = v
        man.velocidadfinal = vfinal

        self.maniobraimpulso = man

        
    def motor(self,frame):
        labelopcionales = ttk.Label(frame, text = " Parametros opcionales ")
        labelimpulsoespecifico = ttk.Label(frame, text = " Impulso especifico ")
        
    def opciones(self,frame):
        labelcrearobjetos = ttk.Label(frame, text = "Agregar maniobras al escenario")
        self.agregar = IntVar()
        self.agregar.set(1)
        botonagregar = ttk.Checkbutton(frame, variable = self.agregar, text = "Agregar maniobras al escenario")

        botonagregar.grid(row = 0, column = 0)        

    def aceptar(self):
        global objetos,dibujarobjetos
        tipo = self.entradatipo.get()
        if tipo == "Maniobra puntual":
            self.manpunt()
            if self.agregar.get() == 1:
                objetos.update({self.maniobrapuntual.propiedades.nombre:self.maniobrapuntual})
                dibujarobjetos.append(self.maniobrapuntual.propiedades.nombre)
            informacionmaniobra(self.maniobrapuntual)
        elif tipo == "Minimo combustible":
            self.manmincomb()
        elif tipo == "Minimo tiempo de viaje":
            self.manmint()
        elif tipo == "Maniobra continua":
            self.mancont()
        elif tipo == "Tiempo de viaje fijo":
            self.mantfijo()
        elif tipo == "Impulso puntual":
            self.imppunt()
            if self.agregar.get()== 1:
                nombreorbita = nuevaorbita()
                objetos[nombreorbita]=self.maniobraimpulso.orbitafinal
                objetos[nombreorbita].propiedades.nombre=nombreorbita
                objetos[nombreorbita].orbita()

                objetos.update({self.maniobraimpulso.propiedades.nombre:self.maniobraimpulso})
                dibujarobjetos.append(self.maniobraimpulso.propiedades.nombre)
               
            informacionmaniobra(self.maniobraimpulso)


            
        self.ventana.destroy()
        actualizararbol()
        actualizarcanvas()
    def cancelar(self):
        self.ventana.destroy()

ventanamaniobras = ventanaasismaniobras()

class ventanaasisvisibilidad():
    global objetos,barrastatus,escenario
    def __init__(self):
        pass
    def mostrar(self):
        ventanavis = Toplevel(root)
        self.ventana = ventanavis
        ventanavis.title(" Asistente de visibilidad " )
        geometria = "500x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
        ventanavis.geometry(geometria)
        framebotones = ttk.Frame(ventanavis)
        framecosas = ttk.Frame(ventanavis)
        
        botonaceptar = ttk.Button(framebotones, text = " Aceptar ", command = self.aceptar)
        botoncancelar = ttk.Button(framebotones, text = " Cancelar ", command = self.cancelar)
        self.framevis(framecosas)
        
        framecosas.pack(side = TOP, fill = BOTH)
        framebotones.pack(side=BOTTOM)           
        botoncancelar.pack(side=RIGHT)
        botonaceptar.pack(side=RIGHT)
    def framevis(self,frame):
        labelobjeto1 = ttk.Label(frame, text = " Objeto 1 ")
        self.obj1 = ttk.Combobox(frame)
        labelobjeto2 = ttk.Label(frame, text = " Objeto 2 ")
        self.obj2 = ttk.Combobox(frame)
        self.entradaarchivo = ttk.Entry(frame)
        iconoarchivo = PhotoImage(file = "graficos/iconos/icono10x20.gif")
        botonarchivo = ttk.Button(frame, image = iconoarchivo, command = lambda:self.elegirarchivo())
        labelarchivo = ttk.Label(frame, text = " Archivo ")
        self.resumen = IntVar()
        self.resumen.set(1)
        self.botonresumen = ttk.Checkbutton(frame, variable = self.resumen, text =(" Resumen "))
        lista = []
        for objeto in objetos:
            if isinstance(objetos[objeto],solido):
                lista.append(objeto)
        for objeto in objetos:
            if isinstance(objetos[objeto],base):
                lista.append(objeto)
        for objeto in objetos:
            if isinstance(objetos[objeto],sensor):
                lista.append(objeto)
        self.obj1["values"] = lista
        lista.append("Sol")
        self.obj2["values"] = lista
        
        labelobjeto1.grid(row = 5, column = 0)
        self.obj1.grid(row = 5, column = 1)
        labelobjeto2.grid(row = 6, column = 0)
        self.obj2.grid(row = 6, column = 1)
        self.entradaarchivo.grid(row = 0, column = 1, columnspan = 2, sticky = (N,S,E,W))
        botonarchivo.grid(row = 0, column = 2)
        labelarchivo.grid(row = 0, column = 0)
        labelsep = ttk.Label(frame, text = "     ").grid(row = 0 , column = 3)
        self.botonresumen.grid(row = 0, column = 4)
    def visibilidad(self):
        self.archivo.write(" Archivo de visibilidad entre "+ self.obj1.get() + " y " + self.obj2.get())
        self.archivo.write("\n")
        self.archivo.write("Fecha inicial:    "+str(escenario.tiempo[2])+"/"+str(escenario.tiempo[1])+"/"+str(escenario.tiempo[0])+"   "+str(escenario.tiempo[3])+":"+str(escenario.tiempo[4])+":"+str(escenario.tiempo[5])+"   UTC")
        self.archivo.write("\n")
        self.archivo.write(" Tiempo (s)".ljust(16))
        self.archivo.write("   ")
        self.archivo.write((" Posicion de "+ self.obj1.get()+ " (Km)").ljust(54))
        self.archivo.write("   ")
        self.archivo.write((" Posicion de "+ self.obj2.get()+ " (Km)").ljust(54))
        self.archivo.write("   ")
        self.archivo.write(" Visibilidad ".ljust(16))
        self.archivo.write("\n")
        self.archivo.write("_____________________________________________ \n")
        obj1 = objetos[self.obj1.get()]
        if self.obj2.get() == "Sol":
            obj2 = "Sol"
        else:
            obj2 = objetos[self.obj2.get()]
        t = 0.
        tmax = 86400.
        if isinstance(obj1,solido) and isinstance(obj2,solido):
            tmax = min(obj1.t[-1,0],obj2.t[-1,0])
        elif isinstance(obj1,solido):
            tmax = obj1.t[-1,0]
        elif isinstance(obj2,solido):
            tmax = obj2.t[-1,0]

        while t < tmax-1:
            if t%(tmax/100)==0:
                self.estado.set(" Calculando, puede llevar tiempo   "+ str(t/(tmax/100))+ "%")
            pos1 = self.pos(obj1,t)
            pos2 = self.pos(obj2,t)            
            vis = visibilidad(pos1,pos2)
            
            if isinstance(obj2,sensor):
                vectors = obj2.calcvector(pos2)
                vectorv = pos1-pos2
                mod = np.sqrt(vectorv[0]**2+vectorv[1]**2+vectorv[2]**2)
                vectorv = vectorv/mod
                angv = np.arccos(vectors[0]*vectorv[0]+vectors[1]*vectorv[1]+vectors[2]*vectorv[2])
                angv = angv*180/np.pi
                if angv> obj2.semiangulo:
                    vis = False
            if isinstance(obj1,sensor):
                vectors = obj1.calcvector(pos1)
                vectorv = pos2-pos1
                mod = np.sqrt(vectorv[0]**2+vectorv[1]**2+vectorv[2]**2)
                vectorv = vectorv/mod
                angv = np.arccos(vectors[0]*vectorv[0]+vectors[1]*vectorv[1]+vectors[2]*vectorv[2])
                angv = angv*180/np.pi
                if angv> obj1.semiangulo:
                    vis = False
            self.archivo.write("{:<16f}".format(t))
            self.archivo.write("   ")
            
            self.archivo.write("{:<16f}".format(pos1[0]))
            self.archivo.write("   ")
            self.archivo.write("{:<16f}".format(pos1[1]))
            self.archivo.write("   ")
            self.archivo.write("{:<16f}".format(pos1[2]))
            self.archivo.write("   ")
            
            self.archivo.write("{:<16f}".format(pos2[0]))
            self.archivo.write("   ")
            self.archivo.write("{:<16f}".format(pos2[1]))
            self.archivo.write("   ")
            self.archivo.write("{:<16f}".format(pos2[2]))
            self.archivo.write("   ")
            if vis :
                self.archivo.write("  Si  ".ljust(16))
            else:
                self.archivo.write("  No  ".ljust(16))
            self.archivo.write("\n")
            t = t+1.
    def visibilidadresumen(self):
        self.archivo.write(" Archivo de visibilidad entre "+ self.obj1.get() + " y " + self.obj2.get())
        self.archivo.write("\n")
        self.archivo.write("Fecha inicial:    "+str(escenario.tiempo[2])+"/"+str(escenario.tiempo[1])+"/"+str(escenario.tiempo[0])+"   "+str(escenario.tiempo[3])+":"+str(escenario.tiempo[4])+":"+str(escenario.tiempo[5])+"   UTC")
        self.archivo.write("\n")
        self.archivo.write(" Entrada ".ljust(16))
        self.archivo.write("   ")
        self.archivo.write(" Salida ".ljust(16))
        self.archivo.write("   ")
        self.archivo.write(" Duración (s) ".ljust(16))
        self.archivo.write("\n")
        self.archivo.write("_____________________________________________ \n")
        obj1 = objetos[self.obj1.get()]
        if self.obj2.get() == "Sol":
            obj2 = "Sol"
        else:
            obj2 = objetos[self.obj2.get()]
        t = 0.
        tmax = 86400.
        if isinstance(obj1,solido) and isinstance(obj2,solido):
            tmax = min(obj1.t[-1,0],obj2.t[-1,0])
        elif isinstance(obj1,solido):
            tmax = obj1.t[-1,0]
        elif isinstance(obj2,solido):
            tmax = obj2.t[-1,0]
        entrada = 0.
        salida = 0.
        vis = False
        visant = False
        while t < tmax-1:
            if t%(tmax/100)==0:
                self.estado.set(" Calculando, puede llevar tiempo   "+ str(t/(tmax/100))+ "%")
                
            pos1 = self.pos(obj1,t)
            pos2 = self.pos(obj2,t)            
            vis = visibilidad(pos1,pos2)
            if isinstance(obj2,sensor):
                vectors = obj2.calcvector(pos2)
                vectorv = pos1-pos2
                mod = np.sqrt(vectorv[0]**2+vectorv[1]**2+vectorv[2]**2)
                vectorv = vectorv/mod
                angv = np.arccos(vectors[0]*vectorv[0]+vectors[1]*vectorv[1]+vectors[2]*vectorv[2])
                angv = angv*180/np.pi
                if angv> obj2.semiangulo:
                    vis = False
            if isinstance(obj1,sensor):
                vectors = obj1.calcvector(pos1)
                vectorv = pos2-pos1
                mod = np.sqrt(vectorv[0]**2+vectorv[1]**2+vectorv[2]**2)
                vectorv = vectorv/mod
                angv = np.arccos(vectors[0]*vectorv[0]+vectors[1]*vectorv[1]+vectors[2]*vectorv[2])
                angv = angv*180/np.pi
                if angv> obj1.semiangulo:
                    vis = False
                
            
            if vis and not visant:
                entrada = t
            elif not vis and visant:
                salida = t
                self.archivo.write("{:<16f}".format(entrada))
                self.archivo.write("   ")
                self.archivo.write("{:<16f}".format(salida))
                self.archivo.write("   ")
                self.archivo.write("{:<16f}".format(salida-entrada))
                self.archivo.write("\n")
            t = t+1.
            visant = vis        
    def elegirarchivo(self):                                      
        import tkFileDialog
        archivo=tkFileDialog.asksaveasfilename(parent = self.ventana,defaultextension = ".txt",filetypes = [("Archivo de texto",".txt")] ,initialdir = "./archivos",initialfile = "Visibilidad.txt")
        self.entradaarchivo.delete(0, END)
        self.entradaarchivo.insert(0,archivo)
    def pos(self,objeto,tiempo):
        if objeto == "Sol":
            pos = posicionsol(juliana(escenario.tiempo)+ tiempo/86400.)
            return pos
        elif isinstance(objeto, solido):
            i = 0
            tinf = 0.
            while i < len(objeto.t):
                tsup = objeto.t[i,0]
                if tsup>tiempo and tinf <=tiempo:
                    break
                i = i+1
                tinf = tsup            
            posinf = objeto.pos[i,:]
            possup = objeto.pos[i+1,:]
            par = tiempo-tinf/(tsup-tinf)
            pos = posinf + par*(possup-posinf)            
            return pos
        elif isinstance(objeto,base):
            pos = geotox(objeto.lat,objeto.lon,tiempo)
            return pos
        elif isinstance(objeto,sensor):
            pos = self.pos(objetos[objeto.objeto],tiempo)
            return pos
    def aceptar(self):
        self.estado = barrastatus
        self.estado.set(" Calculando, puede llevar tiempo ")
        self.archivo = self.entradaarchivo.get()
        self.archivo = open(self.archivo, "w")
        if self.resumen.get()==1:
            self.visibilidadresumen()
        else:
            self.visibilidad()
        self.archivo.close()
        self.estado.completado()
        self.ventana.destroy()
    def cancelar(self):
        self.ventana.destroy()
ventanavisibilidad = ventanaasisvisibilidad()
   
arbolobjetos = ttk.Treeview(areaarbol)
def actualizararbol():
    global objetoactual
    for i in arbolobjetos.get_children():
        arbolobjetos.delete(i)
    arbolobjetos.insert("",0,"objetos", text = "Objetos", open = True)
    arbolobjetos.insert("",1,"orbitas", text = "Orbitas", open = True)
    arbolobjetos.insert("",2,"bases", text = "Bases", open = True)
    arbolobjetos.insert("",3,"sensores", text = "Sensores", open = True)
    arbolobjetos.insert("",4,"maniobras", text = "Maniobras", open = True)

    for nombre in objetos:
        texto = objetos[nombre].propiedades.nombre

        if isinstance(objetos[nombre],solido):
            
            if nombre == objetoactual:
                arbolobjetos.insert("objetos", "end",str(nombre), text =">"+texto)
            else:            
                arbolobjetos.insert("objetos", "end",str(nombre), text =texto)


        if isinstance(objetos[nombre],orbita):
            
            if nombre == objetoactual:
                arbolobjetos.insert("orbitas", "end",str(nombre), text =">"+texto)
            else:            
                arbolobjetos.insert("orbitas", "end",str(nombre), text =texto)


        if isinstance(objetos[nombre],base):
            
            if nombre == objetoactual:
                arbolobjetos.insert("bases", "end",str(nombre), text =">"+texto)
            else:            
                arbolobjetos.insert("bases", "end",str(nombre), text =texto)

        if isinstance(objetos[nombre],sensor):
            
            if nombre == objetoactual:
                arbolobjetos.insert("sensores", "end",str(nombre), text =">"+texto)
            else:            
                arbolobjetos.insert("sensores", "end",str(nombre), text =texto)

        if isinstance(objetos[nombre],maniobra):
            
            if nombre == objetoactual:
                arbolobjetos.insert("maniobras", "end",str(nombre), text =">"+texto)
            else:            
                arbolobjetos.insert("maniobras", "end",str(nombre), text =texto)



def cambiarobjetoactual(event):
    global objetoactual,arbolobjetos
    item = arbolobjetos.identify("row",event.x,event.y)
    objetoactual = arbolobjetos.item(item,"text")
    objetoactual = objetoactual.lstrip(">")
    actualizararbol()
    



def buscarnombreobjeto(nombre):
    if objetos.has_key(nombre):
        return True
    else:
        return False

def nuevoobjeto():
    global objetoactual,objetos,dibujarobjetos
    objeto = solido()
    i=1
    objeto.setnombre("Objeto "+str(i))
    
    while buscarnombreobjeto(objeto.propiedades.nombre):
        i=i+1
        objeto.setnombre("Objeto "+str(i))
    objetos.update({objeto.propiedades.nombre:objeto})
    dibujarobjetos.append(objeto.propiedades.nombre)
    objetoactual=objeto.propiedades.nombre
    return objeto.propiedades.nombre

def botonnuevosolido():
    nombre = nuevoobjeto()    
    actualizararbol()
    cancelado = ventanapropiedadessolido(nombre,"Satelite")
    
    if cancelado:
        del objetos[objetoactual]
        dibujarobjetos.remove(objetoactual)   
    actualizararbol()



def nuevosensor():
    import orbita as orb
    global objetoactual,objetos,dibujarobjetos
    objeto = orb.sensor()
    i=1
    objeto.setnombre("Sensor "+str(i))
    
    while buscarnombreobjeto(objeto.propiedades.nombre):
        i=i+1
        objeto.setnombre("Sensor "+str(i))
    objetos.update({objeto.propiedades.nombre:objeto})
    dibujarobjetos.append(objeto.propiedades.nombre)
    objetoactual=objeto.propiedades.nombre
    
    return objeto.propiedades.nombre

def botonnuevosensor():
    nombre = nuevosensor()
    actualizararbol()
    ventanapropiedadessolido(nombre,"Sensor")        
    actualizararbol()
def nuevaorbita():
    import orbita as orb
    global objetoactual,objetos,dibujarobjetos
    orbita = orb.orbita()
    i=1
    orbita.setnombre("Orbita "+str(i))
    
    while buscarnombreobjeto(orbita.propiedades.nombre):
        i=i+1
        orbita.setnombre("Orbita "+str(i))
    objetos.update({orbita.propiedades.nombre:orbita})
    dibujarobjetos.append(orbita.propiedades.nombre)
    objetoactual=orbita.propiedades.nombre
    return orbita.propiedades.nombre
def botonnuevaorbita():
    nombre = nuevaorbita()
    ventanapropiedadessolido(nombre,"Orbita")        
    actualizararbol()
def nuevabase():
    import orbita as orb
    global objetoactual,objetos,dibujarobjetos
    base = orb.base()
    i=1
    base.setnombre("Base "+str(i))
    
    while buscarnombreobjeto(base.propiedades.nombre):
        i=i+1
        base.setnombre("Base "+str(i))
    objetos.update({base.propiedades.nombre:base})
    dibujarobjetos.append(base.propiedades.nombre)
    objetoactual=base.propiedades.nombre
    return base.propiedades.nombre

def botonnuevabase():
    nombre = nuevabase()
    ventanapropiedadessolido(nombre,"Base")        
    actualizararbol()

    

#################Ventana de propiedades del solido
def ventanapropiedadessolido(nombreobjeto,tipo): #Ventana que se abre para cambiar las propiedades de un objeto
    global objetos,objetoactual
    from tkColorChooser import askcolor
    
    objetotemp = []
    objetotemp.append(objetos[nombreobjeto])
    ventanaprop = Toplevel(root)
    ventanaprop.title(" Propiedades de " + nombreobjeto)
    geometria = "350x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
    ventanaprop.geometry(geometria)
    framepropiedades= ttk.Frame(ventanaprop)
    botonaplicar = ttk.Button(ventanaprop, text = " Aplicar ", command = lambda: aplicar())
    botoncancelar = ttk.Button(ventanaprop, text = " Cancelar ", command = lambda:cancelar())
    botonaceptar = ttk.Button(ventanaprop, text = " Aceptar ", command = lambda:aceptar())
    def cancelar():
        ventanaprop.destroy()
        return False
    def aplicar():
        
        
        if tiposolido[0] == "Satelite":
            objetotemp[0].propiedades.nombre = entradanombre.get()
            pos0 = framesolido.winfo_children()[1].get()
            vel0 = framesolido.winfo_children()[3].get()
            pos0 = pos0.strip("[]()")
            pos0 = pos0.split()
            vel0 = vel0.strip("[]()")
            vel0 = vel0.split()
            
            p0 = []
            v0 = []
            for i in range(0,3):
                p0.append(float(pos0[i]))
                v0.append(float(vel0[i]))
            
            objetotemp[0].setinicio(p0,v0)
            objetotemp[0].propiedades.balistico=float(framesolido.winfo_children()[5].get())
            objetotemp[0].int = framesolido.winfo_children()[7].get()
            objetotemp[0].At = float(framesolido.winfo_children()[9].get())
            
        elif tiposolido[0] == "Orbita":
            objetotemp[0].propiedades.nombre = entradanombre.get()
            a = float(framesolido.winfo_children()[1].get())
            e = float(framesolido.winfo_children()[3].get())
            i = float(framesolido.winfo_children()[5].get())
            ascrec = float(framesolido.winfo_children()[7].get())
            argper = float(framesolido.winfo_children()[9].get())

            objetotemp[0].setorbita(a,e,i,ascrec,argper,0.)
            objetotemp[0].orbita()

        elif tiposolido[0] == "Base":
            objetotemp[0].propiedades.nombre = entradanombre.get()
            lat = float(framesolido.winfo_children()[1].get())
            lon = float(framesolido.winfo_children()[3].get())
            objetotemp[0].pos[-1,:] = np.array([[geotox(lat,lon)]])
            objetotemp[0].lat = lat
            objetotemp[0].lon = lon
        elif tiposolido[0] == "Sensor":
            objetotemp[0].propiedades.nombre = entradanombre.get()
            objetotemp[0].objeto = framesolido.winfo_children()[1].get()
            objetotemp[0].actitud = framesolido.winfo_children()[3].get()
            objetotemp[0].semiangulo = float(framesolido.winfo_children()[5].get())
            objetotemp[0].dmax = float(framesolido.winfo_children()[7].get())
            vec = framesolido.winfo_children()[11].get()            
            vec = vec.strip("[]()")
            vec = vec.split()           
            vector = []
            for i in range(0,3):
                vector.append(float(vec[i]))
            modulo = np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
            for i in range(0,3):
                vector[i] = vector[i]/modulo
            objetotemp[0].vector = np.array(vector)
            
        
        objetos[nombreobjeto] = objetotemp[0]
        cambiarnombreobjeto(nombreobjeto,objetotemp[0].propiedades.nombre)
        
        objetoactual=objetotemp[0].propiedades.nombre
        actualizararbol()
        actualizarcanvas()
    def aceptar():
        global escenario
        
        aplicar()
        ventanaprop.destroy()
        return True
    labelnombre = ttk.Label(framepropiedades, text = " Nombre ")
    entradanombre = ttk.Entry(framepropiedades)
    entradanombre.insert(0,objetotemp[0].propiedades.nombre)    
    labeltiposolido = ttk.Label(framepropiedades, text= " Tipo de objeto ")
    tiposolido = [""]
    tiposolido[0] = tipo
    
    selectiposolido= ttk.Combobox(framepropiedades,textvariable=tiposolido)
    selectiposolido["values"] = ("Satelite","Orbita","Base","Sensor")
    if selectiposolido.get() == tiposolido[0]:
        pass
    else:
        selectiposolido.insert(0,tiposolido[0])
    framesolido = ttk.Frame(framepropiedades)
    framesolido.grid(row = 3, column = 0, columnspan = 3)

    labelcolor = ttk.Label(framepropiedades, text = " Color ")
    botoncolor = ttk.Button(framepropiedades, text = " Color ", command = lambda:botcolor())
    separador = ttk.Separator(framepropiedades)

    def botcolor():
        color = askcolor(parent = ventanaprop)
        objetotemp[0].propiedades.color = color[1]
    
    def cambiotiposolido(event):
        
        for child in framesolido.winfo_children():
            child.destroy()
        tiposolido[0] = selectiposolido.get()

        
        
                
        if tiposolido[0]=="Satelite":
            if isinstance(objetotemp[0],solido):
                pass
            else:
                objetotemp[0] = solido()
            satelite()
        elif tiposolido[0]=="Orbita":
            if isinstance(objetotemp[0],orbita):
                pass
            else:
                objetotemp[0] = orbita()
            frameorbita()
        elif tiposolido[0]=="Base":
            if isinstance(objetotemp[0],base):
                pass
            else:
                objetotemp[0] = base()
            framebase()
        elif tiposolido[0]=="Sensor":
            if isinstance(objetotemp[0],sensor):
                pass
            else:
                objetotemp[0] = sensor()
            framesensor()
        

        
    selectiposolido.bind("<<ComboboxSelected>>", cambiotiposolido)       
    
    def satelite():
         
        labelposini = ttk.Label(framesolido, text = " Posicion inicial ")
        entradaposini = ttk.Entry(framesolido)        
        entradaposini.insert(0,objetotemp[0].pos[0,:])    

        labelvelini = ttk.Label(framesolido, text = " Velocidad inicial ")
        entradavelini = ttk.Entry(framesolido)        
        entradavelini.insert(0,objetotemp[0].vel[0,:])

        labelmasa = ttk.Label(framesolido, text = " Coeficiente balístico ")
        entradamasa = ttk.Entry(framesolido)
        entradamasa.insert(0,objetotemp[0].propiedades.balistico)

        labelintegrador = ttk.Label(framesolido, text = " Integrador ")
        botonintegrador = ttk.Combobox(framesolido)
        botonintegrador["values"] = ("AB4", "RK4","PC4")
        botonintegrador.insert(0,objetotemp[0].int)

        labelAt = ttk.Label(framesolido, text = " Delta-t ")
        entradaAt = ttk.Entry(framesolido)
        entradaAt.insert(0,objetotemp[0].At)
        

        labelformatopos = ttk.Label(framesolido, text = "       [x   y   z]  Km  ")
        labelformatovel = ttk.Label(framesolido, text = "      [Vx  Vy  Vz] Km/s ")
        labelformatomasa = ttk.Label(framesolido, text = "   Kg   ")
        labelformatoAt = ttk.Label(framesolido, text = " Segundos ")
        iconodefinirorbita = PhotoImage(file="graficos/iconos/icono10x40.gif")
        botondefinirorbita = ttk.Button(framesolido, command = lambda:ventanaorbita.mostrar(), image = iconodefinirorbita)
        

            
        labelposini.grid(row=0, column = 0, sticky = (N,S,E,W))
        entradaposini.grid(row=0, column = 1, sticky = (N,S,E,W))
        labelvelini.grid(row = 1, column = 0, sticky = (N,S,E,W))
        entradavelini.grid(row = 1, column = 1, sticky = (N,S,E,W))
        labelmasa.grid(row = 2, column = 0, sticky=(N,S,E,W))
        entradamasa.grid(row = 2, column = 1, sticky=(N,S,E,W))
        labelintegrador.grid(row = 3,column = 0, sticky=(N,S,E,W))
        botonintegrador.grid(row = 3, column = 1, columnspan = 1, sticky = (N,S,E,W))
        labelAt.grid(row = 4, column = 0, sticky = (N,S,E,W))
        entradaAt.grid(row = 4, column = 1, sticky = (N,S,E,W))

        
        botondefinirorbita.grid(row = 0, rowspan = 2, column = 2, sticky = W)
        labelformatopos.grid(row = 0, column = 2, sticky = (N,S,E,W))
        labelformatovel.grid(row = 1, column = 2, sticky = (N,S,E,W))
        #labelformatomasa.grid(row = 2, column = 2, sticky=(N,S,E,W))
        labelformatoAt.grid(row = 4, column = 2, sticky = (N,S,E,W))

        ventanaorbita = ventanadefinirorbita(entradaposini, entradavelini)
        
    class ventanadefinirorbita():
        def __init__(self,entradapos, entradavel):
            self.pos = entradapos
            self.vel = entradavel
        def mostrar(self):
            self.ventana = Toplevel(root)
            self.ventana.title(" Definir orbita ")
            geometria = "300x300"+"+" + str(root.winfo_screenwidth()/2 - 120) + "+" + str(root.winfo_screenheight()/2 - 150)
            self.ventana.geometry(geometria)
            framebotones = ttk.Frame(self.ventana)
            framecosas = ttk.Frame(self.ventana)
            botonaceptar = ttk.Button(framebotones, text = " Aceptar ", command = lambda:self.aceptar())

             

            framebotones.pack(side = BOTTOM, fill = X)
            framecosas.pack(side=TOP, fill=BOTH, expand=1)
            botonaceptar.pack()

            labela = ttk.Label(framecosas, text = " Semieje mayor  ")
            labele = ttk.Label(framecosas, text = " Excentricidad  ")
            labeli = ttk.Label(framecosas, text = " Inclinacion  ")
            labelnodasc = ttk.Label(framecosas, text = " Longitud nodo ascendente  ")
            labelargper = ttk.Label(framecosas, text = " Argumento perigeo  ")
            labelanover = ttk.Label(framecosas, text = " Anomalia verdadera  ")

            self.a = ttk.Entry(framecosas, justify = CENTER)
            self.e = ttk.Entry(framecosas, justify = CENTER)
            self.i = ttk.Entry(framecosas, justify = CENTER)
            self.nodasc = ttk.Entry(framecosas, justify = CENTER)
            self.argper = ttk.Entry(framecosas, justify = CENTER)
            self.anover = ttk.Entry(framecosas, justify = CENTER)
            self.a.insert(0, 7000.)
            self.e.insert(0, 0.)
            self.i.insert(0, 0.)
            self.nodasc.insert(0, 0.)
            self.argper.insert(0, 0.)
            self.anover.insert(0, 0.)

            global objetos
            self.selectorbita = ttk.Combobox(framecosas)
            self.selectorbita.bind("<<ComboboxSelected>>", self.orbitayadef)
            lista = ["..."]
            for objeto in objetos:
                if isinstance(objetos[objeto], orbita):
                    lista.append(objetos[objeto].propiedades.nombre)
            self.selectorbita["values"]= lista

            self.selectorbita.grid(row = 0, column = 0, columnspan = 2)
            labela.grid(row = 1, column = 0, sticky = E)
            labele.grid(row = 2, column = 0, sticky = E)
            labeli.grid(row = 3, column = 0, sticky = E)
            labelnodasc.grid(row = 4, column = 0, sticky = E)
            labelargper.grid(row = 5, column = 0, sticky = E)
            labelanover.grid(row = 6, column = 0, sticky = E)
            self.a.grid(row = 1, column = 1, sticky = W)
            self.e.grid(row = 2, column = 1, sticky = W)
            self.i.grid(row = 3, column = 1, sticky = W)
            self.nodasc.grid(row = 4, column = 1, sticky = W)
            self.argper.grid(row = 5, column = 1, sticky = W)
            self.anover.grid(row = 6, column = 1, sticky = W)

        def orbitayadef(self, event):
            global objetos

            self.a.delete(0, END)
            self.e.delete(0, END)
            self.i.delete(0, END)
            self.nodasc.delete(0, END)
            self.argper.delete(0, END)
            self.anover.delete(0, END)

            if self.selectorbita.get() == "...":
                self.a.insert(0, 6378.)
                self.e.insert(0, 0.)
                self.i.insert(0, 0.)
                self.nodasc.insert(0, 0.)
                self.argper.insert(0, 0.)
                self.anover.insert(0, 0.)
            else:
                orb = self.selectorbita.get()
                par = objetos[orb].parametros
                self.a.insert(0, par[0])
                self.e.insert(0, par[1])
                self.i.insert(0, par[2])
                self.nodasc.insert(0, par[3])
                self.argper.insert(0, par[4])
                self.anover.insert(0, 0.)
                

        def aceptar(self):
            orb = orbita()
            a = float(self.a.get())
            e = float(self.e.get())
            i = float(self.i.get())
            nodasc = float(self.nodasc.get())
            argper = float(self.argper.get())
            anover = float(self.anover.get())

            orb.setorbita(a,e,i,nodasc,argper,anover)
            x,v = orb.par2xv()
            x = "["+str(x[0])+ " " + str(x[1])+ " " +str(x[2])+ "]"
            v = "["+str(v[0])+ " " + str(v[1])+ " " +str(v[2])+ "]"
            self.pos.delete(0, END)
            self.vel.delete(0,END)
            self.pos.insert(0,x)
            self.vel.insert(0,v)

            self.ventana.destroy()
        
        
    def frameorbita():
        
        
        labelsemieje = ttk.Label(framesolido, text = " Semieje mayor ")
        entradasemieje = ttk.Entry(framesolido)
        entradasemieje.insert(0,objetotemp[0].parametros[0])

        labelexcen = ttk.Label(framesolido, text = " Excentricidad ")
        entradaexcen = ttk.Entry(framesolido)
        entradaexcen.insert(0,objetotemp[0].parametros[1])

        labelincli = ttk.Label(framesolido, text = " Inclinacion ")
        entradaincli = ttk.Entry(framesolido)
        entradaincli.insert(0,objetotemp[0].parametros[2])

        labelascrec = ttk.Label(framesolido, text = " Ascension recta del nodo ascendente ")
        entradaascrec = ttk.Entry(framesolido)
        entradaascrec.insert(0,objetotemp[0].parametros[3])

        labelargper = ttk.Label(framesolido, text = " Argumento del perigeo ")
        entradaargper = ttk.Entry(framesolido)
        entradaargper.insert(0,objetotemp[0].parametros[5])

        labelsemieje.grid(row=0, column = 0, sticky = (N,S,E,W))
        entradasemieje.grid(row=0, column = 1, sticky = (N,S,E,W))
        labelexcen.grid(row=1, column = 0, sticky = (N,S,E,W))
        entradaexcen.grid(row=1, column = 1, sticky = (N,S,E,W))
        labelincli.grid(row=2, column = 0, sticky = (N,S,E,W))
        entradaincli.grid(row=2, column = 1, sticky = (N,S,E,W))
        labelascrec.grid(row=3, column = 0, sticky = (N,S,E,W))
        entradaascrec.grid(row=3, column = 1, sticky = (N,S,E,W))
        labelargper.grid(row=4, column = 0, sticky = (N,S,E,W))
        entradaargper.grid(row=4, column = 1, sticky = (N,S,E,W))
        
    def framebase():


        lat, lon = xtogeo(objetotemp[0].pos[-1,:],0.)
        
        labellatitud = ttk.Label(framesolido, text = " Latitud ")
        entradalatitud = ttk.Entry(framesolido)
        entradalatitud.insert(0,lat)

        labellongitud = ttk.Label(framesolido, text = " Longitud ")
        entradalongitud = ttk.Entry(framesolido)
        entradalongitud.insert(0,lon)

        botonposdef = ttk.Combobox(framesolido)


        labellatitud.grid(row = 0, column = 0, sticky = (N,S,E,W))
        entradalatitud.grid(row = 0, column = 1, sticky = (N,S,E,W))
        labellongitud.grid(row = 1, column = 0, sticky = (N,S,E,W))
        entradalongitud.grid(row = 1, column = 1, sticky = (N,S,E,W))
        botonposdef.grid(row = 0, column = 2,rowspan = 2, sticky = (N,S))

        bases = [{"Cabo canaveral":(28.50,-80.57),"Kourou":(5.23,-52.77),"Plesetsk":(62.90,40.60),
                  "Baikonur":(46.00,63.30),"Xichang":(28.25,102.03),
                  "Svalbard":(78.23,15.38),"Trollsat":(-72.01,2.54),
                  }]

        botonposdef["values"] = tuple(bases[0].keys())

        def cambiobase(event):
            base = botonposdef.get()
            posicion = bases[0][base]
            objetotemp[0].pos[-1,:] = geotox(posicion[0],posicion[1])
            objetotemp[0].propiedades.nombre = base
            entradanombre.delete(0,END)
            entradanombre.insert(0,objetotemp[0].propiedades.nombre)
            cambiotiposolido(None)

        botonposdef.bind("<<ComboboxSelected>>", cambiobase)
        
    def framesensor():

        labelobjeto = ttk.Label(framesolido,text = " Añadir sensor a... ")
        entradaobjeto = ttk.Combobox(framesolido)
        lista = []
        for objeto in objetos:
            if isinstance(objetos[objeto],solido):
                lista.append(objetos[objeto].propiedades.nombre)
            if isinstance(objetos[objeto],base):
                #lista.append(objetos[objeto].propiedades.nombre)
                pass
        entradaobjeto["values"] = lista
        entradaobjeto.insert(0,objetotemp[0].objeto)

        labelapuntamiento = ttk.Label(framesolido, text = " Apuntamiento ")
        entradaapuntamiento = ttk.Combobox(framesolido)
        entradaapuntamiento["values"] = ["Nadir","Cenit","Direccion fija"]
        entradaapuntamiento.insert(0,objetotemp[0].actitud)

        labelsemiangulo = ttk.Label(framesolido, text = " Semiapertura ")
        entradasemiangulo = ttk.Entry(framesolido)
        entradasemiangulo.insert(0,objetotemp[0].semiangulo)

        labeldistanciamax = ttk.Label(framesolido, text = " Alcance maximo ")
        entradadistanciamax = ttk.Entry(framesolido)
        entradadistanciamax.insert(0,objetotemp[0].dmax)

        labelunidadessemiangulo = ttk.Label(framesolido, text = " Grados ")
        labelunidadesdistanciamax = ttk.Label(framesolido, text = " Kilometros ")

        labelvector = ttk.Label(framesolido, text = " Vector apunt.")
        entradavector = ttk.Entry(framesolido)
        entradavector.insert(0,objetotemp[0].vector)
        labelconsejovector = ttk.Label(framesolido, text = "(Solo para direccion fija)")

        labelobjeto.grid(row = 0, column = 0, sticky = (N,S,E,W))
        entradaobjeto.grid(row = 0, column = 1, sticky = (N,S,E,W))
        labelapuntamiento.grid(row = 1, column = 0, sticky = (N,S,E,W))
        entradaapuntamiento.grid(row = 1, column = 1, sticky = (N,S,E,W))
        labelsemiangulo.grid(row = 2, column = 0, sticky = (N,S,E,W))
        entradasemiangulo.grid(row = 2, column = 1, sticky = (N,S,E,W))
        labelunidadessemiangulo.grid(row = 2, column = 2, sticky = (N,S,E,W))
        labeldistanciamax.grid(row = 3, column = 0, sticky = (N,S,E,W))
        entradadistanciamax.grid(row = 3, column = 1, sticky = (N,S,E,W))
        labelunidadesdistanciamax.grid(row = 3, column = 2, sticky = (N,S,E,W))
        labelvector.grid(row = 4, column = 0, sticky = (N,S,E,W))
        entradavector.grid(row = 4, column = 1, sticky = (N,S,E,W))
        labelconsejovector.grid(row = 4, column = 2, sticky = (N,S,E,W))
                                            


    framepropiedades.pack(side=TOP, fill=BOTH, expand=1)
    botoncancelar.pack(side=RIGHT)
    botonaplicar.pack(side=RIGHT)
    botonaceptar.pack(side=RIGHT)
    
    labelnombre.grid(row = 0, column = 0, sticky = (N,S,E,W))
    entradanombre.grid(row = 0, column = 1, sticky = (N,S,E,W))
    labeltiposolido.grid(row=1, column = 0, sticky = (N,S,E,W))
    selectiposolido.grid(row=1, column = 1, sticky = (N,S,E,W))
    botoncolor.grid(row = 0, column = 2, sticky = (N,S,E,W))
    separador.grid(row = 2, columnspan = 3, column = 0, sticky = (N,S,E,W))
    cambiotiposolido(None)
##############################################    



icononuevosatelite = PhotoImage(file="graficos/iconos/nuevosatelite.gif")
icononuevaorbita = PhotoImage(file="graficos/iconos/nuevaorbita.gif")
icononuevabase = PhotoImage(file="graficos/iconos/nuevabase.gif")
iconolanzarescenario = PhotoImage(file="graficos/iconos/lanzarescenario.gif")
iconolanzarobjeto = PhotoImage(file="graficos/iconos/lanzarobjeto.gif")
icononuevosensor = PhotoImage(file="graficos/iconos/nuevosensor.gif")
iconoplay = PhotoImage(file="graficos/iconos/play.gif")
iconopause = PhotoImage(file="graficos/iconos/pause.gif")

lanzar1 = ttk.Button(areabotones2, image = iconolanzarobjeto, command = lambda: botonlanzar(objetos[objetoactual]))
nuevoobj = ttk.Button(areabotones1, image = icononuevosatelite, command = lambda: botonnuevosolido())
nuevaorb = ttk.Button(areabotones1, image = icononuevaorbita,command = botonnuevaorbita)
nuevabas = ttk.Button(areabotones1, image = icononuevabase,command = botonnuevabase)
nuevolanz = ttk.Button(areabotones1, text = " Nuevo lanzamiento ", command = lambda:ventanalanzamiento())
nuevosens = ttk.Button(areabotones1, image = icononuevosensor, command = lambda:botonnuevosensor())
lanzartodos = ttk.Button(areabotones2, image = iconolanzarescenario, command = lambda: botonlanzartodos())
labellanzar = ttk.Label(areabotones2, text = " segundos ")
entradalanzar = ttk.Entry(areabotones2, justify = CENTER)
entradalanzar.insert(0,"10000")
botonplay = ttk.Button(areabotones2, image = iconoplay, command = lambda:handbotonplay())
botonpause = ttk.Button(areabotones2, image = iconopause, command = lambda:handbotonpause())

##############################################
class menuderechoarbol():
    global objetos, objetoactual, arbolobjetos,dibujarobjetos
    def __init__(self):
        self.menu = Menu(arbolobjetos, tearoff=0)
        self.menu.add_command(label= " Informacion ",command = self.informacion)
        
        
        
        
        self.labelmostrar = " Ocultar "
        self.menu.add_command(label = self.labelmostrar, command = self.mostrarobj)
        arbolobjetos.bind("<Button-3>", self.mostrar)
        self.menu.add_separator()
        self.menu.add_command(label =" Propiedades ", command = self.propiedades)
        self.menu.add_command(label= " Borrar ", command = self.borrar)
    def informacion(self):
        
        ventanainf= Toplevel(root)
        ventanainf.title(" Informacion de " + objetoactual)
        geometria = "350x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 150) + "+" + str(root.winfo_screenheight()/2 - 300)
        ventanainf.geometry(geometria)
        
        if isinstance(objetos[objetoactual],solido):
            labelsep  = ttk.Label(ventanainf, text = "_________________________________________")
            labelsep1 = ttk.Label(ventanainf, text = "_________________________________________")
            labelsep2 = ttk.Label(ventanainf, text = "_________________________________________")
            
            labelnombre = ttk.Label(ventanainf, text = objetoactual)
            labelposicion = ttk.Label(ventanainf, text = " Posicion ")
            labelpos = ttk.Label(ventanainf, text = str(objetos[objetoactual].pos[-1,:]))
            labelvelocidad = ttk.Label(ventanainf, text = " Velocidad ")
            labelvel = ttk.Label(ventanainf, text = str(objetos[objetoactual].vel[-1,:]))
            labelpunto = ttk.Label(ventanainf, text = " Punto subsatelite")
            labellatitud = ttk.Label(ventanainf, text = " Latitud ")
            labellongitud = ttk.Label(ventanainf, text = " Longitud ")
            lat, lon = xtogeo(objetos[objetoactual].pos[-1,:],objetos[objetoactual].t[-1,0])
            labellat = ttk.Label(ventanainf, text = str(lat))
            labellon = ttk.Label(ventanainf, text = str(lon))
            
            labelorbita = ttk.Label(ventanainf, text = " Orbita prevista ")
            labelsemieje = ttk.Label(ventanainf, text = " Semieje mayor ")
            labelexcentricidad = ttk.Label(ventanainf, text = " Excentricidad ")
            labelinclinacion = ttk.Label(ventanainf, text = " Inclinacion ")
            labelnodascendente = ttk.Label(ventanainf, text = " Longitud del nodo ascendente ")
            labelargperigeo = ttk.Label(ventanainf, text = " Argumento del perigeo ")
            labelanoverdadera = ttk.Label(ventanainf, text = " Anomalia verdadera ")
            orb = orbita()
            orb.xv2par(objetos[objetoactual].pos[-1,:],objetos[objetoactual].vel[-1,:])
            par = orb.parametros
            labelsem = ttk.Label(ventanainf, text = str(par[0]))
            labelexc = ttk.Label(ventanainf, text = str(par[1]))
            labelinc = ttk.Label(ventanainf, text = str(par[2]))
            labelnodasc = ttk.Label(ventanainf, text = str(par[3]))
            labelargper = ttk.Label(ventanainf, text = str(par[4]))
            labelanover = ttk.Label(ventanainf, text = str(par[5]))


            labelnombre.grid(row = 0, column = 0, columnspan = 3, sticky = W)
            labelsep.grid(row = 1, column = 0, columnspan = 3, sticky = W)
            labelposicion.grid(row = 2, column = 0)
            labelpos.grid(row = 2, column = 1)
            labelvelocidad.grid(row = 3, column = 0)
            labelvel.grid(row = 3, column = 1)
            labelsep1.grid(row = 9, column = 0, columnspan = 3, sticky = W)
            labelsep2.grid(row = 4, column = 0, columnspan = 3, sticky = W)
            labelpunto.grid(row = 5, column = 0, columnspan = 3, sticky = W)
            labellatitud.grid(row = 6, column = 0,sticky = E)
            labellat.grid(row = 6, column = 1, sticky = W)
            labellongitud.grid(row = 7, column = 0,  sticky = E)
            labellon.grid(row= 7, column = 1, sticky = W)
            labelorbita.grid(row = 10, column = 0, columnspan = 3, sticky = W)
            labelsemieje.grid(row = 11, column = 0, sticky = E)
            labelexcentricidad.grid(row = 12, column = 0, sticky = E)
            labelinclinacion.grid(row = 13, column = 0, sticky = E)
            labelnodascendente.grid(row = 14, column = 0, sticky = E)
            labelargperigeo.grid(row = 15, column = 0, sticky = E)
            labelanoverdadera.grid(row = 16, column = 0, sticky = E)
            labelsem.grid(row = 11, column = 1, sticky = W)
            labelexc.grid(row = 12, column = 1, sticky = W)
            labelinc.grid(row = 13, column = 1, sticky = W)
            labelnodasc.grid(row = 14, column = 1, sticky = W)
            labelargper.grid(row = 15, column = 1, sticky = W)
            labelanover.grid(row = 16, column = 1, sticky = W)

        elif isinstance(objetos[objetoactual],orbita):
            labelsep = ttk.Label(ventanainf, text = "_________________________________________")
            labelnombre = ttk.Label(ventanainf, text = objetoactual)
            labelsemieje = ttk.Label(ventanainf, text = " Semieje mayor ")
            labelexcentricidad = ttk.Label(ventanainf, text = " Excentricidad ")
            labelinclinacion = ttk.Label(ventanainf, text = " Inclinacion ")
            labelnodascendente = ttk.Label(ventanainf, text = " Longitud del nodo ascendente ")
            labelargperigeo = ttk.Label(ventanainf, text = " Argumento del perigeo ")
            labelanoverdadera = ttk.Label(ventanainf, text = " Anomalia verdadera ")
            
            par = objetos[objetoactual].parametros
            labelsem = ttk.Label(ventanainf, text = str(par[0]))
            labelinc = ttk.Label(ventanainf, text = str(par[1]))
            labelexc = ttk.Label(ventanainf, text = str(par[2]))
            labelnodasc = ttk.Label(ventanainf, text = str(par[3]))
            labelargper = ttk.Label(ventanainf, text = str(par[4]))
            labelanover = ttk.Label(ventanainf, text = str(par[5]))

            labelradioapogeo = ttk.Label(ventanainf, text = " Radio del apogeo")
            labelradioperigeo = ttk.Label(ventanainf, text = " Radio del perigeo ")
            labelrapo = ttk.Label(ventanainf, text = str(par[0]*(1.+par[1])))
            labelrperi = ttk.Label(ventanainf, text = str(par[0]*(1.-par[1])))
            
            labelnombre.grid(row = 0, column = 0, columnspan = 3, sticky = W)
            labelsep.grid(row = 9, column = 0, columnspan = 3, sticky = W)
            labelsemieje.grid(row = 11, column = 1)
            labelexcentricidad.grid(row = 12, column = 1)
            labelinclinacion.grid(row = 13, column = 1)
            labelnodascendente.grid(row = 14, column = 1)
            labelargperigeo.grid(row = 15, column = 1)
            labelanoverdadera.grid(row = 16, column = 1)
            labelsem.grid(row = 11, column = 2)
            labelinc.grid(row = 12, column = 2)
            labelexc.grid(row = 13, column = 2)
            labelnodasc.grid(row = 14, column = 2)
            labelargper.grid(row = 15, column = 2)
            labelanover.grid(row = 16, column = 2)
            labelradioapogeo.grid(row = 20, column = 1)
            labelrapo.grid(row = 20, column = 2)
            labelradioperigeo.grid(row = 22, column =1)
            labelrperi.grid(row = 22, column = 2)

        elif isinstance(objetos[objetoactual],base):
            labelnombre = ttk.Label(ventanainf, text = objetoactual)
            labellatitud = ttk.Label(ventanainf, text = " Latitud ")
            lat,lon = xtogeo(objetos[objetoactual].pos[0,:],0.)
            labellat = ttk.Label(ventanainf, text = str(lat))
            labellongitud = ttk.Label(ventanainf, text = " Longitud ")
            labellon = ttk.Label(ventanainf, text = str(lon))

            labelnombre.grid(row = 0, column = 0, columnspan = 3, sticky = W)
            labellatitud.grid(row = 1, column = 0, sticky = E)
            labellat.grid(row = 1, column = 1, sticky = W)
            labellongitud.grid(row = 2, column = 0, sticky = E)
            labellon.grid(row = 2, column = 1, sticky = W)
        elif isinstance(objetos[objetoactual],sensor):
            objetos[objetoactual].actualizar(objetos)
            labelnombre = ttk.Label(ventanainf, text = objetoactual)
            labelobjeto = ttk.Label(ventanainf, text = " Unido a "+ objetos[objetoactual].objeto)
            labelposicion = ttk.Label(ventanainf, text = " Posicion ")
            labelpos = ttk.Label(ventanainf, text = str(objetos[objetoactual].pos[0,:]))
            labelvector = ttk.Label(ventanainf, text = " Vector director ")
            labelvec = ttk.Label(ventanainf, text = str(objetos[objetoactual].vector))
            labelapuntamiento = ttk.Label(ventanainf, text = " Apuntamiento ")
            labelapunt = ttk.Label(ventanainf, text = objetos[objetoactual].actitud)
            labelmaximorango = ttk.Label(ventanainf, text = " Maximo alcance ")
            labelmaxr = ttk.Label(ventanainf, text = str(objetos[objetoactual].dmax))

            labelnombre.grid(row = 0, column = 0, columnspan = 3, sticky = W)
            labelobjeto.grid(row = 1, column = 0, columnspan = 3, sticky = W)
            labelposicion.grid(row = 2, column = 0, sticky = E)
            labelpos.grid(row = 2, column = 1, sticky = W)
            labelapuntamiento.grid(row = 3, column = 0, sticky = E)
            labelapunt.grid(row = 3, column = 1, sticky = W)
            labelvector.grid(row = 4, column = 0, sticky = E)
            labelvec.grid(row = 4, column = 1, sticky = W)
            labelmaximorango.grid(row = 5, column = 0, sticky = E)
            labelmaxr.grid(row = 5, column = 1, sticky = W)
            
        elif isinstance(objetos[objetoactual],maniobra):
            ventanainf.destroy()
            informacionmaniobra(objetos[objetoactual])

    def mostrar(self,event):
        cambiarobjetoactual(event)
        if objetoactual in dibujarobjetos:
            self.labelmostrar = u'\u2713' + "  Ocultar"
        else:
            self.labelmostrar = " Ocultar "
        if objetoactual not in objetos:
            return
        self.menu.post(event.x_root, event.y_root)
    def borrar(self):
        del objetos[objetoactual]
        dibujarobjetos.remove(objetoactual)
        actualizararbol()
        actualizarcanvas()
    def propiedades(self):
        objetos =  arbolobjetos.get_children("objetos")
        if objetoactual in objetos:
            _ = ventanapropiedadessolido(objetoactual,"Satelite")
        objetos = arbolobjetos.get_children("orbitas")
        if objetoactual in objetos:
            ventanapropiedadessolido(objetoactual,"Orbita")
        objetos = arbolobjetos.get_children("bases")
        if objetoactual in objetos:
            ventanapropiedadessolido(objetoactual,"Base")
        objetos = arbolobjetos.get_children("sensores")
        if objetoactual in objetos:
            ventanapropiedadessolido(objetoactual,"Sensor")
    def mostrarobj(self):
        if objetoactual in dibujarobjetos:
            dibujarobjetos.remove(objetoactual)
            #self.menu.entryconfig(2,label = self.labelmostrar)
        else:
            dibujarobjetos.append(objetoactual)
            #self.menu.entryconfig(2,label = self.labelmostrar)
        
        actualizarcanvas()

def informacionmaniobra(maniobra):
    ventanainf= Toplevel(root)
    ventanainf.title(" Informacion de " + maniobra.propiedades.nombre)
    geometria = "650x"+str(root.winfo_screenheight()/2)+"+" + str(root.winfo_screenwidth()/2 - 300) + "+" + str(root.winfo_screenheight()/2 - 300)
    ventanainf.geometry(geometria)
    labeliniciodemaniobra = ttk.Label(ventanainf, text = " Inicio de maniobra ")
    labelorbitainicial = ttk.Label(ventanainf, text = " Orbita inicial ")
    labelposicioninicial = ttk.Label(ventanainf, text = " Posicion inicial ")
    labelanomaliaverdaderainicial = ttk.Label(ventanainf, text = "           Anomalia verdadera ")
    labelvelocidadinicial = ttk.Label(ventanainf, text = " Velocidad inicial ")
    labelfinaldemaniobra = ttk.Label(ventanainf, text = " Final de maniobra ")
    labelorbitafinal = ttk.Label(ventanainf, text = " Orbita final ")
    labelposicionfinal = ttk.Label(ventanainf, text = " Posicion final ")
    labelanomaliaverdaderafinal = ttk.Label(ventanainf, text = "           Anomalia verdadera ")
    labelvelocidadfinal = ttk.Label(ventanainf, text = " Velocidad final ")
    labelmaniobra = ttk.Label(ventanainf, text = " Maniobra ")
    labeldeltav = ttk.Label(ventanainf, text = " Delta-V ")

    labelorbi = ttk.Label(ventanainf, text = str(maniobra.orbitainicial.propiedades.nombre))
    labelposi = ttk.Label(ventanainf, text = str(maniobra.posicioninicial))
    labelanoi = ttk.Label(ventanainf, text = str(maniobra.anoini))
    labelvi = ttk.Label(ventanainf, text = str(maniobra.velocidadinicial))
    labelorbf = ttk.Label(ventanainf, text = str(maniobra.orbitafinal.propiedades.nombre))
    labelposf = ttk.Label(ventanainf, text = str(maniobra.posicionfinal))
    labelanof = ttk.Label(ventanainf, text = str(maniobra.anofin))
    labelvf = ttk.Label(ventanainf, text = str(maniobra.velocidadfinal))
    labelAv = ttk.Label(ventanainf, text = str(maniobra.Av))

    labelunidadeskm  = ttk.Label(ventanainf, text = " Km ")
    labelunidadeskm2 = ttk.Label(ventanainf, text = " Km ")
    labelunidadesgrados = ttk.Label(ventanainf, text = " Grados ")
    labelunidadesgrados2 = ttk.Label(ventanainf, text = " Grados ")
    labelunidadeskms = ttk.Label(ventanainf, text = " Km/s ")
    labelunidadeskms2 = ttk.Label(ventanainf, text = " Km/s ")
    labelunidadesAt = ttk.Label(ventanainf, text = str(np.sqrt(maniobra.Av[0]**2+maniobra.Av[1]**2+maniobra.Av[2]**2)) + "     Km/s")


    labeliniciodemaniobra.grid(row = 0, column = 0, columnspan = 4, sticky = W)
    labelorbitainicial.grid(row = 1, column = 1, sticky = E)
    labelposicioninicial.grid(row = 2, column = 1, sticky = E)
    labelanomaliaverdaderainicial.grid(row = 3, column = 1, sticky = E)
    labelvelocidadinicial.grid(row = 4, column = 1, sticky = E)
    labelfinaldemaniobra.grid(row = 10, column = 0, columnspan = 4, sticky = W)
    labelorbitafinal.grid(row = 11, column = 1, sticky = E)
    labelposicionfinal.grid(row = 12, column = 1, sticky = E)
    labelanomaliaverdaderafinal.grid(row = 13, column = 1, sticky = E)
    labelvelocidadfinal.grid(row = 14, column = 1, sticky = E)
    labelmaniobra.grid(row = 20, column = 0, columnspan = 4, sticky = W)
    labeldeltav.grid(row = 21, column = 1, sticky = E)
    labelorbi.grid(row = 1, column = 2, sticky = W)
    labelposi.grid(row = 2, column = 2, sticky = W)
    labelanoi.grid(row = 3, column = 2, sticky = W)
    labelvi.grid(row = 4, column = 2, sticky = W)
    labelorbf.grid(row = 11, column = 2, sticky = W)
    labelposf.grid(row = 12, column = 2, sticky = W)
    labelanof.grid(row = 13, column = 2, sticky = W)
    labelvf.grid(row = 14, column = 2, sticky = W)
    labelAv.grid(row = 21, column = 2, sticky = W)
    labelunidadeskm.grid(row = 2, column = 3, sticky = E)
    labelunidadeskm2.grid(row = 12, column = 3, sticky = E)
    labelunidadeskms.grid(row = 4, column = 3, sticky = E)
    labelunidadeskms2.grid(row = 14, column = 3, sticky = E)
    labelunidadesgrados.grid(row = 3, column = 3, sticky = E)
    labelunidadesgrados2.grid(row = 13, column = 3, sticky = E)
    labelunidadesAt.grid(row = 21, column = 3, sticky = E)



arbolobjetos = ttk.Treeview(areaarbol)
arbolobjetos.pack(side =TOP, fill = BOTH, expand = 1)
actualizararbol()
arbolobjetos.bind("<Double-1>",cambiarobjetoactual)
menud = menuderechoarbol()




notebook = ttk.Notebook(areadibujo)
frame2D = ttk.Frame(notebook)
frame3D = ttk.Frame(notebook)
notebook.add(frame2D, text = "   2D   ")
notebook.add(frame3D, text = "   3D   ")
anchofig = root.winfo_screenmmwidth()*0.03937*4/5

altofig = root.winfo_screenmmheight()*0.03937*4/5
figura2D = Figure(figsize=(anchofig,altofig))
#ejes2D = figura2D.add_subplot(111)
ejes2D = mpl.Axes(figura2D,[0.,0.,1.,1.])
ejes2D.set_axis_off()
figura2D.add_axes(ejes2D)
import mpl_toolkits.mplot3d.axes3d as p3
figura3D = Figure(figsize=(altofig,altofig))#Para que salga cuadrada y autoescale bien
ejes3D = p3.Axes3D(figura3D,[0.,0.,1.,1.])

figura3D.add_axes(ejes3D)
mpl.axis("off")
ejes3D.set_axis_off()
tierra = tierra()
tierra.tierra3D()




##############
mapamundi = imread("graficos/mapamundi.png")
ejes2D.imshow(mapamundi,zorder=0,extent=[-180,180,-90,90])
ejes2D.autoscale(False)

#### Funcion externalizada a mapa.py, se lee el archivo graficos/mapamundi.png
##from mpl_toolkits.basemap import Basemap    
##m = Basemap(projection='cyl',lon_0=0,lat_0=0,resolution='l',ax=ejes2D)
##m.drawcoastlines()
##m.fillcontinents(color='white',lake_color="grey")
##m.drawmapboundary(fill_color='grey')
##m.drawcountries(color = "k")
### draw parallels and meridians.
##m.drawparallels(np.arange(-90.,120.,30.))
##m.drawmeridians(np.arange(0.,420.,60.))
##############


    

mpl.axis("off")
canvas2D = FigureCanvasTkAgg(figura2D,frame2D)
canvas2D.show()
canvas2D.get_tk_widget().pack()
canvas3D = FigureCanvasTkAgg(figura3D,frame3D)
canvas3D.show()
canvas3D.get_tk_widget().pack()
ejes3D.mouse_init()



framebase.columnconfigure(1, weight = 1,minsize = 200)
framebase.columnconfigure(0, weight = 4)
barrastatus = barrastatus(root)
framebase.pack()
barrastatus.pack(side = BOTTOM, fill=X) 
areadibujo.grid(row = 1, column = 0)
areabotones1.grid(row = 0, column = 0, columnspan = 1, sticky = W)
areabotones2.grid(row = 0, column = 0, columnspan = 2, sticky = E)
areaarbol.grid(row = 1, column = 1, sticky = (N,S,E,W))

lanzar1.grid(row = 1, column = 23)
nuevoobj.grid(row = 1, column = 1)
nuevaorb.grid(row = 1, column = 2)
nuevabas.grid(row =1, column = 3)
nuevosens.grid(row = 1, column = 4)
lanzartodos.grid(row = 1, column = 20)
entradalanzar.grid(row = 1, column = 21, sticky = (N,S))
labellanzar.grid(row = 1, column = 22)
botonplay.grid(row = 1, column = 25)
botonpause.grid(row = 1, column = 26)
#nuevolanz.grid(row = 1, column = 30)
notebook.pack()


def actualizarcanvas():
    global objetos, dibujarobjetos,m, ejes2D, ejes3D,tierra,escenario,barrastatus

    
    barrastatus.set(" Actualizando gráficos... ")
##    if len(objetos) ==0:
##        return
    
    ejes2D.cla()
    ejes3D.cla()
##    ejes2D = mpl.Axes(figura2D,[0.,0.,1.,1.])
    ejes2D.set_axis_off()



#################
    ejes2D.imshow(mapamundi,zorder=0,extent=[-180,180,-90,90])
    ejes2D.autoscale(False)
##    from mpl_toolkits.basemap import Basemap    
##    m = Basemap(projection='cyl',lon_0=0,lat_0=0,resolution='l',ax=ejes2D)
##    m.drawcoastlines()
##    m.fillcontinents(color='white',lake_color="grey")
##    m.drawmapboundary(fill_color='grey')
##    m.drawcountries(color = "k")
##    # draw parallels and meridians.
##    m.drawparallels(np.arange(-90.,120.,30.))
##    m.drawmeridians(np.arange(0.,420.,60.))
###############
    tierra.dibujartierra3D(ejes3D)

    
    mpl.axis("off")
    ejes3D.set_axis_off()
    ejes3D.set_xticks([])
    ejes3D.set_yticks([])
    ejes3D.w_xaxis.line.set_lw(0.)
    ejes3D.w_yaxis.line.set_lw(0.)
    
    
    for objeto in dibujarobjetos:
        
        if isinstance(objetos[objeto],solido):
            inicio = -escenario.ultimospuntos-1
            paso = escenario.puntos
            if len(objetos[objeto].pos)<-inicio:
                inicio = 0
            dibujartraza(objetos[objeto].pos[inicio::paso],objetos[objeto].t[inicio::paso],objetos[objeto].propiedades.color,ejes2D)
            mostraricono2D(ejes2D,"graficos/iconos/satelite1.png",xtogeo(objetos[objeto].pos[-1,:],objetos[objeto].t[-1]))
            dibujarorbita(objetos[objeto].pos[inicio::paso],0,objetos[objeto].propiedades.color,ejes3D)
            mostraricono3D(ejes3D,objetos[objeto].pos[-1,:],objetos[objeto].propiedades.color)

        if isinstance(objetos[objeto],orbita):
            dibujarorbita(objetos[objeto].pos,0,objetos[objeto].propiedades.color,ejes3D)

        if isinstance(objetos[objeto],base):
            pos=[objetos[objeto].lat,objetos[objeto].lon]
            mostraricono2D(ejes2D,"graficos/iconos/base1.png",pos)
            
        if isinstance(objetos[objeto],sensor):
            objetos[objeto].actualizar(objetos)
            
            if escenario.conosensor == "Si":
                objetos[objeto].dibujar(ejes2D, ejes3D)
            if escenario.maximosensor =="Si":
                if isinstance(objetos[objetos[objeto].objeto],solido):
                    objetos[objeto].dibujartraza(ejes2D)
            
        if isinstance(objetos[objeto],maniobra):
            dibujarmaniobra3D(objetos[objeto],ejes3D)

    autoescala= np.array([getattr(ejes3D,"get_{}lim".format(dim))() for dim in "xyz"])
    ejes3D.auto_scale_xyz(*[[np.min(autoescala),np.max(autoescala)]]*3)
##    ejes3D.set_xlim(-7000,7000)
##    ejes3D.set_ylim(-7000,7000)
##    ejes3D.set_zlim(-7000,7000)
    
    canvas2D.draw()
    canvas3D.draw()
    barrastatus.completado()

def botonlanzar(objeto):
    global objetos, entradalanzar
    if isinstance(objeto,solido):
        objeto.tmax = objeto.t[-1,0] + float(entradalanzar.get())
        objeto.integrar(barrastatus)
    
    actualizarcanvas()
def botonlanzartodos():
    global entradalanzar, objetos, barrastatus
    incrementot = float(entradalanzar.get())
    for objeto in objetos:
        if isinstance(objetos[objeto],solido):
            objetos[objeto].tmax = objetos[objeto].t[-1,0] + incrementot
            objetos[objeto].integrar(barrastatus)
    actualizarcanvas()

play = 0
def handbotonplay():
    global play
    play = 1
    lanzarpaso()
    

def handbotonpause():
    global play
    play = 0

def lanzarpaso():
    global  play,objetos, barrastatus
    incrementot = 1.
    if play == 1:
        for objeto in objetos:
            if isinstance(objetos[objeto],solido):
                objetos[objeto].tmax = objetos[objeto].t[-1,0] + incrementot
                objetos[objeto].integrar(barrastatus)
        actualizarcanvas()
    root.after(1000,lanzarpaso)                   
def mostraricono2D(ejes,icono,pos):
    import Image
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    icono = np.array(Image.open(icono))
    icono = np.ma.masked_where(icono<0.2,icono)
    pos = [pos[1],pos[0]]
    imagen = OffsetImage(icono,zoom = 1)
    caja = AnnotationBbox(imagen,pos[:],xycoords="data",frameon= False)
    ejes.add_artist(caja)


def mostraricono3D(ejes,pos,color):
##    import Image
##    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
##    from mpl_toolkits.mplot3d import proj3d 
##    icono = np.array(Image.open("graficos/iconos/test.png"))
##    icono = np.ma.masked_where(icono<0.2,icono)
##    X,Y,_= proj3d.proj_transform(pos[0],pos[1],pos[2],ejes.get_proj())
##    xy = (X,Y)
##    imagen = OffsetImage(icono,zoom = 1)
##    caja = AnnotationBbox(imagen,xy,frameon= False)
##    ejes.add_artist(caja)
    ejes.scatter(pos[0],pos[1],pos[2], color = color, marker = "x")
    
def actualizarposiiconicono3D(event):
    pass

    
    

def cambiarnombreobjeto(nombreviejo,nombrenuevo):
    global objetos, dibujarobjetos, objetoactual
    objetotemp = objetos[nombreviejo]
    del objetos[nombreviejo]
    objetos.update({nombrenuevo:objetotemp})
    if nombreviejo in dibujarobjetos:
        dibujarobjetos.remove(nombreviejo)
        dibujarobjetos.append(nombrenuevo)

    objetoactual = nombrenuevo
    
    



root.mainloop()
