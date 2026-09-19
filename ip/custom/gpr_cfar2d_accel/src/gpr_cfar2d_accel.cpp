#include "gpr_cfar2d_accel.hpp"
extern "C" void gpr_cfar2d_accel(
    const float* image, ap_uint<8>* mask, int nx, int nz, int guard, int ref, float alpha) {
#pragma HLS INTERFACE m_axi port=image offset=slave bundle=gmem0 max_read_burst_length=64
#pragma HLS INTERFACE m_axi port=mask offset=slave bundle=gmem1 max_write_burst_length=64
#pragma HLS INTERFACE s_axilite port=image bundle=control
#pragma HLS INTERFACE s_axilite port=mask bundle=control
#pragma HLS INTERFACE s_axilite port=nx bundle=control
#pragma HLS INTERFACE s_axilite port=nz bundle=control
#pragma HLS INTERFACE s_axilite port=guard bundle=control
#pragma HLS INTERFACE s_axilite port=ref bundle=control
#pragma HLS INTERFACE s_axilite port=alpha bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
z:
    for(int iz=0;iz<nz;++iz){
x:
        for(int ix=0;ix<nx;++ix){
            float sum=0; int cnt=0;
            for(int dz=-16;dz<=16;++dz){
                for(int dx=-16;dx<=16;++dx){
#pragma HLS PIPELINE II=1
                    if(dx<-ref-guard || dx>ref+guard || dz<-ref-guard || dz>ref+guard) continue;
                    int ax=dx<0?-dx:dx, az=dz<0?-dz:dz;
                    if(ax<=guard && az<=guard) continue;
                    if(ax>guard+ref || az>guard+ref) continue;
                    int xx=ix+dx, zz=iz+dz;
                    if(xx>=0&&xx<nx&&zz>=0&&zz<nz){sum+=image[zz*nx+xx];cnt++;}
                }
            }
            float thr=(cnt?alpha*(sum/cnt):0.0f);
            mask[iz*nx+ix]=(image[iz*nx+ix]>thr && cnt>0)?1:0;
        }
    }
}
