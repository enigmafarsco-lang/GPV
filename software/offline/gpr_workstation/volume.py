import numpy as np
from scipy.interpolate import interp1d
def assemble_volume(images,y_lines):return np.stack(images,axis=1),np.asarray(y_lines,float)
def interpolate_volume(volume,y_lines,y_grid):return interp1d(y_lines,volume,axis=1,kind='linear',bounds_error=False,fill_value='extrapolate')(y_grid)
def cscan(volume,z_m,depth_m):
    i=int(np.argmin(abs(np.asarray(z_m)-depth_m)));return volume[i],i
