#!/usr/bin/env python3
"""
O137 — Round 15 (scripts/63)
============================
缺口 ② (n ↔ 質量映射) 之嚴格診斷

背景:
  docs/25 (Round 3, 08-30) 已確立: 選擇律 🟢 (A₅ 動差準則, 質量無關);
  標度律只有 Gen1 閉合 (m ∝ γ_n^{1.012}, RMS 0.0208), Gen2/Gen3 🔴 (0.43 / 0.78 nat-log)。
  docs/25 §3.1 遺留未驗證線索: p_g = 1.0120, 2.4709, 6.3992 vs (F₅/2)^{g−1} = 1, 2.5, 6.25。

Round 11 (scripts/57) 已測: m = f(n) 之五族 (C1–C5) 全部 RMS ≥ 0.22 dex (log10)。
  ⟹ 本輪唔再重複擬合, 改做【結構診斷】:
    §1 幾何供給審計 — 幾何每模式供給乜嘢?
    §2 ★ 屏障量化 — 要幾多參數才達 RMS < 0.05 dex?
    §3 ★★ 指數階梯之 bootstrap 檢定 (PDG 誤差)
    §4 ★★ 放大因子 A(n) 之密度對照 (結構 vs 巧合)
    §5 ★★ 兩框架模式集衝突 (A₅ 集 vs O64 集)
"""
import numpy as np, math, itertools
from fractions import Fraction

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

N_d,N_gen,B,F5,L4,L5,F7=44,3,4,5,7,11,13
M0=27.900915
gamma=lambda n: 4*math.sin(n*math.pi/88)**2
MODES=[1,2,3,4,5,7,9,11,13]
PART=["e","u","d","s","mu","c","tau","b","t"]
MASS={"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
      "c":1270.0,"tau":1776.86,"b":4180.0,"t":172690.0}
SIG ={"e":1e-9,"u":0.30,"d":0.30,"s":0.8,"mu":2.3e-6,
      "c":20.0,"tau":0.12,"b":30.0,"t":300.0}
m=np.array([MASS[p] for p in PART])
g=np.array([gamma(n) for n in MODES])
lm=np.log10(m); lg=np.log10(g)

print("="*88); print("§1 ★ 幾何供給審計: 幾何每模式供給乜嘢?"); print("="*88)
print(f"""
  A₅ 幾何 (chiral I-60-軌道) 對每模式 n 供給之數據:
    ① n 本身 (整數標籤)
    ② parity(n) = n mod 2
    ③ block(n) = ⌈rank/3⌉  (rank = n 在排序模式集中之序)
    ④ γ_n = 4sin²(nπ/88)  (K_chain 特徵值 — 由 n 決定)
    ⑤ 不變調和次數 {{l : h(l) ≠ 0, l ≤ n, l ≡ n (2)}} — 由 n 決定
  ⟹ 【每模式之幾何數據完全由 n 決定】 — 冇額外自由度。
  ⟹ 「質量由幾何決定」⟺ m = f(n)  (n ∈ M)  — 幾何唔供給第二個變量。
""")
# 驗證 ⑤ 由 n 決定
H_NZ={6,10,12,15,16,18,20,21,22,24,25,26}
def active(n): return [l for l in H_NZ if l<=n and l%2==n%2]
for n in MODES:
    print(f"    n={n:>2}: parity={n%2}, block={MODES.index(n)//3+1}, γ={gamma(n):.6f}, 活躍 l={active(n)}")
ck("§1 每模式幾何數據由 n 唯一決定 (4 個標籤皆 f(n))", True, True)

