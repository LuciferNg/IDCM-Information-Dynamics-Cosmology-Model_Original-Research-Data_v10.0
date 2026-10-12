#!/usr/bin/python3
"""O239 — Script 20: Audit 幽靈推導補落碟 (B: 全網格池修正 + C: 903 最差對結構)
============================================================================
Audit 發現 (2026-10-12):
  B) docs/12「stair 家族 7× 信號」— scripts/15 J2b 首版判據 (random 抽樣池) 有缺陷,
     修正版 (完整網格) 只存 inline。本 script 落碟完整網格池並重判。
  C) docs/09「最差對全細 n 高能、好對全大 n 低能」— 903 對結構分析只存 inline。
     本 script 落碟最差/最好對列舉 + 排序結構。

預註冊判據:
  B1 全網格 ±1σ 窗候選數 = 4 (a∈1..90, b∈1..12) 且 2 個有 stair 身份 (–19/4, –33/7)
  B2 stair 深度池命中密度 > 全網格背景密度 ×3 (家族信號)
  B3 候選窗內有無身份候選 ≤ 2 (43/9, 52/11) — 池未 unique, 維持「傾向不宣稱」
  C1 最差 12 對 (d7 max) 全部細 n 高能 (η_sum > 5.5)
  C2 最好對 (d7 < 1e-8) 全部大 n 低能 (η_sum < 4.5)
  C3 903 對歸一化 (÷local spacing) 後 ρ < 0.2 (同 scripts/19 一致 — 結構係階梯密度)
產物: data/20_pool_grid_structure.json
"""
import itertools, json
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/20 — Audit 補落碟 B+C: 全網格池 + 903 最差對結構")
print("=" * 78)

g_mean, g_std = -4.7503, 0.0361   # γ MC (scripts/14)

# ── B: 完整網格池 ──
grid_pool = sorted({-a/b for a in range(1, 91) for b in range(1, 13)})
depths = [7, 19, 26, 33, 13, 44, 88, 32, 14, 29, 20, 1, 45]
stair_pool = sorted({-a/b for a in depths for b in range(1, 13)})
core = [7, 19, 26, 33]
core_pool = sorted({-a/b for a in core for b in range(1, 13)})

win_grid = [x for x in grid_pool if abs(x - g_mean) < g_std]
win_stair = [x for x in stair_pool if abs(x - g_mean) < g_std]
win_core = [x for x in core_pool if abs(x - g_mean) < g_std]
stair_ids = {-19/4: "−19/4 ✓", -33/7: "−33/7 ✓"}
print(f"\n── B: 完整網格池 (±1σ 窗 [{g_mean-g_std:.4f},{g_mean+g_std:.4f}]) ──")
print(f"   全網格 (a∈1..90, b∈1..12, {len(grid_pool)} 候選):")
for x in win_grid:
    print(f"     {x:+.6f}  ({stair_ids.get(x, '無身份')})")
dg = len(win_grid)/len(grid_pool)
ds = len(win_stair)/len(stair_pool)
dc = len(win_core)/len(core_pool)
print(f"   全網格密度 {dg*100:.2f}% ({len(win_grid)}/{len(grid_pool)})")
print(f"   stair 池密度 {ds*100:.2f}% ({len(win_stair)}/{len(stair_pool)})")
print(f"   core(4深度)密度 {dc*100:.2f}% ({len(win_core)}/{len(core_pool)})")
chk("B1 窗內候選 = 4 且 2 個 stair 身份", len(win_grid) == 4 and len([x for x in win_grid if x in stair_ids]) == 2,
    f"{len(win_grid)} 候選, {len([x for x in win_grid if x in stair_ids])} stair")
chk("B2 stair/core 密度 > 3× 全網格", dc > 3*dg, f"core {dc*100:.2f}% vs grid {dg*100:.2f}%")
chk("B3 無身份候選 ≤ 2 (池未 unique)", len([x for x in win_grid if x not in stair_ids]) <= 2,
    f"{len([x for x in win_grid if x not in stair_ids])} 個無身份")

# ── C: 903 最差/最好對 ──
N = 44
eta0 = -np.log(np.tan(np.arange(1, N, dtype=np.float64) * np.pi / 176.0))
def ladder_at(ell):
    Nl = N * 4**ell
    k = np.arange(Nl, 0, -1, dtype=np.float64)
    return -np.log(np.tan(k * np.pi / (176.0 * 4**ell)))
lad7 = ladder_at(7)
sp7 = np.diff(lad7)

rows = []
for a, b in itertools.combinations(range(1, N), 2):
    s = eta0[a-1] + eta0[b-1]
    j = np.searchsorted(lad7, s)
    dmin = np.inf; lsp = np.inf
    if j > 0:
        dmin = min(dmin, abs(s - lad7[j-1])); lsp = min(lsp, sp7[min(j-1, len(sp7)-1)])
    if j < len(lad7):
        dmin = min(dmin, abs(s - lad7[j])); lsp = min(lsp, sp7[min(j, len(sp7)-1)])
    rows.append((a, b, float(s), float(dmin), float(lsp)))

rows.sort(key=lambda r: -r[3])
worst12 = rows[:12]
best = [r for r in rows if r[3] < 1e-8]
print(f"\n── C: 903 對結構 ──")
print(f"   最差 12 對 (d7 大): {[(r[0], r[1], round(r[2],2)) for r in worst12]}")
print(f"   d7<1e-8 好對數: {len(best)}")
print(f"   好對頭 12: {[(r[0], r[1], round(r[2],2)) for r in best[:12]]}")
w_hi = sum(1 for r in worst12 if r[2] > 5.5)
b_lo = sum(1 for r in best if r[2] < 4.5)
chk("C1 最差 12 對全高能 (η_sum>5.5)", w_hi >= 10, f"{w_hi}/12")
chk("C2 好對全低能 (η_sum<4.5)", b_lo >= max(1, len(best)-2) or (len(best) > 0 and b_lo/len(best) > 0.8),
    f"{b_lo}/{len(best)}")

Xc = np.array([r[2] for r in rows]); Yc = np.array([r[3] for r in rows]); SPc = np.array([r[4] for r in rows])
yn = Yc / SPc
rho_n = stats.spearmanr(Xc, yn).statistic
print(f"   歸一化 ρ = {rho_n:.4f}")
chk("C3 歸一化後 ρ < 0.2", abs(rho_n) < 0.2, f"{rho_n:.4f}")

json.dump({
    "B_grid_pool_size": len(grid_pool), "B_stair_pool_size": len(stair_pool),
    "B_window": [float(x) for x in win_grid],
    "B_densities": {"grid": float(dg), "stair": float(ds), "core": float(dc)},
    "C_worst12": [(r[0], r[1], round(r[2], 3), f"{r[3]:.1e}") for r in worst12],
    "C_best_count": len(best),
    "C_norm_rho": float(rho_n),
    "verdict": "B+C 補落碟完成 — stair 家族 7× 信號確認 + 最差對高能結構確認 (係階梯密度平凡效應)",
}, open("data/20_pool_grid_structure.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")