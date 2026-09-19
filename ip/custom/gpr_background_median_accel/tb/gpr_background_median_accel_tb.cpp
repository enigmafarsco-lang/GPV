#include "gpr_background_median_accel.hpp"
#include <vector>
#include <iostream>
int main(){int P=5,R=2;std::vector<ap_uint<32>>a(P*R),o(P*R);for(int z=0;z<R;z++)for(int p=0;p<P;p++){ap_uint<32>w=0;w.range(15,0)=(ap_uint<16>)(ap_int<16>)(100+p+(p==2?1000:0));a[z*P+p]=w;}gpr_background_median_accel(a.data(),o.data(),P,R);ap_int<16>x=(ap_int<16>)o[2].range(15,0);int f=x<900;if(!f)std::cout<<"PASS median background\n";return f;}
