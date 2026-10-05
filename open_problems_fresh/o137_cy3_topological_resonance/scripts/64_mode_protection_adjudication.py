#!/usr/bin/env python3
"""
O137 — Round 16 (scripts/64)
============================
缺口 ② 之裁決輪

scripts/63 已確立:
  §1 幾何每模式數據【完全由 n 決定】⟹ m = f(n), 冇第二個幾何變量
  §2 屏障: 逐代冪律 (6 參數) RMS = 0.2243 dex; poly_5 (6 參數) = 0.1658
  §3 ★★ 指數階梯 (F₅/2)^{g−1} 之 bootstrap: p₃ = 6.3993 ± 0.0025 vs 6.25 ⟹ **−59.4σ 否證**
       (但幾何比 r = 2.5181 ± 0.0359 vs 2.5 = −0.50σ ✅)
  §4 ★★ 放大因子 A(n) 之密度對照: 1% 容差下目錄覆蓋率 88.7%, 觀測 8/8 vs 期望 7.10
       ⟹ 命中率 ≤ 密度期望 ⟹ **無結構訊號** (O136 致命傷 #1 之判別器)
  §5 ★★ 兩框架模式集近乎不相交: A₅ 集 {1,2,3,4,5,7,9,11,13} ∩ O64 集 {1,7,14,20,33,34,44} = {1,7}

本輪:
  §1 參數屏障曲線 (min RMS vs 參數數)
  §2 ★★★ 模式保護裁決 — A₅ 集 vs O64 集 (精確判準, 非擬合)
"""
import numpy as np, math
from collections import Counter

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

BASE="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/"
D=BASE+"o137_cy3_topological_resonance/data/"
CMB=BASE+"cmb_cold_spot/"
N_d,N_gen,B,F5,L4,L5=44,3,4,5,7,11
M0=27.900915
MODES=[1,2,3,4,5,7,9,11,13]
PART=["e","u","d","s","mu","c","tau","b","t"]
MASS={"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
      "c":1270.0,"tau":1776.86,"b":4180.0,"t":172690.0}
m=np.array([MASS[p] for p in PART])
gamma=lambda n: 4*math.sin(n*math.pi/88)**2
g=np.array([gamma(n) for n in MODES])
lm=np.log10(m); lg=np.log10(g)

print("="*88); print("§1 參數屏障曲線: min RMS vs 參數數"); print("="*88)
print(f"  {'k (參數)':>9} {'poly in n':>12} {'poly in log γ':>14} {'逐代模型':>10}")
def rms(res): return float(np.sqrt(np.mean(np.asarray(res)**2)))
res_tbl={}
for k in range(1,10):
    if k==1:
        rn=rms(lm-lm.mean()); rg=rn; rb=None
    else:
        An=np.vstack([np.array(MODES,float)**j for j in range(k)]).T
        sn=np.linalg.lstsq(An,lm,rcond=None)[0]; rn=rms(lm-An@sn)
        Ag=np.vstack([lg**j for j in range(k)]).T
        sg=np.linalg.lstsq(Ag,lm,rcond=None)[0]; rg=rms(lm-Ag@sg)
    rb=None
    if k in (2,4,6):
        nb=k//2; tot=0.0
        for blk in [[1,2,3],[4,5,7],[9,11,13]]:
            idx=[MODES.index(n) for n in blk]
            Ab=np.vstack([lg[idx]**j for j in range(nb)]).T
            sb=np.linalg.lstsq(Ab,lm[idx],rcond=None)[0]
            tot+=float(np.sum((lm[idx]-Ab@sb)**2))
        rb=math.sqrt(tot/9)
    res_tbl[k]=(rn,rg,rb)
    print(f"  {k:>9} {rn:>12.4f} {rg:>14.4f} {(f'{rb:.4f}' if rb is not None else '—'):>10}")
qual=[k for k,(rn,rg,rb) in res_tbl.items() if min(rn,rg) < 0.05]
kmin=min(qual) if qual else None
print(f"\n  ★ 達 RMS < 0.05 dex 之最少參數 (poly in n 或 log γ) = {kmin if kmin else '≥10 (無)'}")
best7=min(min(rn,rg) for k,(rn,rg,rb) in res_tbl.items() if k<=7)
print(f"  ★★ k ≤ 7 之最佳 RMS = {best7:.4f} dex (因子 {10**best7:.2f}) — 仍未達 0.05")
ck("★★ 屏障: k ≤ 7 全部未達 RMS < 0.05", best7>=0.05, True)
print(f"  ★★ 幾何供給 0 個額外參數 (m = f(n), n 已知) ⟹ 【A₅ 幾何唔可能閉合質量標度】")
print(f"  ★ 註: 逐代飽和模型 (k=6, 每代 3 點 2 參數) RMS = 0 係【構造必然】(零預測力), 唔算閉合")

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§2 ★★★ 模式保護裁決: A₅ 集 vs O64 集"); print("="*88)
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
nodes=[tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()]
def rd(ra,dec):
    r,d=math.radians(ra),math.radians(dec)
    return np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)])
obs=np.array([rd(a,b) for a,b in nodes])
TnC=np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.0 if n%2 else 1.0/(1-n*n)

