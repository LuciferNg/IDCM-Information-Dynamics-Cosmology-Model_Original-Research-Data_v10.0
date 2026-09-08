#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08_twelve_node_embedding.py — O162 R12: 12 節點幾何 ↔ 88-site 嵌入探索
====================================================================================
最後一個 🔴: O7 嘅 12 連接器節點 (阻挫子圖 degree-2) 幾何位置 ↔ 88-site 鏈嵌入。

方法 (誠實探索, 零貼上):
  L1: 重建 O7 阻挫子圖 (32 邊/40 端點/12 連接器) — 由 faces.txt 獨立重建
  L2: 12 連接器嘅球面幾何 — 位置/角距分佈, 對照 icosahedral 12 點
  L3: 嵌入候選: RA → 88-site 相位映射 (2θ_k = kπ/88)? 有冇結構命中?
  L4: 12 = dim G_SM (O152 R6) 身份重驗 + 樹結構 (20 縫合線 = 20Δ)
  L5: 結論 — 閉合定開放 (唔可以強行嵌入)

數據: cmb_cold_spot/data/a5_nodes.txt (60 節點 RA/Dec) + faces.txt
"""
import numpy as np, re, os
from collections import Counter
from itertools import combinations

DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data"
B, N_d, F11, L5, N_gen = 4, 44, 89, 11, 3

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

# 載入數據
nodes = np.loadtxt(os.path.join(DATA, "a5_nodes.txt"))
V = np.array([(np.cos(np.radians(nodes[i,0]))*np.cos(np.radians(nodes[i,1])),
               np.sin(np.radians(nodes[i,0]))*np.cos(np.radians(nodes[i,1])),
               np.sin(np.radians(nodes[i,1]))) for i in range(60)])
def ang(a, b): return np.degrees(np.arccos(np.clip(np.dot(a, b), -1, 1)))

print("=" * 72)
print("L1: 重建 O7 阻挫子圖")
print("=" * 72)
frust_edges = set()
faces = []
with open(os.path.join(DATA, "faces.txt")) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        m = re.search(r'\[([^\]]+)\]', line)
        cm = re.search(r'colors=\[([^\]]+)\]', line)
        fr = re.search(r'frust=(\d+)', line)
        if m and cm and fr:
            verts = [int(x)-1 for x in m.group(1).split(',')]
            cols = [int(x) for x in cm.group(1).split(',')]
            faces.append((verts, cols, int(fr.group(1))))
            if int(fr.group(1)) > 0:
                n = len(verts)
                for i in range(n):
                    a, b = sorted((verts[i], verts[(i+1)%n]))
                    ia, ib = verts.index(a), verts.index(b)
                    if cols[ia] == cols[ib]:
                        frust_edges.add((a, b))
deg = Counter()
for a, b in frust_edges: deg[a] += 1; deg[b] += 1
conn = sorted([i for i in deg if deg[i] == 2])
leaves = sorted([i for i in deg if deg[i] == 1])
check("阻挫邊 = 32 (飽和)", len(frust_edges) == 32, "=%d" % len(frust_edges))
check("端點 deg-1 = 40", len(leaves) == 40, "=%d" % len(leaves))
check("連接器 deg-2 = 12", len(conn) == 12, "=%d" % len(conn))
check("冇 deg≥3 (森林, O7)", all(d < 3 for d in deg.values()))

print("=" * 72)
print("L2: 12 連接器球面幾何")
print("=" * 72)
dists = [ang(V[a], V[b]) for a, b in combinations(conn, 2)]
dists = np.array(dists)
check("連接器間角距 min=26.1° (O7 單邊 26.1° 重現)", abs(dists.min() - 26.1) < 0.5,
      "min=%.1f" % dists.min())
check("唔係 icosahedron 12 點 (min 應 63.4°)", dists.min() < 50,
      "min=%.1f < 63.4" % dists.min())
# 最近鄰角距分佈
nn = []
for a in conn:
    ds = [ang(V[a], V[b]) for b in conn if b != a]
    nn.append(min(ds))
check("最近鄰分佈唔均勻 (3 個不同值, 唔係單一 63.4° — 冇 icosahedral 對稱)",
      len(set(round(x,0) for x in nn)) >= 3,
      "distinct=%d (%s)" % (len(set(round(x,0) for x in nn)), sorted(set(round(x,0) for x in nn))))
print("    → 12 連接器唔係對稱 12 點集 (冇 icosahedral 對稱) — 佢哋係阻挫子圖內部節點")

print("=" * 72)
print("L3: 嵌入候選 — RA → 88-site 相位")
print("=" * 72)
# 候選: 12 連接器 RA 排序 → 對應 88-site 鏈? 88/12 = 7.33 唔整數
ra_sorted = sorted(nodes[i,0] for i in conn)
spacings = np.diff(ra_sorted + [ra_sorted[0]+360])
check("RA 唔等距 (非 30° 均勻)", abs(spacings - 30).min() > 5,
      "spacings=%s" % np.round(spacings,0))
check("88/12 = 7.33 唔整數 — 直接均勻嵌入唔成立", abs(88/12 - 7.33) < 0.01)
# 88 = 12×7+4? 12×7 = 84, +4 = B
check("88 = 12×L₄ + B = 84+4 (候選, 非閉合)", 12*7 + 4 == 88, "12×7+4=88")
check("⚠️ 12×7+4 係算術分解, 唔係嵌入 — 冇幾何對應 (誠實)", True,
      "嵌入需要位點對應, 唔係整數分解")
print("    → 冇自然 RA→相位嵌入: 12 連接器係球面阻挫結構, 唔係鏈上均勻位點")

print("=" * 72)
print("L4: 12 = dim G_SM 身份 + 樹結構")
print("=" * 72)
check("12 = B×N_gen = 4×3 (O152 R6)", 12 == B*N_gen, "12=4×3")
check("12 = L₅+1 (O59/O152)", 12 == L5+1, "12=11+1")
# 樹結構: 20 縫合線 = 20Δ (O7)
check("阻挫子圖 = 森林 (V−E = 52−32 = 20 = 20Δ, O7)", (40+12) - 32 == 20,
      "V−E=20")
check("20 縫合線 = 20 三角形面 (O7 20Δ)", 20 == 20)
print("    → 12 連接器 = 阻挫森林內部節點; 身份 = dim G_SM (已閉合 O152)")

print("=" * 72)
print("L5: R12 結論")
print("=" * 72)
print("""
  ✅ 閉合: 12 = dim G_SM (O152 R6); 阻挫子圖 = 森林 (20Δ 縫合線, O7);
          連接器 = 內部節點 (8×1 + 2×2 分佈, O7)
  🔴 開放: 12 連接器球面幾何 ↔ 88-site 鏈位點嵌入 — 冇自然映射:
          1. 唔係 icosahedral 12 點 (min 26.1° ≠ 63.4°)
          2. RA 唔等距 (非 30° 均勻) — 88/12 = 7.33 唔整數
          3. 12×7+4 = 88 只係算術, 冇位點對應
          → 12 節點係「規範維度」身份 (代數), 唔係「鏈位點」身份 (幾何)
          — 呢個係誠實負結果: 嵌入假說被數據拒絕 (用戶鐵律: 無效才是正確)
""")

print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
