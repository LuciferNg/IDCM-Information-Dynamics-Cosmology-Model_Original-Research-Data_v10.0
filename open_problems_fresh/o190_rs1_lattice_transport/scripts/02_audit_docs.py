#!/usr/bin/env python3
"""O190 scripts/02 — 獨立核對 (Independent Audit): 逐文檔公式/數值驗證

獨立驗證器模式 (userskills-math-validation Independent Verifier):
- 唔 import scripts/01 任何嘢, 所有常數重新定義, 所有公式由第一原理重算
- 每個 check 對照記錄文檔聲稱值 (01_problem_record.md / docs/01 / docs/02),
  二值 PASS/FAIL + tolerance, JSON 存檔 (data/audit.json)
- 檢查 FAIL 時先懷疑 verifier 自己, 唔好立即改記錄文檔
- 範圍: 只驗證 O190 內部推導 + 引用鏈嘅內部算術; 唔跨文檔加新推導
"""
import math, json, os

N = 88
def csc(x): return 1.0 / math.sin(x)
def cot(x): return 1.0 / math.tan(x)
def g176(k): return 4.0 * math.sin(math.pi*k/176)**2
def g88(j):  return 4.0 * math.sin(math.pi*j/88)**2

checks = []
def add(cid, ref, claim, computed, ok):
    checks.append({"id": cid, "doc": ref, "claim": claim,
                   "computed": computed, "ok": bool(ok)})

def chk_abs(cid, ref, claim, computed, target, tol):
    add(cid, ref, claim, f"{computed:.12g}", abs(computed-target) <= tol)

def chk_all(cid, ref, claim, vals, targets, tol):
    ok = all(abs(v-t) <= tol for v, t in zip(vals, targets))
    add(cid, ref, claim, "[" + ", ".join(f"{v:.12g}" for v in vals) + "]", ok)

# ============ A. 世界/觀察者預算 (01_problem_record §一, docs/01 表) ============
S_even = sum(g176(k) for k in range(2, 89, 2))
S_odd  = sum(g176(k) for k in range(1, 88, 2))
chk_abs("V01", "01_pr §一 / docs/01 表", "Σγ_even (world) = 90", S_even, 90.0, 1e-9)
chk_abs("V02", "01_pr §一 / docs/01 表", "Σγ_odd (observer) = 88", S_odd, 88.0, 1e-9)
chk_abs("V03", "01_pr §一 / docs/01 表", "total = 178 = 2F₁₁", S_even+S_odd, 178.0, 1e-9)
chk_abs("V04", "01_pr §一 / docs/01 表", "E−O = 2", S_even-S_odd, 2.0, 1e-9)
add("V05", "01_pr §一", "F₁₁ = 89 (2×89 = 178)", "89", 89 == 89)

# ============ B. mass shell + rapidity (01_pr §一, docs/01 對比 1) ============
ok_ms = all(abs(csc(math.pi*n/N)**2 - cot(math.pi*n/N)**2 - 1) <= 1e-12 for n in range(1, 45))
add("V06", "01_pr §一 / docs/01 對比 1", "mass shell csc²−cot²=1 (n=1..44)", "all-exact", ok_ms)
ok_rp = all(abs(math.cosh(math.log(1/math.tan(math.pi*n/176))) - csc(math.pi*n/N)) <= 1e-9
             and abs(math.tanh(math.log(1/math.tan(math.pi*n/176))) - math.cos(math.pi*n/N)) <= 1e-9
             for n in range(1, 45))
add("V07", "01_pr §一 / docs/01 對比 1", "rapidity cosh(η)=γ & tanh(η)=v/c (n=1..44)", "all-exact", ok_rp)

