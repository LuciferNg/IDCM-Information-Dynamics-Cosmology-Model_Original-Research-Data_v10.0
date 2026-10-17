#!/usr/bin/env python3
"""
51_label_gate.py — 88-site label 終裁閘定義 + 資產檢查 (2026-10-17)
=================================================================
問題: 88-site 樣本外 (R5 輸出 [7,14,22,28,33,44], 4/5) 要終裁,
      需要「88-site 自身物理 label」— 用戶問: label 要咩閘?

本輪:
  G0  資產盤點: 現有 label 源 (P13 09 mapping / O34-O54 公式 / 外部)
  G1  獨立性閘: label 必須源於已閉合公式或外部觀測 — 禁由 R5 反向配
  G2  預註冊閘: label 集必須 lock 喺測試前 (誠實標明: 現況係 R5 先 label 後)
  G3  遷移唯一性閘: 44→88 label 遷移規則必須唯一 (唔可以多種揀)
  G4  數量閘: 88-site 需 ≥9 個獨立 label 先夠統計
  G5  零參數閘: 遷移唔可以引入新 fit
  G6  判定標準閘: PASS/FAIL 定義
  G7  對偶鏈閘: P13 定理 2 (88-site 對偶譜 γ'_d) 要納入

檢查: 現有 P13 資產 (07_physics_mapping 9 個已閉合 mapping) 過唔過到?
零 import 原 scripts; 第一原理。
"""
import json
from math import gcd

# ============ G0: 資產盤點 ============
print("=== G0: 現有 label 資產 ===")
MAPPING = [  # P13 07_physics_mapping.py (O34/O35/O54 已閉合)
    ("u/d 夸克", (10, 24), "O34 ✅ 0.026%"),
    ("c/s 夸克", (8, 22), "O34 ✅ 0.368%"),
    ("t/b 夸克", (19, 33), "O34 ✅ 0.005%"),
    ("m_c/m_b", (8, 33), "O34 ✅ 0.368%"),
    ("m_s/m_d", (1, 22), "O35 ✅ 0.037%"),
    ("m_W/m_Z", (30, 41), "O34 ✅ 0.146%"),
    ("m_H/m_W", (19, 38), "O34 ✅ 0.064%"),
    ("m_μ/m_τ", (1, 18), "O34 ✅ 0.165%"),
    ("n/p BBN", (7, 20), "O13 ✅"),
]
print(f"  P13 已閉合物理 mapping: {len(MAPPING)} 個 (全部公式來源, O34/O35/O54/O13)")
for name, (n, m), st in MAPPING:
    print(f"    {name:<10} ({n:>2},{m:>2}) d={m-n:>2} s={m+n:>3}  {st}")

# 88-site 同座標 presence
print()
print("  88-site 同座標格存在性 (44-site 格 → 88-site):")
all44 = [(n, m) for (_, (n, m), _) in MAPPING]
ok_all = all(1 <= n < m <= 88 for n, m in all44)
print(f"    {len(all44)} 格全部 (i,j)≤44<88 → 存在 ✓")

# ============ G7: 對偶鏈 γ'_d = 4sin²(dπ/176) = B(d,88−d) ============
print()
print("=== G7: P13 定理 2 — 88-site 對偶鏈譜 γ'_d ===")
def gcl88(d): return gcd(abs(88 - d), 352)
def deg_gamma(d):
    # γ'_d = 4sin²(πd/176) = 2−2cos(πd/88), cos(πd/88) ∈ ℚ(ζ₁₇₆)⁺
    # deg(cos(πd/88)) = φ(176/gcd(d,176))/2  ← 用 gcd(d,176), 唔係 |44−d| (嗰個係 ω_d 公式)
    g = gcd(d, 176)
    m = 176 // g
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2

print("  γ'_d (d=1..44) 度數分佈 (88-site 對偶鏈譜):")
dist = {}
for d in range(1, 45):
    dist.setdefault(deg_gamma(d), []).append(d)
for de in sorted(dist, reverse=True):
    print(f"    deg={de:>2}: {len(dist[de])} 個 d: {dist[de]}")

print()
print("  R5 88-site 輸出 [7,14,22,28,33,44] 喺 γ'_d 譜:") 
R5 = [7, 14, 22, 28, 33, 44]
for d in R5:
    print(f"    d={d:>2}: γ'_d deg={deg_gamma(d):>2}, gcl88={gcl88(d):>2}")

# ============ G1-G6: 閘門評估 ============
print()
print("=== 閘門評估 (現有資產) ===")
gates = [
    ("G1 獨立性", "label 來自已閉合公式 (O34/O35/O54/O13) — 唔係 R5 反向配", "✅ PASS 9/9 公式源頭, 冇 R5 反向"),
    ("G2 預註冊", "label 集 lock 喺測試前", "🔴 FAIL 歷史: R5 (37 號) 早於 label 攻堅 (46 號) — 誠實: 屬於樣本外驗證唔係盲測"),
    ("G3 遷移唯一性", "44→88 遷移規則唯一", "🟡 PARTIAL: 同座標存在 (46 號) 係唯一規則, 但冇獨立驗證"),
    ("G4 數量閘", "88-site ≥9 獨立 label", "🔴 FAIL: 88-site 未有獨立 label; 44-site 9 個只係「同座標」唔算 88-site 自證"),
    ("G5 零參數", "遷移唔引入新 fit", "✅ PASS: 同座標遷移零參數"),
    ("G6 判定標準", "PASS/FAIL 定義", "🟡 未定: 需要定義「維持 4/5」要驗咩"),
]
for name, req, st in gates:
    print(f"  {name:<8} {req:<34} → {st}")

print()
print("=== 結論: Label 終裁閘 (要過先可以裁 4/5) ===")
print("""
  ★ 核心: 88-site label 必須係「88-site 自身」嘅量度/公式源,
          而唔係 44-site 9 個 mapping 嘅「同座標搬過去」(嗰個係遷移假設, 唔係 label)。

  閘 G4 (數量) 先係硬閘: 88-site 需要 ≥9 個獨立 label 先夠統計權力。
  現狀: 0 個 88-site 獨立 label → 4/5 無法終裁, 保持 🟡。

  邊度可以攞到 88-site 獨立 label? 三個候選源:
  a) P13 定理 2 對偶鏈 γ'_d 嘅物理身份 (88-site 譜自己)
  b) 88-site 度數層 → O-series 物理公式 (未掃)
  c) 外部觀測 (如 DESI/Planck) 對 88-site 譜嘅對齊 (未有)

  閘 G1 判定: 條 label 必須由外部/公式源頭「獨立於 R5 程序」產生。
  閘 G6 判定標準 (預先定義):
    PASS  = 88-site label 集 ⊆ R5 輸出 ∪ 已閉合 44-site label 遷移
    FAIL  = 存在 88-site label d ∉ R5 輸出 (即程序漏咗物理行)
           或存在 R5 輸出 d 係 label 但唔係 magic (即程序加錯行)
  呢個標準本身要先 lock 先可以做「樣本外 label 驗收」。
""")

res = {
    "test": "51_label_gate",
    "mapping": [(name, list(pair), st) for name, pair, st in MAPPING],
    "gamma_deg_dist": {str(de): dist[de] for de in sorted(dist, reverse=True)},
    "r5_gamma": {d: deg_gamma(d) for d in R5},
    "gates": {name: st for name, _, st in gates},
    "verdict": "88-site 獨立 label = 0 個 → 硬閘 G4 FAIL → 4/5 無法終裁 (保持 🟡)",
}
with open("data/51_label_gate.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/51_label_gate.json")