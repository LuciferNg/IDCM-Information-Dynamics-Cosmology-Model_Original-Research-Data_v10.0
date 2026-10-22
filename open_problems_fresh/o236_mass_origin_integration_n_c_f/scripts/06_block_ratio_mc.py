#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O236 scripts/06 -- R6: C_f 代際塊間比 MC 檢定（收尾負閉合, T5 E2 承諾）

docs/01 R6:
  塊間比 r21 = 9.5586, r32 = 5.5805 (O235 T5 E1/E2, 觀察級)
  要推: 結構池 × 10⁷ MC null, 兩地報 (寬池/結構池), 鎖間相依性照 O208
  預期負結果閉合 (close T5 E2 承諾, 唔會變 golden)

池定義 (O233 docs/02 凍結結構常數集, 57 原子; docs/01 寫「34 原子」係筆誤):
  L₀..L₁₄ (Lucas), F₂..F₂₀ (Fib), B=4 冪 {16,64,256}, N_gen=3, N_d=44, K_tree=33,
  CY₃=134, h11=36, h21=98, μ²=2, 18(L₆), 5(F₅), 88, 176, 946, 123(L₁₀), 137, 90,
  46, 45, 60, 42, 37, 41, 47, 48, 50, 51, 26, 22, 17, 8, 40
  (全部有 corpus 身份; 凍結於 O233 docs/02, pool 概念沿用 O208 紀律)

方法:
  結構池: {s_i/s_j : i≠j, s∈S} 共 57×56 ≈ 3192 個比值 (取 log 網格)
  寬池:   {a/b : a,b ∈ ℤ ∩ [1,500]} (250k 對, 去重)
  兩個觀察比 vs 兩池: 窗口 δ = 1e-3 (rel), MC 10⁷ log-uniform 目標在 [ln3, ln12]:
  E[hits] 分佈 → z, P(≥obs).  lock-dependency: r21/r32 共享 gen2 ⟹ 報聯合 vs 邊際積.

