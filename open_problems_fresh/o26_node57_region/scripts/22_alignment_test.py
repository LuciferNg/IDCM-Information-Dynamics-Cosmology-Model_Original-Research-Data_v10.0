#!/usr/bin/env python3
"""
22_alignment_test.py — O26-G2: 數據對齊測試
================================================
測試: A₅ 節點溫度結構係咪同對徑軸 (328.28°, +18°) 對齊?

方法:
1. 60 節點溫度 → 球諧分解 (dipole/quadrupole 方向)
2. 對徑軸投影測試: 溫度 vs cos(θ_axis)
3. 軸對稱測試: 圍繞對徑軸旋轉嘅溫度對稱性
4. 對徑對測試: 對徑對 |ΔT| vs 軸夾角
5. Monte Carlo null: 隨機軸嘅對齊統計
"""
import numpy as np
import math
import os
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = f"{BASE}/o26_node57_region/data"

# 讀節點
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 讀溫度 (SMICA 4.17)
T = {}
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T[int(p[0])] = float(p[2])
T_arr = np.array([T[i] for i in range(60)])

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    results.append(line)

log("=" * 72)
log("O26-G2: 數據對齊測試 (A₅ 節點溫度 vs 對徑軸)")
log("=" * 72)

# 對徑軸 (328.2825°, +18.0°)
AXIS_RA, AXIS_DEC = 328.2825, 18.0
axis = np.array([math.cos(math.radians(AXIS_DEC))*math.cos(math.radians(AXIS_RA)),
                 math.cos(math.radians(AXIS_DEC))*math.sin(math.radians(AXIS_RA)),
                 math.sin(math.radians(AXIS_DEC))])
log(f"對徑軸: RA={AXIS_RA}°, Dec={AXIS_DEC}°")

# ============ 1. Dipole 擬合 ============
log("\n=== 1. 60 節點溫度 Dipole 擬合 ===")
# 用最小二乘: T = a + d·n̂ (4 個未知: a, d_x, d_y, d_z)
A = np.column_stack([np.ones(60), vecs])
coef, res, rank, sv = np.linalg.lstsq(A, T_arr, rcond=None)
T_fit = A @ coef
dip = coef[1:]
dip_amp = np.linalg.norm(dip)
dip_dir = dip / dip_amp
dip_ra = math.degrees(math.atan2(dip_dir[1], dip_dir[0])) % 360
dip_dec = math.degrees(math.asin(dip_dir[2]))
log(f"  Dipole 振幅: {dip_amp:.2f} μK")
log(f"  Dipole 方向: RA={dip_ra:.1f}°, Dec={dip_dec:.1f}°")
log(f"  對徑軸:      RA={AXIS_RA:.1f}°, Dec={AXIS_DEC:.1f}°")
# 夾角
ang = math.degrees(math.acos(np.clip(np.dot(dip_dir, axis), -1, 1)))
log(f"  Dipole vs 對徑軸夾角: {ang:.1f}°")
log(f"  (0° = 完全對齊, 90° = 垂直)")
# 殘差
resid = T_arr - T_fit
log(f"  殘差 RMS: {np.std(resid):.2f} μK (原始 std {np.std(T_arr):.2f})")
log(f"  Dipole 解釋方差: {1 - np.var(resid)/np.var(T_arr):.1%}")

# ============ 2. 對徑軸投影相關 ============
log("\n=== 2. 對徑軸投影相關 ===")
# T vs cos(θ_axis) — 如果溫度沿軸有梯度, 應該相關
proj = vecs @ axis
r_proj = np.corrcoef(proj, T_arr)[0, 1]
log(f"  corr(T, cos θ_axis) = {r_proj:+.3f}")
# 用 perm 測試
rng = np.random.default_rng(42)
n_perm = 10000
cnt = 0
for _ in range(n_perm):
    rp = np.corrcoef(proj, rng.permutation(T_arr))[0, 1]
    if abs(rp) >= abs(r_proj):
        cnt += 1
