#!/usr/bin/env python3
"""
O183-01: W(i) 加權 A₅ 節點集合 — 溫度統計重審 (對應 v2 第一步)
================================================================
O182 用 A5_60 集合 (無加權): M1 = ⟨|δT|⟩/A = 0.24435 ≈ 11/45 (背景值)
O179 閉合 W(i) = (frust+1)[1+(B/L₅)cos(π·hop/4)] — 位置權重
問題: W(i) 加權後嘅 M1 係咩? 係咪仍然命中背景 (巧合確認)?
      加權會唔會揭示「A5 命中」係巧合定結構?

方法:
  A. 讀 routing['nodes'] → hop/frust → W(i)
  B. 讀 O182 temps2 JSON (三圖 × 窗口) → 節點溫度
  C. 加權 M1_W = ΣW|δT|/(ΣW·A) vs 無加權 M1 vs 背景 0.2444 vs G88 0.2977
  D. 診斷: W(i) 分佈同 |δT| 嘅相關性 (若 W ∝ |δT| → 加權後 M1 變 → 結構信號)
"""
import json, math
import numpy as np

B, L5 = 4, 11
A = 134.2  # μK 冷斑幅度
T11 = 11/45  # 0.244444 背景值

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'

# ---- A. W(i) ----
routing = json.load(open(f'{BASE}/little_red_dots/data/a5_routing_weighted.json'))
nodes = routing['nodes']
print(f"A. routing nodes: {len(nodes)}")
print(f"   示例: {nodes[0]}")

hop_arr, frust_arr, w_arr = [], [], []
for it in nodes:
    hop = it.get('hop_from_cs')
    fr = it.get('frust_count')
    w = it.get('stress_S')   # 已有應力權重 (O179 W(i) 對照)
    hop_arr.append(float(hop))
    frust_arr.append(float(fr))
    w_arr.append(float(w))
hop_arr, frust_arr, w_arr = map(np.array, (hop_arr, frust_arr, w_arr))

print(f"   hop 階梯: {np.bincount(hop_arr.astype(int), minlength=13)[1:13]}")
print(f"   <hop> = {hop_arr.mean():.4f} (O179 預言 4 = B)")
print(f"   W(i) 範圍: [{w_arr.min():.4f}, {w_arr.max():.4f}], 均值 {w_arr.mean():.4f}")
# 對稱檢查 (O179 重心定理: n(h) = n(8-h))
sym = all(np.bincount(hop_arr.astype(int))[h] == np.bincount(hop_arr.astype(int))[8-h] for h in range(1, 8))
print(f"   hop 階梯對稱 n(h)=n(8−h): {sym}")

# ---- B. 節點位置 (RA/Dec) ----
# routing nodes 可能冇 RA/Dec — 用 a5_nodes.txt
nodes_sky = []
with open(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                nodes_sky.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
print(f"B. 天空節點: {len(nodes_sky)} (routing {len(nodes)} — 順序假設一致)")

# ---- C. 溫度統計 (O182 temps2 JSON) ----
print(f"\nC. W(i) 加權溫度統計 (對比 O182):")
print(f"{'map':>10} {'fwhm':>5} {'M1_plain':>9} {'M1_W':>9} {'dev45_plain':>11} {'dev45_W':>10}")
for name in ['SMICA', 'Commander', 'SEVEM']:
    for fwhm in ['4.17', '5.0']:
        try:
            data = json.load(open(f'{BASE}/o182_88grid_geometry/data/temps2_{name}_{fwhm}deg.json'))
            for sname in ['A5_60']:
                if sname not in data:
                    continue
                T = np.array(data[sname])
                if len(T) != len(nodes_sky):
                    # 可能順序唔同 — 用頭 len(T) 個
                    T_set = T[:len(w_arr)] if len(T) >= len(w_arr) else T
                else:
                    T_set = T
                n = len(T_set)
                dT = T_set - T_set.mean()
                m1_plain = np.mean(np.abs(dT))/A
                m1_w = np.sum(w_arr[:n]*np.abs(dT))/(np.sum(w_arr[:n])*A)
                print(f"{name:>10} {fwhm:>5} {m1_plain:>9.5f} {m1_w:>9.5f} "
                      f"{(m1_plain/T11-1)*100:>10.2f}% {(m1_w/T11-1)*100:>9.2f}%")
        except FileNotFoundError:
            pass

# ---- D. 診斷: W(i) 同 |δT| 相關性 ----
print(f"\nD. 診斷 — W(i) vs |δT|:")
try:
    data = json.load(open(f'{BASE}/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))
    T = np.array(data['A5_60'])[:len(w_arr)]
    dT = T - T.mean()
    corr = np.corrcoef(w_arr, np.abs(dT))[0, 1]
    print(f"   corr(W, |δT|) = {corr:+.4f} (若 |corr| > 0.2 → W 携帶溫度結構)")
    # W 分組: 高 W vs 低 W 嘅 |δT|
    hi = np.abs(dT)[w_arr > np.median(w_arr)].mean()
    lo = np.abs(dT)[w_arr <= np.median(w_arr)].mean()
    print(f"   ⟨|δT|⟩ 高W組 = {hi:.2f} μK vs 低W組 = {lo:.2f} μK (比 {hi/lo:.3f})")
except Exception as e:
    print(f"   診斷失敗: {e}")

print("\n完成 — 詳情見 O183 docs/01")
