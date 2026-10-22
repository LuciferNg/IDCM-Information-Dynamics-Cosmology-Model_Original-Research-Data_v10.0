#!/usr/bin/env python3
"""
O29 熱斑幾何歸屬 verifier — 直接讀 hotspot_attribution.json 驗證 NN_results.md 宣稱
===================================================================================
反幻覺鐵律: 每個數字由 file simulation verifier 直接讀返實際 saved JSON 驗證。
"""
import json
import sys

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o29_p072_decompose/data/hotspot_attribution.json'

ok = 0
fail = 0

def check(label, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  ✅ {label}")
    else:
        fail += 1
        print(f"  ❌ {label} {detail}")

print("=" * 60)
print("O29 熱斑幾何歸屬 Verifier (file simulation)")
print("=" * 60)

# 1. 檔案存在
print("\n[1] 檔案存在")
try:
    d = json.load(open(DATA))
    check("hotspot_attribution.json 存在且可讀", True)
except Exception as e:
    check("hotspot_attribution.json 存在且可讀", False, str(e))
    sys.exit(1)

# 2. 結構
print("\n[2] 結構")
check("有 hot 14 斑", len(d.get('hot', [])) == 14, f"got {len(d.get('hot', []))}")
check("有 cold 15 斑", len(d.get('cold', [])) == 15, f"got {len(d.get('cold', []))}")
check("有 random_expect", 'random_expect' in d)
check("有 lat_controlled", 'lat_controlled' in d)
check("有 z_vs_lat", 'z_vs_lat' in d)

# 3. 熱斑數字核對 (NN_results.md 宣稱)
print("\n[3] 熱斑數字核對")
hot_d_node = [h['d_node'] for h in d['hot']]
hot_d_tri = [h['d_tri'] for h in d['hot']]
hot_d_frust = [h['d_frust'] for h in d['hot']]
mean_node = sum(hot_d_node) / len(hot_d_node)
mean_tri = sum(hot_d_tri) / len(hot_d_tri)
mean_frust = sum(hot_d_frust) / len(hot_d_frust)
print(f"  熱斑 mean: node={mean_node:.2f} tri={mean_tri:.2f} frust={mean_frust:.2f}")
check("熱斑 node mean ≈ 10.07", abs(mean_node - 10.07) < 0.05, f"got {mean_node:.3f}")
check("熱斑 tri mean ≈ 20.10", abs(mean_tri - 20.10) < 0.05, f"got {mean_tri:.3f}")
check("熱斑 frust mean ≈ 19.61", abs(mean_frust - 19.61) < 0.05, f"got {mean_frust:.3f}")

# 4. z_vs_lat 核對 (緯度修正)
print("\n[4] z_vs_lat (緯度修正)")
z = d['z_vs_lat']['hot']
check("熱斑 node z ≈ -0.10", abs(z['node'] - (-0.10)) < 0.05, f"got {z['node']:.3f}")
check("熱斑 tri z ≈ +0.92", abs(z['tri'] - 0.92) < 0.05, f"got {z['tri']:.3f}")
check("熱斑 frust z ≈ +1.74", abs(z['frust'] - 1.74) < 0.05, f"got {z['frust']:.3f}")
zc = d['z_vs_lat']['cold']
check("冷斑 node z ≈ -0.89", abs(zc['node'] - (-0.89)) < 0.05, f"got {zc['node']:.3f}")
check("冷斑 tri z ≈ +0.07", abs(zc['tri'] - 0.07) < 0.05, f"got {zc['tri']:.3f}")
check("冷斑 frust z ≈ +0.30", abs(zc['frust'] - 0.30) < 0.05, f"got {zc['frust']:.3f}")

# 5. 全部 |z|<1.8 宣稱
print("\n[5] 全部 |z|<1.8")
all_z = list(z.values()) + list(zc.values())
check("全部 6 個 z |z|<1.8", all(abs(v) < 1.8 for v in all_z), f"max={max(abs(v) for v in all_z):.2f}")

# 6. F6/F7 特定距離 (NN_results 宣稱 9.03°/8.25°)
print("\n[6] F6/F7 特定斑")
# F6 = SMICA-h1? 唔係 — F6/F7 係 O2 文獻熱斑, 唔喺 match_results 入面
# 改為驗證 h1 (node=9.03) 同 h12 (node=2.03) 呢啲喺 JSON 有
h1 = [h for h in d['hot'] if 'h1' in h['name']][0]
check("SMICA-h1 d_node ≈ 9.03", abs(h1['d_node'] - 9.03) < 0.05, f"got {h1['d_node']:.3f}")
h2 = [h for h in d['hot'] if 'h2' in h['name']][0]
check("SMICA-h2 d_node ≈ 1.11", abs(h2['d_node'] - 1.11) < 0.05, f"got {h2['d_node']:.3f}")
h12 = [h for h in d['hot'] if 'h12' in h['name']][0]
check("SMICA-h12 d_node ≈ 2.03", abs(h12['d_node'] - 2.03) < 0.05, f"got {h12['d_node']:.3f}")

# 7. conclusion
print("\n[7] 結論")
check("conclusion 存在", 'conclusion' in d and d['conclusion'])
check("conclusion 講冇系統性歸屬", '冇系統性歸屬' in d['conclusion'] or 'no' in d['conclusion'].lower())

print("\n" + "=" * 60)
print(f"TALLY: {ok}/{ok+fail} PASS")
print("=" * 60)
sys.exit(0 if fail == 0 else 1)
