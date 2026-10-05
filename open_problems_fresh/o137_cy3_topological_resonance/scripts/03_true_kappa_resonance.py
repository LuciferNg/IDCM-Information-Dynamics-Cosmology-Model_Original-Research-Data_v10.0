#!/usr/bin/env python3
"""
O137 — Phase 1: 真實 CY₃ κ 共振模型
========================================
用真實 36³ 相交張量 κ 計算 Kähler modulus 嘅 self-curve volume，
然後建構 m_f(n) = M₀·γ_n·exp(−V_n) 共振譜。

Kähler 參數: t_i = φ^(35−i) (O57 φ-power 選擇, 零參數)
Self-curve volume: V_n = Σ_i t_i·κ_{n,n,i} (divisor D_n 嘅 self-intersection curve)
"""
import math, json, sys
import numpy as np

phi = (1 + math.sqrt(5)) / 2
Nd = 44
M0 = 27.900915  # MeV

# K_Chain
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
omega = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd+1)])

# 載入真實 κ (36³)
data_dir = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o53_cy3_reality/data/polytopes"
d = json.load(open(f"{data_dir}/cy36_98_intersection_full.json"))
kappa = np.array(d['kappa'])  # 36×36×36
print(f"κ shape: {kappa.shape}, nnz: {np.count_nonzero(kappa)}")

LEPTONS = [1, 7, 20]
QUARKS = [14, 33, 34]

print("=" * 72)
print("O137 Phase 1: 真實 CY₃ κ 共振模型")
print("=" * 72)

# ============================================================
# 1. Kähler 參數 + Self-curve Volumes
# ============================================================
print("\n[1] Self-curve volumes V_n = Σ_i t_i·κ_{n,n,i}")

# φ-power Kähler 參數 (36 維, 0-based)
t = np.array([phi ** (35 - i) for i in range(36)])
print(f"  t[0] = φ^35 = {t[0]:.4e}, t[35] = φ^0 = {t[35]:.6f}")

# 正規化: 最大 curve volume ~ 1
# Self-curve volumes
V_self = np.array([sum(t[i] * kappa[n, n, i] for i in range(36)) for n in range(36)])

# Check which observations are valid — positive V produces suppressed mass
V_min = V_self.min()
V_max = V_self.max()
print(f"  V_self: min={V_min:.4f}, max={V_max:.4e}, mean={V_self.mean():.4f}")
print(f"  正數: {np.sum(V_self > 0)} / 36")

# 正規化: V_norm = V / V_max (so e^{-V_norm} is in [0, 1])
V_norm = V_self / V_self.max()
print(f"  V_norm: min={V_norm.min():.6f}, max=1.0")

# ============================================================
# 2. 共振質量譜
# ============================================================
print("\n[2] 共振質量譜 m_f(n) = M₀·γ_n·exp(−V_norm(n))")

# 對應 mode n ↔ divisor n-1 (n=1..36, 0-based divisor index)
# 對於 n>36: 冇對應 Kähler modulus, 用 P̂ 投影和近似
m_f = np.zeros(Nd)
for n in range(1, Nd+1):
    if n <= 36:
        V = V_norm[n-1]
        # 抑制因子
        suppression = math.exp(-V)
        m_f[n-1] = M0 * gamma[n-1] * suppression
    else:
        # n=37..44: 冇 Kähler modulus, 用 extrapolation
        # 外推: V_n 大約線性增長
        V_ext = V_norm[-1] + (V_norm[-1] - V_norm[-2]) * (n - 36)
        suppression = math.exp(-V_ext)
        m_f[n-1] = M0 * gamma[n-1] * suppression

# 打印
print(f"{'n':>3} | {'γ_n':>8} | {'V_n':>10} | {'e^{−V}':>10} | {'m_f(MeV)':>12} | {'log10(m)':>8}")
print("-" * 65)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    V_val = V_norm[n-1] if n <= 36 else (V_norm[-1] + (V_norm[-1]-V_norm[-2])*(n-36))
    supp = math.exp(-V_val)
    logm = math.log10(m_f[n-1]) if m_f[n-1] > 0 else -99
    print(f"{n:3d}{marker} | {gamma[n-1]:8.6f} | {V_val:10.6f} | {supp:10.6f} | {m_f[n-1]:12.6f} | {logm:8.4f}")

# ============================================================
# 3. 極值分析
# ============================================================
print("\n[3] 極值分析 (δS/dn = 0)")

dm = np.gradient(m_f)
d2m = np.gradient(dm)

extrema = []
for n in range(2, Nd):
    if dm[n-2] * dm[n-1] <= 0:
        etype = "max" if d2m[n-1] < 0 else "min"
        extrema.append((n, etype, m_f[n-1]))

print(f"  極值點:")
for n, etype, mf in extrema:
    marker = " ★" if n in LEPTONS else (" ☆" if n in QUARKS else "")
    print(f"    n={n:2d} {etype:>3}: m_f = {mf:12.4f} MeV{marker}")

print(f"\n  輕子命中:")
for n in LEPTONS:
    is_ext = any(e[0] == n for e in extrema)
    print(f"    n={n:2d} ★: m_f = {m_f[n-1]:10.4f} MeV  {'✅ 極值' if is_ext else '🔴 唔係極值'}")

