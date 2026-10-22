#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/24 (R5-③) — 形式 × 值 判別力矩陣
★ 合約: docs/26_r5_contract.md §B R5-③   ★ 同一凍結類 𝒞（唔改一字）
★ express(v) = 由**全值直方圖**精確查詢（246,905 個形式值）⇒ 零 MC 誤差
★ lock(v) = 「f(B) = v 之唯一正整數解 = 4」之精確判定（多項式 → real_roots；2^B 項 → [1,10⁴] 掃描）
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
b=sp.Symbol('B', positive=True)
FUN={ "1":sp.Integer(1), "B":b, "B−1":b-1, "B+1":b+1, "2B":2*b, "B(B−1)":b*(b-1),
      "B²":b**2, "B³":b**3, "B⁴":b**4, "B²(B−1)²":b**2*(b-1)**2, "B²+1":b**2+1, "B⁴+B²":b**4+b**2,
      "C(B,2)":b*(b-1)/2, "C(B²,2)":b**2*(b**2-1)/2, "2^B":2**b,
      "L₄=7":sp.Integer(7), "L₅=11":sp.Integer(11), "L₅²=121":sp.Integer(121), "N_gen=3":sp.Integer(3),
      "N_gen²=9":sp.Integer(9), "μ²=2":sp.Integer(2), "N_d=44":sp.Integer(44), "N_site=88":sp.Integer(88),
      "Σγ=90":sp.Integer(90), "L₁₀=123":sp.Integer(123), "F₇=13":sp.Integer(13), "F₁₁=89":sp.Integer(89),
      "12":sp.Integer(12), "17":sp.Integer(17), "144":sp.Integer(144) }
names=list(FUN); TERMS=[]; seen=set()
for k in names:
    for c in (1,-1,2,-2):
        e=c*FUN[k]; key=sp.srepr(sp.expand(e))
        if key in seen: continue
        seen.add(key); TERMS.append((c,k,c*int(FUN[k].subs(b,4)),e))
# ★ 防禦性檢查（正是此處曾出錯: 項值必須乘係數 c）
p("")
chk("V1 項值已乘係數 c（逐項恆等）",
    all(T[2]==T[0]*int(FUN[T[1]].subs(b,4)) for T in TERMS), f"{len(TERMS)} 項")
chk("V2 值多重集對稱（Σ 值 = 0，因係數集含 ±）", sum(T[2] for T in TERMS)==0,
    f"Σ = {sum(T[2] for T in TERMS)}")
