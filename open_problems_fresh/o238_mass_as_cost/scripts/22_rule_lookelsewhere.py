#!/usr/bin/python3
"""O238 — Script 22: 投影 operator 動態攻堅 — 質數∪平方規則嘅 look-elsewhere 檢定

scripts/18: A₅ = {質數 ≤13} ∪ {平方 ≤13} (9 modes, 1/C(88,9)=1.75e-12).
但「規則空間」有好多自然候選 — 質數∪平方可能只係後見湊中. 本 script 盲測:

  P1 規則庫: 所有「自然 9-mode 選擇規則」— 質數/平方/奇數/偶數/mod-4類/
     Fibonacci/Lucas/三角數/質數冪/… × 上界掃描 {7..16}
  P2 對每個規則: 佢出嘅 mode 集喺譜平面 R² (共線性) — 係咪只有質數∪平方高?
  P3 look-elsewhere: 規則庫 N 個候選中, 隨機 null 出 R²≥0.992 嘅概率
     = 1.75e-12 × N? 修正後仍然顯著嗎?
  P4 最簡規則裁決: 邊個規則係「最簡 + 最共線」

判斷: 若質數∪平方係規則庫中唯一 R²>0.95 ⟹ 數論規則有特權 (唔係湊中)
      若多個規則都高 R² ⟹ 數論表達係後見, A₅ 共線係譜幾何而非數論
"""
import numpy as np, math, json, itertools

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

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
SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]

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

def r2_of(mask):
    ld = np.log(admn[mask]); lg = np.log(gam[mask])
    A = np.vstack([np.ones(mask.sum()), lg]).T
    c, *_ = np.linalg.lstsq(A, ld, rcond=None)
    r = ld - A @ c
    return 1 - (r ** 2).sum() / ((ld - ld.mean()) ** 2).sum()

# ★ 先答關鍵: A₅ 共線 R² 喺 log|dm| vs logγ 平面 — 但係 log|dm| 本身
#   對 logγ 唔係線性, R² 高可能係「|dm| vs γ」冪律假象? 用正交對照:
print("═══ P0. 基線: 88-chain 全譜結構 ═══")
ld_all = np.log(admn); lg_all = np.log(gam)
A_all = np.vstack([np.ones(N), lg_all]).T
c_all, *_ = np.linalg.lstsq(A_all, ld_all, rcond=None)
r_all = ld_all - A_all @ c_all
r2_all = 1 - (r_all**2).sum() / ((ld_all - ld_all.mean())**2).sum()
print(f"  全譜 R²(log|dm|~logγ) = {r2_all:.4f}")
mask9 = np.zeros(N, bool); mask9[np.array(SEL9)-1] = True
print(f"  A₅ R² = {r2_of(mask9):.6f}")

print("\n═══ P1. 規則庫生成 ═══")
rules = {}
for ub in range(7, 17):
    rules[f"primes≤{ub}"] = [k for k in range(1, ub+1) if is_prime(k)]
    rules[f"squares≤{ub}"] = [k for k in range(1, ub+1) if is_sq(k)]
    rules[f"primes∪sq≤{ub}"] = [k for k in range(1, ub+1) if is_prime(k) or is_sq(k)]
    rules[f"odd≤{ub}"] = [k for k in range(1, ub+1) if k % 2 == 1]
    rules[f"even≤{ub}"] = [k for k in range(1, ub+1) if k % 2 == 0]
    rules[f"mod3=1≤{ub}"] = [k for k in range(1, ub+1) if k % 3 == 1]
    rules[f"mod3=2≤{ub}"] = [k for k in range(1, ub+1) if k % 3 == 2]
    rules[f"mod4=1≤{ub}"] = [k for k in range(1, ub+1) if k % 4 == 1]
    rules[f"mod4=3≤{ub}"] = [k for k in range(1, ub+1) if k % 4 == 3]
    rules[f"fib≤{ub}"] = [k for k in range(1, ub+1) if k in FIB]
    rules[f"luc≤{ub}"] = [k for k in range(1, ub+1) if k in LUC]
    rules[f"tri≤{ub}"] = [k for k in range(1, ub+1) if k * (k+1) // 2 * 0 + (int((math.sqrt(8*k+1)-1)//2) * (int((math.sqrt(8*k+1)-1)//2)+1)//2) == k]
    rules[f"primepower≤{ub}"] = [k for k in range(1, ub+1) if (lambda kk: any(is_prime(p) and kk == p**e for e in range(1, 7) for p in range(2, kk+1)))(k)]
    rules[f"coprime11≤{ub}"] = [k for k in range(1, ub+1) if gcd(k, 11) == 1]
# 只留 9 元素規則
newr = {}
for k, v in rules.items():
    if len(v) == 9:
        newr[k] = v
rules = newr
print(f"  9-元素規則數: {len(rules)}")
for k, v in sorted(rules.items()):
    print(f"    {k:22s}: {v}")

print("\n═══ P2. 規則 R² 對照 ═══")
results = []
for k, v in rules.items():
    m = np.zeros(N, bool); m[np.array(v)-1] = True
    r2 = r2_of(m)
    results.append((k, v, r2))
results.sort(key=lambda x: -x[2])
for k, v, r2 in results:
    tag = " ★" if r2 > 0.95 else ""
    print(f"  R²={r2:.4f}  {k:22s} {v}{tag}")
best_rules = [k for k, v, r2 in results if r2 > 0.95]
print(f"\n  R²>0.95 規則數: {len(best_rules)}")

print("\n═══ P3. look-elsewhere 修正 ═══")
# P(特定規則 9 modes = A₅) = 1.75e-12; 修正 = × 規則數
n_rules = len(results)
p_le = 1.75e-12 * n_rules
print(f"  規則庫 {n_rules} 個候選 ⟹ Bonferroni 修正 p = {p_le:.3e}")
chk("P3.1 修正後仍然極顯著 (p<1e-6)", p_le < 1e-6, f"p={p_le:.3e}")

print("\n═══ P4. 最簡規則裁決 ═══")
print(f"  規則數: {n_rules}; 高共線 (R²>0.95): {len(best_rules)}")
if len(best_rules) == 1:
    print(f"  ⟹ 唯一高共線規則: {best_rules[0]} — 數論規則有特權 (唔係湊中)")
    chk("P4.1 唯一高共線規則 = 質數∪平方", best_rules[0] == "primes∪sq≤13", best_rules[0])
elif len(best_rules) > 1:
    print(f"  ⟹ 多個規則共線 — 數論表達係後見, 需譜幾何解釋")
    chk("P4.1 唯一高共線規則 = 質數∪平方", False, str(best_rules))

out = {"n_rules": n_rules, "best_rules": best_rules, "p_lookelsewhere": float(p_le),
       "rules_r2": {k: float(r2) for k, v, r2 in results}}
with open("data/22_rule_lookelsewhere.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")