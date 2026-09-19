from pathlib import Path
import csv, json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
from .io import save_processed_h5

def db20(a):
    a=np.abs(a); return 20*np.log10(a/max(float(np.max(a)),1e-30)+1e-12)

def _heat(path,img,x,z,title,dyn=55,cmap='turbo',dets=None,label='Relative amplitude (dB)'):
    fig,ax=plt.subplots(figsize=(10,5)); im=ax.imshow(db20(img) if np.iscomplexobj(img) or label.endswith('(dB)') else img,extent=[x[0],x[-1],z[-1],z[0]],aspect='auto',vmin=(-dyn if label.endswith('(dB)') else None),vmax=(0 if label.endswith('(dB)') else None),cmap=cmap)
    ax.set(xlabel='Along-track x (m)',ylabel='Depth / range (m)',title=title); fig.colorbar(im,ax=ax,label=label)
    if dets:
        for d in dets: ax.plot(d.x_m,d.depth_m,'wo',mfc='none',ms=8);ax.text(d.x_m,d.depth_m,d.classification,color='white',fontsize=7)
    fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def _freq_stage(path,a,f,x,title,dyn=55):
    fig,ax=plt.subplots(figsize=(10,5));d=db20(a);im=ax.imshow(d,extent=[x[0],x[-1],f[-1]/1e6,f[0]/1e6],aspect='auto',vmin=-dyn,vmax=0,cmap='turbo');ax.set(xlabel='x (m)',ylabel='Frequency (MHz)',title=title);fig.colorbar(im,ax=ax,label='Relative amplitude (dB)');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def _phase_stage(path,a,f,x,title):
    fig,ax=plt.subplots(figsize=(10,5));im=ax.imshow(np.angle(a),extent=[x[0],x[-1],f[-1]/1e6,f[0]/1e6],aspect='auto',vmin=-np.pi,vmax=np.pi,cmap='twilight');ax.set(xlabel='x (m)',ylabel='Frequency (MHz)',title=title);fig.colorbar(im,ax=ax,label='Phase (rad)');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def _stft(path,trace):
    f,t,Z=stft(np.real(trace),nperseg=min(128,len(trace)),noverlap=min(96,max(0,len(trace)//2)));d=db20(Z);fig,ax=plt.subplots(figsize=(9,4.5));im=ax.pcolormesh(t,f,d,shading='auto',vmin=-60,vmax=0,cmap='turbo');ax.set(xlabel='Normalized sample time',ylabel='Normalized frequency',title='Local STFT-style diagnostic');fig.colorbar(im,ax=ax,label='dB');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def _surface3d(path,x,z,img,dyn=55):
    fig=plt.figure(figsize=(10,6));ax=fig.add_subplot(111,projection='3d');X,Z=np.meshgrid(x,z);D=np.maximum(db20(img),-dyn);ax.plot_surface(X,Z,D,cmap='turbo',linewidth=0,rstride=max(1,len(z)//100),cstride=max(1,len(x)//100));ax.set(xlabel='x (m)',ylabel='Depth (m)',zlabel='dB',title='3-D migrated response');ax.invert_yaxis();fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def export_result(r,cfg,outdir,frequencies_hz=None,source_x_m=None):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    storage=cfg.get('storage',{})
    if storage.get('save_npz',True):
        np.savez_compressed(out/'processed.npz',frequency_iq=r.frequency_iq,calibrated_iq=r.calibrated_iq,range_iq=r.range_iq,background_removed=r.background_removed,migrated=r.migrated,detection_mask=r.detection_mask,threshold_map=r.threshold_map,range_m=r.range_m,x_m=r.x_m,z_m=r.z_m)
    if storage.get('save_hdf5',True):
        try:
            save_processed_h5(out/'processed.h5',r)
        except ModuleNotFoundError as exc:
            (out/'HDF5_SKIPPED.txt').write_text(str(exc)+'\n',encoding='utf-8')
            print('WARNING:',exc)
    with open(out/'detections.csv','w',newline='',encoding='utf-8') as f:
        q=csv.writer(f);q.writerow(['id','x_m','depth_m','peak_db','area_pixels','width_m','height_m','class','material_hint','confidence'])
        for d in r.detections:q.writerow([d.id,d.x_m,d.depth_m,d.peak_db,d.area_pixels,d.width_m,d.height_m,d.classification,d.material_hint,d.confidence])
    (out/'diagnostics.json').write_text(json.dumps(r.diagnostics,indent=2),encoding='utf-8')
    v=cfg['visualization'];dyn=v['dynamic_range_db'];cmap=v['colormap'];sx=source_x_m if source_x_m is not None else np.linspace(r.x_m[0],r.x_m[-1],r.background_removed.shape[1])
    _heat(out/'04_range_bscan.png',r.range_iq,sx,r.range_m,'Range-domain B-scan before background removal',dyn,cmap)
    _heat(out/'05_background_removed.png',r.background_removed,sx,r.range_m,'Background/clutter removed B-scan',dyn,cmap)
    _heat(out/'06_migration_2d.png',r.migrated,r.x_m,r.z_m,'Migrated 2-D image',dyn,cmap,r.detections)
    _surface3d(out/'09_migration_3d.png',r.x_m,r.z_m,r.migrated,dyn)
    fig,ax=plt.subplots(figsize=(10,5));im=ax.imshow(r.detection_mask,extent=[r.x_m[0],r.x_m[-1],r.z_m[-1],r.z_m[0]],aspect='auto',cmap='gray_r');ax.set(xlabel='x (m)',ylabel='Depth (m)',title='CFAR detection mask');fig.tight_layout();fig.savefig(out/'08_cfar_mask.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5));im=ax.imshow(r.threshold_map,extent=[r.x_m[0],r.x_m[-1],r.z_m[-1],r.z_m[0]],aspect='auto',cmap='viridis');ax.set(xlabel='x (m)',ylabel='Depth (m)',title='CFAR threshold map');fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(out/'07_cfar_threshold.png',dpi=160);plt.close(fig)
    if frequencies_hz is not None:
        _freq_stage(out/'01_raw_frequency_magnitude.png',r.frequency_iq,frequencies_hz,sx,'Raw RFSoC frequency-domain magnitude',dyn)
        _phase_stage(out/'02_raw_frequency_phase.png',r.frequency_iq,frequencies_hz,sx,'Raw RFSoC frequency-domain phase')
        _freq_stage(out/'03_calibrated_frequency.png',r.calibrated_iq,frequencies_hz,sx,'Calibrated/windowed frequency-domain magnitude',dyn)
        _stft(out/'10_stft_diagnostic.png',r.calibrated_iq[:,r.calibrated_iq.shape[1]//2])
    return out
