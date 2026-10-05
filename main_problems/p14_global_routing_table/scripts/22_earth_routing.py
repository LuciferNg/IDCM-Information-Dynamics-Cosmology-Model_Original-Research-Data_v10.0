#!/usr/bin/env python3
"""GRT-22: 地球內路由列表 — 城市/天文台 ↔ A5 節點接駁表.

原理:
  A5 節點喺天球上有固定 RA/Dec (ICRS).
  地球自轉 → 觀察者嘅天頂每日掃過 RA 360°.
  → 每個地球位置每日會「路過」一系列 A5 節點.

應用:
  1. 每個城市/天文台 24 小時可見節點清單
  2. 城市對共享可視節點 = 同步通信窗口 (中繼站)
  3. 天頂節點 = 該位置嘅「主路由節點」

可測試性:
  - 用 astropy 計 LST + 高度角, 獨立驗證
  - 用 Stellarium / 天文軟件 cross-check
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes

OUT = "../data"
nodes, vecs = load_nodes()

# ============================================================
# 地球位置目錄 (城市 + 天文台 + 射電望遠鏡)
# ============================================================
EARTH_SITES = [
    # (名稱, 類型, 緯度, 經度)
    ("香港",                "城市",  22.32, 114.17),
    ("東京",                "城市",  35.68, 139.69),
    ("新加坡",              "城市",   1.35, 103.82),
    ("倫敦",                "城市",  51.51,  -0.13),
    ("紐約",                "城市",  40.71, -74.01),
    ("雪梨",                "城市", -33.87, 151.21),
    ("開普敦",              "城市", -33.92,  18.42),
    ("聖地牙哥 (智利)",       "城市", -33.45, -70.67),
    ("北京",                "城市",  39.90, 116.41),
    ("莫斯科",              "城市",  55.76,  37.62),
    ("FAST 天眼 (貴州)",     "射電望遠鏡", 25.65, 106.86),
    ("Arecibo (波多黎各)",   "射電望遠鏡", 18.34, -66.75),
    ("Green Bank (西維州)", "射電望遠鏡", 38.43, -79.84),
    ("ALMA (智利阿塔卡馬)",  "射電望遠鏡", -23.03, -67.75),
    ("VLA (新墨西哥)",       "射電望遠鏡", 34.08, -107.62),
    ("Keck (夏威夷)",        "光學望遠鏡", 19.83, -155.47),
    ("VLT (智利帕瑞納)",     "光學望遠鏡", -24.63, -70.40),
    ("Subaru (夏威夷)",      "光學望遠鏡", 19.83, -155.48),
    ("南極點 (Amundsen-Scott)", "觀測站", -90.00, 0.00),
    ("北極點",              "座標",  90.00, 0.00),
    ("格林威治天文台",        "天文台", 51.48, 0.00),
    ("北京興隆觀測站",        "天文台", 40.40, 117.58),
]

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg); dec = math.radians(dec_deg)
    return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1, v2 = radec_to_vec(ra1, dec1), radec_to_vec(ra2, dec2)
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

def alt_angle(lat_deg, node_ra, node_dec, lst_deg):
    """節點高度角 (仰角). LST = 地方恆星時 (度, 0-360)."""
    lat = math.radians(lat_deg)
    dec = math.radians(node_dec)
    ha = math.radians((lst_deg - node_ra) % 360)  # 時角
    sin_alt = (math.sin(lat)*math.sin(dec) +
               math.cos(lat)*math.cos(dec)*math.cos(ha))
    return math.degrees(math.asin(max(-1, min(1, sin_alt))))

def nearest_node(ra, dec):
    best = None
    for i, (nra, ndec) in enumerate(nodes):
        d = ang_deg_between(ra, dec, nra, ndec)
        if best is None or d < best[0]:
            best = (d, i)
    return best if best is not None else (999.0, -1)

# 天頂 (zenith) = Dec = 緯度, RA = LST
# 全天頂掃描: 將 LST 由 0 行到 360 (24h), 搵每個節點嘅最大高度角
def site_node_visibility(lat_deg):
    """每個節點喺該緯度嘅全日最大高度角."""
    vis = []
    for i, (nra, ndec) in enumerate(nodes):
        # 最大高度角 = 90 - |lat - dec| (節點上中天)
        max_alt = 90.0 - abs(lat_deg - ndec)
        # 上中天時嘅 LST
        transit_lst = nra
        vis.append((max_alt, i, nra, ndec, transit_lst))
    vis.sort(reverse=True)
    return vis

L = []
L.append("=" * 82)
L.append("  地球內路由列表 — 城市/天文台 ↔ A5 節點接駁表")
L.append("  你企喺地球邊度, 就由邊個節點「接你上車」")
L.append("=" * 82)
L.append("")
L.append("  原理:")
L.append("    地球自轉 → 你嘅天頂每日掃過天球一圈")
L.append("    A5 節點喺天球有固定位置 → 每日會路過你頭頂")
L.append("    「接駁節點」= 你嗰刻天頂最近嘅節點")
L.append("")
L.append("  點讀下表:")
L.append("    主節點   = 你嘅位置全天最高嘅節點 (緯度決定)")
L.append("    可見清單 = 高度角 > 30° 嘅節點 (可以通信)")
L.append("    過境時間 = 節點上中天 (最高點) 嘅地方恆星時")
L.append("")

# ── 一、每個位置嘅主節點 + 可見節點 ──
L.append("─" * 82)
L.append("  一、22 個地球位置嘅 A5 接駁表")
L.append("─" * 82)
L.append("")
L.append(f"  {'位置':<24} {'緯度':>7} {'經度':>8} {'主節點':>6} {'主節點高度':>9} {'可見節點數':>9}  主節點最近地標")
L.append(f"  {'----':<24} {'--':>7} {'--':>8} {'--':>6} {'----':>9} {'----':>9}  ----")

# 地標 (用 19 號腳本嘅表)
LANDMARKS = [
    ("大冷斑 (CMB)", 48.30, -20.44),
    ("M87 室女A", 187.71, 12.39),
    ("銀河系中心 Sgr A*", 266.42, -29.01),
    ("獵戶座大星雲 M42", 83.82, -5.39),
    ("仙女座星系 M31", 10.68, 41.27),
    ("昴星團 M45", 56.87, 24.11),
    ("M81 波德星系", 148.89, 69.07),
    ("英仙座星系團", 49.95, 41.51),
    ("北冕座星系團", 232.20, 26.00),
    ("船底座η星雲", 161.26, -59.69),
    ("大麥哲倫星雲 LMC", 80.89, -69.76),
    ("小麥哲倫星雲 SMC", 13.19, -72.83),
    ("半人馬座ω星團", 201.70, -47.48),
]

def landmark_for(ra, dec):
    best = None
    for name, lra, ldec in LANDMARKS:
        d = ang_deg_between(ra, dec, lra, ldec)
        if best is None or d < best[0]:
            best = (d, name)
    if best is None:
        return "未知"
    return best[1]

site_summary = []
for name, typ, lat, lon in EARTH_SITES:
    vis = site_node_visibility(lat)
    # 主節點 = 最高可見 (最大高度角)
    max_alt, main_i, main_ra, main_dec, transit = vis[0]
    visible = [v for v in vis if v[0] >= 30.0]
    n_vis = len(visible)
    lm = landmark_for(main_ra, main_dec)
    site_summary.append((name, typ, lat, lon, main_i, max_alt, n_vis, lm, visible))
    L.append(f"  {name:<24} {lat:>7.1f} {lon:>8.1f} {main_i:>6} {max_alt:>8.1f}° {n_vis:>9}  {lm}")

L.append("")
L.append("  主節點高度 90° = 節點正正喺你頭頂 (緯度等於節點 Dec)")
L.append("  可見節點數 = 全日至少有一次高度角 > 30° 嘅節點")
L.append("")

# ── 二、主要城市 24h 節點掃描 ──
L.append("─" * 82)
L.append("  二、24 小時節點路過序列 (城市範例)")
L.append("─" * 82)
L.append("")
L.append("  地球自轉 → 天頂 RA 每小時行 15°")
L.append("  下面列出每個城市 24 小時內路過頭頂 (±30°) 嘅節點:")
L.append("")

def site_hourly_scan(lat, lon):
    """模擬 24 小時: LST 由 0 行到 360, 每小時記低可見節點."""
    hourly = []
    for h in range(24):
        lst = (lon + h * 15) % 360  # 近似 LST (忽略恒星日差)
        visible_now = []
        for i, (nra, ndec) in enumerate(nodes):
            alt = alt_angle(lat, nra, ndec, lst)
            if alt >= 30:
                visible_now.append((alt, i))
        visible_now.sort(reverse=True)
        if visible_now:
            top = visible_now[0]
            hourly.append((h, lst, top[1], top[0]))
    return hourly

for city_name in ["香港", "倫敦", "雪梨", "聖地牙哥 (智利)"]:
    site = next(s for s in EARTH_SITES if s[0] == city_name)
    name, typ, lat, lon = site
    scan = site_hourly_scan(lat, lon)
    L.append(f"  🏙 {name} (緯 {lat}°, 經 {lon}°):")
    L.append(f"    {'小時':>4} {'LST':>6} {'頂點節點':>8} {'高度':>6}  備註")
    last_main = None
    for h, lst, ni, alt in scan:
        note = ""
        if ni != last_main:
            note = f"← 切換到 node {ni}"
            last_main = ni
        L.append(f"    {h:>4} {lst:>6.0f}° {ni:>8} {alt:>5.1f}°  {note}")
    L.append("")

# ── 三、城市對共享節點 (通信窗口) ──
L.append("─" * 82)
L.append("  三、城市對共享可視節點 — 同步通信窗口")
L.append("─" * 82)
L.append("")
L.append("  兩個城市同時睇到同一個節點 = 可以用嗰個節點做中繼")
L.append("  共享節點數 = 同步通信嘅可能性")
L.append("")
L.append(f"  {'城市 A':<18} {'城市 B':<18} {'共享節點':>8} {'共同可見時段':>10}  最佳中繼節點")
L.append(f"  {'----':<18} {'----':<18} {'----':>8} {'----':>10}  ----")

# 城市對 (香港 vs 其他)
cities = ["香港", "東京", "新加坡", "倫敦", "紐約", "雪梨", "開普敦", "聖地牙哥 (智利)"]
site_map = {s[0]: s for s in EARTH_SITES}

def site_visible_nodes(lat):
    vis = site_node_visibility(lat)
    return set(v[1] for v in vis if v[0] >= 30.0)

def common_view_window(lat1, lon1, lat2, lon2, node_ra):
    """兩個位置同時可見某節點嘅 LST 範圍 (度)."""
    # 每個位置: 高度角 > 30 嘅 LST 範圍
    def alt_lst_range(lat, ra):
        # sin(alt) >= sin(30) = 0.5
        # sin(lat)sin(dec) + cos(lat)cos(dec)cos(HA) >= 0.5
        dec = None
        for i, (nra, ndec) in enumerate(nodes):
            if abs(nra - node_ra) < 0.01 or abs(nra - node_ra - 360) < 0.01:
                dec = ndec
                break
        if dec is None:
            # 用近似: 由節點 RA 直接計
            dec = node_ra  # placeholder, 唔會到
        lat_r, dec_r = math.radians(lat), math.radians(dec)
        cos_ha_min = (0.5 - math.sin(lat_r)*math.sin(dec_r)) / (math.cos(lat_r)*math.cos(dec_r))
        cos_ha_min = max(-1, min(1, cos_ha_min))
        ha_half = math.degrees(math.acos(cos_ha_min))
        # LST range: node_ra ± ha_half
        return (node_ra - ha_half, node_ra + ha_half)
    return None  # 用另一方法

# 用時間網格計共同可見
def common_visible_time(lat1, lon1, lat2, lon2, node_idx, node_ra, node_dec):
    """兩個位置喺 24h 內同時可見 node 嘅時長 (小時)."""
    t_common = 0
    for lst in np.arange(0, 360, 1):  # 1° 步長 = 4 分鐘
        alt1 = alt_angle(lat1, node_ra, node_dec, lst)
        alt2 = alt_angle(lat2, node_ra, node_dec, lst)
        if alt1 >= 30 and alt2 >= 30:
            t_common += 1
    return t_common / 15.0  # 1° = 4 min = 1/15 h

# 城市對
city_pairs = []
for i in range(len(cities)):
    for j in range(i+1, len(cities)):
        city_pairs.append((cities[i], cities[j]))

for ca, cb in city_pairs[:14]:
    sa, sb = site_map[ca], site_map[cb]
    lat1, lon1, lat2, lon2 = sa[2], sa[3], sb[2], sb[3]
    vis_a = site_visible_nodes(lat1)
    vis_b = site_visible_nodes(lat2)
    shared = vis_a & vis_b
    if not shared:
        L.append(f"  {ca:<18} {cb:<18} {'0':>8} {'—':>10}  (冇共享節點)")
        continue
    # 最佳中繼 = 共同可見時間最長
    best = None
    for ni in shared:
        nra, ndec = nodes[ni]
        t = common_visible_time(lat1, lon1, lat2, lon2, ni, nra, ndec)
        if best is None or t > best[0]:
            best = (t, ni)
    t_best, ni_best = best
    lm = landmark_for(nodes[ni_best][0], nodes[ni_best][1])
    L.append(f"  {ca:<18} {cb:<18} {len(shared):>8} {t_best:>9.1f}h  node {ni_best} ({lm})")

L.append("")
L.append("  共同可見時長 = 兩個城市每日可以透過該節點同步通信嘅時間")
L.append("  呢個就係地球內「中繼路由」嘅基礎!")
L.append("")

text = "\n".join(L)
with open(os.path.join(OUT, "earth_routing_table.txt"), "w") as f:
    f.write(text + "\n")
print(text)
print(f"\n✅ 已儲存: data/earth_routing_table.txt")
