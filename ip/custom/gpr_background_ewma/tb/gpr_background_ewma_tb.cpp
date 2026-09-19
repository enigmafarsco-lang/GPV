#include "gpr_background_ewma.hpp"
#include <iostream>
static axis32u16_t mk(int v,bool last){axis32u16_t w;w.data=0;w.keep=-1;w.strb=-1;w.user=0;w.last=last;w.data.range(15,0)=(ap_uint<16>)(ap_int<16>)v;return w;}
int main(){
    hls::stream<axis32u16_t> in,out;
    in.write(mk(1000,1)); gpr_background_ewma(in,out,16384,1,0); out.read();
    in.write(mk(1000,1)); gpr_background_ewma(in,out,16384,0,0);
    auto y=out.read(); int v=(ap_int<16>)y.data.range(15,0);
    int fail=(v<450 || v>550);
    if(!fail) std::cout<<"PASS: EWMA background state\n";
    return fail;
}
