#include "gpr_background_ewma.hpp"
#define GPR_MAX_BINS 4096
extern "C" void gpr_background_ewma(
    hls::stream<axis32u16_t>& s_axis,
    hls::stream<axis32u16_t>& m_axis,
    ap_uint<16> alpha_q15,
    ap_uint<1> learn_only,
    ap_uint<1> bypass) {
#pragma HLS INTERFACE axis register_mode=both port=s_axis
#pragma HLS INTERFACE axis register_mode=both port=m_axis
#pragma HLS INTERFACE s_axilite port=alpha_q15 bundle=control
#pragma HLS INTERFACE s_axilite port=learn_only bundle=control
#pragma HLS INTERFACE s_axilite port=bypass bundle=control
#pragma HLS INTERFACE ap_ctrl_none port=return
    static ap_int<24> bg_i[GPR_MAX_BINS];
    static ap_int<24> bg_q[GPR_MAX_BINS];
#pragma HLS BIND_STORAGE variable=bg_i type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=bg_q type=ram_t2p impl=bram
    static ap_uint<12> bin=0;
    if (s_axis.empty()) return;
    axis32u16_t x=s_axis.read();
    ap_int<16> xi=(ap_int<16>)x.data.range(15,0);
    ap_int<16> xq=(ap_int<16>)x.data.range(31,16);
    ap_int<24> bi=bg_i[bin], bq=bg_q[bin];
    ap_uint<16> one_minus=(ap_uint<16>)(32768-alpha_q15);
    ap_int<48> ni=(ap_int<40>)alpha_q15*bi+(ap_int<40>)one_minus*xi;
    ap_int<48> nq=(ap_int<40>)alpha_q15*bq+(ap_int<40>)one_minus*xq;
    bg_i[bin]=(ap_int<24>)(ni>>15);
    bg_q[bin]=(ap_int<24>)(nq>>15);
    ap_int<24> yi=bypass?xi:(learn_only?0:(ap_int<24>)xi-bi);
    ap_int<24> yq=bypass?xq:(learn_only?0:(ap_int<24>)xq-bq);
    axis32u16_t y=x;
    y.data.range(15,0)=(ap_uint<16>)sat16(yi);
    y.data.range(31,16)=(ap_uint<16>)sat16(yq);
    m_axis.write(y);
    bin = x.last ? 0 : (ap_uint<12>)(bin+1);
}
