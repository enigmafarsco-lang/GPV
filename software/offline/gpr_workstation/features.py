import numpy as np
def extract_detection_features(det,image,x,z,frequency_iq=None,frequencies_hz=None):
    ix=int(np.argmin(abs(x-det.x_m)));iz=int(np.argmin(abs(z-det.depth_m)));patch=image[max(0,iz-3):iz+4,max(0,ix-3):ix+4]
    f={'depth_m':det.depth_m,'width_m':det.width_m,'height_m':det.height_m,'area_pixels':float(det.area_pixels),'local_peak':float(np.max(patch)),'local_mean':float(np.mean(patch)),'local_std':float(np.std(patch)),'compactness':float(det.area_pixels/49)}
    if frequency_iq is not None:
        tr=np.abs(frequency_iq[:,min(ix,frequency_iq.shape[1]-1)]);tr=tr/max(np.max(tr),1e-30);q=max(1,len(tr)//4);f.update(low_band_energy=float(np.mean(tr[:q]**2)),high_band_energy=float(np.mean(tr[-q:]**2)),spectral_slope=float((np.mean(tr[-q:])-np.mean(tr[:q]))/(frequencies_hz[-1]-frequencies_hz[0]+1e-30)*1e9))
    return f
