#include "gpr_background_median_accel.hpp"
#define MAX_POS 512
static ap_int<16> medv(ap_int<16>*a,int n){for(int j=1;j<n;j++){ap_int<16>k=a[j];int i=j-1;while(i>=0&&a[i]>k){a[i+1]=a[i];i--;}a[i+1]=k;}if(n&1)return a[n/2];ap_int<17>s=(ap_int<17>)a[n/2-1]+a[n/2];return (ap_int<16>)(s>>1);}
extern "C" void gpr_background_median_accel(const ap_uint<32>*in,ap_uint<32>*out,int np,int nr){
#pragma HLS INTERFACE m_axi port=in offset=slave bundle=g0
#pragma HLS INTERFACE m_axi port=out offset=slave bundle=g1
#pragma HLS INTERFACE s_axilite port=in bundle=control
#pragma HLS INTERFACE s_axilite port=out bundle=control
#pragma HLS INTERFACE s_axilite port=np bundle=control
#pragma HLS INTERFACE s_axilite port=nr bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
ap_int<16>r[MAX_POS],q[MAX_POS];for(int z=0;z<nr;z++){for(int p=0;p<np;p++){ap_uint<32>w=in[z*np+p];r[p]=(ap_int<16>)w.range(15,0);q[p]=(ap_int<16>)w.range(31,16);}ap_int<16>mr=medv(r,np),mq=medv(q,np);for(int p=0;p<np;p++){ap_uint<32>w=in[z*np+p];ap_int<17>dr=(ap_int<16>)w.range(15,0)-mr,dq=(ap_int<16>)w.range(31,16)-mq;ap_int<16>sr=dr>32767?32767:(dr<-32768?-32768:(ap_int<16>)dr),sq=dq>32767?32767:(dq<-32768?-32768:(ap_int<16>)dq);ap_uint<32>o=0;o.range(15,0)=(ap_uint<16>)sr;o.range(31,16)=(ap_uint<16>)sq;out[z*np+p]=o;}}}
