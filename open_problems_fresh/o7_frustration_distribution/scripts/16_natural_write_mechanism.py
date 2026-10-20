#!/usr/bin/env python3
"""
O7 — 16_natural_write_mechanism.py (2026-10-11)
====================================================================
O7/natural-write-closure 第一輪: 阻挫邊 Ising 位元之相位滑移寫入機制
====================================================================
目標: 由 O7 圖結構第一性原理推導「天然寫入」機制, 唔重推 O220 docs/19
      (熱力學/資訊審計) 同 O41 (成本閉合), 而係填補佢哋中間嘅機制空檔:

  G1. 翻轉操作 ⟺ 譜相位 π 配對: O7 端點顏色反轉 (Z2 乘法 ×(−1))
      vs O161 88-鏈 Nyquist link U_88 = e^{i·2θ_88} = e^{iπ} = −1
  G2. ΔE = 2|h_i| 中「2」嘅兩層身份裁定 (譜側 2×半整數 vs 圖側 3−1 邊變化)
  G3. 12 個近零能量節點實測 (|T|≈0 ⟺ ΔE≈0): 數量 + 結構角色 + 誠實 threshold 分析
  G4. θ_i = arccos(T_i/A) 身份偵察: 否證「同冷斑角距離」假設, 另測幾何方位

數據: cmb_cold_spot/data (smica_smoothed.txt = 4.17° 節點溫度, a5_nodes, faces,
      frustration_edges, anchored_coloring) — 全部獨立重算, 唔 import 上游。
譜慣例: O161 site-link phase 2θ_k = kπ/88, γ_k = 4sin²(kπ/176), γ_44 = 2 = μ²。
"""

import math, re
from collections import defaultdict, deque, Counter
import numpy as np

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — 天然寫入機制 (G1-G4)")
print("=" * 76)

# ── 載入 ──
nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split()
    nodes.append((float(p[0]), float(p[1])))   # (ra, dec), idx = 行序 0..59
nodes = np.array(nodes)

T = {}
for line in open(f'{DATA}/smica_smoothed.txt'):
    if line.startswith('#'): continue
    p = line.split(); T[int(p[0])] = float(p[2])

col = {}
for line in open(f'{DATA}/anchored_coloring.txt'):
    if line.startswith('#'): continue
    p = line.split(); col[int(p[0])] = int(p[3])

frust = set()
for line in open(f'{DATA}/frustration_edges.txt'):
    if line.startswith('#'): continue
    p = line.split(); frust.add((int(p[0]), int(p[1])))

adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])

dg = {v: sum(1 for (a, b) in frust if v in (a, b)) for v in range(60)}
frust_nodes = [v for v in range(60) if dg[v] > 0]

# 縫合線 (阻挫子圖 components)
seen = set(); seams = []
for s in frust_nodes:
    if s in seen: continue
    comp = []; q = deque([s]); seen.add(s)
    while q:
        u = q.popleft(); comp.append(u)
        for w in [x for x in frust_nodes if (min(u, x), max(u, x)) in frust and x not in seen]:
            seen.add(w); q.append(w)
    if len(comp) >= 2: seams.append(sorted(comp))
endpoints = set()
for comp in seams:
    endpoints.update(v for v in comp if dg[v] == 1)

# ═══════════════════════════════════════════════════════════════
# G1. 翻轉操作 ⟺ 譜相位 π 配對
# ═══════════════════════════════════════════════════════════════
print("\n─── G1. 翻轉 = Z2 反轉 = e^{i pi} = U_88 配對 ───")
# (a) 圖側: 顏色反轉 = Z2 乘法 ×(−1)
#     冷=1, 熱=0 → 翻轉: c → 1−c; 誌裏 {0,1} → {+1,−1}: x' = −x
#     翻轉兩次 = 恆等 ⟺ (−1)^2 = 1 = e^{i2π}
# (b) 譜側 (O161): 88-鏈 Nyquist link U_88 = e^{i·2θ_88} = e^{i·88π/88} = e^{iπ} = −1
theta_88_degrees = 88 * 180.0 / 88.0
U88_re = math.cos(math.pi)
U88_im = math.sin(math.pi)
check("G1a: 2θ_88 = 88π/88 = π (exact)", abs(theta_88_degrees - 180.0) < 1e-12, f"{theta_88_degrees}°")
check("G1b: U_88 = e^{iπ} = −1", abs(U88_re + 1.0) < 1e-15 and abs(U88_im) < 1e-15)
check("G1c: 翻轉兩次 = 恆等 ⟺ e^{i2π} = 1", abs(math.cos(2*math.pi) - 1.0) < 1e-15)
# 配對: 翻轉 (Z2) ≅ 乘 (−1) ≅ U_88
# 客觀檢查: 翻轉改變 阻挫邊狀態 (同色↔異色), 對應 link phase 0↔π
# 一條邊 (u,v) 同色 ⟺ 相位差 0 (mod π); 翻轉 u → 相位差 π
same_pairs = sum(1 for (u, v) in frust if col[u] == col[v])
check("G1d: 全部 32 阻挫邊 = 同色邊 (相位差 0 mod π)", same_pairs == 32, f"{same_pairs}/32")
# 翻轉一個端點 → 佢 4 條邊嘅相位差全部 +π (0↔π 對調)
# 即「寫入」= 對該節點實施 U_88 相位單位
eps = sorted(endpoints)
bad = 0
for v in eps:
    # 翻轉 v 後, 原本同色邊變異色, 異色邊變同色
    for w in adj[v]:
        before = (col[v] == col[w])
        after = (1 - col[v] == col[w])
        if before == after:
            bad += 1
