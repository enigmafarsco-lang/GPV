#include "gpr_cal_window.hpp"
#include <iostream>
int main(){
    hls::stream<axis32u16_t> x,c,y;
    axis32u16_t a,b; a.data=0;b.data=0;a.keep=b.keep=-1;a.strb=b.strb=-1;a.user=3;a.last=1;b.user=0;b.last=1;
    a.data.range(15,0)=(ap_uint<16>)(ap_int<16>)1000;
    a.data.range(31,16)=(ap_uint<16>)(ap_int<16>)-500;
    b.data.range(15,0)=(ap_uint<16>)(ap_int<16>)16384; // 0.5
    b.data.range(31,16)=0;
    x.write(a); c.write(b); gpr_cal_window(x,c,y);
    auto o=y.read(); int fail=0;
    if((ap_int<16>)o.data.range(15,0)!=500) ++fail;
    if((ap_int<16>)o.data.range(31,16)!=-250) ++fail;
    if(!o.last || (int)o.user!=3) ++fail;
    if(!fail) std::cout<<"PASS: calibration/window complex multiply\n";
    return fail;
}
