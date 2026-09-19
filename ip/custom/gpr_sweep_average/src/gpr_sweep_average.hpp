#include <ap_int.h>
#include <hls_stream.h>
#include <ap_axi_sdata.h>
typedef ap_axiu<32,16,0,0> axis32u16_t;
typedef ap_axiu<32,32,0,0> axis32u32_t;
typedef ap_axiu<128,0,0,0> axis128_t;
static ap_int<16> gpr_sat16(ap_int<64> x) {
    if (x > 32767) return 32767;
    if (x < -32768) return -32768;
    return (ap_int<16>)x;
}

extern "C" void gpr_sweep_average(hls::stream<axis32u32_t>&s_axis,hls::stream<axis32u16_t>&m_axis,ap_uint<16>n_tones,ap_uint<8>n_averages);