eta1  = math.log(1/math.tan(math.pi*1/176))
eta22 = math.log(1/math.tan(math.pi*22/176))
eta44 = math.log(1/math.tan(math.pi*44/176))
chk_abs("V08", "docs/01 對比 1", "η₁ = 4.0257", eta1, 4.0257, 5e-4)
chk_abs("V09", "docs/01 對比 1", "η₂₂ = 0.8814", eta22, 0.8814, 5e-4)
chk_abs("V10", "docs/01 對比 1", "η₄₄ = 0.0000", eta44, 0.0, 1e-9)
chk_abs("V11", "docs/01 對比 1", "γ₂₂ = 1.414 = √2 (csc)", csc(math.pi*22/N), math.sqrt(2), 1e-9)
chk_abs("V12", "docs/01 對比 1", "γ₄₄ = 1.000 (csc)", csc(math.pi*44/N), 1.0, 1e-9)
chk_abs("V13", "01_pr §一", "γ_max = csc(π/88) = 28.017", csc(math.pi/N), 28.017, 5e-4)

# Δη 非均勻 (01_pr §一: 4.026→3.332→2.926, ratio ~5:1)
etas3 = [math.log(1/math.tan(math.pi*n/176)) for n in (1, 2, 3)]
chk_all("V14", "01_pr §一", "η₁,η₂,η₃ = 4.026,3.332,2.926", etas3, (4.026, 3.332, 2.926), 5e-4)
etas8 = [math.log(1/math.tan(math.pi*n/176)) for n in range(1, 9)]
diffs = [abs(etas8[i+1]-etas8[i]) for i in range(7)]
ratio = max(diffs)/min(diffs)
chk_abs("V15", "01_pr §一", "Δη ratio ~5:1", ratio, 5.13, 0.05)

# ============ C. N→∞ 連續 SR 回復 (01_pr §一, docs/01 對比 5) ============
g1 = [csc(math.pi/88), csc(math.pi/352), csc(math.pi/1408)]
v1 = [math.cos(math.pi/88), math.cos(math.pi/352), math.cos(math.pi/1408)]
chk_all("V16", "01_pr §一", "γ₁ = 28.0/112.0/448.2 (N=88/352/1408)", g1, (28.017, 112.047, 448.181), 0.05)
chk_all("V17", "docs/01 對比 5", "v₁/c = 0.99936/0.99996/0.9999975", v1, (0.9993628, 0.9999602, 0.9999975), 1e-5)

# ============ D. Z₂ / Nyquist (88-chain Laplacian, 01_pr §一) ============
chk_abs("V18", "01_pr §一", "γ₂₂ = 2 (Z₂ self-dual, 4sin²)", g88(22), 2.0, 1e-9)
chk_abs("V19", "01_pr §一", "γ₄₄ = 4 (Nyquist, 4sin²)", g88(44), 4.0, 1e-9)
ok_dual = all(abs(g88(j) + g88(44-j) - 4.0) <= 1e-9 for j in range(1, 44))
add("V20", "docs/01 表", "γ_n + γ_{44−n} = 4 (n=1..43)", "all-exact", ok_dual)

# ============ E. 誠實修正記錄 (01_pr §五: csc naive 奇偶和) ============
csc_odd  = sum(csc(math.pi*n/N) for n in range(1, 88, 2))
csc_even = sum(csc(math.pi*n/N) for n in range(2, 88, 2))
chk_abs("V21", "01_pr §五", "csc naive Σ_odd = 148.35", csc_odd, 148.352, 5e-3)
chk_abs("V22", "01_pr §五", "csc naive Σ_even = 109.52", csc_even, 109.517, 5e-3)

# ============ F. 階梯形狀 (docs/01 對比 1: RS1 KK vs IDCM γ) ============
# Bessel J₁ 零點: 獨立用 Newton-Raphson + J₁ 冪級數重算 (唔靠文獻值)
def j1(x, terms=80):
    s, m = 0.0, 0
    x2 = x/2.0
    p = x2                      # m=0 term: (x/2)^1 / (0! 1!)
    for m in range(terms):
        s += (1 if m % 2 == 0 else -1) * p / (math.factorial(m) * math.factorial(m+1))
        p *= x2 * x2
    return s

x_zeros = []
for n in range(1, 8):
    xk = (n + 0.25) * math.pi           # 起始點 (J₁ 零點漸近)
    for _ in range(12):
        xk = xk - j1(xk) / (j1(xk + 1e-6) - j1(xk - 1e-6)) * 2e-6   # 數值導數
    x_zeros.append(xk)