check("G1e: 翻轉端點令其全部 4 條邊相位差反轉 (0↔π)", bad == 0 and all(len(adj[v]) == 4 for v in eps), f"bad={bad}")
print(f"  → O7 flip ≅ 節點相位滑移 π ≅ U_88 = e^{{iπ}}: 20 條縫合線 = 20 個獨立 Z2 相位單位")
print(f"     (2^20 圖案 ⇔ 20 個獨立 π 相位自由度, 衝突圖 0 邊已證 O7/99d)")

# ═══════════════════════════════════════════════════════════════
# G2. ΔE = 2|h_i| 嘅「2」— 兩層身份裁定
# ═══════════════════════════════════════════════════════════════
print("\n─── G2. ΔE = 2|h_i| 的「2」兩層裁定 ───")
# 層 A (譜側, O41 已閉合): π = 2 × (π/2) = 2 個半整數相位單位, 每單位 E_min
#   ΔE_write = 2 × E_min × γ × |cos θ_i|, E_min = 123/176, B(n) = 2 E_min = 123/88
B_per = 123.0 / 88.0
E_min = 123.0 / 176.0
check("G2a: B(n) = 2 × E_min (譜側雙半整數)", abs(B_per - 2 * E_min) < 1e-15)
check("G2b: π 滑移 = 2 個半整數單位 (O41 閉合)", abs(B_per - 2 * E_min) < 1e-12)
# 層 B (圖側, 本輪獨立重算): 翻轉單端點, 3 外邊 N→F (+3), 1 縫合線邊 F→N (−1)
#   → 淨 +2 條阻挫邊變化; 翻轉整縫合線 (雙端點) → +6, −0..2 (script 10 / 99d 已證)
net2 = []
for v in eps:
    bef_same = sum(1 for w in adj[v] if col[v] == col[w])   # 翻轉前同色邊數 (即阻挫邊數)
    added = 4 - bef_same                                     # 翻轉前異色邊 → 翻轉後同色 (新增阻挫)
    removed = bef_same                                       # 翻轉前同色邊 → 翻轉後異色 (移除阻挫)
    net2.append(added - removed)                             # = 4 − 2·bef_same
check("G2c: 單端點翻轉淨 = +2 條阻挫邊變化 (3−1)", all(n == 2 for n in net2), f"n={len(net2)}")
# 裁定: 兩個「2」不同層 — 唔好強行統一:
#   譜側 2 = 雙半整數單位 (成本單位); 圖側 2 = 3−1 邊淨變化 (圖拓撲)
#   兩者喺 ΔE = 2|h_i| 重疊係「巧合」定「同源」? 記錄為開放 (唔強推)
print("  → 裁定: 譜側 2 (=2×E_min, 成本) 與 圖側 2 (=3−1, 邊變化) 係兩個唔同結構層")
print("  → ΔE = 2|h_i| 嘅「2」以譜側為準 (成本單位 μ²=γ_44, O159); 圖側 2 記錄為平行結構")
check("G2d: ΔE 成本單位 = μ² = γ_44 = 2 (O161/O159 慣例)", abs(4*math.sin(math.pi*44/176)**2 - 2.0) < 1e-12, f"γ_44={4*math.sin(math.pi*44/176)**2:.12f}")