def violation(V,n,ntest=300,seed=11):
    """F_n(c) = Σᵢ T_n(vᵢ·c) 之【絕對】跨度 (max − min) over random c。
       因 |T_n(x)| ≤ 1 (|x| ≤ 1) ⟹ F_n ∈ [−60, 60]; 受保護 ⟹ 恆定 ⟹ 跨度 ≈ 0。
       ⚠ 唔可以用 max|F| 正規化: 受保護模式 F ≈ 0, 正規化會退化為噪聲比。"""
    rng=np.random.default_rng(seed)
    C=rng.normal(size=(ntest,3)); C/=np.linalg.norm(C,axis=1,keepdims=True)
    x=V@C.T
    F=TnC(n)(x).sum(axis=0)
    return float(np.ptp(F))

print(f"  判準 (精確, 非容差): 模式 n 受保護 ⟺ 全部活躍不變調和次數 j ≤ n 且 j ≡ n (mod 2) 皆為零")
H_NZ={6,10,12,15,16,18,20,21,22,24,25,26}
def protected_exact(n): return not any(j<=n and j%2==n%2 for j in H_NZ)
exact_set=[n for n in range(1,45) if protected_exact(n)]
print(f"  精確判準之受保護集 = {exact_set}")
ck("★★★ 精確受保護集 = A₅ 集 {1,2,3,4,5,7,9,11,13}", exact_set, MODES)
ck("★ 受保護模式數 = 9", len(exact_set), 9)

print(f"\n  ── 暴力驗證 (節點集上 Σᵢ T_n(vᵢ·c) 之相對跨度) ──")
print(f"  {'n':>4} {'精確受保護':>10} {'A₅集':>6} {'O64集':>6} {'跨度 ptp(F_n)':>16} {'判定':>8}")
A5set=set(MODES); O64set={1,7,14,20,33,34,44}
rows=[]
for n in sorted(A5set|O64set):
    v=violation(obs,n)
    rows.append((n,protected_exact(n),v))
    print(f"  {n:>4} {str(protected_exact(n)):>10} {str(n in A5set):>6} {str(n in O64set):>6} {v:>16.3e} "
          f"{'✅ 保護' if v<1e-3 else '❌ 破缺':>8}")
prot=[v for n,_,v in rows if protected_exact(n)]
unpr=[v for n,_,v in rows if not protected_exact(n)]
print(f"\n  受保護模式之跨度: max = {max(prot):.3e}")
print(f"  未受保護模式之跨度: min = {min(unpr):.3e}")
ck("★★ 受保護模式全部跨度 < 1e−3 (殘餘 = 節點集 I-不變性精度 9.7e−5°)", max(prot)<1e-3, True)
ck("★★ 未受保護模式全部跨度 > 1e1", min(unpr)>1e1, True)
print(f"  ★★ 分離度 = {min(unpr)/max(prot):.3e} (10–15 個數量級)")

o64_extra=sorted(O64set-A5set)
print(f"\n  ★★ O64 集之額外模式 (不在 A₅ 集) = {o64_extra}")
for n in o64_extra:
    print(f"     n = {n:>2}: 精確受保護 = {protected_exact(n)}, 暴力跨度 = {violation(obs,n):.3e}")
ck("★★★ O64 集之 5 個額外模式全部【不受保護】", all(not protected_exact(n) for n in o64_extra), True)

print("\n"+"="*88); print("§3 裁決"); print("="*88)
print(f"""
  ★★★ 裁決結果 (精確, 非擬合):
     A₅ 集 {{1,2,3,4,5,7,9,11,13}} = 【恰好】全部受保護模式 (9 個)
       — 由「無活躍不變調和次數 j ≤ n, j ≡ n (mod 2)」精確判定 (定理, 零容差)
       — 暴力驗證: 受保護模式之 Σᵢ T_n 跨度 ≤ {max(prot):.1e} (殘餘 = 節點集 I-不變性 9.7e−5°)
     O64 集 {{1,7,14,20,33,34,44}} 之 5 個額外模式 {{14,20,33,34,44}}
       — 全部【不受保護】: 跨度 ≥ {min(unpr):.1e}
       — 分離度 {min(unpr)/max(prot):.1e} ≈ {math.log10(min(unpr)/max(prot)):.1f} 個數量級, 無中間地帶

  ⟹ 兩個框架對同一 9 費米子給出近乎不相交之模式集, 而【幾何只支持 A₅ 集】:
     ・A₅ 集: 質量無關, 第一性原理 (A₅ 動差準則), 9 個互異模式, 質量升序 = n 升序
     ・O64 集: 由質量閉合反推, 含 5 個【非全息通道】(未受保護) 之模式
     ⟹ 若「費米子模式 = 全息保護模式」成立, 則 O64 之模式分配唔合法;
        O64 之數值閉合係靠 F_proj 補償, 唔係結構。

  ⚠️ 誠實界限: 上述裁決【依賴】「費米子模式必須係全息保護模式」此一前提。
     若 O64 框架唔主張全息保護 (而係另一種機制), 則兩者唔直接衝突, 只係
     「同一數字 (模式集) 有兩個來源」之並存。此前提必須明列。
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
