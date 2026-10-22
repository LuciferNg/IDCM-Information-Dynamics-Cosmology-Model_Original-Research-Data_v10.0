#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/23 (R5-②) — 凍結形式類 𝒞 之枚舉（形式非唯一性 vs 收斂於 B = 4）
★ 合約: docs/26_r5_contract.md §B R5-②   ★ 類別凍結於跑數前，跑數後一字不改
"""
import json, os, itertools
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
b=sp.Symbol('B', positive=True)
p("="*78); p("O229/23 (R5-②) — 凍結形式類 𝒞 之枚舉（目標 137, B = 4）"); p("="*78)

# --- 凍結基 ℱ（合約 §B R5-② 逐字） ---
FUN={ "1":sp.Integer(1), "B":b, "B−1":b-1, "B+1":b+1, "2B":2*b, "B(B−1)":b*(b-1),
      "B²":b**2, "B³":b**3, "B⁴":b**4, "B²(B−1)²":b**2*(b-1)**2, "B²+1":b**2+1, "B⁴+B²":b**4+b**2,
      "C(B,2)":sp.binomial(b,2), "C(B²,2)":sp.binomial(b**2,2), "2^B":2**b,
      "L₄=7":sp.Integer(7), "L₅=11":sp.Integer(11), "L₅²=121":sp.Integer(121), "N_gen=3":sp.Integer(3),
      "N_gen²=9":sp.Integer(9), "μ²=2":sp.Integer(2), "N_d=44":sp.Integer(44), "N_site=88":sp.Integer(88),
      "Σγ=90":sp.Integer(90), "L₁₀=123":sp.Integer(123), "F₇=13":sp.Integer(13), "F₁₁=89":sp.Integer(89),
      "12":sp.Integer(12), "17":sp.Integer(17), "144":sp.Integer(144) }
names=list(FUN); exprs={k:FUN[k] for k in names}
p(f"\n[1] 凍結基 ℱ: {len(names)} 項 ⟹ 項集 = {{±1,±2}} × ℱ")
val4={k:int(FUN[k].subs(b,4)) for k in names}
hasB={k:(b in FUN[k].free_symbols) for k in names}
RAW=[(c,k,c*val4[k],c*exprs[k]) for k in names for c in (1,-1,2,-2)]
def canon_groups(raw):
    groups=[]
    for c,k,v,e in raw:
        ee=sp.expand(e); placed=False
        for g in groups:
            if sp.simplify(ee-g[0])==0: g[1].append((c,k,v,e)); placed=True; break
        if not placed: groups.append((ee,[(c,k,v,e)]))
    return groups
G=canon_groups(RAW)
COLL=[g for g in G if len(g[1])>1]
TT=[g[1][0] for g in G]
p(f"    字面項數 = {len(RAW)}；expand-正則 = {len({sp.srepr(sp.expand(x[3])) for x in RAW})}；"
  f"**函數正則（本輪採用）** = {len(TT)}")
p(f"    ⚠️ 符號陷阱: {len(COLL)} 組重複（同一函數被多記）:")
for g in COLL: p("      "+"  ≡  ".join(f"{c}·{k}" for c,k,_,_ in g[1]))
p(f"    配對/三元組 = {len(TT)*(len(TT)-1)//2} / {len(TT)*(len(TT)-1)*(len(TT)-2)//6}")
chk("T1 三種讀數已記錄（字面 120 / expand-正則 114 / 函數正則 112）",
    len(RAW)==120 and len(TT)==112, f"{len(RAW)}/{len({sp.srepr(sp.expand(x[3])) for x in RAW})}/{len(TT)}")
chk("T2 符號陷阱 = 8 組（含 1·B(B−1) ≡ 2·C(B,2)、2·1 ≡ 1·μ²、2·B ≡ 1·2B、2·N_d ≡ 1·N_site）",
    len(COLL)==8 and len({frozenset((a[0],a[1]) for a in g[1]) for g in COLL})==8)

TARGET=137; hits=[]
p(f"\n[2] 枚舉 2 項與 3 項形式（f 互不相同），篩 f(B=4) = {TARGET}")
for n in (2,3):
    for comb in itertools.combinations(range(len(TT)),n):
        if sum(TT[i][2] for i in comb)!=TARGET: continue
        hits.append(tuple(comb))
p(f"    命中形式數 #forms = {len(hits)}")
by_n={}
for h in hits: by_n[len(h)]=by_n.get(len(h),0)+1
p(f"    項數分佈: {by_n}")
chk("B1 #forms(137) ≥ 3", len(hits)>=3, f"#forms = {len(hits)}")
chk("B3 項數分佈已記錄（2 項 / 3 項）", sum(by_n.values())==len(hits), f"{by_n}")

# --- 收斂: 含 B 之形式解 B ---
p("\n[3] 收斂檢驗: 含 B 之形式 f(B) = 137 之正整數解")
def solve_forms(hitlist):
    out=[]
    for h in hitlist:
        expr=sp.expand(sum(TT[i][3] for i in h))
        if b not in expr.free_symbols: continue
        desc=" + ".join(f"{TT[i][0]:+d}·{TT[i][1]}" for i in h)
        diff=sp.expand(expr-TARGET)
        roots=[]
        try:
            if diff.free_symbols<= {b} and diff.is_polynomial(b):
                poly=sp.Poly(diff,b)
                for r in sp.real_roots(poly):
                    rf=float(sp.N(r,30))
                    if rf>0 and abs(rf-round(rf))<1e-25: roots.append(int(round(rf)))
            else:
                for Bv in range(1,10001):
                    if int(expr.subs(b,Bv))==TARGET: roots.append(Bv)
        except Exception as e:
            roots=["ERR:"+str(e)[:30]]
        out.append((desc,sorted(set(roots)),expr))
    return out
sols=solve_forms(hits)
uniq4=[s for s in sols if s[1]==[4]]
p(f"    含 B 之命中形式數 = {len(sols)}；其中**唯一正整數解 = 4** 者 = {len(uniq4)}")
chk("B2 含 B 之形式 ≥ 3 且全部之唯一正整數解 = 4",
    len(sols)>=3 and len(uniq4)==len(sols), f"含B {len(sols)} / 收斂 {len(uniq4)}")
p("\n[4] B4 純結構命中形式（示例，最少 4 個）")
shown=[]
for desc,rt,ex in uniq4[:8]:
    p(f"    {desc} = 137   （正整數解 {rt}）"); shown.append(desc)
chk("B4 至少 4 個純結構命中形式（未經擬合）", len(uniq4)>=4, f"{len(uniq4)}")
def _d24():
    try:
        return json.load(open(os.path.join(BASE,"data","24_r5_discrimination.json"),encoding="utf-8"))
    except Exception:
        return None
_D=_d24()
chk("B5 [c] #forms(137) 與 scripts/24 之 express(137) 一致（跨腳本核對；24 需先跑）",
    _D is not None and _D["express"]["137"]==len(hits), f"23 = {len(hits)}；24 = {None if _D is None else _D['express']['137']}")
chk("B6 [c] 收斂數與 scripts/24 之 lock(137) 一致（real_roots 精確 vs Cauchy 掃描）",
    _D is not None and _D["lock"]["137"]==len(uniq4), f"23 = {len(uniq4)}/{len(sols)}；24 = {None if _D is None else _D['lock']['137']}")
V=(f"★ R5-②（函數正則類，{len(TT)} 項）: 命中 137 之形式 **#forms = {len(hits)}**"
   f"（2 項 {by_n.get(2,0)}／3 項 {by_n.get(3,0)}）；含 B 者 {len(sols)} 個，其中**唯一正整數解 = 4** 者 {len(uniq4)} 個。\n"
   f"★ 兩面結論: (i) 端點鎖之**形式非唯一**（{len(hits)} 個形式給同一值）；(ii) 但含 B 之形式中只有 {len(uniq4)} 個以 B = 4 為**唯一**解，"
   f"其餘有額外正整數解 ⟹ 收斂係**局部**（{len(uniq4)}/{len(sols)}），並非全體過定。\n"
   f"★ 符號陷阱（本輪自捉）: ℱ 內部有 8 組同一函數之重複表示（2·1 ≡ μ²、2·B ≡ 2B、2·N_d ≡ N_site、1·B(B−1) ≡ 2·C(B,2) 各 ±）；"
   f"字面讀數 120 項／expand 正則 114 項／**函數正則 112 項**。舊（114 項）之 281/239 已作廢，保留於 logs/23_r5_form_class.pre_correction.out。")
p("\n★ R5-② 判決"); p(V)
np_,nf_=res()
json.dump({"script":"23_r5_form_class","pass":np_,"fail":nf_,"total":np_+nf_,
  "frozen_basis":names,"n_terms_dedup":len(TT),"target":TARGET,"forms_hits":len(hits),
  "by_n":by_n,"withB":len(sols),"converged_B4":len(uniq4),
  "examples":[[d,rt] for d,rt,_ in uniq4[:12]],"verdict":V},
  open(os.path.join(BASE,"data","23_r5_form_class.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","23_r5_form_class.out"),"w").write("\n".join(OUT)+"\n")
