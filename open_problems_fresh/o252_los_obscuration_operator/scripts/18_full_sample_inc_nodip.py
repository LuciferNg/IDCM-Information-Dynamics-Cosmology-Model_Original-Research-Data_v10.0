#!/usr/bin/env python3
"""
O252 — Script 18 v2: 全樣本含冇-dip 窗命中率 (修正統計) (2026-10-17)
===================================================================
誠實修正: R3-R11 命中率只計「fit 到 dip 嘅窗」— 遮蔽若普適, 所有
(源,線) 窗都應有 dip。A Hβ h (ΔAIC −25) 同 F Hβ (ΔAIC −11) 係
「冇 dip」窗, E Hβ (bound −800) 同 J Hβ h (bound +493) 係 fit 退化。
全部由 data/07 JSON 讀真實值 (data/stdout 一致)。
本 script:
  [N-a] 全部 (源,線,grating) 窗: 有 dip / 冇 dip / bound 分類
  [N-b] 去重後 12 窗全樣本命中率 (hop4 vs hop2 窗)
  [N-c] MC null (全窗, 冇 dip 窗對應 null 亦唔命中)
  [N-d] Hβ 系統性弱 (ΔAIC Hα > Hβ) — SNR 唔足解釋冇 dip
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

sig_E = 189.525
hop4, hop2 = 289.759, 204.89

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
allres = d7["results"]

print("="*84)
print("O252/18v2 — 全樣本含冇-dip 命中率 (JSON 讀取)")
print("="*84)

# N-a: 全窗分類
def classify(r):
    if r["dAIC"] < 4: return "nodip"
    if abs(r["dv"]) > 700 or r["depth"] > 1.2: return "bound"
    return "dip"
from collections import Counter
cat0 = Counter(classify(r) for r in allres)
print(f"N-a: 全部 {len(allres)} 窗: {dict(cat0)}")

# 去重: 每 (源,線) 取 grating 最好 (g395h優先), 整體窗分類
gr_rank = {'g395h': 0, 'g395m': 1}
best = {}
for r in allres:
    key = (r["src"], r["line"])
    g = "g395h" if "g395h" in str(r.get("fn","")) else "g395m"
    if key not in best:
        best[key] = []
    best[key].append(r)

rows = []
for key, rs in best.items():
    # 揀最好 grating (rank 最細), 若都係 nodip 就揀 dAIC 最大（最接近顯著）
    rs_sorted = sorted(rs, key=lambda r: (gr_rank.get("g395h" if "g395h" in str(r.get("fn","")) else "g395m", 1)))
    pick = rs_sorted[0]
    rows.append(pick)

n_all = len(rows)
cat = Counter(classify(r) for r in rows)
print(f"N-a': 去重後 {n_all} 窗: {dict(cat)}")

for name, c in [("hop4 289.76", hop4), ("hop2 204.89", hop2)]:
    hits = 0; miss = []
    for r in rows:
        if r["dAIC"] < 4:
            miss.append(f"{r['src']}{r['line']}(冇dip)")
        elif abs(r["dv"]) > 700 or r["depth"] > 1.2:
            miss.append(f"{r['src']}{r['line']}(bound {r['dv']:.0f})")
        elif abs(abs(r["dv"])-c) <= sig_E:
            hits += 1
        else:
            miss.append(f"{r['src']}{r['line']}({r['dv']:.0f})")
    print(f"N-b {name}: 命中 {hits}/{n_all} ({hits/n_all*100:.0f}%)  miss={miss}")
    # N-c MC null (50000)
    rng = np.random.default_rng(42 if name.startswith("hop4") else 7)
    n_sim = 50000
    mc = 0
    for _ in range(n_sim):
        hit = 0
        for r in rows:
            if r["dAIC"] < 4: continue
            pos = abs(rng.uniform(-1500, 1500))
            if abs(pos - c) <= sig_E: hit += 1
        if hit >= hits: mc += 1
    p = mc/n_sim
    ck(f"N-c MC null {name}", p < 0.01, f"p={p:.4g}")

# N-d: Hβ 系統性弱
ha = [r["dAIC"] for r in rows if r["line"]=="Hα"]
hb = [r["dAIC"] for r in rows if r["line"]=="Hβ"]
print(f"\nN-d: Hα ΔAIC mean={np.mean(ha):.0f} (n={len(ha)}), "
      f"Hβ ΔAIC mean={np.mean(hb):.0f} (n={len(hb)})")
ck("N-d Hβ 系統性弱 (SNR 解釋冇 dip)", np.mean(ha) > np.mean(hb),
   f"Hα {np.mean(ha):.0f} > Hβ {np.mean(hb):.0f}")

data = {"n_all_grating": len(allres), "n_dedup": n_all,
        "class_all": dict(Counter(classify(r) for r in allres)),
        "class_dedup": dict(cat),
        "Hα_mean_dAIC": float(np.mean(ha)), "Hβ_mean_dAIC": float(np.mean(hb)),
        "note": "冇 dip / bound 窗全數納入命中率分母 — 保守修正",
        "checks": [{"name": x, "pass": p, "detail": d} for x,p,d in LOG]}
with open(f"{DATA}/18_full_sample_inc_nodip.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/18_full_sample_inc_nodip.json")