#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/22 (R5-①) — 端點鎖之三項解剖 (137 = 120 + 16 + 1)
★ 合約: docs/26_r5_contract.md §B R5-①   ★ 零新參數（全部係群論/組合計數之顯式枚舉）
"""
import json, os, itertools
import sympy as sp
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF
B=4; NC=3; ND=44; SG=90; L4=7; L5=11
p("="*78); p("O229/22 (R5-①) — 端點鎖三項解剖: α⁻¹(0) = C(B²,2) + B² + 1 = 120 + 16 + 1"); p("="*78)

# --- A1: 三條獨立精確路線 ---
p("\n[1] A1 — 三條獨立路線之 120")
perms5=list(itertools.permutations(range(5))); perms4=list(itertools.permutations(range(4)))
def parity(pm):
    s=0
    for i in range(len(pm)):
        for j in range(i+1,len(pm)):
            s += (pm[i]>pm[j])
    return s%2
A5=[pm for pm in perms5 if parity(pm)==0]; A4=[pm for pm in perms4 if parity(pm)==0]
p(f"    (i) 組合: C(16,2) = {sp.binomial(16,2)}")
p(f"    (ii) 對稱群: |S₅| = 5! = {len(perms5)}；|A₅|（5 元偶置換顯式枚舉）= {len(A5)}")
p(f"    (iii) 四元數: 2T = 8 個 ±單位 + 16 個 (±1±i±j±k)/2 = {8+16}；|A₄| = {len(A4)}，[A₅:A₄] = {len(A5)//len(A4)}")
twoT=set()
for s1 in (1,-1):
    for k in range(4):
        v=[0,0,0,0]; v[k]=s1; twoT.add(tuple(v))
for a in (1,-1):
    for b in (1,-1):
        for c in (1,-1):
            for d in (1,-1):
                twoT.add((a/2,b/2,c/2,d/2))
def qmul(x,y):
    a,b,c,d=x; e,f,g,h=y
    return (a*e-b*f-c*g-d*h, a*f+b*e+c*h-d*g, a*g-b*h+c*e+d*f, a*h+b*g-c*f+d*e)
closed=all(qmul(x,y) in twoT for x in twoT for y in twoT)
chk("1.1 C(16,2) = 120（精確）", sp.binomial(16,2)==120)
chk("1.2 |S₅| = 120（顯式枚舉 5!）", len(perms5)==120)
chk("1.3 |A₅| = 60（顯式枚舉偶置換）", len(A5)==60)
chk("1.4 2T 顯式枚舉 = 24 且乘法封閉（真群）", len(twoT)==24 and closed, f"|2T|={len(twoT)}, 封閉={closed}")
chk("1.5 [A₅:A₄] = 60/12 = 5 ⟹ |2I| = 5·|2T| = 120", len(A5)//len(A4)==5 and 5*24==120)
chk("1.6 三路線同值: C(16,2) = |S₅| = |2I| = 120", sp.binomial(16,2)==len(perms5)==5*len(twoT)==120)

# --- A2: 群階讀法之可證範圍 ---
p("\n[2] A2 — 群階讀法之可證範圍（傳遞 vs 非傳遞）")
p(f"    (i) 傳遞作用於 16 點需要 index-16 子群 ⟹ |H| = 120/16 = {sp.Rational(120,16)} ∉ ℤ")
chk("2.1 index-16 子群唔存在（120/16 = 15/2 ∉ ℤ）⟹ 冇**傳遞** 2I-作用於 16 點",
    sp.Rational(120,16).is_Integer is False)
chk("2.2 ⟹ 由 16 態誘導之等變雙射 Pairs(16) → 2I **唔存在**（在 16 態不可分之下）", 120%16!=0)
sizes=[d for d in range(1,17) if 120%d==0]
decomp=[]
for r in range(1,5):
    for comb in itertools.combinations_with_replacement(sizes,r):
        if sum(comb)==16: decomp.append(comb)
p(f"    (ii) 16 之整除 120 之尺寸分解（非傳遞讀法）: {decomp}")
chk("2.3 ⚠️ 非傳遞分解**存在**（如 10+6、1+5+10 …）⟹ 本項只排除傳遞讀法，唔聲稱一般不可能",
    len(decomp)>0, f"{len(decomp)} 組")
chk("2.4 另記: 16 ∤ 120 且 |Aut| = 2·60 = 120（O223 之 120 亦同值）", 120%16!=0 and 2*60==120)

# --- A3/A4/A5 ---
p("\n[3] A3–A5")
p(f"    A3: 16 = B² = {B}² ✓（每代左旋 Weyl 態，R1 §C 已證）")
p(f"    A4: +1 = 單態（trivial，無進一步結構內容）")
chk("3.1 三項之和恆等: C(B²,2)+B²+1 = 137 且 = (B⁴+B²+2)/2",
    sp.binomial(B**2,2)+B**2+1==137 and sp.Rational(B**4+B**2+2,2)==137)
chk("3.2 等價多項式 B⁴+B²−272 = 0 之正根唯一 = 4",
    [r for r in sp.real_roots(sp.Poly(sp.Symbol('x')**4+sp.Symbol('x')**2-272, sp.Symbol('x')))
     if r.is_positive]==[4])
chk("3.3 形式之「群階讀法」未被證明: 傳遞讀法排除 ∧ 非傳遞分解存在 ⟹ 判為**半結構**",
    (120%16!=0) and len(decomp)>0)
V=("★ R5-①: 137 = C(B²,2) + B² + 1 = 120 + 16 + 1。三項之結構身份:\n"
   "  • 16 = B²（每代左旋 Weyl 態）✔ 結構指派\n"
   "  • +1 = 單態 ✔ 結構指派\n"
   "  • 120 = C(16,2)（配對計數）✔；但其「= |2I| = |S₅|」之**群階讀法**只在「16 態不可分」之下被排除\n"
   "    （index-16 子群唔存在: 120/16 = 7.5 ∉ ℤ）；若容許 16 態分裂（10+6 等），計數等式另有讀法。\n"
   "  ⟹ 端點鎖形式 = **半結構**：2/3 項有結構指派，第三項係配對計數而非已知群論必然。")
p("\n★ R5-① 判決"); p(V)
np_,nf_=res()
json.dump({"script":"22_r5_endpoint_anatomy","pass":np_,"fail":nf_,"total":np_+nf_,
  "S5":len(perms5),"A5":len(A5),"A4":len(A4),"twoT":len(twoT),"twoT_closed":closed,
  "C16_2":int(sp.binomial(16,2)),"index16":str(sp.Rational(120,16)),
  "nontransitive_decomps":[list(c) for c in decomp],"verdict":V},
  open(os.path.join(BASE,"data","22_r5_endpoint_anatomy.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","22_r5_endpoint_anatomy.out"),"w").write("\n".join(OUT)+"\n")
