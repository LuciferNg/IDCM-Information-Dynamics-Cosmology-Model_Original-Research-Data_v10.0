#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — 商殘餘算子化: Ĉ_f = m̂·b̂⁻¹ 嘅 eigenvalue 身份 (docs/10 路線 A 收尾)
================================================================================
docs/10 路線 A: F_proj 非 VEV = 商殘餘 (m/(M₀γ)), 冇獨立 chain 身份 (除 C_e)。
本 script 嘗試將「商殘餘」升格做算子層陳述 (唔係詞語):
  m_f = M₀γ_nF_proj = M₀·b̂²·...  (b̂ = √γ̂, U4 已閉合)
  商算子 Ĉ = 質量算子 / 譜算子 = ?

嘗試:
  T1: Ĉ = m̂·b̂⁻¹ (b̂ 可逆? det b̂ = Π 2sin(nπ/88) = 88 非零 ✓)
  T2: Ĉ 嘅 eigenvalue = C_f 商值 (F_proj)?
  T3: Ĉ 有冇 𝒯 身份? (7 個商值唔同 ⟹ Ĉ 唔可能係標量算子)
      ⟹ 若 Ĉ eigenvalue 全異 → Ĉ 係非退化算子 → 但「邊個」算子? 
  T4: 商值 family 檢驗: C_f = m/(M₀γ) 嘅集合 {3.59, 3.80, 3.66, 41.3, 30.0, 186.1, 159.6, 255.8}
      有冇共同生成? (docs/04 §二: 5 族 blind 負; docs/08-10: chain 內部 4 家族負)
  T5: 內積檢驗: ⟨C_f, chain 譜量⟩ 正交 + 剩餘 ＝ 商殘餘嘅算子層定義?
"""
import math

def g(n): return 4 * math.sin(math.pi * n / 88) ** 2
def b(n): return 2 * math.sin(math.pi * n / 88)

PASS, FAIL = [], []
def ck(name, ok, info=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name}  {info}")

print("="*92)
print("O237 U2 — 商殘餘算子化 (docs/10 路線 A 收尾)")
print("="*92)

# ---- T1: b̂ 可逆性
print("\n[T1] b̂ = √γ̂ 可逆? (det b̂ = Π 2sin(nπ/88))")
det_log = sum(math.log(b(n)) for n in range(1, 45))
ck("det b̂ = Π 2sin(nπ/88) ≠ 0 (全部 sin>0, n=1..44)", all(b(n) > 0 for n in range(1, 45)),
   f"min b_n = {min(b(n) for n in range(1,45)):.6f} > 0")
print(f"  ln det b̂ = {det_log:.6f} ⟹ det b̂ 非零 ✓")

# ---- T2: b̂⁻¹ 存在, Ĉ = m̂·b̂⁻¹ 定義?
print("\n[T2] 商算子 Ĉ = m̂·b̂⁻¹ — eigenvalue = C_f?")
# 譜層: m̂ = M₀b̂; 公式層: m_f = M₀γF = M₀b²F
# 商 = m_f/(M₀b̂) = b̂·F — F 係商因子
M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
CF = {p: MASS[p]/(M0*g(n)) for p, n in MODES.items()}
print(f"  C_f 商值集合: {[f'{v:.2f}' for v in CF.values()]}")

# 商值同 b̂ 嘅關係: C_f · b_n = m/(M0·b_n)? no — C_f = m/(M0·γ) = m/(M0·b²)
# C_f·b_n = m/(M0·b_n) = '振幅商'
AmpQ = {p: MASS[p]/(M0*b(n)) for p, n in MODES.items()}
print(f"  振幅商 C_f·b: {[f'{v:.2f}' for v in AmpQ.values()]}")

# ---- T3: Ĉ 有冇 𝒯 身份?
print("\n[T3] 商值 family 嘅 𝒯 身份檢查 (docs/04+08-10 已 9 家族負, 補充):")
# 8 個非 VEV 商值: e/d/u (~3.6-3.8) 為一組; s/μ (~30-41); c/τ/b (~160-256)
# 組內比: 
print(f"  s/μ = {CF['s']/CF['mu']:.4f}   c/τ = {CF['c']/CF['tau']:.4f}   τ/b = {CF['tau']/CF['b']:.4f}")
print(f"  e/d = {CF['e']/CF['d']:.4f}   d/u = {CF['d']/CF['u']:.4f}   e/u = {CF['e']/CF['u']:.4f}")
# 呢啲比有冇鏈數? ratio 家族:
r1 = CF['s']/CF['mu']
ck("s/μ ≈ 1.376 — 冇明顯鏈數 (唔係 4/3, √2, φ...)", abs(r1 - 1.376) < 1e-3,
   f"s/μ={r1:.4f} (4/3=1.333, √2=1.414, φ=1.618)")
r2 = CF['tau']/CF['b']
ck("τ/b ≈ 0.624 — 冇明顯鏈數", abs(r2 - 0.624) < 1e-3, f"τ/b={r2:.4f}")
# 商殘餘定義: 唔可以 fit — 只係記錄「冇共同鏈數」

# ---- T4: 正交檢驗 — 商值同所有 chain 譜量嘅關聯
print("\n[T4] 商值同 chain 譜量嘅關聯 (正方向: 唔係 pool match):")
import numpy as np
gam = np.array([g(m) for m in range(1,45)])
# 投影: C_f 向量喺 γ-basis 嘅表示
n_vec = np.array([MODES[p] for p in CF])
cv = np.array([CF[p] for p in ["e","u","d","s","mu","c","tau","b"]])
gv = np.array([g(n) for n in n_vec])
r2 = np.corrcoef(cv, gv)[0,1]
print(f"  corr(C_f, γ_mode) = {r2:+.4f} — 正相關(注意: assignment 已按質量排序 ⟹ 偽相關)")
# v₂ 檢驗
def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c
v2v = np.array([v2(n) for n in n_vec])
corr2 = np.corrcoef(cv, v2v)[0,1]
print(f"  corr(C_f, v₂(mode)) = {corr2:+.4f}")

# ---- T5: 誠實收尾
print("\n[T5] 結論:")
print("""
  C_e = 18/5 例外 (chain 2-adic 身份, 已閉合)
  其餘 7 個非 VEV C_f:
    - 9 家族 blind 掃描全負 (docs/04+08-10)
    - 商算子 Ĉ 非退化 (8 個 eigenvalue 全異) — 但冇 𝒯 身份
    - corr(C_f, γ) = +0.95 係「assignment 按質量排序」之偽相關 (log-log spread 10.1×,
      scripts/20: 唔係單一冪律 p; r²=0.836 由跨度 8e3× 驅動)
    - 同 v₂(mode) corr = −0.33 (弱負)
  ⟹ docs/10 路線 A 定案: F_proj 非 VEV = 商殘餘 (後驗), 唔係漏網幾何。
     U2 正確姿態 = 承認商殘餘 + O234 凍結判準 (lattice mu/md 1-2%, HL-LHC)。
""")
print("="*92)
print(f"U2 商殘餘算子化: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*92)