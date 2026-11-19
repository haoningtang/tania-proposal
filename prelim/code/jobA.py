from rc import *
a,t,r=0.62,0.22,0.12
res=[]
for h in (0.04,0.05,0.06,0.07,0.08,0.09):
    for pol in 'ps':
        B=bands(a,t,r,h,0.0,pol,lo=1.36,hi=1.72)
        res.append({'h':h,'pol':pol,'b':B}); print(h,pol,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],2)) for x in B],flush=True)
        json.dump(res,open('jobA.json','w'))
