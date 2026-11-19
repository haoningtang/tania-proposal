import json,glob,numpy as np
def branches(d,pol):
    """track branches from smallest angle by nearest wavelength; keep Q<3000 at start"""
    D=d['data'][pol]; ths=sorted(D,key=float)
    start=[p for p in D[ths[0]] if p[1]<3000]
    out=[]
    for l0,q0 in start:
        tr=[(float(ths[0]),l0,q0)]; cur=l0
        for th in ths[1:]:
            c=[p for p in D[th]]
            if not c: break
            p=min(c,key=lambda x:abs(x[0]-cur))
            if abs(p[0]-cur)>0.012: break
            tr.append((float(th),p[0],p[1])); cur=p[0]
        out.append(tr)
    return out
def Mfit(tr):
    th=np.radians([x[0] for x in tr]); lam=np.array([x[1] for x in tr])
    s2=np.sin(th)**2; y=(lam-lam[0])/lam[0]
    if len(tr)<3: return None
    # dlam/lam = -(s2)/(2M)  -> slope
    m=s2<=np.sin(np.radians(6.1))**2
    c=np.polyfit(s2[m],y[m],1)[0]
    return -1/(2*c)
rows=[]
for f in sorted(glob.glob('trk_*.json')):
    d=json.load(open(f))
    for pol in 'sp':
        for tr in branches(d,pol):
            M=Mfit(tr)
            rows.append((d['h'],d['sx'],pol,tr[0][1],tr[0][2],M,len(tr),tr[-1][1],tr[-1][2]))
print('h   sx  pol lam0    Q0    M(<=6deg)  npts lam@last Q@last')
for r in sorted(rows): print(r[0],r[1],r[2],round(r[3],4),round(r[4]),None if r[5] is None else round(r[5],2),r[6],round(r[7],4),round(r[8]))
json.dump(rows,open('rows.json','w'))
