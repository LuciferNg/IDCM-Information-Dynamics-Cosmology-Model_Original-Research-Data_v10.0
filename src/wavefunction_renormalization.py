"""
IDCM v10.0 — 真正嘅波函數重整化從 d_{ijk} 張量推導
=====================================================
目標: 從 d_{ijk} 張量嚴格推導 Z-factor，驗證 √φ 嘅幾何來源
"""

import math
import numpy as np
import os

# ══════════════════════════════════════════════════════════════
# 基本常數
# ══════════════════════════════════════════════════════════════
φ = (1 + math.sqrt(5)) / 2
M_Pl = 1.220890e22  # MeV

EIGENVALUES = [
    51.5606114384, 10.0002078429, 4.5782815814, 3.4328552619,
    1.8661710340, 0.2347191871, 0.0227488532, 0.0117201474,
    0.0068136131, 0.0018507699, 0.0013608351, -1.264797e-11
]

V_CYCLES = {"Gen3": 42.7396, "Gen2": 44.9431, "Gen1": 46.5390}

PARTICLE_MAP = [
    ("Top",     0, "Gen3", "up",   True),
    ("Bottom",  1, "Gen3", "down", False),
    ("Tau",     2, "Gen3", "lep",  False),
    ("Charm",   3, "Gen2", "up",   True),
    ("Strange", 4, "Gen2", "down", False),
    ("Muon",    5, "Gen2", "lep",  False),
    ("Up",      6, "Gen1", "up",   False),
    ("Down",    7, "Gen1", "down", False),
    ("Electron",8, "Gen1", "lep",  True),
    ("ν_τ",     9, "Gen1", "n1",   False),
    ("ν_μ",    10, "Gen1", "n2",   False),
]

PDG = {"Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
       "Charm": 1270.0, "Strange": 93.4, "Muon": 105.6583745,
       "Up": 2.16, "Down": 4.67, "Electron": 0.51099895}

# ══════════════════════════════════════════════════════════════
# 1. 載入數據
# ══════════════════════════════════════════════════════════════
d_path = "data/d_tensor_final.npy"
d = np.load(d_path)
n = d.shape[0]
v = np.array([φ ** (-k / 12) for k in range(n)])

print("=" * 80)
print("IDCM v10.0 — 波函數重整化從 d_{ijk} 嚴格推導")
print("=" * 80)
print(f"\nd_tensor shape: {d.shape}")
print(f"d_tensor 負值比例: {np.sum(d < 0) / d.size * 100:.1f}%")
print(f"d_tensor 正最小值: {d[d > 0].min():.6e}")
print(f"d_tensor 負最大值: {d[d < 0].max():.6e}")

# ══════════════════════════════════════════════════════════════
# 2. 裸 Yukawa 矩陣
# ══════════════════════════════════════════════════════════════
Y = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        Y[i, j] = sum(d[i, j, k] * v[k] for k in range(n))

Y_sym = (Y + Y.T) / 2
sym_err = np.max(np.abs(Y - Y.T))
print(f"\nYukawa 矩陣對稱誤差: {sym_err:.2e}")

# 對角化
eigvals_Y, eigvecs_Y = np.linalg.eigh(Y_sym)
idx = np.argsort(eigvals_Y)[::-1]
eigvals_Y = eigvals_Y[idx]
eigvecs_Y = eigvecs_Y[:, idx]

print(f"Yukawa 本徵值 (前 12): {[f'{e:.6f}' for e in eigvals_Y[:12]]}")
print(f"零態檢查: {sum(1 for e in eigvals_Y if abs(e) < 1e-10)}")

# ══════════════════════════════════════════════════════════════
# 3. 從 d_{ijk} 嚴格推導 Z-factor
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 從 d_{ijk} 嚴格推導 Z-factor")
print("─" * 80)

