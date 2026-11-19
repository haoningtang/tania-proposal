from rc import *
a,t=0.62,0.22; r=0.336*a
res=[]
for h in (None,0.10,0.20,0.30):
    for pol in 'ps':
        B=bands(a,t,r,h,0.0,pol,TH=(0.5,2,4,6,8,10) if h is None else (0.5,2,4,6),lo=1.15,hi=1.50,step=0.002)
        res.append({'h':h,'pol':pol,'b':B}); print(h,pol,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],1),[round(p[1],4) for p in x['pts']]) for x in B],flush=True)
        json.dump(res,open('jobE.json','w'))
