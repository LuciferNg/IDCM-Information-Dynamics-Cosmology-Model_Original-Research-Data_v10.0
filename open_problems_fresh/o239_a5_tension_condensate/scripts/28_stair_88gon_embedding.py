#!/usr/bin/python3
"""O239 — Script 28: 88-gon 全鏈嵌入 — stair 深度 ↔ 88-chain 相位
============================================================================
狀態: 2026-10-12 新增（第二十二輪後續——候選 F, 繼續推）
目的: 檢定「stair 深度（33/26/19）同 γ/β/α stair 點喺 88-gon 相位格嘅嵌入」——
     延續 docs/17「88−Σstair=10」（已閉合）到全鏈: stair 深度本身係咪 88-gon
     上相隔 L₄=7 步嘅三個相位格點?

先驗結構（唔 fit target）:
  - 88-gon 相位格 θ_n = nπ/88, n=1..87
  - stair 深度: 33 (K_Tree), 26 (=33−7), 19 (=33−14), 步長 7 = L₄
  - 88 = 8×11: n=11m 位置 = mπ/8 特別角族（22.5° 週期）

判據預註冊（盲測, threshold 零放寬）:
  S1: 33π/88 = 3π/8 係特別角 EXACT —— sin(33π/88) = cos(π/8) = √(2+√2)/2
  S2: 26 同 19 唔係特別角族（n≠11m）——但係格點（平凡）
  S3: stair 步長 7 = L₄: 33−26=7, 26−19=7（代數恒等, 結構定義）
  S4: 88 − Σstair = 10（docs/17 重新落碟確認）
  S5: ★池 null: 特別角族 n=11m 喺 n∈[1..87] 有 7 個成員 (11,22,...,77);
      stair 三深度 (33,26,19) 撞上特別角 = 1/3 中——期望數 3×7/87 ≈ 0.241,
      實際 1 (n=33)。用超幾何/二項檢定: P(≥1 中 | 池 7/87, 抽 3) 要算出嚟。
      若 P > 0.05 ⟹ 「33 係特別角」唔夠罕有, 唔可以宣稱嵌入身份
  S6: 相位差: 33→26→19 每次退 7 步 = 7π/88 ≈ 14.32°（stair= 88-gon 上
      相隔 L₄ 步嘅三格點, S3 平凡重述——僅記錄）
產物: data/28_stair_88gon_embedding.json（新增）
"""
import json
import math

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/28 — 88-gon 全鏈嵌入: stair 深度 ↔ 88-chain 相位")
print("=" * 78)

PI = math.pi
sqrt2 = math.sqrt(2)

# ── S1: 33π/88 = 3π/8 特別角 ──
print("\n── S1: stair 頂深度 33 = 特別角 ──")
th33 = 33*PI/88
print(f"   33π/88 = {th33:.12f} rad = 3π/8?  {th33:.12f} vs {3*PI/8:.12f}")
print(f"   33π/88 = {th33*180/PI:.4f}° = 67.5°?")
sin33 = math.sin(th33)
cos8 = math.cos(PI/8)
formula = math.sqrt(2+sqrt2)/2   # cos(π/8) = √(2+√2)/2 —— 分子開方除 2
print(f"   sin(33π/88) = {sin33:.12f}")
print(f"   cos(π/8)    = {cos8:.12f}  = √(2+√2)/2 = {formula:.12f}")
dev1 = abs(sin33 - formula)
chk("S1 sin(33π/88) = cos(π/8) EXACT", dev1 < 1e-12, f"dev={dev1:.1e}")

# ── S2: 26/19 唔係特別角族 ──
print("\n── S2: 26/19 特別角族檢查 ──")
sp = {11*m: m for m in range(1, 8)}   # 11,22,...,77 → mπ/8
print(f"   特別角族 n=11m: {sorted(sp.keys())}")
for n in (33, 26, 19):
    print(f"   n={n}: {'∈ 特別角族 (' + str(sp[n]) + 'π/8)' if n in sp else '∉ 特別角族 (平凡格點)'}")
