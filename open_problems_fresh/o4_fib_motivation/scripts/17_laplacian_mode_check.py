#!/usr/bin/env python3
"""
17_laplacian_mode_check.py — 真正嘅圖譜模態分析
==================================================
O4 16 發現: 層均衰減唔係 φ⁻¹ (偏差 -47%), 層內分散極大

問題: 如果唔係「每 hop φ⁻¹」嘅簡單衰減,
      真正嘅物理係咪 A₅ 圖譜嘅 Laplacian 特徵模態?

檢查:
1. 節點振幅向量 |T_i| 投影到各 Laplacian 特徵向量
   → 主模係咪 λ₂ = φ⁻² 對應嘅向量?
2. 定係 |T| 根本冇圖譜結構 (純噪聲)?
3. 同「F₅·φ^(-d) 層均」vs「特徵模態疊加」邊個解釋力高?
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

phi = (1 + 5**0.5) / 2
F5 = 5

print("=" * 72)
print("O4 17: 特徵模態投影分析 — |T| 有冇圖譜結構?")
print("=" * 72)

# ---------- 載入 ----------
nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
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

# Laplacian
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
D = np.diag(A.sum(axis=1))
L = D - A
eigvals, eigvecs = np.linalg.eigh(L)

# 溫度
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

for fwhm in [0.5, 4.17]:
    print(f"\n{'='*72}")
    print(f"=== FWHM = {fwhm}° ===")
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    
    # ---------- 1. 投影係數 ----------
    print("\n--- 1. |T| 對 Laplacian 特徵向量嘅投影 ---")
    # 投影係數 = <Tabs, v_k>
    proj = np.abs(eigvecs.T @ Tabs)
    # 歸一化
    norm = np.linalg.norm(Tabs)
    proj_n = proj / norm
    # 前 10 個
    print(f"{'k':>3} {'λ_k':>10} {'投影|coef|':>12} {'% 能量':>8}")
    for k in range(10):
        print(f"{k:>3} {eigvals[k]:>10.4f} {proj_n[k]:>12.4f} {proj_n[k]**2*100:>7.1f}%")
    
    # 累計能量 (前 k 模)
    cum = np.cumsum(proj_n**2)
    print(f"\n前 5 模累計能量: {cum[4]*100:.1f}%")
    print(f"前 10 模累計能量: {cum[9]*100:.1f}%")
    
    # 隨機向量嘅期望投影 = 1/√60 ≈ 0.129
    print(f"\n隨機期望投影: {1/math.sqrt(60):.4f}")
    print(f"λ₂ 模投影: {proj_n[1]:.4f} ({'顯著高' if proj_n[1] > 3/math.sqrt(60) else '唔顯著'})")
    
    # ---------- 2. 圖譜能量 vs 層均模型 ----------
    print("\n--- 2. 模型比較: 特徵模態 vs 層均 φ 衰減 ---")
    # 模型 A: 層均 φ 衰減 (F₅φ^(-d))
    model_phi = np.array([F5*phi**(-dist[i]) for i in range(60)])
    # 模型 B: λ₂ 特徵向量 (第 2 模)
    model_vec = np.abs(eigvecs[:, 1])
    model_vec = model_vec / np.mean(model_vec) * np.mean(Tabs)  # 縮放
    
    def r2(y, model):
        ss_res = np.sum((y - model)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        return 1 - ss_res/ss_tot
    
    r2_phi = r2(Tabs, model_phi)
    r2_vec = r2(Tabs, model_vec)
    r2_mean = r2(Tabs, np.full(60, np.mean(Tabs)))
    
    print(f"R² (層均 φ 衰減): {r2_phi:.4f}")
    print(f"R² (λ₂ 特徵向量): {r2_vec:.4f}")
    print(f"R² (常數 mean):   {r2_mean:.4f}")
    
    # ---------- 3. 每層內 vs 層間 variance ----------
    print("\n--- 3. 層內 vs 層間 variance (ANOVA) ---")
    groups = []
    for d in range(6):
        idx = [i for i in range(60) if dist[i] == d]
        if idx:
            groups.append(np.abs(T[idx]))
    f_stat, p_anova = st.f_oneway(*groups)
    print(f"ANOVA: F={f_stat:.2f}, p={p_anova:.3f}")
    print(f"→ {'層間有顯著差異 (衰減結構存在)' if p_anova < 0.05 else '層間冇顯著差異 (層均係假象!)'}")

    # ---------- 4. 單節點 |T| 同距離嘅相關 ----------
    print("\n--- 4. |T| vs BFS 距離 相關 ---")
    rho, p_sp = st.spearmanr([dist[i] for i in range(60)], Tabs)
    print(f"Spearman ρ = {rho:.4f}, p = {p_sp:.3f}")
    print(f"→ {'距離相關顯著' if p_sp < 0.05 else '距離相關唔顯著 — φ 衰減缺乏獨立支持!'}")

with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/laplacian_mode_check.txt', 'w') as f:
    f.write("# O4 17: 特徵模態投影分析\n")
    for fwhm in [0.5, 4.17]:
        f.write(f"# FWHM={fwhm}: 見 stdout\n")
print(f"\n✅ 已存: data/laplacian_mode_check.txt")
