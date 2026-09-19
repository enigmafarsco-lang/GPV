#include "gpr_cfar2d_accel.hpp"
#include <vector>
#include <iostream>
int main(){int nx=16,nz=16;std::vector<float>im(nx*nz,1.0f);std::vector<ap_uint<8>>m(nx*nz);im[8*nx+8]=100;gpr_cfar2d_accel(im.data(),m.data(),nx,nz,1,3,3.0f);int f=!m[8*nx+8];if(!f)std::cout<<"PASS: 2D CFAR\n";return f;}
