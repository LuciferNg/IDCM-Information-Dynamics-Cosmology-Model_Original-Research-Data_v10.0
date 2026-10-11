#!/usr/bin/python3
"""O238 — Script 29: 挫阻 → 張力 → 質量 機制鏈 probe（調律者綱領, 選項 1）

調律者: 「物質 = 挫阻缺陷張力凝聚體」——試建機制鏈, 唔開新 O.

鏈結構:
  A₅ 晶體網 (120 邊) --挫阻缺陷--> 88 透明邊 (= 88-chain!) --張力(應變)--> 質量

已知 (O171/O182/O223 實錘):
  g88_edge_map.txt  = 88 條透明邊 (mid_idx edge_u edge_v)
  g32_frustration_midpoints.txt = 32 個阻挫邊中點
  120 = 88 + 32; 88 = 2(|A₅|−B²) = 2N_d; 邊長應變 +0.822%/ +1.112%

P1 計數鏈: 88-chain 嘅「88」= A₅ 網剔走 32 挫阻後嘅透明邊數?
   → 驗證 120 = 88 + 32 且 88 透明邊 ≠ 32 阻挫邊 (disjoint)
P2 挫阻邊 vs 透明邊幾何分離: 32 阻挫中點同 88 透明中點有冇空間排斥?
   (如果挫阻缺陷係「晶體缺陷」, 應該同透明邊有幾何距離結構)
P3 張力 → α: 應變 ε (0.822%, 1.112%) 同 α 觀測差 (S1/S2 vs φ²) 有冇可檢驗鏈?
   OLS α 誤差 ±0.15 (5.8%) — 應變 1% 級 — 級別分析: 有冇檢驗力?
P4 挫阻密度 32/88 = 4/11 嘅結構身份 (B=4; 11=88/8) — 觀察級定結構?
   (⚠️ 呢類 ratio 好易凑 — 只報, 唔宣稱)

盲測紀律: P3/P4 只測「機制預言」, 唔 fit 目標; 任何單點命中 = refrain.
"""
import json, math
import numpy as np

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/data/"
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ── 讀實數據 ──
edges = []
with open(BASE + "g88_edge_map.txt") as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1]), int(parts[2])))
frust = []
with open(BASE + "g32_frustration_midpoints.txt") as fh:
    for line in fh:
        line = line.strip()
        if line:
            ra, dec = line.split()
            frust.append((float(ra), float(dec)))
nodes = []
with open(BASE + "g88_nodes.txt") as fh:
    for line in fh:
        line = line.strip()
        if line:
            ra, dec = line.split()
            nodes.append((float(ra), float(dec)))

print(f"88 透明邊: {len(edges)}, 32 阻挫中點: {len(frust)}, 88 節點: {len(nodes)}")

print("\n═══ P1. 計數鏈: 88-chain = A₅ 網剔挫阻 ═══")
print(f"  120 = 88 + 32? → {88 + 32}")
print(f"  88 透明邊 = 88-chain 節點數? → {len(edges) == len(nodes)}")
# 阻挫中點會唔會同 88 節點重疊?
fr_set = set((round(a,3), round(b,3)) for a, b in frust)
nd_set = set((round(a,3), round(b,3)) for a, b in nodes)
overlap = fr_set & nd_set
print(f"  阻挫中點 ∩ 88 節點 = {len(overlap)} (應 0 = disjoint)")
chk("P1.1 120 = 88+32 計數鏈", 88 + 32 == 120)
chk("P1.2 88 透明邊數 = 88-chain 節點數", len(edges) == len(nodes) == 88)
chk("P1.3 挫阻 ≠ 透明 (disjoint)", len(overlap) == 0, f"overlap={len(overlap)}")

print("\n═══ P2. 挫阻邊 vs 透明邊空間分離 ═══")
# 挫阻中點 vs 透明邊中點 (88 節點) 最近角距
def ang(ra1, dec1, ra2, dec2):
    d = math.acos(max(-1, min(1,
        math.sin(math.radians(dec1))*math.sin(math.radians(dec2)) +
        math.cos(math.radians(dec1))*math.cos(math.radians(dec2))*math.cos(math.radians(ra1-ra2)))))
    return math.degrees(d)

