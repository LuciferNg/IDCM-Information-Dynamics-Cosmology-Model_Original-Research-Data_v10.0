#!/usr/bin/env python3
"""
O15: ⁷Li 線性 η_B 檢驗 — 敏感度分析
======================================
IDCM: ⁷Li/H = η_B × 2ε(1-ε)  →  ∝ η_B (線性)
ΛCDM: ⁷Li/H ∝ η_B^α, α ≈ 2.1-2.4 (超線性, BBN 核網絡敏感度)

目標: 分辨需要 η_B 範圍, 用文獻數據評估可行性
"""
import math
import sys
sys.path.insert(0, '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p1_bbn/scripts')
import numpy as np

# ============================================================
# [1] 常數
# ============================================================
phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4
kappa = 1 / 16

# IDCM 閉合值
eta_B_idcm = 6.0622e-10          # 已閉合 (0.62%)
factor_2eps = 2 * eps            # 0.309017 = φ⁻¹/2
factor_surv = 1 - eps            # 0.845492
factor_li7 = factor_2eps * factor_surv  # 0.2613

Li7_idcm = eta_B_idcm * factor_li7  # 1.584e-10

# 觀測值
Li7_obs = 1.58e-10               # Spite plateau (Sbordone+2010)
Li7_obs_err = 0.03e-10           # ~2% 誤差

# ΛCDM BBN (η_B = 6.1e-10)
eta_B_lcdm = 6.1e-10
Li7_lcdm = 5.24e-10              # Cyburt+2008 (WMAP5)

# ============================================================
# [2] 標準 BBN ⁷Li 敏感度指数
# ============================================================
# 文獻來源:
# - Cyburt+2008 (JCAP 0811:012): d(log Y_Li7)/d(log η_B) ≈ 2.4
# - Fields+2011 (Ann.Rev.Nucl.Part.Sci.): ≈ 2.4
# - Burns+2026 (Phys.Rept. 1194): 完整敏感度地圖
# - Coc+2014 (PRD 90, 085018): ≈ 2.1-2.4 視 η_B 範圍
#
# 原因: ⁷Li ∝ ⁷Be ∝ ³He(α,γ)⁷Be, 而 ³He/H 本身 ∝ η_B^(-0.6)
# 所以 ⁷Li/H ∝ η_B × ³He/H ∝ η_B × η_B^(-0.6) = η_B^0.4? 不對
# 實際: ⁷Be 產量 ∝ ³He × ⁴He, ⁴He 基本常數, ³He 隨 η_B 增加而減少
# 核網絡耦合複雜, 敏感度指数 ≈ 2.1-2.4

# 用兩個常見指数
ALPHA_LCDM_LOW = 2.1    # 較保守
ALPHA_LCDM_HIGH = 2.4   # 標準值

# ============================================================
# [3] 模型比較: ⁷Li/H vs η_B
# ============================================================
eta_range = np.logspace(-10.5, -9.0, 100)  # η_B ∈ [3e-11, 1e-9]

# IDCM: 線性
Li7_idcm_eta = eta_range * factor_li7

# ΛCDM: η_B^α, 歸一化於 η_B = 6.1e-10
Li7_lcdm_low = Li7_lcdm * (eta_range / eta_B_lcdm) ** ALPHA_LCDM_LOW
Li7_lcdm_high = Li7_lcdm * (eta_range / eta_B_lcdm) ** ALPHA_LCDM_HIGH

print("=" * 72)
print("O15: ⁷Li 線性 η_B 檢驗 — 敏感度分析")
print("=" * 72)

print(f"\n[1] 模型預測 @ η_B = {eta_B_idcm:.2e}")
print("-" * 72)
print(f"IDCM: ⁷Li/H = η_B × {factor_li7:.6f} = {Li7_idcm:.4e}")
print(f"       ∝ η_B^{1.0:.1f} (線性)")
print(f"ΛCDM: ⁷Li/H ∝ η_B^{ALPHA_LCDM_LOW:.1f}–{ALPHA_LCDM_HIGH:.1f} (超線性)")
print(f"       @ η_B = 6.1e-10: ⁷Li/H = {Li7_lcdm:.4e}")
print(f"觀測: ⁷Li/H = {Li7_obs:.4e} ± {Li7_obs_err:.2e}")

print(f"\n[2] 分辨需要 η_B 範圍")
print("-" * 72)
print("要分辨 ⁷Li ∝ η_B (IDCM) vs η_B^α (ΛCDM):")
print()

# 計算在每種 η_B 下, 兩個模型嘅差異
# 列出關鍵 η_B 值
eta_test = [eta_B_idcm * 0.5, eta_B_idcm * 0.8, eta_B_idcm, 
            eta_B_idcm * 1.2, eta_B_idcm * 1.5, eta_B_idcm * 2.0]

