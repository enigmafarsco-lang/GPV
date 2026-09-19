import argparse,json
from pathlib import Path
import numpy as np
from .config import load_config
from .live_udp import UDPFrameReceiver

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--positions',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args();cfg=load_config(a.config);nt=int(cfg['waveform']['n_tones']);rx=UDPFrameReceiver(cfg['live']['udp_host'],int(cfg['live']['udp_port']),float(cfg['live']['frame_timeout_s']));S=np.zeros((nt,a.positions),complex);ts=[]
    for j in range(a.positions):
        frame,pos,t,z=rx.receive_position(nt);S[:,j]=z;ts.append(int(t));print(f'position {j+1}/{a.positions}: frame={frame} pos={pos}')
    f=np.linspace(cfg['waveform']['f_start_hz'],cfg['waveform']['f_stop_hz'],nt);x=np.linspace(cfg['scan']['x_start_m'],cfg['scan']['x_stop_m'],a.positions);meta={'timestamps_ns':ts,'source':'udp_GPR1'};np.savez_compressed(a.out,iq=S,frequencies_hz=f,x_m=x,metadata_json=json.dumps(meta));print(a.out)
if __name__=='__main__':main()
