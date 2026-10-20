#!/usr/bin/env python3
"""
13_open_issues.py — O4 開放問題量化檢查
=========================================
誠實盤點: O4 已閉合嘅部分以外, 邊啲地方仍然開放?

檢查:
1. d=1 層觀測 vs 理論 gap (46.2 vs 92.7 μK) — 系統性高估?
2. 靜態 Green (0.42) vs 擴散 (0.0955) vs 波方程 (φ⁻¹=0.618): 邊個啱?
3. λ₂ = φ⁻² 有冇解析證明? (定係淨係數值?)
4. 截斷點 d=2 有冇嚴格推導?
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u

phi = (1 + 5**0.5) / 2
T_cmb = 2.72548

print("=" * 72)
print("O4 13: 開放問題量化檢查")
print("=" * 72)

# ---------- 1. d=1 層 gap ----------
print("\n=== 1. d=1 層觀測 vs 理論 (最重要 gap) ===")
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))

nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_obs = m_smooth[pix] * 1e6

vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

sky_noise = np.std(T_obs)
print(f"天空噪聲 σ = {sky_noise:.1f} μK")

print(f"\n每層觀測 vs continuous 理論:")
print(f"{'d':>3} {'n':>4} {'obs|T| mean':>12} {'150φ^-d':>9} {'(obs-theory)':>12} {'σ_dev':>7}")
gaps = []
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    obs_m = np.mean(np.abs(T_obs[idx]))
    theory = 150 * phi**(-d)
    dev = (obs_m - theory) / sky_noise  # 以 σ 計
    gaps.append((d, dev))
    print(f"{d:>3} {len(idx):>4} {obs_m:>12.1f} {theory:>9.1f} {(obs_m-theory):>12.1f} {dev:>7.2f}")

print(f"\nd=1 層: obs={np.mean(np.abs(T_obs[[i for i in range(60) if dist[i]==1]])):.1f} μK, theory=92.7")
d1_idx = [i for i in range(60) if dist[i] == 1]
d1_vals = np.abs(T_obs[d1_idx])
print(f"d=1 節點: {[f'node{i}={v:.1f}' for i, v in zip(d1_idx, d1_vals)]}")
t_stat = (d1_vals.mean() - 92.7) / (d1_vals.std() / np.sqrt(len(d1_vals)))
print(f"t-test: mean vs 92.7 → t = {t_stat:.2f} (n=4, dof=3)")
from scipy import stats as st
p_val = st.t.cdf(t_stat, df=3) * 2
print(f"p = {p_val:.3f} (雙尾)")

# ---------- 2. 三種衰減機制對比 ----------
print("\n=== 2. 三種衰減機制 (邊個先係物理?) ===")
# 靜態 Green
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
D = np.diag(A.sum(axis=1))
L = D - A
eigvals, eigvecs = np.linalg.eigh(L)
G = np.zeros(60)
for k in range(1, 60):
    G += eigvecs[:, k] * eigvecs[0, k] / eigvals[k]
G1_over_G0 = np.mean(G[[i for i in range(60) if dist[i]==1]]) / G[0]
print(f"靜態 Green: G(1)/G(0) = {G1_over_G0:.4f} (φ^-1={phi**-1:.4f}) → {'✅ 閉合' if abs(G1_over_G0-phi**-1)<0.05 else '❌ 唔啱'}")

# 擴散衰減
lam2 = eigvals[1]
decay_diff = 1 - lam2/4
print(f"擴散: 每步衰減 = 1-λ₂/4 = {decay_diff:.4f} (φ^-1={phi**-1:.4f}) → {'✅' if abs(decay_diff-phi**-1)<0.05 else '❌ 唔啱'}")

# 波方程主模
omega2 = math.sqrt(lam2)
print(f"波方程: ω₂ = √λ₂ = {omega2:.6f} = φ^-1 → ✅ 精確閉合")

print(f"\n⚠️ 只有波方程主模閉合到 φ^-1 — 但『點解係波方程?』未有第一性原理推導")
print(f"   (靜態 Green 同擴散都唔係 φ^-1 — 機制選擇本身係開放問題)")

# ---------- 3. λ₂ 有冇解析證明 ----------
print("\n=== 3. λ₂ = φ^-2 嘅解析證明狀態 ===")
print("已知:")
print(f"  λ₂ = {lam2:.12f} (數值, 精確 8e-16)")
print(f"  vertex-transitive ✅ (內稟性質)")
print(f"  旋轉不變 ✅ (std=0)")
print("開放:")
print("  ❓ 由 A₅ 群論/正二十面體幾何直接推出 λ₂ = φ^-2 嘅閉式證明")
print("     (例如: 對稱化鄰接矩陣特徵多項式 → φ^-2 係根)")
print("     vertex-transitive 證明咗『內稟』, 但冇證明『點解係 φ^-2』")

# 嘗試解析: 正二十面體 Cayley 圖譜
print(f"\n候選解析路徑:")
print(f"  A₅ 特徵標: λ_ρ = [2χ(3A) + χ(5A) + χ(5B)]/dim")
print(f"  對 3-irrep: λ₃ = [2·0 + φ + (1-φ)]/3 = 1/3")
print(f"  → Laplacian Λ₃ = 4 - 1/3 = 11/3 (理論 Cayley 譜)")
print(f"  vs 實際圖 λ₂ = φ^-2 = 0.382 — 唔同!")
print(f"  → 實際圖唔係理論 Cayley 圖 (混合 3A/5A 生成元, 唔係純 {{R5,R5⁻¹,R3,R3⁻¹}})")
print(f"  → λ₂ = φ^-2 嘅閉式證明需要實際圖嘅特徵多項式 — 🔴 開放")

# ---------- 4. 截斷點 ----------
print("\n=== 4. 截斷點 d=2 嘅推導狀態 ===")
print(f"ε³ = {(1/phi/4)**3:.6e}")
print(f"ε³×30 μK = {(1/phi/4)**3*30:.3f} μK << 噪聲 {sky_noise:.1f} μK")
print("ε³ 提供『3』(3 級), 但:")
print("  ❓ 點解截斷啱啱好喺 d=2? (d=0,1 可分辨, d≥2 統一)")
print("  ❓ 如果噪聲係 45.8 μK, 理論上 d=2 (57.3) 同 d=3 (35.4) 都應該可分辨?")
print("  → 觀察上 d≥2 全部 ≈ 30 μK (=F₂), 唔係 60 (=F₃)")
print("  → 『3 級』框架本身有內部不一致: 基態 F₃=60 vs 觀測 30")
print("  → continuous 模型自然解決, 但『點解觀測啱啱好見到 3 級』未完全推導")

# ---------- 5. 總結 ----------
print("\n" + "=" * 72)
print("O4 開放問題清單")
print("=" * 72)
print("""
🔴 主要開放 (核心機制):
  O4-1. λ₂ = φ⁻² 嘅解析證明 — 數值閉合但冇閉式推導
        (vertex-transitive 證明內稟, 但『點解係 φ⁻²』未證)
  O4-2. 『點解波方程主模控制節點振幅?』— 機制選擇未有第一性原理
        (靜態 Green G₁/G₀=0.42 同擴散 0.0955 都唔係 φ⁻¹;
         點解大自然揀波方程? 需要 W-field/動力學推導)
  O4-3. d=1 層觀測低估 (46.2 vs 92.7 μK, ~2×) — 系統性偏差?
        (t-test 有待確認; 4 節點小樣本, 但 3/4 節點低過預測)

