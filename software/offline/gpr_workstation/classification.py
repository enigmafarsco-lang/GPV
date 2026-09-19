import pickle
import numpy as np

FEATURES = ['depth_m','width_m','height_m','area_pixels','local_peak','local_mean',
            'local_std','compactness','low_band_energy','high_band_energy','spectral_slope']


def heuristic_classify(f):
    if f.get('width_m', 0) > .45 and f.get('height_m', 0) < .25:
        return 'plate_or_rebar', 'metal_generic', .62
    if .03 < f.get('width_m', 0) < .45:
        return 'pipe_or_cable', 'metal_generic', .60
    return 'unknown', 'unknown', .35


def load_classifier(path):
    with open(path, 'rb') as h:
        return pickle.load(h)


def classify(f, model=None, min_confidence=.6):
    if model is None:
        return heuristic_classify(f)
    names = model.get('features', FEATURES)
    X = np.array([[f.get(n, 0) for n in names]])
    clf = model['model']
    pr = clf.predict_proba(X)[0]
    i = int(np.argmax(pr))
    lab = str(clf.classes_[i])
    conf = float(pr[i])
    if conf < min_confidence:
        return 'unknown', 'unknown', conf
    generic = lab if lab in {'pipe_or_cable','plate_or_rebar','void_or_dielectric','unknown'} else 'metal_generic'
    material = lab if generic == 'metal_generic' else ('metal_generic' if generic in {'pipe_or_cable','plate_or_rebar'} else 'unknown')
    return generic, material, conf


def train_from_csv(csv_path, out_model, label_column='label', features=None):
    try:
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            'Classifier training requires pandas and scikit-learn. Run ./setup_offline.sh '
            'or install requirements.txt inside the package virtual environment.'
        ) from exc
    d = pd.read_csv(csv_path)
    features = features or [x for x in FEATURES if x in d.columns]
    clf = RandomForestClassifier(n_estimators=300, random_state=7, class_weight='balanced').fit(
        d[features].fillna(0), d[label_column].astype(str))
    bundle = {'model': clf, 'features': features}
    with open(out_model, 'wb') as h:
        pickle.dump(bundle, h)
    return bundle
