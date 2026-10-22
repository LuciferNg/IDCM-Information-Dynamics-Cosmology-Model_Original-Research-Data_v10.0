#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/16 (R3-④) — 端點鎖之密度誠實界：連續區間 vs 原子池
★ 合約: docs/14_r3_contract.md §A R3-④
"""
import json, os, math
from fractions import Fraction as Fr
import sympy as sp
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF
ATOMS=[1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
CAP=400
p("="*78); p("O229/16 (R3-④) — 端點形式家族之判別力（R1 1.25% 之重新評估）"); p("="*78)

form=lambda k: math.comb(k*k,2)+k*k+1
p("\n[1] R3-④ D1: 形式家族 k ↦ C(k²,2)+k²+1 之小 k 值")
rows=[]
for k in range(1,20):
    v=form(k)
    if v>CAP*1000: break
    rows.append((k,v,v in ATOMS))
    p(f"    k={k:2d} → {v:<8d} {'★原子' if v in ATOMS else '（非原子）'}")
small=[(k,v) for k,v,a in rows if v<=CAP]
hits=[(k,v) for k,v in small if v in ATOMS]
chk("1.1 ≤400 之形式值 = 5 個: k = 1..5 → {2, 11, 46, 137, 326}", len(small)==5,
    f"{small}")
chk("1.2 其中 k = 1,2,3,4 之值 {2, 11, 46, 137} 皆為原子（= μ², L₅, Σγ_even, α⁻¹(0)）",
    [k for k,v in hits]==[1,2,3,4], f"{hits}")
chk("1.3 k = 5 → 326 非原子（形式家族之原子性在 k = 5 斷）", form(5)==326 and 326 not in ATOMS)
chk("1.4 ★ 前綴封閉: k = 1,2,3,4 **全部**落於原子表 ⟹ 4/4 = 100%",
    all(form(k) in ATOMS for k in (1,2,3,4)))

p("\n[2] R3-④ D2: 原子池前驗下之判別力")
pool=[a for a in ATOMS if a<=CAP]
num=len([k for k in pool if form(k) in ATOMS])
q_atom=Fr(num,len(pool))
p(f"    池 = 原子表 ∩ [1,{CAP}] ⟹ |池| = {len(pool)}（最大原子 {max(ATOMS)} ≤ {CAP}）")
p(f"    命中 = {num}（k = {[k for k in pool if form(k) in ATOMS]}）⟹ q_atom = {num}/{len(pool)} = {float(q_atom)*100:.2f}%")
q_r1=Fr(5,CAP-1)
p(f"    R1 之連續區間前驗: q_R1 = 5/{CAP-1} = {float(q_r1)*100:.3f}%")
chk("2.1 q_atom ≫ q_R1（原子池前驗下判別力**更弱**）", q_atom > q_r1,
    f"{float(q_atom)*100:.2f}% vs {float(q_r1)*100:.3f}%")
chk("2.2 q_atom ≈ 12%（預註冊寫 4/33；實測 4/34，分母係全部原子 ⟹ 預註冊算術瑕疵）",
    abs(q_atom-Fr(4,34))==0, f"q_atom = {q_atom} = {float(q_atom)*100:.2f}%")
chk("2.3 量級結論與預註冊一致: q_atom ∈ [0.11, 0.13]（≫ 1.25%）", Fr(11,100) < q_atom < Fr(13,100))
chk("2.4 ★ 判別力評估: 「端點鎖命中 137」之條件機率 ≈ 12% ⟹ **接近零判別力**（非「邊緣顯著」）",
    float(q_atom)>0.10)

p("\n[3] R3-④ D3: 端點鎖之精確性**不受**本項影響")
Bs=sp.Symbol('Bs',positive=True)
poly=Bs**4+Bs**2-272
roots=[r for r in sp.solve(poly,Bs) if r.is_real and r>0]
chk("3.1 B⁴+B²−272 = 0 之正根唯一 = 4（精確）", roots==[sp.Integer(4)])
chk("3.2 端點形式於 k = 4 ⟹ C(16,2)+16+1 = 137 = α⁻¹(0)（精確）", form(4)==137)
chk("3.3 形式 ≡ 端點鎖代數: C(k²,2)+k²+1 = (k⁴+k²+2)/2 ⟹ k⁴+k²−272 = 0",
    sp.simplify(sp.binomial(Bs**2,2)+Bs**2+1-(Bs**4+Bs**2+2)/2)==0)
V=("★ R3-④: 端點形式家族 `k ↦ C(k²,2)+k²+1` 對 **k = 1,2,3,4 全部**落於原子表"
   "（`2, 11, 46, 137` = `μ², L₅, Σγ⁽⁸⁸⁾_even, α⁻¹(0)`），k = 5 → 326 才斷。"
   "以**原子池**為前驗（`B = 4` 本身係原子，故池 = 34 原子）⟹ q_atom = **4/34 = 11.76%**，"
   "**≫** R1 之連續區間值 5/399 = 1.253%。")
p("\n★ R3-④ 判決"); p(V)
p("⟹ R1 之 🟡「邊緣顯著」應**下修**為：端點鎖之判別力**接近零**（命中 137 係原子值家族之第 4 員，唔係孤立巧合）；")
p("  端點鎖之**精確性**（B = 4 唯一）不受影響，但其「似非巧合」之量化唔成立。")
np_,nf_=res()
json.dump({"script":"16_r3_density_atom_pool","pass":np_,"fail":nf_,"total":np_+nf_,
           "form_values":[[k,v,(v in ATOMS)] for k,v in small],
           "pool_size":len(pool),"hits":num,"q_atom":[num,len(pool)],"q_R1":[5,CAP-1],
           "prefix_closure":[form(k) for k in (1,2,3,4)],"verdict":V},
          open(os.path.join(BASE,"data","16_r3_density_atom_pool.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","16_r3_density_atom_pool.out"),"w").write("\n".join(OUT)+"\n")
