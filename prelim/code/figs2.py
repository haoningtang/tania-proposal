import json,numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.size']=10
G='#0F6E56'; P='#534AB7'; O='#D85A30'; K='#5F5E5A'
def clean(ax):
    ax.spines[['top','right']].set_visible(False)
# ---------- Fig 1: tunable flat band (A1 + path)
fig,ax=plt.subplots(1,3,figsize=(14,4.2))
m=np.load('map_flat.npz'); a=ax[0]
a.pcolormesh(m['ths'],m['lams']*1000,m['T'].T,cmap='Greens_r',shading='nearest',vmin=0,vmax=1)
th=np.linspace(0,12,100); a.plot(th,1457.3*np.cos(np.radians(th)),'--',color='#D85A30',lw=1.6); a.text(7.2,1437.5,'air-gap Fabry–Perot',color='#D85A30',fontsize=9,rotation=-33)
a.set_xlabel('angle of incidence (deg)'); a.set_ylabel('wavelength (nm)'); a.set_title('(a) Flat band at gap = 85 nm (dark = resonance)',fontsize=10.5,loc='left')
C=json.load(open('jobC.json')); a=ax[1]
cols=plt.cm.coolwarm(np.linspace(0,1,6)); k=0
for d in sorted([d for d in C if d['tag']=='flat'],key=lambda d:d['h']):
    b=d['b'][0]['pts']; t=[p[0] for p in b]; l=np.array([p[1] for p in b])*1000
    a.plot(t,l-l[0],'o-',color=cols[k],lw=1.8,ms=4,label=f"{d['h']*1000:.0f} nm"); k+=1
a.plot(th,1457*(np.cos(np.radians(th))-1),'--',color=K,lw=1.2); a.set_ylim(-1.3,1.3); a.text(3.3,-1.15,'Fabry–Perot',color=K,fontsize=9)
a.axhline(0,color='k',lw=.5); a.set_xlabel('angle of incidence (deg)'); a.set_ylabel('resonance shift (nm)'); a.legend(title='gap',frameon=False,fontsize=8.5,ncol=2,loc='upper left')
a.set_title('(b) MEMS gap sweeps the band curvature through zero',fontsize=10.5,loc='left'); clean(a)
F=json.load(open('jobF.json')); a=ax[2]
hs=[0.085,0.10,0.15,0.20]; sxs=[0,0.125,0.25,0.375,0.5]
Z=np.zeros((4,5)); L=np.zeros((4,5))
for d in F:
    if d['h'] in hs:
        b=min(d['b'],key=lambda x:x['Q']); Z[hs.index(d['h']),sxs.index(d['sx'])]=1/b['M']; L[hs.index(d['h']),sxs.index(d['sx'])]=b['lam']*1000
X,Y=np.meshgrid(sxs,np.array(hs)*1000)
cf=a.contourf(X,Y,Z*100,levels=np.linspace(-4,4,17),cmap='coolwarm',extend='both'); plt.colorbar(cf,ax=a,label='band curvature 1/M  (×10⁻²)')
a.contour(X,Y,Z,levels=[0],colors='k',linewidths=2)
for (x,y,lab) in [(0.02,84,'1457 nm'),(0.25,100,'1472'),(0.47,146,'1495')]:
    a.plot(x,y,'o',color='k',ms=5); a.text(x+0.012,y+4,lab,fontsize=9)
