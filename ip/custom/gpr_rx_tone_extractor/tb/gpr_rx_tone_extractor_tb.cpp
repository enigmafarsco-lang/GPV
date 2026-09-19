#include "gpr_rx_tone_extractor.hpp"
#include <cmath>
#include <iostream>
int main(){hls::stream<axis32u16_t>rx;hls::stream<axis128_t>ctx;hls::stream<axis32u32_t>out;const unsigned N=256;ap_uint<48>step=0x010000000000ULL;
axis128_t c;c.data=0;c.keep=-1;c.strb=-1;c.last=0;c.data.range(47,0)=step;c.data.range(63,48)=3;c.data.range(79,64)=2;c.data.range(87,80)=1;c.data[96]=1;ctx.write(c);
unsigned long long ph=0;for(unsigned n=0;n<N;n++){double a=6.2831853071795864769*(double)(ph&((1ULL<<48)-1))/(double)(1ULL<<48),psi=.7;int I=lround(10000*cos(a+psi)),Q=lround(10000*sin(a+psi));axis32u16_t w;w.data=0;w.keep=-1;w.strb=-1;w.user=0;w.last=n==N-1;w.data.range(15,0)=(ap_uint<16>)(ap_int<16>)I;w.data.range(31,16)=(ap_uint<16>)(ap_int<16>)Q;rx.write(w);ph=(ph+(unsigned long long)step)&((1ULL<<48)-1);}
gpr_rx_tone_extractor(rx,ctx,out,N,0);auto y=out.read();int I=(ap_int<16>)y.data.range(15,0),Q=(ap_int<16>)y.data.range(31,16);int f=(abs(I-7648)>180||abs(Q-6442)>180);if(!f)std::cout<<"PASS residual derotation/dwell\n";return f;}
