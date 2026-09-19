#include "gpr_power32.hpp"
extern "C" void gpr_power32(hls::stream<axis32u16_t>& s_axis, hls::stream<axis32p_t>& m_axis) {
#pragma HLS INTERFACE axis register_mode=both port=s_axis
#pragma HLS INTERFACE axis register_mode=both port=m_axis
#pragma HLS INTERFACE ap_ctrl_none port=return
    if(s_axis.empty()) return;
    axis32u16_t x=s_axis.read();
    ap_int<16> i=(ap_int<16>)x.data.range(15,0), q=(ap_int<16>)x.data.range(31,16);
    ap_uint<33> p=(ap_int<32>)i*i+(ap_int<32>)q*q;
    axis32p_t y; y.data=(p>0xffffffffULL)?0xffffffffu:(ap_uint<32>)p;
    y.keep=-1;y.strb=-1;y.user=x.user;y.last=x.last;
    m_axis.write(y);
}
