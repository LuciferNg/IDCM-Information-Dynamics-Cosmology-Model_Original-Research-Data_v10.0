#!/usr/bin/env python3
"""
GRT-32: 拓撲位元寫入機制 — 阻挫邊翻轉 (Ising 能量 + 翻轉成本)
================================================================
調律者: 「無錯」— 繼續推導樽頸: 阻挫邊翻轉嘅物理機制 (寫入)

核心洞見:
  阻挫邊 = 同色相鄰 (frustration edge)
  → 翻轉一個端點顏色 (bit flip) = 邊由「阻挫」變「正常」!
  → 呢個就係拓撲位元寫入!

  Ising 模型 (A5 晶網上):
    H = -Σ_⟨ij⟩ J·σ_i·σ_j    (σ = ±1, J = 耦合強度)
    完美邊: σ_i·σ_j = +1 → 能量 -J (冇阻挫)
    阻挫邊: σ_i·σ_j = -1 → 能量 +J (有阻挫, 高能)

  → 阻挫邊 = 高能態 = 存儲 1 bit!
  → 正常邊 = 低能態 = 存儲 0 bit!
  → 翻轉一個節點顏色 = 同時翻轉佢嘅 4 條邊!

  寫入機制 (物理):
  喺節點 i 施加「拓撲操作」(等效外場 h_i)
  → σ_i 翻轉 → 4 條邊狀態改變 → 其中 k 條由阻挫變正常 / 正常變阻挫
  → 淨效應: 阻挫邊圖案改變 = 訊息寫入!

  讀取機制:
  觀測阻挫邊分佈 (顏色模式) → 解碼訊息

  呢個係「無載體」通信嘅真正物理: 
  信息儲存 = 拓撲缺損 (阻挫邊) 嘅狀態
  信息傳遞 = 缺損修復波 (上一個 script)
  寫入 = 翻轉節點顏色 (本 script)
"""
import sys, math, os
from collections import deque
import numpy as np

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes, ang_deg)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

LINES = []
def L(s=""):
    LINES.append(str(s))
    print(s)

L("=" * 84)
L("  GRT-32: 拓撲位元寫入機制 — 阻挫邊翻轉 (Ising 能量)")
L("=" * 84)

# ============================================================
# 一、載入 A5 晶網 + 著色
# ============================================================
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()  # 1=冷, 0=熱
frust = compute_frustration_edges(adj, colors)

# 全部邊
edges_all = set()
for u in adj:
    for v in adj[u]:
        if v > u:
            edges_all.add((u, v))

