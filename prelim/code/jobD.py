from rc import *
a,t=0.62,0.22
res=[]
for ra in (0.31,0.32,0.33,0.34,0.35,0.36):
    for pol in 'ps':
        B=bands(a,t,ra*a,None,0.0,pol,TH=(0.5,2,4,6),lo=1.15,hi=1.45,step=0.002)
        res.append({'ra':ra,'pol':pol,'b':B}); print(ra,pol,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],2),[round(p[1],4) for p in x['pts']]) for x in B],flush=True)
        json.dump(res,open('jobD.json','w'))
