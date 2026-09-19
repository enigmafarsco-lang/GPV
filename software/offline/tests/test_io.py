import numpy as np
from gpr_workstation.io import load_raw_ci16

def test_raw_roundtrip(tmp_path):
    nt,np_=8,3;a=np.arange(nt*np_).reshape(nt,np_)+1j*np.ones((nt,np_))*4
    raw=np.empty((nt,np_,2),dtype='<i2');raw[...,0]=a.real;raw[...,1]=a.imag
    p=tmp_path/'a.bin';raw.tofile(p)
    cap=load_raw_ci16(p,{'n_tones':nt,'n_positions':np_,'f_start_hz':1e8,'f_stop_hz':2e8})
    assert np.all(cap.iq==a)
