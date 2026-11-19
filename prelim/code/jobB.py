from rc import *
a,t=0.62,0.22
res=[]
for ra in (0.10,0.14,0.18,0.22,0.26,0.30,0.34,0.38,0.42,0.46):
    for pol in 'ps':
        B=bands(a,t,ra*a,None,0.0,pol,lo=1.15,hi=1.75,step=0.002)
        res.append({'ra':ra,'pol':pol,'b':B}); print(ra,pol,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],2)) for x in B],flush=True)
        json.dump(res,open('jobB.json','w'))
