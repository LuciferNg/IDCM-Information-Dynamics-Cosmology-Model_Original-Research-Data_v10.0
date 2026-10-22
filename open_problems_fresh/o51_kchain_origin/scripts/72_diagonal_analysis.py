#!/usr/bin/env python3
"""
O51/72: 對角化分析 — λ_sync/2 vs r_drag 嘅 0.237% 偏差
===============================================================
發現: 0.237% ≈ 1/421 = 1/(L₇×F₇ + N_d) = 1/(29×13 + 44)
驗證: 呢個係結構修正定係巧合?

結構推導:
  rd_idcm = λ_sync/2 = πR_H/88 (純結構, 零 ΛCDM 參數)
  r_drag = 147.09 Mpc (Planck 2018, ΛCDM sound horizon)
  dev = 0.237% = 1/421 = 1/(L₇×F₇ + N_d)
  
如果真係結構修正:
  r_drag = rd_idcm × (1 - 1/(L₇×F₇ + N_d)) = 147.44 × (1 - 1/421)
  = 147.44 × 420/421 = 147.09 Mpc ✅
"""
import json, math, sys

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. 基礎數字 ============
R_H = 4129.94
L_7, F_7, N_d, B = 29, 13, 44, 4
phi = (1 + math.sqrt(5)) / 2

rd_idcm = math.pi * R_H / 88  # λ_sync/2
r_drag = 147.09  # Planck 2018
dev = rd_idcm / r_drag - 1

print("=" * 62)
print("λ_sync/2 vs r_drag 對角化分析")
print("=" * 62)
print(f"rd_idcm = {rd_idcm:.6f} Mpc")
print(f"r_drag  = {r_drag:.6f} Mpc (Planck 2018)")
print(f"dev = {dev*100:.6f}% = {dev:.6f} (ratio)")

# ============ 2. 候選結構 ============
print("\n" + "=" * 62)
print("候選結構修正")
print("=" * 62)

candidates = []

# 候選 1: 1/(L₇×F₇ + N_d) = 1/421
c1 = 1 / (L_7 * F_7 + N_d)
candidates.append(('1/(L₇×F₇ + N_d) = 1/421', c1, abs(dev - c1)/dev*100))

# 候選 2: 1/(L₇×F₇) = 1/377
c2 = 1 / (L_7 * F_7)
candidates.append(('1/(L₇×F₇) = 1/377', c2, abs(dev - c2)/dev*100))

# 候選 3: φ⁻⁸ = 1/φ⁸
c3 = phi**(-8)
candidates.append(('φ⁻⁸', c3, abs(dev - c3)/dev*100))

# 候選 4: φ⁻⁹
c4 = phi**(-9)
candidates.append(('φ⁻⁹', c4, abs(dev - c4)/dev*100))

# 候選 5: 1/(2N_d²) = 1/(2×44²)
c5 = 1 / (2 * N_d**2)
candidates.append(('1/(2N_d²) = 1/3872', c5, abs(dev - c5)/dev*100))

# 候選 6: 1/(F₇×L₇ - N_d) = 1/(377-44) = 1/333
c6 = 1 / (F_7 * L_7 - N_d)
candidates.append(('1/(F₇×L₇ - N_d) = 1/333', c6, abs(dev - c6)/dev*100))

# 候選 7: B/N_d² = 4/44²
c7 = B / N_d**2
candidates.append(('B/N_d² = 4/44²', c7, abs(dev - c7)/dev*100))

# 候選 8: 1/(φ⁴B) = 1/(φ⁴×4)
c8 = 1 / (phi**4 * B)
candidates.append(('1/(φ⁴B)', c8, abs(dev - c8)/dev*100))

# 候選 9: 1/(Σγ + N_d) = 1/(90+44) = 1/134
c9 = 1 / (90 + N_d)
candidates.append(('1/(Σγ+N_d) = 1/134', c9, abs(dev - c9)/dev*100))

# 候選 10: 1/(L₇²+F₇²) = 1/(29²+13²) = 1/1010
c10 = 1 / (L_7**2 + F_7**2)
candidates.append(('1/(L₇²+F₇²) = 1/1010', c10, abs(dev - c10)/dev*100))

