import lib, json
from rc import *
res=[]
# thin Si: 100 nm thick, period 800 nm, r=150 nm
for h in (None,0.10,0.15,0.20,0.25,0.30,0.40):
    B=bands(0.80,0.10,0.15,h,0.0,'p',TH=(0.5,3,6),lo=1.25,hi=1.75,step=0.002)
    res.append({'h':h,'b':B}); print('thinSi',h,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],1)) for x in B if x['Q']<1500],flush=True)
    json.dump(res,open('jobH.json','w'))
