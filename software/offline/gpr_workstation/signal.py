import numpy as np
from scipy.signal import windows,stft
C0=299792458.0

def coherent_average(iq): return np.mean(iq,axis=0) if np.asarray(iq).ndim==3 else np.asarray(iq)
def make_window(n,name='kaiser',beta=6.0):
    name=name.lower()
    if name=='kaiser':return windows.kaiser(n,beta,False)
    if name=='hann':return windows.hann(n,False)
    if name=='hamming':return windows.hamming(n,False)
    if name=='blackman':return windows.blackman(n,False)
    if name in {'none','rect','rectangular'}:return np.ones(n)
    raise ValueError(name)
def calibrate(iq,coef):
    if coef is None:return iq.copy()
    c=np.asarray(coef).reshape(-1,1)
    if len(c)!=iq.shape[0]:raise ValueError('calibration coefficient length mismatch')
    return iq*c
def range_process(iq,freq,n_ifft,eps,window='kaiser',beta=6.0):
    n=iq.shape[0];z=np.zeros((n_ifft,iq.shape[1]),complex);z[:n]=iq*make_window(n,window,beta)[:,None];r=np.fft.ifft(z,axis=0);df=float(np.median(np.diff(freq)));depth=np.arange(n_ifft)*C0/(2*n_ifft*df*np.sqrt(eps));return r,depth
def local_stft(trace,fs_equiv):return stft(np.asarray(trace),fs=fs_equiv,nperseg=min(128,len(trace)),return_onesided=False)
