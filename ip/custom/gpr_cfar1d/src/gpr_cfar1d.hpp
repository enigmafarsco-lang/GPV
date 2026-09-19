#include <ap_int.h>
#include <hls_stream.h>
#include <ap_axi_sdata.h>
typedef ap_axiu<32,16,0,0> axis32p_t;
typedef ap_axiu<64,16,0,0> axis64d_t;
extern "C" void gpr_cfar1d(
    hls::stream<axis32p_t>& s_axis,
    hls::stream<axis64d_t>& m_axis,
    ap_uint<16> n_bins,
    ap_uint<8> guard_cells,
    ap_uint<8> ref_cells,
    ap_uint<24> alpha_q16);
