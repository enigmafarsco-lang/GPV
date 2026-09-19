#include <ap_int.h>
extern "C" void gpr_cluster2d_accel(const ap_uint<8>*mask,const float*magnitude,ap_uint<16>*labels,ap_uint<32>*report,int nx,int nz,ap_uint<32>dx_q16,ap_uint<32>dz_q16);
