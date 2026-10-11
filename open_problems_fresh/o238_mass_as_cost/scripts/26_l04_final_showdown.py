#!/usr/bin/python3
"""O238 — Script 26: LO4 收尾對決 — 全 7 個高共線規則嘅質量 fit RMS

scripts/22: 7 個 9-元素規則全部 R²>0.95 (共線層面數論係後見)
scripts/23: {1..9} vs A₅ — A₅ RMS 0.546 vs 1.102 (2×) — 但只對比咗 1 個
本 script: 補齊其餘 5 個規則嘅質量 fit — 證明 A₅ 喺『質量 fit 層』唯一特權

對照: 7 規則 = primes∪sq≤13 (A₅), coprime11≤9, primepower≤13, odd≤15?
      由 scripts/22 輸出確認邊 7 個
判準: 若只有 A₅ RMS<0.60 而其餘全部 >0.90 ⟹ 質數∪平方 = 質量 fit 層唯一規則
      ⟹ LO4 閉合: 投影 operator = 數論選擇 (質數∪平方) ∩ 共線, 質量訊息喺數論選擇
"""
import numpy as np, math, json

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
Eee = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = Eee[:, None] - Eee[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
logd9 = np.log([admn[n-1] for n in SEL9])
logg9 = np.log([gam[n-1] for n in SEL9])

def is_prime(k):
    if k < 2: return False
    for d in range(2, int(math.sqrt(k)) + 1):
        if k % d == 0: return False
    return True
def is_sq(k):
    r = int(round(math.sqrt(k)))
    return r * r == k
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34]
LUC = [2, 1, 3, 4, 7, 11, 18, 29, 47]
def gcd(a, b):
    while b: a, b = b, a % b
    return a

# 全部 9-元素規則 (scripts/22 規則庫重現)
rules_all = {}
for ub in range(7, 17):
    rules_all[f"primes≤{ub}"] = [k for k in range(1, ub+1) if is_prime(k)]
    rules_all[f"squares≤{ub}"] = [k for k in range(1, ub+1) if is_sq(k)]
    rules_all[f"primes∪sq≤{ub}"] = [k for k in range(1, ub+1) if is_prime(k) or is_sq(k)]
    rules_all[f"odd≤{ub}"] = [k for k in range(1, ub+1) if k % 2 == 1]
    rules_all[f"even≤{ub}"] = [k for k in range(1, ub+1) if k % 2 == 0]
    rules_all[f"mod3=1≤{ub}"] = [k for k in range(1, ub+1) if k % 3 == 1]
    rules_all[f"mod3=2≤{ub}"] = [k for k in range(1, ub+1) if k % 3 == 2]
    rules_all[f"mod4=1≤{ub}"] = [k for k in range(1, ub+1) if k % 4 == 1]
    rules_all[f"mod4=3≤{ub}"] = [k for k in range(1, ub+1) if k % 4 == 3]
    rules_all[f"fib≤{ub}"] = [k for k in range(1, ub+1) if k in FIB]
    rules_all[f"luc≤{ub}"] = [k for k in range(1, ub+1) if k in LUC]
    rules_all[f"tri≤{ub}"] = [k for k in range(1, ub+1) if (lambda t: t*(t+1)//2 == k)(int((math.sqrt(8*k+1)-1)//2))]
    rules_all[f"primepower≤{ub}"] = [k for k in range(1, ub+1) if any((lambda p, e: is_prime(p) and k == p**e)(p, e) for e in range(1, 7) for p in range(2, k+1))]
    rules_all[f"coprime11≤{ub}"] = [k for k in range(1, ub+1) if gcd(k, 11) == 1]
rules9 = {k: v for k, v in rules_all.items() if len(v) == 9}
print(f"9-元素規則: {len(rules9)}")
for k, v in sorted(rules9.items()):
    print(f"  {k:22s} {v}")

def r2_of(mods):
    ld = np.log([admn[n-1] for n in mods]); lg = np.log([gam[n-1] for n in mods])
    A = np.vstack([np.ones(len(mods)), lg]).T
    c, *_ = np.linalg.lstsq(A, ld, rcond=None)
    r = ld - A @ c
    return 1 - (r ** 2).sum() / ((ld - ld.mean()) ** 2).sum()

def rms_of(mods):
    # 質量 fit: log m = log C + φ²·log|dm| — C OLS, fixed φ²
    ld = np.log([admn[n-1] for n in mods])
    C_ = math.exp(np.mean(logm - PHI2 * np.array(ld)))
    r = logm - (math.log(C_) + PHI2 * np.array(ld))
    return math.sqrt(np.mean(r ** 2))

print("\n═══ 全規則: R² vs 質量 fit RMS ═══")
print(f"{'規則':22s} {'R²':>8s} {'RMS':>8s}  判決")
res = []
for k, v in sorted(rules9.items()):
    r2 = r2_of(v)
    rms = rms_of(v)
    res.append((k, v, r2, rms))
    tag = ""
    if rms < 0.60: tag = " ★★ 質量層特權"
    elif rms < 0.90: tag = " ★ 中等"
    print(f"{k:22s} {r2:8.4f} {rms:8.3f}  {tag}")

print("\n═══ 裁決 ═══")
best = sorted(res, key=lambda x: x[3])
a5 = [x for x in res if x[0] == "primes∪sq≤13"][0]
others_best = [x for x in res if x[0] != "primes∪sq≤13"][0]
ratio = others_best[3] / a5[3]
print(f"A₅ RMS = {a5[3]:.3f} | 次佳 {others_best[0]} RMS = {others_best[3]:.3f} | ratio = {ratio:.2f}")
rms_leq_060 = [x[0] for x in res if x[3] < 0.60]
print(f"RMS<0.60 規則: {rms_leq_060}")
checks = []
if len(rms_leq_060) == 1 and rms_leq_060[0] == "primes∪sq≤13":
    checks.append(("唯一質量層特權規則 = A₅", True, f"ratio={ratio:.2f}"))
else:
    checks.append(("唯一質量層特權規則 = A₅", False, str(rms_leq_060)))

# 非特權者嘅 RMS 係咪<0.90? (至少 5/6 其他 >0.90)
other_rms = [x[3] for x in res if x[0] != "primes∪sq≤13"]
n_gt_090 = sum(1 for r in other_rms if r > 0.90)
checks.append(("其餘 ≥5/6 規則 RMS>0.90", n_gt_090 >= 5, f"{n_gt_090}/6"))

out = {"rules": {k: {"modes": v, "r2": float(r2), "rms": float(rms)} for k, v, r2, rms in res}}
with open("data/26_l04_final_showdown.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")