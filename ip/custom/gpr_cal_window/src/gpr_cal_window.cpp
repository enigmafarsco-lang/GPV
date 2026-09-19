#include "gpr_cal_window.hpp"
extern "C" void gpr_cal_window(
    hls::stream<axis32u16_t>& s_axis,
    hls::stream<axis32u16_t>& s_axis_coef,
    hls::stream<axis32u16_t>& m_axis) {
#pragma HLS INTERFACE axis register_mode=both port=s_axis
#pragma HLS INTERFACE axis register_mode=both port=s_axis_coef
#pragma HLS INTERFACE axis register_mode=both port=m_axis
#pragma HLS INTERFACE ap_ctrl_none port=return
    if (s_axis.empty() || s_axis_coef.empty()) return;
    axis32u16_t x=s_axis.read();
    axis32u16_t c=s_axis_coef.read();
    ap_int<16> xr=(ap_int<16>)x.data.range(15,0);
    ap_int<16> xi=(ap_int<16>)x.data.range(31,16);
    ap_int<16> cr=(ap_int<16>)c.data.range(15,0);
    ap_int<16> ci=(ap_int<16>)c.data.range(31,16);
    ap_int<40> rr=(ap_int<32>)xr*cr-(ap_int<32>)xi*ci;
    ap_int<40> ii=(ap_int<32>)xr*ci+(ap_int<32>)xi*cr;
    axis32u16_t y;
    y.data.range(15,0)=(ap_uint<16>)sat16(rr>>15);
    y.data.range(31,16)=(ap_uint<16>)sat16(ii>>15);
    y.keep=x.keep; y.strb=x.strb; y.user=x.user; y.last=x.last;
    m_axis.write(y);
}
