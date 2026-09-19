#include "gpr_kirchhoff_coherent_accel.hpp"
#include <vector>
#include <iostream>
int main(){int P=8,R=32,X=8,Z=8;std::vector<ap_uint<32>>b(P*R);std::vector<float>im(X*Z);ap_uint<32>w=0;w.range(15,0)=(ap_uint<16>)(ap_int<16>)10000;b[5*P+4]=w;gpr_kirchhoff_coherent_accel(b.data(),im.data(),P,R,X,Z,.1,.1,.1,0,0,0,1);float m=0;for(float v:im)if(v>m)m=v;int f=!(m>0);if(!f)std::cout<<"PASS coherent migration\n";return f;}