print(f"{'候選':<35}{'值':<15}{'偏差%':<10}")
print("-" * 60)
for name, val, err in sorted(candidates, key=lambda x: x[2]):
    print(f"{name:<35}{val:<15.6f}{err:<10.2f}%")

best = min(candidates, key=lambda x: x[2])
print(f"\n最佳: {best[0]} = {best[1]:.6f}, dev from obs = {best[2]:.2f}%")

# ============ 3. 驗證最佳候選 ============
print("\n" + "=" * 62)
print("最佳候選驗證: 1/(L₇×F₇ + N_d) = 1/421")
print("=" * 62)
L7F7_Nd = L_7 * F_7 + N_d  # 421
print(f"L₇×F₇ + N_d = {L_7}×{F_7} + {N_d} = {L7F7_Nd}")
print(f"1/{L7F7_Nd} = {1/L7F7_Nd:.6f} = {1/L7F7_Nd*100:.4f}%")

# 結構修正
rd_corrected = rd_idcm * (1 - 1/L7F7_Nd)
print(f"\nrd_corrected = rd_idcm × (1 - 1/{L7F7_Nd})")
print(f"             = {rd_idcm:.6f} × ({L7F7_Nd-1}/{L7F7_Nd})")
print(f"             = {rd_idcm:.6f} × {(L7F7_Nd-1)/L7F7_Nd:.6f}")
print(f"             = {rd_corrected:.6f} Mpc")
print(f"r_drag       = {r_drag:.6f} Mpc")
print(f"dev          = {abs(rd_corrected - r_drag)/r_drag*100:.4f}%")

check("rd_corrected ≈ r_drag (0.1%)", abs(rd_corrected - r_drag)/r_drag < 0.001,
      f"修正後 dev = {abs(rd_corrected - r_drag)/r_drag*100:.4f}%")

# ============ 4. 結構意義 ============
print("\n" + "=" * 62)
print("4. 結構意義")
print("=" * 62)
print(f"421 = L₇×F₇ + N_d = 29×13 + 44")
print(f"    = 377 + 44")
print(f"    = F₇×L₇ + N_d")
print(f"\n如果 1/(L₇×F₇ + N_d) 係結構修正,")
print(f"r_drag = πR_H/88 × (1 - 1/(L₇×F₇ + N_d))")
print(f"       = πR_H/88 × (F₇×L₇ + N_d - 1)/(F₇×L₇ + N_d)")
print(f"       = πR_H/88 × 420/421")
print(f"\n421 = 421 係質數。421 = 20²+21² = 400+21")
print(f"但最直接: 421 = L₇×F₇ + N_d — 呢個組合有結構意義嗎?")

# 檢查 421 有冇其他 IDCM 結構
print(f"\n421 相關結構:")
print(f"  L₇×F₇ = 377 = F₁₄")
print(f"  F₁₄ = 377 (Fibonacci 數!)")
print(f"  421 = F₁₄ + N_d = 377 + 44")
print(f"  421 = F₁₄ + N_d  ✓")
print(f"  421 = L₇×F₇ + N_d = F₁₄ + N_d")

# 驗證 F₁₄ = 377
F = [0, 1]
for i in range(2, 15):
    F.append(F[-1] + F[-2])
print(f"  F₁₄ = F(14) = {F[14]} ✅")

# ============ 5. 總結 ============
print(f"\n{'=' * 62}")
print(f"對角化分析總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'rd_idcm': round(rd_idcm, 6),
    'r_drag': r_drag,
    'dev_raw': round(dev*100, 4),
    'L7F7_Nd': L7F7_Nd,
    'inv_421': 1/L7F7_Nd,
    'rd_corrected': round(rd_corrected, 6),
    'dev_corrected': round(abs(rd_corrected - r_drag)/r_drag*100, 4),
    'best_candidate': best[0],
    'fibonacci_14': F[14],
    'pass': PASS,
    'fail': FAIL
}

with open('data/72_diagonal_analysis.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/72_diagonal_analysis.json")