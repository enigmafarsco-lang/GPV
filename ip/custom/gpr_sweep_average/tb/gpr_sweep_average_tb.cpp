#include "gpr_sweep_average.hpp"
#include <iostream>
int main(){hls::stream<axis32u32_t>i;hls::stream<axis32u16_t>o;for(int a=0;a<4;a++)for(int t=0;t<3;t++){axis32u32_t w;w.data=0;w.keep=-1;w.strb=-1;w.last=t==2;w.user=0;w.user.range(11,0)=t;w.user.range(31,24)=a;w.data.range(15,0)=(ap_uint<16>)(ap_int<16>)(100+t);w.data.range(31,16)=(ap_uint<16>)(ap_int<16>)-20;i.write(w);gpr_sweep_average(i,o,3,4);}int f=0;for(int t=0;t<3;t++){auto w=o.read();if((ap_int<16>)w.data.range(15,0)!=100+t)f++;}if(!f)std::cout<<"PASS sweep avg\n";return f;}