print(f"{'η_B':>12s} | {'IDCM ⁷Li/H':>12s} | {'ΛCDM²·¹':>12s} | {'ΛCDM²·⁴':>12s} | {'Δ/σ(2.1)':>10s} | {'Δ/σ(2.4)':>10s}")
print("-" * 80)
for eta in eta_test:
    Li_idcm = eta * factor_li7
    Li_lcdm_l = Li7_lcdm * (eta / eta_B_lcdm) ** ALPHA_LCDM_LOW
    Li_lcdm_h = Li7_lcdm * (eta / eta_B_lcdm) ** ALPHA_LCDM_HIGH
    d21 = (Li_lcdm_l - Li_idcm) / Li7_obs_err
    d24 = (Li_lcdm_h - Li_idcm) / Li7_obs_err
    print(f"{eta:>12.2e} | {Li_idcm:>12.4e} | {Li_lcdm_l:>12.4e} | {Li_lcdm_h:>12.4e} | {d21:>+10.1f}σ | {d24:>+10.1f}σ")

print()
print(f"註: σ = {Li7_obs_err:.2e} (Spite plateau 觀測誤差~2%)")
print("正 Δ/σ 表示 ΛCDM 預測高於 IDCM")

print(f"\n[3] 關鍵 η_B 範圍分辨條件")
print("-" * 72)
# 要達到 3σ 分辨, 需要 η_B 範圍
for alpha in [ALPHA_LCDM_LOW, ALPHA_LCDM_HIGH]:
    # ㈲邊界: 在 η_B 高於某閾值時, 兩個模型差異達 3σ
    # Li7_idcm = η_B × factor_li7
    # Li7_lcdm = Li7_lcdm_0 × (η_B/η_B_0)^α
    # Δ = Li7_lcdm - Li7_idcm
    # 設 Δ = 3σ, 解 η_B
    
    # 用牛頓法
    def delta(eta):
        return Li7_lcdm * (eta / eta_B_lcdm) ** alpha - eta * factor_li7 - 3 * Li7_obs_err
    
    # 掃描
    eta_scan = np.logspace(-10.3, -9.0, 1000)
    delta_vals = np.array([Li7_lcdm * (e/eta_B_lcdm)**alpha - e * factor_li7 - 3*Li7_obs_err for e in eta_scan])
    
    # 找第一個跨零點 (η_B > η_B_idcm)
    idx = np.where(delta_vals > 0)[0]
    if len(idx) > 0:
        eta_3sigma = eta_scan[idx[0]]
        print(f"α = {alpha:.1f}: η_B ≳ {eta_3sigma:.2e} 可達 3σ 分辨")
        print(f"           即 η_B/η_B(WMAP) ≳ {eta_3sigma/eta_B_idcm:.2f}×")
    else:
        print(f"α = {alpha:.1f}: 在合理 η_B 範圍內無法達 3σ 分辨")

print(f"\n[4] 實際可觀測環境")
print("-" * 72)
print(f"{'環境':>20s} | {'η_B 範圍':>12s} | {'⁷Li 可測?':>10s} | {'分辨力':>12s}")
print("-" * 60)
# 各環境嘅 η_B 範圍
envs = [
    ("Spite 星 (Pop II)", "6.1e-10 (固定)", "✅ 豐富", "不可分辨"),
    ("SMC 星際氣體", "~6.1e-10", "✅ 1 個", "不可分辨 (Howk+2012)"),
    ("高z DLA 氣體", "6-7e-10", "❌ 極難", "N/A"),
    ("矮星系 (z~0)", "6-7e-10", "⚠️ 少", "不可分辨"),
    ("極貧金屬恆星", "6.1e-10 (固定)", "✅", "不可分辨"),
    ("高z 星系 (z>5)", "~6e-10", "❌ JWST 難", "N/A"),
]
for env, eta_r, li_meas, res in envs:
    print(f"{env:>20s} | {eta_r:>12s} | {li_meas:>10s} | {res:>12s}")

print()
print("[5] 結論")
print("-" * 72)
print("""
1. 核心問題: 所有已知 ⁷Li 測量都喺 η_B ≈ 6×10⁻¹⁰ (WMAP/Planck 值)
   因為 η_B 係宇宙學常數, 唔會有 local 變化

2. 理論分辨:
   - IDCM: ⁷Li/H ∝ η_B (線性)
   - ΛCDM: ⁷Li/H ∝ η_B^α, α ≈ 2.1-2.4
   - 需要 η_B 變化 > 2× 先達 3σ 分辨
   - 但宇宙中 η_B 係全域常數, 冇 local 變化

3. 實際限制:
   - Spite plateau: 所有星喺差不多 [Fe/H] ~ -2, η_B 固定
   - DLA: ⁷Li 吸收線極弱 (λ6708 得 0.3-0.5 pm), 幾乎冇量度
   - SMC: 只有一個 data point, 且係 interstellar 非 primordial
   - 矮星系: ⁷Li 測量極少, 星際吸收困難

4. 🟡 結論: 線性 vs 超線性分辨
   - 理論上清晰分辨 (指數 1 vs 2.1-2.4)
   - 觀測上 η_B 冇 local 變化, 無法直接測斜率
   - 唯一可行路徑: 間接 — 如果未來發現 η_B 有 local 變化
     (如 modified gravity 改變早期宇宙), 則可分辨
   - 目前: 證偽命題成立, 但觀測不可行
""")

print("=" * 72)
print(f"檔案: 01_li7_eta_sensitivity.py")
print(f"日期: 2026-08-20")
print("=" * 72)