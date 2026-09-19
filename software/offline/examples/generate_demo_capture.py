import argparse,json,numpy as np
C=299792458.;p=argparse.ArgumentParser();p.add_argument('--out',default='demo_capture.npz');a=p.parse_args();rng=np.random.default_rng(3);nt=256;np_=200;f=np.linspace(500e6,3e9,nt);x=np.linspace(0,10,np_);eps=3.2;v=C/np.sqrt(eps);S=np.zeros((nt,np_),complex)
for xp,z,A in [(2,.1,.03),(4,.25,.08),(6,.5,.18),(8,.8,.35)]:R=np.sqrt(z*z+(x-xp)**2);S+=A*np.exp(-1j*4*np.pi*f[:,None]*R[None,:]/v)/(R[None,:]+.12)**2
S+=.3*np.exp(1j*(.4+.12*(f-f[0])/(f[-1]-f[0])))[:,None];S+=.005*(rng.normal(size=S.shape)+1j*rng.normal(size=S.shape));meta={'f_start_hz':f[0],'f_stop_hz':f[-1],'n_tones':nt,'n_positions':np_,'synthetic_demo':True};np.savez_compressed(a.out,iq=S,frequencies_hz=f,x_m=x,metadata_json=json.dumps(meta));print(a.out)
