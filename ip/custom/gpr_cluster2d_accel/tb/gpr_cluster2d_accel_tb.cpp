#include "gpr_cluster2d_accel.hpp"
#include <vector>
#include <iostream>
int main(){int X=8,Z=8;std::vector<ap_uint<8>>m(X*Z);std::vector<float>a(X*Z,1);std::vector<ap_uint<16>>l(X*Z);std::vector<ap_uint<32>>r(6);m[18]=m[19]=m[54]=1;gpr_cluster2d_accel(m.data(),a.data(),l.data(),r.data(),X,Z,65536,65536);int f=(r[0]!=3||r[1]!=2);if(!f)std::cout<<"PASS clustering\n";return f;}
