from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import copy, json, yaml

DEFAULTS: Dict[str, Any] = {
    "system": {"name":"ZCU208_XCZU48DR_GPR","mode":"SFCW","sample_format":"ci16_le","rfsoctile":{"dac_tile":0,"dac_block":0,"adc_tile":0,"adc_block":0}},
    "waveform": {"f_start_hz":500e6,"f_stop_hz":3e9,"n_tones":256,"n_ifft":2048,"dwell_s":50e-6,"averages":32,"window":"kaiser","window_beta":6.0},
    "environment": {"soil_name":"custom","epsilon_r":4.0,"conductivity_s_m":0.005,"moisture_vv":0.08,"attenuation_db_m":4.0,"standoff_m":0.5,"surface_reference_m":0.0,"temperature_c":20.0},
    "antenna": {"configuration":"bistatic","tx_rx_spacing_m":0.15,"polarization":"co-pol","gain_dbi":5.0,"beamwidth_deg":70.0,"orientation_deg":0.0},
    "scan": {"x_start_m":0.0,"x_stop_m":10.0,"n_positions":200,"line_spacing_m":0.5,"n_lines":1,"velocity_m_s":0.2,"position_source":"encoder","resample_uniform":True},
    "calibration": {"enabled":True,"coefficient_file":"","regularization":1e-6,"remove_dc":False,"phase_reference":True,"iq_balance":False},
    "background": {"method":"median","svd_modes":1,"ewma_alpha":0.98,"fk_kx_cut_fraction":0.04},
    "migration": {"enabled":True,"method":"kirchhoff","epsilon_r":"environment","x_pixels":200,"z_pixels":320,"max_depth_m":2.0,"aperture_m":2.0},
    "detection": {"enabled":True,"method":"ca_cfar_2d","pfa":1e-5,"guard_x":2,"guard_z":2,"ref_x":8,"ref_z":8,"min_cluster_pixels":4,"max_cluster_pixels":5000,"min_depth_m":0.03,"max_depth_m":5.0},
    "classification": {"enabled":True,"mode":"rules_or_model","model_file":"","min_confidence":0.60,"classes":["metal_generic","pipe_or_cable","plate_or_rebar","void_or_dielectric","unknown"],"material_subtype_requires_trained_model":True},
    "visualization": {"dynamic_range_db":55.0,"depth_min_m":0.0,"depth_max_m":2.0,"show_detections":True,"colormap":"turbo","volume_threshold_db":-18.0},
    "storage": {"save_npz":True,"save_hdf5":True,"save_png":True,"save_csv":True,"save_html":True},
    "live": {"udp_host":"0.0.0.0","udp_port":50000,"packet_magic":"GPR1","frame_timeout_s":1.0,"max_packet_bytes":65507}
}

def _deep_update(dst,src):
    for k,v in src.items():
        if isinstance(v,dict) and isinstance(dst.get(k),dict): _deep_update(dst[k],v)
        else: dst[k]=v
    return dst

def validate_config(cfg):
    wf=cfg['waveform']; env=cfg['environment']; scan=cfg['scan']
    if int(wf['n_tones'])<8: raise ValueError('waveform.n_tones must be >= 8')
    if int(wf['n_ifft'])<int(wf['n_tones']): raise ValueError('n_ifft must be >= n_tones')
    if float(wf['f_stop_hz'])<=float(wf['f_start_hz']): raise ValueError('f_stop_hz must exceed f_start_hz')
    if float(env['epsilon_r'])<=1.0: raise ValueError('environment.epsilon_r must be > 1')
    if int(scan['n_positions'])<1: raise ValueError('scan.n_positions must be positive')
    if cfg['background']['method'] not in {'none','mean','median','ewma','svd','fk'}: raise ValueError('unsupported background.method')
    if cfg['migration']['method'] not in {'none','kirchhoff'}: raise ValueError('unsupported migration.method')

def load_config(path=None,overrides=None):
    cfg=copy.deepcopy(DEFAULTS)
    if path:
        p=Path(path); data=yaml.safe_load(p.read_text(encoding='utf-8')) if p.suffix.lower() in {'.yaml','.yml'} else json.loads(p.read_text(encoding='utf-8'))
        if data: _deep_update(cfg,data)
    if overrides: _deep_update(cfg,overrides)
    validate_config(cfg); return cfg

def save_config(cfg,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(cfg,indent=2) if p.suffix.lower()=='.json' else yaml.safe_dump(cfg,sort_keys=False),encoding='utf-8')
