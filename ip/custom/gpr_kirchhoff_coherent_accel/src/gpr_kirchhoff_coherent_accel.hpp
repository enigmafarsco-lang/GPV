#include <ap_int.h>
#include <hls_math.h>
extern "C" void gpr_kirchhoff_coherent_accel(const ap_uint<32>*bscan_iq,float*image,int n_pos,int n_range,int n_x,int n_z,float dx,float dz,float dr,float r_off,float kbeta_cycles_per_m,float alpha2_np_per_m,float aperture_m);
