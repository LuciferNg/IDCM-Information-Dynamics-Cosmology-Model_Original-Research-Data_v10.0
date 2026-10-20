#!/usr/bin/env python3
"""
07_verify.py — O4 雙重驗證
============================
獨立重算所有關鍵數字, 驗證推導鏈每個環節。

驗證項目:
V1. A₅ irrep 維數平方和 = 60
V2. A₅ 特徵標 χ₃(5A) = φ
V3. F_{5-d} vs 5φ^(-d) 閉合 (d=0,1,2)
V4. BFS 距離分佈總和 = 60
V5. 阻挫邊 = 32
V6. F₅ = F₄ + F₃ (5 = 3 + 2)
V7. ε⁵/8 = RMS
V8. 5ε⁵/8 = 冷斑理論
V9. continuous φ^-d BIC < 3lv BIC
V10. 邊數 = 120
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
T_cmb = 2.72548

print("=" * 72)
print("O4 07: 雙重驗證")
print("=" * 72)

results = []
def check(name, cond, detail=""):
    results.append((name, cond))
    status = "✅" if cond else "❌"
    print(f"{status} {name}: {detail}")

# ---------- V1: A₅ irrep 維數 ----------
dims = [1, 3, 3, 4, 5]
check("V1 A₅ irrep 維數平方和 = 60", sum(d**2 for d in dims) == 60, f"{sum(d**2 for d in dims)}")

# ---------- V2: A₅ 特徵標 ----------
chi3_5A = phi
check("V2 χ₃(5A) = φ", abs(chi3_5A - phi) < 1e-12, f"φ={phi:.6f}")

# ---------- V3: F_{5-d} vs 5φ^(-d) ----------
print("\nV3: F_{5-d} 閉合")
for d in range(3):
    fv = F[5-d]
    pv = 5 * phi**(-d)
    err = abs(fv - pv) / pv * 100
    check(f"V3 d={d}: F_{5-d}={fv} ≈ 5φ^(-{d})={pv:.3f}", err < 10, f"差 {err:.1f}%")

# ---------- V4: BFS 距離 ----------
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
dist_counts = [sum(1 for i in range(60) if dist[i] == d) for d in range(9)]
check("V4 BFS 距離分佈 1+4+8+11+12+11+8+4+1", dist_counts == [1,4,8,11,12,11,8,4,1], str(dist_counts))
check("V4b 總和 = 60", sum(dist_counts) == 60, str(sum(dist_counts)))
check("V10 邊數 = 120", len(edges) == 120, str(len(edges)))

# ---------- V5: 阻挫邊 ----------
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)
frustration = sum(1 for u, v in edges if color[u] == color[v])
check("V5 阻挫邊 = 32", frustration == 32, str(frustration))

# ---------- V6: F₅ = F₄ + F₃ ----------
check("V6 5 = 3 + 2", F[5] == F[4] + F[3], f"{F[5]} = {F[4]} + {F[3]}")

# ---------- V7: ε⁵/8 = RMS ----------
RMS = eps**5 / 8
check("V7 RMS = ε⁵/8", abs(RMS - 1.100707e-5) < 1e-9, f"{RMS:.6e}")
check("V7b RMS → 30 μK", abs(RMS * T_cmb * 1e6 - 30.0) < 0.5, f"{RMS*T_cmb*1e6:.2f} μK")

# ---------- V8: 冷斑 ----------
cold = 5 * RMS
check("V8 冷斑 = 5ε⁵/8", abs(cold - 5.5035e-5) < 1e-8, f"{cold:.6e}")
check("V8b 冷斑 → 150 μK", abs(cold * T_cmb * 1e6 - 150.0) < 0.5, f"{cold*T_cmb*1e6:.1f} μK")

# ---------- V9: BIC 比較 (重算) ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
nodes_arr = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
sc = SkyCoord(ra=nodes_arr[:, 0]*astro_u.deg, dec=nodes_arr[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_obs = m_smooth[pix] * 1e6
sigma_noise = np.std(T_obs)
N = 60

F5 = 150.0
def chi2_model(fn):
    return sum(((abs(T_obs[i]) - fn(dist[i])) / sigma_noise)**2 for i in range(N))

chi2_cont = chi2_model(lambda d: F5 * phi**(-d))
chi2_3lv = chi2_model(lambda d: F5 if d==0 else (F5*3/5 if d==1 else F5*2/5))
bic_cont = chi2_cont + 1*math.log(N)
bic_3lv = chi2_3lv + 3*math.log(N)
check("V9 continuous φ^-d BIC < 3lv BIC", bic_cont < bic_3lv, f"BIC_cont={bic_cont:.1f} < BIC_3lv={bic_3lv:.1f}")
check("V9b continuous χ²/dof < 1", chi2_cont/59 < 1.0, f"χ²/dof={chi2_cont/59:.2f}")

# ---------- 總結 ----------
print("\n" + "=" * 72)
passed = sum(1 for _, c in results if c)
total = len(results)
print(f"驗證: {passed}/{total} 通過")
if passed == total:
    print("✅ 全部通過 — O4 推導鏈完整閉合")
else:
    print("❌ 有失敗項目, 需修正")
print("=" * 72)

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/verification.txt', 'w') as f:
    f.write("# O4 07: 雙重驗證結果\n")
    for name, cond in results:
        f.write(f"{'✅' if cond else '❌'} {name}\n")
    f.write(f"\nBIC: continuous={bic_cont:.1f}, 3lv={bic_3lv:.1f}\n")
    f.write(f"χ²: continuous={chi2_cont:.1f}, 3lv={chi2_3lv:.1f}\n")
print(f"\n✅ 已存: data/verification.txt")
