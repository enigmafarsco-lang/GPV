#include "gpr_zero_pad_cfg.hpp"
#include <iostream>
int main(){
    hls::stream<axis32u16_t> in,out; hls::stream<axis16_t> cfg;
    for(int k=0;k<3;++k){ axis32u16_t w;w.data=k+1;w.keep=-1;w.strb=-1;w.user=k;w.last=(k==2);in.write(w);}
    gpr_zero_pad_cfg(in,out,cfg,3,8,0x1234);
    int fail=0; if(cfg.read().data!=0x1234) ++fail;
    for(int k=0;k<8;++k){auto w=out.read(); if((unsigned)w.data!=(unsigned)(k<3?k+1:0))++fail; if((bool)w.last!=(k==7))++fail;}
    if(!fail) std::cout<<"PASS: zero pad and FFT config\n";
    return fail;
}
