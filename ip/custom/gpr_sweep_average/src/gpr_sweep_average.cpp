#include "gpr_sweep_average.hpp"
#define GPR_MAX_TONES 4096
extern "C" void gpr_sweep_average(hls::stream<axis32u32_t>&s_axis,hls::stream<axis32u16_t>&m_axis,ap_uint<16>n_tones,ap_uint<8>n_averages){
#pragma HLS INTERFACE axis port=s_axis
#pragma HLS INTERFACE axis port=m_axis
#pragma HLS INTERFACE s_axilite port=n_tones bundle=control
#pragma HLS INTERFACE s_axilite port=n_averages bundle=control
#pragma HLS INTERFACE ap_ctrl_none port=return
static ap_int<48>ai[GPR_MAX_TONES],aq[GPR_MAX_TONES];
#pragma HLS BIND_STORAGE variable=ai type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=aq type=ram_t2p impl=bram
if(s_axis.empty())return;axis32u32_t w=s_axis.read();ap_uint<16>t=w.user.range(11,0);ap_uint<8>a=w.user.range(31,24);ap_int<16>i=(ap_int<16>)w.data.range(15,0),q=(ap_int<16>)w.data.range(31,16);
ap_int<48>si=(a==0)?i:ai[t]+i,sq=(a==0)?q:aq[t]+q;if(a==n_averages-1){axis32u16_t o;o.data=0;o.keep=-1;o.strb=-1;o.user=t;o.last=(t==n_tones-1);o.data.range(15,0)=(ap_uint<16>)gpr_sat16(si/(ap_int<48>)n_averages);o.data.range(31,16)=(ap_uint<16>)gpr_sat16(sq/(ap_int<48>)n_averages);m_axis.write(o);ai[t]=0;aq[t]=0;}else{ai[t]=si;aq[t]=sq;}}
