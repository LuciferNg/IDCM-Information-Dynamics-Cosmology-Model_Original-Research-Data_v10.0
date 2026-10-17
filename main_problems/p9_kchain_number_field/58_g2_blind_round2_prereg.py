#!/usr/bin/env python3
"""
58_g2_blind_round2_prereg.py — G2 第二輪盲測預註冊 (2026-10-17)
================================================================
第一輪 (56/57): B*={55,68,74,81} 3/4 vs C={46,56,62,73} 1/4, n=8 Fisher p≈0.49
第二輪目標: 增加樣本, 收集統計權力。新規則 — 唔重用 HALF mirror (已有結果)。

規則二: Fib mirror — k* = 88 − F_m (Fib 序列), 域 [45,87]
  F₅=5→83, F₆=8→80, F₇=13→75, F₈=21→67, F₉=34→54, F₁₀=55→33(出域剔除)
  ⟹ 盲測集 B2 = {54, 67, 75, 80, 83} — 5 個候選
  (F₁₀=55→33 因為 33≤44 唔喺 [45,87] 域, 剔除 — 域規則, 唔係睇結果)
預言: 5/5 全部有 O-series 物理身份 (直接公式或代數恒等)
對照: C2 = 隨機 5 個 k ∈ [45,87] (seed=20261018 固定, 可重現)

已知剔除 (第一輪已查/已知): {55,68,74,81,46,56,62,73,66} — B2 全部未查
"""
import json, random

print("=== G2 第二輪盲測預註冊 (2026-10-17, lock 呢一刻) ===")
print()
print("規則二: Fib mirror — k* = 88 − F_m, 域 [45,87]")
Fibs = [(5, 5), (6, 8), (7, 13), (8, 21), (9, 34), (10, 55)]
full = []
for m, F in Fibs:
    k = 88 - F
    full.append((m, F, k, "in" if 45 <= k <= 87 else "✗出域"))
    print(f"  F_{m}={F:<2} → k*={k:>2}  {'✓' if 45<=k<=87 else '✗ 出域'}")

B2 = sorted(k for _, _, k, tag in full if tag == "in")
print(f"\n  ★預註冊盲測集 B2 = {B2} — 5 個候選 (全部未在第一輪查過)")
print(f"  預言: 5/5 全部有 O-series 物理身份")
print()

# 已知 + 第一輪查過
consumed = {55, 68, 74, 81, 46, 56, 62, 73, 66}
pool = [k for k in range(45, 88) if k not in consumed and k not in set(B2)]
random.seed(20261018)
ctrl2 = sorted(random.sample(pool, 5))
print(f"  第一輪已消費 k: {sorted(consumed)}")
print(f"  對照集 C2 = {ctrl2} (seed=20261018, 由未消費池抽)")
print(f"  預言: 命中率遠低 (uniform 域隨機)")
print()

lock = {
    "test": "58_g2_blind_round2_prereg",
    "date": "2026-10-17",
    "round": 2,
    "rule": "Fib mirror k* = 88 - F_m, domain [45,87]",
    "BLIND_SET": B2,
    "prediction": "5/5 have O-series physical identity",
    "control_set": ctrl2,
    "control_prediction": "low or zero hits",
    "excluded_known": sorted(consumed),
    "status": "LOCKED — do not query identity before commit",
}
with open("data/58_g2_blind_round2_prereg.json", "w") as f:
    json.dump(lock, f, indent=1, ensure_ascii=False, default=str)
print("已寫: data/58_g2_blind_round2_prereg.json")
print("⚠️ 未查任何身份 — lock 完成, 下一步先 commit, 之後先 grep (unlock)")