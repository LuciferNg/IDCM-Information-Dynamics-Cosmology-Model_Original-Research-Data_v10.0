#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/20 (R4-③) — R1 四硬測試之重審（重點：10⁷ MC null 之池選擇）
★ 合約: docs/20_r4_contract.md §A R4-③   ★ 零新參數
★ 本檔**忠實重建** R1 scripts/07 §5 之 null（同 RNG 演算法、同 seed、同 10⁷、同 3 鎖），
  再以 R3-④ 之結構性池（原子池）重跑；兩池並報。
"""
import json, os, math
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=50
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF
M64=(1<<64)-1
class SM64:                                     # 與 R1 scripts/07 逐字節相同之 splitmix64
    def __init__(self,seed): self.s=seed&M64
    def next(self):
        self.s=(self.s+0x9E3779B97F4A7C15)&M64
        z=self.s
        z=((z^(z>>30))*0xBF58476D1CE4E5B9)&M64
        z=((z^(z>>27))*0x94D049BB133111EB)&M64
        return z^(z>>31)
ATOMS=[1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
E={k: math.comb(k*k,2)+k*k+1 for k in range(2,9)}
K=10_000_000
def zsig(q): return float(mp.sqrt(2)*mp.erfinv(1-2*mp.mpf(q)))
p("="*78); p("O229/20 (R4-③) — 硬測試重審: 寬池 vs 結構池（原子池）"); p("="*78)

p("\n[1] R4-③ C1: 忠實重建 R1 之寬池 null（同 seed 229、同 10⁷、同 3 鎖、同抽取次序）")
rng=SM64(229); hits=0; Bsols=set()
for _ in range(K):
    a0=100+rng.next()%101; Nd=20+rng.next()%61; L5=5+rng.next()%26; sp_=4+rng.next()%61
    k=math.isqrt(sp_)
    if k*k!=sp_ or k<2: continue
    if E.get(k,-1)!=a0: continue
    if k*L5!=Nd: continue
    hits+=1; Bsols.add(k)
q_wide=hits/K
p(f"    樣本 = {K:,}；命中 = {hits}；q_wide = {q_wide:.3e}   B' 集 = {sorted(Bsols)}")
chk("1.1 復現 R1 之 q_wide ≈ 1.30e-06（±20%）", abs(q_wide-1.30e-6)/1.30e-6<=0.20, f"{q_wide:.3e}")
# 精確有理值（獨立於 MC）
q_wide_x=Fr(1,61)*Fr(1,101)*Fr(16,26)*Fr(1,61)     # (spinor=16) × (a0=137) × (L5∈[5,20]) × (Nd=4L5)
p(f"    精確有理值 = {q_wide_x} = {float(q_wide_x):.4e}（MC 抽樣一致）")
chk("1.2 精確值與 MC 一致（泊松 z < 3）",
    abs(hits-int(q_wide_x*K))/math.sqrt(max(1,q_wide_x*K))<3.0,
    f"期望 {q_wide_x*K:.1f}, 實測 {hits}")
p(f"    ⟹ 寬池等效顯著性 z = {zsig(float(q_wide_x)):.2f}σ")

p("\n[2] R4-③ C2: 結構池 null（全部量只可取自 IDCM 原子表）")
A4=[a for a in ATOMS if 4<=a<=64]; A100=[a for a in ATOMS if 100<=a<=200]
A20=[a for a in ATOMS if 20<=a<=80]; A5=[a for a in ATOMS if 5<=a<=30]
p(f"    spinor' ∈ ATOMS∩[4,64]  ({len(A4)} 值): {A4}")
p(f"    α⁻¹(0)' ∈ ATOMS∩[100,200] ({len(A100)} 值): {A100}")
p(f"    N_d' ∈ ATOMS∩[20,80]   ({len(A20)} 值)   L₅' ∈ ATOMS∩[5,30] ({len(A5)} 值)")
rng2=SM64(229); hits2=0; ksols=set()
for _ in range(K):
    a0=A100[rng2.next()%len(A100)]; Nd=A20[rng2.next()%len(A20)]
    L5=A5[rng2.next()%len(A5)];      sp_=A4[rng2.next()%len(A4)]
    k=math.isqrt(sp_)
    if k*k!=sp_ or k<2: continue
    if E.get(k,-1)!=a0: continue
    if k*L5!=Nd: continue
    hits2+=1; ksols.add(k)
q_atom=hits2/K
p(f"    樣本 = {K:,}；命中 = {hits2}；q_atom = {q_atom:.3e}   k 集 = {sorted(ksols)}")
chk("2.1 q_atom ≥ 1e-4（≥ 77× 寬池）", q_atom>=1e-4, f"{q_atom:.3e} vs 1.30e-6 ⟹ {q_atom/1.30e-6:.1f}×")
chk("2.2 q_atom ≤ 0.1", q_atom<=0.1, f"{q_atom:.3e}")
tbl=[]
for k in (2,4,6):
    sp_=k*k
    if sp_ not in A4: continue
    pl=Fr(1,len(A4))*Fr(1,len(A100))*(Fr(1,len(A5)) if E[k] in A100 else 0)*(Fr(1,len(A20)) if E[k] in A100 else 0)
    tbl.append((k,sp_,E[k],E[k] in A100))
    p(f"    k = {k}: spinor' = {sp_}, E[k] = {E[k]}, E[k] ∈ A100 = {E[k] in A100}"
      f"  ⟹ 該支之機率 = {pl}")
q_atom_x=Fr(1,len(A4))*Fr(1,len(A100))*Fr(2,len(A5))*Fr(1,len(A20))
p(f"    精確有理值 = {q_atom_x} = {float(q_atom_x):.4e}（k = 4 支 × L₅' ∈ {{11,19}}）")
chk("2.3 精確值與 MC 一致（泊松 z < 3）",
    abs(hits2-int(q_atom_x*K))/math.sqrt(max(1,q_atom_x*K))<3.0,
    f"期望 {q_atom_x*K:.1f}, 實測 {hits2}")
p(f"    ⟹ 結構池等效顯著性 z = {zsig(float(q_atom_x)):.2f}σ")

p("\n[3] R4-③ C3: 鎖之間之相依性")
m1=Fr(1,len(A4))*Fr(1,len(A100))                        # 端點鎖（k = 4 唯一）
m2=Fr(4,len(A5))*Fr(1,len(A20))                         # k·L₅' = N_d'（k = 2 或 4 各 2 個 L₅'）
p(f"    邊際 m1 = {m1} = {float(m1):.3e}（端點鎖）")
p(f"    邊際 m2 = {m2} = {float(m2):.3e}（算術鎖）")
p(f"    乘積 m1·m2 = {m1*m2} = {float(m1*m2):.3e}   聯合 q_atom = {q_atom_x} = {float(q_atom_x):.3e}")
chk("3.1 ★ 預註冊「正相關（聯合 > 乘積）」", q_atom_x>m1*m2,
    f"實測 聯合 ({float(q_atom_x):.3e}) < 乘積 ({float(m1*m2):.3e}) ⟹ **負相依**，預註冊 FAIL 原樣保留")
chk("3.2 [c] 正確陳述: 聯合 = (1/2)·乘積 ⟹ 負相依；機制 = 端點鎖**強制** k = 4，"
    "殺死 k = 2 支（該支可滿足算術鎖但 E[2] = 11 ∉ A100）",
    q_atom_x==m1*m2/2, f"比值 聯合/乘積 = {q_atom_x/(m1*m2)} = 1/2")

p("\n[4] R4-③ C4: 「遠超 5σ」之重審")
zw=zsig(float(q_wide_x)); za=zsig(float(q_atom_x))
p(f"    寬池 z = {zw:.2f}σ    結構池 z = {za:.2f}σ")
chk("4.1 ★ 「遠超 5σ 級」之聲稱（結構池下）", za>=5.0,
    f"結構池 z = {za:.2f}σ < 5 ⟹ 聲稱對池敏感、須下修 ⟹ 預註冊 FAIL 原樣保留")
chk("4.2 [c] 正確陳述: 寬池 {:.2f}σ / 結構池 {:.2f}σ；兩池**必須並報** ——".format(zw,za)+
    "寬池答「若數字任意則幾罕見」，結構池答「在 IDCM 自身數字系統內有幾大約束」", 3.0<za<5.0)
chk("4.3 比值 q_atom/q_wide = {}×（級數差 = 判別力對池之敏感度）".format(round(float(q_atom_x/q_wide_x),1)),
    60<float(q_atom_x/q_wide_x)<120, f"{float(q_atom_x/q_wide_x):.1f}×")
V=("★ R4-③: R1 之「10⁷ MC null ⟹ q_obs = 1.30e-06，遠超 5σ 級」**忠實復現**（同 RNG/seed/次序/命中數 13），"
   "但同一 3 鎖在**結構池**（全部量取自 34 原子）下 q_atom = 2/15015 = 1.332e-04 ⟹ **81× 寬**（精確比）、99×（MC 比）、"
   "等效顯著性由 **4.65σ（寬池精確）降至 3.65σ（結構池）**。\n"
   "★★ 更關鍵: 連**寬池自身**之精確值 8/4885673 = 1.637e-06 亦只對應 **4.65σ < 5σ** ⟹ "
   "R1 之「遠超 5σ」在兩種池下皆**唔成立**，須下修為「~4.7σ（寬池）/ ~3.6σ（結構池）」。\n"
   "★ 另發現: 鎖之間為**負相依**（聯合 = ½·乘積）：端點鎖強制 k = 4，殺死 k = 2 支。")
p("\n★ R4-③ 判決"); p(V)
np_,nf_=res()
json.dump({"script":"20_r4_hardtest_reaudit","pass":np_,"fail":nf_,"total":np_+nf_,
           "wide":{"hits":hits,"q":q_wide,"q_exact":str(q_wide_x),"z":zsig(float(q_wide_x))},
           "atom":{"hits":hits2,"q":q_atom,"q_exact":str(q_atom_x),"z":zsig(float(q_atom_x)),
                   "pools":{"A4":A4,"A100":A100,"A20":len(A20),"A5":len(A5)}},
           "dependence":{"m1":str(m1),"m2":str(m2),"joint_over_product":str(q_atom_x/(m1*m2))},
           "ratio_exact":float(q_atom_x/q_wide_x),"ratio_mc":q_atom/q_wide,"verdict":V},
          open(os.path.join(BASE,"data","20_r4_hardtest_reaudit.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","20_r4_hardtest_reaudit.out"),"w").write("\n".join(OUT)+"\n")
