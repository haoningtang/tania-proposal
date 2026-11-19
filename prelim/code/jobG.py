import lib, json
from rc import *
res=[]
def go(tag,n,a,t,r,hs,lo,hi):
    lib.NSI=n
    for h in hs:
        B=bands(a,t,r,h,0.0,'p',TH=(0.5,3,6),lo=lo,hi=hi,step=0.002)
        res.append({'tag':tag,'h':h,'b':B}); print(tag,h,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],1)) for x in B if x['Q']<1500],flush=True)
        json.dump(res,open('jobG.json','w'))
# SiN (n=2.0), period 1000 nm, 300 nm thick, r=200 nm
go('SiN',2.0,1.0,0.30,0.20,(None,0.15,0.20,0.25,0.30,0.40,0.50),1.30,1.75)
