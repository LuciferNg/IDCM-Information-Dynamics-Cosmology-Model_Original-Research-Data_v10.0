#!/usr/bin/env python3
"""
O183-03: W_179 加權 M1 — 三圖 × 兩窗口 全表驗證 (12/55 候選 pre-registration)
=============================================================================
O183-02 發現: SMICA 4.17 W_179 加權 M1 = 0.21796 ≈ 12/55 = 0.21818 (dev −0.10%)
12 = B·N_gen, 55 = F₁₀ — 全譜量!

判準 (O182 教訓 — pre-registered):
  ✅ PASS: 三圖 × 兩窗口 W_179 加權 M1 全部 dev(|12/55|) < 1%
  ❌ FAIL: 任何窗口 dev > 1% → 候選降級 (巧合)

對照: 無加權命中背景 11/45 (O182 巧合確認); stress_S/bc 加權偏離更大.
"""
import json
import numpy as np

B, L5 = 4, 11
A = 134.2
T55 = 12/55  # 0.2181818 — 候選預言值

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
routing = json.load(open(f'{BASE}/little_red_dots/data/a5_routing_weighted.json'))
nodes = routing['nodes']
hop = np.array([float(n['hop_from_cs']) for n in nodes])
frust = np.array([float(n['frust_count']) for n in nodes])
W_179 = (frust+1)*(1+(B/L5)*np.cos(np.pi*hop/4))

print("O183-03: W_179 加權 M1 三圖×兩窗口 (候選 12/55 = 0.218182)")
print(f"{'map':>10} {'fwhm':>5} {'M1_plain':>9} {'M1_W179':>9} {'dev55':>8} {'PASS':>5}")
results = []
for name in ['SMICA', 'Commander', 'SEVEM']:
    for fwhm in ['4.17', '5.0']:
        data = json.load(open(f'{BASE}/o182_88grid_geometry/data/temps2_{name}_{fwhm}deg.json'))
        T = np.array(data['A5_60'])[:60]
        dT = T - T.mean()
        m1_plain = np.mean(np.abs(dT))/A
        m1_w = np.sum(W_179*np.abs(dT))/(np.sum(W_179)*A)
        dev = (m1_w/T55 - 1)*100
        ok = abs(dev) < 1.0
        results.append(ok)
        print(f"{name:>10} {fwhm:>5} {m1_plain:>9.5f} {m1_w:>9.5f} {dev:>7.2f}% {'✅' if ok else '❌'}")

npass = sum(results)
print(f"\n結果: {npass}/{len(results)} PASS (pre-registered 判準: 全部 dev < 1%)")
print(f"結論: {'🟢 12/55 = (B·N_gen)/F₁₀ 候選成立' if npass == len(results) else '❌ 候選降級 (窗口依賴)'}")
