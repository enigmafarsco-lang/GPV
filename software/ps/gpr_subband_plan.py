#!/usr/bin/env python3
"""Reference computation for the uniform Hybrid-V3 sub-band plan."""
import argparse, json, math

def make_plan(f_start, f_stop, n_tones, tones_per_subband, fabric_hz):
    df=(f_stop-f_start)/(n_tones-1)
    # Choose a common residual start so every sub-band uses the same residual DDS pattern.
    residual0=-0.5*(tones_per_subband-1)*df
    plan=[]
    for k in range(n_tones):
        sb=k//tones_per_subband
        local=k%tones_per_subband
        residual=residual0+local*df
        rf=f_start+k*df
        lo=rf-residual
        step=round((residual/fabric_hz)*(1<<48)) & ((1<<48)-1)
        plan.append(dict(tone=k,subband=sb,rf_hz=rf,lo_hz=lo,residual_hz=residual,phase_step_u48=step))
    return dict(df_hz=df,residual0_hz=residual0,tones_per_subband=tones_per_subband,plan=plan)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--f-start",type=float,default=500e6)
    ap.add_argument("--f-stop",type=float,default=3e9)
    ap.add_argument("--tones",type=int,default=256)
    ap.add_argument("--tones-per-subband",type=int,default=12)
    ap.add_argument("--fabric-hz",type=float,default=245.76e6)
    ap.add_argument("--out",default="sweep_plan.json")
    a=ap.parse_args()
    p=make_plan(a.f_start,a.f_stop,a.tones,a.tones_per_subband,a.fabric_hz)
    with open(a.out,"w") as f: json.dump(p,f,indent=2)
    print(a.out)