# ============================================================
# 4. 對數譜分析 (階層結構)
# ============================================================
print("\n" + "=" * 72)
print("[4] 對數質量譜分析")
print("=" * 72)

logm = np.array([math.log10(m) if m > 0 else -99 for m in m_f])
print(f"  log10(m) 譜:")
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"    n={n:2d}{marker}: log10(m) = {logm[n-1]:8.4f}")

# 階層倍數
print(f"\n  階層比:")
for n1, n2 in [(1,7), (7,20), (1,20)]:
    if m_f[n1-1] > 0 and m_f[n2-1] > 0:
        r = m_f[n2-1]/m_f[n1-1]
        print(f"    m_{n2}/m_{n1} = {r:.4f} (log10 diff = {logm[n2-1]-logm[n1-1]:.4f})")

# ============================================================
# 5. 不同 Kähler 參數嘅影響
# ============================================================
print("\n" + "=" * 72)
print("[5] Kähler 參數掃描: t = φ^(α·(35−i))")
print("=" * 72)

print(f"{'α':>5} | 輕子極值命中 | 極值點")
print("-" * 50)
for alpha in [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]:
    t_a = np.array([phi ** (alpha * (35 - i)) for i in range(36)])
    V_a = np.array([sum(t_a[i] * kappa[n, n, i] for i in range(36)) for n in range(36)])
    V_a_norm = V_a / V_a.max()
    
    m_a = np.zeros(Nd)
    for n in range(1, min(37, Nd+1)):
        m_a[n-1] = M0 * gamma[n-1] * math.exp(-V_a_norm[n-1])
    for n in range(37, Nd+1):
        V_ext = V_a_norm[-1] + (V_a_norm[-1] - V_a_norm[-2]) * (n - 36)
        m_a[n-1] = M0 * gamma[n-1] * math.exp(-V_ext)
    
    dm_a = np.gradient(m_a)
    ext_a = [n for n in range(2, Nd) if dm_a[n-2]*dm_a[n-1] <= 0]
    hits = [n for n in LEPTONS if n in ext_a]
    print(f"{alpha:5.1f} | {str(hits):>20} | {ext_a}")

# ============================================================
# 6. 其他 curve volume 選擇: mean curve 或 max curve
# ============================================================
print("\n" + "=" * 72)
print("[6] 其他 curve volume 選擇")
print("=" * 72)

for model_name, V_func in [
    ("self-curve V_n = κ_nni·t_i", V_self),
    ("mean curve V_n = Σ_{ab} |κ_nab|·t_b / 36²", None),
]:
    if V_func is not None:
        V_use = V_func / V_func.max()
        m_use = np.zeros(Nd)
        for n in range(1, min(37, Nd+1)):
            m_use[n-1] = M0 * gamma[n-1] * math.exp(-V_use[n-1])
        for n in range(37, Nd+1):
            V_ext = V_use[-1] + (V_use[-1] - V_use[-2]) * (n - 36)
            m_use[n-1] = M0 * gamma[n-1] * math.exp(-V_ext)
        dm_u = np.gradient(m_use)
        ext_u = [n for n in range(2, Nd) if dm_u[n-2]*dm_u[n-1] <= 0]
        hits = [n for n in LEPTONS if n in ext_u]
        print(f"  {model_name}: 極值={ext_u}, 命中={hits}")

# 用 mean curve volume: V_n = Σ_{i,j} |κ_{n,i,j}|·t_j / (36²)
V_mean = np.array([sum(abs(kappa[n,i,j]) * t[j] for i in range(36) for j in range(36)) / (36*36) for n in range(36)])
V_mean_norm = V_mean / V_mean.max()
m_mean = np.zeros(Nd)
for n in range(1, min(37, Nd+1)):
    m_mean[n-1] = M0 * gamma[n-1] * math.exp(-V_mean_norm[n-1])
for n in range(37, Nd+1):
    V_ext = V_mean_norm[-1] + (V_mean_norm[-1] - V_mean_norm[-2]) * (n - 36)
    m_mean[n-1] = M0 * gamma[n-1] * math.exp(-V_ext)
dm_mean = np.gradient(m_mean)
ext_mean = [n for n in range(2, Nd) if dm_mean[n-2]*dm_mean[n-1] <= 0]
hits = [n for n in LEPTONS if n in ext_mean]
print(f"  mean curve volume: 極值={ext_mean}, 命中={hits}")

# ============================================================
# 7. 保存
# ============================================================
results = {
    "test": "O137 Phase 1: 真實 κ 共振模型",
    "V_self": V_self.tolist(),
    "V_norm": V_norm.tolist(),
    "m_f": m_f.tolist(),
    "extrema": [(n, t, float(mf)) for n, t, mf in extrema],
    "lepton_hits": [n for n in LEPTONS if any(e[0]==n for e in extrema)],
}
with open(f"{data_dir.replace('o53_cy3_reality/data/polytopes', 'o137_cy3_topological_resonance/data')}/01_resonance_spectrum.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n結果已保存 data/01_resonance_spectrum.json")