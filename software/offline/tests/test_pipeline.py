import numpy as np
from gpr_workstation.config import load_config
from gpr_workstation.models import Capture
from gpr_workstation.pipeline import GPRPipeline

def test_pipeline_shapes():
    c=299792458.0;nt=32;np_=24;f=np.linspace(500e6,1e9,nt);x=np.linspace(0,2,np_);eps=4.;v=c/np.sqrt(eps);R=np.sqrt(.3**2+(x-1.0)**2)
    S=.2*np.exp(-1j*4*np.pi*f[:,None]*R[None,:]/v)+.1
    cap=Capture(S,f,x)
    cfg=load_config(overrides={'waveform':{'n_tones':nt,'n_ifft':128},'environment':{'epsilon_r':eps},'scan':{'n_positions':np_},'migration':{'x_pixels':24,'z_pixels':40,'max_depth_m':.8,'aperture_m':1.0},'detection':{'min_cluster_pixels':1}})
    r=GPRPipeline(cfg).run(cap)
    assert r.range_iq.shape==(128,np_)
    assert r.migrated.shape==(40,24)
    assert r.detection_mask.shape==r.migrated.shape
