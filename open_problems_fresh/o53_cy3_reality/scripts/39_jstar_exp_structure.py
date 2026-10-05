#!/usr/bin/env python3
"""
O53 開放 2 深化: J* 原序 φ 指數 26/36 近整數
================================================
發現:
  - J* 排序 ≠ φ^(-k/12) (81.6% 誤差 — 假相關)
  - 但原序 φ 指數 26/36 近整數 (72%)!

分析:
  1. J* 嘅 φ 指數近整數有幾強?
  2. 指數集有冇結構 (重複值)?
  3. 指數 vs modulus index 有冇模式?
  4. J* = φ^(-n) 精確形式?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 2: J* φ 指數原序結構")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J = np.array(jstar['Jstar_36D'])

exps = np.log(1/J) / math.log(phi)

print("\n[1] J* 原序 φ 指數:")
for i in range(36):
    n = round(exps[i])
    d = abs(exps[i] - n)
    flag = "✅" if d < 0.3 else ""
    print(f"    J[{i:2d}] = {J[i]:8.5f}  φ^({exps[i]:6.3f}) → φ^{n:3d} (差 {d:.3f}) {flag}")

# --- [1] 統計 ---
print("\n[2] 近整數統計:")
near = np.abs(exps - np.round(exps)) < 0.3
print(f"    近整數: {near.sum()}/36 = {near.sum()/36*100:.0f}%")
# 隨機期望: 0.3 窗口 → 60% (兩邊) 實際 ~30%
# 但 φ 指數本身分佈廣, 近整數應該低於隨機?
rng = np.random.default_rng(0)
rand_exps = rng.uniform(6, 14, 10000)
rand_near = np.mean(np.abs(rand_exps - np.round(rand_exps)) < 0.3)
print(f"    隨機對照 (uniform 6-14): {rand_near*100:.0f}%")
check("近整數 > 隨機對照", near.mean() > rand_near, f"({near.mean()*100:.0f}% vs {rand_near*100:.0f}%)")

# --- [2] 指數集 ---
print("\n[3] 近整數指數集:")
n_vals = np.round(exps[near]).astype(int)
print(f"    指數值: {sorted(n_vals.tolist())}")
print(f"    重複: " + ", ".join(f"{v}×{list(n_vals).count(v)}" for v in sorted(set(n_vals))))

# --- [3] 指數 vs index ---
print("\n[4] 指數 vs modulus index:")
print(f"    index 0-11: {[round(exps[i]) for i in range(12)]}")
print(f"    index 12-23: {[round(exps[i]) for i in range(12, 24)]}")
print(f"    index 24-35: {[round(exps[i]) for i in range(24, 36)]}")

# --- [4] J* = φ^(-n) 精確? ---
print("\n[5] J* 係咪 φ^(-n) (n 整數)?")
J_pred = phi ** (-np.round(exps))
errs = np.abs(J_pred - J) / J
print(f"    平均誤差: {errs.mean()*100:.1f}%")
print(f"    最大誤差: {errs.max()*100:.1f}%")
check("平均誤差 < 40%", errs.mean() < 0.4, f"({errs.mean()*100:.1f}%)")

# --- [5] 對比 φ^(-n/2), φ^(-n/3) ---
print("\n[6] 其他 φ 步長:")
for denom in [1, 2, 3, 4, 6, 12]:
    e = exps * denom
    near_d = np.abs(e - np.round(e)) < 0.3
    print(f"    φ^(-k/{denom}): 近整數 {near_d.sum()}/36 ({near_d.mean()*100:.0f}%)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
