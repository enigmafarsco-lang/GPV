#include "gpr_cluster2d_accel.hpp"
#define MAXLAB 512
static ap_uint<16> rt(ap_uint<16>x,ap_uint<16>*p){int g=0;while(x&&p[x]!=x&&g<MAXLAB){x=p[x];g++;}return x;}
extern "C" void gpr_cluster2d_accel(const ap_uint<8>*m,const float*a,ap_uint<16>*lab,ap_uint<32>*rep,int nx,int nz,ap_uint<32>dxq,ap_uint<32>dzq){
#pragma HLS INTERFACE m_axi port=m offset=slave bundle=g0
#pragma HLS INTERFACE m_axi port=a offset=slave bundle=g1
#pragma HLS INTERFACE m_axi port=lab offset=slave bundle=g2
#pragma HLS INTERFACE m_axi port=rep offset=slave bundle=g3
#pragma HLS INTERFACE s_axilite port=m bundle=control
#pragma HLS INTERFACE s_axilite port=a bundle=control
#pragma HLS INTERFACE s_axilite port=lab bundle=control
#pragma HLS INTERFACE s_axilite port=rep bundle=control
#pragma HLS INTERFACE s_axilite port=nx bundle=control
#pragma HLS INTERFACE s_axilite port=nz bundle=control
#pragma HLS INTERFACE s_axilite port=dxq bundle=control
#pragma HLS INTERFACE s_axilite port=dzq bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
ap_uint<16>p[MAXLAB];ap_uint<32>cnt[MAXLAB];float pk[MAXLAB];ap_uint<16>px[MAXLAB],pz[MAXLAB];for(int i=0;i<MAXLAB;i++){p[i]=i;cnt[i]=0;pk[i]=-1;px[i]=pz[i]=0;}ap_uint<16>next=1;ap_uint<32>hits=0;
for(int z=0;z<nz;z++)for(int x=0;x<nx;x++){int id=z*nx+x;if(!m[id]){lab[id]=0;continue;}hits++;ap_uint<16>best=0,n[4]={0,0,0,0};if(z&&x)n[0]=lab[(z-1)*nx+x-1];if(z)n[1]=lab[(z-1)*nx+x];if(z&&x+1<nx)n[2]=lab[(z-1)*nx+x+1];if(x)n[3]=lab[z*nx+x-1];for(int k=0;k<4;k++)if(n[k]){ap_uint<16>r=rt(n[k],p);if(!best||r<best)best=r;}if(!best){best=next<MAXLAB?next++:MAXLAB-1;p[best]=best;}for(int k=0;k<4;k++)if(n[k]){ap_uint<16>r=rt(n[k],p);if(r!=best){ap_uint<16>lo=r<best?r:best,hi=r<best?best:r;p[hi]=lo;best=lo;}}lab[id]=best;}
for(int z=0;z<nz;z++)for(int x=0;x<nx;x++){int id=z*nx+x;ap_uint<16>l=lab[id];if(!l)continue;ap_uint<16>r=rt(l,p);lab[id]=r;cnt[r]++;if(a[id]>pk[r]){pk[r]=a[id];px[r]=x;pz[r]=z;}}
ap_uint<32>nc=0,sd=0,sx=0,dmin=0,dmax=0;bool first=true;for(int l=1;l<MAXLAB;l++)if(cnt[l]){nc++;ap_uint<32>d=(ap_uint<32>)pz[l]*dzq,x=(ap_uint<32>)px[l]*dxq;sd+=d;sx+=x;if(first){dmin=dmax=d;first=false;}else{if(d<dmin)dmin=d;if(d>dmax)dmax=d;}}rep[0]=hits;rep[1]=nc;rep[2]=nc?sd/nc:0;rep[3]=nc?sx/nc:0;rep[4]=dmin;rep[5]=dmax;}