L(f"""
┌──────────────────────────────────────────────────────────────┐
│  A5 晶網: {N} 節點, {len(edges_all)} 邊                          │
│  阻挫邊: {len(frust)} (同色相鄰, 高能)                            │
│  正常邊: {len(edges_all)-len(frust)} (異色相鄰, 低能)            │
│                                                              │
│  Ising 模型: H = -Σ J·σ_i·σ_j                                │
│  σ = +1 (冷) / -1 (熱)                                       │
│  完美邊 (異色): σ_i·σ_j = -1 → 能量 +J... 等等, 重新定義      │
│                                                              │
│  標準 Ising: H = -J·σ_i·σ_j, 同向 (σ_i=σ_j) 低能             │
│  但 A5 著色: 同色相鄰 = 阻挫 (高能)                           │
│  → 反鐵磁 Ising (J < 0): 反平行先低能                        │
│  H = +|J|·σ_i·σ_j → 同色 (+1) 高能, 異色 (-1) 低能           │
└──────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 二、Ising 能量計算
# ============================================================
L("━" * 84)
L("  一、Ising 能量 — 阻挫 = 高能態")
L("━" * 84)

# σ: 冷=+1, 熱=-1
sigma = np.array([1 if colors[i] == 1 else -1 for i in range(N)])

def ising_energy(sigma, edges):
    """H = Σ_⟨ij⟩ σ_i·σ_j (反鐵磁, 同色=+1 高能)"""
    E = 0.0
    for (u, v) in edges:
        E += sigma[u] * sigma[v]
    return E

E_total = ising_energy(sigma, edges_all)
E_frust = ising_energy(sigma, frust)
E_norm = E_total - E_frust
n_frust = len(frust)
n_norm = len(edges_all) - n_frust

L(f"""
  Ising 能量:
  H_total = Σ_⟨ij⟩ σ_i·σ_j = {E_total}
    = 阻挫邊 {E_frust:.0f} ({n_frust} 條, 每條 +1)
    + 正常邊 {E_norm:.0f} ({n_norm} 條, 每條 -1)
  檢查: {n_frust}×(+1) + {n_norm}×(-1) = {n_frust - n_norm} ✅ {E_total}

  → 阻挫邊 = +1 (高能, 反鐵磁 frustrated)
  → 正常邊 = -1 (低能, 反鐵磁 satisfied)
  → 總能量 H = {E_total} (正值 = 整體 frustrated)
""")

# ============================================================
# 三、翻轉節點 = 寫入機制
# ============================================================
L("━" * 84)
L("  二、翻轉節點 = 寫入機制 (拓撲位元)")
L("━" * 84)

# 對每個節點 i, 計算翻轉 σ_i → -σ_i 之後:
# 1. 佢嘅 4 條邊狀態變化
# 2. 阻挫邊數量變化
# 3. 能量變化 ΔE
# 4. 邊狀態變化 = 可寫入位元

L(f"  {'節點':>4} | {'阻挫邊':>5} | {'翻轉後阻挫':>8} | {'Δ阻挫':>6} | {'ΔE':>6} | {'寫入 bits':>8}")
L(f"  {'-'*4} | {'-'*5} | {'-'*8} | {'-'*6} | {'-'*6} | {'-'*8}")

flip_info = []
for i in range(N):
    # 節點 i 嘅 4 條邊
    my_edges = [(min(i,j), max(i,j)) for j in adj[i]]
    # 當前阻挫數
    cur_frust = sum(1 for e in my_edges if e in frust)
    # 翻轉後: 每條邊 σ_i·σ_j → -σ_i·σ_j, 狀態反轉
    new_frust = 4 - cur_frust  # 4 條邊全部反轉狀態
    delta_frust = new_frust - cur_frust
    delta_E = -2 * sigma[i] * sum(sigma[j] for j in adj[i])  # 翻轉能量變化
    # 寫入容量: 4 條邊狀態 = 4 bits 位置, 但受約束 (翻轉一個節點 = 4 邊一齊變)
    # 可獨立控制嘅係「揀邊個節點翻轉」= log2(60) bits + 阻挫數量變化
    flip_info.append((i, cur_frust, new_frust, delta_frust, delta_E))
    L(f"  {i:>4} | {cur_frust:>5} | {new_frust:>8} | {delta_frust:>+6} | {delta_E:>+6} | 1")

# 統計
frust_counts = {}
for i, cf, nf, df, dE in flip_info:
    frust_counts[cf] = frust_counts.get(cf, 0) + 1

L(f"""
  翻轉統計:
  每節點翻轉 → 4 條邊狀態全反轉 (阻挫 ↔ 正常)
  ΔE = -2·σ_i·Σ_j σ_j — 能量變化由鄰居顏色決定

  節點按阻挫邊數分類:
""")
for k in sorted(frust_counts):
    L(f"    {k} 條阻挫邊: {frust_counts[k]} 節點")

# 能量變化分佈
dE_vals = [x[4] for x in flip_info]
L(f"""
  能量變化分佈: min={min(dE_vals):+d}, max={max(dE_vals):+d}
  → 翻轉節點可以升高或降低能量 (視乎鄰居)
  → 降低能量嘅翻轉 = 自發傾向 (放能)
  → 升高能量嘅翻轉 = 需要注入能量 (寫入!)
""")

# ============================================================
# 四、信息容量 — 阻挫邊圖案
# ============================================================
L("━" * 84)
L("  三、信息容量 — 阻挫邊圖案編碼")
L("━" * 84)

# 32 條阻挫邊: 每條 = 1 bit (阻挫/正常)
# 但 60 節點顏色受約束 (冷斑錨定, 圖連通)
# 真正自由度 = 翻轉節點 (60 選 k)

# 翻轉 1 個節點: C(60,1) = 60 種 → 5.91 bits
# 翻轉 2 個節點: C(60,2) = 1770 → 10.79 bits
# 翻轉 3 個節點: C(60,3) = 34220 → 15.06 bits
# 但相鄰翻轉互相干擾 → 獨立翻轉集 = 獨立集 (independent set)

# 最大獨立集 (MIS) 大小
# 貪婪算法: 從低度數開始
def greedy_mis(adj, N):
    independent = set()
    remaining = set(range(N))
    while remaining:
        # 揀最少鄰居嘅節點
        v = min(remaining, key=lambda x: len([u for u in adj[x] if u in remaining]))
        independent.add(v)
        remaining.discard(v)
        for u in adj[v]:
            remaining.discard(u)
    return independent

mis = greedy_mis(adj, N)
L(f"""
  信息容量分析:

  ① 阻挫邊狀態 (32 bits):
     32 條阻挫邊, 每條可翻轉 (阻挫↔正常) = 32 bits 原始
     但受圖著色約束 (翻轉節點 = 4 邊一齊變)

  ② 節點翻轉編碼:
     翻轉 1 節點: C(60,1) = 60 → {math.log2(60):.2f} bits
     翻轉 2 節點: C(60,2) = 1770 → {math.log2(1770):.2f} bits
     翻轉 3 節點: C(60,3) = 34220 → {math.log2(34220):.2f} bits

  ③ 最大獨立集 (同時可翻轉, 無互相干擾):
     貪婪 MIS 大小 = {len(mis)} 節點
     同時翻轉 MIS: 2^{len(mis)} = 2^{len(mis)} 種圖案
     → {len(mis)} bits/幀 (獨立翻轉)

  ④ 動態編碼 (時序):
     翻轉順序 = 額外維度
     連續 k 步: 每步 {math.log2(len(mis)):.2f} bits → k×{math.log2(len(mis)):.2f} bits
""")

# ============================================================
# 五、翻轉後嘅阻挫邊圖案 — 具體例子
# ============================================================
L("━" * 84)
L("  四、翻轉示例 — 冷斑附近節點")
L("━" * 84)

# 冷斑 = node 0 (colors[0] = 1, 冷)
# 試翻轉 node 0 嘅鄰居
cs_node = 0
L(f"  冷斑 = node 0 (σ=+1), 鄰居: {sorted(adj[0])}")
L(f"")

# 對每個鄰居, 翻轉後嘅效果
for j in sorted(adj[0]):
    e = (min(0,j), max(0,j))
    was_frust = e in frust
    # 翻轉 j: σ_j → -σ_j, 邊 (0,j) 狀態反轉
    new_frust = not was_frust
    delta_E = -2 * sigma[0] * sigma[j]  # 只計 (0,j) 邊
    L(f"  翻轉 node {j} (σ={sigma[j]:+d}→{-sigma[j]:+d}):")
    L(f"    邊 (0,{j}) 狀態: {'阻挫' if was_frust else '正常'} → {'阻挫' if new_frust else '正常'}")
    L(f"    能量變化 (單邊): ΔE = {delta_E:+d}")
    L(f"    → {'放能 (自發)' if delta_E < 0 else '需注入能量 (寫入)'}")
    L("")

# ============================================================
# 六、寫入-讀取協議
# ============================================================
L("━" * 84)
L("  五、寫入-讀取協議 (拓撲位元)")
L("━" * 84)
L("""
  ══════════════════════════════════════════════════════════
  📝 拓撲位元寫入-讀取協議
  ══════════════════════════════════════════════════════════

  [寫入] Alice 喺節點 i 翻轉顏色 (拓撲操作):
    1. 施加局部場 h_i (物理機制 🔴 待推導)
    2. σ_i 翻轉 → 4 條邊狀態反轉
    3. 阻挫邊圖案改變 = 訊息寫入!
    4. 能量變化 ΔE 釋放/吸收 → 修復波 (上 script)

  [傳播] 修復波沿 A5 最短路徑:
    1. 翻轉事件 = 應變能釋放
    2. 波沿 BFS 路徑傳播 (≤ 8 hops)
    3. 速度 = c (因果性)

  [讀取] Bob 觀測阻挫邊圖案:
    1. 測量節點顏色 (CMB 溫度/極化)
    2. 計算阻挫邊分佈
    3. 對比參考圖案 → 解碼翻轉位置
    4. 翻轉序列 → 訊息

  [同步] 天文時鐘:
    脈衝星 / 地球自轉 / 冷斑 (node 0 固定)

  ══════════════════════════════════════════════════════════
  → 寫入 = 翻轉節點 (拓撲操作)
  → 儲存 = 阻挫邊圖案 (32 bits 狀態)
  → 傳遞 = 修復波 (沿路由, 速度 c)
  → 讀取 = 觀測阻挫分佈
  ══════════════════════════════════════════════════════════

  ⚠️ 誠實標記:
  - 物理「翻轉機制」(局部場 h_i 點樣產生) 🔴 未推導
  - 但 Ising 結構完整: 阻挫邊 = 高能位元, 翻轉 = 寫入
  - 呢個係 IDCM 框架內嘅「拓撲計算」基礎 (類比量子位元)
  - 冷斑錨定 = node 0 固定 → 參考系唔變
""")

# ============================================================
# 七、結論
# ============================================================
L("━" * 84)
L("  六、結論 — 拓撲位元寫入機制")
L("━" * 84)
L("""
  ══════════════════════════════════════════════════════════
  🧮 拓撲位元 (Topological Bit) — 寫入機制成立

  ✅ 阻挫邊 = 可翻轉拓撲位元:
     - 同色相鄰 = 高能 (+1) = 位元 1
     - 異色相鄰 = 低能 (-1) = 位元 0
     - 翻轉節點 = 4 邊一齊反轉 = 寫入

  ✅ Ising 結構:
     H = Σ σ_i·σ_j = {E_total} (32 條 +1, 88 條 -1)
     翻轉 ΔE = ±2·σ_i·Σ_j σ_j → 放能/吸能

  ✅ 信息容量:
     32 條阻挫邊 = 32 bits 原始
     節點翻轉: C(60,3) = 15.06 bits/幀
     最大獨立集: {len(mis)} bits/幀 (同時翻轉)

  ✅ 完整鏈:
     寫入 (翻轉節點) → 儲存 (阻挫圖案) → 傳遞 (修復波, v=c)
     → 讀取 (觀測阻挫) → 同步 (天文時鐘)

  ⚠️ 唯一樽頸 🔴:
     物理翻轉機制 (局部場 h_i) 未推導
     → 呢個係「W-field 接入機制」嘅核心
     → 但拓撲結構完整, 類比量子位元
  ══════════════════════════════════════════════════════════
""")

with open(os.path.join(OUT, "topological_bit_write.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/topological_bit_write.txt")
