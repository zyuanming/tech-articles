"""Original SDR sRGB teaching arithmetic, CC0-1.0. Domain [0, 1]."""
import math

def unit(x):
    if not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=1:
        raise ValueError('finite normalized value in [0,1] required')
    return float(x)

def decode(s):
    s=unit(s)
    return s/12.92 if s<=0.04045 else ((s+0.055)/1.055)**2.4

def encode(l):
    l=unit(l)
    return 12.92*l if l<=0.0031308 else 1.055*l**(1/2.4)-0.055

def q8(s):return math.floor(unit(s)*255+0.5)

def blend(a,b,t,linear=True):
    t=unit(t);a=unit(a);b=unit(b)
    if linear:return encode((1-t)*decode(a)+t*decode(b))
    return (1-t)*a+t*b

def average_rgb(colors,linear=True):
    if not colors:raise ValueError('nonempty colors required')
    return tuple(encode(sum(decode(c[j]) for c in colors)/len(colors)) if linear else sum(unit(c[j]) for c in colors)/len(colors) for j in range(3))

def over_white_premult(t,premult=True):
    """Interpolate opaque red -> transparent blue in LINEAR RGB; over white."""
    t=unit(t);a=(1,0,0,1);b=(0,0,1,0)
    alpha=(1-t)*a[3]+t*b[3]
    if premult:
        contribution=[(1-t)*a[j]*a[3]+t*b[j]*b[3] for j in range(3)]
    else:
        color=[(1-t)*a[j]+t*b[j] for j in range(3)]
        contribution=[alpha*c for c in color]
    return [encode(c+(1-alpha)) for c in contribution]
