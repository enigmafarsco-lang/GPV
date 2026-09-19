from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import numpy as np
@dataclass
class Capture:
    iq: np.ndarray
    frequencies_hz: np.ndarray
    x_m: np.ndarray
    y_m: Optional[np.ndarray]=None
    gps: Optional[np.ndarray]=None
    imu: Optional[np.ndarray]=None
    metadata: Dict[str,Any]=field(default_factory=dict)
    def normalized_iq(self):
        a=np.asarray(self.iq)
        if a.ndim not in (2,3): raise ValueError(f'IQ array must have 2 or 3 dimensions, got {a.shape}')
        return a.astype(np.complex128,copy=False)
@dataclass
class Detection:
    id:int; x_m:float; y_m:float; depth_m:float; peak_db:float; area_pixels:int; width_m:float; height_m:float
    classification:str='unknown'; material_hint:str='unknown'; confidence:float=0.0; features:Dict[str,float]=field(default_factory=dict)
