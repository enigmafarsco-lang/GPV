#include "gpr_sweep_scheduler.hpp"
#include <iostream>
int main(){
 hls::stream<axis32u16_t>tx;hls::stream<axis128_t>ctx;
 ap_uint<1>req=0,preq=0,done=0;ap_uint<8>sb=0;ap_uint<16>pid=0;
 gpr_sweep_scheduler(tx,ctx,4,2,2,8,2,0x010000000000ULL,0x001000000000LL,12000,1,1,1,req,sb,preq,pid,done);
 int f=!done,c=0;
 const int expected[16]={0,1,0,1,2,3,2,3,0,1,0,1,2,3,2,3};
 while(!ctx.empty()){auto w=ctx.read();if((int)w.data.range(63,48)!=expected[c])f++;c++;}
 if(c!=16)f++;
 int t=0;while(!tx.empty()){tx.read();t++;}if(t!=128)f++;
 if(!f)std::cout<<"PASS scheduler subband-major frame/context\n";return f;
}
