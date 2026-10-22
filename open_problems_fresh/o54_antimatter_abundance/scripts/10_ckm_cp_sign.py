#!/usr/bin/env python3
"""
O54 — 檢查 10: CKM/CP 差額符號 — 點解物質 > 反物質
==================================================
目標: 用 CKM 結構 (δ_CKM = 66.40°, O53 閉合) 推導
      「點解宏觀物質 > 反物質」嘅符號來源。

背景:
- IDCM: 物質 = 差頻 (拍頻投影), 反物質 = 和頻
- 對產生係對稱嘅 (荷守恆): 0 → (+1) + (−1)
- 但宏觀 n_B̄/n_B < 1e-9 (物質主導)
- ⟹ 需要「符號」機制: 點解差頻通道 (物質) 有優勢?

候選: CKM 相位 δ_CKM = 66.40° (O53 閉合)
- J_CP = 3.2267e-5 (檢查 3: PDG 1.47%)
- CP 破壞 = 物質/反物質 不對稱嘅微觀來源 (Sakharov)

但 IDCM 冇熱大爆炸 (冇 freeze-out) — 需要結構版本:

新結構假設:
- 投影 T_pipe 係「有向」: 差頻 (物質) 被投影, 和頻 (反物質) 唔被投影
- 方向性來源 = CKM 相位 δ ≠ 0 (CP 破壞 = 投影方向性)
- δ_CKM = 66.40° > 0 ⟹ 差頻優先投影 ⟹ 物質主導

檢查:
1. CKM 矩陣結構 (δ_CKM = 66.40°)
2. J_CP 符號 vs 投影方向
3. 差頻/和頻 不對稱定量
4. η_B 符號 = f(δ_CKM)
5. 結論: 符號機制
"""
import math
import json
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi

print("=" * 72)
print("O54 檢查 10: CKM/CP 差額符號 — 點解物質 > 反物質")
print("=" * 72)

# ============ 1. CKM 結構 ============
print("\n[1] CKM 矩陣結構 (O53 閉合)")
print("-" * 72)
delta_ckm = 66.40  # 度
delta_rad = math.radians(delta_ckm)
print(f"  δ_CKM = {delta_ckm}° (O53 攻堅二閉合)")
print(f"  J_CP = 3.2267e-5 (檢查 3: PDG 1.47%)")
print(f"  sin(δ) = {math.sin(delta_rad):.4f} > 0 ⟹ J_CP > 0")

# J_CP 符號
print(f"\n  J_CP 符號 = sign(sin δ) = + (正)")
print(f"  ⟹ CP 破壞係「正方向」: 物質通道優先")

# ============ 2. 投影方向性 ============
print("\n[2] 投影方向性: T_pipe 有向性")
print("-" * 72)
print(f"""
  假設: 投影 T_pipe 係有向 (差頻優先):
  - σ_n(差頻) = 1 (完全投影, 物質)
  - σ_n(和頻) = f_proj < 1 (部分投影, 反物質被抑制)

  CKM 相位 δ = 66.40° > 0 ⟹ 差頻通道耦合更強
  ⟹ 差頻 (物質) 投影率 > 和頻 (反物質) 投影率

  定量: 投影不對稱度 ε_CP?
  ε_CP ∝ J_CP = 3.2267e-5 (CP 破壞大小)
  ⟹ 物質/反物質 差額 ∝ J_CP × 結構因子

  🔴 但 η_B = 6.062e-10 >> J_CP = 3.2e-5?
  η_B/J_CP = 1.88e-5 (檢查 3)
  ⟹ 需要額外放大/抑制因子 (1.88e-5)
""")

# ============ 3. 差頻/和頻不對稱 ============
print("\n[3] 差頻/和頻 不對稱定量")
print("-" * 72)
# K_Chain 頻率
Nd = 44
omegas = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)])

# 差頻譜 vs 和頻譜
diffs = []
sums = []
for a in range(Nd):
    for b in range(a + 1, Nd):
        diffs.append(abs(omegas[a] - omegas[b]))
        sums.append(omegas[a] + omegas[b])
diffs = np.array(diffs)
sums = np.array(sums)

print(f"  差頻 (物質): {len(diffs)} 個值, mean = {diffs.mean():.4f}")
print(f"  和頻 (反物質): {len(sums)} 個值, mean = {sums.mean():.4f}")
print(f"  和頻/差頻 mean 比 = {sums.mean()/diffs.mean():.4f}")

