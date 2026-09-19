import argparse, json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .config import load_config
from .io import load_capture
from .pipeline import GPRPipeline
from .export import db20
from .volume import assemble_volume, interpolate_volume, cscan

def main(argv=None):
    ap=argparse.ArgumentParser(description='Process multiple parallel GPR lines into a 3-D volume')
    ap.add_argument('inputs',nargs='+');ap.add_argument('--y-lines',required=True,help='comma-separated line y positions in metres');ap.add_argument('--config',required=True);ap.add_argument('--out',required=True);ap.add_argument('--depths',default='0.25,0.5,0.75')
    a=ap.parse_args(argv); y=np.array([float(v) for v in a.y_lines.split(',')])
    if len(y)!=len(a.inputs):raise ValueError('number of --y-lines values must equal number of inputs')
    cfg=load_config(a.config);results=[]
    for p in a.inputs:results.append(GPRPipeline(cfg).run(load_capture(p)))
    z=results[0].z_m;x=results[0].x_m
    for r in results[1:]:
        if r.migrated.shape!=results[0].migrated.shape:raise ValueError('all lines must share migrated grid')
    vol,_=assemble_volume([r.migrated for r in results],y)
    ygrid=np.linspace(y.min(),y.max(),max(2,int(round((y.max()-y.min())/max(np.median(np.diff(y)) if len(y)>1 else 0.25,1e-6)))+1))
    voli=interpolate_volume(vol,y,ygrid) if len(y)>1 else vol
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'volume.npz',volume=voli,x_m=x,y_m=ygrid,z_m=z)
    for depth in [float(v) for v in a.depths.split(',')]:
        cs,iz=cscan(voli,z,depth);fig,ax=plt.subplots(figsize=(8,5));im=ax.imshow(db20(cs),extent=[x[0],x[-1],ygrid[-1],ygrid[0]],aspect='auto',vmin=-55,vmax=0,cmap='turbo');ax.set(xlabel='x (m)',ylabel='y (m)',title=f'C-scan at {z[iz]:.2f} m');fig.colorbar(im,ax=ax,label='dB');fig.tight_layout();fig.savefig(out/f'cscan_{z[iz]:.2f}m.png',dpi=160);plt.close(fig)
    D=db20(voli);thr=float(cfg['visualization'].get('volume_threshold_db',-18));idx=np.argwhere(D>=thr)
    if len(idx)>30000:idx=idx[::max(1,len(idx)//30000)]
    fig=plt.figure(figsize=(9,7));ax=fig.add_subplot(111,projection='3d')
    if len(idx):
        zz,yy,xx=idx.T;ax.scatter(x[xx],ygrid[yy],z[zz],c=D[zz,yy,xx],s=5,cmap='turbo',vmin=thr,vmax=0,alpha=.7)
    ax.set(xlabel='x (m)',ylabel='y (m)',zlabel='depth (m)',title='3-D GPR volume above display threshold');ax.invert_zaxis();fig.tight_layout();fig.savefig(out/'volume_3d.png',dpi=170);plt.close(fig)
    (out/'volume_metadata.json').write_text(json.dumps({'n_lines':len(a.inputs),'y_lines_m':y.tolist(),'interpolated_y_m':ygrid.tolist(),'volume_threshold_db':thr},indent=2),encoding='utf-8')
    print(out)
if __name__=='__main__':main()
