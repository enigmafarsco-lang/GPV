import numpy as np
def kirchhoff_migrate(b,x_in,range_m,x_out,z_out,aperture_m=None):
    b=np.asarray(b,float);dr=float(np.median(np.diff(range_m)));im=np.zeros((len(z_out),len(x_out)))
    for iz,z in enumerate(z_out):
        for ix,x0 in enumerate(x_out):
            dx=x_in-x0;use=np.abs(dx)<=aperture_m/2 if aperture_m else np.ones_like(dx,bool)
            R=np.sqrt(z*z+dx[use]**2);idx=np.rint(R/dr).astype(int);v=(idx>=0)&(idx<b.shape[0])
            if np.any(v):
                cols=np.flatnonzero(use)[v];rr=R[v];im[iz,ix]=np.sum(b[idx[v],cols]*(z/(rr+1e-6))/(rr+1e-3))
    return im
