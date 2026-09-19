import builtins
import json
import numpy as np


def test_npz_loader_does_not_require_h5py(tmp_path, monkeypatch):
    original = builtins.__import__
    def blocker(name, *args, **kwargs):
        if name == 'h5py' or name.startswith('h5py.'):
            raise ModuleNotFoundError('blocked h5py')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', blocker)
    from gpr_workstation.io import load_capture
    p = tmp_path / 'x.npz'
    z = np.ones((8, 3), complex)
    np.savez(p, iq=z, frequencies_hz=np.arange(8.), x_m=np.arange(3.), metadata_json=json.dumps({}))
    cap = load_capture(p)
    assert cap.iq.shape == (8, 3)


def test_heuristic_classifier_does_not_require_sklearn_or_pandas(monkeypatch):
    original = builtins.__import__
    def blocker(name, *args, **kwargs):
        if name in {'pandas','sklearn'} or name.startswith('pandas.') or name.startswith('sklearn.'):
            raise ModuleNotFoundError('blocked optional ML dependency')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', blocker)
    import importlib
    mod = importlib.import_module('gpr_workstation.classification')
    c, m, conf = mod.classify({'width_m':0.2,'height_m':0.1}, None, .6)
    assert c == 'pipe_or_cable'
    assert m == 'metal_generic'
    assert conf >= .6



def test_export_survives_missing_h5py(tmp_path, monkeypatch):
    import numpy as np
    from gpr_workstation.pipeline import PipelineResult
    import gpr_workstation.export as ex
    def missing(*args, **kwargs):
        raise ModuleNotFoundError('HDF5 support requires h5py')
    monkeypatch.setattr(ex, 'save_processed_h5', missing)
    r = PipelineResult(
        np.ones((8,3),complex), np.ones((8,3),complex), np.ones((16,3),complex),
        np.ones((16,3),complex), np.ones((8,3),float), np.zeros((8,3),bool),
        np.zeros((8,3),float), np.linspace(0,1,16), np.linspace(0,1,3), np.linspace(.01,.8,8),
        [], {'test': True})
    cfg = {
        'storage': {'save_npz': True, 'save_hdf5': True},
        'visualization': {'dynamic_range_db': 55, 'colormap': 'turbo'}
    }
    out = ex.export_result(r, cfg, tmp_path/'out', np.linspace(1,2,8), np.linspace(0,1,3))
    assert (out/'processed.npz').exists()
    assert (out/'HDF5_SKIPPED.txt').exists()
