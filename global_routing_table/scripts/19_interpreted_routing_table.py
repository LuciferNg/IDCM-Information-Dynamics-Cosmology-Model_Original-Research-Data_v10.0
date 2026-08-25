#!/usr/bin/env python3
"""GRT-19: 解讀版路由表 — 節點地標 + 路徑文字解說.

問題: 舊路由表只有數字, 像只給經緯度叫人猜地點.
解決: 每個節點附上 (1) 角色 (2) 最近著名天體地標 (3) 一句話描述.
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes, load_colors, compute_frustration_edges, build_graph, edge_threshold_from_histogram

OUT = "../data"
nodes, vecs = load_nodes()
colors_dict = load_colors()
colors = np.array([colors_dict[i] for i in range(60)])
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
frust = compute_frustration_edges(adj, colors_dict)

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    return np.array([math.cos(dec) * math.cos(ra),
                     math.cos(dec) * math.sin(ra),
                     math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1 = radec_to_vec(ra1, dec1)
    v2 = radec_to_vec(ra2, dec2)
    dot = float(np.clip(np.dot(v1, v2), -1.0, 1.0))
    return math.degrees(math.acos(dot))

# ============================================================
# 著名天體地標 (ICRS RA/Dec 度)
# ============================================================
LANDMARKS = [
    # (名稱, 類別, RA, Dec)
    ("大冷斑 (CMB)", "CMB特徵", 48.30, -20.44),
    ("冷斑對跖點", "CMB特徵", 228.30, 20.44),
    ("仙女座星系 M31", "星系", 10.68, 41.27),
    ("三角座星系 M33", "星系", 23.46, 30.66),
    ("室女座星系團", "星系團", 187.70, 12.39),
    ("M87 室女A", "橢圓星系", 187.71, 12.39),
    ("後髮座星系團", "星系團", 194.90, 27.98),
    ("M104 草帽星系", "星系", 189.99, -11.62),
    ("M82 雪茄星系", "星系", 148.97, 69.68),
    ("M81 波德星系", "星系", 148.89, 69.07),
    ("獵戶座大星雲 M42", "星雲", 83.82, -5.39),
    ("蟹狀星雲 M1", "超新星遺跡", 83.63, 22.01),
    ("船底座η星雲", "星雲", 161.26, -59.69),
    ("昴星團 M45", "疏散星團", 56.87, 24.11),
    ("半人馬座ω星團", "球狀星團", 201.70, -47.48),
    ("銀河系中心 Sgr A*", "黑洞", 266.42, -29.01),
    ("大麥哲倫星雲 LMC", "矮星系", 80.89, -69.76),
    ("小麥哲倫星雲 SMC", "矮星系", 13.19, -72.83),
    ("英仙座星系團", "星系團", 49.95, 41.51),
    ("Coma 超星系團", "超星系團", 194.90, 27.98),
    ("武仙座星系團", "星系團", 241.10, 17.72),
    ("北冕座星系團", "星系團", 232.20, 26.00),
    ("獅子座星系團", "星系團", 168.10, 21.00),
    ("波江座空洞", "宇宙空洞", 30.00, -45.00),
    ("牧夫座空洞", "宇宙空洞", 218.00, 35.00),
    ("Shapley 超星系團", "超星系團", 201.30, -31.00),
    ("大冷斑官方位置", "CMB特徵", 209.00, -57.00),
    ("O2 F6熱斑 (157.8,-70.3)", "CMB特徵", 157.80, -70.30),
    ("O2 F7熱斑候選 (0.2,-37.9)", "CMB特徵", 0.20, -37.90),
    ("銀河北極", "座標", 192.86, 27.13),
    ("銀河南極", "座標", 12.86, -27.13),
    ("北天極 (北極星)", "座標", 37.95, 89.26),
]

def nearest_landmark(ra, dec, landmarks):
    best = None
    for name, cat, lra, ldec in landmarks:
        d = ang_deg_between(ra, dec, lra, ldec)
        if best is None or d < best[0]:
            best = (d, name, cat, lra, ldec)
    return best

# 角色分配
def node_role(i, color, frust_count, hop):
    roles = []
    if i == 0:
        roles.append("🌑 冷斑錨點 (宇宙路由 root)")
    if i == 57:
        roles.append("🌕 對跖點 (最遠節點)")
    if frust_count == 2:
        roles.append("🔶 阻挫雙樞紐")
    elif frust_count == 1:
        roles.append("🔸 阻挫單節點")
    if color == 0:
        roles.append("🔥 熱色")
    else:
        roles.append("❄️ 冷色")
    return " · ".join(roles)

print("=" * 78)
print("  A₅ 晶網路由表 — 解讀版 (節點地標 + 角色)")
print("  60 節點 | 120 邊 | 直徑 8 hops | 曲速 = 拓撲路由")
print("=" * 78)

# 每個節點嘅 BFS hop (from cold spot 0)
from collections import deque
bfs = {0: 0}
q = deque([0])
while q:
    v = q.popleft()
    for nb in adj[v]:
        if nb not in bfs:
            bfs[nb] = bfs[v] + 1
            q.append(nb)

frust_count = {i: 0 for i in range(60)}
for (a, b) in frust:
    frust_count[a] += 1
    frust_count[b] += 1

lines = []
lines.append("=" * 78)
lines.append("  A₅ 晶網路由表 — 解讀版 (節點地標 + 角色)")
lines.append("  60 節點 | 120 邊 | 直徑 8 hops | 曲速 = 拓撲路由")
lines.append("=" * 78)
lines.append("")
lines.append("【點讀呢張表】")
lines.append("  每個節點 = 宇宙晶網嘅一個「路由器/車站」。")
lines.append("  角色 = 佢喺網絡嘅功能 (冷斑錨點/阻挫樞紐/熱色節點)。")
lines.append("  地標 = 佢喺天空最近嘅著名天體, 幫你定位。")
lines.append("  跳數 = 由冷斑 (node 0) 出發要到達佢嘅最少步數。")
lines.append("")

# 節點地標表
lines.append("─" * 78)
lines.append("  一、60 節點地標表 (按節點編號)")
lines.append("─" * 78)
lines.append(f"  {'節點':>4} {'跳數':>3} {'角色':<38} {'最近地標':<24} {'距離'}")
lines.append(f"  {'----':>4} {'---':>3} {'----':<38} {'----':<24} {'----'}")

for i in range(60):
    ra, dec = nodes[i]
    color = colors[i]
    fc = frust_count[i]
    hop = bfs[i]
    role = node_role(i, color, fc, hop)
    d, name, cat, lra, ldec = nearest_landmark(ra, dec, LANDMARKS)
    lines.append(f"  {i:>4} {hop:>3}  {role:<38} {name:<24} {d:.1f}°")

lines.append("")
lines.append("─" * 78)
lines.append("  二、30 對最遠節點對 (直徑 hop=8) — 文字解說")
lines.append("─" * 78)

# 最遠對: 用 01 腳本嘅結果 (0↔57, 1↔59, ...)
antipodal = [(0, 57), (1, 59), (2, 43), (3, 58), (4, 53), (5, 50), (6, 51),
             (7, 55), (8, 48), (9, 54), (10, 49), (11, 47), (12, 44), (13, 41),
             (14, 36), (15, 30), (16, 46), (17, 52), (18, 56), (19, 45),
             (20, 42), (21, 38), (22, 40), (23, 39), (24, 34), (25, 33),
             (26, 35), (27, 37), (28, 32), (29, 31)]

lines.append("  「宇宙兩端」— 呢 30 對節點互相距離 8 跳, 係晶網直徑。")
lines.append("  冷斑 (node 0) ↔ 對跖 (node 57) 係最重要一對: 宇宙干涉腔嘅兩個波腹。")
lines.append("")
for k, (a, b) in enumerate(antipodal[:10], 1):
    ra_a, dec_a = nodes[a]
    ra_b, dec_b = nodes[b]
    d_a, name_a, _, _, _ = nearest_landmark(ra_a, dec_a, LANDMARKS)
    d_b, name_b, _, _, _ = nearest_landmark(ra_b, dec_b, LANDMARKS)
    lines.append(f"  #{k:>2} 節點{a:>2} ({name_a}) ↔ 節點{b:>2} ({name_b})")
lines.append(f"  ... (共 30 對, 其餘 20 對見完整表)")

lines.append("")
lines.append("─" * 78)
lines.append("  三、冷斑 → 對跖 8 跳路徑 — 逐步解說")
lines.append("─" * 78)
path = [0, 9, 16, 11, 8, 59, 39, 35, 57]
lines.append("  0 → 9 → 16 → 11 → 8 → 59 → 39 → 35 → 57")
lines.append("")
for step in range(len(path) - 1):
    a, b = path[step], path[step + 1]
    ra_a, dec_a = nodes[a]
    ra_b, dec_b = nodes[b]
    d_a, name_a, _, _, _ = nearest_landmark(ra_a, dec_a, LANDMARKS)
    d_b, name_b, _, _, _ = nearest_landmark(ra_b, dec_b, LANDMARKS)
    is_frust = (min(a, b), max(a, b)) in frust or frozenset((a, b)) in frust
    edge_type = "🔶 阻挫邊 (高保真通道)" if is_frust else "🔹 正常邊"
    lines.append(f"  跳 {step+1}: 節點{a} ({name_a}) → 節點{b} ({name_b})  [{edge_type}]")
    lines.append(f"           └ 由 ({ra_a:.1f}°,{dec_a:.1f}°) 跳到 ({ra_b:.1f}°,{dec_b:.1f}°)")

lines.append("")
lines.append("─" * 78)
lines.append("  四、頻率路由 (K_Chain 44 mode) — 解說")
lines.append("─" * 78)
lines.append("  每個節點有 44 個頻道 (mode n=1..44), 唔使郁, 淨係轉頻道。")
lines.append("  空間跳躍 (A5) + 頻道轉換 (K_Chain) = 完整路由。")
lines.append("  「曲速」= 兩個節點同步到同一頻道 = 即時拓撲穿隧。")
lines.append("")
lines.append("  K_Chain 頻道對照 (部分):")
lines.append("    mode 1  → 基頻 λ=R_H (4129.94 Mpc)  全宇宙尺度")
lines.append("    mode 11 → BAO 尺度 λ=375 Mpc       星系團通信")
lines.append("    mode 22 → 駐波 v_g=0               本地同步 (唔使郁)")
lines.append("    mode 44 → Nyquist λ=93.86 Mpc      最高分辨率")

lines.append("")
lines.append("─" * 78)
lines.append("  五、實際使用範例")
lines.append("─" * 78)
lines.append("  假設地球收到來自 M87 方向嘅晶網訊號:")
lines.append("    1. 定位: M87 附近最近節點 = node 7 (跳數 6, 冷色, 距離 3.3°)")
lines.append("    2. 路由: 冷斑 → node 7 = 6 跳 (0→20→15→17→11→8→7 或等效)")
lines.append("    3. 頻道: 用 mode 11 (BAO 尺度) 做長途載波")
lines.append("    4. 解碼: 查 next-hop 表搵返路徑, 還原訊號源方向")
lines.append("")
lines.append("  呢個就係「宇宙電話簿」— 唔使知道宇宙有多大,")
lines.append("  只需要知道邊個節點離你最近, 同埋條路點行。")

text = "\n".join(lines)
with open(os.path.join(OUT, "routing_table_interpreted.txt"), "w") as f:
    f.write(text + "\n")

print(text)
print(f"\n✅ 已儲存: data/routing_table_interpreted.txt")