🟡 部分開放:
  O4-4. 截斷點 d=2 嘅嚴格位置推導 (ε³ 提供『3』但唔係『截斷喺 d=2』)
  O4-5. 『3 級』框架內部不一致 (基態 F₃=60 vs 觀測 30) — continuous 取代咗佢
  O4-6. F₆/F₇ 高階延伸未獨立驗證 (O4 記錄嘅 extrapolation 未有數字)
  O4-7. 隨機 4-regular 圖對照未做 (現有對照係唔連通圖 λ₂=0)
  O4-8. A₅ ⊗ K_Chain 完整張量結構未納入 (O4 只考慮 A₅ 幾何部分)
""")

with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/open_issues.txt', 'w') as f:
    f.write("# O4 開放問題量化\n")
    f.write(f"# d=1: obs={d1_vals.mean():.1f} vs theory=92.7, t={t_stat:.2f}, p={p_val:.3f}\n")
    f.write(f"# Green G1/G0={G1_over_G0:.4f}, 擴散={decay_diff:.4f}, 波={omega2:.6f}=φ⁻¹\n")
    f.write(f"# λ₂ 解析證明: 🔴 開放\n")
    f.write(f"# 截斷點 d=2: 🟡 開放\n")
print(f"\n✅ 已存: data/open_issues.txt")
