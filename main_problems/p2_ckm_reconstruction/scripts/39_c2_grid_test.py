#!/usr/bin/env python3
"""39 — (c2) 決定性測試: 全 grid 角度匹配 + (d,s) 結構性
問題: D6×S6 嘅「生成原則」= 角度匹配唯一性 + (d,s) 結構性嘅湧現? 定係需要更多規則?
測試: 對 4 個角度, 全 beat-ratio 類 (3828²) 搵全部命中 (tol 0.01° 同 1e-4 rel),
      檢查命中嘅 (d,s) 有幾多係 D6×S6 / STRUCT×STRUCT, 框架 8 對係咪結構命中嘅全集。
"""
import numpy as np, itertools

N = 88
sin176 = np.sin(np.arange(1, 88)*np.pi/176.0)  # d 側: sin(dπ/176), d=1..87
pairs = [(a,b) for a in range(1,N) for b in range(a+1,N+1)]
beats = np.array([4*np.sin((b-a)*np.pi/176.0)*np.cos((a+b)*np.pi/176.0) for a,b in pairs])
ds = np.array([(b-a, a+b) for a,b in pairs])
M = len(pairs)

D6 = {1,2,6,9,19,21}; S6 = {11,25,41,44,68,85}; C6 = {3,11,20,25,41,44}
STRUCT = {1,2,3,4,5,6,7,8,9,11,12,13,16,17,18,19,20,21,22,25,27,29,32,33,34,36,38,40,41,42,44,47,55,63,64,66,68,76,77,85,88,90,91,98,123,137,143,153,176,178}

targets = {
    "θ₁₂": (np.tan(np.radians(13.039994)), {(5,6),(19,25)}),
    "θ₂₃": (np.tan(np.radians(2.379994)), {(33,35),(3,22)}),
    "θ₁₃": (np.sin(np.radians(0.200961)), {(42,43),(10,31)}),
    "δ":   (np.tan(np.radians(66.399960)), {(2,23),(8,17)}),
}

for name, (t, fw_pairs) in targets.items():
    for tol_name, tol in [("0.01°", 1e-4), ("1e-4rel", 1e-4)]:
        # 0.01° 角容差 ≈ rel 1e-4 (13° 時 0.01°=7.7e-4, 但 2.4° 時 = 4e-4) — 統一用 rel 1e-4 做角容差代理
        hits = []
        for i in range(M):
            r = beats[i]/beats
            m = np.abs(r - t) < tol*t  # rel tolerance
            idx = np.argwhere(m).flatten()
            for j in idx:
                (d1,s1),(d2,s2) = ds[i], ds[j]
                hits.append((tuple(pairs[i]), tuple(pairs[j]), int(d1),int(s1),int(d2),int(s2)))
        if not hits:
            print(f"{name} tol={tol_name}: 0 hits")
            continue
        # 結構命中: (d,s) 全部 ∈ STRUCT
        st = [h for h in hits if h[2] in STRUCT and h[3] in STRUCT and h[4] in STRUCT and h[5] in STRUCT]
        d6s6 = [h for h in hits if h[2] in D6 and h[3] in S6 and h[4] in D6 and h[5] in S6]
        fw_list = list(fw_pairs)
        fw_set = {tuple(sorted((fw_list[0], fw_list[1]))), tuple(sorted((fw_list[1], fw_list[0])))}
        fw = [h for h in hits if (h[0], h[1]) in fw_set]
        print(f"{name} tol={tol_name}: total={len(hits)} struct={len(st)} D6×S6={len(d6s6)} framework={len(fw)}")
        if len(st) <= 12:
            for h in st[:12]:
                print(f"    {h[0]}(d{h[2]},s{h[3]}) / {h[1]}(d{h[4]},s{h[5]})")

print("\nRESULT: (c2) grid 測試完成")
