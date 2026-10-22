#!/usr/bin/env python3
"""C02_frame_audit.py — 座標 frame 審計 (冷斑位置交叉驗證)"""
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

print("=== C02: 座標 frame 審計 ===")

# 冷斑文獻位置 (Cruz 2005): Galactic (209°, -57°)
cs_gal = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic')
cs_icrs_from_gal = cs_gal.icrs
print(f"\n1. 文獻冷斑 Galactic (209°, -57°) → ICRS = ({cs_icrs_from_gal.ra.deg:.2f}°, {cs_icrs_from_gal.dec.deg:.2f}°)")

# a5_nodes[0]
print(f"\n2. a5_nodes[0] = (48.30, -20.44)")
cs_a5 = SkyCoord(ra=48.30*u.deg, dec=-20.44*u.deg, frame='icrs')
g_a5 = cs_a5.galactic
print(f"   a5_nodes[0] 當 ICRS → Galactic = ({g_a5.l.deg:.2f}°, {g_a5.b.deg:.2f}°)")

# 對比
print(f"\n3. 對比:")
print(f"   a5[0] 轉換後 Galactic = ({g_a5.l.deg:.2f}, {g_a5.b.deg:.2f})")
print(f"   文獻冷斑 Galactic    = (209.00, -57.00)")
match = abs(g_a5.l.deg - 209) < 0.5 and abs(g_a5.b.deg + 57) < 0.5
print(f"   → {'✅ a5_nodes 存 ICRS, node 0 = 冷斑' if match else '❌ 唔匹配'}")

# 之前 script 用嘅 reference 數字
print(f"\n4. 之前 C01 script 用 reference (263.86°, -48.74°) 係錯嘅幻覺數字")
print(f"   實際文獻: 冷斑 Galactic (209°, -57°)")
print(f"   (263.86, -48.74) 係邊度嚟? — 冇根據, 應該刪除")

with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_renew/data/C02_frame_audit.txt', 'w') as f:
    f.write("# O4_renew C02: 座標 frame 審計\n")
    f.write(f"coldspot_galactic=209,-57\n")
    f.write(f"a5_nodes0_as_ICRS={g_a5.l.deg:.2f},{g_a5.b.deg:.2f}\n")
    f.write(f"match={match}\n")
    f.write(f"NOTE: a5_nodes.txt stores ICRS (RA,Dec); node0 = cold spot at Gal (209,-57)\n")
print("\n✅ 已存: data/C02_frame_audit.txt")