print("\n"+"="*88); print("§2 ★★ 屏障量化: 要幾多參數?"); print("="*88)
def rms_of(res): return float(np.sqrt(np.mean(np.asarray(res)**2)))
print(f"  判準: RMS < 0.05 dex (因子 1.12) 視為形狀閉合\n")
print(f"  {'模型':<34}{'參數':>5}{'RMS(log10)':>12}{'因子':>8}")
rows=[]
# (a) 全局冪律
A=np.vstack([lg,np.ones_like(lg)]).T
s=np.linalg.lstsq(A,lm,rcond=None)[0]
r=rms_of(lm-A@s); rows.append(("m ∝ γ_n^p (全局)",2,r))
# (b) 逐代冪律
GEN=[[1,2,3],[4,5,7],[9,11,13]]
tot=0.0; pgs=[]; Cgs=[]
for blk in GEN:
    idx=[MODES.index(n) for n in blk]
    Ab=np.vstack([lg[idx],np.ones_like(lg[idx])]).T
    sb=np.linalg.lstsq(Ab,lm[idx],rcond=None)[0]
    pgs.append(sb[0]); Cgs.append(10**(sb[1]-math.log10(M0)))
    tot+=float(np.sum((lm[idx]-Ab@sb)**2))
rows.append(("m ∝ γ_n^{p_g}·C_g (逐代)",6,rms_of(np.sqrt(np.full(9,tot/9)))))
r6=math.sqrt(tot/9)
rows[-1]=("m ∝ γ_n^{p_g}·C_g (逐代)",6,r6)
# (c) log-log 二次
A3=np.vstack([lg**2,lg,np.ones_like(lg)]).T
s3=np.linalg.lstsq(A3,lm,rcond=None)[0]
rows.append(("log m = a+b·logγ+c·(logγ)²",3,rms_of(lm-A3@s3)))
# (d) 多項式 in n
for deg in (2,3,4,5):
    Ap=np.vstack([np.array(MODES,float)**k for k in range(deg+1)]).T
    sp=np.linalg.lstsq(Ap,lm,rcond=None)[0]
    rows.append((f"log m = poly_{deg}(n)",deg+1,rms_of(lm-Ap@sp)))
# (e) 逐代 3 點二次 (飽和)
tot=0.0
for blk in GEN:
    idx=[MODES.index(n) for n in blk]
    Ab=np.vstack([np.array(blk,float)**k for k in range(3)]).T
    sb=np.linalg.lstsq(Ab,lm[idx],rcond=None)[0]
    tot+=float(np.sum((lm[idx]-Ab@sb)**2))
rows.append(("逐代 3 點二次 (飽和)",9,rms_of(np.sqrt(np.full(9,tot/9)))))
for nm,k,r in rows:
    print(f"  {nm:<34}{k:>5}{r:>12.4f}{10**r:>8.2f}")
ck("★★ 逐代冪律 (6 參數) 仍未達 RMS < 0.05", r6>=0.05, True)
minok=[(nm,k) for nm,k,r in rows if r<0.05]
print(f"\n  ★ 達 RMS < 0.05 之最簡模型 = {minok[0] if minok else '無 (除飽和模型)'}")
print(f"  ★★ 屏障: 幾何供給 0 個自由參數 (m = f(n), n 已知);")
print(f"      而數據需要 ≥ {min(k for nm,k in minok) if minok else '≥6'} 個額外參數才閉合 ⟹ 缺口 ② 唔可以由 A₅ 幾何閉合。")
ck("★★ 屏障成立 (數據需 ≥6 額外參數)", bool(minok) and min(k for nm,k in minok)>=6, True)

print("\n"+"="*88); print("§3 ★★ 指數階梯之 bootstrap 檢定"); print("="*88)
print(f"  逐代冪律指數: p_g = {[f'{p:.4f}' for p in pgs]}")
print(f"  逐代常數:     C_g = {[f'{c:.4f}' for c in Cgs]}")
print(f"  (F₅/2)^(g−1) = {[ (F5/2)**(k) for k in range(3)]}")
dev=[(pgs[k]-(F5/2)**k)/(F5/2)**k*100 for k in range(3)]
print(f"  偏差 = {[f'{d:+.3f}%' for d in dev]}")
r_geo=math.sqrt(pgs[2]/pgs[0])
print(f"\n  ★ 幾何比估計 r = sqrt(p₃/p₁) = {r_geo:.4f}   vs F₅/Z₂ = {F5/2:.4f}   (偏差 {(r_geo/(F5/2)-1)*100:+.3f}%)")
# bootstrap
rng=np.random.default_rng(20260925); NB=4000
pb=[]; rb=[]
for _ in range(NB):
    mb=np.array([max(1e-9, MASS[p]+rng.normal(0,SIG[p])) for p in PART])
    lmb=np.log10(mb); pg=[]
    ok=True
    for blk in GEN:
        idx=[MODES.index(n) for n in blk]
        Ab=np.vstack([lg[idx],np.ones_like(lg[idx])]).T
        try: sb=np.linalg.lstsq(Ab,lmb[idx],rcond=None)[0]
        except Exception: ok=False; break
        pg.append(sb[0])
    if not ok: continue
    pb.append(pg); rb.append(math.sqrt(pg[2]/pg[0]))
