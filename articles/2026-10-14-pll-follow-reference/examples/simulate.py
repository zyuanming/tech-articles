#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original sampled phase PI teaching loop. Not a measured chip or complete PFD.
Phases in cycles, frequencies in cycles/second (Hz), times in seconds of the
intentionally slowed teaching model. No VCO rail limits or fixed-point effects.
"""
from pathlib import Path
import argparse,json,platform,hashlib
import numpy as np

def wrap(e):
    return (e+.5)%1-.5

def run(duration=30.,dt=.1,free=.8,kp=1.,ki=.5,initial_reference=.25,
        divide=1,ref_step_time=None,ref_step_size=0.,ref_phase_noise=None,
        local_frequency_noise=None):
    count=round(duration/dt)
    phase=0.;integral=0.;rows=[]
    for n in range(count+1):
        t=n*dt
        rfreq=1.+(ref_step_size if ref_step_time is not None and t>=ref_step_time else 0)
        ref=initial_reference+t+(ref_step_size*max(0.,t-ref_step_time) if ref_step_time is not None else 0)
        noise=0. if ref_phase_noise is None else float(ref_phase_noise(t,n))
        measured=ref+noise
        feedback=phase/divide
        error=wrap(measured-feedback)
        before_integral=integral
        integral+=ki*dt*error
        disturbance=0. if local_frequency_noise is None else float(local_frequency_noise(t,n))
        frequency=free+kp*error+integral+disturbance
        rows.append(dict(n=n,time=t,reference_phase=ref,measured_reference_phase=measured,
                         reference_frequency=rfreq,output_phase=phase,feedback_phase=feedback,
                         error=error,integral_before=before_integral,integral_after=integral,
                         proportional=kp*error,frequency=frequency,local_disturbance=disturbance))
        phase+=dt*frequency
    return rows

def array(rows,key):return np.array([r[key] for r in rows])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out)
    if out.exists() and any(out.iterdir()):raise SystemExit('Refusing to overwrite nonempty directory')
    out.mkdir(parents=True,exist_ok=True)
    mainrun=run();ponly=run(ki=0);multiplied=run(free=3.2,kp=4,ki=2,divide=4)
    # The two bandwidth comparisons use their own explicitly labeled timestep.
    fast=dict(kp=2.,ki=1.);slow=dict(kp=.4,ki=.04);dt=.02;duration=140.
    tracking={k:run(duration=80,dt=dt,ref_step_time=30,ref_step_size=.2,**g) for k,g in [('fast',fast),('slow',slow)]}
    # Deterministic sinusoidal disturbances make source/frequency/amplitude explicit.
    # Reference is a phase perturbation: .03 cycle amplitude, .8 cycles/s modulation.
    rn=lambda t,n:.03*np.sin(2*np.pi*.8*t)
    # Local oscillator is a frequency perturbation: .04 Hz amplitude, .08 Hz modulation.
    on=lambda t,n:.04*np.sin(2*np.pi*.08*t)
    noise_ref={k:run(duration=duration,dt=dt,ref_phase_noise=rn,**g) for k,g in [('fast',fast),('slow',slow)]}
    noise_local={k:run(duration=duration,dt=dt,local_frequency_noise=on,**g) for k,g in [('fast',fast),('slow',slow)]}
    alias=run(duration=1.,free=11.,initial_reference=0.)
    tests={}
    assert abs(mainrun[0]['error']-.25)<1e-14
    assert abs(mainrun[0]['integral_after']-.0125)<1e-14
    assert abs(mainrun[0]['frequency']-1.0625)<1e-14
    assert abs(mainrun[1]['error']-.24375)<1e-14
    assert abs(mainrun[1]['frequency']-1.0684375)<1e-14
    tests['main_final_error_cycles']=mainrun[-1]['error']
    tests['main_final_frequency_hz']=mainrun[-1]['frequency']
    tests['main_final_integral_hz']=mainrun[-1]['integral_after']
    tests['ponly_final_error_cycles']=ponly[-1]['error']
    tests['ponly_final_frequency_hz']=ponly[-1]['frequency']
    tests['divide4_final_output_frequency_hz']=multiplied[-1]['frequency']
    tests['phase_sample_alias_max_error']=float(max(abs(r['error']) for r in alias))
    A=np.array([[1-1*.1-.5*.1*.1,-.1],[.5*.1,1.]])
    eig=np.linalg.eigvals(A)
    tests['small_signal_update_eigenvalue_moduli']=abs(eig).tolist()
    assert abs(mainrun[-1]['error'])<1e-6 and abs(mainrun[-1]['frequency']-1)<1e-6
    assert abs(mainrun[-1]['integral_after']-.2)<1e-6
    assert abs(ponly[-1]['error']-.2)<1e-10
    assert abs(multiplied[-1]['frequency']-4)<1e-5
    assert tests['phase_sample_alias_max_error']<1e-12
    tests['noise_rms_cycles']={}
    for source,runs in [('reference_phase',noise_ref),('local_frequency',noise_local)]:
        tests['noise_rms_cycles'][source]={}
        for speed,rows in runs.items():
            sel=[r for r in rows if 100<=r['time']<125]
            errors=np.array([r['output_phase']-r['reference_phase'] for r in sel])
            tests['noise_rms_cycles'][source][speed]=float(np.std(errors))
    nr=tests['noise_rms_cycles'];assert nr['reference_phase']['slow']<nr['reference_phase']['fast']
    assert nr['local_frequency']['slow']>nr['local_frequency']['fast']
    def settle(rows):
        # Last time outside 0.01 Hz of the new target AFTER step, reported plus one dt.
        bad=[r['time'] for r in rows if r['time']>=30 and abs(r['frequency']-1.2)>.01]
        return (max(bad)+dt-30) if bad else 0.
    tests['tracking_settling_after_step_seconds_with_0_01_hz_band']={k:settle(v) for k,v in tracking.items()}
    result=dict(model='Sampled wrapped phase, original PI teaching loop, ideal frequency actuator',
                environment=dict(python=platform.python_version(),numpy=np.__version__),
                main_config=dict(dt=.1,reference_hz=1,free_hz=.8,kp=1,ki=.5,initial_reference_cycles=.25,divide=1),
                comparison_config=dict(dt=dt,fast=fast,slow=slow,reference_phase_disturbance=dict(amplitude_cycles=.03,modulation_hz=.8),local_frequency_disturbance=dict(amplitude_hz=.04,modulation_hz=.08),rms_window_seconds=[100,125]),
                main=mainrun,ponly=ponly,multiply4=multiplied,alias=alias,tests=tests)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    arrays={}
    for group,runs in [('tracking',tracking),('ref_noise',noise_ref),('local_noise',noise_local)]:
        for speed,rows in runs.items():
            for key in ['time','reference_phase','measured_reference_phase','reference_frequency','output_phase','frequency','error']:
                arrays[group+'_'+speed+'_'+key]=array(rows,key)
    np.savez_compressed(out/'comparisons.npz',**arrays)
    (out/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [out/'results.json',out/'comparisons.npz']},indent=2)+'\n')
    print(json.dumps(tests,indent=2))

if __name__=='__main__':main()
