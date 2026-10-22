#!/usr/bin/env python3
"""
11_epsilon_closed_form.py — O26: 5.34° 對徑誤差閉式探索
===========================================================
問題: angle(v_{π(i)}, −v_i) = 5.340° 常數。閉式係咩?

數學重述: 對 180° 旋轉 R_a (軸 a), angle(R_a·v, −v) = 2·arcsin(|v·a|)
所以 ε = 2·arcsin(min_a |v₀·a|) over 15 個 2-fold 軸
→ min_a |v₀·a| = sin(2.670°) = 0.04658

探索:
1. 15 個軸同冷斑嘅全部 |dot|
2. min 值高精度
3. φ 候選: φ⁻⁵/2, 1/(2φ⁵), sin(2π/135), 1/√230...
4. Monte Carlo: random v 嘅 min |dot| 分佈 → 5.34° 係咪特殊?
5. 冷斑結構座標 (209 = 180+L₇, −57 = −(44+F₇)) 同軸網格關係
"""
import numpy as np
import math
from collections import Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
phi = (1+5**0.5)/2
inv_phi = 1/phi

def norm(v):
    v = np.asarray(v, dtype=float)
    return v/np.linalg.norm(v)
def rot_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float); axis = axis/np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

# A₅ 群 + 2-fold 軸
ico_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            ico_verts.append((0, sx, sy*phi)); ico_verts.append((sx, sy*phi, 0)); ico_verts.append((sx*phi, 0, sy))
ico_verts = np.array([norm(v) for v in ico_verts])
dod_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            dod_verts.append((sx, sy, sz))
for sx in [-1,1]:
    for sy in [-1,1]:
        dod_verts.append((0, sx*inv_phi, sy*phi)); dod_verts.append((sx*inv_phi, sy*phi, 0)); dod_verts.append((sx*phi, 0, sy*inv_phi))
dod_verts = np.array([norm(v) for v in dod_verts])

g1 = rot_matrix(ico_verts[0], 2*math.pi/5)
g2 = rot_matrix(dod_verts[0], 2*math.pi/3)
group = [np.eye(3)]
seen = {tuple(np.round(np.eye(3).flatten(), 10))}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = np.dot(gen, M)
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key); group.append(new); queue.append(new)

# 15 個 2-fold 軸
r180 = [M for M in group if abs((np.trace(M)-1)/2 + 1) < 1e-6]
def axis_of(M):
    evals, evecs = np.linalg.eigh(M)
    return evecs[:, np.argmax(evals)]
axes = [axis_of(M) for M in r180]
# 去 ± 重複 → 15 個方向
axes_uniq = []
for a in axes:
    if not any(np.allclose(a, b, atol=1e-6) or np.allclose(a, -b, atol=1e-6) for b in axes_uniq):
        axes_uniq.append(a)
print(f"2-fold 軸 (去 ±): {len(axes_uniq)}")

# 冷斑向量 (galactic 209, -57 → ICRS 48.2999, -20.4373)
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
v0 = vecs[0]

# ============ 1. 全部 |v0·a| ============
print("\n=== 1. 冷斑同 15 個 2-fold 軸嘅 |dot| ===")
dots = sorted([abs(np.dot(v0, a)) for a in axes_uniq])
for d in dots:
    ang = 2*math.degrees(math.asin(min(1, d)))
    print(f"  |v0·a| = {d:.8f}  → 對徑誤差 ε = {ang:.5f}°")
print(f"  min |v0·a| = {dots[0]:.10f}")
print(f"  ε_min = {2*math.degrees(math.asin(min(1,dots[0]))):.6f}°")

# ============ 2. 高精度 + φ 候選 ============
print("\n=== 2. φ 閉式候選 ===")
m = dots[0]
eps = 2*math.degrees(math.asin(m))
print(f"  min|v0·a| = {m:.10f}")
print(f"  ε = {eps:.6f}°")
cands = {
    "φ⁻⁵/2": phi**-5/2,
    "1/(2φ⁵)": 1/(2*phi**5),
    "1/√230": 1/math.sqrt(230),
    "1/√(2·115)": 1/math.sqrt(2*115),
    "sin(2π/135)": math.sin(2*math.pi/135),
    "φ⁻⁶": phi**-6,
    "1/21.46": 1/21.46,
    "(φ⁻⁴)/3": phi**-4/3,
    "1/(2·F₈·φ)": 1/(2*21*phi),
    "sin(π/67.4)": math.sin(math.pi/67.4),
}
for name, val in cands.items():
    print(f"  {name} = {val:.10f}  (diff = {abs(val-m):.2e}, {abs(val-m)/m*100:.2f}%)")

