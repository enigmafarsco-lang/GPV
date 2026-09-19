import numpy as np
from .export import db20
def plot_ascan(ax,r,t,title='A-scan'):ax.clear();ax.plot(db20(t),r);ax.invert_yaxis();ax.set(xlabel='Relative amplitude (dB)',ylabel='Depth / range (m)',title=title);ax.grid(True,alpha=.25)
def plot_bscan(ax,x,z,img,title='B-scan',dyn=55,cmap='turbo',detections=None):
 ax.clear();im=ax.imshow(db20(img),extent=[x[0],x[-1],z[-1],z[0]],aspect='auto',vmin=-dyn,vmax=0,cmap=cmap);ax.set(xlabel='x (m)',ylabel='Depth (m)',title=title)
 if detections:
  for d in detections:ax.plot(d.x_m,d.depth_m,'wo',mfc='none')
 return im
def plot_spectrum(ax,f,t):a=np.abs(t);a=20*np.log10(a/max(np.max(a),1e-30)+1e-12);ax.clear();ax.plot(f/1e6,a);ax.set(xlabel='Frequency (MHz)',ylabel='Relative amplitude (dB)',title='Frequency response');ax.grid(True,alpha=.25)
def plot_3d_surface(ax,x,z,img,dyn=55):X,Z=np.meshgrid(x,z);D=np.maximum(db20(img),-dyn);ax.clear();ax.plot_surface(X,Z,D,cmap='turbo',linewidth=0,rstride=max(1,len(z)//100),cstride=max(1,len(x)//100));ax.set(xlabel='x (m)',ylabel='depth (m)',zlabel='dB',title='3-D migrated surface');ax.invert_yaxis()