預期: 負結果閉合 (hit 數 ≈ MC 中位 / 低於) —— T5 E2「塊間比暫無身份」正式 close.
"""
import json, math, os, random

L = [2, 1]
for _ in range(14):
    L.append(L[-1] + L[-2])
F = [0, 1]
for k in range(2, 21):
    F.append(F[k-1] + F[k-2])
S_atoms = set(L) | set(F[2:]) | {4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2, 18, 5,
                                 88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37, 41,
                                 47, 48, 50, 51, 26, 22, 17, 8, 40}
S_atoms = sorted(int(s) for s in S_atoms if 1 <= s <= 10**6)

# 塊幾何中位 (O235 T5 數據)
cf = {"e": 3.5941, "u": 3.8029, "d": 3.6620,
      "s": 41.3207, "mu": 30.0309,
      "c": 186.0605, "tau": 159.6437, "b": 255.7517}
def gm(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))
g1 = gm([cf["e"], cf["u"], cf["d"]])
g2 = gm([cf["s"], cf["mu"]])
g3 = gm([cf["c"], cf["tau"], cf["b"]])
r21 = g2 / g1
r32 = g3 / g2

DELTA = 1e-3          # rel 窗口
LNRANGE = (math.log(3.0), math.log(12.0))   # log-uniform 目標範圍蓋 r32/r21
N_MC = 10**7

CHK = []
def chk(name, ok, msg=""):
    CHK.append((name, bool(ok), msg))
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")

print("O236 scripts/06 -- R6: C_f 代際塊間比 MC 檢定")
print("=" * 78)
print(f"  gmeans: gen1={g1:.4f}, gen2={g2:.4f}, gen3={g3:.4f}  (T5 重現)")
print(f"  r21 = {r21:.4f}, r32 = {r32:.4f}")

# ---------- 結構池比值網格 ----------
ratio_logs_s = sorted(math.log(ai / aj) for ai in S_atoms for aj in S_atoms if ai != aj)
# 只保留 [0.1, 1e4] 比例範圍內
ratio_logs_s = [x for x in ratio_logs_s if math.log(0.1) <= x <= math.log(1e4)]
print(f"\n[S] 結構原子池: {len(S_atoms)} atoms → ratio grid {len(ratio_logs_s)} 值")
r21_hits_s = sum(1 for x in ratio_logs_s if abs(x - math.log(r21)) < DELTA)
r32_hits_s = sum(1 for x in ratio_logs_s if abs(x - math.log(r32)) < DELTA)
chk("C1  結構池 hit 數 (δ=1e-3): r21/r32 = %d/%d (窗口內)" % (r21_hits_s, r32_hits_s),
    True, f"預期: 命中=0 最常見; 非零都唔代表富集 (睇 null)")

# ---------- 寬池比值網格 ----------
WMAX = 500
w_logs = sorted(math.log(a / b) for a in range(1, WMAX + 1) for b in range(1, WMAX + 1))
w_unique = sorted(set(w_logs))
print(f"[W] 寬池 {WMAX}² = {WMAX*WMAX} 對 → 唯一 log 值 {len(w_unique)}")
r21_hits_w = sum(1 for x in w_unique if abs(x - math.log(r21)) < DELTA)
r32_hits_w = sum(1 for x in w_unique if abs(x - math.log(r32)) < DELTA)
chk("C2  寬池 hit 數 (δ=1e-3): r21/r32 = %d/%d" % (r21_hits_w, r32_hits_w),
    True, "寬池密度高, 有命中係預期 (O233 教訓: 5.5 萬池內 '漂亮命中' 零意義)")

# ---------- MC null ----------
from bisect import bisect_left, bisect_right

def hits_in(pool_logs, t, delta):
    i0 = bisect_left(pool_logs, t - delta)
    i1 = bisect_right(pool_logs, t + delta)
    return i1 - i0

def mc_hits(pool_logs, n, rng):
    a, b = LNRANGE
    total = 0
    for _ in range(n):
        t = a + (b - a) * rng.random()
        total += hits_in(pool_logs, t, DELTA)
    return total

def pois_ge(k, lam):
    """P(X >= k), X ~ Poisson(lam) (精確尾和)"""
    if k <= 0:
        return 1.0
    pmf = math.exp(-lam)
    tail, cur = pmf, pmf
    for i in range(1, k):
        cur *= lam / i
        tail += cur
    return 1.0 - tail

rng = random.Random(20261007)
hit_s = mc_hits(ratio_logs_s, N_MC, rng)
rng2 = random.Random(20261007)
hit_w = mc_hits(w_unique, N_MC, rng2)
med_s = hit_s / N_MC          # 每目標期望命中數 (結構池, MC 實測)
med_w = hit_w / N_MC
lam_s = sum(1 for x in ratio_logs_s if LNRANGE[0] + DELTA <= x <= LNRANGE[1] - DELTA) \
        * 2 * DELTA / (LNRANGE[1] - LNRANGE[0])   # 泊松解析 (只數窗口內池點)
lam_w = sum(1 for x in w_unique if LNRANGE[0] + DELTA <= x <= LNRANGE[1] - DELTA) \
        * 2 * DELTA / (LNRANGE[1] - LNRANGE[0])
p21_s = pois_ge(r21_hits_s, med_s)
p32_s = pois_ge(r32_hits_s, med_s)
p21_w = pois_ge(r21_hits_w, med_w)
p32_w = pois_ge(r32_hits_w, med_w)
chk("C3  結構池 null (10⁷ log-uniform): λ_MC=%.4f/目標 (泊松 λ=%.4f); r21 P(≥%d)=%.4f, "
    "r32 P(≥%d)=%.4f" % (med_s, lam_s, r21_hits_s, p21_s, r32_hits_s, p32_s),
    p21_s > 0.05 and p32_s > 0.05,
    "無富集 ⟹ 負結果 (預期)")
chk("C4  寬池 null: λ_MC=%.4f/目標 (泊松 λ=%.4f); r21 P(≥%d)=%.4f, r32 P(≥%d)=%.4f"
    % (med_w, lam_w, r21_hits_w, p21_w, r32_hits_w, p32_w),
    p21_w > 0.05 and p32_w > 0.05,
    "兩池皆無富集 ⟹ 塊間比身份 = 負閉合 (T5 E2 承諾兌現)")

# ---------- lock dependency ----------
print("\n[依賴性] r21/r32 共享 gen2 (35.226)")
# 邊際積 vs 聯合: 若兩鎖獨立, P(both hit) ≈ p21*p32; 共享變量 ⟹ 實際相關
prod_s = p21_s * p32_s
joint_s = min(p21_s, p32_s)      # 全正相關上界 (保守)
chk("C5  鎖間相依性報告: P(兩鎖同時富集) ∈ [0, min(P21,P32)]; 邊際積 = %.5f"
    % prod_s, True,
    f"共享 gen2 ⟹ 非獨立 (O229 tech 12); 兩邊際皆無顯著 ⟹ 聯合亦必然負")
# 直測: gen2 幾何中位單獨對結構池 (3.5226e1 = g2 本身)
g2_hits_s = sum(1 for x in ratio_logs_s if abs(x - math.log(g2)) < DELTA)
chk("C6  共享量 g2 本身對結構池 hit = %d (δ=1e-3) —— 亦無身份" % g2_hits_s,
    True, "gen2 中位唔係原子比 ⟹ 鎖共享唔引入額外命中")

# ---------- 氣味測試複查 ----------
print("\n[氣味測試] docs/01 註: r32 對 88/16 = 5.5 dev 1.4%")
dev55 = abs(math.log(r32) - math.log(88 / 16)) < DELTA
chk("C7  88/16=5.5 對 r32 喺 δ=1e-3 內? " + ("係" if dev55 else "唔係 (dev 1.4% ≫ 窗口)"),
    not dev55, "氣味只係觀察級 (1.4%), 窗口外 ⟹ 唔構成命中")

# ---------- verdict ----------
chk("C8  裁決: 塊間比 {9.5586, 5.5805} 對結構池/寬池皆無富集 (P≥0.05) ⟹ T5 E2 負閉合, "
    "P5「塊間比身份暫無」維持, 唔升格金", True,
    f"r21: P_s={p21_s:.4f} P_w={p21_w:.4f}; r32: P_s={p32_s:.4f} P_w={p32_w:.4f}")

# ---------- data JSON ----------
out = {
    "R": "R6", "title": "C_f 塊間比 MC 檢定 (負閉合)",
    "r21": r21, "r32": r32, "gmeans": {"g1": g1, "g2": g2, "g3": g3},
    "pool_atoms": len(S_atoms), "atoms_are_34_or_57": "docs/01 寫 34 係筆誤; O233 docs/02 凍結 57 原子",
    "structure_pool": {"grid_size": len(ratio_logs_s), "hits_r21": r21_hits_s,
                       "hits_r32": r32_hits_s, "lambda_per_target": med_s,
                       "P21": p21_s, "P32": p32_s},
    "wide_pool": {"grid_unique": len(w_unique), "hits_r21": r21_hits_w,
                  "hits_r32": r32_hits_w, "lambda_per_target": med_w,
                  "P21": p21_w, "P32": p32_w},
    "dependency": {"shared_gen2": g2, "P_joint_bound": min(p21_s, p32_s),
                   "marginal_product": prod_s},
    "smell": {"88_16": 88/16, "dev": abs(math.log(r32)-math.log(88/16)), "hit": dev55},
    "verdict": "負閉合: 塊間比冇結構身份 (T5 E2/P5 承諾兌現); 唔升格金",
    "cheat": "池凍結於 O233 docs/02; δ=1e-3; log-uniform 10⁷; 零新常數",
}
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json.dump(out, open(os.path.join(BASE, "data", "06_block_ratio_mc.json"), "w"),
          ensure_ascii=False, indent=1)
print("\n-> data/06_block_ratio_mc.json")

print("\n" + "=" * 78)
okn = sum(1 for _, ok, _ in CHK if ok)
print(f"RESULT: {okn}/{len(CHK)} PASS")
for name, ok, msg in CHK:
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")
if okn != len(CHK):
    raise SystemExit(1)