import numpy as np, grcwa, warnings
warnings.filterwarnings("ignore")
from scipy.interpolate import AAA
NSI=3.48
def solve(lam, kx, ky, a, t, r, h, sx=0.0, sy=0.0, pol='s', nG=81, N=96, r2=None):
    """two identical Si hole slabs (square lattice, period a), gap h, upper shifted by (sx,sy)*a.
    returns complex zero-order transmitted amplitude projected on incident pol, and power T"""
    f=1.0/lam
    kpar=np.hypot(kx,ky)
    theta=np.arcsin(min(kpar/f,0.999999)); phi=np.arctan2(ky,kx)
    o=grcwa.obj(nG,[a,0],[0,a],f,theta,phi,verbose=0)
    o.Add_LayerUniform(0.0,1.0)
    o.Add_LayerGrid(t,N,N)
    if h is not None:
        o.Add_LayerUniform(h,1.0)
        o.Add_LayerGrid(t,N,N)
    o.Add_LayerUniform(0.0,1.0)
    o.Init_Setup()
    x=(np.arange(N)+0.5)/N
    X,Y=np.meshgrid(x,x,indexing='ij')
    def grid(sx,sy,rr):
        dx=(X-0.5-sx+0.5)%1-0.5; dy=(Y-0.5-sy+0.5)%1-0.5
        e=np.ones((N,N))*NSI**2; e[dx**2+dy**2<(rr/a)**2]=1.0; return e.flatten()
    eps=grid(0,0,r)
    if h is not None: eps=np.concatenate([eps,grid(sx,sy,r if r2 is None else r2)])
    o.GridLayer_geteps(eps)
    if pol=='s': o.MakeExcitationPlanewave(0,0,1,0,order=0)
    else: o.MakeExcitationPlanewave(1,0,0,0,order=0)
    R,T=o.RT_Solve(normalize=1)
    ai,bi=o.GetAmplitudes(o.Layer_N-1,0.0)
    n=o.nG
    ex,ey=ai[0],ai[n]
    return ex,ey,np.real(T),np.real(R)
def poles(lams, tvals, lam_lo, lam_hi, qmin=5):
    w=1.0/np.asarray(lams)
    A=AAA(w, np.asarray(tvals), rtol=1e-6, max_terms=20)
    out=[]
    for p in A.poles():
        if p.real<=0: continue
        lam0=1/p.real; Q=p.real/(2*abs(p.imag)+1e-300)
        if lam_lo<lam0<lam_hi and Q>qmin: out.append((lam0,Q))
    return sorted(out)
