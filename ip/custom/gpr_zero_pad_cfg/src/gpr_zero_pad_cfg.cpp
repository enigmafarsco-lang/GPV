#include "gpr_zero_pad_cfg.hpp"
extern "C" void gpr_zero_pad_cfg(
    hls::stream<axis32u16_t>& s_axis,
    hls::stream<axis32u16_t>& m_axis,
    hls::stream<axis16_t>& m_axis_cfg,
    ap_uint<16> n_tones,
    ap_uint<16> n_fft,
    ap_uint<16> fft_config_word) {
#pragma HLS INTERFACE axis register_mode=both port=s_axis
#pragma HLS INTERFACE axis register_mode=both port=m_axis
#pragma HLS INTERFACE axis register_mode=both port=m_axis_cfg
#pragma HLS INTERFACE s_axilite port=n_tones bundle=control
#pragma HLS INTERFACE s_axilite port=n_fft bundle=control
#pragma HLS INTERFACE s_axilite port=fft_config_word bundle=control
#pragma HLS INTERFACE ap_ctrl_none port=return
    axis16_t cfg; cfg.data=fft_config_word; cfg.keep=-1; cfg.strb=-1; cfg.last=1;
    m_axis_cfg.write(cfg);
frame:
    for (ap_uint<16> k=0;k<n_fft;++k) {
#pragma HLS PIPELINE II=1
        axis32u16_t out;
        if (k<n_tones) {
            out=s_axis.read();
        } else {
            out.data=0; out.keep=-1; out.strb=-1; out.user=k; out.last=0;
        }
        out.user=k; out.last=(k==n_fft-1);
        m_axis.write(out);
    }
}
