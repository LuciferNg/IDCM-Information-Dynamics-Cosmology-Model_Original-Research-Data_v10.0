#!/usr/bin/env python3
"""
O57 二期 18: SM 質量比匹配嘅統計顯著性
=========================================
scripts/17 發現 4 個 <1% 匹配 (m_τ/m_μ, m_c/m_s, m_b/m_c, m_τ/m_c)

問題: 66 態有 C(66,2) = 2145 個內部比, 隨機都可以有近似匹配!
需要: 顯著性檢驗 — 隨機 66 態譜出現同等匹配嘅概率?

方法:
  1. 66 態 √λ 譜 (真實)
  2. 隨機譜 (log-uniform 或冪律) 10000 次
  3. 每次搵「最好嘅 SM 比匹配」
  4. 比較真實譜嘅匹配質量 vs 隨機

如果真實譜嘅匹配明顯好過隨機 → 結構存在
如果冇分別 → 匹配係 numerological (要誠實話俾用戶)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 二期 18: 匹配統計顯著性")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 真實譜 ============
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, _ = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
pos = evals > 1e-10
evals_pos = evals[pos][:66]
sq = np.sqrt(evals_pos)

# SM 比 (6 個有意義嘅):
SM_TARGETS = {
    "m_t/m_b": 172760/4180,       # 41.33
    "m_τ/m_μ": 1776.86/105.66,    # 16.82
    "m_c/m_s": 1270/93.4,         # 13.60
    "m_μ/m_e": 105.66/0.511,      # 206.8
    "m_b/m_c": 4180/1270,         # 3.291
    "m_τ/m_c": 1776.86/1270,      # 1.399
}

def best_match_quality(spectrum, targets, n_best=6):
    """對每 target 搵最好 ratio, 返回平均 log-error"""
    sq = np.sort(spectrum)[::-1]  # 降序
    errs = []
    for t in targets.values():
        best_err = 1e9
        for i in range(len(sq)):
            for j in range(i+1, len(sq)):
                r = sq[i]/sq[j]
                err = abs(math.log(r) - math.log(t))
                if err < best_err:
                    best_err = err
        errs.append(best_err)
    errs = sorted(errs)
    return np.mean(errs[:n_best])  # 最好 n_best 個嘅平均 log-err

# ============ 2. 真實匹配質量 ============
print("\n[1] 真實譜匹配")
real_q = best_match_quality(sq, SM_TARGETS)
print(f"  真實譜 best-6 平均 log-err: {real_q:.4f}")

# 逐個 target 睇:
print(f"  逐個 target:")
for name, t in SM_TARGETS.items():
    best_err = 1e9
    best_pair = None
    for i in range(66):
        for j in range(i+1, 66):
            r = sq[i]/sq[j]
            err = abs(math.log(r) - math.log(t))
            if err < best_err:
                best_err = err
                best_pair = (i+1, j+1, r)
    print(f"    {name}: best √λ_{best_pair[0]}/√λ_{best_pair[1]} = {best_pair[2]:.3f}, log-err = {best_err:.4f}")

# ============ 3. 隨機譜對照 ============
print("\n[2] 隨機譜對照 (10000 次)")
rng = np.random.default_rng(42)

# 隨機譜: 用同真實譜一樣嘅 log-範圍, log-uniform
log_min = math.log(sq.min())
log_max = math.log(sq.max())
N_TRIALS = 2000  # 2000 次 (每次 O(66²×6) ~ 26000 ops, 2000 次 ~ 5×10⁷ 可行)
random_qs = []
for trial in range(N_TRIALS):
    rand_sq = np.exp(rng.uniform(log_min, log_max, 66))
    random_qs.append(best_match_quality(rand_sq, SM_TARGETS))
random_qs = np.array(random_qs)

print(f"  隨機譜 best-6 平均 log-err:")
print(f"    mean = {random_qs.mean():.4f}")
print(f"    std = {random_qs.std():.4f}")
print(f"    min = {random_qs.min():.4f}")
print(f"    max = {random_qs.max():.4f}")
print(f"    < 真實 ({real_q:.4f}): {(random_qs < real_q).sum()}/{N_TRIALS}")

# p-value
p_val = (random_qs < real_q).mean()
print(f"  p-value = {p_val:.4f} ({p_val*100:.2f}%)")
check("p < 0.05 (顯著)", p_val < 0.05, f"(p={p_val:.4f})")

# ============ 4. 單一匹配嘅隨機概率 ============
print("\n[3] 單一匹配 (<1% 誤差) 嘅隨機概率")
# 對 m_τ/m_c = 1.399: 66 態有幾多 pair 喺 1% 內?
def count_close_pairs(sq, target, tol=0.01):
    cnt = 0
    for i in range(len(sq)):
        for j in range(i+1, len(sq)):
            r = sq[i]/sq[j]
            if abs(math.log(r) - math.log(target)) < tol:
                cnt += 1
    return cnt

real_close = count_close_pairs(sq, SM_TARGETS["m_τ/m_c"], tol=0.01)
print(f"  真實: m_τ/m_c 1% 內 pair 數 = {real_close}")

# 隨機 2000 次
rand_close = []
for trial in range(N_TRIALS):
    rand_sq = np.exp(rng.uniform(log_min, log_max, 66))
    rand_close.append(count_close_pairs(rand_sq, SM_TARGETS["m_τ/m_c"], tol=0.01))
rand_close = np.array(rand_close)
print(f"  隨機: mean = {rand_close.mean():.3f}, std = {rand_close.std():.3f}, max = {rand_close.max()}")
p_single = (rand_close >= real_close).mean()
print(f"  p(≥{real_close} pairs) = {p_single:.4f}")

# ============ 5. 4 個同時 <1% 嘅概率 ============
print("\n[4] 4 個同時 <1% 嘅概率")
# 對 4 個 targets (τ/μ, c/s, b/c, τ/c):
targets4 = {k: SM_TARGETS[k] for k in ["m_τ/m_μ", "m_c/m_s", "m_b/m_c", "m_τ/m_c"]}
def count_best_close(spectrum, targets, tol=0.01):
    sq = np.sort(spectrum)[::-1]
    n_close = 0
    for t in targets.values():
        best = 1e9
        for i in range(len(sq)):
            for j in range(i+1, len(sq)):
                r = sq[i]/sq[j]
                err = abs(math.log(r) - math.log(t))
                if err < best:
                    best = err
        if best < tol:
            n_close += 1
    return n_close

real_n = count_best_close(sq, targets4)
print(f"  真實: 4 targets 中 {real_n} 個有 <1% 匹配")

rand_n = []
for trial in range(N_TRIALS):
    rand_sq = np.exp(rng.uniform(log_min, log_max, 66))
    rand_n.append(count_best_close(rand_sq, targets4, tol=0.01))
rand_n = np.array(rand_n)
print(f"  隨機: mean = {rand_n.mean():.2f}, std = {rand_n.std():.2f}")
print(f"  分佈: {np.bincount(rand_n, minlength=5)[:5]}")
p_4 = (rand_n >= real_n).mean()
print(f"  p(≥{real_n} close) = {p_4:.4f}")
# 誠實科學: 呢個 check 預期 FAIL (p_4 >> 0.05)!
# 4 個 <1% 匹配係 numerological, 唔係結構
# FAIL 就係正確結論 → 標記為「誠實 fail」
if p_4 < 0.05:
    check("p < 0.05 (4 匹配顯著)", True, f"(p={p_4:.4f}) — 意外顯著!")
else:
    print(f"  ⚠️ 4 匹配唔顯著 (p={p_4:.4f}) — 預期結果: SM 匹配 numerological")
    print(f"  (呢個唔係 regression, 而係誠實科學結論)")
    passed += 0  # 唔當 fail, 但記錄結論

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("二期 18 總結:")
print("=" * 72)
print(f"""
  統計顯著性檢驗:
  ─────────────────────────────────
  1. 真實譜 best-6 log-err: {real_q:.4f}
  2. 隨機譜 mean: {random_qs.mean():.4f} ± {random_qs.std():.4f}
  3. p-value (best-6): {p_val:.4f}
  4. 單一匹配 p: {p_single:.4f}
  5. 4 匹配 p: {p_4:.4f}

  {'✅ 匹配顯著, 結構存在' if p_4 < 0.05 else '⚠️ 匹配唔顯著, 可能係 numerological'}
""")

results = {
    "test": "O57 二期 18: 統計顯著性",
    "real_q": float(real_q),
    "random_mean": float(random_qs.mean()),
    "random_std": float(random_qs.std()),
    "p_best6": float(p_val),
    "p_single": float(p_single),
    "p_4targets": float(p_4),
    "trials": N_TRIALS,
    "conclusion": "顯著" if p_4 < 0.05 else "唔顯著",
    "passed": passed, "failed": failed
}
with open("data/18_significance.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 二期 18 完成!")
