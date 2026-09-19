import numpy as np
def remove_background(a,method='median',svd_modes=1,ewma_alpha=.98,fk_kx_cut_fraction=.04):
    a=np.asarray(a);method=method.lower()
    if method=='none':return a.copy()
    if method=='mean':return a-np.mean(a,axis=1,keepdims=True)
    if method=='median':
        bg=np.median(a.real,axis=1)+1j*np.median(a.imag,axis=1) if np.iscomplexobj(a) else np.median(a,axis=1);return a-bg[:,None]
    if method=='ewma':
        out=np.empty_like(a);bg=a[:,0].copy();out[:,0]=0
        for j in range(1,a.shape[1]):out[:,j]=a[:,j]-bg;bg=ewma_alpha*bg+(1-ewma_alpha)*a[:,j]
        return out
    if method=='svd':
        U,s,Vh=np.linalg.svd(a,full_matrices=False);k=min(max(int(svd_modes),0),len(s));return a-(U[:,:k]*s[:k])@Vh[:k,:] if k else a.copy()
    if method=='fk':
        F=np.fft.fftshift(np.fft.fft2(a));c=a.shape[1]//2;k=max(1,int(a.shape[1]*fk_kx_cut_fraction));F[:,max(0,c-k):min(a.shape[1],c+k+1)]=0;return np.fft.ifft2(np.fft.ifftshift(F))
    raise ValueError(method)