# 方法 A: Kähler 度量方法
# K_{iī} = d_{iik} v_k (對角近似)
# Z_i = 1 / K_{iī} 正規化
print("\n  [方法 A] Kähler 度量 Z-factor:")
K_diag = np.array([sum(d[i, i, k] * v[k] for k in range(n)) for i in range(n)])
print(f"  K_ii 對角元素: {[f'{k:.4f}' for k in K_diag]}")
print(f"  負值: {sum(1 for k in K_diag if k < 0)}/{n}")

# 用絕對值處理
K_abs = np.array([abs(k) if abs(k) > 1e-15 else 1e-15 for k in K_diag])
Z_A = 1.0 / K_abs
Z_A = Z_A / np.max(Z_A)

# 方法 B: 自我相交數方法
# Z_i ∝ 1/|d_{iii}| (波函數局域化)
print("\n  [方法 B] 自我相交數 Z-factor:")
d_diag = np.array([abs(d[i, i, i]) if abs(d[i, i, i]) > 1e-15 else 1e-15 for i in range(n)])
Z_B = 1.0 / d_diag
Z_B = Z_B / np.max(Z_B)

# 方法 C: Yukawa 本徵向量方法
# Z_i = 本徵向量嘅範數
print("\n  [方法 C] Yukawa 本徵向量 Z-factor:")
Z_C = np.array([np.linalg.norm(eigvecs_Y[i, :]) for i in range(n)])
Z_C = Z_C / np.max(Z_C)

# 方法 D: Yukawa 本徵值方法
# Z_i = 1/|Y_{ii}| (對角 Yukawa 嘅 inverse)
print("\n  [方法 D] Yukawa 對角元素 Z-factor:")
Y_diag = np.array([abs(Y_sym[i, i]) if abs(Y_sym[i, i]) > 1e-15 else 1e-15 for i in range(n)])
Z_D = 1.0 / Y_diag
Z_D = Z_D / np.max(Z_D)

# 方法 E: 用 Yukawa 本徵向量嘅第二範數
# 本徵向量嘅分量平方和 = 1，但每個本徵向量嘅「集中度」= 1/|U_{ii}|
print("\n  [方法 E] 本徵向量集中度 Z-factor:")
Z_E = np.array([1.0 / max(abs(eigvecs_Y[i, i]), 1e-15) for i in range(n)])
Z_E = Z_E / np.max(Z_E)

# ══════════════════════════════════════════════════════════════
# 4. 用 Z-factor 做質量預測
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. Z-factor 質量預測對比")
print("─" * 80)

def compute_bare_mass(li, gen):
    return EIGENVALUES[li] * M_Pl * math.exp(-V_CYCLES[gen])

# 舊 sector factor (empirical, 但用作參考)
old_factors = {
    "down": {"Gen3": 1/8.0, "Gen2": 1/7.4, "Gen1": 5.3},
    "lep":  {"Gen3": 1/8.6, "Gen2": 1.22,  "Gen1": 1.0},
    "up":   {"Gen3": 1.0,   "Gen2": 1.0,   "Gen1": math.sqrt(φ)},
}

methods = {
    "A: Kähler metric": Z_A,
    "B: d_iii self-intersection": Z_B,
    "C: Eigenvector norm": Z_C,
    "D: Yukawa diagonal": Z_D,
    "E: Eigenvector concentration": Z_E,
}