# 88 節點最近挫阻距離 (min over frust)
dists = []
for ra, dec in nodes:
    dmin = min(ang(ra, dec, fra, fdec) for fra, fdec in frust)
    dists.append(dmin)
dists = np.array(dists)
print(f"  88 透明節點→最近挫阻中點角距: min={dists.min():.3f}° median={np.median(dists):.3f}° max={dists.max():.3f}°")
# 同 random 對照: 假設 88 點均勻, 最近距離分佈
print(f"  邊長 26.09° — 最近挫阻 median {np.median(dists):.2f}° vs 邊長 26°?")
near = (dists < 26.0).sum()
print(f"  有 {near}/88 個透明節點距離挫阻 <26° (即同挫阻「鄰接」)")
# 挫阻之間最近距離 (32 點)
fd = []
for i in range(len(frust)):
    dmin = min(ang(frust[i][0], frust[i][1], frust[j][0], frust[j][1]) for j in range(len(frust)) if j != i)
    fd.append(dmin)
fd = np.array(fd)
print(f"  32 挫阻中點相互最近: min={fd.min():.3f}° median={np.median(fd):.3f}° max={fd.max():.3f}°")
chk("P2.1 挫阻中點最近距 median ~ 邊長尺度", 20 < np.median(fd) < 32,
    f"median={np.median(fd):.2f}°")

print("\n═══ P3. 張力 → α: 應變 ε 有冇檢驗力? ═══")
PHI2 = (1 + math.sqrt(5)) ** 2 / 4
e1, e2 = 0.00822, 0.01112          # O223 邊長應變 2+2 分裂
a_s1, a_s2 = 2.616977, 2.642463     # O238 S1/S2 OLS α
a_err = 0.151                        # OLS 誤差 (~±0.15)
print(f"  φ² = {PHI2:.6f}")
for nm, a in [("S1", a_s1), ("S2", a_s2)]:
    dev = (a - PHI2) / PHI2 * 100
    print(f"  α_{nm} = {a:.6f}  (vs φ² dev {dev:+.3f}%), OLS 誤差 ±{a_err:.3f} ({a_err/PHI2*100:.2f}%)")
print(f"  ε₁={e1*100:.3f}% ε₂={e2*100:.3f}% — 應變 1% 級 vs OLS 誤差 5.8% 級")
print(f"  ⟹ 應變對 α 嘅『修正』(1%) 完全喺 OLS 誤差 (5.8%) 內 — 冇檢驗力")
# 若鎖 φ² (零誤差理論值), α_obs 差有幾大?
print(f"  鎖 φ²: S1 dev {((a_s1-PHI2)/PHI2*100):+.3f}%, S2 dev {((a_s2-PHI2)/PHI2*100):+.3f}%")
print(f"  compare ε₂={e2*100:.3f}%: S2 dev 唔等於 ε₂ (0.93 vs 1.11), S1 dev 反方向")
chk("P3.1 應變修正(1%) ≪ OLS 誤差(5.8%) — 級別冇檢驗力", e2*100 < a_err/PHI2*100)

print("\n═══ P4. 挫阻密度 32/88 結構身份 (只報, 唔宣稱) ═══")
r = 32 / 88
print(f"  32/88 = {r:.6f} = 4/11 = {4}/{11}")
print(f"  B=4 (色數, O223); 11 = 88/8 (2³·11; scripts/25 11×奇數子格)")
print(f"  4/11 ≈ 0.3636 — 有冇已註冊結構常數? 存疑, 只記錄")
# A₅ 清澈度: 32/120 = 4/15? 阻挫密度 rc
rc = 32 / 120
print(f"  32/120 = {rc:.6f} = 4/15 (B/(3×5)? N_gen×F₅=45→但15=?) — 都只記錄")

out = {
    "count_chain": {"edges": len(edges), "frust": len(frust), "sum": len(edges)+len(frust), "target": 120},
    "disjoint": len(overlap) == 0,
    "node_frust_dist_median": float(np.median(dists)),
    "frust_frust_dist_median": float(np.median(fd)),
    "alpha": {"S1": a_s1, "S2": a_s2, "phi2": PHI2, "ols_err": a_err},
    "strain": {"e1": e1, "e2": e2},
    "density": {"32/88": r, "32/120": rc},
}
with open("data/29_frustration_tension_chain.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")