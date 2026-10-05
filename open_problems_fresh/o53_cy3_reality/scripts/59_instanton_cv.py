#!/usr/bin/env python3
"""
O53 路徑一 (嚴謹): instanton fit 交叉驗證
=============================================
問題: 13-term fit R²=0.954 係 overfit (13 params / 36 pts)?

修正:
  1. A 計算: A = exp(mean(lnJ − n·lnφ))
  2. 交叉驗證: train 24 / test 12
  3. 減參數: 1, 2, 3 term fit
  4. 真正測試: 殘餘結構
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
print("O53 路徑一嚴謹: CV + 減參數")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
lnJ = np.log(J0)
lnphi = math.log(phi)

# --- [1] 修正 A ---
print("\n[1] J* = A·φ^(-n) 修正 fit:")
n_int = np.round(lnJ/lnphi)
lnA = np.mean(lnJ - n_int*lnphi)
A = math.exp(lnA)
print(f"    lnA = {lnA:.4f}, A = {A:.4f}")
pred = A * phi**(-n_int)
rel_err = np.abs(pred - J0)/J0
print(f"    mean rel err = {rel_err.mean()*100:.2f}%")
print(f"    max rel err = {rel_err.max()*100:.2f}%")
print(f"    → 之前 973 萬% 係 A 計算 bug, 修正後正常")

# 殘餘
res_ln = lnJ - (lnA - n_int*lnphi)
print(f"    mean|res_ln| = {np.abs(res_ln).mean():.4f}")
print(f"    std res_ln = {res_ln.std():.4f}")

# --- [2] 交叉驗證 ---
print("\n[2] 交叉驗證 (train 24 / test 12):")
rng = np.random.default_rng(7)
idx = rng.permutation(36)
train, test = idx[:24], idx[12:]
Ms = np.arange(1, 14)
inst_all = np.exp(-2*math.pi*Ms[None, :]/12)  # 36×13

def fit_terms(res_tr, k):
    # 揀最好 k 個 term (greedy)
    best = []
    remaining = list(range(13))
    for _ in range(k):
        best_r2 = -1
        best_t = None
        for t in remaining:
            X = np.column_stack([inst_all[:, t]] + [inst_all[:, b] for b in best])
            coef, _, _, _ = np.linalg.lstsq(X, res_tr, rcond=None)
            pred = X @ coef
            r2 = 1 - np.sum((res_tr - pred)**2)/np.sum(res_tr**2)
            if r2 > best_r2:
                best_r2, best_t = r2, t
        if best_t is not None:
            best.append(best_t)
            remaining.remove(best_t)
    return best

for k in [1, 2, 3, 5, 8]:
    terms = fit_terms(res_ln[train], k)
    Xtr = inst_all[train][:, terms]
    coef, _, _, _ = np.linalg.lstsq(Xtr, res_ln[train], rcond=None)
    pred_tr = Xtr @ coef
    r2_tr = 1 - np.sum((res_ln[train]-pred_tr)**2)/np.sum(res_ln[train]**2)
    Xte = inst_all[test][:, terms]
    pred_te = Xte @ coef
    r2_te = 1 - np.sum((res_ln[test]-pred_te)**2)/np.sum(res_ln[test]**2)
    print(f"    k={k}: terms={terms}, R²_train={r2_tr:.3f}, R²_test={r2_te:.3f}")
    if k == 3:
        check("3-term test R² > 0.3", r2_te > 0.3, f"({r2_te:.3f})")

# --- [3] 真正結構: res_ln 有冇 1/12 周期? ---
print("\n[3] res_ln 結構:")
print(f"    res_ln 排序: {np.array2string(np.sort(res_ln), precision=3)}")
print(f"    mean = {res_ln.mean():.4f}, std = {res_ln.std():.4f}")
# res 同 n_int 相關?
print(f"    corr(res, n) = {np.corrcoef(res_ln, n_int)[0,1]:.3f}")
print(f"    corr(res, q) = {np.corrcoef(res_ln, -lnJ/(2*math.pi))[0,1]:.3f}")

# --- [4] 結論 ---
print("\n[4] 結論:")
print(f"    J* ≈ A·φ^(-n) 係主結構 (A 修正後)")
print(f"    殘餘 res_ln std = {res_ln.std():.3f} (~30% 誤差)")
print(f"    instanton 級數 fit: 需要 CV 判斷")
print(f"    → 如果 test R² 高 → instanton 真")
print(f"    → 如果 test R² 低 → overfit")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
