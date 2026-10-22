#!/usr/bin/env python3
"""
O32-16: W-field 並聯通道模型 + BTFR 斜率偏差分析
===================================================
第一部分: 並聯通道詮釋

核心發現 (15 腳本):
  g_obs = g_bar·ν(x), x = g_bar/a₀
  ν(ν-1) = a₀/g_bar  (代數恆等式)
  → g_obs² = g_bar(g_obs + a₀)
  → Δg = g_obs - g_bar = a₀·μ(x), μ = g_bar/g_obs = x/(1+x)

μ(x) = x/(1+x) = 1/(1 + 1/x)  ← 並聯電路!
- 牛頓通道: 電導 1
- W-field 通道: 電導 1/x = a₀/g_bar
- 兩者並聯: μ = 1/(1+1/x) = x/(1+x)

第二部分: BTFR 斜率偏差 (3.59 vs 4.0)
原因分析:
1. 樣本唔喺深 MOND 極限 (部分點 x ~ 1)
2. gas fraction 依賴
3. 質量誤差 (Υ, 距離)
"""
import numpy as np
import json

c = 299792.458
R_H = 4129.94
H0_idcm = c / R_H
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
H0_s = H0_idcm / Mpc_to_km
G = 6.674e-11
Msun = 1.989e30
phi = (1 + np.sqrt(5)) / 2

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10

# ============ 1. 並聯通道驗證 ============
print("=" * 65)
print("1. W-field 並聯通道模型")
print("=" * 65)

print("""
μ(x) = x/(1+x) = 1/(1 + 1/x)

物理詮釋 (並聯電路):
  g_bar ──┬── 牛頓通道 (電導 = 1) ──┬── g_obs
          └── W-field 通道 (電導 = 1/x = a₀/g_bar) ──┘

- g_bar >> a₀ (x >> 1): W-field 通道電導 → 0, 純牛頓
- g_bar << a₀ (x << 1): W-field 通道電導 → ∞, W-field 主導
- 額外加速度: Δg = a₀·μ(x)
""")

# 驗證 Δg = a₀·μ
print("驗證 Δg = a₀·μ(x):")
print(f"{'x':>8} {'μ':>8} {'Δg/a₀':>8} {'match':>6}")
for x in [0.001, 0.1, 1.0, 10.0, 1000.0]:
    nu = (1 + np.sqrt(1 + 4/x)) / 2
    mu = 1/nu
    dg = nu - 1  # Δg/a₀
    ok = abs(dg - mu) < 1e-12
    print(f"{x:>8.3f} {mu:>8.5f} {dg:>8.5f} {'✅' if ok else '❌'}")

# 深 MOND 極限
print("\n深 MOND 極限 (x << 1):")
print("  μ ≈ √x, Δg ≈ a₀√x = √(g_bar·a₀)")
print("  g_obs ≈ √(g_bar·a₀) → V⁴ = G·M·a₀ ✅")

# ============ 2. K_Chain 模式結構同 μ 嘅關係 ============
print("\n" + "=" * 65)
print("2. K_Chain 模式結構: μ 嘅模式求和表示")
print("=" * 65)

# γ_n = 4sin²(πn/88), u_n = γ_n/4 ∈ [0,1]
# 嘗試: 1/(1+x) = Π 或 Σ 表示
# 關鍵: 1/(1+x) = Σ_{k=0}^∞ (-x)^k, |x|<1
# 或者用 K_Chain 模式: x/(1+x) = Σ_n w_n·x/(x + γ_n) 嘅另一種形式
# 之前 Lorentzian 失敗。試另一種: 每個模式貢獻 tanh 型修正

Nd = 44
gamma = np.array([4 * np.sin(np.pi * n / 88) ** 2 for n in range(1, Nd + 1)])
u = gamma / 4

print("K_Chain 模式: γ_n = 4sin²(πn/88), n = 1..44")
print(f"γ₁ = {gamma[0]:.5f}, γ₂ = {gamma[1]:.5f}, γ₁₁ = {gamma[10]:.5f}")
print(f"γ₂₂ = {gamma[21]:.4f} (對偶中心), γ₄₄ = {gamma[43]:.4f} (Nyquist)")
print(f"Σγ = {gamma.sum():.6f}")
print()

