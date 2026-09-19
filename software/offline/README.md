# GPR Offline / Live Workstation v2.1

Desktop/offline processing companion for the ZCU208/XCZU48DR GPR build kit. It accepts RFSoC frequency-domain I/Q captures, applies the GPR processing chain, and produces A-scan, B-scan, migrated 2-D images, CFAR detections, C-scan/depth slices, 3-D products, spectra and diagnostics.

Supported input: raw interleaved complex int16 (`.bin`) plus YAML/JSON metadata, NPZ, MAT, HDF5, and UDP live packets using the included `GPR1` protocol.

## Recommended installation on Ubuntu/Debian

Do not install the requirements into the system Python. Modern Debian/Ubuntu enables PEP 668 and intentionally rejects that operation.

From the FullStack root:

```bash
./setup_offline.sh
./run_offline_demo.sh
```

Or from this directory:

```bash
./setup_venv.sh
./run_demo.sh
```

The setup script creates `software/offline/.venv` and installs all dependencies there.
If venv support is not installed:

```bash
sudo apt update
sudo apt install -y python3-venv
```

## Manual virtual-environment setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python examples/generate_demo_capture.py --out demo_capture.npz
PYTHONPATH=. python -m gpr_workstation.cli process \\
  demo_capture.npz \\
  --config configs/demo_synthetic.yaml \\
  --out output/demo
```

## Environment check

```bash
.venv/bin/python -m gpr_workstation.doctor
```

`h5py`, pandas and scikit-learn are loaded only when their features are used. NPZ/MAT/raw processing and rule-based classification no longer fail just because HDF5 or ML training dependencies are absent. If `h5py` is not installed, processing still completes and writes `HDF5_SKIPPED.txt` instead of aborting.

## GUI

```bash
./run_gui.sh --input demo_capture.npz --config configs/demo_synthetic.yaml
```

## Multi-line 3-D / C-scan

```bash
.venv/bin/python examples/generate_demo_volume_lines.py --outdir demo_lines
PYTHONPATH=. .venv/bin/python -m gpr_workstation.volume_cli \\
  demo_lines/line_00.npz demo_lines/line_01.npz demo_lines/line_02.npz \\
  demo_lines/line_03.npz demo_lines/line_04.npz \\
  --y-lines 0,0.35,0.70,1.05,1.40 \\
  --config configs/demo_synthetic.yaml \\
  --out output/volume \\
  --depths 0.25,0.55
```

Specific metal subtypes are model-gated. A generic GPR image is not treated as sufficient evidence to distinguish copper, aluminum and steel. The default pipeline reports generic conductor/geometry classes. A user-trained labeled classifier can enable site-specific material labels after validation.
