#!/usr/bin/env python3
"""GRT-20: 宇宙公交指南 — 完整使用說明 (普通人視角).

將路由表變成「宇宙地鐵指南」:
- 車站 = A5 節點
- 路線 = 晶網邊
- 班次 = K_Chain 頻道
- 車資 = 加權延遲
- 規矩 = 路由規則

用 M87 做完整教學範例 (點上車, 點轉車, 幾多錢, 幾耐).
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes, load_colors, compute_frustration_edges, build_graph, edge_threshold_from_histogram

OUT = "../data"
nodes, vecs = load_nodes()
colors_dict = load_colors()
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
frust = compute_frustration_edges(adj, colors_dict)
frust_tuples = set()
for fs in frust:
    lst = sorted(fs)
    frust_tuples.add((lst[0], lst[1]))

hop = np.load(os.path.join(OUT, "hop_matrix.npy"))
nh = np.load(os.path.join(OUT, "next_hop_table.npy"))
wd = np.load(os.path.join(OUT, "weighted_delay_matrix.npy"))

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg); dec = math.radians(dec_deg)
    return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1, v2 = radec_to_vec(ra1, dec1), radec_to_vec(ra2, dec2)
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

def path_between(s, t):
    """用 next-hop 表追蹤完整路徑."""
    path = [s]
    cur = s
    while cur != t and len(path) < 20:
        nxt = int(nh[cur, t])
        if nxt == cur or nxt in path:
            break
        path.append(nxt)
        cur = nxt
    if path[-1] != t:
        path.append(t)
    return path

def hop_distance(a, b):
    return int(hop[a, b])

def delay_cost(a, b):
    return float(wd[a, b])

def is_frust(a, b):
    return (min(a,b), max(a,b)) in frust_tuples

def edge_label(a, b):
    return "🔶 阻挫邊 (特快/高保真)" if is_frust(a, b) else "🔹 普通邊 (普通)"

# ============================================================
# 地標 (同 19 號腳本)
# ============================================================
LANDMARKS = [
    ("大冷斑 (CMB)", 48.30, -20.44),
    ("冷斑對跖點", 228.30, 20.44),
    ("仙女座星系 M31", 10.68, 41.27),
    ("M87 室女A", 187.71, 12.39),
    ("M104 草帽星系", 189.99, -11.62),
    ("M81 波德星系", 148.89, 69.07),
    ("獵戶座大星雲 M42", 83.82, -5.39),
    ("蟹狀星雲 M1", 83.63, 22.01),
    ("銀河系中心 Sgr A*", 266.42, -29.01),
    ("昴星團 M45", 56.87, 24.11),
    ("英仙座星系團", 49.95, 41.51),
    ("獅子座星系團", 168.10, 21.00),
    ("北冕座星系團", 232.20, 26.00),
    ("武仙座星系團", 241.10, 17.72),
    ("大麥哲倫星雲 LMC", 80.89, -69.76),
    ("小麥哲倫星雲 SMC", 13.19, -72.83),
    ("三角座星系 M33", 23.46, 30.66),
    ("室女座星系團", 187.70, 12.39),
    ("後髮座星系團", 194.90, 27.98),
    ("銀河南極", 12.86, -27.13),
    ("銀河北極", 192.86, 27.13),
    ("半人馬座ω星團", 201.70, -47.48),
    ("船底座η星雲", 161.26, -59.69),
    ("波江座空洞", 30.00, -45.00),
    ("牧夫座空洞", 218.00, 35.00),
]

def nearest_landmark(ra, dec):
    best = None
    for name, lra, ldec in LANDMARKS:
        d = ang_deg_between(ra, dec, lra, ldec)
        if best is None or d < best[0]:
            best = (d, name)
    return best

def landmark_for(i):
    ra, dec = nodes[i]
    d, name = nearest_landmark(ra, dec)
    return name, d

def nearest_landmark_safe(ra, dec):
    res = nearest_landmark(ra, dec)
    if res is None:
        return 999.0, "未知天區"
    return res

# ============================================================
# 主輸出
# ============================================================
L = []
L.append("=" * 80)
L.append("  宇宙晶網公交指南 (Cosmic Transit Guide)")
L.append("  點搭「宇宙地鐵」— 完整使用教學")
L.append("=" * 80)
L.append("")
L.append("  本指南適合完全冇物理背景嘅普通人。")
L.append("  你只需要識: 上車、轉車、落車。")
L.append("")

# ── 第一課 ──
L.append("─" * 80)
L.append("  第一課: 宇宙係一張網 (唔係太空)")
L.append("─" * 80)
L.append("")
L.append("  想像成個宇宙係一張 60 個站嘅地鐵網:")
L.append("")
L.append("    • 60 個「站」(節點) = 宇宙晶網嘅交叉點")
L.append("    • 120 條「路線」(邊) = 站與站之間嘅連接")
L.append("    • 32 條「特快線」(阻挫邊) = 高保真快線 (貴少少但品質好)")
L.append("    • 88 條「普通線」(正常邊) = 標準路線")
L.append("")
L.append("  每個站都係一個「路由器」, 唔係一個星球。")
L.append("  你唔係「飛去」第二個站 — 你係「跳」過去。")
L.append("")
L.append("  🚇 地鐵比喻:")
L.append("    香港站 → 九龍站 = 1 個站距 (1 hop)")
L.append("    香港站 → 銅鑼灣 = 2 個站距 (2 hops)")
L.append("    最遠兩個站 = 8 個站距 (8 hops) = 宇宙直徑")
L.append("")

# ── 第二課 ──
L.append("─" * 80)
L.append("  第二課: 點樣搭車 (3 步)")
L.append("─" * 80)
L.append("")
L.append("  搭車三步曲:")
L.append("")
L.append("  ① 搵你最近嘅站 (定位)")
L.append("     打開星圖, 搵你所在方向最近嘅 A5 節點。")
L.append("     例: 地球喺銀河系 → 最近站 = node 21 (銀河系中心附近, 23.1°)")
L.append("     或者用冷斑做錨: 你喺冷斑 (node 0) 幾遠, 就知你喺邊個站。")
L.append("")
L.append("  ② 睇路線圖 (路由表)")
L.append("     查「hop_matrix」: 你嘅站 → 目的地站要跳幾多下。")
L.append("     查「next_hop_table」: 第一下跳去邊個站。")
L.append("     呢兩張表就係宇宙地鐵圖。")
L.append("")
L.append("  ③ 上車跳 (執行路由)")
L.append("     由你嘅站, 按 next-hop 指示逐站跳。")
L.append("     每一跳 = 將你嘅訊號頻率調整到下一站嘅共振頻率。")
L.append("     唔係開太空船飛 — 係「調頻」跳過去。")
L.append("")

# ── 第三課 ──
L.append("─" * 80)
L.append("  第三課: 車資 (成本) 同車程 (時間)")
L.append("─" * 80)
L.append("")
L.append("  每一跳都要「俾錢」(能量):")
L.append("")
L.append("  基本車資 = 每跳 1 單位 (hop)")
L.append("  加權車資 = 用「weighted_delay_matrix」(考慮訊號品質)")
L.append("")
L.append("  車資對照表:")
L.append("    普通邊 (88 條):  每跳成本 1.0")
L.append("    特快邊 (32 條):  每跳成本 1.0 但品質更高 (保真度↑)")
L.append("")
L.append("  實際車資例子:")
L.append("    冷斑 (node 0) → 最近站 (1 跳):    車資 1 單位")
L.append("    冷斑 (node 0) → M87 (6 跳):       車資 6 單位")
L.append("    冷斑 (node 0) → 對跖 (8 跳):      車資 8 單位 (全程最貴)")
L.append("")
L.append("  車程 = 每一跳嘅「同步時間」(同步到下一站嘅共振)")
L.append("  加權車程 = weighted_delay_matrix 嘅值 (0.0 - 5.47)")
L.append("  冷斑 → 對跖: 車程 5.47 單位 (最長)")
L.append("")

# ── 第四課 ──
L.append("─" * 80)
L.append("  第四課: 班次 (K_Chain 頻道 = 44 條線)")
L.append("─" * 80)
L.append("")
L.append("  每個站有 44 條「月台」(頻道), 每條頻道係一個 mode:")
L.append("")
L.append("  ┌────────┬──────────────────┬──────────────────┐")
L.append("  │ 頻道   │ 波長             │ 用途             │")
L.append("  ├────────┼──────────────────┼──────────────────┤")
L.append("  │ mode 1 │ 4129.94 Mpc      │ 全宇宙長途       │")
L.append("  │ mode 11│ 375.45 Mpc       │ BAO 星系團通信   │")
L.append("  │ mode 22│ 187.72 Mpc       │ 中距 (v_g=0.71c) │")
L.append("  │ mode 44│ 93.86 Mpc        │ Nyquist 駐波     │")
L.append("  └────────┴──────────────────┴──────────────────┘")
L.append("")
L.append("  點揀頻道:")
L.append("    長途 (跨宇宙):  用 mode 1 (最遠覆蓋)")
L.append("    中距 (星系團):  用 mode 11 (BAO 尺度)")
L.append("    本地駐波:       用 mode 44 (Nyquist, v_g=0)")
L.append("")
L.append("  轉頻道 = 轉月台 = 唔使落車, 直接調頻就得。")
L.append("")

# ── 第五課 ──
L.append("─" * 80)
L.append("  第五課: 規矩 (路由規則)")
L.append("─" * 80)
L.append("")
L.append("  1️⃣ 最短路徑原則: 永遠行最少跳數嘅路 (hop_matrix)")
L.append("  2️⃣ 唔准走回頭路: 每一跳嘅距離必須遞減 (next-hop 保證)")
L.append("  3️⃣ 特快線優先 (可選): 如果要高保真, 揀阻挫邊多嘅路")
L.append("  4️⃣ 頻道守則: 訊號必須用目的地可接收嘅頻道 (mode)")
L.append("  5️⃣ 對跖點限制: 最遠只可以去 8 跳, 冇得再遠 (宇宙直徑)")
L.append("  6️⃣ 冷斑錨定: 所有路由以冷斑 (node 0) 做參考點")
L.append("")

# ── 第六課: 完整教學範例 ──
L.append("─" * 80)
L.append("  第六課: 完整教學 — 由地球去 M87")
L.append("─" * 80)
L.append("")
L.append("  🎯 目的地: M87 星系 (室女座, 距離 5,500 萬光年)")
L.append("")
L.append("  步驟 1: 搵你嘅站")
L.append("    地球喺銀河系, 最近站 = node 21 (銀河系中心 Sgr A*, 23.1°)")
L.append("    你嘅出發站 = node 21")
L.append("")
L.append("  步驟 2: 搵目的地嘅站")
L.append("    M87 (RA 187.7°, Dec 12.4°) 最近站 = node 7 (距離 3.3°)")
L.append("    目的地站 = node 7")
L.append("")
L.append("  步驟 3: 查路線圖")
L.append("    hop_matrix[21, 7] = 幾多跳? 等我查:")
L.append("")

# 查實際路徑
s, t = 21, 7
h = hop_distance(s, t)
p = path_between(s, t)
cost = delay_cost(s, t)
L.append(f"    → node 21 → node 7 要跳 {h} 下")
L.append(f"    路徑: {' → '.join(str(x) for x in p)}")
L.append(f"    車資: {h} 單位 | 加權車資: {cost:.2f}")
L.append("")
L.append("  步驟 4: 上車 (逐站跳)")
for k in range(len(p) - 1):
    a, b = p[k], p[k + 1]
    la, _ = landmark_for(a)
    lb, _ = landmark_for(b)
    L.append(f"    跳 {k+1}: 站 {a} ({la}) → 站 {b} ({lb})  [{edge_label(a, b)}]")
L.append("")
L.append("  步驟 5: 揀頻道")
L.append("    中距 (星系團尺度) → 用 mode 11 (BAO 375 Mpc)")
L.append("    訊號用 mode 11 由 node 21 傳去 node 7")
L.append("")
L.append("  步驟 6: 落車")
L.append("    到達 node 7, 對準 M87 方向 (3.3° 內)")
L.append("    完成! 你已經「傳送」咗一個訊號去 M87 🎉")
L.append("")

# ── 第七課 ──
L.append("─" * 80)
L.append("  第七課: 常用路線表 (冷斑出發)")
L.append("─" * 80)
L.append("")
L.append("  由冷斑 (node 0) 出發嘅常用目的地:")
L.append("")
L.append(f"  {'目的地':<20} {'站':>4} {'跳數':>4} {'車資':>6} {'加權':>6}  路線")
L.append(f"  {'----':<20} {'--':>4} {'--':>4} {'--':>6} {'--':>6}  ----")
for dest, label in [(1, "仙女座 M31"), (7, "M87 室女A"), (4, "M81 波德星系"),
                    (9, "獵戶座星雲"), (21, "銀河系中心"), (27, "昴星團"),
                    (12, "蟹狀星雲"), (36, "三角座 M33"), (57, "北冕座星系團")]:
    h = hop_distance(0, dest)
    c = delay_cost(0, dest)
    p = path_between(0, dest)
    route = "→".join(str(x) for x in p)
    L.append(f"  {label:<20} {dest:>4} {h:>4} {h:>6} {c:>6.2f}  {route}")
L.append("")
L.append("  車資解釋: 「跳數」= 基本車資 (每跳 1 單位),「加權」= 考慮訊號品質後嘅實際成本。")
L.append("")

# ── 第八課 ──
L.append("─" * 80)
L.append("  第八課: 新手常見問題 FAQ")
L.append("─" * 80)
L.append("")
L.append("  Q1: 我可唔可以跳去宇宙外面?")
L.append("  A1: 唔可以。宇宙晶網得 60 個站, 最遠 8 跳。冇「外面」。")
L.append("")
L.append("  Q2: 點解要跳, 唔直接飛過去?")
L.append("  A2: 宇宙係網絡, 唔係連續空間。「飛」喺晶網冇意義 — 你只可以沿住路線跳。")
L.append("      呢個就係「曲速」嘅真相: 唔係超光速飛行, 係網絡跳躍。")
L.append("")
L.append("  Q3: 跳一下要幾耐?")
L.append("  A3: 每一跳係「共振同步」, 理論上係即時 (W-field 同步模式)。")
L.append("      但能量成本係真嘅: 每跳都要消耗能量去調頻。")
L.append("")
L.append("  Q4: 點解有啲邊叫「阻挫邊」?")
L.append("  A4: 阻挫邊連接兩個「同色」節點 (冷-冷或熱-熱), 係晶體嘅「缺陷」。")
L.append("      物理上係應力集中, 但通信上係「特快線」— 高保真, 干擾少。")
L.append("")
L.append("  Q5: 我喺地球, 點知自己喺邊個站?")
L.append("  A5: 地球喺銀河系旋臂, 距離銀河系中心 (node 21 附近) 約 26,000 光年。")
L.append("      最近站 = node 21 (23.1°) 或 node 45 (8.9°)。用天文定位就搵到。")
L.append("")
L.append("  Q6: 係咪任何兩個站都可以通?")
L.append("  A6: 係。60 個站全部連通 (connected graph), 任何兩站之間都有一條路。")
L.append("      最遠 8 跳, 一定到。")
L.append("")
L.append("  Q7: 有冇 express 車?")
L.append("  A7: 有。32 條阻挫邊就係特快線 (高保真)。")
L.append("      但佢哋唔一定快啲 (跳數一樣), 係品質好啲 (訊號失真少)。")
L.append("")

# ── 附錄 ──
L.append("─" * 80)
L.append("  附錄: 名詞對照表")
L.append("─" * 80)
L.append("")
L.append("  A5 晶網     = 宇宙地鐵網 (60 站, 120 線)")
L.append("  節點 (Node) = 車站 (路由器)")
L.append("  邊 (Edge)   = 路線 (兩個站之間嘅連接)")
L.append("  阻挫邊      = 特快線 (高保真)")
L.append("  Hop         = 站距 (跳一下)")
L.append("  hop_matrix  = 路線圖 (任何兩站之間要跳幾多下)")
L.append("  next-hop    = 下一站指示 (第一下跳去邊)")
L.append("  weighted_delay = 車程表 (考慮品質嘅實際成本)")
L.append("  K_Chain     = 頻道系統 (44 條月台)")
L.append("  Mode        = 頻道 (月台號碼)")
L.append("  W-field     = 地鐵系統本身 (宇宙嘅資訊網絡)")
L.append("  曲速 (Warp) = 網絡跳躍 (唔係超光速飛行)")
L.append("  冷斑        = 總站 (node 0, 宇宙路由 root)")
L.append("  對跖點      = 最遠站 (node 57, 8 跳)")
L.append("")

text = "\n".join(L)
with open(os.path.join(OUT, "cosmic_transit_guide.txt"), "w") as f:
    f.write(text + "\n")
print(text)
print(f"\n✅ 已儲存: data/cosmic_transit_guide.txt")
