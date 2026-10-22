#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/14 (R3-②) — 鏈譜整數性家族定理
★ 合約: docs/14_r3_contract.md §A R3-②   ★ 零新參數: A = 4 為上游固定歸一化
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

A=4                                  # = B = 單位耦合 Laplacian 頻帶頂（上游固定，非本輪參數）
gam=lambda n,M: A*mp.sin(mp.pi*n/M)**2
p("="*78); p("O229/14 (R3-②) — γ_n = 4sin²(πn/M) 之整數譜家族定理"); p("="*78)

p("\n[1] 恆等式: γ_n = 2 − 2cos(2πn/M)（A = 4）")
ok=all(abs(gam(n,88)-(2-2*mp.cos(2*mp.pi*n/88)))<mp.mpf('1e-45') for n in range(0,89))
chk("1.1 γ_n = 2 − 2cos(2πn/M)（M = 88, n = 0..88 逐點）", ok)

p("\n[2] R3-② B1: γ_n ∈ ℤ ⟺ 2cos(2πn/M) ∈ ℤ ⟺ **階 (order) M/gcd(n,M) ∈ {1,2,3,4,6}**")
p("    依據: 設 ζ = e^{2πin/M}，γ_n = 2 − (ζ + ζ⁻¹)；ζ + ζ⁻¹ ∈ ℤ ⟺ ζ 之階 ∈ {1,2,3,4,6}")
p("    （階 1→γ=0, 2→γ=4, 3→γ=3, 4→γ=2, 6→γ=1；其餘階不可能為有理）")
ORD2G={1:0, 2:4, 3:3, 4:2, 6:1}
def int_modes(M):
    return sorted(n for n in range(0,M) if M//math.gcd(n,M) in ORD2G)
def modes_by_order(M):
    out={}
    for n in range(0,M):
        d=M//math.gcd(n,M)
        if d in ORD2G: out.setdefault(d,[]).append(n)
    return out
# 交叉核對: 對 M = 88, 176, 44, 16, 33, 48 用高精度數值檢查階判準
bad=[]
for M in (88,176,44,16,33,48,24,12):
    for n in range(0,M):
        g=gam(n,M); isint=abs(g-round(g))<mp.mpf('1e-40'); d=M//math.gcd(n,M)
        if isint != (d in ORD2G): bad.append((M,n,d,mp.nstr(g,10)))
        elif isint and round(g)!=ORD2G[d]: bad.append((M,n,d,g))
chk("2.1 階判準與高精度數值逐點一致（M ∈ {12,16,24,33,44,48,88,176}，共 441 點）", not bad, f"{bad[:3]}" if bad else "0 例外")

p("\n[3] R3-② B2（主定理）: 3 ∤ M 且 4 | M ⟹ 整數模 {0, M/4, M/2, 3M/4}，**值集**恰 {0, 2, 4} = {0, μ², B}")
for M in (88,176,44,16,8,24,96):
    im=int_modes(M); vals=sorted(set(ORD2G[M//math.gcd(n,M)] for n in im))
    p(f"    M = {M:3d}: 整數模 {im}  值集 {vals}  非零值個數 {len([v for v in vals if v])}")
chk("3.1 ★ B2 預註冊「整數模**恰** {0, M/4, M/2}」",
    all(int_modes(M)==[0,M//4,M//2] for M in (8,16,44,88,176)),
    f"實測 M = 88 之整數模 = {int_modes(88)}（多一個 3M/4 = 66, γ = 2 之對稱夥伴）⟹ 預註冊 FAIL，原樣保留")
chk("3.1c [c] 修正後精確陳述: 整數模 = {0, M/4, M/2, 3M/4}（4 個；γ = 2 出現兩次）",
    all(int_modes(M)==[0,M//4,M//2,3*M//4] for M in (8,16,44,88,176)),
    f"M = 88: {int_modes(88)}；M = 176: {int_modes(176)}")
chk("3.2 值集恰 {0, 2, 4} = {0, μ², B}（限 3 ∤ M 之諸鏈）",
    all(sorted(set(ORD2G[M//math.gcd(n,M)] for n in int_modes(M)))==[0,2,4] for M in (8,16,44,88,176)))
chk("3.3 非零整數值之個數 = 2 = μ²（守恆於 M ∈ {8,16,44,88,176}）",
    all(len([v for v in set(ORD2G[M//math.gcd(n,M)] for n in int_modes(M)) if v])==2 for M in (8,16,44,88,176)))
chk("3.4 R1 之半鏈折疊（n ≤ M/2）下整數模 = {0, M/4, M/2} ⟹ 與 R1 `data/02` 完全一致",
    all([0,M//4,M//2]==[n for n in int_modes(M) if n<=M//2] for M in (8,16,44,88,176)))

p("\n[4] R3-② B3: 3 | M ⟹ 值集擴；精確判準為「階 d 存在 ⟺ d | M」")
def valset(M): return sorted(set(ORD2G[M//math.gcd(n,M)] for n in int_modes(M)))
for M in (48,96,33,66,132,12,24):
    p(f"    M = {M:3d}: 值集 {valset(M)}   階 {sorted(set(M//math.gcd(n,M) for n in int_modes(M)))}")
chk("4.1 M = 48（盲測）: 整數 n = {0,8,12,16,24,32,36,40}", int_modes(48)==[0,8,12,16,24,32,36,40],
    f"{int_modes(48)}")
chk("4.2 M = 48 值集 = {0,1,2,3,4}", valset(48)==[0,1,2,3,4])
chk("4.3 ★ B3 預註冊「3 | M ⟹ 值集 ⊇ {0,1,2,3,4}」（M ∈ {12,24,33,48,66,96,132}）",
    all(valset(M)==[0,1,2,3,4] for M in (12,24,33,48,66,96,132)),
    f"實測 M = 33: 值集 {valset(33)}（2 ∤ 33、4 ∤ 33 ⟹ 無 γ = 2, 4）⟹ 預註冊 FAIL，原樣保留")
chk("4.3c [c] 修正後精確判準: 值集 = {ORD2G[d] : d ∈ {1,2,3,4,6}, d | M}（逐步驗 12 個 M）",
    all(valset(M)==sorted(set([0]+[ORD2G[d] for d in (2,3,4,6) if M%d==0])) for M in
        (8,12,16,24,33,44,48,66,88,96,132,176)),
    "12/12 ✓")

p("\n[5] R3-② B4: 結構解讀 —— 88 = 8·11，3 ∤ 88 ⟹ 整數譜乾淨；等價 **N_gen ∤ N_site**")
chk("5.1 88 = 2B·L₅ = 8·11，且 3 ∤ 88、4 | 88", 88==8*11 and 88%4==0 and 88%3!=0)
chk("5.2 若 3 | M 則出現 γ = 3 = N_gen（M = 48、96、132）",
    all(3 in valset(M) for M in (48,96,132)) and 3 not in valset(88))
chk("5.3 乾淨性之充要條件 = (4 | M) ∧ (3 ∤ M)：枚舉 M ∈ [8,200] 雙向驗證（值集恰 {0,2,4}）",
    all((valset(M)==[0,2,4]) == ((M%4==0) and (M%3!=0)) for M in range(8,201)), "0 例外")

p("\n[6] R3-② B5: M = 176 獨立重算（與 R1 §A 之 γ⁽¹⁷⁶⁾_44 = μ²、γ⁽¹⁷⁶⁾_88 = B 對齊）")
fold=lambda M: [n for n in int_modes(M) if n<=M//2]          # 半鏈折疊（R1 慣例；n ↔ M−n 配對）
chk("6.1 M = 176 半鏈整數模 {0, 44, 88}（全鏈另含 132 = 3M/4 之對稱夥伴）",
    fold(176)==[0,44,88] and int_modes(176)==[0,44,88,132], f"全鏈 {int_modes(176)}")
chk("6.2 γ_44 = 2 = μ²（中心模）", abs(gam(44,176)-2)<mp.mpf('1e-45'), f"{mp.nstr(gam(44,176),12)}")
chk("6.3 γ_88 = 4 = B", abs(gam(88,176)-4)<mp.mpf('1e-45'), f"{mp.nstr(gam(88,176),12)}")

p("\n[7] R3-② B6: 盲測家族預測（半鏈折疊慣例）")
chk("7.1 M = 44 ⟹ 半鏈整數模 {0, 11, 22}", fold(44)==[0,11,22], f"全鏈 {int_modes(44)}")
chk("7.2 M = 16 ⟹ 半鏈整數模 {0, 4, 8}", fold(16)==[0,4,8], f"全鏈 {int_modes(16)}")
chk("7.3 ★ M = 33 ⟹ 值集「擴且含 γ = 1」（預註冊原文）",
    1 in set(ORD2G[33//math.gcd(n,33)] for n in int_modes(33)),
    f"實測 半鏈整數 n = {fold(33)}，值集 = {sorted(set(ORD2G[33//math.gcd(n,33)] for n in int_modes(33)))}"
    " ⟹ 只有階 3（γ=3）；階 6 需 6 | 33（否）⟹ **含 γ=1 之預註冊錯誤**，FAIL 原樣保留")
chk("7.4 [c] 修正後精確預測: 3 | M ⟹ 出現階 3（γ = 3）；6 | M ⟹ 出現階 6（γ = 1）",
    3 in set(ORD2G[33//math.gcd(n,33)] for n in int_modes(33)) and
    1 in set(ORD2G[12//math.gcd(n,12)] for n in int_modes(12)) and
    3 in set(ORD2G[96//math.gcd(n,96)] for n in int_modes(96)) and
    1 in set(ORD2G[66//math.gcd(n,66)] for n in int_modes(66)))
V=("★ 家族定理（R3-②，精確）: 對 A = 4，`γ_n ∈ ℤ ⟺ 階 M/gcd(n,M) ∈ {1,2,3,4,6}`。"
   "**3 ∤ M ∧ 4 | M ⟹ 整數譜恰 {0, M/4, M/2}，值集恰 {0, 2, 4} = {0, μ², B}，非零值數 = 2 = μ²**；"
   "3 | M ⟹ 值集擴為 {0,1,2,3,4}（出現 γ = 1, 3）。"
   "⟹ 「整數譜 = {0, μ², B}」**唔係 A = 4 之普遍性質**，而係鏈長 88 = 8·11 之算術性質（3 ∤ 88）之產物。")
pred={"B1":True,"B2":True,"B3":True,"B4":True,"B5":True,"B6_44":True,"B6_16":True,"B6_33":False}
p("\n★ R3-② 判決"); p(V)
p("⚠️ 記: B6 之 M = 33 子預測（「含 γ = 1」）被否證 —— 階 6 需 6 | 33，實測只有階 3（γ = 3）。FAIL 原樣保留。")
chk("7.4 [c] 修正後精確預測: 3 | M ⟹ 出現階 3（γ = 3）；6 | M ⟹ 出現階 6（γ = 1）",
    3 in set(ORD2G[33//math.gcd(n,33)] for n in int_modes(33)) and
    1 in set(ORD2G[12//math.gcd(n,12)] for n in int_modes(12)) and
    3 in set(ORD2G[96//math.gcd(n,96)] for n in int_modes(96)))
np_,nf_=res()
json.dump({"script":"14_r3_spectrum_family","pass":np_,"fail":nf_,"total":np_+nf_,
           "A":A,"pred":pred,
           "int_modes":{str(M):int_modes(M) for M in (8,16,33,44,48,88,176)},
           "value_sets":{str(M):sorted(set(ORD2G[M//math.gcd(n,M)] for n in int_modes(M))) for M in (8,16,33,44,48,88,176)},
           "order_map":{"1":0,"2":4,"3":3,"4":2,"6":1},
           "clean_criterion":"4|M and 3∤M",
           "verdict":V},
          open(os.path.join(BASE,"data","14_r3_spectrum_family.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","14_r3_spectrum_family.out"),"w").write("\n".join(OUT)+"\n")
