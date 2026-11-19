from rc import *
import numpy as np
a,t=0.62,0.22
def tmap(r,h,lams,ths,name,pol='p'):
    T=np.array([[amp(l,max(th,0.2),a,t,r,h,0.0,pol)[1] for l in lams] for th in ths]); np.savez(name,T=T,lams=lams,ths=ths); print('map',name,flush=True)
ths=np.arange(0,12.1,1.0)
tmap(0.12,0.085,np.arange(1.42,1.5001,0.001),ths,'map_flat')
tmap(0.12,0.20,np.arange(1.46,1.5401,0.001),ths,'map_h200')
tmap(0.062,0.10,np.arange(1.5520,1.5660,0.0001),ths,'map_highR')
res=[]
for h in (0.085,0.10,0.15,0.20,0.30):
    for sx in (0.0,0.125,0.25,0.375,0.5):
        B=bands(a,t,0.12,h,sx,'p',TH=(0.5,6),lo=1.42,hi=1.56)
        res.append({'h':h,'sx':sx,'b':B}); print(h,sx,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],1)) for x in B],flush=True)
        json.dump(res,open('jobF.json','w'))
