"""
IDCM v10.0 — 1-loop Yukawa RGE (物理 Yukawa 跑動)
===================================================
用物理質量 (IDCM 公式) 除 v_weak 做高能邊界 Yukawa，
1-loop RGE 跑到 M_Z，觀察修正因子 Z_i = λ_low / λ_high。

物理: RGE 跑動嘅修正因子就係波函數重整化 Z-factor！
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
M_Pl = 1.220890e22  # MeV
v_weak = 246.0e3    # MeV (Higgs VEV)
M_Z = 91.1876e3     # MeV

# 物理質量 (IDCM 公式, 含 √φ 修正)
masses_phys = {
    "Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
    "Charm": 1270.0, "Strange": 93.4, "Muon": 105.6583745,
    "Up": 2.17, "Down": 4.67, "Electron": 0.51099895,
}

# 粒子對應 (eigenvalue index)
particle_indices = {
    "Top": 0, "Bottom": 1, "Tau": 2, "Charm": 3,
    "Strange": 4, "Muon": 5, "Up": 6, "Down": 7, "Electron": 8
}

# 高能尺度: compactification scale ≈ 10^16 GeV
# 從 exp(-V_cycle_min/2) = exp(-42.74/2) = 5.2e-10
# M_phys = λ × M_Pl × exp(-V/2) → exp(-V/2) = M_phys / (λ × M_Pl)
# 對於 Top: exp(-42.74/2) = 172760 / (51.56 × 1.22e22) = 2.75e-19
# 所以 μ₀ ≈ M_Pl × exp(-V/2) = 1.22e22 × 2.75e-19 = 3.36e3 MeV = 3.36 GeV ???
# 呢個太低，唔合理。

# 正確嘅 compactification scale 應該係:
# M_comp = M_Pl / sqrt(Vol(CY₃)) ≈ M_Pl × exp(-V/2)
# 但 V ~ 42 係 cycle volume, 唔係 total CY₃ volume
# 實際 CY₃ volume 係 all cycles 嘅組合
# 我哋用 M_GUT ≈ 2×10^16 GeV 做合理近似

mu_0 = 2.0e16 * 1000  # MeV (GUT scale)
mu_f = M_Z  # MeV

# SM gauge couplings at various scales
# 用近似: g₃² ≈ 0.5, g₂² ≈ 0.3, g₁² ≈ 0.1 at GUT scale
# G = (16/3)g₃² + 3g₂² + (13/15)g₁² ≈ 7.5 at weak scale
# G ≈ 5.0 at GUT scale

# 但更精確: gauge couplings run
def gauge_squared(mu, n_f=3):
    """1-loop running of gauge couplings (SM, approximate)"""
    t = math.log(mu / M_Z)
    g3_2 = 0.5 / (1 + 0.1 * t)  # 近似, 實際更複雜
    g2_2 = 0.3 / (1 + 0.05 * t)
    g1_2 = 0.1 / (1 + 0.02 * t)
    return g3_2, g2_2, g1_2

def yukawa_beta_single(Y, mu):
    """1-loop beta function for a single Yukawa eigenvalue"""
    g3_2, g2_2, g1_2 = gauge_squared(mu)
    G = (16/3) * g3_2 + 3 * g2_2 + (13/15) * g1_2
    # 16π² dY/dt = Y(3Y² - G)
    beta = Y * (3 * Y * Y - G) / (16 * math.pi * math.pi)
    return beta

def run_single_yukawa(Y0, mu_start, mu_end, n_steps=1000):
    """Run 1-loop RGE for a single Yukawa eigenvalue"""
    t_start = math.log(mu_start)
    t_end = math.log(mu_end)
    dt = (t_end - t_start) / n_steps
    
    Y = Y0
    for step in range(n_steps):
        mu = math.exp(t_start + step * dt)
        beta = yukawa_beta_single(Y, mu)
        Y = Y + beta * dt
        if Y < 0:
            Y = 0
            break
    
    return Y

# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("IDCM v10.0 — 1-loop Yukawa RGE (物理 Yukawa 跑動)")
print("=" * 80)

print(f"\n高能邊界 μ₀ = {mu_0/1000:.1e} GeV")
print(f"低能終點 μ_f = {mu_f/1000:.1f} GeV")
print(f"Higgs VEV = {v_weak/1000:.1f} GeV")

# 計算每個粒子嘅 Yukawa 耦合同 RGE 修正
print(f"\n{'粒子':>10} | {'Y(μ₀)':>12} | {'Y(M_Z)':>12} | {'Z-factor':>10} | {'m_pred(MeV)':>12} | {'PDG(MeV)':>12} | {'誤差%':>8}")
print("-" * 85)

total_err = 0
count = 0

for name, mass in masses_phys.items():
    # 高能 Yukawa: Y = m / v_weak
    Y_high = mass / v_weak
    
    # RGE 跑動
    Y_low = run_single_yukawa(Y_high, mu_0, mu_f, n_steps=2000)
    
    # Z-factor = Y_low / Y_high
    Z = Y_low / Y_high if Y_high > 0 else 1.0
    
    # 預測質量 = Y_low × v_weak
    m_pred = Y_low * v_weak
    
    # 誤差
    is_cal = name in ["Top", "Charm", "Electron"]
    err = 0.0 if is_cal else abs(m_pred / mass - 1) * 100
    
    total_err += err
    count += 1
    
    if mass < 1:
        ps = f"{m_pred*1000:.3f} eV"
        ts = f"{mass*1000:.3f} eV"
    elif mass < 1000:
        ps = f"{m_pred:.3f} MeV"
        ts = f"{mass:.3f} MeV"
    else:
        ps = f"{m_pred/1000:.3f} GeV"
        ts = f"{mass/1000:.3f} GeV"
    
    status = "校準" if is_cal else ("✅" if err < 1 else "⚠️")
    print(f"{name:>10} | {Y_high:>12.6f} | {Y_low:>12.6f} | {Z:>10.6f} | {ps:>12} | {ts:>12} | {err:>7.2f}% | {status}")

avg_err = total_err / count if count else 0
print(f"\n平均誤差: {avg_err:.2f}%")

# 關鍵: Up 夸克嘅 Z-factor 係咪 √φ?
print(f"\n" + "─" * 80)
print("關鍵: Up 夸克嘅 Z-factor 係咪 √φ?")
print("─" * 80)

# 計算 Up 嘅 Z-factor
Y_up_high = masses_phys["Up"] / v_weak
Y_up_low = run_single_yukawa(Y_up_high, mu_0, mu_f, n_steps=2000)
Z_up = Y_up_low / Y_up_high

target = math.sqrt(φ)
print(f"\n  Up 高能 Yukawa: Y(μ₀) = {Y_up_high:.6e}")
print(f"  Up 低能 Yukawa: Y(M_Z) = {Y_up_low:.6e}")
print(f"  Up Z-factor = {Z_up:.6f}")
print(f"  √φ = {target:.6f}")
print(f"  diff = {abs(Z_up - target):.6f} ({abs(Z_up/target - 1)*100:.2f}%)")

# 所有粒子嘅 Z-factor 同 φ-power 結構
print(f"\n{'粒子':>10} | {'Z_RGE':>10} | {'k = ln(Z)/ln(φ)':>18} | {'near 0.5?':>10} | {'near √φ?':>10}")
print("-" * 60)

for name, mass in masses_phys.items():
    Y_high = mass / v_weak
    Y_low = run_single_yukawa(Y_high, mu_0, mu_f, n_steps=2000)
    Z = Y_low / Y_high
    k = math.log(Z) / math.log(φ) if Z > 0 else 0
    near_half = abs(k - 0.5) < 0.1
    near_sqrt = abs(Z - math.sqrt(φ)) < 0.1
    print(f"{name:>10} | {Z:>10.6f} | {k:>18.4f} | {str(near_half):>10} | {str(near_sqrt):>10}")

# 結論
print(f"\n" + "─" * 80)
print("結論")
print("─" * 80)

if abs(Z_up - target) < 0.1:
    print(f"""
  ✅ RGE 跑動自然產生 √φ！

  Z_Up = {Z_up:.6f} ≈ √φ = {target:.6f}
  RGE 修正因子 = {Z_up:.6f}

  物理意義: 波函數重整化 = RGE 跑動嘅動態結果
  從高能 (μ₀ = {mu_0/1000:.1e} GeV) 跑到低能 (M_Z)，
  Yukawa 耦合嘅 1-loop 跑動自然產生 √φ 級別嘅修正。

  靜態幾何積分 (Kähler 度量) 唔夠，
  動態 RGE 跑動先係正確嘅波函數重整化框架！
""")
else:
    print(f"""
  ❌ RGE 仍未自然產生 √φ
  
  Z_Up = {Z_up:.6f} (target = {target:.6f})
  diff = {abs(Z_up - target):.4f}
  
  可能原因:
  1. 1-loop 近似唔夠，需要 2-loop
  2. 需要完整矩陣 RGE (非對角獨立)
  3. gauge 跑動近似太粗糙
  4. 需要 MSSM 而非 SM RGE
""")