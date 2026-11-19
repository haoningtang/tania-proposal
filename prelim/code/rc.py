import numpy as np, json, sys, warnings
warnings.filterwarnings("ignore")
from lib import solve
from scipy.interpolate import AAA
def amp(lam,th,a,t,r,h,sx,pol,nG=81,r2=None):
    k=np.sin(np.radians(th))/lam
    ex,ey,T,R=solve(lam,k,0,a,t,r,h,sx=sx,pol=pol,nG=nG,r2=r2)
    return (ex if pol=='s' else ey),T
def getpoles(lams,tv,lo,hi,qmax=3e4):
    w=1/np.asarray(lams); A=AAA(w,np.asarray(tv),rtol=1e-5,max_terms=10)
    out=[]
    for p,rz in zip(A.poles(),A.residues()):
        if p.real<=0 or p.imag==0: continue
        l0=1/p.real; Q=p.real/(2*abs(p.imag))
        if lo<l0<hi and 15<Q<qmax and abs(rz)/abs(p.imag)>0.05: out.append((l0,Q))
    return sorted(out)
def bands(a,t,r,h,sx,pol,TH=(0.5,3,6),lo=1.35,hi=1.75,step=0.0015,nG=81,r2=None,qmax0=4000):
    """returns list of branches: each [(th,lam,Q),...] started from bright poles at TH[0]"""
    lams=np.arange(lo,hi,step)
    tv=[amp(l,TH[0],a,t,r,h,sx,pol,nG,r2)[0] for l in lams]
    P0=[p for p in getpoles(lams,tv,lo+0.005,hi-0.005) if p[1]<qmax0]
    br=[[(TH[0],p[0],p[1])] for p in P0]
    for th in TH[1:]:
        for b in br:
            if b[-1] is None: continue
            l0=b[-1][1]; w=max(0.012,3*l0/b[-1][2]) if b[-1][2]<400 else 0.012
            if th>=5: w+=0.02
            ll=np.linspace(l0-w-0.02*(th>=5),l0+w,41 if b[-1][2]<800 else 81)
            tv=[amp(l,th,a,t,r,h,sx,pol,nG,r2)[0] for l in ll]
            P=getpoles(ll,tv,ll[0],ll[-1])
            if not P: b.append(None); continue
            # predict by quadratic extrapolation if possible
            if len(b)>=2:
                s0,s1,sn=[np.sin(np.radians(x))**2 for x in (b[0][0],b[-1][0],th)]
                pred=b[0][1]+(b[-1][1]-b[0][1])*(sn-s0)/(s1-s0)
            else: pred=l0
            p=min(P,key=lambda x:abs(x[0]-pred)); b.append((th,p[0],p[1]))
    out=[]
    for b in br:
        b=[x for x in b if x is not None]
        M=None
        if len(b)>=2:
            s2=np.array([np.sin(np.radians(x[0]))**2 for x in b]); y=np.array([x[1] for x in b]); y=(y-y[0])/y[0]
            c=np.polyfit(s2[:2],y[:2],1)[0]; M=-1/(2*c) if c!=0 else np.inf
        out.append({'lam':b[0][1],'Q':b[0][2],'M':M,'pts':b})
    return out