p_proj = cnt / n_perm
log(f"  Permutation p (雙尾) = {p_proj:.4f}")
log(f"  {'✅ 顯著' if p_proj < 0.05 else '❌ 唔顯著 (無對齊證據)'}")

# ============ 3. 軸對稱測試 ============
log("\n=== 3. 軸對稱測試 (圍繞對徑軸旋轉) ===")
# 將節點投影到軸: n̂ = (proj)·axis + perpendicular
# 旋轉 180° 圍繞軸 → 節點 i 嘅對稱夥伴
def rotate_around(v, axis, theta):
    """Rodrigues 旋轉"""
    v = v / np.linalg.norm(v)
    a = axis / np.linalg.norm(axis)
    return v*math.cos(theta) + np.cross(a, v)*math.sin(theta) + a*np.dot(a, v)*(1-math.cos(theta))

sym_ts = []
for i in range(60):
    v_rot = rotate_around(vecs[i], axis, math.pi)
    # 搵最近節點
    dists = np.arccos(np.clip(vecs @ v_rot, -1, 1))
    j = np.argmin(dists)
    if dists[j] < math.radians(10):  # 10° 內
        sym_ts.append((T_arr[i], T_arr[j], dists[j]))
log(f"  搵到 {len(sym_ts)} 對軸對稱節點 (10° 內)")
if sym_ts:
    ts = np.array([s[0] for s in sym_ts])
    ts2 = np.array([s[1] for s in sym_ts])
    r_sym = np.corrcoef(ts, ts2)[0, 1]
    log(f"  軸對稱相關: r = {r_sym:+.3f} (n={len(sym_ts)})")
    log(f"  平均 |ΔT| = {np.mean(np.abs(ts-ts2)):.1f} μK")

# ============ 4. 對徑對 vs 軸 ============
log("\n=== 4. 對徑對 |ΔT| vs 軸夾角 ===")
# 30 對徑對
def antip(x):
    best = None; ba = 1e9
    for y in range(60):
        if y == x: continue
        dd = math.degrees(math.acos(np.clip(np.dot(vecs[x], vecs[y]), -1, 1)))
        if dd > 170 and dd < ba:
            ba = dd; best = y
    return best
pairs = []
used = set()
for i in range(60):
    if i in used: continue
    j = antip(i)
    pairs.append((i, j))
    used.add(i); used.add(j)
# 每對嘅中點方向 (對徑對連線方向)
pair_dirs = []
pair_dT = []
for i, j in pairs:
    mid = (vecs[i] + vecs[j]) / 2
    mid = mid / np.linalg.norm(mid)
    pair_dirs.append(mid)
    pair_dT.append(abs(T_arr[i] - T_arr[j]))
pair_dirs = np.array(pair_dirs)
pair_dT = np.array(pair_dT)
# 對徑對連線方向 vs 軸夾角
angs = np.array([math.degrees(math.acos(np.clip(np.dot(d, axis), -1, 1))) for d in pair_dirs])
log(f"  對徑對連線 vs 軸夾角: min={angs.min():.1f}°, max={angs.max():.1f}°")
r_pd = np.corrcoef(angs, pair_dT)[0, 1]
log(f"  corr(|ΔT|, 軸夾角) = {r_pd:+.3f} (n={len(pairs)})")
# 細分: 近軸 (<45°) vs 遠軸 (>45°)
near = pair_dT[angs < 45]
far = pair_dT[angs >= 45]
if len(near) > 0 and len(far) > 0:
    log(f"  近軸 (<45°): mean|ΔT| = {np.mean(near):.1f} μK (n={len(near)})")
    log(f"  遠軸 (≥45°): mean|ΔT| = {np.mean(far):.1f} μK (n={len(far)})")
    # permutation
    obs = np.mean(near) - np.mean(far)
    cnt2 = 0
    for _ in range(10000):
        perm = rng.permutation(pair_dT)
        cnt2 += (np.mean(perm[:len(near)]) - np.mean(perm[len(near):])) >= obs
    log(f"  Permutation p (單尾, near<far) = {cnt2/10000:.4f}")

