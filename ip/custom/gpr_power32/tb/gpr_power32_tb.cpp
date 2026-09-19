#include "gpr_power32.hpp"
#include <iostream>
int main(){hls::stream<axis32u16_t> i;hls::stream<axis32p_t> o;axis32u16_t w;w.data=0;w.keep=-1;w.strb=-1;w.user=2;w.last=1;w.data.range(15,0)=(ap_uint<16>)(ap_int<16>)3;w.data.range(31,16)=(ap_uint<16>)(ap_int<16>)4;i.write(w);gpr_power32(i,o);auto y=o.read();int f=(y.data!=25||!y.last||(int)y.user!=2);if(!f)std::cout<<"PASS: power\n";return f;}