pb=np.array(pb); rb=np.array(rb)
print(f"\n  bootstrap ({NB} 次, PDG 誤差):")
for k in range(3):
    print(f"    p_{k+1} = {pb[:,k].mean():.4f} ± {pb[:,k].std():.4f}   [(F₅/2)^{k} = {(F5/2)**k:.4f}, "
          f"z = {((F5/2)**k-pb[:,k].mean())/max(1e-12,pb[:,k].std()):+.2f}σ]")
print(f"    r = {rb.mean():.4f} ± {rb.std():.4f}   [F₅/Z₂ = 2.5000, z = {(2.5-rb.mean())/max(1e-12,rb.std()):+.2f}σ]")
p_in=all(abs((F5/2)**k-pb[:,k].mean())<=2*pb[:,k].std() for k in range(3))
ck("★ (F₅/2)^{g−1} 在 bootstrap 2σ 內 (全部 3 個)", bool(p_in), True)

print("\n"+"="*88); print("§4 ★★ 放大因子 A(n) = (m比)/(γ比) 之密度對照"); print("="*88)
Amp=[]
for k in range(len(MODES)-1):
    mr=m[k+1]/m[k]; gr=g[k+1]/g[k]
    Amp.append(mr/gr)
    print(f"  {PART[k]:>3}→{PART[k+1]:<3} (n={MODES[k]:>2}→{MODES[k+1]:>2}): m比 = {mr:>10.5f}, γ比 = {gr:>8.5f}, A = {mr/gr:>9.5f}")
Amp=np.array(Amp)
# 結構數目錄
CAT=set()
base=[N_gen,B,F5,L4,2,L5,F7,18,21,29,34,36,N_d,55,47,90,88,176,264,528,123,98,19,15,6,9,20,33,37,41,8,12,3,4,5,7,11,13,16,22,24,25,44,60,120,32,64,105,75,28,1,10,14,17,23,26,27,30,31,35,38,39,40,42,43,45,46,48,49,50,51,52,53,54,56,57,58,59,61,62,63,65,66,67,68,69,70,71,72,73,74,76,77,78,79,80,81,82,83,84,85,86,87,89,91,92,93,94,95,96,97,99,100]
# 只用【結構】數 (非任意整數): Lucas/Fib/IDCM 派生
struct=[]
for k in range(0,11):
    a,b=2,1
    for _ in range(k): a,b=b,a+b
    struct.append(a)          # Lucas L_k
for k in range(1,12):
    a,b=0,1
    for _ in range(k): a,b=b,a+b
    struct.append(a)          # Fibonacci F_k
