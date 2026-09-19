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

extern "C" void gpr_sweep_scheduler(
    hls::stream<axis32u16_t>& m_axis_tx,
    hls::stream<axis128_t>& m_axis_ctx,
    ap_uint<16> n_tones, ap_uint<16> n_positions, ap_uint<8> n_averages,
    ap_uint<32> dwell_samples, ap_uint<16> tones_per_subband,
    ap_uint<48> residual_step0, ap_int<48> residual_step_delta,
    ap_int<16> amplitude_q15, ap_uint<1> system_ready, ap_uint<1> sb_ack, ap_uint<1> pos_ack,
    ap_uint<1>& sb_req, ap_uint<8>& sb_id, ap_uint<1>& pos_req, ap_uint<16>& pos_id, ap_uint<1>& frame_done);
