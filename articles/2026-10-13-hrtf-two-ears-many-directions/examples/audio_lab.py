"""MIT-licensed teaching renderer. Uses cited MIT KEMAR HRIR data, not a new recording.
Requires Python 3 and NumPy. Writes generated results and WAVs beside this file.
The four input WAVs in ../originals retain MIT Media Laboratory's 1994 terms.
"""
from pathlib import Path
import hashlib,json,platform,wave
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
FS=44100
SEED=20261013
FILES={'front':'H0e000a.wav','right':'H0e090a.wav','back':'H0e180a.wav','up40':'H40e000a.wav'}

def read_hrir(name):
    with wave.open(str(ROOT/'originals'/name),'rb') as f:
        assert f.getnchannels()==2 and f.getsampwidth()==2 and f.getframerate()==FS and f.getnframes()==128
        return np.frombuffer(f.readframes(128),dtype='<i2').reshape(-1,2).astype(np.float64)/32768

def convolve_slow(x,h):
    out=[0.]*(len(x)+len(h)-1)
    for i,a in enumerate(x):
        for k,b in enumerate(h):out[i+k]+=a*b
    return out

def write_wav(name,signal):
    assert signal.ndim==2 and signal.shape[1]==2
    assert np.isfinite(signal).all() and np.abs(signal).max()<1
    raw=np.rint(signal*32767).astype('<i2').tobytes()
    with wave.open(str(HERE/name),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(FS);f.writeframes(raw)
    with wave.open(str(HERE/name),'rb') as f:
        assert f.getnframes()==len(signal) and f.getnchannels()==2 and f.getframerate()==FS
        decoded=np.frombuffer(f.readframes(len(signal)),dtype='<i2').reshape(-1,2).astype(float)/32767
    assert np.max(np.abs(decoded-signal))<=.5/32767+1e-15
    return {'frames':len(signal),'seconds':len(signal)/FS,'peak_pcm_fraction':float(np.abs(decoded).max()),'bytes':(HERE/name).stat().st_size,'sha256':hashlib.sha256((HERE/name).read_bytes()).hexdigest()}

def test():
    assert np.allclose(convolve_slow([1,2,0],[1,.5]),[1,2.5,1,0])
    rng=np.random.default_rng(123456);cases=0;maximum=0.
    for n in (1,2,7,31):
        for m in (1,2,5,17):
            for _ in range(50):
                x=rng.normal(size=n);h=rng.normal(size=m)
                error=float(np.max(np.abs(np.convolve(x,h)-convolve_slow(x,h))))
                assert error<1e-12;maximum=max(maximum,error);cases+=1
    for name in FILES.values():
        h=read_hrir(name)
        for c in range(2):assert np.array_equal(np.convolve([1.],h[:,c]),h[:,c])
    return {'hand_example':[1,2.5,1,0],'slow_vs_numpy_cases':cases,'max_absolute_error':maximum,'unit_impulse_reproduces_four_stereo_filters':True}

def run():
    responses={key:read_hrir(name) for key,name in FILES.items()}
    assert np.array_equal(responses['front'][:,0],responses['front'][:,1])
    assert np.array_equal(responses['back'][:,0],responses['back'][:,1])
    assert np.array_equal(responses['up40'][:,0],responses['up40'][:,1])
    rng=np.random.default_rng(SEED);dry=np.zeros(FS*2);burst=rng.uniform(-1,1,round(FS*.09))*np.hanning(round(FS*.09))
    for second in (.2,.65,1.1,1.55):start=round(FS*second);dry[start:start+len(burst)]+=burst
    outputs={key:np.column_stack([np.convolve(dry,h[:,ear]) for ear in range(2)]) for key,h in responses.items()}
    outputs['dry']=np.column_stack([dry,dry])
    # Preserve relative left/right and direction levels: one shared gain for every file.
    gain=.28/max(float(np.abs(x).max()) for x in outputs.values())
    audio={key:write_wav(key+'.wav',x*gain) for key,x in outputs.items()}
    analysis={};freq=np.linspace(0,16000,321);indices=np.arange(128)
    for key,h in responses.items():
        peaks=np.argmax(np.abs(h),axis=0)
        onsets=[int(np.flatnonzero(np.abs(h[:,c])>=.05*np.max(np.abs(h[:,c])))[0]) for c in range(2)]
        rms=np.sqrt(np.mean(h*h,axis=0))
        spectrum=np.exp(-2j*np.pi*freq[:,None]*indices/FS)@h
        # Common unit reference, NOT sound pressure level and not separate per-ear normalization.
        db=20*np.log10(np.maximum(np.abs(spectrum),1e-8))
        analysis[key]={'file':FILES[key],'frames':128,'peak_indices_L_R':peaks.tolist(),'peak_difference_ms_L_minus_R':float((peaks[0]-peaks[1])/FS*1000),'onset_5percent_indices_L_R':onsets,'onset_5percent_difference_ms_L_minus_R':(onsets[0]-onsets[1])/FS*1000,'rms_L_R':rms.tolist(),'rms_ratio_R_over_L':float(rms[1]/rms[0]),'energy_ratio_db_R_over_L':float(20*np.log10(rms[1]/rms[0])),'samples_L_R':h.tolist(),'frequencies_hz':freq.tolist(),'magnitude_db_L_R':db.tolist()}
    result={'python':platform.python_version(),'numpy':np.__version__,'sample_rate':FS,'seed':SEED,'input':'synthetic 90ms windowed-noise burst repeated at .2/.65/1.1/1.55s; not footsteps or recording','hrir_source':'Bill Gardner and Keith Martin, MIT Media Laboratory, 1994 compact data; derived symmetrical small-pinna set; speaker-equalized','shared_audio_gain':gain,'tests':test(),'audio':audio,'analysis':analysis,'cautions':['Maximum-absolute-peak delay is not a rigorous ITD estimate','5%-of-own-peak onset uses an explicit threshold, not a universal auditory timing measure','dB values use a digital filter reference, not dB SPL','No subjective listening or new acoustic measurement claimed','All audio files use one shared stereo gain; headphones not individually equalized']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'tests':result['tests'],'shared_audio_gain':gain,'audio':audio,'summary':{k:{n:v for n,v in d.items() if n not in ('samples_L_R','frequencies_hz','magnitude_db_L_R')} for k,d in analysis.items()}},indent=2))
if __name__=='__main__':run()
