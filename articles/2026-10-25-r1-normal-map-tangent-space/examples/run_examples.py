"""Recompute numerical records and actual images. CC0-1.0."""
from pathlib import Path
import json,math,random,hashlib,platform
from PIL import Image,PngImagePlugin
from normal_map import *
ROOT=Path(__file__).resolve().parent

def save_image(name,pixels,size,color=True):
    im=Image.new('RGB',(size,size));im.putdata(pixels)
    info=PngImagePlugin.PngInfo()
    if color:info.add(b'sRGB',b'\x00')
    p=ROOT/'output'/name;p.parent.mkdir(exist_ok=True);im.save(p,pnginfo=info)
    return dict(file='examples/output/'+name,size=[size,size],sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def compute():
    positions=[(0,0,0),(0,2,0),(-1,0,0)];uv=[(0,0),(1,0),(0,1)]
    f=triangle_frame(positions,uv);rgb=(.68,.74,.9);nt=unpack(rgb);nw=transform(nt,f['T'],f['B'],f['N']);light=(-.48,.36,.8)
    quant=[q8(x) for x in rgb];qn=unpack([x/255 for x in quant]);qw=transform(qn,f['T'],f['B'],f['N'])
    assert abs(dot(nw,light)-1)<1e-12 and abs(dot(nt,light)-.64)<1e-12
    mir=triangle_frame(positions,[(0,0),(1,0),(0,-1)])
    mirror_nt=(nt[0],-nt[1],nt[2]);mirror_correct=transform(mirror_nt,mir['T'],mir['B'],mir['N']);mirror_wrong=transform(mirror_nt,mir['T'],cross(mir['N'],mir['T']),mir['N'])
    assert max(abs(a-b) for a,b in zip(mirror_correct,nw))<1e-12
    flat8=unpack([128/255,128/255,1]);bad=unpack([decode(x) for x in [.5,.5,1]])
    mean=mul(add((.6,0,.8),(-.6,0,.8)),.5)
    # Tangent (1,1,0) and normal (-1,1,0) under M=diag(2,1,1).
    tangent=norm((1,1,0));normal=norm((-1,1,0));mt=(2*tangent[0],tangent[1],0)
    wrong=norm((2*normal[0],normal[1],0));correct=norm((normal[0]/2,normal[1],0))
    rng=random.Random(20261025);tested=0
    for _ in range(1000):
        angle=rng.uniform(-math.pi,math.pi);T=rot((1,0,0),angle);B=rot((0,1,0),angle);N=(0,0,1)
        n=norm((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(.01,1)))
        w=transform(n,T,B,N)
        assert abs(dot(w,w)-1)<1e-12
        back=(dot(w,T),dot(w,B),dot(w,N));assert max(abs(a-b) for a,b in zip(back,n))<1e-12;tested+=1
    try:triangle_frame(positions,[(0,0),(1,0),(2,0)])
    except ValueError:pass
    else:raise AssertionError('degenerate UV not rejected')
    assert abs(dot(mirror_wrong,light)-.5392)<1e-12
    assert abs(dot(mt,correct))<1e-12 and abs(dot(mt,wrong))>.9
    assert abs(math.sqrt(dot(mean,mean))-.8)<1e-12
    assert norm(mean)==(0.,0.,1.)
    assert unpack(rgb,0)==(0.,0.,1.)
    assert abs(dot(flat8,flat8)-1)<1e-12 and flat8[0]>0
    size=96;outputs={};details={}
    outputs['normal-map']=save_image('normal-map-data.png',make_map(size),size,False)
    for mode in ['flat','mapped','other-light','rotated-correct','rotated-wrong','green-flip','gamma-wrong']:
        px,detail=render(mode,size);outputs[mode]=save_image(mode+'.png',px,size);details[mode]=detail
    return dict(python=platform.python_version(),main=dict(positions=positions,uv=uv,frame=f,rgb=rgb,nt=nt,nw=nw,light=light,good_dot=dot(nw,light),wrong_dot=dot(nt,light),codes=quant,quant_nt=qn,quant_nw=qw,quant_dot=dot(qw,light)),mirror=dict(frame=mir,nt=mirror_nt,correct=mirror_correct,wrong=mirror_wrong,wrong_dot=dot(mirror_wrong,light)),flat8=flat8,gamma_wrong_flat=bad,filter=dict(a=[.6,0,.8],b=[-.6,0,.8],mean=mean,length=math.sqrt(dot(mean,mean)),normalized=norm(mean)),scales=[dict(scale=s,n=unpack(rgb,s)) for s in [0,.5,1,2]],nonuniform=dict(tangent=tangent,normal=normal,scaled_tangent=mt,wrong_normal=wrong,correct_normal=correct,wrong_dot=dot(mt,wrong),correct_dot=dot(mt,correct)),outputs=outputs,render_details=details,config=dict(size=size,height_amplitude=.025,height_waves=4,ambient=.08,diffuse_weight=.92,albedo=[.42,.58,.72]),checks=dict(rigid_roundtrips=tested,degenerate_uv_rejected=True))
if __name__=='__main__':
    d=compute();(ROOT/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:d[k] for k in ['main','mirror','flat8','gamma_wrong_flat','checks']},ensure_ascii=False,indent=2))
