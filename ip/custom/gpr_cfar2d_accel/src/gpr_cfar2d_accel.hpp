#include <ap_int.h>
extern "C" void gpr_cfar2d_accel(
    const float* image,
    ap_uint<8>* mask,
    int nx,
    int nz,
    int guard,
    int ref,
    float alpha);
