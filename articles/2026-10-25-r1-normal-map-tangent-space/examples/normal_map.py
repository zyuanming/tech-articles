"""Original educational normal mapping arithmetic and CPU renderer, CC0-1.0.
Rigid rotations, orthonormal bases, Lambert+constant ambient only; not a glTF loader.
"""
import math

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(v):
    length=math.sqrt(dot(v,v))
    if length<1e-12:raise ValueError('zero/near-zero vector')
    return tuple(x/length for x in v)
def unpack(rgb,scale=1):return norm(((2*rgb[0]-1)*scale,(2*rgb[1]-1)*scale,2*rgb[2]-1))
def transform(nt,T,B,N):return norm(tuple(nt[0]*T[i]+nt[1]*B[i]+nt[2]*N[i] for i in range(3)))
def encode(x):return 12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055
def decode(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def q8(x):return max(0,min(255,math.floor(x*255+.5)))
def rot(v,angle):
    c=math.cos(angle);s=math.sin(angle)
    return (c*v[0]-s*v[1],s*v[0]+c*v[1],v[2])
def triangle_frame(p,uv):
    e1=add(p[1],mul(p[0],-1));e2=add(p[2],mul(p[0],-1))
    d1=add(uv[1],mul(uv[0],-1));d2=add(uv[2],mul(uv[0],-1))
    det=d1[0]*d2[1]-d1[1]*d2[0]
    if abs(det)<1e-12:raise ValueError('degenerate UV triangle')
    tr=mul(add(mul(e1,d2[1]),mul(e2,-d1[1])),1/det)
    br=mul(add(mul(e2,d1[0]),mul(e1,-d2[0])),1/det)
    N=norm(cross(e1,e2));T=norm(add(tr,mul(N,-dot(N,tr))))
    w=1 if dot(cross(N,T),br)>0 else -1
    B=mul(cross(N,T),w)
    return dict(edges=[e1,e2],duv=[d1,d2],det=det,rawT=tr,rawB=br,T=T,B=B,N=N,w=w)

def make_map(size=96):
    pixels=[]
    for j in range(size):
        v=(j+.5)/size
        for i in range(size):
            u=(i+.5)/size;k=2*math.pi*4;A=.025
            du=A*k*math.cos(k*u)*math.sin(k*v)
            dv=A*k*math.sin(k*u)*math.cos(k*v)
            nt=norm((-du,-dv,1))
            pixels.append(tuple(q8((c+1)/2) for c in nt))
    return pixels

def render(mode='mapped',size=96):
    """Orthographic XY square; u right, v down. T=+X B=-Y N=+Z w=-1."""
    texture=make_map(size);N=(0,0,1);angle=math.pi/2 if mode.startswith('rotated') else 0
    T=rot((1,0,0),angle);B=rot((0,-1,0),angle)
    light=norm((-.6,.4,1) if mode=='other-light' else (.6,.4,1))
    pixels=[];normal_samples=[]
    for j in range(size):
        for i in range(size):
            # Inverse rigid rotation maps the visible square back to its UV.
            x=(i+.5)/size-.5;y=.5-(j+.5)/size
            local=rot((x,y,0),-angle);u=local[0]+.5;v=.5-local[1]
            ix=min(size-1,max(0,int(u*size)));iy=min(size-1,max(0,int(v*size)))
            rgb=[c/255 for c in texture[iy*size+ix]]
            if mode=='gamma-wrong':rgb=[decode(c) for c in rgb]
            nt=unpack(rgb)
            if mode=='green-flip':nt=(nt[0],-nt[1],nt[2])
            nw=N if mode=='flat' else nt if mode=='rotated-wrong' else transform(nt,T,B,N)
            diffuse=max(0,dot(nw,light));value=.08+.92*diffuse
            pixels.append(tuple(q8(encode(a*value)) for a in (.42,.58,.72)))
            if (i,j) in [(size//2,size//2),(size//4,size//3)]:normal_samples.append(dict(pixel=[i,j],nt=nt,nw=nw,dot=diffuse))
    return pixels,dict(size=size,mode=mode,T=T,B=B,N=N,light=light,samples=normal_samples)
