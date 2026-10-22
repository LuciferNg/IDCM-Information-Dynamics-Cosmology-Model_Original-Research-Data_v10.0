#!/usr/bin/env python3
"""
O187 Step 2: LOOCV 框架 — 分辨「查找表」vs「代數公式」
=====================================================
核心診斷: 任何「查找表」式規則 (每個 (color,T3,g) 對應一個 n)
必然通過唔到 LOOCV — 因為移除一個粒子後, 該量子數組合冇訓練數據。

只有「代數公式」式規則 (n = 量子數嘅解析函數) 先可能通過。

測試程序:
1. 對每個費米子 i: 用其餘 7 個建立規則 → 預測第 i 個嘅 (n, P_f)
2. 檢查: 預測係咪唯一鎖定? 質量誤差 < 5%?
3. 8 次 LOOCV 全通過 → 先算結構閉合

盲測協議 (三不原則):
- 訓練過程禁止讀取第 i 個粒子嘅質量
- 只用量子數 (Q, T3, g, color) + C₄₄⊗C₅ 拓撲性質
"""
import numpy as np
import json, os, itertools, sys

phi = (1+np.sqrt(5))/2
psi = -1/phi
def L(n): return phi**n + psi**n
def F(n): return (phi**n - psi**n)/np.sqrt(5)

Nd = 44
gamma = 4*np.sin(np.pi*np.arange(1,45)/88)**2
M0 = 27.900915  # MeV (O34/O38 標度, 唯一外部輸入)

# ── 量子數數據集 (無質量) ──
# name, Q, T3, gen, color, n_existing, Pf_desc
fermions = [
    ('e',  -1,   -0.5, 1, 'singlet', 1,  'L6/F5'),
    ('mu', -1,   -0.5, 2, 'singlet', 7,  'Nd-E_proj'),
    ('tau',-1,   -0.5, 3, 'singlet', 20, 'Nd-L4'),
    ('u',  +2/3, +0.5, 1, 'triplet', 1,  'Nd-E_proj'),
    ('d',  -1/3, -0.5, 1, 'triplet', 1,  'Nd-L5'),
    ('s',  -1/3, -0.5, 2, 'triplet', 14, 'L6/F5'),
    ('c',  +2/3, +0.5, 2, 'triplet', 34, 'F7'),
    ('b',  -1/3, -0.5, 3, 'triplet', 33, 'Nd'),
]

# PDG 質量 (只喺驗證用, 訓練禁用)
PDG = {'e':0.511,'mu':105.66,'tau':1776.86,'u':2.16,'d':4.67,'s':93,'c':1270,'b':4180}

# P_f 候選 (全部 Lucas/Fibonacci/N_d 組合)
PF_CANDS = {}
for i in range(0, 10):
    PF_CANDS[f'L{i}'] = L(i)
    PF_CANDS[f'F{i}'] = F(i)
for i in range(0, 10):
    for j in range(1, 10):
        if abs(F(j)) > 1e-9: PF_CANDS[f'L{i}/F{j}'] = L(i)/F(j)
        if abs(L(j)) > 1e-9: PF_CANDS[f'F{i}/L{j}'] = F(i)/L(j)
for i in range(1, 10):
    for j in range(1, 10):
        PF_CANDS[f'L{i}+L{j}'] = L(i)+L(j)
        PF_CANDS[f'L{i}-L{j}'] = L(i)-L(j)
for k, v in list(PF_CANDS.items()):
    if 0 < v < 100:
        PF_CANDS[f'Nd-({k})'] = Nd - v

print("="*70)
print(" O187 Step 2: LOOCV 框架")
print("="*70)

print(f"""
── 核心診斷: 查找表必然失敗 ──

假設規則 f: (color, T3, g) ↦ n 係查找表:
  移除 e⁻ 後, (singlet, -½, 1) 組合冇訓練數據
  → 冇辦法預測 e⁻ 嘅 n
  → 查找表 LOOCV 必然 FAIL

只有「代數公式」先有可能:
  n = F(Q, T3, g, color)  (解析函數)
  即使移除一個粒子, 公式仍然適用
""")

# ── 測試 1: 純量子數查找表 (對照組) ──
print("── 測試 1: 查找表對照 ──")
for i, (name, Q, T3, g, color, n_obs, pfd) in enumerate(fermions):
    train = [f for j, f in enumerate(fermions) if j != i]
    # 有冇其他粒子同 (color,T3,g) 組合?
    same_qn = [t for t in train if t[3] == g and t[4] == color and t[2] == T3]
    if same_qn:
        print(f"  {name}: 同 (color,T3,g) 嘅訓練樣本 = {[t[0] for t in same_qn]} → 可查表")
    else:
        print(f"  {name}: (color={color}, T3={T3}, g={g}) 喺訓練集冇同類 → 🔴 查找表 FAIL")

