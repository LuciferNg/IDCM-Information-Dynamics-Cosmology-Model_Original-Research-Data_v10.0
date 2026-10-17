# G2 第二輪盲測預註冊 — 58 號 (2026-10-17)

> **G2 第一輪 (56/57)**: B\* 3/4 vs C 1/4, n=8 Fisher p≈0.49 — 方向支持冇權力
> **第二輪目標**: 增加樣本收集統計權力, 新規則唔重用 HALF mirror
> **Script**: `58_g2_blind_round2_prereg.py` → `data/58_g2_blind_round2_prereg.json`
> **狀態**: 🔒 **LOCKED — 未查任何身份**

---

## 規則二: Fib mirror

```
k* = 88 − F_m（Fib 序列）, 域 [45,87]（88-site 專屬）
  F₅=5→83  F₆=8→80  F₇=13→75  F₈=21→67  F₉=34→54  ✓ 全部在域
  F₁₀=55→33 ✗ 出域剔除（33≤44, 88-site 專屬域以外）
★ 預註冊盲測集 B2 = {54, 67, 75, 80, 83} — 5 個候選
★ 預言: 5/5 全部有 O-series 物理身份
對照 C2 = {52, 59, 82, 84, 86}（seed=20261018, 未消費池抽）
```

## 已知剔除（第一輪已查 + 已知）

```
已消費: {46, 55, 56, 62, 66, 68, 73, 74, 81}
B2 全部未查過 — 規則由 Fib 定義, 唔受預期結果影響
```

## 點解 Fib mirror（結構動機, 非目標驅動）

```
· 44-site magic 已含 Fib/Lucas 鏈（20 = 4F₅, 28 = 4L₄）
· F_m 喺 88-site 域嘅 mirror（88−F）係自然延伸
· 同 HALF mirror（k*=88−k）同族但唔重複 — 第二輪獨立規則
· 唔係睇咗 O-series 先揀 — 預註冊 lock 喺查身份之前
```

## 程序紀律（同第一輪）

```
1. 🔒 呢個 md/json = lock（commit 一刻先算 lock）
2. commit 之後先可以做身份查詢（unlock）
3. 命中判準（預註冊）: sin(kπ/176) 或 4sin² 出現喺 O-series 已閉合 md/scripts
4. 解鎖後唔可以改 B2
5. 兩輪合併統計（n=18）評估 G2 — 若仍然冇權力, G2 維持 🟡
```

## 檔案
```
58_g2_blind_round2_prereg.py
data/58_g2_blind_round2_prereg.json
```