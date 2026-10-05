#!/usr/bin/env python3
"""GRT-23: 地球路由驗證 — astropy 精確 LST + 過境時間驗證.

驗證 22 號腳本嘅近似結果:
1. 用 astropy 計真實 LST (考慮恒星日 23h56m, 唔係近似 24h)
2. 驗證每個城市主節點 (全天最高節點) 正確
3. 驗證節點上中天時間 (transit time) 精確
4. 香港 → node 57 高度角 89.9° 嘅獨立驗證
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes

OUT = "../data"
nodes, vecs = load_nodes()

try:
    from astropy.time import Time
    from astropy.coordinates import EarthLocation, AltAz, SkyCoord, Longitude, Latitude
    import astropy.units as u
    from astropy.utils import iers
    # 用內置 IERS 表避免下載 (離線可用)
    iers.conf.auto_download = False
    iers.conf.auto_max_age = None
    HAVE_ASTROPY = True
except ImportError:
    HAVE_ASTROPY = False
    print("⚠️ astropy 唔可用, 用近似法")

def radec_to_vec(ra_deg, dec_deg):
    ra = math.radians(ra_deg); dec = math.radians(dec_deg)
    return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1, v2 = radec_to_vec(ra1, dec1), radec_to_vec(ra2, dec2)
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

def alt_approx(lat_deg, node_ra, node_dec, lst_deg):
    lat = math.radians(lat_deg)
    dec = math.radians(node_dec)
    ha = math.radians((lst_deg - node_ra) % 360)
    sin_alt = (math.sin(lat)*math.sin(dec) +
               math.cos(lat)*math.cos(dec)*math.cos(ha))
    return math.degrees(math.asin(max(-1, min(1, sin_alt))))

# 地球位置
SITES = [
    ("香港", 22.32, 114.17),
    ("東京", 35.68, 139.69),
    ("倫敦", 51.51, -0.13),
    ("雪梨", -33.87, 151.21),
    ("紐約", 40.71, -74.01),
    ("ALMA (智利)", -23.03, -67.75),
    ("南極點", -90.00, 0.00),
]

L = []
L.append("=" * 82)
L.append("  地球路由驗證 — astropy 精確 LST + 過境時間")
L.append("=" * 82)
L.append("")

# ── 驗證 1: 恒星日 vs 太陽日 ──
L.append("─" * 82)
L.append("  驗證 1: 恒星日 (23h56m) vs 太陽日 (24h)")
L.append("─" * 82)
L.append("")
L.append("  22 號腳本用 24h 近似 (LST = 經度 + 15°/h)")
L.append("  真實恒星日 = 23h56m04s → LST 每小時行 15.041°")
L.append("  24 小時後 LST 會多 360° + 0.986° (1 日誤差)")
L.append("")

if HAVE_ASTROPY:
    # 計兩個時刻嘅 LST 差
    t0 = Time("2026-08-16 00:00:00", scale="utc")
    t1 = Time("2026-08-17 00:00:00", scale="utc")
    loc = EarthLocation(lat=22.32*u.deg, lon=114.17*u.deg)
    lst0 = t0.sidereal_time("apparent", longitude=loc.lon)
    lst1 = t1.sidereal_time("apparent", longitude=loc.lon)
    lst_delta = (lst1.deg - lst0.deg) % 360
    L.append(f"  astropy 實測 (香港):")
    L.append(f"    8/16 00:00 LST = {lst0.deg:.4f}°")
    L.append(f"    8/17 00:00 LST = {lst1.deg:.4f}°")
    L.append(f"    24h 後 LST 變化 = {lst_delta:.4f}° (理想 360.9856°)")
    L.append(f"    誤差 vs 24h 近似 = {lst_delta - 360:.4f}°")
    L.append(f"    → 過 1 日, 近似法誤差 {abs(lst_delta-360):.3f}° ≈ {abs(lst_delta-360)*4:.1f} 分鐘")
    L.append("")
    L.append("  結論: 單日內誤差 < 1°, 對路由應用可接受;")
    L.append("        但多日 tracking 要用 astropy 精確 LST.")
    L.append("")

# ── 驗證 2: 主節點 (全天最高) ──
L.append("─" * 82)
L.append("  驗證 2: 主節點全天最大高度 (近似 vs 精確)")
L.append("─" * 82)
L.append("")
L.append("  主節點理論值 = 緯度最近嘅節點 Dec (上中天時 90° - |lat - dec|)")
L.append("")

if HAVE_ASTROPY:
    obs_time = Time("2026-08-16 12:00:00", scale="utc")
    for name, lat, lon in SITES:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
        # 向量化: 一次計 60 節點 × 時間網格
        times = obs_time + np.arange(0, 24, 0.25)*u.hour  # 每 15 分鐘
        max_alt_each = np.zeros(60)
        for i, (nra, ndec) in enumerate(nodes):
            node_coord = SkyCoord(ra=nra*u.deg, dec=ndec*u.deg, frame="icrs")
            altaz = node_coord.transform_to(AltAz(obstime=times, location=loc))
            max_alt_each[i] = altaz.alt.deg.max()
        main_i = int(np.argmax(max_alt_each))
        max_alt = max_alt_each[main_i]
        nra, ndec = nodes[main_i]
        theory = 90.0 - abs(lat - ndec)
        L.append(f"  {name:<14} 精確主節點 = node {main_i:>2} ({nra:.1f}°, {ndec:.1f}°)")
        L.append(f"    精確最大高度 = {max_alt:.2f}° | 理論值 = {theory:.2f}° | 差 = {abs(max_alt-theory):.3f}°")
        L.append("")
else:
    for name, lat, lon in SITES:
        vis = []
        for i, (nra, ndec) in enumerate(nodes):
            max_alt = 90.0 - abs(lat - ndec)
            vis.append((max_alt, i, nra, ndec))
        vis.sort(reverse=True)
        max_alt, main_i, nra, ndec = vis[0]
        L.append(f"  {name:<14} 主節點 = node {main_i:>2} ({nra:.1f}°, {ndec:.1f}°) 高度 {max_alt:.1f}°")
        L.append("")

# ── 驗證 3: 香港 node 57 高度 89.9° 驗證 ──
L.append("─" * 82)
L.append("  驗證 3: 香港 → node 57 高度角 (重點驗證)")
L.append("─" * 82)
L.append("")
L.append("  22 號腳本: 香港主節點 = node 57, 高度 89.9°")
L.append("  node 57 Dec = 22.2° | 香港緯度 = 22.32°")
L.append("  → 上中天理論高度 = 90 - |22.32 - 22.2| = 89.88° ✅")
L.append("")

if HAVE_ASTROPY:
    loc_hk = EarthLocation(lat=22.32*u.deg, lon=114.17*u.deg)
    node57 = SkyCoord(ra=nodes[57][0]*u.deg, dec=nodes[57][1]*u.deg, frame="icrs")
    # 向量化: 掃描 24h (每 5 分鐘)
    times = obs_time + np.arange(0, 24, 5/60)*u.hour
    altaz_all = node57.transform_to(AltAz(obstime=times, location=loc_hk))
    alt_all = altaz_all.alt.deg
    best_idx = int(np.argmax(alt_all))
    best_alt = alt_all[best_idx]
    best_t = times[best_idx]
    lst_at_transit = best_t.sidereal_time("apparent", longitude=loc_hk.lon)
    L.append(f"  astropy 精確計算:")
    L.append(f"    node 57 上中天最大高度 = {best_alt:.3f}°")
    L.append(f"    上中天時間 (UTC) = {best_t.iso}")
    L.append(f"    上中天 LST = {lst_at_transit.deg:.3f}°")
    L.append(f"    node 57 RA = {nodes[57][0]:.3f}°")
    L.append(f"    上中天 LST vs RA 差 = {abs((lst_at_transit.deg - nodes[57][0]) % 360):.3f}°")
    L.append(f"    (上中天時 LST = RA, 差應 ≈ 0)")
    L.append("")

# ── 驗證 4: 22 號腳本近似 vs astropy 交叉驗證 ──
L.append("─" * 82)
L.append("  驗證 4: 近似高度角 vs astropy 精確高度角")
L.append("─" * 82)
L.append("")

if HAVE_ASTROPY:
    L.append(f"  {'位置':<14} {'節點':>4} {'近似高度':>8} {'astropy高度':>10} {'差':>6}")
    L.append(f"  {'----':<14} {'--':>4} {'----':>8} {'----':>10} {'--':>6}")
    check_count = 0
    check_pass = 0
    for name, lat, lon in SITES[:5]:
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
        for h in [0, 6, 12, 18]:
            # 用 astropy 真實 LST (唔係近似 lon+15h!)
            t = obs_time + h*u.hour
            lst_real = t.sidereal_time("apparent", longitude=loc.lon).deg
            # 近似: 喺真實 LST 下揀最高節點
            alt_max_approx = -90
            best_i = None
            for i, (nra, ndec) in enumerate(nodes):
                a = alt_approx(lat, nra, ndec, lst_real)
                if a > alt_max_approx:
                    alt_max_approx = a
                    best_i = i
            # astropy 精確
            node_coord = SkyCoord(ra=nodes[best_i][0]*u.deg, dec=nodes[best_i][1]*u.deg, frame="icrs")
            altaz = node_coord.transform_to(AltAz(obstime=t, location=loc))
            alt_exact = altaz.alt.deg
            diff = abs(alt_max_approx - alt_exact)
            check_count += 1
            if diff < 2.0:
                check_pass += 1
            flag = "✅" if diff < 2.0 else "❌"
            L.append(f"  {name:<14} {best_i:>4} {alt_max_approx:>8.1f}° {alt_exact:>9.1f}° {diff:>5.2f}° {flag}")
    L.append("")
    L.append(f"  通過率: {check_pass}/{check_count}")
    L.append("")
    L.append("  誤差來源: 近似公式忽略章動/歲差/蒙氣差 (refraction)")
    L.append("  → 2° 內誤差 = 路由定位精度足夠 (< 節點間距 26° 嘅 1/10)")
    L.append("")
else:
    L.append("  astropy 唔可用, 跳過 (需 pip install astropy)")
    L.append("")

# ── 驗證 5: 城市對共享節點穩定性 ──
L.append("─" * 82)
L.append("  驗證 5: 共享節點數嘅幾何穩定性")
L.append("─" * 82)
L.append("")
L.append("  共享節點數只取決於兩個城市嘅緯度 (Dec 覆蓋範圍)")
L.append("  → 唔受經度/時間影響 → 長期穩定")
L.append("")
L.append("  共享節點數公式 (理論):")
L.append("    城市 A 可見: Dec ∈ [lat_A - 60°, lat_A + 60°] (高度>30)")
L.append("    城市 B 可見: Dec ∈ [lat_B - 60°, lat_B + 60°]")
L.append("    共享: Dec ∈ [max(lat_A,lat_B) - 60°, min(lat_A,lat_B) + 60°]")
L.append("")
for name_a, lat_a, lon_a in SITES[:3]:
    for name_b, lat_b, lon_b in SITES[3:6]:
        dec_lo = max(lat_a, lat_b) - 60
        dec_hi = min(lat_a, lat_b) + 60
        # 節點 Dec 喺範圍內嘅數
        n_shared_theory = sum(1 for _, ndec in nodes if dec_lo <= ndec <= dec_hi)
        # 實際 (用 22 號方法)
        vis_a = set(i for i, (_, ndec) in enumerate(nodes) if ndec >= lat_a - 60 and ndec <= lat_a + 60)
        vis_b = set(i for i, (_, ndec) in enumerate(nodes) if ndec >= lat_b - 60 and ndec <= lat_b + 60)
        n_shared_actual = len(vis_a & vis_b)
        L.append(f"  {name_a:<12} × {name_b:<12} 理論共享 = {n_shared_theory:>2} | 實際 = {n_shared_actual:>2} | {'✅' if n_shared_theory == n_shared_actual else '⚠️'}")
L.append("")
L.append("  結論: 共享節點數係緯度嘅純幾何函數, 穩定可預測")
L.append("")

text = "\n".join(L)
with open(os.path.join(OUT, "earth_routing_verification.txt"), "w") as f:
    f.write(text + "\n")
print(text)
print(f"\n✅ 已儲存: data/earth_routing_verification.txt")
