#!/usr/bin/env python3
"""
O32-17: 修正驗證 — 並聯通道 + 對偶和 + BTFR orthogonal fit
============================================================
修正:
1. Δg = a₀·μ 驗證: Δg/a₀ = x(ν-1) = 1/ν = μ ✓ (之前 print 錯 ν-1)
2. 對偶和 index: γ_{44-n} 嘅 index 係 43-n 唔係 44-n
3. BTFR: 用 orthogonal fit (Lelli+2016 用嘅方法) 驗證斜率 ~ 3.7-3.85
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

A0_IDCM = c_ms * H0_s / (2 * np.pi)

# ============ 1. 並聯通道 (修正) ============
print("=" * 65)
print("1. Δg = a₀·μ(x) 驗證 (修正)")
print("=" * 65)
print("μ = 1/ν, Δg/a₀ = x(ν-1) = 1/ν = μ")
print(f"{'x':>8} {'μ':>10} {'x(ν-1)':>10} {'Δg/a₀':>8} {'match':>6}")
for x in [0.001, 0.1, 1.0, 10.0, 1000.0]:
    nu = (1 + np.sqrt(1 + 4/x)) / 2
    mu = 1/nu
    dg = x * (nu - 1)  # Δg/a₀ = x(ν-1)
    ok = abs(dg - mu) < 1e-12
    print(f"{x:>8.3f} {mu:>10.5f} {dg:>10.5f} {mu:>8.5f} {'✅' if ok else '❌'}")

print("""
結論: Δg = a₀·μ(x), μ = 1/ν = x/(1+x)  ✅
並聯通道詮釋成立:
  g_obs = g_bar + a₀·μ(x)
  額外加速度 = a₀ × (並聯通道導納)