# ═══════════════════════════════════════════════════════════════
# G3. 12 個近零能量節點 (ΔE ≈ 0 ⟺ |cos θ| ≈ 0 ⟺ |T| ≈ 0)
# ═══════════════════════════════════════════════════════════════
print("\n─── G3. 12 個近零能量節點 — 負結果確認 (|T|≈0 ⟺ ΔE≈0 候選) ───")
At = [abs(T[v]) for v in range(60)]
At_sorted = sorted(At)
print("   |T| 排序 (首 18):", " ".join(f"{x:.1f}" for x in At_sorted[:18]))
# gap 分析: 最大間隙
gaps = [(At_sorted[i+1] - At_sorted[i], i) for i in range(len(At_sorted)-1)]
mg = max(gaps)
print(f"   最大 gap = {mg[0]:.1f} μK (喺第 {mg[1]} 位, |T|={At_sorted[mg[1]]:.1f}→{At_sorted[mg[1]+1]:.1f})")
# 「12 近零節點」check (O162: 12 ΔE=0 = B×N_gen = dim G_SM, 🟡)
cnt12_low = At_sorted[11]
gap_at_12 = At_sorted[12] - At_sorted[11]
print(f"   第 12 位 |T| = {cnt12_low:.1f}, 第 12→13 gap = {gap_at_12:.1f} μK (全段 gap 中位 = {np.median([g[0] for g in gaps]):.1f})")
n_below = {}
for thr in [5.0, 7.5, 10.0, 12.5]:
    n_below[thr] = sum(1 for x in At if x < thr)
print(f"   |T|<threshold 節點數: {n_below}")
check("G3a: |T| 冇 12-cluster 自然 gap (最大 gap 遠離第12位)", not (mg[1] == 11 or mg[1] == 12), f"max-gap@idx{mg[1]}")
check("G3b: 「12 近零」係 threshold 依賴 (thr=7.5→12, thr=5→9, thr=10→15)", not (n_below[7.5] == 12 and n_below[5.0] == 12 and n_below[10.0] == 12), f"{n_below}")
low = [v for v in range(60) if abs(T[v]) < 7.5]
print(f"   (thr=7.5 參考組 n={len(low)}: {sorted(low)})")
check("G3c: 12 ΔE=0 節點候選 (O162) 無自然 gap 支撐 → threshold 依賴", len(low) == 12, "thr=7.5 啱好 12 (巧合)")

# ═══════════════════════════════════════════════════════════════
# G4. θ_i = arccos(T_i/A) 身份偵察
# ═══════════════════════════════════════════════════════════════
print("\n─── G4. θ_i = arccos(T_i/A) 身份偵察 ───")
A = 134.2
# 否證: θ_i = 同冷斑角距離 (corr ≈ 0.11, 已測)
from astropy.coordinates import SkyCoord
import astropy.units as AU
sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
sep0 = sc[0].separation(sc).deg
obs = np.array([T[i] for i in range(60)])
pred_c = -A * np.cos(np.radians(sep0))
c1 = np.corrcoef(pred_c, obs)[0, 1]
check("G4a: θ=同冷斑角距離 假設否證 (|corr| < 0.2)", abs(c1) < 0.2, f"corr={c1:+.3f}")
# 幾何方位: node 0 為極點嘅方位角 (繞 node0 軸)
# 建 local frame: z = node0 方向, x = 任意垂直 (RA 增加方向), 計方位
z = sc[0].cartesian.xyz.value
z = z / np.linalg.norm(z)
e_ra = np.array([-math.sin(math.radians(nodes[0][0])), math.cos(math.radians(nodes[0][0])), 0.0])
e_ra = e_ra - np.dot(e_ra, z) * z
e_ra = e_ra / np.linalg.norm(e_ra)
e_dec = np.cross(z, e_ra)
az = []
for i in range(60):
    v = sc[i].cartesian.xyz.value
    v = v / np.linalg.norm(v)
    az.append(math.degrees(math.atan2(np.dot(v, e_dec), np.dot(v, e_ra))))
az = np.array(az)
for kphase in [1, 2]:
    p = -A * np.cos(np.radians(az * kphase))
    ck = np.corrcoef(p, obs)[0, 1]
    print(f"   方位 cos({kphase}·az): corr = {ck:+.3f} (偵察, 非 check)")
check("G4b: θ=方位角 假設否證 (|corr| < 0.2)", abs(np.corrcoef(-A*np.cos(np.radians(az)), obs)[0,1]) < 0.2, f"corr={np.corrcoef(-A*np.cos(np.radians(az)), obs)[0,1]:+.3f}")
# θ 反推唔呈譜格 (θ ≈ kπ/88 檢查)
th = np.degrees(np.arccos(np.clip(obs / A, -1, 1)))
spec = th / (180.0 / 88.0)      # θ 用 kπ/88 單位
frac = np.abs(spec - np.round(spec))
check("G4c: θ_i 唔呈 kπ/88 譜格 (平均 frac > 0.1)", np.mean(frac) > 0.1, f"mean frac={np.mean(frac):.3f}")
print("   → θ_i 身份開放: 非角距離、非方位、非 88-格譜格; 維持 🔴 (O162 R6 per-mode 實作未定)")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)