#!/usr/bin/env python3
"""
56_g2_blind_prereg.py — G2 盲測預註冊 (2026-10-17)
==================================================
G2 閘要求: label 集 lock 喺測試前 — 唔可以用存量盤點 (53-55 號全部係後驗)。

盲測設計:
  域: 88-site 對偶鏈 k ∈ [45,87] (44-site 完全冇對應 — 真 88-site 專屬)
  規則: HALF 鏡像互補 k* = 88 − k (44-site magic {7,14,20,22,33} 嘅鏡像)
        ⟹ 盲測集 B = {88−7, 88−14, 88−20, 88−22, 88−33} = {81,74,68,66,55}
  已知剔除: k=66 = 2·33 (偶模 carry, 55 號已知 KTREE) — 剔除
  ⟹ 預註冊盲測集 B* = {81, 74, 68, 55} — 4 個候選, 預言「全部有 O-series 物理身份」
  對照: 隨機抽 4 個 k ∈ [45,87] (seed 固定, 可重現) — 預言命中率遠低

注意: k=66 已知所以剔除 — 呢個係「用已知移除」, 唔係「睇結果先改」。
     盲測集 lock 喺 script 呢一刻; 後續查身份必須喺 lock 之後。

程序:
  1. 呢個 script 輸出 BLIND_LOCK JSON (只含清單, 唔含身份)
  2. commit lock (01/00/register append-only)
  3. 之後先 grep O-series 查 B* 身份 (unlock)
"""
import json, random

print("=== G2 盲測預註冊 (2026-10-17, lock 呢一刻) ===")
print()
print("設計:")
print("  域: k ∈ [45,87] (88-site 對偶鏈真專屬域, 44-site 冇對應)")
print("  規則: HALF 鏡像互補 k* = 88 − k")
print("  44-site magic: {7, 14, 20, 22, 33}")
full_mirror = [88 - m for m in (7, 14, 20, 22, 33)]
print(f"  全鏡像集: {full_mirror}")
known = {66}   # 66 = 2·33 偶模 carry 已知 (55 號)
blind = sorted(k for k in full_mirror if k not in known)
print(f"  已剔除已知 k=66 (γ'_66 = γ_33 KTREE, 55 號)")
print(f"  ★預註冊盲測集 B* = {blind} — 4 個候選")
print(f"  預言: 4/4 全部有 O-series 物理身份 (直接公式或代數恒 etc)")
print()

# 對照集: 隨機 4 個, seed 固定
random.seed(20261017)
ctrl = sorted(random.sample(range(45, 88), 4))
print(f"  對照集 C = {ctrl} (seed=20261017 固定)")
print(f"  預言: 命中率遠低 (uniform 域隨機)")
print()

lock = {
    "test": "56_g2_blind_prereg",
    "date": "2026-10-17",
    "domain": "k in [45,87] 88-site exclusive",
    "rule": "HALF mirror complement k* = 88 - k",
    "source_magic": [7, 14, 20, 22, 33],
    "full_mirror": full_mirror,
    "excluded_known": [66],
    "exclude_reason": "66 = 2*33 even-mode carry known (55號)",
    "BLIND_SET": blind,
    "prediction": "4/4 have O-series physical identity",
    "control_set": ctrl,
    "control_prediction": "low or zero hits",
    "status": "LOCKED — do not query identity before commit",
}
with open("data/56_g2_blind_prereg.json", "w") as f:
    json.dump(lock, f, indent=1, ensure_ascii=False, default=str)
print("已寫: data/56_g2_blind_prereg.json")
print("⚠️ 未查任何身份 — lock 完成, 下一步先 commit, 之後先 grep 身份 (unlock)")