# ── 測試 2: 候選代數公式 ──
print(f"\n── 測試 2: 候選代數公式 ──")

# 候選公式列表 (只用量子數 + 譜)
def candidates(name, Q, T3, g, color):
    """候選 (n, P_f) 公式 — 全部只用量子數同結構常數"""
    out = []
    g_int = int(round(g))
    # A: n = L(g) 家族 (輕子 g=2→7=L4?)
    out.append(('n=L(g+2)', L(g_int+2)))
    # B: n = F(g+3) 家族 (g=2→F5=5?)
    out.append(('n=F(g+3)', F(g_int+3)))
    # C: n = N_d/g 家族
    out.append(('n=Nd/g', Nd/g_int))
    # D: n = 2^g - 1? (g=1→1, g=2→3)
    out.append(('n=2^g-1', 2**g_int - 1))
    # E: n = L(g)*L(g)? (g=1→1, g=2→9)
    out.append(('n=L(g)^2', L(g_int)**2))
    return out

for i, (name, Q, T3, g, color, n_obs, pfd) in enumerate(fermions):
    c = candidates(name, Q, T3, g, color)
    hits = [f"{fname}={val:.1f}" for fname, val in c if abs(val - n_obs) < 0.5]
    print(f"  {name} (Q={Q}, T3={T3}, g={g}, {color}): n_obs={n_obs}")
    for fname, val in c:
        mark = ' ✓' if abs(val-n_obs) < 0.5 else ''
        print(f"    {fname} = {val:.2f}{mark}")
    if not hits:
        print(f"    🔴 冇候選公式命中 n={n_obs}")

# ── 測試 3: 質量比規則 (真結構部分) ──
print(f"\n── 測試 3: 質量比 = γ 比 (真結構, 可 LOOCV) ──")
print(f"規則: 同一 P_f 嘅兩個粒子, 質量比 = γ_{'{n1}'}/γ_{'{n2}'}")
print(f"測試: μ (P_f=15.5) vs u (P_f=15.5): γ₇/γ₁ = {gamma[6]/gamma[0]:.1f}")
print(f"      PDG: 105.66/2.16 = {105.66/2.16:.1f}  → {'✅ 結構預測' if abs(gamma[6]/gamma[0]-105.66/2.16)/(105.66/2.16)<0.05 else '❌'}")
print(f"      s (P_f=3.6) vs e (P_f=3.6): γ₁₄/γ₁ = {gamma[13]/gamma[0]:.1f}")
print(f"      PDG: 93/0.511 = {93/0.511:.1f}  → {'✅ 結構預測' if abs(gamma[13]/gamma[0]-93/0.511)/(93/0.511)<0.05 else '❌'}")

# ── 測試 4: 完整 LOOCV — 用質量比規則預測 ──
print(f"\n── 測試 4: LOOCV — P_f 分組質量比預測 ──")
# 如果已知一個粒子嘅 (n, P_f) 同質量, 同一 P_f 組嘅另一粒子:
# m₂/m₁ = γ_{n₂}/γ_{n₁} → 需要知 n₂ — 但 n₂ 係乜?
# 如果 n₂ 由量子數決定... 循環問題
print("關鍵循環: 質量比規則只鎖定『相對』質量, 唔鎖定 n 本身")
print("→ n 必須由量子數先驗鎖定, 質量比先有用")
print("→ 目前: n 嘅先驗規則 唔存在 → LOOCV 無法完整進行")

# ═══════════════════════════════════════════════════════════════
# 結論
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f" O187 Step 2 結論")
print(f"{'='*70}")
print(f"""
  🔴 確認: n 嘅先驗規則 目前唔存在

  1. 查找表 (color,T3,g)→n: LOOCV 必然 FAIL (8/8)
     → 每個量子數組合唯一, 移除即無法預測

  2. 簡單代數公式 (L(g), F(g+3), 2^g-1, L(g)²):
     → 冇一個命中 8 個粒子嘅 n

  3. 質量比 = γ 比 (真結構):
     → 有效但只鎖定相對質量, 唔鎖定 n 本身

  4. P_f 同 n 嘅配對: 冇先驗規則

  → O187 保持 🔴 開放
  → O136 質量譜 = 後驗擬合 (唔係結構推導)

  下一步 (如果要繼續):
  - 搜尋更大嘅代數公式空間 (n = 量子數嘅非平凡組合)
  - 或者接受 O136 為「後驗擬合」, 從零重新推導質量譜
""")