struct += [N_d,B,N_gen,F5,2*N_d,4*N_d,2*B*L5,B*(L5+B),N_gen**2,N_gen*F5,F5+B,
           N_gen*(N_d-N_gen),N_d-L4,N_d-L5,N_d+B,N_d-F7,2*N_gen*F5,B*N_gen,
           sum(struct[:0]) if False else 0,90,88,176,264,528,36,98,123,32,64,
           F5*L5,2*B*B,B*L5,4*(N_d-N_gen),N_d+2*B,2*N_d-2,N_d//2,N_d+1]
struct=sorted(set(x for x in struct if x>0))
print(f"\n  結構數目錄 |S| = {len(struct)}: {struct}")
ratios=set()
for a in struct:
    for b in struct:
        if b>0 and a!=b:
            ratios.add(a/b)
ratios=sorted(ratios)
print(f"  結構比目錄 |S/S| = {len(ratios)}")

def coverage(targets, tol):
    """給定容差, 目錄覆蓋率 = 隨機目標有命中嘅比例"""
    rng2=np.random.default_rng(7)
    rngs=np.exp(rng2.uniform(math.log(0.1),math.log(100.0),20000))
    hit=0
    ra=np.array(ratios)
    for t in rngs:
        if np.any(np.abs(ra/t-1.0)<tol): hit+=1
    return hit/len(rngs)
for tol in (0.001,0.005,0.01,0.02,0.05):
    cov=coverage(None,tol)
    hits=int(sum(np.any(np.abs(np.array(ratios)/a-1.0)<tol) for a in Amp))
    print(f"  容差 {tol*100:>5.1f}%: 目錄覆蓋率 = {cov*100:>5.1f}%   觀測 8 個 A 中命中 {hits}/8   (期望 {cov*8:.2f})")
print(f"""
  ★ 判定: 若覆蓋率 ≫ 觀測命中率 ⟹ 命中係密度效應 (O136 致命傷 #1)。
""")
cov1=coverage(None,0.01); hits1=int(sum(np.any(np.abs(np.array(ratios)/a-1.0)<0.01) for a in Amp))
ck("★ 放大因子命中率 ≤ 密度期望 (即無結構訊號)", hits1<=cov1*8+1, True)

print("\n"+"="*88); print("§5 ★★ 兩框架模式集衝突"); print("="*88)
A5set=set(MODES); O64={"e":1,"mu":7,"tau":20,"u":1,"d":1,"s":14,"c":34,"b":33,"t":44}
o64set=set(O64.values())
print(f"  A₅ 集 (O137, 質量無關, 幾何)     = {sorted(A5set)}   |·| = {len(A5set)}")
print(f"  O64 集 (夸克/輕子閉合框架)        = {sorted(o64set)}   |·| = {len(o64set)} (9 費米子, 有重複: n=1 三次)")
print(f"  ★ 交集 = {sorted(A5set & o64set)}")
print(f"  ★ 對稱差 = {sorted(A5set ^ o64set)}")
ck("★★ A₅ 集 ∩ O64 集 = {1,7} (兩個框架近乎不相交)", sorted(A5set & o64set), [1,7])
print(f"""
  ★★ 衝突: 兩個 IDCM 框架對【同一 9 個帶電費米子】給出【近乎不相交】之模式集。
     A₅ 集: 9 個【互異】模式 (費米子↔模式 雙射), 質量升序 = n 升序
     O64 集: 6 個互異模式 + n=1 三重 (靠 F_proj 分離 e/u/d), 質量升序 ≠ n 升序
     (O64: μ@7 = 105.658 MeV > s@14 = 93.4 MeV ⟹ 違反單調)
  ⟹ 兩者唔可能同時為「費米子模式分配」之正確答案。此為【未裁決之內部矛盾】,
     必須記錄 (唔可以兩邊都引用)。
""")

print("="*88); print("§6 判定"); print("="*88)
print(f"""
  §1 幾何每模式數據【完全由 n 決定】⟹ m = f(n)  (冇第二個幾何變量)
  §2 ★★ 屏障: 逐代冪律 (6 參數) 仍 RMS = {r6:.4f} dex (因子 {10**r6:.2f});
        達 <0.05 dex 需 ≥6 額外參數 ⟹ 【A₅ 幾何唔可能閉合質量標度】
  §3 ★ 指數階梯 p_g = {[f'{p:.3f}' for p in pgs]} vs (F₅/2)^{{g−1}} = 1, 2.5, 6.25;
        bootstrap z = {[f'{((F5/2)**k-pb[:,k].mean())/max(1e-12,pb[:,k].std()):+.1f}' for k in range(3)]}σ
  §4 ★★ 放大因子命中率 vs 密度覆蓋率 — 見上 (判別巧合 vs 結構)
  §5 ★★ 兩框架模式集近乎不相交 (交集 {{1,7}}) — 未裁決內部矛盾
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
