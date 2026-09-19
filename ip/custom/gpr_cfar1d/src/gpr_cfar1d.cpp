#include "gpr_cfar1d.hpp"
#define MAX_BINS 4096
extern "C" void gpr_cfar1d(
    hls::stream<axis32p_t>& s_axis,
    hls::stream<axis64d_t>& m_axis,
    ap_uint<16> n_bins,
    ap_uint<8> guard_cells,
    ap_uint<8> ref_cells,
    ap_uint<24> alpha_q16) {
#pragma HLS INTERFACE axis register_mode=both port=s_axis
#pragma HLS INTERFACE axis register_mode=both port=m_axis
#pragma HLS INTERFACE s_axilite port=n_bins bundle=control
#pragma HLS INTERFACE s_axilite port=guard_cells bundle=control
#pragma HLS INTERFACE s_axilite port=ref_cells bundle=control
#pragma HLS INTERFACE s_axilite port=alpha_q16 bundle=control
#pragma HLS INTERFACE ap_ctrl_none port=return
    static ap_uint<32> p[MAX_BINS];
#pragma HLS BIND_STORAGE variable=p type=ram_t2p impl=bram
load:
    for(ap_uint<16> i=0;i<n_bins;++i){
#pragma HLS PIPELINE II=1
        p[i]=s_axis.read().data;
    }
detect:
    for(ap_uint<16> i=0;i<n_bins;++i){
        ap_uint<64> sum=0; ap_uint<16> cnt=0;
        int lo0=(int)i-(int)guard_cells-(int)ref_cells;
        int lo1=(int)i-(int)guard_cells-1;
        int hi0=(int)i+(int)guard_cells+1;
        int hi1=(int)i+(int)guard_cells+(int)ref_cells;
refloop:
        for(int k=0;k<MAX_BINS;++k){
#pragma HLS PIPELINE II=1
            if(k>hi1) break;
            bool use=(k>=lo0 && k<=lo1)||(k>=hi0 && k<=hi1);
            if(use && k>=0 && k<(int)n_bins){sum+=p[k];cnt++;}
        }
        ap_uint<32> mean=(cnt? (ap_uint<32>)(sum/cnt):0);
        ap_uint<56> prod=(ap_uint<56>)mean*alpha_q16;
        ap_uint<32> thr=(ap_uint<32>)(prod>>16);
        bool det=(p[i]>thr && cnt>0);
        axis64d_t y; y.data=0;
        y.data.range(31,0)=p[i];
        y.data.range(62,32)=thr.range(30,0);
        y.data[63]=det;
        y.keep=-1;y.strb=-1;y.user=i;y.last=(i==n_bins-1);
        m_axis.write(y);
    }
}