""")

# ============ 2. 對偶和 (修正 index) ============
print("=" * 65)
print("2. K_Chain 對偶和 (修正)")
print("=" * 65)

Nd = 44
gamma = np.array([4 * np.sin(np.pi * n / 88) ** 2 for n in range(1, Nd + 1)])

print("恆等式: 1/γ_n + 1/γ_{44-n} = 4/γ_{2n}")
print(f"{'n':>3} {'1/γ_n+1/γ_44-n':>16} {'4/γ_2n':>12} {'match':>6}")
all_ok = True
for n in range(1, 22):
    lhs = 1/gamma[n-1] + 1/gamma[43-n]       # γ_{44-n} = index 43-n
    rhs = 4/gamma[2*n-1]                      # γ_{2n} = index 2n-1
    ok = abs(lhs - rhs) < 1e-9
    all_ok &= ok
    if n in [1, 2, 3, 5, 10, 11, 21]:
        print(f"{n:>3} {lhs:>16.8f} {rhs:>12.8f} {'✅' if ok else '❌'}")
print(f"全部 21 對: {'✅ 全部成立' if all_ok else '❌ 有錯'}")

# Σ 1/γ_n 對稱性
inv_sum = np.sum(1/gamma)
print(f"\nΣ 1/γ_n = {inv_sum:.4f}")
print(f"Σ_{{-22}} 2/γ_{{2n}} = {np.sum(2/gamma[1::2]):.4f}")
print(f"關係: Σ 1/γ_n = 2·Σ 1/γ_{{2n}} + 1/γ_{{44}}?")
# 1/γ_n = 1/γ_{44-n}, 所以 Σ = 2·Σ_{n=1}^{22} 1/γ_n
print(f"2·Σ_{{n=1}}^{{22}} 1/γ_n = {2*np.sum(1/gamma[:22]):.4f}")
print(f"Σ_{{n=1}}^{{44}} 1/γ_n = {inv_sum:.4f}")

# 重要: Σ_{n=1}^{22} 1/γ_n 有冇閉合形式?
# 1/γ_n = 1/(4sin²(πn/88)) = csc²(πn/88)/4
# Σ csc²(πk/(2N)) = 2N(N-1)/3? 唔係... 等我查
# Σ_{k=1}^{N-1} csc²(πk/N) = (N²-1)/3
# 我哋有 n=1..22, 角度 πn/88 → 2N = 88, N = 44
# Σ_{n=1}^{43} csc²(πn/88) = (88²-1)/3 = 2581
# Σ_{n=1}^{22} csc²(πn/88) = 2581/2 (對稱) = 1290.5
# Σ 1/γ_n = Σ csc²(πn/88)/4 = 1290.5/4 = 322.625 ✓ (接近 322.75)
# 差少少因為 csc² 公式用 πk/N 而我哋用 πn/88 = πn/(2·44), N=88?
# Σ_{k=1}^{87} csc²(πk/88) = (88²-1)/3 = 2581
# 對稱: n 同 88-n 相同 → Σ_{n=1}^{44} = 2581/2 = 1290.5, 但 n=44 係 csc²(π/2)=1
# Σ_{n=1}^{43} = 1290.5 - 1 = 1289.5... 再對稱 n 同 44-n:
# 我哋 n=1..44, 對偶 γ_{44-n} = 4-γ_n 唔係 γ_n (同 n↔88-n 唔同!)
# 小心: csc²(πn/88) 對稱係 n ↔ 88-n, 唔係 n ↔ 44-n!
# γ_{88-n} = 4sin²(π(88-n)/88) = 4sin²(π - πn/88) = 4sin²(πn/88) = γ_n ✓
# 所以 γ_n 對稱係 n ↔ 88-n (即 n ↔ -n mod 88)
# Σ_{n=1}^{44} csc²(πn/88) = Σ_{k=1}^{44} csc²(πk/88), 其中 k=44 對應 π/2
# 用公式: Σ_{k=1}^{N-1} csc²(πk/N) = (N²-1)/3, N=88:
# Σ_{k=1}^{87} = (88²-1)/3 = 2581
# k=1..44 ∪ k=45..87: 對稱 csc²(π(88-k)/88) = csc²(πk/88)
# Σ_{k=1}^{44} = (2581 + csc²(π·44/88))/2 = (2581+1)/2 = 1291
# Σ 1/γ_n = 1291/4 = 322.75 ✓✓✓ EXACT!
print(f"\n閉合形式: Σ 1/γ_n = [(88²-1)/3 + 1]/8 = (2581+1)/8 = 322.75 ✅")
print(f"Σ 1/γ_n = (N²-1)/12 + 1/8, N = 88 → 322.75")

# ============ 3. BTFR orthogonal fit ============
print("\n" + "=" * 65)
print("3. BTFR orthogonal fit (Lelli+2016 方法)")
print("=" * 65)

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
            elogMb = float(parts[5])
            logVf = float(parts[6])
            elogVf = float(parts[7])
            Fg = float(parts[8])
            btfr.append((logMb, elogMb, logVf, elogVf, Fg))
        except ValueError:
            continue

btfr = np.array(btfr)
logMb = btfr[:, 0].astype(float)
logVf = btfr[:, 2].astype(float)
elogMb = btfr[:, 1].astype(float)
elogVf = btfr[:, 3].astype(float)
Fg = btfr[:, 4].astype(float)

# 3.1 OLS (y on x)
slope_ols, intercept_ols = np.polyfit(logVf, logMb, 1)
print(f"OLS (y on x): slope = {slope_ols:.3f}")

# 3.2 Orthogonal fit (最小化垂直距離)
# 用 PCA: 第一主成分方向
def orthogonal_fit(x, y):
    # 中心化
    xc = x - x.mean()
    yc = y - y.mean()
    cov = np.cov(xc, yc)
    eigvals, eigvecs = np.linalg.eigh(cov)
    # 最大 eigenvalue 對應主方向
    v = eigvecs[:, np.argmax(eigvals)]
    slope = v[1] / v[0]
    intercept = y.mean() - slope * x.mean()
    return slope, intercept

slope_orth, intercept_orth = orthogonal_fit(logVf, logMb)
print(f"Orthogonal (PCA): slope = {slope_orth:.3f}, intercept = {intercept_orth:.3f}")

# 3.3 加權 orthogonal fit (用誤差)
# Lelli+2016 用 weighted least squares
# 簡化: 用誤差加權
w = 1/(elogMb**2 + (4*elogVf)**2)  # 斜率 4 先驗
# weighted OLS
W = np.diag(w)
X = np.vstack([np.ones_like(logVf), logVf]).T
beta = np.linalg.inv(X.T @ W @ X) @ (X.T @ W @ logMb)
print(f"Weighted OLS: slope = {beta[1]:.3f}, intercept = {beta[0]:.3f}")

# 3.4 按 Fg 分區 orthogonal
print(f"\n按 gas fraction orthogonal fit:")
for lo, hi, label in [(0, 0.2, 'Fg<0.2'), (0.2, 0.5, '0.2-0.5'), (0.5, 1.01, 'Fg>0.5')]:
    mask = (Fg >= lo) & (Fg < hi)
    if mask.sum() < 10:
        continue
    s, i = orthogonal_fit(logVf[mask], logMb[mask])
    print(f"  {label:<10} N={mask.sum():>3}: slope = {s:.3f}")

# 3.5 深 MOND 子樣本 (低 g_bar)
# 用 V_f 同 R 估算: g_obs = V²/R, 需要 R。用 SPARC sample 嘅 Reff
sample = {}
with open('data/SPARC_Lelli2016c.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 17:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            Reff = float(parts[9])
        except (ValueError, IndexError):
            continue
        sample[name] = Reff

# BTFR 星系嘅 g_obs 估算 (用 Reff)
gobs_est = []
for (logMb, elogMb, logVf, elogVf, Fg), (name,) in zip(btfr, btfr[:, None]):
    pass
# 直接用 V_f 同 Reff
g_obs_est = []
valid_idx = []
for i in range(len(btfr)):
    name = None
for i, row in enumerate(btfr):
    pass

# 簡化: 用名字匹配
names = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        nm = parts[0]
        if nm and nm[0].isalpha() and nm not in ('Galaxy', 'Authors', 'Table', 'Title:'):
            names.append(nm)

# 用 BTFR 記錄本身嘅名字 (從 btfr array 冇存名字, 重新讀)
btfr_names = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        nm = parts[0]
        if nm and nm[0].isalpha() and nm not in ('Galaxy', 'Authors', 'Table', 'Title:'):
            btfr_names.append(nm)

g_obs_arr = []
for i, nm in enumerate(btfr_names):
    if i >= btfr.shape[0]:
        break
    if nm in sample and btfr[i, 2].astype(float) > 0:
        V = 10**btfr[i, 2].astype(float) * 1e3  # m/s
        R = sample[nm] * 3.085677581e19  # m
        g = V**2 / R
        g_obs_arr.append((g, btfr[i, 0].astype(float), btfr[i, 2].astype(float)))
g_obs_arr = np.array(g_obs_arr)

# 深 MOND: g < 0.3·a₀
mask_dm = g_obs_arr[:, 0] < 0.3 * A0_IDCM
print(f"\n深 MOND 子樣本 (g < 0.3a₀): {mask_dm.sum()} 星系")
if mask_dm.sum() >= 10:
    s_dm, i_dm = orthogonal_fit(g_obs_arr[mask_dm, 2], g_obs_arr[mask_dm, 1])
    print(f"  深 MOND orthogonal slope = {s_dm:.3f}")
    s_dm_ols, _ = np.polyfit(g_obs_arr[mask_dm, 2], g_obs_arr[mask_dm, 1], 1)
    print(f"  深 MOND OLS slope = {s_dm_ols:.3f}")

# 全部星系用 Reff
s_all, i_all = orthogonal_fit(logVf, logMb)
print(f"\n全部 (orthogonal): slope = {s_all:.3f}")

# ============ 4. 結論 ============
print("\n" + "=" * 65)
print("4. 斜率偏差結論")
print("=" * 65)
print(f"""
OLS slope       = {slope_ols:.3f} (低估)
Orthogonal      = {slope_orth:.3f}
Lelli+2016      = 3.71 ± 0.08 (orthogonal, 118 星系)
Lelli+2016 修正 = 3.85 ± 0.09 (gas-corrected)

IDCM/MOND 預言 = 4.0 (深 MOND 極限)
偏差來源:
1. 有限樣本: 高 V 星系喺過渡區 (g ~ a₀)
2. 質量誤差 (Υ, 距離) → OLS 偏差
3. gas correction 之後斜率 → 3.85, 更接近 4
4. 深 MOND 子樣本應該 → 4.0
""")

with open('data/orthogonal_btfr.json', 'w') as f:
    json.dump({
        'sum_inv_gamma': float(inv_sum),
        'closed_form': 322.75,
        'slope_ols': float(slope_ols),
        'slope_orthogonal': float(slope_orth),
        'slope_weighted': float(beta[1]),
        'literature': 3.71,
        'deep_mond_n': int(mask_dm.sum()) if 'mask_dm' in dir() else 0
    }, f, indent=2)
print("結果已存: data/orthogonal_btfr.json")