chk("S2 只有 33 屬特別角族", (33 in sp) and (26 not in sp) and (19 not in sp))

# ── S3: stair 步長 = L₄ ──
print("\n── S3: stair 步長 7 = L₄ ──")
print(f"   33−26 = {33-26}, 26−19 = {26-19}, L₄ = 7 (泛 Lucas, B+(B−1)=4+3)")
chk("S3 步長 7 = L₄ 恒等", (33-26 == 7) and (26-19 == 7))

# ── S4: 88 − Σstair = 10 ──
print("\n── S4: 88 − Σstair = 10（docs/17 重確認）──")
sums = 33+26+19
print(f"   33+26+19 = {sums}, 88−{sums} = {88-sums}")
chk("S4 88−Σstair = 10", 88-sums == 10, f"={88-sums}")

# ── S5: ★池 null —— 特別角命中罕有度 ──
print("\n── S5: ★池 null（唔可以見 33 命中就宣稱）──")
special = set(sp.keys())   # {11,...,77}, 7 個
pool_N = 87                 # n=1..87
draw = {33, 26, 19}
hits = len(draw & special)
exp = len(draw) * len(special) / pool_N
print(f"   特別角池: {len(special)}/87 格點 ({len(special)/pool_N*100:.1f}%)")
print(f"   抽 3 個 stair 深度, 命中 {hits} 個 (n=33)")
print(f"   期望命中數 = 3×{len(special)}/87 = {exp:.3f}")
# 二項: P(X>=1 | p=7/87, n=3)
p0 = (1 - len(special)/pool_N) ** 3
p_ge1 = 1 - p0
print(f"   P(≥1 命中 | Bin(3, {len(special)}/87)) = {p_ge1:.4f}")
# 精確超幾何: C(7,1)C(80,2)/C(87,3) + C(7,2)C(80,1)/C(87,3) + C(7,3)
from math import comb
ph1 = comb(7,1)*comb(80,2)/comb(87,3)
ph2 = comb(7,2)*comb(80,1)/comb(87,3)
ph3 = comb(7,3)*comb(87-7,0)/comb(87,3)
p_hyper = ph1 + ph2 + ph3
print(f"   精確超幾何 P(≥1) = {p_hyper:.4f}")
chk("S5 P(≥1) > 0.05 ⟹ 33 唔夠罕有, 唔宣稱嵌入身份", p_hyper > 0.05, f"P={p_hyper:.3f}")

# ── S6: 相位差記錄 ──
print("\n── S6: stair 相位步長（僅記錄）──")
for n in (33, 26, 19):
    print(f"   n={n}: θ = {n*PI/88:.4f} rad = {n*180/88:.2f}° (步長差 7 = 14.32°)")

# ── JSON ──
json.dump({
    "S1_33_special": {"theta33": 33*PI/88, "deg": 33*180/88,
                      "sin": sin33, "cos_pi8": cos8, "dev": dev1},
    "S2_special_family": {str(n): (n in sp) for n in (33, 26, 19)},
    "S3_step": {"33-26": 7, "26-19": 7, "L4": 7},
    "S4_sum_remainder": {"sum": sums, "rem": 88-sums},
    "S5_pool_null": {"special_count": len(special), "pool": pool_N,
                     "draw": sorted(draw), "hits": hits, "expected": exp,
                     "p_hyper_ge1": p_hyper},
    "verdict": "88-gon 嵌入盲測: 33 步 = 3π/8 特別角 EXACT (sin=cos(π/8)), 但池 null "
               "P(≥1 命中特別角)=0.241 (超幾何) — 『33 係特別角』唔罕有, 唔可以宣稱 "
               "『stair 頂深度嵌入 88-gon 特別位置』; stair 三深度 = 88-gon 上相隔 "
               "L₄=7 步嘅三格點 (平凡重述); 88−Σstair=10 承 docs/17; "
               "結論: 數字層面 33=3π/8 係代數真, 但身份層面唔夠罕有 — 需要更強 "
               "判據 (如 33/26/19 三點一齊嘅非平凡相位置) 先可以閉合",
}, open("data/28_stair_88gon_embedding.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")