# 能量差
print(f"\n  和頻平均能量 > 差頻平均能量:")
print(f"  ΔE_mean = {sums.mean()-diffs.mean():.4f} (ω 單位)")
print(f"  ⟹ 反物質通道平均需要更多能量")
print(f"  ⟹ 宏觀 (低能量環境) 差頻佔優 = 物質主導 ✅")

# ============ 4. η_B 符號 ============
print("\n[4] η_B 符號 = f(δ_CKM)")
print("-" * 72)
print(f"""
  IDCM 結構鏈 (已閉合):
  η_B = n_B/n_γ = 6.0622e-10 (0.62%)

  符號分解:
  |η_B| = 能量分配結構 (Ω_Λ → Ω_m → Ω_b)  — 大小
  sign(η_B) = 投影方向性 (δ_CKM > 0)       — 符號

  如果 δ_CKM < 0 (CP 相位反轉):
  ⟹ 和頻優先投影 ⟹ 反物質主導 (反宇宙?)

  觀察: 我哋宇宙 δ_CKM = +66.40° > 0
  ⟹ 物質主導 = δ_CKM 符號嘅投影後果
""")

# ============ 5. 結構驗證: δ 同 K_Chain 相位 ============
print("\n[5] δ_CKM 同 K_Chain 相位量子")
print("-" * 72)
pi_88 = 180 / 88  # 相位量子 (度)
print(f"  π/88 = {pi_88:.6f}° (K_Chain 相位量子)")
print(f"  δ_CKM/(π/88) = {delta_ckm/pi_88:.4f}")

# 檢查 δ 同 66.40 嘅結構
# 66.40 = 72 − 5.60 (2π/5 減去偏移)
# 5.60 = ?
print(f"\n  66.40 = 72 − 5.60")
print(f"  5.60/π = {5.60/math.pi:.4f}")
print(f"  5.60/(π/88) = {5.60/pi_88:.4f}")

# 試 φ 表達式
print(f"\n  φ 檢查:")
for expr, val in [
    ("φ⁴−φ⁻⁴", phi**4 - phi_inv**4),
    ("φ³+φ⁻³", phi**3 + phi_inv**3),
    ("2φ", 2*phi),
]:
    print(f"  {expr} = {val:.4f}")

# ============ 6. 結論 ============
print("\n[6] 檢查 10 結論")
print("-" * 72)
print(f"""
  ★ 差額符號機制 (CKM/CP):

  1. δ_CKM = 66.40° > 0 ⟹ J_CP > 0 ⟹ CP 破壞正方向
  2. 投影 T_pipe 有向性: 差頻 (物質) 優先投影
     ⟹ 宏觀物質主導 (n_B̄/n_B < 1e-9)
  3. 和頻 (反物質) 平均能量更高:
     ΔE_mean = {sums.mean()-diffs.mean():.4f} (ω 單位)
     ⟹ 宏觀低能量環境差頻佔優
  4. |η_B| = 能量分配 (大小), sign = δ_CKM (符號)
  5. 如果 δ_CKM < 0 → 反宇宙 (預言)

  🟡 部分閉合: 符號方向清晰 (δ > 0 → 物質)
  🔴 開放: δ_CKM = 66.40° 嘅「投影耦合」精確形式
""")

results = {
    "test": "CKM/CP 差額符號",
    "delta_ckm": delta_ckm,
    "J_cp": 3.2267e-5,
    "J_cp_sign": "+",
    "sum_mean": float(sums.mean()),
    "diff_mean": float(diffs.mean()),
    "delta_E_mean": float(sums.mean() - diffs.mean()),
    "eta_B_sign": "+",
    "eta_B_mechanism": "能量分配 (大小) + δ_CKM 投影 (符號)",
    "antiuniverse_prediction": "δ_CKM < 0 → 反宇宙",
    "conclusion": "δ_CKM=66.40°>0 ⟹ J_CP>0 ⟹ 差頻(物質)優先投影; 和頻平均能量更高 (ΔE=0.946) ⟹ 宏觀物質主導; |η_B|=能量分配, sign=δ_CKM",
}
print("驗證摘要:")
for k, v in results.items():
    print(f"  {k}: {v}")

with open("data/10_ckm_cp_sign.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n✅ 結果已寫入 data/10_ckm_cp_sign.json")
