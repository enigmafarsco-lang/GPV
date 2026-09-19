#include <ap_int.h>
#include <hls_stream.h>
#include <ap_axi_sdata.h>
typedef ap_axiu<32,16,0,0> axis32u16_t;
static ap_int<16> sat16(ap_int<40> x) {
    if (x > 32767) return 32767;
    if (x < -32768) return -32768;
    return (ap_int<16>)x;
}

extern "C" void gpr_cal_window(
    hls::stream<axis32u16_t>& s_axis,
    hls::stream<axis32u16_t>& s_axis_coef,
    hls::stream<axis32u16_t>& m_axis);