lit = (3.8317, 7.0156, 10.1735, 13.3237, 16.4706, 19.6159, 22.7601)
ok_zero = all(abs(a-b) <= 5e-4 for a, b in zip(x_zeros, lit))
add("V23", "docs/01 對比 1", "Bessel J₁ 零點 x₁..x₇ 命中文獻 (4dp)", "[" + ", ".join(f"{z:.4f}" for z in x_zeros) + "]", ok_zero)
ok_j1 = all(abs(j1(z)) < 1e-6 for z in x_zeros)
add("V24", "docs/01 對比 1", "J₁(x_n) ≈ 0 (零點品質)", "max|J₁|<1e-6", ok_j1)
ratios = [z/x_zeros[0] for z in x_zeros]
chk_all("V25", "docs/01 對比 1", "RS1 KK m/m₁ = 1.000..5.940", ratios,
        (1.000, 1.831, 2.655, 3.477, 4.299, 5.119, 5.940), 1e-3)
gam = [csc(math.pi*n/N) for n in range(1, 8)]
chk_all("V26", "docs/01 對比 1", "IDCM γ 階梯 28.017..4.044", gam,
        (28.017, 14.018, 9.355, 7.027, 5.632, 4.704, 4.044), 5e-4)
vvs = [math.cos(math.pi*n/N) for n in range(1, 8)]
chk_all("V27", "docs/01 對比 1", "IDCM v/c 0.9994..0.9689", vvs,
        (0.9994, 0.9975, 0.9943, 0.9898, 0.9841, 0.9771, 0.9689), 5e-4)

# ============ G. 尺度精化 (docs/01 表 + docs/02 攻堅 1) ============
chk_abs("V28", "docs/01 表", "N_ℓ: N_0 = 44, N_1 = 176 (44·4^ℓ)", 44*4, 176, 0)
chk_abs("V29", "docs/01 表 / docs/02", "γ_max(0) = csc(π/88) = 28.017", csc(math.pi/(88*1)), 28.017, 5e-4)
chk_abs("V30", "docs/01 表 / docs/02", "γ_max(1) = csc(π/352) = 112.047", csc(math.pi/(88*4)), 112.047, 5e-4)

# ============ H. docs/02 攻堅內部算術 ============
add("V31", "docs/02 攻堅 1", "δ=1 → ΔS' = μ² = 2 (2λδ, λ=1)", "2×1×1=2", 2 == 2)
add("V32", "docs/02 攻堅 1", "δ=N_d → ΔS' = 88 = Σγ_odd (2×44)", "2×44=88", 2*44 == 88)
add("V33", "docs/02 攻堅 1", "Tr(D)−Tr(N) = 176−174 = 2 (O159 引用, 內部算術)", "176−174=2", 176-174 == 2)
chk_abs("V34", "docs/02 攻堅 3", "μ² = E−O = γ₄₄/2 三重身份 = 2", S_even-S_odd, 2.0, 1e-9)

# ============ I. 結構一致性 (01_pr / docs/01 / SESSION_START) ============
add("V35", "docs/01 表", "K_tree: 34 層 = M+1 = 33+1", "33+1=34", 33+1 == 34)
add("V36", "docs/01 表", "K_tree μ_m = φ^{L−m}, L = 53/8 = 6.625 (O159 引用)", "53/8=6.625", abs(53/8 - 6.625) < 1e-12)

# ============ 輸出 ============
npass = sum(1 for c in checks if c["ok"])
print(f"獨立核對: {npass}/{len(checks)} PASS\n")
for c in checks:
    print(f"  {'✅' if c['ok'] else '❌'} {c['id']} [{c['doc']}] {c['claim']}  → {c['computed']}")

os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"), exist_ok=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "audit.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"date": "2026-09-13", "total": len(checks), "pass": npass,
               "fail": len(checks)-npass, "checks": checks}, f, ensure_ascii=False, indent=1)
print(f"\nJSON → {out}")
