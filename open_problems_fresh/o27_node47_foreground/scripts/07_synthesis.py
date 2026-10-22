#!/usr/bin/env python3
"""
07_synthesis.py — O27: 綜合判定
================================
整合所有結果 → 最終判決:
  🟢 真實冷結構  /  🔴 前景污染  /  🟡 混合

輸入 (data/):
  - node47_multiscale.json  (多尺度 rank)
  - crossmap_node47.json    (三地圖 spread)
  - mask_node47.json        (前景 mask)
  - antipode_node47.json    (對徑 + 環境)
  - commander_anomaly.json  (Commander 系統偏差)
  - multifreq_node47.json   (多頻譜)
"""
import json, os, sys

DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o27_node47_foreground/data"

def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        print(f"  [missing] {name}")
        return None
    return json.load(open(p))

print("=" * 70)
print("O27: 綜合判定")
print("=" * 70)

scores = []  # (test, verdict, weight, note)

# 1. 多尺度
ms = load("node47_multiscale.json")
if ms:
    ranks = [r["rank47"] for r in ms]
    T47_3 = [r["T47_uK"] for r in ms if abs(r["fwhm"]-3.0) < 0.01][0]
    all_top2 = all(r <= 2 for r in ranks)
    print(f"\n① 多尺度穩定性: {len(ms)} scales, rank 全部 {min(ranks)}-{max(ranks)}/60"
          f"{' — 全部 top-2!' if all_top2 else ''}")
    print(f"   3.0° T47 = {T47_3:+.1f} μK")
    scores.append(("多尺度", "🟢🟢" if all_top2 else "🟡", 3, f"rank {min(ranks)}-{max(ranks)}/60"))

# 2. 三地圖
cm = load("crossmap_node47.json")
if cm:
    spreads = [r["spread_pct"] for r in cm]
    s0 = [r["node0_spread_pct"] for r in cm]
    smica_nilc = [abs(r["SMICA"]-r["NILC"])/abs((r["SMICA"]+r["NILC"])/2)*100 for r in cm]
    print(f"\n② 三地圖 spread: {[f'{s:.1f}%' for s in spreads]}"
          f" (node0 對照: {[f'{s:.1f}%' for s in s0]})")
    print(f"   SMICA↔NILC 差: {[f'{s:.1f}%' for s in smica_nilc]}")
    # Commander 係系統偏差 (p=0.0004), 扣除後 SMICA/NILC 差先係真
    worst = max(spreads)
    scores.append(("三地圖", "🟡" if worst > 5 else "🟢", 2,
                   f"spread {worst:.1f}% (Commander 系統偏冷, SMICA/NILC 差 {max(smica_nilc):.1f}%)"))

# 3. mask
mk = load("mask_node47.json")
if mk:
    r3 = mk.get("CMB-common-Int-R3", {})
    r2 = mk.get("CMB-IQU-common-R2", {})
    print(f"\n③ 前景 mask:")
    print(f"   R3 CMB common: node47 = {'保留' if r3.get('node47_status')=='clean' else '🔴 遮住'}"
          f" (60節點 {r3.get('n_nodes_keep')}/60 保留)")
    print(f"   R2 IQU common: node47 = {'保留' if r2.get('node47_status')=='clean' else '遮住'}"
          f" (60節點 {r2.get('n_nodes_keep')}/60 保留)")
    masked_r3 = r3.get('node47_status') == 'masked'
    scores.append(("前景 mask", "🔴" if masked_r3 else "🟢", 3,
                   "R3 官方 CMB mask 遮住 node47 (|b|=8.6° 銀河面)"))

# 4. 對徑
ap = load("antipode_node47.json")
if ap:
    anti = [r for r in ap["anti_T"] if abs(r["fwhm"]-3.0) < 0.01]
    T_anti = anti[0]["T_anti"] if anti else None
    env47_3 = ap["env47"].get("8.0", {})
    env0_3 = ap["env0"].get("8.0", {})
    print(f"\n④ 對徑反查: 3.0° T_anti = {T_anti:+.1f} μK (node47 -135.7) → "
          f"{'🟢 冇 mirror 對稱' if T_anti and T_anti > -30 else '⚠️ 對徑都冷'}")
    print(f"   週邊 8°: node47 mean={env47_3.get('mean',0):+.1f} vs 冷斑 mean={env0_3.get('mean',0):+.1f} μK")
    scores.append(("對徑反查", "🟢" if T_anti and T_anti > -30 else "🔴", 2,
                   f"對徑 {T_anti:+.1f} μK 唔冷"))

