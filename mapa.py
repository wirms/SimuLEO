import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure

figura = plt.figure(1,figsize=(20,10),dpi = 100,frameon = False)

#a = figura.add_subplot(111)
ejes = plt.Axes(figura,[0.,0.,1.,1.])

m = Basemap(projection='cyl',lon_0=0,lat_0=0,resolution='l')
m.drawcoastlines(linewidth = 0.1,color = "k")
m.fillcontinents(color='white',lake_color="lightgrey")
m.drawmapboundary(fill_color='lightgrey')
m.drawcountries(color = "grey")
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,120.,30.),linewidth = 0.2)
m.drawmeridians(np.arange(0.,420.,60.),linewidth = 0.2)

plt.savefig("graficos/mapamundi.png",bbox_inches = "tight",pad_inches = 0)

plt.show()


