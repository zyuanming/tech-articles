"""Compute every numerical data series used in the article. CC0-1.0."""
from pathlib import Path
import json,math,platform
from srgb import *
P=Path(__file__).resolve().parent

def compute():
    xs=[i/1000 for i in range(1001)]
    roundtrip=max(abs(encode(decode(x))-x) for x in xs)
    assert roundtrip<3e-8
    assert [q8(encode(decode(i/255))) for i in range(256)]==list(range(256))
    assert all(decode(a)<decode(b) for a,b in zip(xs,xs[1:]))
    pairs=0
    for a in range(0,256,17):
        for b in range(0,256,17):
            for t in [0,.25,.5,.75,1]:
                y=blend(a/255,b/255,t);assert min(a,b)/255-1e-12<=y<=max(a,b)/255+1e-12;pairs+=1
    thresholds=[]
    for name,fn,back,boundary in [('decode',decode,encode,.04045),('encode',encode,decode,.0031308)]:
        for x in [boundary-1e-10,boundary,boundary+1e-10]:
            y=fn(x);error=abs(back(y)-x);assert error<4e-8
            thresholds.append(dict(direction=name,input=x,output=y,roundtrip_error=error))
    sample=[0,32,64,128,188,255]
    main={'S_half':.5,'L_from_S_half':decode(.5),'S_from_L_half':encode(.5),'code_direct':q8(.5),'code_linear':q8(encode(.5)),'L_from_128':decode(128/255),'L_from_188':decode(188/255),'no_encode':q8(.5),'double_encode':q8(encode(encode(.5)))}
    grad={'direct':[q8(i/255) for i in range(256)],'linear':[q8(encode(i/255)) for i in range(256)]}
    dark_x=[.02*i/255 for i in range(256)]
    dark={'linear8':[q8(encode(q8(x)/255)) for x in dark_x],'srgb8':[q8(encode(x)) for x in dark_x]}
    dark['linear_levels']=len(set(dark['linear8']));dark['srgb_levels']=len(set(dark['srgb8']))
    errors=[abs(decode(x)-x**2.2) for x in xs]
    kernel=[.25,.5,.25];edge=[0]*8+[1]*8
    blurred=[sum(kernel[j]*edge[min(len(edge)-1,max(0,i+j-1))] for j in range(3)) for i in range(len(edge))]
    redgreen={'encoded':[q8(x) for x in average_rgb([(1,0,0),(0,1,0)],False)],'linear':[q8(x) for x in average_rgb([(1,0,0),(0,1,0)],True)]}
    # Original 48x48 checker/diagonal test image, exact 4x4 area average to12x12.
    side=48;source=[]
    for y in range(side):
        row=[]
        for x in range(side):
            if y<24:v=255 if (x+y)%2 else 0
            else:v=255 if x>y-24 else 0
            row.append(v)
        source.append(row)
    small={k:[] for k in ['encoded','linear']}
    for y in range(12):
        for key in small:small[key].append([])
        for x in range(12):
            vals=[source[4*y+j][4*x+i]/255 for j in range(4) for i in range(4)]
            small['encoded'][y].append(q8(sum(vals)/16))
            small['linear'][y].append(q8(encode(sum(map(decode,vals))/16)))
    # W3C13.4 declared red->transparent black->blue, encoded-sRGB interpolation.
    refs={'premult':[],'straight':[]}
    for i in range(257):
        t=i/256;u=2*t if t<=.5 else 2*(1-t);base=[1,0,0] if t<=.5 else [0,0,1];alpha=1-u
        for key in refs:
            rgb=base if key=='premult' else [v*alpha for v in base]
            refs[key].append([q8(alpha*v+1-alpha) for v in rgb])
    return dict(python=platform.python_version(),threshold_checks=thresholds,main=main,samples=[{'code':i,'S':i/255,'L':decode(i/255)} for i in sample],curve=[{'S':x,'L':decode(x)} for x in xs],gradients=grad,dark=dark,approx={'max_error':max(errors),'at_S':xs[errors.index(max(errors))],'samples':[{'S':x,'exact':decode(x),'power22':x**2.2} for x in [.02,.1,.5,.8]]},edge={'input':edge,'weights':kernel,'linear_values':blurred,'encoded_codes':[q8(v) for v in blurred],'linear_codes':[q8(encode(v)) for v in blurred]},redgreen=redgreen,alpha=[{'a':a,'direct_code':q8(a),'linear_code':q8(encode(a))} for a in [.25,.5,.75]],premult={'mid_good':[q8(x) for x in over_white_premult(.5)],'mid_bad':[q8(x) for x in over_white_premult(.5,False)],'good':[[q8(x) for x in over_white_premult(i/255)] for i in range(256)],'bad':[[q8(x) for x in over_white_premult(i/255,False)] for i in range(256)]},image={'source':source,'small':small,'factor':4},reference_gradients=refs,checks={'roundtrip_points':len(xs),'max_error':roundtrip,'eight_bit_roundtrips':256,'blend_cases':pairs})
if __name__=='__main__':
    d=compute();(P/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:d[k] for k in ['main','checks','redgreen']},indent=2))