# 2.67° 候選
print(f"\n  ε/2 = {eps/2:.6f}°")
cands2 = {
    "360/135": 360/135,
    "360/(27·5)": 360/(27*5),
    "360/134.8": 360/134.8,
    "2·φ⁻⁵·57.3": 2*phi**-5*57.2958,
    "1/φ⁶ 度": 1/phi**6 * 57.2958,
}
for name, val in cands2.items():
    print(f"  {name} = {val:.6f}°  (diff = {abs(val-eps/2):.4f}°)")

# ============ 3. Monte Carlo: random v 嘅 min |dot| ============
print("\n=== 3. Monte Carlo: random v 嘅 min_a |v·a| ===")
rng = np.random.default_rng(11)
N = 10000
mins = np.empty(N)
for k in range(N):
    v = rng.normal(size=3); v = norm(v)
    ds = [abs(np.dot(v, a)) for a in axes_uniq]
    mins[k] = min(ds)
print(f"  random min|v·a|: mean={mins.mean():.4f} std={mins.std():.4f}")
print(f"  median={np.median(mins):.4f} min={mins.min():.4f}")
pct = (mins < m).mean()*100
print(f"  冷斑 min ({m:.4f}) 百分位: {pct:.2f}% ({'極端!' if pct < 5 else '普通'})")
# 冷斑嘅「對徑誤差」ε 對應嘅 random 分佈
eps_rand = 2*np.degrees(np.arcsin(mins))
print(f"  random ε: mean={eps_rand.mean():.2f}° median={np.median(eps_rand):.2f}°")
print(f"  冷斑 ε = {eps:.2f}° 百分位: {(eps_rand < eps).mean()*100:.2f}%")

# ============ 4. 全部 60 節點嘅 min |v_i·a| ============
print("\n=== 4. 全部 60 節點嘅 ε (應該全部一樣) ===")
eps_all = []
for v in vecs:
    ds = [abs(np.dot(v, a)) for a in axes_uniq]
    eps_all.append(2*math.degrees(math.asin(min(1, min(ds)))))
eps_all = np.array(eps_all)
print(f"  ε: mean={eps_all.mean():.6f}° std={eps_all.std():.6f} max={eps_all.max():.6f}")
print(f"  獨特值: {len(set(np.round(eps_all, 6)))}")

# ============ 5. 冷斑結構座標 ============
print("\n=== 5. 冷斑結構座標 vs ε ===")
# 冷斑 (l=209, b=-57): 209 = 180+L₇ (L₇=29), -57 = -(44+F₇) (F₇=13)
# 檢查: ε 同呢啲數有冇關係?
print(f"  209 = 180 + 29 (L₇=29)")
print(f"  -57 = -(44 + 13) (F₇=13)")
# 軸 a* 嘅方向 (min dot 嗰個)
i_star = np.argmin([abs(np.dot(v0, a)) for a in axes_uniq])
a_star = axes_uniq[i_star]
ra_a = math.degrees(math.atan2(a_star[1], a_star[0])) % 360
dec_a = math.degrees(math.asin(a_star[2]))
print(f"  最佳軸 a*: RA={ra_a:.3f}° Dec={dec_a:.3f}°")
print(f"  a* 同 v0 夾角 = 90°±2.67°: {math.degrees(math.acos(np.clip(np.dot(v0,a_star),-1,1))):.5f}°")
# 軸 a* 係咪都係結構方向?
from astropy.coordinates import SkyCoord
import astropy.units as u
sc_a = SkyCoord(ra=ra_a*u.deg, dec=dec_a*u.deg, frame='icrs')
gal_a = sc_a.galactic
print(f"  a* galactic: l={gal_a.l.deg:.3f}° b={gal_a.b.deg:.3f}°")
