#!/usr/bin/env python3
"""O146 L1: 數學存在 — 拍頻結構指紋 + 零模型對照
================================================
驗證拍頻表結構係咪 sin 譜獨有 (K_Chain), 隨機譜做唔做到。
"""
import math, random, json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "01_math_existence.json")
N = 44
checks = {}

# ---------- 指紋 1: 可分性 B(d,s) = 4·sin(dπ/176)·cos(sπ/176) ----------
w = lambda n: 2 * math.sin(math.pi * n / 88)
maxdev = 0.0
for n in range(1, N+1):
    for m in range(n+1, N+1):
        d, s = m-n, m+n
        pred = 4*math.sin(d*math.pi/176)*math.cos(s*math.pi/176)
        maxdev = max(maxdev, abs((w(m)-w(n)) - pred))
checks["separability"] = {"max_dev": maxdev, "pass": maxdev < 1e-12}

# ---------- 指紋 2: 946 唯一性 ----------
vals = sorted(round(w(m)-w(n), 12) for n in range(1, N+1) for m in range(n+1, N+1))
checks["uniqueness"] = {"total": len(vals), "unique": len(set(vals)),
                        "pass": len(set(vals)) == len(vals)}

# ---------- 指紋 3: Z₂ 對偶 γ_n + γ_{44−n} = 4 ----------
z2_ok = all(abs((w(n)**2 + w(44-n)**2) - 4) < 1e-12 for n in range(1, 44))
checks["z2_duality"] = {"pass": z2_ok}

# ---------- 指紋 4: 斜邊閉合 B(d,88−d) = 4sin²(dπ/176) ----------
hyp = max(abs((w(44)-w(44-d)) - 4*math.sin(math.pi*d/176)**2) for d in range(1, 44))
checks["hypotenuse"] = {"max_dev": hyp, "pass": hyp < 1e-12}

# ---------- 指紋 5: 無理度分層 (sympy minimal polynomial 權威計算) ----------
from sympy import sin as ssin, pi as spi, minimal_polynomial, symbols, degree
_x = symbols('x')
n_deg = {}
for n in range(1, N+1):
    mp_ = minimal_polynomial(ssin(n*spi/88), _x)
    n_deg[n] = degree(mp_)
deg_hist = {}
for n, dg in n_deg.items():
    deg_hist[dg] = deg_hist.get(dg, 0) + 1
# 44-site 譜: γ_n = 4sin²(nπ/88), sin(nπ/88) 次數 ⊂ {1,2,4,5,10,20,40}
# n=44: sin(π/2)=1 有理 (degree 1), n=22: √2/2 (degree 2)
checks["degree_layer"] = {"per_mode": {str(k): v for k, v in sorted(n_deg.items())},
                          "histogram": {str(k): v for k, v in sorted(deg_hist.items())},
                          "pass": set(deg_hist.keys()) <= {1,2,4,5,10,20,40}}

# ---------- 零模型: 隨機 44 頻率譜 × 50 ----------
def random_separability(rng):
    w_r = np.sort(rng.uniform(0.01, 2, N))
    err = 0.0
    for d in range(1, N):
        rows = [(n,m) for n in range(N) for m in range(n+1,N) if m-n==d]
        for (n,m) in random.sample(rows, min(10, len(rows))):
            s = (m+1)+(n+1)
            pred = 4*math.sin(d*math.pi/176)*math.cos(s*math.pi/176)
            err = max(err, abs(w_r[m]-w_r[n]-pred))
    return err

rng = np.random.default_rng(7)
rand_errs = [random_separability(rng) for _ in range(50)]
checks["null_model"] = {
    "kchain_max_dev": maxdev,
    "random_median": float(np.median(rand_errs)),
    "random_range": [float(min(rand_errs)), float(max(rand_errs))],
    "pass": maxdev < min(rand_errs) * 1e-6,   # 10⁶ 量級分離
    "separation_power": maxdev / np.median(rand_errs),
}

all_pass = all(v.get("pass", True) for v in checks.values())
print("=" * 60)
print("  O146 L1: 數學存在 — 拍頻結構指紋")
print("=" * 60)
print(f"  可分性 B=4sin(dπ/176)cos(sπ/176): max_dev = {checks['separability']['max_dev']:.2e}  {'✅' if checks['separability']['pass'] else '🔴'}")
print(f"  唯一性: {checks['uniqueness']['unique']}/{checks['uniqueness']['total']}  {'✅' if checks['uniqueness']['pass'] else '🔴'}")
print(f"  Z₂ 對偶 γ_n+γ_(44−n)=4: {'✅' if z2_ok else '🔴'}")
print(f"  斜邊閉合 B(d,88−d): max_dev = {hyp:.2e}  {'✅' if checks['hypotenuse']['pass'] else '🔴'}")
print()
print("  零模型對照 (隨機 44 頻率譜 × 50):")
print(f"    K_Chain 可分性偏差: {maxdev:.2e}")
print(f"    隨機譜偏差中位數:   {np.median(rand_errs):.4f}")
print(f"    隨機譜偏差範圍:     [{min(rand_errs):.4f}, {max(rand_errs):.4f}]")
print(f"    分離力度 (K/隨機中位數): {checks['null_model']['separation_power']:.1e}")
print(f"  → {'✅ 結構指紋係 sin 譜獨有' if checks['null_model']['pass'] else '🔴 隨機譜都可分離, 指紋無判定力'}")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer)): return bool(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        try:
            import sympy
            if isinstance(obj, sympy.Integer): return int(obj)
        except Exception:
            pass
        return super().default(obj)

with open(OUT, "w") as f:
    json.dump(checks, f, indent=2, cls=NumpyEncoder)
print(f"\n  結果: {OUT}")
print(f"  總判定: {'✅ PASS' if all_pass else '🔴 FAIL'}")
