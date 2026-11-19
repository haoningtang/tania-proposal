import numpy as np, sys, json, time
from lib import *
from scipy.interpolate import AAA
a,t,r=0.62,0.22,0.12
TH=[0.5,2,4,6,8,10]
def amp(lam,th,h,sx,pol,az=0.0,nG=81):
    k=np.sin(np.radians(th))/lam
    ex,ey,T,R=solve(lam,k*np.cos(az),k*np.sin(az),a,t,r,h,sx=sx,pol=pol,nG=nG)
    if az==0.0: return (ex if pol=='s' else ey),T
    # project on s / p unit vectors
    if pol=='s': return (-np.sin(az)*ex+np.cos(az)*ey),T
    return (-np.sin(az)*ex+np.cos(az)*ey),T
def getpoles(lams,tv,lo,hi):
    w=1/np.asarray(lams); A=AAA(w,np.asarray(tv),rtol=1e-5,max_terms=9)
    out=[]
    P=A.poles(); Rz=A.residues()
    for p,rz in zip(P,Rz):
        if p.real<=0 or p.imag==0: continue
        l0=1/p.real; Q=p.real/(2*abs(p.imag))
        if lo<l0<hi and 15<Q<3e4 and abs(rz)/abs(p.imag)>0.05: out.append((l0,Q))
    return sorted(out)
def run(h,sx,az=0.0,tag=''):
    res={'h':h,'sx':sx,'az':az,'data':{}}
    lams=np.linspace(1.40,1.70,151)
    for pol in ('s','p'):
        tv=[amp(l,TH[0],h,sx,pol,az)[0] for l in lams]
        P0=getpoles(lams,tv,1.41,1.69)
        prev=P0; res['data'][pol]={str(TH[0]):P0}
        for th in TH[1:]:
            if not prev: break
            lo=min(p[0] for p in prev)-0.02; hi=max(p[0] for p in prev)+0.02
            ll=np.linspace(lo,hi,int((hi-lo)/0.001)+1)
            tv=[amp(l,th,h,sx,pol,az)[0] for l in ll]
            P=getpoles(ll,tv,lo,hi)
            res['data'][pol][str(th)]=P; prev=P if P else prev
    json.dump(res,open(f'trk_h{h}_s{sx}_az{az:.2f}{tag}.json','w'))
    print('done',h,sx,az,{k:{th:[(round(x,4),round(q)) for x,q in v] for th,v in d.items()} for k,d in res['data'].items()},flush=True)
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='gap':
        for h in (0.10,0.15,0.20,0.25,0.30,0.35,0.40): run(h,0.0)
    elif mode=='shift':
        for sx in (0.1,0.2,0.3,0.4,0.5): run(0.20,sx)