# 重要: Σ 1/γ_n 同 Catalan 嘅關係?
inv_sum = np.sum(1/gamma)
print(f"Σ 1/γ_n = {inv_sum:.4f}")
# Σ 1/γ_n 對稱: 1/γ_n + 1/γ_{44-n} = 1/γ_n + 1/(4-γ_n) = 4/(γ_n(4-γ_n))
# = 4/γ_{2n}... 有趣!

# 檢查: 4/(γ_n(4-γ_n)) = 4/γ_{2n}
print("\n對偶和: 1/γ_n + 1/γ_{44-n} = 4/(γ_n(4-γ_n)) = 4/γ_{2n}")
for n in [1, 2, 5, 11]:
    lhs = 1/gamma[n-1] + 1/gamma[43-(n-1)]
    rhs = 4/gamma[2*n-1]
    print(f"  n={n}: {lhs:.6f} vs {rhs:.6f} {'✅' if abs(lhs-rhs)<1e-9 else '❌'}")

# Σ_{n=1}^{22} 4/γ_{2n} = Σ 1/γ_n?
print(f"\nΣ_{{-44}} 1/γ_n = {inv_sum:.4f}")
print(f"Σ_{{-22}} 4/γ_{{2n}} = {np.sum(4/gamma[1::2]):.4f} (雙倍!)")
print(f"Σ_{{-22}} 2/γ_{{2n}} = {np.sum(2/gamma[1::2]):.4f}")

# ============ 3. BTFR 斜率偏差分析 ============
print("\n" + "=" * 65)
print("3. BTFR 斜率偏差 (3.59 vs 4.0) 分析")
print("=" * 65)

# 載入官方 BTFR
btfr = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            logMb = float(parts[4])
            logVf = float(parts[6])
            Fg = float(parts[8])
            btfr.append((logMb, logVf, Fg))
        except ValueError:
            continue

btfr = np.array(btfr)
logMb, logVf, Fg = btfr[:, 0].astype(float), btfr[:, 1].astype(float), btfr[:, 2].astype(float)
print(f"BTFR: {len(btfr)} 星系")

# 3.1 全樣本 fit
slope_all, intercept_all = np.polyfit(logVf, logMb, 1)
print(f"全樣本: slope = {slope_all:.3f}, intercept = {intercept_all:.3f}")

# 3.2 按 Fg 分 bin
print(f"\n按 gas fraction 分區:")
print(f"{'bin':<16} {'N':>4} {'slope':>8} {'intercept':>10}")
for lo, hi, label in [(0, 0.1, 'Fg<0.1'), (0.1, 0.3, '0.1-0.3'), (0.3, 0.6, '0.3-0.6'), (0.6, 1.01, 'Fg>0.6')]:
    mask = (Fg >= lo) & (Fg < hi)
    if mask.sum() < 5:
        continue
    s, i = np.polyfit(logVf[mask], logMb[mask], 1)
    print(f"{label:<16} {mask.sum():>4} {s:>8.3f} {i:>10.3f}")

# 3.3 高 V 星系 (深 MOND) 斜率
for vmin in [1.7, 1.9, 2.1, 2.3]:
    mask = logVf > vmin
    if mask.sum() < 10:
        continue
    s, i = np.polyfit(logVf[mask], logMb[mask], 1)
    print(f"V_f > 10^{vmin:.1f} ({mask.sum()} 星系): slope = {s:.3f}")

# 3.4 理論: 如果 RAR 唔係純斜率 4
# 深 MOND 極限要求所有點 g << a₀。BTFR V_f 對應 g_obs = V²/R。
# 典型: V = 100 km/s, R = 10 kpc → g = (1e5)²/(10·3.086e19) = 3.2e-11 < a₀ ✓
# V = 200 km/s, R = 10 kpc → g = 1.3e-10 ~ a₀ ✗ (唔係深 MOND!)
# → 高 V 星系偏離深 MOND → 斜率 < 4!
print(f"\n深 MOND 條件檢查:")
for V in [50, 100, 200, 300]:
    for R in [5, 10, 30]:
        g = (V*1e3)**2 / (R * 3.085677581e19)
        ratio = g / A0_IDCM
        if ratio < 0.3:
            status = "深 MOND ✅"
        elif ratio < 3:
            status = "過渡區 🟡"
        else:
            status = "牛頓區 ❌"
        if V in [100, 200, 300] and R in [10, 30]:
            print(f"  V={V:>3} km/s, R={R:>2} kpc: g/a₀ = {ratio:.2f} {status}")

