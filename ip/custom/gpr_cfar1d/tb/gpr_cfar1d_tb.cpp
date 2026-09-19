#include "gpr_cfar1d.hpp"
#include <iostream>
int main(){
 hls::stream<axis32p_t> in;hls::stream<axis64d_t> out;
 for(int i=0;i<32;++i){axis32p_t w;w.data=(i==16)?10000:100;w.keep=-1;w.strb=-1;w.user=i;w.last=(i==31);in.write(w);}
 gpr_cfar1d(in,out,32,1,4,2<<16);
 int dets=0;for(int i=0;i<32;++i){auto y=out.read();if(y.data[63])dets++;}
 int fail=(dets<1);if(!fail)std::cout<<"PASS: 1D CFAR\n";return fail;
}
