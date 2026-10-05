#!/usr/bin/env python3
"""GRT-21: 銀河系內路由分析 — 城市入面點行?

問題: 宇宙公交指南講咗星系際 (A5 節點間) 路由,
      但銀河系入面 (恆星/星雲/黑洞之間) 點算?

關鍵 insight:
  銀河系直徑 ~10萬光年 = 0.031 Mpc
  λ_sync = 294.88 Mpc (K_Chain 同步尺度)
  → 成個銀河系係 K_Chain「一個胞」入面!
  → 銀河系內 = 本地域 (同一 K_Chain 胞) = 唔使跳 A5!

結構:
  1. 銀河系內天體目錄 + 最近 A5 節點
  2. 物理距離 vs 角距離 (關鍵: 唔同!)
  3. 銀河系 = 一個 K_Chain 胞 嘅證明
  4. 銀河系內通信 = 本地域 (同一胞內同步)
  5. 太陽系運動對節點歸屬嘅影響
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes

OUT = "../data"
nodes, vecs = load_nodes()

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg); dec = math.radians(dec_deg)
    return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1, v2 = radec_to_vec(ra1, dec1), radec_to_vec(ra2, dec2)
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

def nearest_node(ra, dec):
    best = None
    for i, (nra, ndec) in enumerate(nodes):
        d = ang_deg_between(ra, dec, nra, ndec)
        if best is None or d < best[0]:
            best = (d, i)
    return best if best is not None else (999.0, -1)

# ============================================================
# 銀河系內天體目錄 (RA, Dec, 物理距離光年, 類型)
# ============================================================
GALACTIC = [
    ("太陽系 (地球)",        None, None,  0,    "本地"),
    ("銀河系中心 Sgr A*",    266.42, -29.01, 26000, "超大質量黑洞"),
    ("半人馬座α (南門二)",   219.90, -60.83, 4.37, "恆星 (最近)"),
    ("巴納德星",             269.45, 4.67,  6.0,  "恆星 (第二近)"),
    ("天狼星",               101.29, -16.72, 8.6,  "恆星"),
    ("織女星",               279.23, 38.78,  25,   "恆星"),
    ("參宿四 (獵戶臂)",      88.79,  7.41,  640,  "紅超巨星"),
    ("心宿二",               247.35, -26.43, 550,  "紅超巨星"),
    ("獵戶座大星雲 M42",     83.82,  -5.39,  1344, "恆星形成區"),
    ("昴星團 M45",           56.87,  24.11,  444,  "疏散星團"),
    ("蟹狀星雲 M1",          83.63,  22.01,  6500, "超新星遺跡"),
    ("船底座η星雲",          161.26, -59.69, 7500, "恆星形成區"),
    ("M8 瀉湖星雲",          270.96, -24.38, 4100, "恆星形成區"),
    ("M16 鷹狀星雲",         274.70, -13.81, 7000, "恆星形成區"),
    ("M17 奧米加星雲",       275.20, -16.17, 5500, "恆星形成區"),
    ("半人馬座ω星團",        201.70, -47.48, 15800, "球狀星團"),
    ("大麥哲倫星雲 LMC",     80.89,  -69.76, 160000, "衛星星系"),
    ("小麥哲倫星雲 SMC",     13.19,  -72.83, 200000, "衛星星系"),
]

L = []
L.append("=" * 78)
L.append("  銀河系內路由指南 — 城市入面點行?")
L.append("=" * 78)
L.append("")
L.append("  宇宙公交指南講咗「跨城」(星系際) 點搭地鐵。")
L.append("  但銀河系入面 (恆星之間) 點算? 等我話你知:")
L.append("")

# ── 1. 關鍵尺度對比 ──
L.append("─" * 78)
L.append("  一、關鍵 insight: 銀河系係「一個站」嘅入面")
L.append("─" * 78)
L.append("")
MILKY_WAY_LY = 100000   # 銀河系直徑 10 萬光年
LY_TO_MPC = 1 / 3.26e6   # 1 ly = 3.086e-7 Mpc
mw_mpc = MILKY_WAY_LY * LY_TO_MPC
lam_sync = 294.88  # Mpc
ratio = lam_sync / mw_mpc
L.append(f"  銀河系直徑:  {MILKY_WAY_LY:,} 光年 = {mw_mpc:.4f} Mpc")
L.append(f"  K_Chain 同步尺度 λ_sync: {lam_sync} Mpc")
L.append(f"  比例: λ_sync / 銀河系 = {ratio:,.0f}")
L.append("")
L.append(f"  → 銀河系比起 λ_sync 細 {ratio:,.0f} 倍!")
L.append("  → 成個銀河系係 K_Chain「一個胞」入面")
L.append("  → 銀河系內所有點都係「本地」→ 唔使跳 A5 節點")
L.append("")
L.append("  🚇 地鐵比喻:")
L.append("     A5 節點 = 地鐵站 (城際/星系際)")
L.append("     銀河系   = 一個城市 (中環站嘅入面)")
L.append("     城入面行路/搭巴士就得, 唔使上地鐵!")
L.append("")

# ── 2. 天體投影 ──
L.append("─" * 78)
L.append("  二、銀河系內天體 → 最近 A5 節點 (投影)")
L.append("─" * 78)
L.append("")
L.append("  (注意: 呢個係「方向投影」, 唔係「位置」)")
L.append("  (天體喺銀河系內物理好近, 但方向可以差好遠)")
L.append("")
L.append(f"  {'天體':<26} {'RA':>7} {'Dec':>7} {'最近節點':>8} {'距離':>6}  {'物理距離':>9}  備註")
L.append(f"  {'----':<26} {'--':>7} {'---':>7} {'----':>8} {'--':>6}  {'----':>9}  ----")
for name, ra, dec, dist_ly, typ in GALACTIC:
    if ra is None:
        continue
    d, ni = nearest_node(ra, dec)
    dist_str = f"{dist_ly:,} ly" if dist_ly > 0 else "本地"
    note = "銀道面" if abs(dec) < 30 else ("高銀緯" if abs(dec) > 60 else "")
    L.append(f"  {name:<26} {ra:>7.1f} {dec:>7.1f} {ni:>8} {d:>5.1f}°  {dist_str:>9}  {note}")
L.append("")

# ── 3. 物理 vs 角距離 ──
L.append("─" * 78)
L.append("  三、物理距離 vs 角距離 — 點解唔一樣?")
L.append("─" * 78)
L.append("")
L.append("  天狼星 (8.6 ly) 同 織女星 (25 ly):")
d_sir_vega = ang_deg_between(101.29, -16.72, 279.23, 38.78)
L.append(f"    角距離: {d_sir_vega:.1f}° → A5 節點距離: 幾多 hop?")
L.append(f"    物理距離: 兩粒星其實相距 ~{d_sir_vega/57.3*25:.0f} 光年左右")
L.append(f"    但佢哋喺天空睇落喺對面!")
L.append("")
L.append("  關鍵: A5 節點代表「方向」(RA/Dec), 唔係三維位置。")
L.append("  銀河系內嘅天體物理上近, 但投影方向可以好遠。")
L.append("  → 所以銀河系內唔應該用 A5 空間路由!")
L.append("  → 銀河系內要用「本地域同步」(同一 K_Chain 胞)")
L.append("")

# ── 4. 銀河系內通信策略 ──
L.append("─" * 78)
L.append("  四、銀河系內通信 = 本地域同步 (同一 K_Chain 胞)")
L.append("─" * 78)
L.append("")
L.append("  K_Chain 全環 λ_sync = 294.88 Mpc 遠大於銀河系")
L.append("  → 銀河系內所有點都喺同一個胞入面")
L.append("  → 同一胞內同步 = 相位關係確定 (唔使 A5 路由)")
L.append("")
L.append("  銀河系內「路由」= 頻道複用 + 本地共振:")
L.append("")
L.append("    太陽系 → 半人馬座α (4.37 ly):")
L.append("      同一本地域 → 0 hop → 直接同步")
L.append("      成本: 0 (冇跳) | 延遲: 即時 (W-field 同步)")
L.append("")
L.append("    太陽系 → Sgr A* (26,000 ly):")
L.append("      銀河系內 → 0 hop → 都係本地同步")
L.append("      但黑洞附近引力強, 訊號要加大功率")
L.append("")
L.append("    太陽系 → 大麥哲倫星雲 (160,000 ly):")
L.append("      已出銀河系邊緣 → 要上 A5 地鐵")
L.append("      最近節點: node 4 (M81 方向) 或 node 13/17")
L.append("")
L.append("  🚇 比喻:")
L.append("    銀河系內 = 中環站入面 → 行路 (本地同步)")
L.append("    銀河系外 = 上地鐵 (A5 節點跳躍)")
L.append("")

# ── 5. 太陽系運動 ──
L.append("─" * 78)
L.append("  五、太陽系運動對節點歸屬嘅影響")
L.append("─" * 78)
L.append("")
L.append("  太陽繞銀河系中心: 220 km/s, 一圈 2.3 億年")
L.append("  太陽喺銀河系嘅位置變化:")
L.append("    一圈 2.3 億年 → 1 百萬年行 3.6° (銀心視角)")
L.append("    1 萬年行 0.036° → 遠細過節點間距 26.09°")
L.append("")
L.append("  → 太陽系嘅「銀河系地址」基本上永恆不變")
L.append("  → A5 節點歸屬穩定 (唔使更新路由表)")
L.append("")
L.append("  地球自轉/公轉影響:")
L.append("    地球自轉 → 節點每日轉一圈 (觀測座標問題)")
L.append("    地球公轉 → 季節性視差 (~0.0002 arcsec, 可忽略)")
L.append("  → 用銀河座標 (l, b) 定址, 唔用 RA/Dec, 就冇呢個問題")
L.append("")

# ── 6. 完整例子 ──
L.append("─" * 78)
L.append("  六、完整例子: 太陽系 → 半人馬座α")
L.append("─" * 78)
L.append("")
L.append("  🎯 目的地: 半人馬座α (南門二, 4.37 光年)")
L.append("")
L.append("  步驟 1: 定位")
L.append("    太陽系 = 本地 (銀河系內)")
L.append("    半人馬座α = 本地 (銀河系內, 4.37 ly)")
L.append("")
L.append("  步驟 2: 判斷範圍")
L.append("    兩點都喺銀河系內 (< 0.031 Mpc << λ_sync 294.88 Mpc)")
L.append("    → 同一 K_Chain 胞 → 唔使跳 A5")
L.append("")
L.append("  步驟 3: 揀頻道")
L.append("    本地域同步 (同一 K_Chain 胞, 唔使 A5 路由)")
L.append("")
L.append("  步驟 4: 傳輸")
L.append("    同步到同一胞 → 同半人馬座α相位鎖定 → 即時到達")
L.append("    車資: 0 單位 (冇跳) | 車程: 即時")
L.append("")
L.append("  🎉 完成! 太陽系 → 半人馬座α = 0 跳, 免費, 即時!")
L.append("")

# ── 7. 銀河系內外分界 ──
L.append("─" * 78)
L.append("  七、幾時用本地 (同一胞), 幾時上地鐵 (A5)?")
L.append("─" * 78)
L.append("")
L.append("  距離 < 銀河系 (~10 萬光年):")
L.append("    → 本地域同步, 0 hop")
L.append("")
L.append("  距離 > 銀河系 (星系際):")
L.append("    → 上 A5 地鐵, 由最近節點開始跳")
L.append("")
L.append("  分界線 = 銀河系邊緣 ~50,000 光年")
L.append("")
L.append("  銀河系內「地鐵站」就係你自己:")
L.append("    你唔使去任何節點 — 你本身就喺網絡入面")
L.append("    你只需要調頻到目的地嘅頻道就得")
L.append("")

text = "\n".join(L)
with open(os.path.join(OUT, "galactic_routing_guide.txt"), "w") as f:
    f.write(text + "\n")
print(text)
print(f"\n✅ 已儲存: data/galactic_routing_guide.txt")
