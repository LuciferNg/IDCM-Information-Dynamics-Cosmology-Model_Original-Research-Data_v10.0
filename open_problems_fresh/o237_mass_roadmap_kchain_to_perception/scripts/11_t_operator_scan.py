#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — 𝒯 算子代數數值掃描 (O210 七運算: ⊗/⊕/Tr/Spec/Proj/†/Contr)
================================================================================
docs/08 第二輪負: chain 扇區統計 (v₂-mean/γ-mean) 唔覆蓋 8 C_f。
最後一個 chain 內部家族: O210 𝒯 型別代數 —— 由 U/γ̂/b̂ 算子 + 跡/譜/冪
構造嘅所有可計算數值 (零外部)。先計晒, 後對照 C_f (唔 fit)。

候選算子數值 (全部 chain 內):
  T1: Tr(γ̂^k) = Σ γ_n^k        k=1..8
  T2: Tr(b̂^k) = Σ b_n^k        k=1..8
  T3: Tr(U^k) = Σ e^{iknπ/44}  (k=1..44)
  T4: 對數跡: ln Π b_n = Σ ln b_n; ln Π γ_n
  T5: 譜幾何: max/min/median/Σ(奇)/Σ(偶)
  T6: 組合: Σγ/44, Σb/44, 90/44, 90/Σb, Σb/Σγ, 2Σγ, ...
  T7: Squared traces: (Σb)², (Σγ)², Σb·Σγ, Σγ²/Σγ, Σb³/Σb²
"""
import math

def g(m): return 4 * math.sin(math.pi * m / 88) ** 2
def b(m): return 2 * math.sin(math.pi * m / 88)

G = [g(n) for n in range(1, 45)]
B = [b(n) for n in range(1, 45)]

print("="*100)
print("O237 U2 — 𝒯 算子代數數值掃描 (先計, 後對照)")
print("="*100)

vals = {}
# T1: Tr γ^k
for k in range(1, 9):
    vals[f'Trγ^{k}'] = sum(x**k for x in G)
# T2: Tr b^k
for k in range(1, 9):
    vals[f'Trb^{k}'] = sum(x**k for x in B)
# T4 對數跡
vals['lnΠb'] = sum(math.log(x) for x in B)
vals['lnΠγ'] = sum(math.log(x) for x in G)
# T5 譜幾何
vals['maxγ'] = max(G); vals['minγ'] = min(G)
vals['maxb'] = max(B); vals['minb'] = min(B)
vals['Σγ_odd'] = sum(g(n) for n in range(1,45,2))
vals['Σγ_even'] = sum(g(n) for n in range(2,45,2))
vals['Σb_odd'] = sum(b(n) for n in range(1,45,2))
vals['Σb_even'] = sum(b(n) for n in range(2,45,2))
vals['Σγ'] = sum(G); vals['Σb'] = sum(B)
# T6 組合
vals['Σγ/44'] = sum(G)/44
vals['Σb/44'] = sum(B)/44
vals['90/44'] = 90/44
vals['90/Σb'] = 90/sum(B)
vals['Σb/Σγ'] = sum(B)/sum(G)
vals['2Σγ'] = 2*sum(G)
vals['2Σb'] = 2*sum(B)
vals['Σγ−Σb'] = sum(G)-sum(B)
vals['Σγ+Σb'] = sum(G)+sum(B)
vals['Σγ/2'] = sum(G)/2
vals['Σb/2'] = sum(B)/2
vals['44/Σγ'] = 44/sum(G)
# T7 squared
vals['(Σb)²'] = sum(B)**2
vals['(Σγ)²'] = sum(G)**2
vals['ΣbΣγ'] = sum(B)*sum(G)
vals['Σγ²/Σγ'] = sum(x*x for x in G)/sum(G)
vals['Σb³/Σb²'] = sum(x**3 for x in B)/sum(x*x for x in B)
vals['Σγ²'] = sum(x*x for x in G)
vals['Σb²'] = sum(x*x for x in B)
# T8 有理譜比
vals['γ44/γ1'] = g(44)/g(1)
vals['γ22/γ1'] = g(22)/g(1)
vals['b44/b1'] = b(44)/b(1)
vals['b22/b1'] = b(22)/b(1)
vals['Σγ/Σb×2'] = 2*sum(G)/sum(B)

print(f"{'算子數值':>12} {'值':>14}")
for k, v in sorted(vals.items()):
    print(f"{k:>12} {v:>14.8f}")

# ---------------------------------------------------------------- 對照
print("\n[對照] A5 C_f 真值 (O206 第十輪):")
M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
CFn = {p: MASS[p]/(M0*g(n)) for p, n in zip(["e","u","d","s","mu","c","tau","b"],
                                            [1,2,3,4,5,7,9,11])}
for p, n in zip(["e","u","d","s","mu","c","tau","b"], [1,2,3,4,5,7,9,11]):
    print(f"  {p:>4} n={n:>2}  C_f = {CFn[p]:>10.4f}")

# 自動偵測: 有冇 𝒯 值 ≈ C_f (<1% rel) 或 C_f 嘅簡單比
print("\n[偵測] 𝒯 值 vs C_f (<1% rel):")
hits = 0
for pk, pv in CFn.items():
    for tk, tv in sorted(vals.items()):
        if tv == 0: continue
        rel = abs(pv-tv)/tv
        if rel < 0.01:
            print(f"  {pk}: C_f={pv:>10.4f} ≈ 𝒯 {tk}={tv:>12.6f} (rel {rel:.3%})")
            hits += 1
if hits == 0:
    print("  無")
print(f"\n命中數 = {hits} (8 C_f × 50 算子值 = 400 次比較, 1% 窗隨機期望 ~4)")

print("""
[判定] 𝒯 算子數值家族結果:
  - Σγ=90, Σb=1+cot(π/176)=57.0, Trγ², 對數跡, 譜幾何等全部列出
  - 1% 窗命中數 vs 隨機期望 4 ⟹ 有冇超越性? 若有實命中需獨立 confirm (唔可以當即結構)
  - C_e=3.6 已知 (G8 扇區); 其他 7 值若無 𝒯 身份 ⟹ 維持 🔴
""")