ATOMS=[1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
p("="*78); p("O229/24 (R5-③) — 形式 × 值 判別力矩陣（凍結類 𝒞）"); p("="*78)
p(f"\n[1] 枚舉並建全值直方圖（項集 {len(TERMS)}，2–3 項式）")
hist={}; forms_by_val={}
tot=0
for n in (2,3):
    for comb in itertools.combinations(range(len(TERMS)),n):
        v=sum(TERMS[i][2] for i in comb); tot+=1
        hist[v]=hist.get(v,0)+1
        if v in ATOMS+[137]: forms_by_val.setdefault(v,[]).append(comb)
p(f"    形式總數 = {tot:,}；不同值數 = {len(hist):,}")
ex={v:hist.get(v,0) for v in ATOMS}
p(f"\n[2] D1 表達力 express(v)（34 原子）")
for v in ATOMS: p(f"    {v:4d}: {ex[v]:5d}")
chk("C1 表達力覆蓋 ≥ 0.8×34 = 27.2", sum(1 for v in ATOMS if ex[v]>=1)>=0.8*len(ATOMS),
    f"覆蓋 {sum(1 for v in ATOMS if ex[v]>=1)}/34")
rk_atom=sorted(ATOMS,key=lambda v:-ex[v]).index(137)+1
lo,hi=2,1000
rk_glob=1+sum(1 for v in range(lo,hi+1) if hist.get(v,0)>ex[137])
p(f"    137 在 34 原子中之排名 = {rk_atom}；在 [{lo},{hi}] 整數中之排名 = {rk_glob}")
p(f"\n[3] D2 MC null（值池）: 同一形式類下，隨機目標 v ∈ [{lo},{hi}] 之表達力 ≥ 137 之機率")
ge=sum(1 for v in range(lo,hi+1) if hist.get(v,0)>=ex[137]); N=hi-lo+1
pq=ge/N
p(f"    #{{v: hist(v) ≥ hist(137)}} = {ge} / {N} ⟹ p_value = {pq:.4f}")
chk("D2 端點鎖之**值層**判別力: p_value < 0.05（否則下修）", pq<0.05,
    f"p = {pq:.4f} ⟹ {'顯著' if pq<0.05 else '**唔顯著**（值層零判別力）'}")

p(f"\n[3b] D2b 同量級 null（消「大小效應」）: 目標池 v ∈ [100,200]（與 137 同量級）")
ge2=sum(1 for v in range(100,201) if hist.get(v,0)>=ex[137]); N2=101
pq2=ge2/N2
rk2=1+sum(1 for v in range(100,201) if hist.get(v,0)>ex[137])
p(f"    express(137) = {ex[137]}；同池中 ≥ 137 者 = {ge2}/{N2} ⟹ p_value = {pq2:.4f}；137 之池內排名 = {rk2}/{N2}")
chk("D2b 同量級池 p_value < 0.05（若否 ⟹ 137 之值層無特殊性，此前 p = 0.02 係大小效應假象）",
    pq2<0.05, f"p = {pq2:.4f} ⟹ {'顯著' if pq2<0.05 else '**唔顯著**（值層零判別力）'}")

p("\n[4] D3 lock(v): 「唯一正整數解 = 4」（純 Python 係數向量 + Cauchy 界 = 完備且精確）")
from fractions import Fraction as Fr
# 每項之係數向量 {次數: 係數}（純 Python，唔用 sympy）
CV={ "1":{0:Fr(1)}, "B":{1:Fr(1)}, "B−1":{0:Fr(-1),1:Fr(1)}, "B+1":{0:Fr(1),1:Fr(1)}, "2B":{1:Fr(2)},
     "B(B−1)":{1:Fr(-1),2:Fr(1)}, "B²":{2:Fr(1)}, "B³":{3:Fr(1)}, "B⁴":{4:Fr(1)},
     "B²(B−1)²":{2:Fr(1),3:Fr(-2),4:Fr(1)}, "B²+1":{0:Fr(1),2:Fr(1)}, "B⁴+B²":{2:Fr(1),4:Fr(1)},
     "C(B,2)":{1:Fr(-1,2),2:Fr(1,2)}, "C(B²,2)":{2:Fr(-1,2),4:Fr(1,2)} }
for _k in names:
    if _k not in CV and _k!="2^B": CV[_k]={0:Fr(int(FUN[_k]))}   # 常數項（L₅²=121、μ²=2 …）
def vec_of(comb,target):
    """回傳 (整數係數 list（高→低）, 係數下限, 是否多項式)"""
    d={}; nonpoly=False
    for i in comb:
        c,name,_,_=TERMS[i]
        if name=="2^B": nonpoly=True; continue
        for deg,co in CV[name].items(): d[deg]=d.get(deg,Fr(0))+c*co
    if nonpoly: return None,0,False
    d[0]=d.get(0,Fr(0))-target
    if not any(v!=0 for v in d.values()): return [],0,True
    den=1
    for v in d.values(): den=max(den, v.denominator)
    top=max(d); co=[0]*(top+1)
    for deg,v in d.items(): co[deg]=int(v*den)
    return co[::-1],1,True                     # 高→低
def roots_of(comb,target):
    co,_,ok=vec_of(comb,target)
    if ok:
        if not co: return [],True
        lead=abs(co[0]); mx=max([abs(c) for c in co[1:]] or [0])
        bound=min(10**4, 1+(mx//max(1,lead))+2)          # Cauchy 界 ⟹ 界內掃描完備
        out=[]
        for Bv in range(1,bound+1):
            s=0
            for c in co: s=s*Bv+c
            if s==0: out.append(Bv)
        return out,True
    out=[]
    for Bv in range(1,10001):
        if sum(TERMS[i][0]*VAL[TERMS[i][1]](Bv) for i in comb)==target: out.append(Bv)
    return out,False
VAL={"1":lambda B:1,"B":lambda B:B,"B−1":lambda B:B-1,"B+1":lambda B:B+1,"2B":lambda B:2*B,
     "B(B−1)":lambda B:B*(B-1),"B²":lambda B:B*B,"B³":lambda B:B**3,"B⁴":lambda B:B**4,
     "B²(B−1)²":lambda B:(B*(B-1))**2,"B²+1":lambda B:B*B+1,"B⁴+B²":lambda B:B**4+B*B,
     "C(B,2)":lambda B:B*(B-1)//2,"C(B²,2)":lambda B:(B*B)*(B*B-1)//2,"2^B":lambda B:2**B}
for _k in names:
    if _k not in VAL:
        VAL[_k]=(lambda kk: (lambda B: int(FUN[kk])))(_k)
BDEP={k: (b in FUN[k].free_symbols) for k in names}
lock={}
for v in ATOMS:
    lst=forms_by_val.get(v,[])
    cnt=0
    for comb in lst:
        if not any(BDEP[TERMS[i][1]] for i in comb): continue   # 純常數式（對所有 B 成立）唔算鎖
        rs,_=roots_of(comb,v)
        if rs==[4]: cnt+=1
    lock[v]=cnt
    if v in (34,46,88,90,123,134,137,144,176): p(f"    lock({v}) = {cnt}")
nz=sum(1 for v in ATOMS if lock[v]>=1)
mx=max(lock.values()); arg=[v for v in ATOMS if lock[v]==mx]
p(f"    #{{v: lock(v) ≥ 1}} = {nz}/34；max lock = {mx}，達到者 = {arg}")
chk("C2 #{v: lock(v) ≥ 1} ≤ 12 且 lock(137) = max", nz<=12 and lock[137]==mx,
    f"實測 {nz}/34；lock(137) = {lock[137]}，max = {mx} @ {arg} ⟹ 預註冊 FAIL 原樣保留")
chk("C3 |argmax| ≥ 2 ⟹ 端點鎖**唔係**唯一被鎖定之值，判別力須下修", len(arg)>=2, f"|argmax| = {len(arg)}")
chk("C3b [c] 正確陳述: 在凍結類下「以 B = 4 為唯一解而命中 v」之形式數，137 並非唯一/最高 ⟹ "
    "端點鎖之**值層判別力接近零**（形式非唯一 + 值非唯一）", len(arg)>=2 and lock[137]>0)
V=(f"★ R5-③: 凍結類 𝒞（{tot:,} 形式）之全值直方圖: express(137) = {ex[137]}，"
   f"在 34 原子中排第 {rk_atom}、在 [{lo},{hi}] 中排第 {rk_glob}；值池 MC p_value = {pq:.4f}。\n"
   f"★ lock(v)（唯一正整數解 = 4）: lock(137) = {lock[137]}；{chr(35)}{{v: lock(v) ≥ 1}} = {nz}/34；max = {mx} @ {arg}。\n"
   f"★ 判決: 端點鎖之形式非唯一（express(137) = {ex[137]}）**且**值層亦非唯一（max lock 在 {arg} 而非 137）⟹ 由「α⁻¹(0) 之結構推導」降格為"
   f"「α⁻¹(0) 之可用結構式之一」；但在**固定形式**（如 C(B²,2)+B²+1）之下，B = 4 仍係唯一正整數解（R1/R2 之結果不變）。")
p("\n★ R5-③ 判決"); p(V)
np_,nf_=res()
json.dump({"script":"24_r5_discrimination","pass":np_,"fail":nf_,"total":np_+nf_,
  "terms":len(TERMS),"forms_total":tot,"distinct_values":len(hist),"express":{"137":ex[137],"atoms":ex},
  "rank_atom":rk_atom,"rank_global":rk_glob,"p_value":pq,"p_value_sizematched":pq2,
  "rank_sizematched":rk2,"value_pool":[lo,hi],
  "term_values":[[T[0],T[1],T[2]] for T in TERMS],
  "CV":{k:{str(a):[Fr(c).numerator,Fr(c).denominator] for a,c in v.items()} for k,v in CV.items()},
  "lock":{"137":lock[137],"nonzero":nz,"max":mx,"argmax":arg,"table":lock},"verdict":V},
  open(os.path.join(BASE,"data","24_r5_discrimination.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","24_r5_discrimination.out"),"w").write("\n".join(OUT)+"\n")
