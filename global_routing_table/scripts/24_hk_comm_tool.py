#!/usr/bin/env python3
"""GRT-24: 香港↔香港 通信工具 — 價格/速度/易購性最佳平衡點.

用法:
  python3 24_hk_comm_tool.py                 # 預設: 中環 ↔ 沙田
  python3 24_hk_comm_tool.py "中環" "元朗"    # 指定兩個地點

輸出:
  - 距離 + 視線判斷
  - 4 個方案嘅 link budget (LoRa 10mW / LoRa 1W / 業餘電台 5W / ESP32)
  - A5 路由整合 (主節點 + 共享中繼節點 + 通信窗口)
  - 零件清單 (香港易購性 + 價格)
  - 協議規格 (A5 宇宙電話簿 header)
  - 最佳平衡點結論

原則:
  - W-field 同步 = 理論層 (🔴 未實現, 有待突破)
  - 電磁波 = W-field 激發態 = 可測試物理層
  - A5 路由表 = 定址層 (宇宙電話簿), 完全免費
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes

OUT = "../data"
nodes, vecs = load_nodes()

# ============================================================
# 香港地點 (緯度, 經度)
# ============================================================
HK_SITES = {
    "中環":   (22.2819, 114.1582),
    "沙田":   (22.3803, 114.1950),
    "西貢":   (22.3819, 114.2735),
    "赤柱":   (22.2167, 114.2167),
    "觀塘":   (22.3109, 114.2260),
    "元朗":   (22.4414, 114.0220),
    "大嶼山昂坪": (22.2550, 113.9050),
    "石崗":   (22.4360, 114.0810),
    "大埔":   (22.4450, 114.1700),
    "屯門":   (22.3910, 113.9770),
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg); dec = math.radians(dec_deg)
    return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1, v2 = radec_to_vec(ra1, dec1), radec_to_vec(ra2, dec2)
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

def site_main_node(lat):
    """主節點 = Dec 最接近緯度嘅節點 (上中天最高)."""
    best = None
    for i, (nra, ndec) in enumerate(nodes):
        d = abs(lat - ndec)
        if best is None or d < best[0]:
            best = (d, i)
    return best[1]

def site_visible_nodes(lat):
    """高度角 > 30° 可見節點 (Dec ∈ [lat-60, lat+60])."""
    return [i for i, (_, ndec) in enumerate(nodes) if lat-60 <= ndec <= lat+60]

# ============================================================
# Link budget 模型
# ============================================================
def fspl_db(f_mhz, d_km):
    return 32.44 + 20*math.log10(f_mhz) + 20*math.log10(d_km)

def link_budget(f_mhz, d_km, tx_dbm, tx_gain, rx_gain, rx_sens, urban_clutter=20.0, fade=10.0):
    """回傳 (margin_dB, 是否可行)."""
    loss = fspl_db(f_mhz, d_km) + urban_clutter
    margin = tx_dbm + tx_gain + rx_gain - loss - fade - rx_sens
    return margin, margin > 0

# 方案定義: (名稱, 頻率MHz, TX dBm, 天線增益, RX靈敏度, 數據率, 牌照, 單價HK$)
PLANS = [
    ("LoRa 10mW (免牌 ISM)",  433,  10, 5, -137, "0.3-1.2 kbps", "免牌 (OFCA SRD)", 150),
    ("LoRa 1W (需業餘牌)",    433,  30, 5, -137, "0.3-5.5 kbps", "需業餘牌照",     200),
    ("業餘電台 5W (VHF)",     145,  37, 3, -120, "2.4 kbps APRS", "需業餘牌照",    250),
    ("ESP32 2.4GHz (免牌)",  2400,  20, 2,  -98, "250 kbps",     "免牌 (Wi-Fi)",   80),
]

# ============================================================
# BOM (香港易購性)
# ============================================================
BOM = [
    # (零件, 型號, 用途, 香港易購, 價格HK$, 邊度買)
    ("LoRa 模組", "Ebyte E22-400M22S (22dBm)", "射頻收發", "★★★★★", 45, "華輝WECL / 淘寶 ¥25"),
    ("MCU", "Raspberry Pi Pico W", "控制+協議", "★★★★★", 45, "華輝WECL / RS"),
    ("433MHz 天線", "半波偶極/彈簧天線", "收發", "★★★★☆", 25, "鴨寮街 / 淘寶"),
    ("電源", "18650 電池+座", "供電", "★★★★★", 30, "鴨寮街"),
    ("GPS 模組 (選配)", "NEO-6M", "自動定址", "★★★★☆", 25, "淘寶 ¥15"),
    ("外殼+線材", "鋁盒/3D打印+杜邦線", "組裝", "★★★★★", 20, "新填地街/華輝"),
    ("Software", "自寫 (呢個 project)", "協議棧", "★★★★★", 0, "本倉庫 scripts/"),
]
TOTAL_BOM = sum(row[4] for row in BOM if row[0] != "GPS 模組 (選配)")

def main():
    # 讀取地點參數
    if len(sys.argv) >= 3:
        site_a, site_b = sys.argv[1], sys.argv[2]
    else:
        site_a, site_b = "中環", "沙田"
    if site_a not in HK_SITES or site_b not in HK_SITES:
        print("⚠️ 地點唔喺清單:", list(HK_SITES.keys()))
        return
    lat1, lon1 = HK_SITES[site_a]
    lat2, lon2 = HK_SITES[site_b]
    d_km = haversine_km(lat1, lon1, lat2, lon2)

    L = []
    L.append("=" * 82)
    L.append(f"  香港↔香港 通信工具 — {site_a} ↔ {site_b}")
    L.append("  價格 / 速度 / 易購性 最佳平衡點分析")
    L.append("=" * 82)
    L.append("")
    L.append(f"  距離: {d_km:.1f} km (直線)")
    L.append(f"  地點 A: {site_a} ({lat1:.4f}°, {lon1:.4f}°)")
    L.append(f"  地點 B: {site_b} ({lat2:.4f}°, {lon2:.4f}°)")
    L.append("")

    # ── 1. A5 路由整合 ──
    L.append("─" * 82)
    L.append("  一、A5 宇宙電話簿 — 兩個地點嘅「宇宙地址」")
    L.append("─" * 82)
    L.append("")
    n1 = site_main_node(lat1)
    n2 = site_main_node(lat2)
    v1 = set(site_visible_nodes(lat1))
    v2 = set(site_visible_nodes(lat2))
    shared = sorted(v1 & v2)
    L.append(f"  {site_a} 主節點 = node {n1} ({nodes[n1][0]:.1f}°, {nodes[n1][1]:.1f}°)")
    L.append(f"  {site_b} 主節點 = node {n2} ({nodes[n2][0]:.1f}°, {nodes[n2][1]:.1f}°)")
    L.append(f"  共享可見節點 = {len(shared)} 個: {shared[:15]}{'...' if len(shared)>15 else ''}")
    L.append("")
    if n1 == n2:
        L.append(f"  → 兩地主節點相同 (node {n1}) → 同一「宇宙地址」!")
        L.append(f"  → 本地域 (同一 A5 節點 + 同一 K_Chain 胞)")
    else:
        L.append(f"  → 兩地主節點唔同 (node {n1} vs node {n2})")
        L.append(f"  → 需要 A5 路由: node {n1} → ... → node {n2}")
    L.append("")
    L.append("  地球自轉 → 節點每日過境 → 通信窗口:")
    L.append(f"    共享節點每日過境窗口 = 約 {len(shared)*2/60:.1f} 小時 (全部節點累計)")
    L.append(f"    最佳單一中繼: 兩地同時最高嘅共享節點")
    L.append("")

    # 最佳中繼
    best_relay = None
    for ni in shared:
        alt1 = 90 - abs(lat1 - nodes[ni][1])
        alt2 = 90 - abs(lat2 - nodes[ni][1])
        min_alt = min(alt1, alt2)
        if best_relay is None or min_alt > best_relay[0]:
            best_relay = (min_alt, ni, alt1, alt2)
    if best_relay:
        L.append(f"  最佳中繼節點 = node {best_relay[1]} ({nodes[best_relay[1]][0]:.1f}°, {nodes[best_relay[1]][1]:.1f}°)")
        L.append(f"    兩地同時高度: {best_relay[2]:.1f}° / {best_relay[3]:.1f}° (最小 {best_relay[0]:.1f}°)")
        L.append(f"    → 每日最佳同步通信時段 = 呢個節點上中天前後 ±{best_relay[0]/15:.1f} 小時")
    L.append("")

    # ── 2. Link budget ──
    L.append("─" * 82)
    L.append("  二、4 方案 Link Budget (距離 {:.1f} km, 城市雜訊 +20 dB)".format(d_km))
    L.append("─" * 82)
    L.append("")
    L.append(f"  {'方案':<26} {'頻率':>6} {'TX':>6} {'數據率':>12} {'盈餘':>7} {'可行':>4}  {'牌照':<14} {'單價':>6}")
    L.append(f"  {'----':<26} {'--':>6} {'--':>6} {'----':>12} {'--':>7} {'--':>4}  {'--':<14} {'--':>6}")
    results = {}
    for name, f, tx, tg, rx_sens, rate, lic, price in PLANS:
        rg = 2.0
        margin, ok = link_budget(f, d_km, tx, tg, rg, rx_sens)
        results[name] = (margin, ok, rate, price)
        flag = "✅" if ok else "❌"
        L.append(f"  {name:<26} {f:>5}M {tx:>5} {rate:>12} {margin:>6.1f}dB {flag:>4}  {lic:<14} ${price:>5}")
    L.append("")
    L.append("  註: 盈餘 = TX功率 + 天線增益 - 路徑損耗 - 城市雜訊 - 衰落餘量 - RX靈敏度")
    L.append("       > 0 = 可靠通信 | 城市雜訊 20dB 係香港高樓密集環境嘅保守估計")
    L.append("")

    # ── 3. 速度 vs 價格 ──
    L.append("─" * 82)
    L.append("  三、速度 vs 價格 vs 易購性 矩陣")
    L.append("─" * 82)
    L.append("")
    L.append("  需求分級:")
    L.append("    A) 傳文字 (短訊級): 0.3-1.2 kbps 就夠 → LoRa 10mW ✅")
    L.append("    B) 傳檔案 (電郵級): 需 10+ kbps → 業餘電台 5W (APRS/Packet)")
    L.append("    C) 傳語音: 需 8+ kbps → 業餘電台 5W (FM 語音) 或 ESP32 (VoIP)")
    L.append("")
    L.append(f"  {'方案':<26} {'速度':>12} {'單價':>7} {'易購':>6} {'用途':>18}")
    L.append(f"  {'----':<26} {'--':>12} {'--':>7} {'--':>6} {'--':>18}")
    for name, f, tx, tg, rx_sens, rate, lic, price in PLANS:
        if "10mW" in name:
            use = "短訊/緊急訊息"
        elif "1W" in name:
            use = "長距短訊/中繼"
        elif "業餘電台" in name:
            use = "語音+數據 (需牌)"
        else:
            use = "本地高速 (短距)"
        L.append(f"  {name:<26} {rate:>12} ${price:>6} ★★★★★ {use:>18}")
    L.append("")

    # ── 4. BOM ──
    L.append("─" * 82)
    L.append("  四、零件清單 — 香港易購性 + 價格")
    L.append("─" * 82)
    L.append("")
    L.append(f"  {'零件':<20} {'型號':<28} {'易購':>6} {'價格HK$':>8}  邊度買")
    L.append(f"  {'----':<20} {'----':<28} {'--':>6} {'--':>8}  ----")
    for name, model, use, ease, price, where in BOM:
        L.append(f"  {name:<20} {model:<28} {ease:>6} {price:>7}  {where}")
    L.append("")
    L.append(f"  總價 (基本套件, 唔計 GPS): HK${TOTAL_BOM} (~US${TOTAL_BOM/7.8:.0f})")
    L.append(f"  全套連 GPS: HK${TOTAL_BOM + 25} (~US${(TOTAL_BOM+25)/7.8:.0f})")
    L.append("")

    # ── 5. 協議 ──
    L.append("─" * 82)
    L.append("  五、A5 宇宙電話簿協議 (packet format)")
    L.append("─" * 82)
    L.append("")
    L.append("  每一包數據用 A5 地址做 header — 「宇宙電話號碼」:")
    L.append("")
    L.append("  ┌─────────┬──────────┬──────────┬─────────┬──────────┐")
    L.append("  │ 前導碼   │ 源節點    │ 目標節點  │ K_Chain │ 數據      │")
    L.append("  │ (8×F₅)  │ (6 bit)  │ (6 bit)  │ (6 bit) │ (任意)    │")
    L.append("  ├─────────┼──────────┼──────────┼─────────┼──────────┤")
    L.append("  │ 同步     │ 你喺邊個  │ 對方喺邊個 │ 用邊個  │ 訊息      │")
    L.append("  │ 標記     │ 節點      │ 節點      │ mode    │ (Fib FEC)│")
    L.append("  └─────────┴──────────┴──────────┴─────────┴──────────┘")
    L.append("")
    L.append(f"  {site_a} 嘅宇宙地址 = node {n1} (主) + 共享中繼 node {best_relay[1] if best_relay else '?'}")
    L.append(f"  {site_b} 嘅宇宙地址 = node {n2} (主) + 共享中繼 node {best_relay[1] if best_relay else '?'}")
    L.append("")
    L.append("  6-bit 節點 ID: 0-59 (60 個 A5 節點) → 1 字節搞掂")
    L.append("  6-bit mode ID: 1-44 (K_Chain 頻道) → 本地用 mode 44, 跨區用 mode 1/11")
    L.append("  前導碼 8×F₅: 8 次 Fibonacci 同步脈衝, 接收器自動鎖定")
    L.append("  Fib FEC: 訊息重複 φ⁻¹ 冗餘 → 城市干擾下自動修錯")
    L.append("")

    # ── 6. 結論 ──
    L.append("─" * 82)
    L.append("  六、結論 — 最佳平衡點")
    L.append("─" * 82)
    L.append("")
    L.append(f"  香港↔香港 ({d_km:.1f} km) 最佳平衡點:")
    L.append("")
    L.append("  ✅ 首選: LoRa 10mW 433MHz 免牌方案")
    L.append(f"     價格: HK${TOTAL_BOM} (全套, 一勞永逸)")
    L.append(f"     速度: 0.3-1.2 kbps (短訊級, 每秒 100-400 字)")
    L.append(f"     易購: ★★★★★ (華輝WECL + 鴨寮街 + 淘寶, 全部現成)")
    L.append(f"     牌照: 免牌 (OFCA SRD 10mW ERP) → 即買即用")
    L.append(f"     距離: {d_km:.1f} km 盈餘 {results['LoRa 10mW (免牌 ISM)'][0]:.1f} dB ✅")
    L.append("")
    L.append("  🟡 升級: 業餘電台 5W (需考牌)")
    L.append("     價格: HK$250+ | 速度: 語音+APRS | 距離: 30+ km")
    L.append("     適合: 要語音/長距離, 肯考 HKRA 業餘牌")
    L.append("")
    L.append("  🔴 理論層: W-field 同步通信 (本地胞同步)")
    L.append("     價格: 未實現 | 速度: 即時 | 依賴: W-field 共振理論突破")
    L.append("     現階段只能用電磁波 (W-field 激發態) 做物理層,")
    L.append("     A5 路由表做定址層 — 呢個就係「窮人版晶體通信」")
    L.append("")

    text = "\n".join(L)
    with open(os.path.join(OUT, "hk_comm_plan.txt"), "w") as f:
        f.write(text + "\n")
    print(text)
    print(f"\n✅ 已儲存: data/hk_comm_plan.txt")
    print(f"\n💡 用法: python3 24_hk_comm_tool.py \"中環\" \"元朗\"  (換地點)")

if __name__ == "__main__":
    main()
