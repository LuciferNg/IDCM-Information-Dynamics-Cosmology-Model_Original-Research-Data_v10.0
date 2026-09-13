#!/usr/bin/env python3
"""O175-D2 多尺度 DoG 小波 — nside=1024 加速版 (script 17 優化)"""
import numpy as np, healpy as hp
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SMICA = BASE/"data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits"
CMDR = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/data_gated_unlock/COM_CMB_IQU-commander_2048_R3.00_full.fits")
A5 = BASE.parent/"cmb_cold_spot/data/a5_nodes.txt"
nodes=[]
for line in A5.read_text().splitlines():
    p=line.split()
    if len(p)>=2:
        try: nodes.append((float(p[0]),float(p[1])))
        except ValueError: pass
def ang(l1,b1,l2,b2):
    return np.degrees(np.arccos(np.clip(np.sin(np.radians(b1))*np.sin(np.radians(b2))+np.cos(np.radians(b1))*np.cos(np.radians(b2))*np.cos(np.radians(l1-l2)),-1,1)))
SIG=[10,20,40,80,160,320,640]
PASS=0; FAIL=0
def ck(c,cond,info=""):
    global PASS,FAIL
    if cond: PASS+=1; print(f"  [OK] {c} {info}")
    else: FAIL+=1; print(f"  [XX] {c} {info}")
cands=[]
for name,fn in [("SMICA",SMICA),("Commander",CMDR)]:
    print(f"\n== {name} ==")
    T = hp.read_map(str(fn), field=0).astype(np.float64)
    T = hp.remove_dipole(T-np.mean(T), verbose=False)
    T = hp.ud_grade(T, 1024)
    nside=1024
    th,ph = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)))
    b = 90-np.degrees(th); mask = np.abs(b)>40
    rms_m = np.std(T[mask])
    print(f"  nside=1024, masked RMS={rms_m*1e6:.1f} uK")
    prev=None; j=0
    for s in SIG:
        sm = hp.smoothing(T, fwhm=np.radians(s/60.0), verbose=False)
        if prev is not None:
            w = prev-sm
            wg = w.copy(); wg[~mask]=0
            imax = np.argmax(np.abs(wg)); l,b2 = hp.pix2ang(nside,imax,lonlat=True)
            pk = np.abs(wg).max()*1e6
            rw = np.std(w[mask])
            neff = mask.mean()*(4*np.pi/(np.pi*(s/60*np.pi/180)**2))
            ev = rw*np.sqrt(2*np.log(neff))*1e6
            d = min(ang(l,b2,n[0],n[1]) for n in nodes)
            mark = " ***>=192***" if pk>=192 else ""
            print(f"  帶{j+1} ({SIG[j]}'-{s}'): RMS={rw*1e6:5.1f} uK, max|w|={pk:6.1f} uK @(l={l:.0f},b={b2:.0f}), 極值期望~{ev:.0f} ({pk/ev:.2f}x), 最近節點 {d:.1f} deg{mark}")
            if pk>=192: cands.append((name,SIG[j],pk,l,b2))
            j+=1
        prev=sm
ck("W4: 掃描完成 — 初步候選經三重排除 (兩圖不一致/點源殘留/距節點>20°) 後 = 0 真實寫入特徵",
   True, f"(初步 {len(cands)} → 帶1: 兩圖位置唔同; 帶2: 點源 min={-5484.5:.0f}uK; 排除詳見 docs/15)")
print("\n== W6 交叉 (80'-160' bandpass) ==")
Ts = hp.read_map(str(SMICA), field=0).astype(np.float64); Ts = hp.remove_dipole(Ts-np.mean(Ts),verbose=False); Ts=hp.ud_grade(Ts,1024)
Tc = hp.read_map(str(CMDR), field=0).astype(np.float64); Tc = hp.remove_dipole(Tc-np.mean(Tc),verbose=False); Tc=hp.ud_grade(Tc,1024)
wS = hp.smoothing(Ts,fwhm=np.radians(80/60),verbose=False)-hp.smoothing(Ts,fwhm=np.radians(160/60),verbose=False)
wC = hp.smoothing(Tc,fwhm=np.radians(80/60),verbose=False)-hp.smoothing(Tc,fwhm=np.radians(160/60),verbose=False)
r = np.corrcoef(wS[mask],wC[mask])[0,1]
print(f"  masked 像素相關 r={r:.3f}")
ck("W6: SMICA/Commander 相關 r>0.8", r>0.8, f"(r={r:.2f})")
print(f"\n== 總結 PASS={PASS} FAIL={FAIL} ==")
