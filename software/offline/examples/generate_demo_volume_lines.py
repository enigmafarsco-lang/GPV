import argparse,json
from pathlib import Path
import numpy as np
C=299792458.;p=argparse.ArgumentParser();p.add_argument('--outdir',default='demo_lines');p.add_argument('--lines',type=int,default=5);p.add_argument('--spacing',type=float,default=.35);a=p.parse_args();out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(11);nt=256;np_=120;f=np.linspace(500e6,3e9,nt);x=np.linspace(0,6,np_);eps=3.2;v=C/np.sqrt(eps);targets=[(2.0,.7,.25,.18),(4.1,1.0,.55,.28)]
for li in range(a.lines):
 y=li*a.spacing;S=np.zeros((nt,np_),complex)
 for xp,yp,z,A in targets:
  R=np.sqrt(z*z+(x-xp)**2+(y-yp)**2);S+=A*np.exp(-1j*4*np.pi*f[:,None]*R[None,:]/v)/(R[None,:]+.15)**2
 S+=.28*np.exp(1j*(.3+.08*(f-f[0])/(f[-1]-f[0])))[:,None];S+=.004*(rng.normal(size=S.shape)+1j*rng.normal(size=S.shape));meta={'line_y_m':y,'f_start_hz':f[0],'f_stop_hz':f[-1]};np.savez_compressed(out/f'line_{li:02d}.npz',iq=S,frequencies_hz=f,x_m=x,metadata_json=json.dumps(meta))
print(out)
