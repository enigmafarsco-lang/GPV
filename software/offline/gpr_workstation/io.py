from pathlib import Path
import json
import numpy as np
from scipy.io import loadmat
from .models import Capture


def _meta(path):
    if not path:
        return {}
    p = Path(path)
    if p.suffix.lower() == '.json':
        return json.loads(p.read_text(encoding='utf-8'))
    import yaml
    return yaml.safe_load(p.read_text(encoding='utf-8')) or {}


def _axes(meta, n_tones, n_pos):
    f = np.asarray(meta.get('frequencies_hz', np.linspace(
        float(meta.get('f_start_hz', 500e6)),
        float(meta.get('f_stop_hz', 3e9)), n_tones)), float)
    x = np.asarray(meta.get('x_m', np.linspace(
        float(meta.get('x_start_m', 0.0)),
        float(meta.get('x_stop_m', max(1, n_pos - 1))), n_pos)), float)
    return f, x


def load_raw_ci16(path, metadata):
    meta = metadata if isinstance(metadata, dict) else _meta(metadata)
    nt = int(meta['n_tones'])
    np_ = int(meta['n_positions'])
    na = int(meta.get('n_averages', 1))
    raw = np.fromfile(path, dtype='<i2')
    exp = na * nt * np_ * 2
    if raw.size != exp:
        raise ValueError(f'raw file has {raw.size} int16 values; expected {exp}')
    a = raw.reshape(na, nt, np_, 2)
    z = a[..., 0].astype(float) + 1j * a[..., 1].astype(float)
    if na == 1:
        z = z[0]
    f, x = _axes(meta, nt, np_)
    return Capture(z, f, x, metadata=meta)


def _import_h5py():
    try:
        import h5py
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            'HDF5 support requires h5py. The NPZ/MAT/raw pipeline does not. '
            'Run ./setup_offline.sh (recommended) or install the optional dependency '
            'inside the package virtual environment: .venv/bin/python -m pip install h5py'
        ) from exc
    return h5py


def load_capture(path, metadata=None):
    p = Path(path)
    ext = p.suffix.lower()
    if ext == '.bin':
        if metadata is None:
            raise ValueError('raw .bin requires metadata JSON/YAML')
        return load_raw_ci16(p, metadata)
    if ext == '.npz':
        d = np.load(p, allow_pickle=True)
        iq = d['iq'] if 'iq' in d else d['S']
        meta = json.loads(str(d['metadata_json'])) if 'metadata_json' in d else {}
        f = d['frequencies_hz'] if 'frequencies_hz' in d else (
            d['f'] if 'f' in d else np.linspace(meta.get('f_start_hz', 500e6), meta.get('f_stop_hz', 3e9), iq.shape[-2]))
        x = d['x_m'] if 'x_m' in d else (
            d['x'] if 'x' in d else np.arange(iq.shape[-1], dtype=float))
        return Capture(iq, np.asarray(f), np.asarray(x), metadata=meta)
    if ext == '.mat':
        d = loadmat(p, squeeze_me=True)
        iq = d.get('iq', d.get('S'))
        if iq is None:
            raise KeyError('MAT requires iq or S')
        f = np.ravel(d.get('frequencies_hz', d.get('f', np.arange(iq.shape[-2]))))
        x = np.ravel(d.get('x_m', d.get('x', np.arange(iq.shape[-1]))))
        return Capture(iq, f, x)
    if ext in {'.h5', '.hdf5'}:
        h5py = _import_h5py()
        with h5py.File(p, 'r') as h:
            if 'iq' in h:
                iq = h['iq'][()]
            elif 'iq_real' in h and 'iq_imag' in h:
                iq = h['iq_real'][()] + 1j * h['iq_imag'][()]
            else:
                raise KeyError('HDF5 requires iq or iq_real/iq_imag')
            f = h['frequencies_hz'][()] if 'frequencies_hz' in h else np.arange(iq.shape[-2])
            x = h['x_m'][()] if 'x_m' in h else np.arange(iq.shape[-1])
            meta = {k: v for k, v in h.attrs.items()}
        return Capture(iq, np.asarray(f), np.asarray(x), metadata=meta)
    raise ValueError(f'unsupported input {ext}')


def save_processed_h5(path, result):
    h5py = _import_h5py()
    with h5py.File(path, 'w') as h:
        for name in ('frequency_iq', 'calibrated_iq', 'range_iq', 'background_removed',
                     'migrated', 'detection_mask', 'threshold_map'):
            a = getattr(result, name, None)
            if a is None:
                continue
            if np.iscomplexobj(a):
                g = h.create_group(name)
                g.create_dataset('real', data=np.real(a), compression='gzip')
                g.create_dataset('imag', data=np.imag(a), compression='gzip')
            else:
                h.create_dataset(name, data=a, compression='gzip')
        h.create_dataset('range_m', data=result.range_m)
        h.create_dataset('x_m', data=result.x_m)
        h.create_dataset('z_m', data=result.z_m)
