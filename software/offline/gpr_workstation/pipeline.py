from dataclasses import dataclass,field
import numpy as np
from .signal import coherent_average,calibrate,range_process
from .background import remove_background
from .migration import kirchhoff_migrate
from .detection import ca_cfar_2d,cluster_detections
from .features import extract_detection_features
from .classification import load_classifier,classify
@dataclass
class PipelineResult:
    frequency_iq:np.ndarray; calibrated_iq:np.ndarray; range_iq:np.ndarray; background_removed:np.ndarray; migrated:np.ndarray; detection_mask:np.ndarray; threshold_map:np.ndarray; range_m:np.ndarray; x_m:np.ndarray; z_m:np.ndarray; detections:list=field(default_factory=list); diagnostics:dict=field(default_factory=dict)
class GPRPipeline:
    def __init__(self,cfg):self.cfg=cfg
    def _coef(self,n):
        p=self.cfg['calibration'].get('coefficient_file','')
        if not p:return None
        if p.endswith('.npy'):c=np.load(p)
        elif p.endswith('.npz'):c=np.load(p)['coef']
        else:
            a=np.fromfile(p,dtype='<i2').reshape(-1,2);c=(a[:,0]+1j*a[:,1])/32768.0
        if len(c)!=n:raise ValueError('calibration coefficient length mismatch')
        return c
    def run(self,capture):
        cfg=self.cfg;iq=coherent_average(capture.normalized_iq());cal=calibrate(iq,self._coef(iq.shape[0])) if cfg['calibration']['enabled'] else iq.copy()
        if cfg['calibration'].get('remove_dc'):cal-=np.mean(cal,axis=0,keepdims=True)
        riq,rm=range_process(cal,capture.frequencies_hz,int(cfg['waveform']['n_ifft']),float(cfg['environment']['epsilon_r']),cfg['waveform']['window'],float(cfg['waveform']['window_beta']))
        b=cfg['background'];clean=remove_background(riq,b['method'],b['svd_modes'],b['ewma_alpha'],b['fk_kx_cut_fraction']);mag=np.abs(clean)
        m=cfg['migration'];xout=np.linspace(capture.x_m.min(),capture.x_m.max(),int(m['x_pixels']));zout=np.linspace(max(rm[1],1e-6),min(float(m['max_depth_m']),rm[-1]),int(m['z_pixels']))
        if m['enabled'] and m['method']=='kirchhoff':mig=kirchhoff_migrate(mag,capture.x_m,rm,xout,zout,float(m['aperture_m']))
        else:
            mig=np.column_stack([np.interp(zout,rm,mag[:,np.argmin(abs(capture.x_m-x))]) for x in xout])
        dcfg=cfg['detection']
        if dcfg['enabled']:
            mask,thr,noise=ca_cfar_2d(mig,dcfg['guard_x'],dcfg['guard_z'],dcfg['ref_x'],dcfg['ref_z'],dcfg['pfa']);dets=cluster_detections(mask,mig,xout,zout,dcfg['min_cluster_pixels'],dcfg['max_cluster_pixels'],dcfg['min_depth_m'],dcfg['max_depth_m'])
        else:mask=np.zeros_like(mig,bool);thr=np.zeros_like(mig);dets=[]
        cc=cfg['classification'];model=load_classifier(cc['model_file']) if cc['enabled'] and cc.get('model_file') else None
        for d in dets:
            d.features=extract_detection_features(d,mig,xout,zout,cal,capture.frequencies_hz)
            if cc['enabled']:d.classification,d.material_hint,d.confidence=classify(d.features,model,cc['min_confidence'])
        diag={'n_tones':iq.shape[0],'n_positions':iq.shape[1],'n_detections':len(dets),'epsilon_r':cfg['environment']['epsilon_r'],'range_max_m':float(rm[-1]),'background_method':b['method'],'migration_method':m['method'],'detection_method':dcfg['method']}
        return PipelineResult(iq,cal,riq,clean,mig,mask,thr,rm,xout,zout,dets,diag)
