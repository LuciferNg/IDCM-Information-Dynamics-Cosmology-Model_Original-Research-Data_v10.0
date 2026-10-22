#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/18 (R4-①) — IDCM 鏈長族之普遍定理（閉合 R3-② 之殘餘）
★ 合約: docs/20_r4_contract.md §A R4-①   ★ 零新參數
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
A=4; B=4; mu2=2; L5=11
ORD2G={1:0,2:4,3:3,4:2,6:1}
def int_modes(M): return sorted(n for n in range(M) if M//math.gcd(n,M) in ORD2G)
valset=lambda M: sorted(set(ORD2G[M//math.gcd(n,M)] for n in int_modes(M)))
gv=lambda n,M: A*mp.sin(mp.pi*n/M)**2
MM=sorted(set([2**k for k in (3,4)]+[2**k*L5 for k in (2,3,4,5,6)]))
p("="*78); p("O229/18 (R4-①) — IDCM 鏈長族 ℳ 之整數譜普遍性"); p("="*78)
p(f"\n[1] 鏈長族 ℳ = {{2^k:k∈[3,4]}} ∪ {{2^k·L₅:k∈[2,6]}} = {MM}")

p("\n[2] R4-① A1: ∀M ∈ ℳ: 4|M ∧ 3∤M ⟹ 整數譜 {0,M/4,M/2,3M/4}、值集恰 {0,2,4}")
for M in MM:
    p(f"    M = {M:4d} = 2^{int(math.log2(M//(L5 if M%L5==0 else 1)))}·11^{1 if M%L5==0 else 0}"
      f"  整數模 {int_modes(M)}  值集 {valset(M)}")
chk("2.1 全部 M ∈ ℳ 滿足 4 | M", all(M%4==0 for M in MM))
chk("2.2 全部 M ∈ ℳ 滿足 3 ∤ M", all(M%3!=0 for M in MM))
chk("2.3 整數模恰 {0, M/4, M/2, 3M/4}", all(int_modes(M)==[0,M//4,M//2,3*M//4] for M in MM))
chk("2.4 值集恰 {0, 2, 4} = {0, μ², B}", all(valset(M)==[0,2,4] for M in MM))
chk("2.5 與高精度掃描一致（容差 1e-45）",
    all(abs(gv(n,M)-ORD2G[M//math.gcd(n,M)])<mp.mpf('1e-45') for M in MM for n in int_modes(M)))
chk("2.6 中心模 γ_(M/4) = μ² 且 Nyquist γ_(M/2) = B（精確）",
    all(abs(gv(M//4,M)-mu2)<mp.mpf('1e-45') and abs(gv(M//2,M)-B)<mp.mpf('1e-45') for M in MM))

p("\n[3] R4-① A2: 3 ∤ M 係**結構必然**（ℳ 之元素皆 2^a·11^b；3 ∤ 2^a、3 ∤ 11）")
fac={}
for M in MM:
    a=0; v=M
    while v%2==0: v//=2; a+=1
    b=0
    while v%11==0: v//=11; b+=1
    fac[M]=(a,b,v)
    p(f"    {M:4d} = 2^{a} · 11^{b} · {v}   （餘因子 {v} = 1 ⟹ 純 2-平滑 × 11）")
chk("3.1 全部 M ∈ ℳ 之分解餘因子 = 1（即 M = 2^a·11^b）", all(fac[M][2]==1 for M in MM))
chk("3.2 3 ∤ 2^a（∀a）且 3 ∤ 11 ⟹ 3 | M 對 ℳ 不可能",
    all(pow(2,a,3)!=0 for a in range(0,40)) and 11%3!=0)
chk("3.3 等價陳述: N_gen = 3 ∤ N_site = 2B·L₅（因 3 ∤ 2B = 8 且 3 ∤ 11）",
    (2*B)%3!=0 and L5%3!=0 and (2*B*L5)%3!=0)
chk("3.4 充分性: 3 ∤ M ⟹ 無階 3、6 模 ⟹ 值集唔含 γ = 1, 3",
    all(1 not in valset(M) and 3 not in valset(M) for M in MM))

p("\n[4] R4-① A3（反面可證偽）: 乾淨性唯一依賴 L₅ ≡ ±1 (mod 3)")
bad=[]
for Lp in range(2,31):
    Mp=2*B*Lp
    ok=(valset(Mp)==[0,2,4])
    pred=(Lp%3!=0)
    if ok!=pred: bad.append((Lp,Mp,ok,pred))
    if Lp in (5,7,11,13,17,19,23,29,6,12,15): p(f"    L₅' = {Lp:2d} → M = {Mp:3d}: 值集 {valset(Mp)}  （預測乾淨={pred}）")
chk("4.1 ∀L₅' ∈ [2,30]: (值集恰 {0,2,4}) ⟺ (3 ∤ L₅')（雙向，0 例外）", not bad, f"{bad[:3]}" if bad else "0 例外")
chk("4.2 L₅ = 11 ≡ 2 (mod 3) ⟹ 落於乾淨分支；L₅' = 6, 12（3 之倍數）則值集擴為 {0,1,2,3,4}",
    (11%3==2) and valset(2*B*6)==[0,1,2,3,4] and valset(2*B*12)==[0,1,2,3,4], f"L₅'=6 → {valset(48)}")
chk("4.3 臨界值 L₅' = 3, 6, 9, 12, 15 皆 3|M ⟹ 出現 γ = 3 = N_gen",
    all(3 in valset(2*B*Lp) for Lp in (3,6,9,12,15)))
V=("★ R4-① **普遍定理成立**: IDCM 鏈長族 ℳ = {8, 16, 44, 88, 176, 352, 704} = {2^a·11^b} 之每個元素皆\n"
   "  (i) 4 | M、(ii) 3 ∤ M ⟹ 整數譜恰 {0, M/4, M/2, 3M/4}、**值集恰 {0, 2, 4} = {0, μ², B}**。\n"
   "  ★ 而 3 ∤ M 係**結構必然**（3 ∤ 2^a、3 ∤ 11）⟹ 「3 | M 之 IDCM 鏈唔存在」由 `N_site = 2B·L₅` 與 `L₅ = 11` 強制。\n"
   "  ⟹ R3-② 之 🟡 殘餘**閉合**：整數譜乾淨唔係巧合，係 `L₅ ≡ 2 (mod 3)`（質數 11）之算術後果；\n"
   "     反面驗證：任何 3 | L₅' 之鏈（如 6, 12）即出現 γ = 3 = N_gen，值集擴為 {0,1,2,3,4}。")
p("\n★ R4-① 判決"); p(V)
np_,nf_=res()
json.dump({"script":"18_r4_chain_family","pass":np_,"fail":nf_,"total":np_+nf_,
           "family":MM,"factorisation":{str(k):list(v) for k,v in fac.items()},
           "int_modes":{str(M):int_modes(M) for M in MM},"value_sets":{str(M):valset(M) for M in MM},
           "verdict":V},
          open(os.path.join(BASE,"data","18_r4_chain_family.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","18_r4_chain_family.out"),"w").write("\n".join(OUT)+"\n")