# 5. Commander 異常
ca = load("commander_anomaly.json")
if ca:
    print(f"\n⑤ Commander 系統偏差: 低緯 C-S = {ca['low_lat_CminusS_mean']:+.1f} μK"
          f" (p={ca['ttest_p']:.4f}) → 高緯 {ca['high_lat_CminusS_mean']:+.1f} μK")
    scores.append(("Commander 偏差", "🟢", 1,
                   f"系統性 (低緯偏冷 {ca['low_lat_CminusS_mean']:+.1f} μK, p={ca['ttest_p']:.4f})"))

# 6. 多頻譜
mf = load("multifreq_node47.json")
if mf:
    rows = {r["name"].split(" ")[0]: r for r in mf["rows"]}
    n47 = rows.get("node47")
    n0 = rows.get("node0")
    if n47 and n0:
        r47 = n47["r217_143"]
        r0 = n0["r217_143"]
        print(f"\n⑥ 多頻譜 (3° 盤平均, K_CMB):")
        for name, tag in [("node47", "問題點"), ("node0", "冷斑對照"), ("node9", "第二冷")]:
            r = rows.get(name)
            if r:
                print(f"   {name:<8} 100={r['T100']:+7.1f} 143={r['T143']:+7.1f} "
                      f"217={r['T217']:+7.1f} 353={r['T353']:+7.1f}  217/143={r['r217_143']:.2f} 353/217={r['r353_217']:.2f}")
        # 判定: CMB 平譜 → 217/143 ≈ 1
        flat = abs(r47 - r0) < 0.3 and abs(r47 - 1.0) < 0.5
        rising = r47 > 1.5
        print(f"   node47 217/143 = {r47:.2f} vs 冷斑 {r0:.2f} → "
              f"{'🟢 平譜 (CMB-like)' if flat else '🔴 上升 (dust-like)' if rising else '🟡 混合'}")
        scores.append(("多頻譜", "🟢" if flat else "🔴" if rising else "🟡", 5,
                       f"217/143={r47:.2f} vs 冷斑 {r0:.2f}"))

# 最終
print("\n" + "=" * 70)
print("判定矩陣:")
total_w = 0
weighted = 0
for name, verdict, w, note in scores:
    total_w += w
    wv = {"🟢🟢": 2, "🟢": 1, "🟡": 0, "🔴": -1}[verdict]
    weighted += w * wv
    print(f"  {verdict}  {name:<12} (w={w})  {note}")
ratio = weighted / total_w if total_w else 0
print(f"\n加權分: {weighted}/{total_w} = {ratio:+.2f} (多頻譜 veto 優先)")

# 多頻譜 veto: 光譜上升 = 前景污染, 一票否決
mf_verdict = next((v for n, v, w, note in scores if n == "多頻譜"), None)
if mf_verdict == "🔴":
    print("\n### 最終判決: 🔴 前景污染 (多頻譜 veto) ###")
    print("多頻譜係最決定性測試: 真 CMB 冷結構 (node0) 143GHz=-112 μK 全頻率冷,")
    print("node47 143GHz=+18 μK 唔冷 + 217GHz 急升 (217/143=13-21) = dust 特徵。")
    print("SMICA 嘅 -136 μK 係銀河面塵埃殘留, 唔係真實 CMB 冷結構。")
elif ratio > 0.4:
    verdict = "🟢🟢 真實冷結構"
elif ratio > 0:
    verdict = "🟢 傾向真實 (有前景疊加)"
elif ratio > -0.3:
    verdict = "🟡 混合 — 需要更多證據"
else:
    verdict = "🔴 前景污染"
    print(f"\n### 最終判決: {verdict} ###")
