#include <ap_int.h>
#include <hls_stream.h>
#include <ap_axi_sdata.h>
typedef ap_axiu<32,16,0,0> axis32u16_t;
static ap_int<16> sat16(ap_int<40> x) {
    if (x > 32767) return 32767;
    if (x < -32768) return -32768;
    return (ap_int<16>)x;
}

typedef ap_axiu<16,0,0,0> axis16_t;
extern "C" void gpr_zero_pad_cfg(
    hls::stream<axis32u16_t>& s_axis,
    hls::stream<axis32u16_t>& m_axis,
    hls::stream<axis16_t>& m_axis_cfg,
    ap_uint<16> n_tones,
    ap_uint<16> n_fft,
    ap_uint<16> fft_config_word);
