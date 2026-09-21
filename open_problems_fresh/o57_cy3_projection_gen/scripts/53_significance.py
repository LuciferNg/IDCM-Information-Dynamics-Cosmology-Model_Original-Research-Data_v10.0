#!/usr/bin/env python3
"""
O57 七期 53: m2/m3 ↔ t/e 對應顯著性測試
==========================================
七期 52 發現: 模型 m2/m3 = 3.30e5 ↔ SM t/e = 3.38e5 (Δln=0.023, 2.3%)

問題: 呢個係咪巧合?
  - 5 個 volume → 10 個質量比
  - 9 個 SM 粒子 → 36 個 SM 比
  - 總共 10×36 = 360 個組合
  - 隨機機會搵到 Δln < 0.1 嘅概率?

測試:
  1. 隨機 5 個 volume (指數分佈) 重複 10000 次
  2. 每次計 best Δln
  3. 對比實際 best Δln = 0.023
  4. p-value
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 七期 53: m2/m3 ↔ t/e 顯著性")
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

# ============ 1. SM 比集合 ============
print("\n[1] SM 質量比集合")
sm = {"t": 172760, "b": 4180, "τ": 1776.86, "c": 1270, "μ": 105.66, "s": 93.4, "d": 4.67, "u": 2.16, "e": 0.511}
sm_names = list(sm.keys())
sm_ratios = []
sm_ratio_names = []
for i in range(len(sm_names)):
    for j in range(len(sm_names)):
        if sm[sm_names[i]] > sm[sm_names[j]]:
            sm_ratios.append(sm[sm_names[i]]/sm[sm_names[j]])
            sm_ratio_names.append(f"{sm_names[i]}/{sm_names[j]}")
print(f"  SM 比: {len(sm_ratios)} 個")
print(f"  範圍: {min(sm_ratios):.2e} ~ {max(sm_ratios):.2e}")

# ============ 2. 實際 V ============
print("\n[2] 實際模型")
V_actual = np.array([1.0, 9.47213595, 22.18033989, 24.79837388, 40.1246118])
m_actual = np.exp(-V_actual)
model_ratios_actual = []
for i in range(5):
    for j in range(i+1, 5):
        model_ratios_actual.append(m_actual[i]/m_actual[j])

def best_dln(V):
    """V 5 個 volume → 最好嘅 Δln"""
    m = np.exp(-V)
    mr = []
    for i in range(5):
        for j in range(i+1, 5):
            mr.append(m[i]/m[j])
    best = min(abs(math.log(mr_i) - math.log(sr)) for mr_i in mr for sr in sm_ratios)
    return best

d_actual = best_dln(V_actual)
print(f"  實際 best Δln: {d_actual:.4f}")

# ============ 3. Permutation test ============
print("\n[3] Permutation test (10000 次)")
rng = np.random.default_rng(999)
n_perm = 10000
count_better = 0
for _ in range(n_perm):
    # 隨機 5 個 volume (同實際差嘅尺度 ~ 指數)
    V_rand = np.sort(rng.exponential(15, 5))  # 類似 scale
    # 確保最小 = 1 (scale 不變性)
    V_rand = V_rand / V_rand[0]
    d_rand = best_dln(V_rand)
    if d_rand <= d_actual:
        count_better += 1
p_val = count_better / n_perm
print(f"  隨機 best Δln ≤ {d_actual:.4f}: {count_better}/{n_perm}")
print(f"  p = {p_val:.4f}")
# 誠實 fail: p=0.32 唔顯著 — 呢個係正確科學結論 (m2/m3↔t/e 可能巧合)
print(f"  → 誠實結論: p={p_val:.3f} 唔顯著, 單一匹配可能巧合 (需要全譜對應)")
check("m2/m3 ↔ t/e 顯著 (p<0.05)", p_val < 0.05, f"(p={p_val:.4f}) ← 誠實 fail: 唔顯著係正確結論")

# ============ 4. 單一比對 ============
print("\n[4] 單一比對 (m2/m3 vs t/e)")
r_model = m_actual[1]/m_actual[2]
r_sm = 172760/0.511
print(f"  m2/m3 = {r_model:.4e}")
print(f"  t/e   = {r_sm:.4e}")
print(f"  Δln = {abs(math.log(r_model)-math.log(r_sm)):.4f}")
print(f"  相對誤差 = {abs(r_model-r_sm)/r_sm*100:.2f}%")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("七期 53 總結:")
print("=" * 72)
print(f"""
  m2/m3 ↔ t/e 顯著性:
  ─────────────────────────────────
  1. 實際 best Δln: {d_actual:.4f}
  2. Permutation p: {p_val:.4f}
  3. 單一比對: {abs(math.log(r_model)-math.log(r_sm)):.4f} ({(abs(r_model-r_sm)/r_sm*100):.2f}%)

  {'✅ 顯著! 唔係巧合!' if p_val < 0.05 else '❌ 唔顯著 (可能巧合)'}
""")

results = {
    "test": "O57 七期 53: 顯著性",
    "d_actual": float(d_actual),
    "p_val": float(p_val),
    "m2m3": float(r_model),
    "te": float(r_sm),
    "passed": passed, "failed": failed
}
with open("data/53_significance.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 七期 53 完成!")
