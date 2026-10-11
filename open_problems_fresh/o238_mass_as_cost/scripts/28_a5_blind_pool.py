#!/usr/bin/python3
"""O238 — Script 28: A₅ 群論幾何池盲測 — 質量參數 (α/C) + 應變量 vs A₅ 池

調律者綱領: 「物質 = 挫阻缺陷張力凝聚體 ⟹ 應充滿 A₅ 廿面體本徵同構」
docs/14 LO4 已閉合 (投影 operator 不可歸約); 本 script 盲測幾何層 A₅ 池
同質量模型參數有冇結構關係.

【盲測紀律】
- 池 = A₅ 群論/幾何一次運算不變量 (子群階/類大小/irep dims/面數/阻挫/邊數…
  只准一次比值, 唔准任意深組合 — 深組合 = 撓場池, 結構動機消失)
- 目標 (先寫死, 唔改): α_S1 = 2.616977 (OLS), φ² = 2.618034 (模型輸入),
  C/M₀ = 5.255862036e-08, ε₁ = 0.00822, ε₂ = 0.01112, δ_rad = 0.0932015
- 窗: log 距離 < 1e-4, 5e-4, 1e-3 三檔 (睇密度遞減)
- null: 100k log-uniform 隨機數, 相同目標相同窗 ⟹ 期望命中 = N_pool × 2W_pool? 直接 MC
- 判準: 命中數 vs null; 單點命中 = refrain (包含唔當發現)

★ 特別聲明: φ² 本身係模型凍結值 (α=φ² 係假設, 唔係 A₅ 發現) —
  池唔放 φ², 但放 φ 相關幾何量 (廿面體座標含 φ³, 5-fold 對稱) 檢查「A₅ 幾何
  自然生成 φ 而 φ²=α」呢條鏈。
"""
import math, random, json
from itertools import combinations

# ── 1. A₅ 有理池 (一次運算) ──
# A₅ 群論不變量
A5_order = 60
subgroup_orders = [1, 2, 3, 4, 5, 6, 10, 12, 20, 60]   # A5 子群階 (真)
class_sizes = [1, 15, 20, 12, 12]                        # 1A,2A,3A,5A,5B
irrep_dims = [1, 3, 3, 4, 5]                             # ireps
aut_order = 120                                          # |Aut|=|S5| (O223 組合 Aut)
# 幾何計數 (O171/O223 實錘)
V60, E120, F62 = 60, 120, 62
faces = [20, 30, 12]                                     # △ □ ⬠
frust = 32                                               # 阻挫邊
chi_ = 2
Nd = 44                                                  # N_d = 88/2
B = 4
# 基礎池
base = set(subgroup_orders + class_sizes + irrep_dims +
           [aut_order, V60, E120, F62, frust, chi_, Nd, B, 88, 421])
# 一次比值 (a/b, a≠b) — 唔做第二層
ratios = set()
bl = sorted(base)
for a in bl:
    for b in bl:
        if b != 0 and a != b:
            r = a / b
            ratios.add(round(r, 12))
base_all = base | set(round(r, 12) for r in [60/32, 32/60, 20/12, 12/20, 30/12, 12/30,
                                             120/32, 32/120, 62/60, 60/62, 44/32, 32/44,
                                             421/60, 60/421, 120/88, 88/120])
pool = sorted(base_all | ratios)
print(f"A₅ 池大小: {len(pool)} (基礎 {len(base)} + 一次比值 {len(ratios)})")

# ── 2. 目標 ──
targets = {
    "α_S1 (OLS)": 2.616977,
    "φ² (模型輸入)": (1 + math.sqrt(5)) ** 2 / 4,
    "C/M₀": 5.255862036e-08,
    "ε₁ 應變(短邊)": 0.00822,
    "ε₂ 應變(長邊)": 0.01112,
    "δ_rad 手性角": 5.3401 * math.pi / 180,   # 0.0932015
}
wins = [1e-4, 5e-4, 1e-3]
print(f"\n目標: { {k: ('%.6g' % v) for k, v in targets.items()} }")

def hits_for(tval, win):
    return sum(1 for p in pool if abs(math.log(p / tval)) < win)

print("\n═══ 命中表 (A₅ 池 vs 目標) ═══")
hit_rows = []
for tname, tval in targets.items():
    row = [tname, "%.8g" % tval]
    for w in wins:
        h = hits_for(tval, w)
        row.append(f"{h}/{len(pool)}")
        if h and tname not in ("α_S1 (OLS)", "φ² (模型輸入)"):
            got = [p for p in pool if abs(math.log(p / tval)) < w]
            row.append(f"  → {got[:3]}")
    print(f"  {'%-22s' % tname}: " + "  ".join(row))
    hit_rows.append((tname, tval))

# ── 3. null: 同大小 log-uniform 隨機池 ──
random.seed(20261011)
loglo, loghi = math.log(min(pool)), math.log(max(pool))
n_mc = 20000
print(f"\n═══ MC null ({n_mc} 次, 池大小 {len(pool)}) ═══")
for tname, tval in targets.items():
    for w in wins[:2]:
        hits_mc = 0
        for _ in range(n_mc):
            rp = [math.exp(random.uniform(loglo, loghi)) for _ in range(len(pool))]
            if sum(1 for p in rp if abs(math.log(p / tval)) < w) > 0:
                hits_mc += 1
        prob_any = hits_mc / n_mc
        obs = hits_for(tval, w)
        if obs or prob_any < 0.05:
            print(f"  {tname:20s} win={w:.0e}: 觀測 {obs} 命中, null P(≥1命中)={prob_any:.4f}")

# ── 4. 特別: φ 幾何鏈 → φ²=α? ──
print("\n═══ φ 幾何鏈檢定 ═══")
# 廿面體頂點座標含 φ³; 5-fold: φ = 2cos(π/5); A5 幾何角: 3π/5, 2π/5, π/5
for expr_name, val in [
    ("φ = 2cos(π/5)", 2*math.cos(math.pi/5)),
    ("φ³ = 2+√5", (1+math.sqrt(5))**3/8),
    ("28° 閾值邊餘: 26.0913°/28°", 26.0913/28),
    ("26.1664°/26.0913° 長短比", 26.1664/26.0913),
    ("32 阻挫/20△", 32/20),
    ("(32/120)²", (32/120)**2),
    ("F₇=13 上界/60", 13/60),
    ("9 費米子/32 阻挫", 9/32),
]:
    d_alpha = abs(math.log(val / ((1+math.sqrt(5))**2/4)))
    d_c = abs(math.log(val / 5.255862036e-08))
    tag = ""
    if d_alpha < 1e-2: tag = " ← α 鏈?"
    if d_c < 1e-2: tag = " ← C 鏈?"
    print(f"  {expr_name:26s} = {val:.8g}  (α dev {d_alpha*100:.2f}%, C dev {d_c*100:.2f}%){tag}")

# ── 存檔 ──
out = {
    "pool_size": len(pool),
    "targets": {k: v for k, v in targets.items()},
    "hits": {t: {str(w): hits_for(v, w) for w in wins} for t, v in targets.items()},
}
with open("data/28_a5_blind_pool.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print("\nRESULT: 盲測完成 — 命中率 vs null 比較 (詳見輸出)")
print("判準: 任何單點命中 = refrain (池密度效應, 唔當發現); 只有「命中數超出 null 很多」先算結構")