for method_name, Z in methods.items():
    # Up 嘅 Z-factor
    up_idx = 6  # Up = index 6
    Z_up = Z[up_idx]
    Z_up_sqrt = math.sqrt(Z_up) if Z_up > 0 else 0
    bare_up = compute_bare_mass(up_idx, "Gen1")
    pred_up = bare_up * Z_up_sqrt
    up_err = abs(pred_up / PDG["Up"] - 1) * 100

    print(f"\n  {method_name}:")
    print(f"    Z_Up = {Z_up:.4f}, √Z_Up = {Z_up_sqrt:.4f}")
    print(f"    Up pred = {pred_up:.4f} MeV, PDG = {PDG['Up']:.4f} MeV, err = {up_err:.2f}%")
    print(f"    vs √φ factor = {math.sqrt(φ):.6f}")

    # 所有粒子預測
    total_err = 0
    count = 0
    print(f"    {'粒子':>10} | {'Z_i':>8} | {'√Z':>8} | {'預測':>15} | {'PDG':>15} | {'誤差%':>8}")
    print(f"    " + "-" * 70)
    for name, li, gen, sec, is_cal in PARTICLE_MAP:
        if is_cal or name in ["ν_τ", "ν_μ"]:
            continue
        bare = compute_bare_mass(li, gen)
        Z_i = Z[li]
        Z_sqrt = math.sqrt(Z_i) if Z_i > 0 else 0
        pred = bare * Z_sqrt
        pdg = PDG[name]
        err = abs(pred / pdg - 1) * 100
        total_err += err
        count += 1
        print(f"    {name:>10} | {Z_i:>8.4f} | {Z_sqrt:>8.4f} | {pred:>15.4f} | {pdg:>15.4f} | {err:>7.2f}%")

    print(f"    → 平均誤差: {total_err/count:.2f}% (count={count})")

# ══════════════════════════════════════════════════════════════
# 5. 關鍵分析: √φ 嘅幾何來源
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 關鍵分析: √φ 嘅幾何來源")
print("─" * 80)

# 所有粒子嘅所需 factor 同 φ-power 結構
print(f"\n  所有粒子所需 factor 嘅 φ-power 結構:")
print(f"  {'粒子':>10} | {'λ':>8} | {'所需 factor':>12} | {'k = ln(f)/ln(φ)':>18} | {'near 0.5?':>10}")
print(f"  " + "-" * 65)

for name, li, gen, sec, is_cal in PARTICLE_MAP:
    if is_cal or name in ["ν_τ", "ν_μ"]:
        continue
    bare = compute_bare_mass(li, gen)
    pdg = PDG[name]
    needed = pdg / bare
    k = math.log(needed) / math.log(φ)
    near_half = abs(k - 0.5) < 0.1
    print(f"  {name:>10} | {EIGENVALUES[li]:>8.4f} | {needed:>12.6f} | {k:>18.4f} | {'✅' if near_half else '❌':>10}")

# 檢查: 點解 Gen1 up 嘅 factor 係 √φ?
# 答案: 因為 Gen1 up (Up) 同 Gen1 lep (Electron) 嘅 eigenvalue 比例
# λ_Up / λ_Electron = 0.02275 / 0.00681 = 3.34
# 而 Electron 係 calibration point (factor=1), 所以 Up 嘅 factor 需要
# 等於 (PDG_Up / PDG_Electron) / (λ_Up / λ_Electron) × (V_cycle 修正)
# 呢個比例自然收斂到 √φ

print(f"\n  物理: 點解 Gen1 Up 嘅 factor = √φ?")

# Electron calibration
lam_e = EIGENVALUES[8]  # Electron = index 8
lam_up = EIGENVALUES[6]  # Up = index 6
V_1 = V_CYCLES["Gen1"]
bare_e = lam_e * M_Pl * math.exp(-V_1)
bare_up = lam_up * M_Pl * math.exp(-V_1)
pdg_e = PDG["Electron"]
pdg_up = PDG["Up"]

print(f"\n  Gen1 裸質量:")
print(f"    Electron: λ={lam_e:.6f}, bare={bare_e:.6f} MeV, PDG={pdg_e:.6f} MeV")
print(f"    Up:       λ={lam_up:.6f}, bare={bare_up:.6f} MeV, PDG={pdg_up:.6f} MeV")
print(f"  λ_Up/λ_e = {lam_up/lam_e:.4f}")
print(f"  PDG_Up/PDG_e = {pdg_up/pdg_e:.4f}")
print(f"  Required factor_Up = {pdg_up/bare_up:.4f}")
print(f"  √φ = {math.sqrt(φ):.6f}")
print(f"  Difference: {abs(pdg_up/bare_up - math.sqrt(φ))/(math.sqrt(φ))*100:.2f}%")

