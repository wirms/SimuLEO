from distutils.core import setup
import py2exe
import numpy
import matplotlib
import Tkinter





from distutils.core import setup
import py2exe
from glob import glob

datafiles = ["C:\\Users\\David\\Anaconda\\tcl\\tcl8.5\\init.tcl"]
datafiles.extend(matplotlib.get_py2exe_datafiles()) 
#datafiles.extend('C:\Users\David\Anaconda\tcl\tcl8.5\init.tcl')

setup(windows=['gui.py'], data_files= datafiles, options={"py2exe": {"includes": ["matplotlib"]}})


#"Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'


#setup(data_files=[matplotlib.get_py2exe_datafiles()],
#      console=['exe.py'])


#setup(console=["gui.py"],data_files =matplotlib.get_py2exe_datafiles())
#matplotlib.get_py2exe_datafiles()