# ============ 5. 隨機軸 null ============
log("\n=== 5. Monte Carlo: 隨機軸對齊統計 ===")
# 隨機 10000 軸, 計 dipole 擬合 + 投影相關分佈
n_mc = 2000
mc_angles = []
mc_projs = []
rng2 = np.random.default_rng(7)
for _ in range(n_mc):
    # 隨機軸
    z = rng2.uniform(-1, 1)
    phi = rng2.uniform(0, 2*math.pi)
    ax = np.array([math.sqrt(1-z*z)*math.cos(phi), math.sqrt(1-z*z)*math.sin(phi), z])
    # dipole 擬合方向
    A = np.column_stack([np.ones(60), vecs])
    coef2, _, _, _ = np.linalg.lstsq(A, T_arr, rcond=None)
    dip2 = coef2[1:]
    if np.linalg.norm(dip2) < 1e-10: continue
    dip2 = dip2 / np.linalg.norm(dip2)
    ang2 = math.degrees(math.acos(np.clip(np.dot(dip2, ax), -1, 1)))
    mc_angles.append(ang2)
    # 投影相關
    proj2 = vecs @ ax
    mc_projs.append(abs(np.corrcoef(proj2, T_arr)[0, 1]))
mc_angles = np.array(mc_angles)
mc_projs = np.array(mc_projs)
# 對徑軸嘅投影相關
r_proj_abs = abs(r_proj)
pct_angle = np.mean(mc_angles <= ang) * 100
pct_proj = np.mean(mc_projs >= r_proj_abs) * 100
log(f"  隨機軸 dipole 夾角分佈: 中位 {np.median(mc_angles):.1f}°")
log(f"  對徑軸 dipole 夾角 {ang:.1f}° = {pct_angle:.1f} 百分位")
log(f"  隨機軸 |投影相關| 分佈: 中位 {np.median(mc_projs):.3f}")
log(f"  對徑軸 |r|={r_proj_abs:.3f} = {pct_proj:.1f} 百分位")
log(f"  ({pct_proj}% 隨機軸超過 — {'有對齊' if pct_proj < 5 else '無對齊'})")

# ============ 6. 多極分解 ============
log("\n=== 6. 節點溫度多極結構 (ℓ≤3) ===")
def ylm_vec(l, m, v):
    """實球諧基函數 (v = (60,3) 陣列)"""
    x = v[:, 0]; y = v[:, 1]; z = v[:, 2]
    if l == 0: return np.ones(len(v))
    if l == 1:
        if m == -1: return y
        if m == 0: return z
        if m == 1: return x
    if l == 2:
        if m == -2: return x*y
        if m == -1: return y*z
        if m == 0: return 3*z*z - 1
        if m == 1: return x*z
        if m == 2: return x*x - y*y
    if l == 3:
        if m == -3: return y*(3*x*x - y*y)
        if m == -2: return x*y*z
        if m == -1: return y*(5*z*z - 1)
        if m == 0: return 5*z**3 - 3*z
        if m == 1: return x*(5*z*z - 1)
        if m == 2: return z*(x*x - y*y)
        if m == 3: return x*(x*x - 3*y*y)
    return np.zeros(len(v))

basis = []
labels = []
for l in range(4):
    for m in range(-l, l+1):
        basis.append(ylm_vec(l, m, vecs))
        labels.append(f"ℓ={l},m={m}")
B = np.column_stack(basis)
coef_lm, _, _, _ = np.linalg.lstsq(B, T_arr, rcond=None)
# 每 ℓ 嘅功率
for l in range(4):
    idx = [i for i, lab in enumerate(labels) if lab.startswith(f"ℓ={l},")]
    power = np.sum(coef_lm[idx]**2)
    log(f"  ℓ={l}: power = {power:.1f} μK²")

with open(f"{OUT}/node57_alignment.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_alignment.txt")