a.text(0.06,118,'flat-band path\n(1/M = 0)',fontsize=9)
a.set_xlabel('lateral shift (fraction of period)'); a.set_ylabel('gap (nm)'); a.set_title('(c) Gap + shift keep the band flat while tuning',fontsize=10.5,loc='left')
fig.text(0.5,-0.03,'Full-wave (RCWA) calculation: two identical Si photonic-crystal slabs (period 620 nm, thickness 220 nm, hole radius 120 nm), TE polarization (E perpendicular to the plane of incidence), incidence plane along a lattice axis, Q ≈ 155–185.',ha='center',fontsize=8.5,color=K)
plt.tight_layout(); plt.savefig('Fig_A_tunable_flat_band.png',dpi=170,bbox_inches='tight'); plt.savefig('Fig_A_tunable_flat_band.pdf',bbox_inches='tight'); plt.close()
# ---------- Fig 2: high-R filter
fig,ax=plt.subplots(1,3,figsize=(14,4.2))
m=np.load('map_highR.npz'); a=ax[0]
a.pcolormesh(m['ths'],m['lams']*1000,m['T'].T,cmap='Greens_r',shading='nearest',vmin=0,vmax=1)
a.plot(th,1560.46*np.cos(np.radians(th)),'--',color='#D85A30',lw=1.6); a.text(1.2,1553.2,'air-gap Fabry–Perot',color='#D85A30',fontsize=9)
a.set_ylim(1552,1566); a.set_xlabel('angle of incidence (deg)'); a.set_ylabel('wavelength (nm)'); a.set_title('(a) 1.2 nm resonance (R ≈ 1270), gap = 100 nm',fontsize=10.5,loc='left')
a=ax[1]; H=[d for d in C if d['tag']=='highR']; H=sorted(H,key=lambda d:d['h'])
hh=[d['h']*1000 for d in H]; ll=[d['b'][0]['lam']*1000 for d in H]; MM=[d['b'][0]['M'] for d in H]; QQ=[d['b'][0]['Q'] for d in H]
a.plot(hh,ll,'o-',color=G,lw=2.2); a.set_xlabel('gap between slabs (nm)'); a.set_ylabel('resonance wavelength (nm)',color=G)
b=a.twinx(); b.plot(hh,MM,'s--',color=P,lw=1.6); b.set_ylim(0,20); b.set_ylabel('M  (étendue × resolving power, FP = 1)',color=P)
a.set_title(f'(b) {ll[-1]-ll[0]:.0f} nm ({(ll[-1]-ll[0])/np.mean(ll)*100:.1f}%) tuning, M ≈ 12, R ≈ {min(QQ):.0f}–{max(QQ):.0f}',fontsize=10.5,loc='left'); a.spines[['top']].set_visible(False); b.spines[['top']].set_visible(False)
a=ax[2]; n=3.48; r=np.logspace(-3,3,400); tune=30/(1+n*r); M=(1+n*r)/(1+r/n)
a.fill_between(tune,0.8,M,color='#888780',alpha=.13); a.plot(tune,M,color=K,lw=1.6); a.text(0.85,1.5,'reachable by planar\ncavities (30% travel)',fontsize=8.5,color='#444441')
a.plot([(ll[-1]-ll[0])/np.mean(ll)*100],[min(MM)],marker='*',ms=17,color=G,ls='none'); a.text(6.6,min(MM)*0.95,'R ≈ 1300\n(panel b)',fontsize=8.5,color=G)
a.plot([4.1],[25],marker='*',ms=13,color=G,ls='none',alpha=.6); a.text(5.2,24,'R ≈ 200',fontsize=8.5,color=G)
a.plot([2.7],[100],marker='*',ms=13,color=G,ls='none',alpha=.6); a.text(3.4,95,'flat-band path, R ≈ 170',fontsize=8.5,color=G)
a.plot([2],[10],marker='o',ms=9,mfc='none',mec=P,mew=1.6,ls='none'); a.text(0.33,5.0,'project target\n(1 nm, ±6.5°, both pol.)',fontsize=8.5,color=P)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(0.3,40); a.set_ylim(0.8,200); a.set_xlabel('tuning range (%)'); a.set_ylabel('M'); a.set_title('(c) Beyond the planar-cavity trade-off',fontsize=10.5,loc='left'); clean(a)
fig.text(0.5,-0.03,'Full-wave (RCWA) calculation: two aligned Si photonic-crystal slabs (period 620 nm, thickness 220 nm, hole radius 62 nm in a,b), TE polarization (E perpendicular to the plane of incidence), incidence plane along a lattice axis. Stars: computed designs.',ha='center',fontsize=8.5,color=K)
plt.tight_layout(); plt.savefig('Fig_B_highR_filter.png',dpi=170,bbox_inches='tight'); plt.savefig('Fig_B_highR_filter.pdf',bbox_inches='tight'); plt.close()
print('highR',list(zip(hh,ll,MM,QQ)))
# ---------- Fig 3: both polarizations
fig,ax=plt.subplots(1,2,figsize=(9.6,4.1))
B=json.load(open('jobB.json'))+json.load(open('jobD.json')); a=ax[0]
pts={'p':[], 's':[]}
for d in B:
    if not (0.305<d['ra']<0.37): continue
    c=[b for b in d['b'] if b['M'] is not None]
    if not c: continue
    b=max(c,key=lambda x:x['lam']); pts[d['pol']].append((d['ra'],1/b['M']))
for pol,col,lab in (('p',G,'TE'),('s',O,'TM')):
    z=np.array(sorted(set(pts[pol]))); a.plot(z[:,0],z[:,1]*100,'o-',color=col,lw=2,label=lab)
a.axhline(0,color='k',lw=.6); a.axhspan(-10,10,color=G,alpha=.08); a.text(0.345,-24,'|M| > 10',fontsize=8.5,color=G)
a.set_ylim(-130,45); a.set_xlabel('hole radius / period'); a.set_ylabel('band curvature 1/M  (×10⁻²)'); a.legend(frameon=False,fontsize=9,loc='lower right'); a.set_title('(a) Hole size flattens the TM band',fontsize=10.5,loc='left'); clean(a)
E=json.load(open('jobE.json')); a=ax[1]
for d in E:
    if d['h'] is None:
        b=max(d['b'],key=lambda x:x['lam'])['pts']; t=[p[0] for p in b]; l=np.array([p[1] for p in b])*1000
        a.plot(t,l-l[0],'o-',color=G if d['pol']=='p' else O,lw=2,label=('TE' if d['pol']=='p' else 'TM'))
a.plot(th,1313.5*(np.cos(np.radians(th))-1),'--',color=K,lw=1.3,label='air-gap Fabry–Perot'); a.set_ylim(-21,3)
a.set_xlabel('angle of incidence (deg)'); a.set_ylabel('resonance shift (nm)'); a.legend(frameon=False,fontsize=9,loc='lower left'); a.set_title('(b) TE and TM both flat (radius/period = 0.336)',fontsize=10.5,loc='left'); clean(a)
fig.text(0.5,-0.03,'Full-wave (RCWA): single Si photonic-crystal slab (period 620 nm, thickness 220 nm), resonance near 1.31 µm, Q ≈ 37; incidence plane along a lattice axis.',ha='center',fontsize=8.5,color=K)
plt.tight_layout(); plt.savefig('Fig_C_both_polarizations.png',dpi=170,bbox_inches='tight'); plt.savefig('Fig_C_both_polarizations.pdf',bbox_inches='tight'); plt.close()
print(pts)