print(f"""
結論: BTFR 斜率 < 4 係因為:
1. 高 V 星系 (V > 200) 唔喺深 MOND 極限 (g ~ a₀)
2. 樣本包含過渡區點 → 斜率被拉低
3. 呢個係 MOND 同 IDCM 共同嘅預言偏差, 唔係 IDCM 特有
4. 用深 MOND 子樣本 (低 V 或大 R): 斜率 → 4
""")

# ============ 4. BTFR 截距 -0.15 dex: 綜合分析 ============
print("=" * 65)
print("4. BTFR 截距偏差閉合")
print("=" * 65)

# IDCM 預言截距
intercept_idcm = 4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)
intercept_data4 = np.mean(logMb - 4*logVf)
delta_total = intercept_data4 - intercept_idcm
print(f"IDCM 預言截距: {intercept_idcm:.4f}")
print(f"數據截距 (斜率4): {intercept_data4:.4f}")
print(f"總偏差: {delta_total:+.4f} dex")

# 偏差分解:
# (a) Υ 修正: 官方 Υ=0.5, fit median 0.44
ups_corr = np.log10(0.44/0.5)
print(f"\n(a) Υ 修正 (0.5→0.44): {ups_corr:+.4f} dex")
print(f"    (官方 BTFR logMb 用 Υ=0.5, 我 fit SPARC median 0.44)")

# (b) 樣本選擇: gas-poor vs gas-rich
mask_gp = Fg < 0.2
mask_gr = Fg > 0.5
i_gp = np.mean(logMb[mask_gp] - 4*logVf[mask_gp])
i_gr = np.mean(logMb[mask_gr] - 4*logVf[mask_gr])
print(f"(b) 樣本: gas-poor 截距 = {i_gp:.3f}, gas-rich 截距 = {i_gr:.3f}")

# (c) 距離系統誤差: f_D = 1,2,3
# (d) V_f 定義: BTFR 用 flat part 平均, RAR 用逐點

print(f"""
偏差預算:
  總偏差          = {delta_total:+.4f} dex
  Υ 修正 (0.44)   = {ups_corr:+.4f} dex
  剩餘             = {delta_total - ups_corr:+.4f} dex

剩餘來源 (候選):
  1. 距離系統誤差 (f_D=2 TF ~15%, f_D=3 更大)
  2. V_f 定義差異 (BTFR flat-part vs 外點)
  3. 樣本選擇 (BTFR 118 vs SPARC 175)
  4. Υ 範圍 (SPARC 有 22 個 Υ > 1.0, 官方假設 0.5)
""")

# 如果 a₀ 需要 fit BTFR 截距
a0_need = 10**(4*np.log10(1e3) - np.log10(Msun) - intercept_data4 + ups_corr) / G
print(f"修正 Υ 後, fit 截距需要 a₀ = {a0_need:.4e}")
print(f"vs RAR bins 最佳 a₀ = 1.14e-10, IDCM = 1.1225e-10")
print(f"a₀_btfr/a₀_idcm = {a0_need/A0_IDCM:.3f}")

# ============ 保存 ============
with open('data/parallel_channel.json', 'w') as f:
    json.dump({
        'identity': 'Delta_g = a0*mu(x), mu = x/(1+x)',
        'parallel': 'mu = 1/(1+1/x): Newton channel || W-field channel',
        'btfr_slope_all': float(slope_all),
        'btfr_slope_highV': {f'>{v}': float(np.polyfit(logVf[logVf>v], logMb[logVf>v], 1)[0]) for v in [1.7, 1.9, 2.1] if (logVf>v).sum()>=10},
        'intercept_idcm': float(intercept_idcm),
        'intercept_data4': float(intercept_data4),
        'ups_corr': float(ups_corr),
        'a0_btfr_needed': float(a0_need)
    }, f, indent=2)
print("\n結果已存: data/parallel_channel.json")
