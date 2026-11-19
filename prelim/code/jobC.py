from rc import *
a,t=0.62,0.22
res=[]
def go(r,h,lo,hi,step,TH,tag):
    B=bands(a,t,r,h,0.0,'p',TH=TH,lo=lo,hi=hi,step=step)
    res.append({'tag':tag,'r':r,'h':h,'b':B}); print(tag,r,h,[(round(x['lam'],4),round(x['Q']),None if x['M'] is None else round(x['M'],1),[round(p[1],5) for p in x['pts']]) for x in B],flush=True)
    json.dump(res,open('jobC.json','w'))
for h in (0.075,0.08,0.085,0.09,0.10,0.07):
    go(0.12,h,1.42,1.50,0.0015,(0.5,2,4,6,8,10),'flat')
for h in (0.06,0.08,0.10,0.14,0.20):
    go(0.062,h,1.50,1.68,0.0008,(0.5,3,6,10),'highR')
