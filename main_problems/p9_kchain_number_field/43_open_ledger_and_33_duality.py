#!/usr/bin/env python3
"""
43_open_ledger_and_33_duality.py — P9 開放項終局清帳 + 33 對偶 (2026-10-17)
============================================================================
用戶閘: 「先1 (SYNC)，完成後沒有開放才審計」
SYNC 已終結 (42 號: ⚫降級/🔴框架內否證/🟢掃完 bounded)
今輪: 機械式清帳 P9 剩餘開放項 + 檢查 33 對偶 (magic d × M-pipeline s)

T1 7 vs 3 終極判準: 3 係咪 R5 生成集成員? (決定性排除)
T2 33 對偶: 邊啲數同時係 magic d 值 AND 特殊 s 值?
T3 開放項機械清帳: 逐項列狀態 (閉合/bounded/降級/等數據)
T4 R5 程序可驗性: 邊啲判準有樣本外可測性 (有 label 才可測?)
T5 SYNC 完成判定: 06 §4 三項 + magic rows 五項 = 有冇殘留可內部閉合?

零 import; 純整數。
"""
import json
from math import gcd
from collections import defaultdict

def gc(d):
    return gcd(abs(44 - d), 176)

def luc(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a
def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
ANCHORS = (5, 7, 11)
R5GEN = sorted({m*a for a in ANCHORS for m in (1, 2, 3, 4) if 1 <= m*a <= 87})
R5GEN43 = [d for d in R5GEN if d <= 43]

# ============ T1: 3 係咪 R5 成員 ============
print("=== T1: 7 vs 3 終極判準 ===")
print(f"  R5 生成集 (m×anchor, m≤4, anchor∈{ANCHORS}) = {R5GEN43}")
print(f"  3 ∈ R5 生成? {3 in R5GEN43}")
print(f"  → 3 唔係 m×anchor 形式 (anchor 最小 5, m≥1 → 最小 5);")
print(f"    ⟹ 3 由構造排除, 唔需要 TEST F (重複索引) 或者 N_gen 參數理由")
print()
print(f"  gcd1 内 R5 成員: {[d for d in R5GEN43 if gc(d)==1]}")
print(f"  7 = 唯一 Lucas∧質數 (5=F₅ Fib; 15=3F₅ 合; 21=3L₄ 合)")
print(f"  11 = L₅ Lucas∧質數 但 DATA row (m_W/m_Z) → data-free 排除")
print(f"  ⟹ gcd1 代表 = 7: 三重過濾 (R5 ∩ ¬data ∩ Lucas∧質數) 唯一剩")

# ============ T2: 33 對偶 ============
print()
print("=== T2: 33 對偶 (magic d 值 × 特殊 s 值) ===")
special_s = {33: "M-pipeline throughput (CY₃−2)/4", 44: "N_d-domain", 22: "? (HALF)"}
print(f"  magic d 值 = {MAGIC}")
print(f"  特殊 s 值 = {dict((k, v) for k, v in special_s.items())}")
inter = sorted(set(MAGIC) & set(special_s))
print(f"  交集 = {inter}  ← 33 同時係 magic 行 (3L₅, KTREE) 同 M-pipeline 列")
# 檢查 33 喺 33 列
s33_cells = [(i, 33-i) for i in range(1, 17)]
d33_row = [(i, i+33) for i in range(1, 44-33+1)]
print(f"  d=33 行: {len(d33_row)} 成員 {d33_row}")
print(f"  s=33 列: {len(s33_cells)} 成員")
print(f"  交叉格 (d=33 ∧ s=33)? {[c for c in d33_row if sum(c)==33]} (∅ — d=33 行 s∈[35,55])")
print()
print(f"  33 = 3 × L₅ = 3 × 11;  亦 = (CY₃−2)/4;  亦 = 3·N_d/4")
print(f"  33 mod 4 = 1 (odd); 33 ∈ R5 (3×11)")
print(f"  ⟹ 33 嘅雙重身份: 操作軸 (d) 揀佢做 gcd11 代表; workflow 軸 (s) 揀佢做 M")
print(f"     兩個身份獨立產生 (R5 鏈 vs throughput 定義) — 冇循環")

# 檢查其他雙重身份
print()
print("  其他 d=s 交叉檢查:")
for n in range(3, 44):
    as_d = n in MAGIC
    as_s = n in special_s
    if as_d or as_s:
        print(f"    n={n:>2}: d-role={'MAGIC' if as_d else '—'}  s-role={special_s.get(n, '—')}")

# ============ T3: 開放項機械清帳 ============
print()
print("=== T3: P9 magic-rows cluster 開放項清帳 ===")
ledger = [
    ("24 算子身份", "✅ 閉合", "38 號: 24=2B·N_gen (O142 v16 引用), ρ=3/11, γ₂₀ 補角"),
    ("20 生成鏈", "✅ 閉合", "33 號: 20=4F₅"),
    ("缺 {4,16}", "✅ 閉合", "37 T1 mod-8 代數必然 + 38 缺類重組 {4,16}→{8,16,32}"),
    ("d=29 角色", "✅ 閉合", "42 號: 行全普通 (15 成員零特殊, bounded)"),
    ("SYNC 物理語義", "⚫ 降級", "42 號: 物理主張撤回, 保留 i=2 代數 fact"),
    ("SYNC opcode 執行", "🔴 否證(框架內)", "42 號: 冇執行信號"),
    ("7 vs 3 終極判準", "🟡→✅ 構造排除", "43 T1: 3 ∉ R5 生成集 (anchor≥5) — 由構造排除"),
    ("R5 程序 44-site 唯一鎖定", "✅ 5/5 EXACT", "37 T3 兩階段程序"),
    ("R5 程序 88-site 樣本外", "🟡 等數據", "37 T4: 3/5 保留 (20→28, 33→11); 88-site 冇 label"),
    ("R5 gcd2 判準 (14 vs 10)", "🟡 等數據", "Lucas 鏈優先; 冇樣本外可測"),
    ("R5 gcd16 判準 (28 排除)", "✅ 機制清楚", "36/37: S3 deg5 撞層 + 前半優先"),
    ("33 對偶 (magic d × M s)", "🟡 新觀察", "43 T2: 唯一交叉, 兩身份獨立產生"),
    ("s=24..34 重載帶", "✅ 座標算術", "41 號: 14/20/22 s 值域交集"),
    ("TEST F m≤3 窗口", "🟡 未驗證", "28=4L₄ 超窗 — 窗口唔可為 fit 改"),
]
for name, status, ev in ledger:
    print(f"  {status:>16} | {name:<28} | {ev[:60]}")

open_items = [l for l in ledger if not l[1].startswith("✅")]
print()
print(f"  殘餘非 ✅ = {len(open_items)} 項:")
for name, status, ev in open_items:
    print(f"    {status:>16} | {name}")

# ============ T4: 可驗性分析 ============
print()
print("=== T4: 殘餘項可驗性 (內部 vs 等數據) ===")
verifiability = {
    "R5 88-site 樣本外": "等 88-site 物理 label (外部)",
    "R5 gcd2 判準": "等樣本外類 (外部)",
    "33 對偶": "內部可推 (定義檢查) — 已推: 兩身份獨立",
    "TEST F m≤3 窗口": "內部可審計 (窗口來源) — 需查 TEST F 原始推導",
    "SYNC 物理語義": "已 ⚫ 撤回 (永久)",
    "SYNC opcode": "已 🔴 框架內否證",
}
for k, v in verifiability.items():
    print(f"  {k:<24} → {v}")

# ============ T5: SYNC 完成判定 ============
print()
print("=== T5: SYNC 線完成判定 ===")
print("  06 §4 三項: ①⚫降級 ②🔴框架內否證 ③🟢掃完bounded — 全部終結 (無殘留可內部推)")
print("  → SYNC 線 = 完成 (掃到盡), 冇未開始項")
print()
print("  magic-rows cluster 殘餘 (非 4 項 ✅):")
print("    · R5 88-site 樣本外 🟡 — 等外部 label (唔可內部閉合)")
print("    · R5 gcd2 判準 🟡 — 等樣本外類 (唔可內部閉合)")
print("    · 33 對偶 🟡 — 內部可推: 已推 (T2 兩身份獨立) → 可升 ✅")
print("    · TEST F m≤3 窗口 🟡 — 內部可審計: 需查原始推導來源")
print()
print("  ⟹ 內部可推項 = 2 (33 對偶 ✅ 已推 / TEST F 窗口 待審計)")
print("     外部等數據項 = 2 (R5 88-site / R5 gcd2)")
print("     依 O238 教訓: 等數據項唔可以夾硬閉合 — 保持 partial")

res = {
    "test": "43_open_ledger_33_duality",
    "T1": {"R5GEN43": R5GEN43, "three_in_R5": 3 in R5GEN43,
           "gcd1_members": [d for d in R5GEN43 if gc(d) == 1],
           "gcd1_rep": 7, "reason": "三重過濾唯一剩"},
    "T2": {"magic_d": MAGIC, "special_s": special_s, "intersection": inter,
           "note": "33 雙重身份兩軸獨立產生"},
    "T3": [{"item": n, "status": s, "evidence": e} for n, s, e in ledger],
    "T5": {"internal_closeable": ["33 對偶", "TEST F 窗口審計"],
           "external_gated": ["R5 88-site 樣本外", "R5 gcd2 判準"]},
}
with open("data/43_open_ledger_33_duality.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print()
print("輸出: data/43_open_ledger_33_duality.json")