# ══════════════════════════════════════════════════════════════
# 6. 結論
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 結論")
print("─" * 80)

print("""
  Z-factor 從 d_{{ijk}} 嚴格推導結果:

  [方法 A] Kähler metric Z-factor:
    - 理論基礎最強 (直接來自 CY₃ Kähler 度量)
    - 但 d_tensor 有 7.1% 負值 → Kähler 度量有負值 → 物理上無意義
    - 需要先解決 d_tensor 正定性問題

  [方法 B] d_{{iii}} 自我相交數:
    - 反映波函數局域化程度
    - 但 d_{{iii}} 有正有負，數值噪聲大

  [方法 C-E] Yukawa 本徵向量方法:
    - 理論上合理但數值上受 d_tensor 噪聲影響
    - 目前無法穩定重現 √φ

  實證結論:
  ─────────────────────────────────────────────────────────────────
  Up 夸克嘅 factor = √φ 係**純粹從實證發現**嘅，
  目前無法從 d_{{ijk}} 嚴格推導出嚟。

  原因: d_tensor_final.npy 有 7.1% 嘅負值噪聲，
  導致 Kähler 度量、Yukawa 矩陣等幾何量都受污染。

  需要:
  1. 先解決 d_tensor 正定性問題 (正定投影)
  2. 然後重新計算 Kähler 度量
  3. 從 Kähler 度量嚴格推導 Z-factor
  4. 預期結果: Z_i ∝ φ^{{k_i}} 其中 k_i 由幾何決定

  目前 √φ 嘅實證支持:
  - k = ln(1.266)/ln(φ) = 0.49 ≈ 0.5 (精確到 2%)
  - √φ 係 IDCM 最自然結構 (光速模式、振幅、beat)
  - 6/8 盲測 < 1% 誤差 (包含 Up 嘅 0.47%)
""")

# 儲存結果
lines = []
lines.append("IDCM v10.0 — 波函數重整化嚴格推導")
lines.append("=" * 70)
lines.append("")
lines.append("## 從 d_{ijk} 張量推導 Z-factor")
lines.append("")
lines.append(f"d_tensor 負值比例: {np.sum(d < 0) / d.size * 100:.1f}%")
lines.append(f"Yukawa 對稱誤差: {sym_err:.2e}")
lines.append("")
lines.append("### 方法 A: Kähler 度量方法")
lines.append(f"Z_Up = {Z_A[6]:.4f}")
lines.append(f"√Z_Up = {math.sqrt(Z_A[6]):.4f}")
lines.append("")
lines.append("### 方法 B: 自我相交數方法")
lines.append(f"Z_Up = {Z_B[6]:.4f}")
lines.append(f"√Z_Up = {math.sqrt(Z_B[6]):.4f}")
lines.append("")
lines.append("### 方法 C: 本徵向量方法")
lines.append(f"Z_Up = {Z_C[6]:.4f}")
lines.append(f"√Z_Up = {math.sqrt(Z_C[6]):.4f}")
lines.append("")
lines.append("### 方法 D: Yukawa 對角方法")
lines.append(f"Z_Up = {Z_D[6]:.4f}")
lines.append(f"√Z_Up = {math.sqrt(Z_D[6]):.4f}")
lines.append("")
lines.append("### 結論")
lines.append("目前從 d_{ijk} 無法穩定推導 √φ，因為 d_tensor 有數值噪聲。")
lines.append("√φ 係實證發現，需先解決 d_tensor 正定性問題。")
lines.append("")

with open("data/wavefunction_renormalization_derivation.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存 data/wavefunction_renormalization_derivation.txt ✅")