import numpy as np
from scipy.ndimage import uniform_filter,label,find_objects
from .models import Detection
def ca_cfar_2d(img,guard_x=2,guard_z=2,ref_x=8,ref_z=8,pfa=1e-5):
    p=np.maximum(np.asarray(img,float),0);outer=(2*(guard_z+ref_z)+1,2*(guard_x+ref_x)+1);inner=(2*guard_z+1,2*guard_x+1);nref=np.prod(outer)-np.prod(inner)
    noise=np.maximum((uniform_filter(p,outer,mode='nearest')*np.prod(outer)-uniform_filter(p,inner,mode='nearest')*np.prod(inner))/nref,1e-30);alpha=nref*(pfa**(-1/nref)-1);thr=alpha*noise;return p>thr,thr,noise
def cluster_detections(mask,img,x,z,min_pixels=4,max_pixels=5000,min_depth=0,max_depth=1e9):
    lab,n=label(mask);dets=[];ref=max(float(np.max(img)),1e-30);did=1
    for k,sl in enumerate(find_objects(lab),1):
        if sl is None:continue
        pix=np.argwhere(lab[sl]==k);area=len(pix)
        if area<min_pixels or area>max_pixels:continue
        zz=pix[:,0]+sl[0].start;xx=pix[:,1]+sl[1].start;vals=img[zz,xx];m=int(np.argmax(vals));zi=int(zz[m]);xi=int(xx[m]);depth=float(z[zi])
        if not min_depth<=depth<=max_depth:continue
        width=float(x[xx.max()]-x[xx.min()]) if len(np.unique(xx))>1 else 0;height=float(z[zz.max()]-z[zz.min()]) if len(np.unique(zz))>1 else 0
        dets.append(Detection(did,float(x[xi]),0,depth,20*np.log10(float(vals[m])/ref+1e-12),area,width,height));did+=1
    return dets
