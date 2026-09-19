#include "gpr_kirchhoff_coherent_accel.hpp"
extern "C" void gpr_kirchhoff_coherent_accel(const ap_uint<32>*b,float*im,int np,int nr,int nx,int nz,float dx,float dz,float dr,float ro,float kb,float a2,float ap){
#pragma HLS INTERFACE m_axi port=b offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=im offset=slave bundle=gmem1
#pragma HLS INTERFACE s_axilite port=b bundle=control
#pragma HLS INTERFACE s_axilite port=im bundle=control
#pragma HLS INTERFACE s_axilite port=np bundle=control
#pragma HLS INTERFACE s_axilite port=nr bundle=control
#pragma HLS INTERFACE s_axilite port=nx bundle=control
#pragma HLS INTERFACE s_axilite port=nz bundle=control
#pragma HLS INTERFACE s_axilite port=dx bundle=control
#pragma HLS INTERFACE s_axilite port=dz bundle=control
#pragma HLS INTERFACE s_axilite port=dr bundle=control
#pragma HLS INTERFACE s_axilite port=ro bundle=control
#pragma HLS INTERFACE s_axilite port=kb bundle=control
#pragma HLS INTERFACE s_axilite port=a2 bundle=control
#pragma HLS INTERFACE s_axilite port=ap bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
for(int z0=0;z0<nz;z0++){float z=(z0+1)*dz;for(int x0=0;x0<nx;x0++){float ar=0,ai=0;int nc=0;for(int p=0;p<np;p++){
#pragma HLS PIPELINE II=1
float xs=p*dx-x0*dx;if(hls::fabsf(xs)>ap)continue;float R=hls::sqrtf(z*z+xs*xs),fb=(R+ro)/dr;int r=(int)hls::floorf(fb);float fr=fb-r;if(r<0||r+1>=nr)continue;ap_uint<32>w0=b[r*np+p],w1=b[(r+1)*np+p];ap_int<16>r0=(ap_int<16>)w0.range(15,0),i0=(ap_int<16>)w0.range(31,16),r1=(ap_int<16>)w1.range(15,0),i1=(ap_int<16>)w1.range(31,16);float vr=(1-fr)*(float)r0+fr*(float)r1,vi=(1-fr)*(float)i0+fr*(float)i1;float wt=z/(R+1e-6f)/hls::sqrtf(R+1e-6f)*hls::expf(-a2*hls::fmaxf(0.0f,R-z));float u=xs/(ap+1e-9f);wt*=0.5f*(1+hls::cosf(3.14159265f*u));float ph=6.2831853f*kb*R,c=hls::cosf(ph),s=hls::sinf(ph);ar+=wt*(vr*c-vi*s);ai+=wt*(vr*s+vi*c);nc++;}im[z0*nx+x0]=nc?hls::sqrtf(ar*ar+ai*ai)/hls::sqrtf((float)nc):0;}}}
