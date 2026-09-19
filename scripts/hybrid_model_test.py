#!/usr/bin/env python3
import cmath, math, sys

def test_residual_derotation():
    n=512
    step=2*math.pi*0.071
    psi=0.63
    x=[10000*cmath.exp(1j*(step*k+psi)) for k in range(n)]
    raw=sum(x)/n
    der=sum(x[k]*cmath.exp(-1j*step*k) for k in range(n))/n
    assert abs(raw) < 300, f"raw residual unexpectedly coherent: {abs(raw)}"
    assert abs(abs(der)-10000) < 1e-6
    assert abs(cmath.phase(der)-psi) < 1e-9

def test_dwell_discard_contract():
    dwell=12288; discard=512
    assert dwell-discard == 11776 and dwell>discard

def test_sweep_counts():
    tones, pos, avg, dwell = 256, 200, 32, 12288
    contexts=tones*pos*avg
    tx_samples=contexts*dwell
    assert contexts == 1_638_400
    assert tx_samples == 20_132_659_200


def test_subband_major_retune_count():
    tones, avg, tps = 256, 32, 12
    n_sb=(tones+tps-1)//tps
    old=n_sb*avg
    new=n_sb
    assert n_sb == 22
    assert new == 22 and old == 704

def test_coherent_migration_phase():
    # Point target; phase-correct coherent sum must exceed incoherent wrong-sign sum.
    kbeta=5.0
    xs=[(i-16)*0.05 for i in range(33)]
    z=0.8
    samples=[]
    for x in xs:
        R=math.sqrt(z*z+x*x)
        samples.append(cmath.exp(-1j*2*math.pi*kbeta*R))
    good=sum(samples[i]*cmath.exp(1j*2*math.pi*kbeta*math.sqrt(z*z+xs[i]*xs[i])) for i in range(len(xs)))
    bad=sum(samples[i]*cmath.exp(-1j*2*math.pi*kbeta*math.sqrt(z*z+xs[i]*xs[i])) for i in range(len(xs)))
    assert abs(good) > 5*abs(bad), (abs(good),abs(bad))

def main():
    tests=[test_residual_derotation,test_dwell_discard_contract,test_sweep_counts,test_subband_major_retune_count,test_coherent_migration_phase]
    for t in tests:
        t(); print("PASS",t.__name__)
    print(f"Hybrid V3 model regression: {len(tests)}/{len(tests)} PASS")
if __name__=="__main__":
    main()
