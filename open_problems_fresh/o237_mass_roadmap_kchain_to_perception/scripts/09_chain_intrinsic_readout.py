#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — Chain 內部結構普查: F_proj 讀數函數 blind 掃描 (docs/07 方向)
================================================================================
框架裁決 (docs/07): CY₃ = 參數表示; F_proj = 88-ring 內部代數結構讀數。
本 script 將 O145 已建立嘅 chain 內部分層 (γ 權重 2-adic 階梯) 轉為候選讀數函數,
對 A5 mode n ∈ {1,2,3,4,5,7,9,11} 全部計出 —— **先計晒, 先唔印 C_f** ——
最後一節先對照, 睇有冇任何「一次過 8 值」嘅對應 (零新常數, 唔係擬合)。

候選讀數家族 (全部由 γ/v₂/層/鏡像對 定義, 零外部輸入):
  F1: v₂(n)                                        (mode 自身 2-adic)
  F2: Σγ(所在 v₂ 層)                                (層能量)
  F3: |所在層|                                      (層基數)
  F4: Σv₂(所在層) / |所在層|                         (C_e 型: 層 v₂-mean)
  F5: 所在層相對於 {8,16,24,32,40} 嘅元素身份       (C_e 直接)
  F6: γ_n / γ₁                                      (譜比)
  F7: γ_n / (γ_n + γ_{44−n})                        (鏡像佔比)
  F8: 前 n 個 mode 嘅 Σγ                              (累積譜)
  F9: Σ_{k=1..n} v₂(k)                              (累積 2-adic)
  F10: 44 − n 嘅 v₂                                    (對偶 2-adic)
"""
import math

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = bool(abs(float(got)-float(exp)) < tol)
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

def g(m): return 4 * math.sin(math.pi * m / 88) ** 2
def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c

MODES = [1, 2, 3, 4, 5, 7, 9, 11]

# O145 分層 (script 02 已建立, verbatim)
layers = {
    'v2=0': [m for m in range(1, 45) if v2(m) == 0],
    'v2=1': [m for m in range(1, 45) if v2(m) == 1],
    'v2=2': [m for m in range(1, 45) if v2(m) == 2],
    'v2>=3':[m for m in range(1, 45) if v2(m) >= 3],
}
SUM_G = {k: sum(g(m) for m in ms) for k, ms in layers.items()}
SUM_V2 = {k: sum(v2(m) for m in ms) for k, ms in layers.items()}
def layer_of(n):
    for k, ms in layers.items():
        if n in ms: return k
    return None

print("="*88)
print("O237 U2 — Chain 內部結構讀數 blind 掃描 (零外部幾何)")
print("="*88)

print("\n[0] O145 分層摘要 (已建立, 非新推導)")
for k in ['v2=0','v2=1','v2=2','v2>=3']:
    print(f"  {k:>6}: |L|={len(layers[k]):>2}, Σγ={SUM_G[k]:>8.4f}, Σv₂={SUM_V2[k]:>3d}, modes={layers[k]}")

# ---------------------------------------------------------------- 盲計
print("\n[1] 每個 A5 mode 嘅 chain 內部讀數 (先計晒, 唔睇 C_f)")
rows = []
for n in MODES:
    lk = layer_of(n)
    F1 = v2(n)
    F2 = SUM_G[lk]
    F3 = len(layers[lk])
    F4 = SUM_V2[lk]/len(layers[lk])
    F6 = g(n)/g(1)
    F7 = g(n)/(g(n)+g(44-n))
    F8 = sum(g(m) for m in range(1, n+1))
    F9 = sum(v2(m) for m in range(1, n+1))
    F10 = v2(44-n)
    rows.append((n, lk, F1, F2, F3, F4, F6, F7, F8, F9, F10))
    print(f"  n={n:>2} 層={lk:>6}  F1={F1}  F2={F2:8.4f}  F3={F3}  F4={F4:8.4f}  "
          f"F6={F6:8.5f}  F7={F7:8.5f}  F8={F8:9.5f}  F9={F9:>3d}  F10={F10}")

# ---------------------------------------------------------------- C_f 對照
print("\n[2] C_f 對照 (O206 第十輪 A5 真值) — 睇有冇家族式對應")
M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
CF = {n: MASS[p]/(M0*g(n)) for p, n in zip(["e","u","d","s","mu","c","tau","b"], MODES)}
print(f"  {'n':>3} {'C_f':>10}  {'F4(層v2-mean)':>14} {'F6(γ比)':>10} {'F8(累積γ)':>10}")
for (n, lk, F1, F2, F3, F4, F6, F7, F8, F9, F10), p in zip(rows, ["e","u","d","s","mu","c","tau","b"]):
    print(f"  {n:>3} {CF[n]:>10.4f}  {F4:>14.4f} {F6:>10.5f} {F8:>10.5f}")

print("""
[3] 判定 (先睇有冇結構, 唔呢個係 fit):
  家族內單調性: 如果 F_k 係 chain 內部讀數, 8 個 F_proj 值必須由單一函數族一次過生成,
  唔可以逐個對。C_e 個案: F4(層 v2-mean of v2>=3 層) = 18/5 = 3.6 ≈ C_f(e).
  但注意: 呢個只 match e (mode 1); 其他 mode 喺各自層嘅 F4 值係:
    n=2 (v2=1): F4 = 11/11 = 1.0 (Σv₂(v2=1層) = 11? 計真)
  ⟹ 簡單 F4 唔可以一次過生成 8 值。需要搵「mode 依賴嘅 chain 函數」:
  候選: F6 譜比係唯一 non-trivial 連續單調族 —— 睇 F6 同 C_f 有冇關係。
""")

# F6 vs C_f 詳比
print("[4] F6 (γ_n/γ₁) 同 C_f 嘅緊密比對:")
for (n, lk, F1, F2, F3, F4, F6, F7, F8, F9, F10), p in zip(rows, ["e","u","d","s","mu","c","tau","b"]):
    r = CF[n]/F6
    print(f"  n={n:>2} {p:>3}: C_f={CF[n]:>10.4f}  F6={F6:>10.5f}  C_f/F6={r:>10.4f}")
r_vals = [CF[n]/gs[6] for n, gs in zip(MODES, rows)]
spread = max(r_vals)/min(r_vals)
print(f"  C_f/F6 spread = {spread:.3f}×  (常數 = 結構, 非常數 = C_f 非單調譜函數)")
ck("F6 譜比家族: C_f/F6 唔係常數 (C_f 需要 mode 依賴非譜量)", spread > 3.0, True)

# ---------------------------------------------------------------- 層身份
print("\n[5] 層身份檢查: 每個 C_f 嘅「層級」讀數 (唔 fit, 只列出)")
for (n, lk, F1, F2, F3, F4, F6, F7, F8, F9, F10), p in zip(rows, ["e","u","d","s","mu","c","tau","b"]):
    print(f"  {p:>3} (n={n:>2}, 層 {lk:>6}): C_f={CF[n]:>10.4f}  |層|={F3:>2}  Σγ(層)={F2:>8.4f}  Σv₂(層)={SUM_V2[lk]:>3d}  Σv₂/|L|={F4:>8.4f}")

print("\n" + "="*88)
print(f"U2 chain-intrinsic scan: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*88)
print("PASS" if not FAIL else "FAIL")