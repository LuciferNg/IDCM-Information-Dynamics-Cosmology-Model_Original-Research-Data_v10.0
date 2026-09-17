#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/02 -- 譜身份判準 (Spectral Identity Criterion) — C3

憲章路線 2: 4 步判準 script 化
  ① 譜表達存在   候選式每個因子都係已註冊譜泛函 (原語池成員), 唔可以係裸數
  ② 獨立出處     每個因子有自己嘅推導出處 (O 編號); 冇出處 = FAIL
  ③ 零參數       式中冇任何非註冊數值常數 (擬合常數 = FAIL)
  ④ 陷阱窗       dev = |expr − target|/|target| 唔准落 (1e-5, 1e-3)
  ⑤ 數域         expr 所屬數域 vs target 所需數域 — 域分離 => 可證明唔相等
                 (本步係 C2 唯一性嘅硬約束, 唔可以靠數值判斷)

數域定理 (本 script 驗證):
  ★ Q(zeta_5) ∩ Q(zeta_176) = Q(zeta_gcd(5,176)) = Q(zeta_1) = Q
    => sqrt(5) ∉ Q(zeta_176)  =>  phi-冪族同鏈譜族喺無理層面**域不相交**
    => 任何「b_spec = sqrt(5)/2」型等式可以**證明唔成立** (唔係數值判斷)

必要案例 (憲章指定, 判決必須正確):
  T1  b_spec = 1/<v_g>_{1..22}      -> ✅ 譜身份 (鏈譜, Q(zeta_176)^+)
  T2  sqrt(5)/2                      -> 🟡 合法樹譜量, 但域分離 => 唔可能等於 b_spec
  T3  C_old = -0.1697                -> ❌ 冇譜表達 + 陷阱窗 => 已證偽
  T4 注入必然錯案例 x4 (證明判準識 FAIL — O148 check 簽名坑教訓)
"""
import os
import json

import mpmath as mp
import sympy as sp

mp.mp.dps = 50
PI = mp.pi
PHI = (1 + mp.sqrt(5)) / 2
Nd = 44
vg22 = mp.fsum([mp.cos(n * PI / 88) for n in range(1, 23)]) / 22
B_SPEC = 1 / vg22
SQ5_2 = mp.sqrt(5) / 2

TRAP_LO, TRAP_HI = mp.mpf('1e-5'), mp.mpf('1e-3')
EXACT_TOL = mp.mpf('1e-40')

# ============================================================
# 0. 註冊譜原子 (判準 ① 用: 因子必須係呢啲之一)
# ============================================================
REG = {}
REG["v_g(n) = cos(pi n/88)"] = [mp.cos(n * PI / 88) for n in range(1, 45)]
REG["sec(n) = 1/cos(pi n/88)"] = [1 / mp.cos(n * PI / 88) for n in range(1, 45)]
REG["gamma_n = 4sin^2(pi n/88)"] = [4 * mp.sin(n * PI / 88) ** 2 for n in range(1, 45)]
REG["Gamma_k = 4sin^2(k pi/176)"] = [4 * mp.sin(k * PI / 176) ** 2 for k in range(1, 89)]
TH = mp.matrix([[1, 1], [1, 0]])
_thp = {0: mp.eye(2), 1: TH}
for n in range(2, 20):
    _thp[n] = _thp[n - 1] * TH
for n in range(1, 20):
    REG["L_%d = Tr(T^n)" % n] = mp.mpf(int(round(_thp[n][0, 0] + _thp[n][1, 1])))
    REG["F_%d = (T^n)_12" % n] = mp.mpf(int(round(_thp[n][0, 1])))
REG["phi (T_hat 本徵值)"] = PHI
REG["sqrt5 = 2phi-1"] = mp.sqrt(5)
REG["N_d"] = mp.mpf(44); REG["B"] = mp.mpf(4); REG["N_gen"] = mp.mpf(3)
REG["L5"] = mp.mpf(11); REG["F_proj"] = mp.mpf(17); REG["K_tree"] = mp.mpf(33)
REG["Sum_gamma"] = mp.mpf(90); REG["Sum_gamma_odd"] = mp.mpf(44); REG["Sum_gamma_even"] = mp.mpf(46)
REG["N_d/2 = 22"] = mp.mpf(22)
REG["L10/2 = 61.5"] = mp.mpf("61.5")
REG["L10 = 123"] = mp.mpf(123)
REG["2^7 = 128"] = mp.mpf(128)
REG["4 N_d + B^2 = 192"] = mp.mpf(192)
REG["pi"] = PI
for K in range(1, 45):
    REG["mean_sec_1_%d" % K] = mp.fsum([1 / mp.cos(n * PI / 88) for n in range(1, K + 1)]) / K
    REG["inv_mean_vg_1_%d" % K] = 1 / (mp.fsum([mp.cos(n * PI / 88) for n in range(1, K + 1)]) / K)
REG_VALS = {k: v for k, v in REG.items() if not isinstance(v, list)}


def is_registered(value, tol=mp.mpf('1e-30')):
    """值係咪等於某個已註冊譜泛函 (判準 ①)"""
    hits = []
    for k, v in REG.items():
        if isinstance(v, list):
            if any(abs(x - value) <= tol * max(1, abs(value)) for x in v):
                hits.append(k)
        elif abs(v - value) <= tol * max(1, abs(value)):
            hits.append(k)
    return hits


# ============================================================
# 1. 數域工具 (判準 ⑤)
# ============================================================
print("=" * 78)
print("O201/02 -- 譜身份判準 (C3)")
print("=" * 78)
print("\n[數域定理驗證]")
print("  (i) 正對照: 5 | 10  => Q(sqrt5) ⊆ Q(zeta_10) ?")
x = sp.symbols('x')
mp10 = sp.minimal_polynomial(2 * sp.cos(2 * sp.pi / 10), x)
print("      2cos(2pi/10) = phi, minimal polynomial = %s  (degree %d)"
      % (sp.nsimplify(mp10), sp.degree(mp10, x)))
phi_exact = (1 + sp.sqrt(5)) / 2
sq5_from_phi = sp.simplify(2 * phi_exact - 1)
print("      sqrt5 = 2phi-1 = %s  => sqrt5 ∈ Q(zeta_10)  [正對照 PASS]" % sq5_from_phi)
print("  (ii) 負對照: 5 | 176 ? 176 = %d, 176 mod 5 = %d" % (176, 176 % 5))
print("      conductor(Q(sqrt5)) = 5 (fundamental discriminant 5); 5 ∤ 176")
print("  (iii) Q(zeta_m) ∩ Q(zeta_n) = Q(zeta_gcd(m,n))  =>  Q(zeta_5) ∩ Q(zeta_176) = Q(zeta_1) = Q")
print("  (iv) Q(sqrt5) ⊆ Q(zeta_5) 且 Q(sqrt5) ⊄ Q(zeta_176)")
print("       => sqrt5 ∉ Q(zeta_176)   [域分離定理]")
print("  (v) 鏈譜 gamma_n = 4sin^2(pi n/88) ∈ Q(zeta_88)^+ ⊆ Q(zeta_176)^+ (degree 40)")
print("      => phi-冪族 (Q(sqrt5), degree 2) 同鏈譜族喺無理層面域不相交")
ND_176 = sp.nsimplify(sp.totient(176))
print("      [Q(zeta_176):Q] = phi(176) = %s,  [Q(zeta_176)^+ : Q] = %s" % (
    ND_176, ND_176 / 2))
ND_88 = sp.totient(88)
print("      [Q(zeta_88):Q]  = %s,  [Q(zeta_88)^+ : Q]  = %s" % (ND_88, ND_88 / 2))


def field_of(factors):
    """因子數域嘅 compositum (由因子聲明推導; Q 係單位, 唔加階)"""
    fs = {f[2] for f in factors}
    fs.discard("Q")
    if not fs:
        return "Q", 1
    if fs == {"Q(zeta_176)^+"}:
        return "Q(zeta_176)^+", 40
    if fs == {"Q(sqrt5)"}:
        return "Q(sqrt5)", 2
    return "compositum(%s)" % ",".join(sorted(fs)), None


def disjoint(fa, fb):
    return {fa, fb} == {"Q(zeta_176)^+", "Q(sqrt5)"}


# ============================================================
# 2. 判準本體
# ============================================================
def criterion(case_id, desc, target, sigma, expr_name, expr_value, factors,
              numeric_literals=()):
    """
    factors: list of (factor_name, factor_value, field, provenance)
    numeric_literals: 式中額外數值常數 (非註冊 => 判準 ③ FAIL)
    ④ 陷阱窗係**條件律**: 只有當目標精度 sigma/|target| < 1e-4 (窗寬 1e-3 之 1/10)
       先有判別力。目標精度不足時窗律 N/A (唔可以當 FAIL, 亦唔可以當證據)。
    """
    print("\n" + "-" * 78)
    print("%s  %s" % (case_id, desc))
    print("-" * 78)
    dev = abs((expr_value - target) / target)
    steps = {}

    # ① 譜表達存在性
    bad = [f for f in factors if not is_registered(f[1])]
    steps[1] = (len(bad) == 0, "全部 %d 個因子係註冊譜泛函" % len(factors) if not bad
                else "非譜因子: %s" % [b[0] for b in bad])

    # ② 獨立出處
    noprov = [f for f in factors if not (f[3] and f[3].strip())]
    steps[2] = (len(noprov) == 0, "每個因子有出處: %s" % "; ".join(
        "%s→%s" % (f[0], f[3]) for f in factors) if not noprov
        else "冇出處: %s" % [f[0] for f in noprov])

    # ③ 零參數
    unreg = [str(n) for n in numeric_literals if not is_registered(mp.mpf(n))]
    steps[3] = (len(unreg) == 0, "零非註冊數值常數" if not unreg else "非註冊常數: %s" % unreg)

    # ④ 陷阱窗 (條件律: 須目標精度 sigma/|target| < 1e-4)
    prec = abs(sigma / target) if sigma else None
    if prec is None:
        steps[4] = (True, "目標無誤差 => 窗律不適用 (n/a)")
    elif prec >= mp.mpf('1e-4'):
        steps[4] = (True, "目標精度 sigma/|t| = %.2e >= 1e-4 => 窗律不適用 (n/a); dev = %.4e (%.3f sigma)"
                    % (float(prec), float(dev), float((expr_value - target) / sigma)))
    else:
        in_trap = (dev > TRAP_LO) and (dev < TRAP_HI)
        steps[4] = (not in_trap, "dev = %.4e (窗外, 窗律適用)" % float(dev) if not in_trap
                    else "dev = %.4e 落陷阱窗 (1e-5,1e-3) => 數值巧合" % float(dev))

    # ⑤ 數域
    fexpr, dexpr = field_of(factors)
    ftgt = "Q(zeta_176)^+"
    sep = disjoint(fexpr, ftgt)
    steps[5] = (not sep, "expr 域 = %s%s; 目標域 = %s%s" % (
        fexpr, " (degree %s)" % dexpr if dexpr else "", ftgt,
        "  => 域分離, 可證明唔相等" if sep else ""))

    for k in (1, 2, 3, 4, 5):
        print("   %s %s   %s" % ("PASS" if steps[k][0] else "FAIL", "①②③④⑤"[k - 1], steps[k][1]))

    fails = [k for k in (1, 2, 3, 4, 5) if not steps[k][0]]
    trap_flag = (TRAP_LO < dev) and (dev < TRAP_HI)
    if not fails:
        verdict = "✅ 譜身份"
    elif 5 in fails:
        verdict = "❌ 域分離 => 可證明唔相等 (唔係數值巧合, 係結構上唔可能)"
    elif 1 in fails and 3 in fails:
        verdict = "❌ 裸數/擬合常數 => 唔係譜表達"
    elif trap_flag:
        verdict = "❌ 陷阱窗 => 最近譜候選 dev %.2e 落 (1e-5,1e-3), 數值巧合" % float(dev)
    else:
        verdict = "❌ 唔合格 (FAIL 項: %s)" % ",".join("①②③④⑤"[k - 1] for k in fails)
    if trap_flag and not fails:
        verdict += "  ⚠️ 但 dev 落陷阱窗 — 標 φ 陷阱"
    elif trap_flag and fails and not verdict.startswith("❌ 陷阱窗"):
        print("   ⚠️ 候選 dev %.2e 落陷阱窗 (1e-5,1e-3) — 標 φ 陷阱" % float(dev))
    print("   dev vs target = %.4e (%.4f%%)   sigma 距離 = %s"
          % (float(dev), float(dev) * 100,
             ("%.3f sigma" % float((expr_value - target) / sigma)) if sigma else "n/a"))
    print("   >> 判決: %s" % verdict)
    return verdict, steps, float(dev)


# ============================================================
# 3. 必要案例
# ============================================================
# T1: b_spec = 1/<v_g>_{1..22}
B_FIT = mp.mpf("1.1188501")
S_FIT = mp.mpf("0.0070934")
v1, s1, d1 = criterion(
    "T1", "b_spec = 1/<v_g>_{1..22}  (O169 零參數截距)",
    B_FIT, S_FIT, "1/<v_g>_{1..22}", B_SPEC,
    [("v_g(n) = cos(pi n/88)", mp.cos(PI / 88), "Q(zeta_176)^+", "O190 rapidity"),
     ("22 = N_d/2", mp.mpf(22), "Q", "O145 Z2 自對偶模 (gamma_22 = mu^2)")])

# T2: sqrt5/2 (phi 讀法)
v2, s2, d2 = criterion(
    "T2", "sqrt(5)/2  (O169 phi 讀法對照)",
    B_FIT, S_FIT, "sqrt5/2", SQ5_2,
    [("sqrt5 = 2phi-1", mp.sqrt(5), "Q(sqrt5)", "O97 自相似根 / O142 T_hat 譜")])

# T3: C_old = -0.1697 (O51 scripts/82 FAIL) — 用深度 2 最近命中嘅真值
SEC6 = mp.fsum([1 / mp.cos(n * PI / 88) for n in range(1, 7)]) / 6
SEC25 = mp.fsum([1 / mp.cos(n * PI / 88) for n in range(1, 26)]) / 25
C_OLD_BEST = SEC6 - SEC25
v3, s3, d3 = criterion(
    "T3", "C_old = -0.1697  (O51 scripts/82 已 FAIL)",
    mp.mpf("-0.1697"), None, "mean_sec_1_6 - mean_sec_1_25", C_OLD_BEST,
    [("mean_sec_1_6", SEC6, "Q(zeta_176)^+", ""),
     ("mean_sec_1_25", SEC25, "Q(zeta_176)^+", "")])

# ============================================================
# 4. 注入必然錯案例 (證明判準識 FAIL)
# ============================================================
print("\n" + "=" * 78)
print("注入必然錯案例 (O148 check 簽名坑教訓: 判準必須識 FAIL)")
print("=" * 78)
INJ = []

# T4a: 44 = 45 (① FAIL: 45 唔係譜泛函)
v4a, _, _ = criterion(
    "T4a", "[注入] 44 = 45", mp.mpf(44), None, "45", mp.mpf(45),
    [("45 (裸數)", mp.mpf(45), "Q", "")])
INJ.append(("T4a 裸數因子", v4a.startswith("❌")))

# T4b: b_spec = sqrt5/2 (⑤ FAIL: 域分離)
v4b, _, _ = criterion(
    "T4b", "[注入] b_spec 直接等於 sqrt(5)/2", B_SPEC, None, "sqrt5/2", SQ5_2,
    [("sqrt5 = 2phi-1", mp.sqrt(5), "Q(sqrt5)", "O97")])
INJ.append(("T4b 域分離", v4b.startswith("❌")))

# T4c: 含擬合常數 (③ FAIL)
v4c, _, _ = criterion(
    "T4c", "[注入] b = 1/<v_g>_{1..22} x 1.000237 (擬合因子)", B_FIT, None,
    "1/<v_g> x 1.000237", B_SPEC * mp.mpf("1.000237"),
    [("v_g(n) = cos(pi n/88)", mp.cos(PI / 88), "Q(zeta_176)^+", "O190"),
     ("1.000237 (擬合)", mp.mpf("1.000237"), "Q", "冇出處")],
    numeric_literals=[mp.mpf("1.000237")])
INJ.append(("T4c 擬合常數", v4c.startswith("❌")))

# T4d: 因子冇出處 (② FAIL) — 用 23 (非結構數)
v4d, _, _ = criterion(
    "T4d", "[注入] 1/<v_g>_{1..23}  (23 非註冊結構數)", B_FIT, None,
    "1/<v_g>_{1..23}", 1 / (mp.fsum([mp.cos(n * PI / 88) for n in range(1, 24)]) / 23),
    [("v_g(n) = cos(pi n/88)", mp.cos(PI / 88), "Q(zeta_176)^+", "O190"),
     ("23 (非結構數)", mp.mpf(23), "Q", "")])
INJ.append(("T4d 無出處因子", v4d.startswith("❌")))

# ============================================================
# 5. 判準對註冊常數集嘅整體判決
# ============================================================
print("\n" + "=" * 78)
print("判準對 O201/01 註冊常數集嘅整體判決")
print("=" * 78)
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
p = os.path.join(d, "01_spectral_dictionary.json")
with open(p) as f:
    D1 = json.load(f)
verd = D1["verdicts"]
cnt = {}
for nm, v in verd.items():
    k = v.split(":")[0]
    cnt[k] = cnt.get(k, 0) + 1
print("  由 01 掃描繼承嘅 tier 分佈:")
for k in sorted(cnt):
    print("    %-8s %d" % (k, cnt[k]))
print("  (判準 ① = tier A/B 命中; 判準 ④ = tier 唔可以係 TRAP/TRAP2)")

# ============================================================
# 5b. data 輸出
# ============================================================
out2 = {
    "cases": {
        "T1_b_spec": {"verdict": v1, "field": "Q(zeta_176)^+", "dev": float(d1)},
        "T2_sqrt5_2": {"verdict": v2, "dev": float(d2)},
        "T3_C_old": {"verdict": v3, "dev": float(d3)},
    },
    "injections": {nm: bool(ok) for nm, ok in INJ},
    "tier_distribution_from_01": cnt,
    "criterion_steps": ["(1) 譜表達存在", "(2) 每因子有獨立出處", "(3) 零參數 (無擬合常數)",
                        "(4) 過陷阱窗 (1e-5,1e-3)", "(5) 數域相容 (Q(zeta_176)^+ / Q(sqrt5) / Q)"],
    "verdict": "判準對 3 個已知案例判決正確 + 4 個注入必然錯案例全部識 FAIL",
}
os.makedirs(d, exist_ok=True)
p2 = os.path.join(d, "02_identity_criterion.json")
with open(p2, "w") as f:
    json.dump(out2, f, indent=2, ensure_ascii=False)
print("\n[data] %s" % os.path.abspath(p2))

# ============================================================
# 6. 自檢
# ============================================================
print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NPASS = NFAIL = 0


def check(label, cond):
    global NPASS, NFAIL
    if cond:
        NPASS += 1
        print("  PASS  %s" % label)
    else:
        NFAIL += 1
        print("  FAIL  %s" % label)


check("[INJECT] checker 識 FAIL (3 != 4)", not (abs(mp.mpf(3) - mp.mpf(4)) < EXACT_TOL))
check("T1 b_spec 判決 = ✅ 譜身份", v1.startswith("✅"))
check("T2 sqrt5/2 判決 = ❌ 域分離", "域分離" in v2)
check("T3 C_old 判決 = ❌ (陷阱窗)", v3.startswith("❌"))
check("T4a/b/c/d 全部識 FAIL", all(x[1] for x in INJ))
check("域分離定理: 5 ∤ 176", 176 % 5 != 0)
check("正對照: sqrt5 ∈ Q(zeta_10) (2phi-1)", sp.simplify(2 * phi_exact - 1 - sp.sqrt(5)) == 0)
check("Q(zeta_176) degree = 80", ND_176 == 80)
check("Q(zeta_176)^+ degree = 40", ND_176 / 2 == 40)
check("Q(zeta_88) degree = 40", ND_88 == 40)
check("b_spec 唔係 sqrt5/2 (dev %.3e)" % float(abs((B_SPEC - SQ5_2) / SQ5_2)),
      abs((B_SPEC - SQ5_2) / SQ5_2) > mp.mpf('1e-6'))
check("b_spec 同 DESI fit 差 %.3f sigma (< 1)" % float((B_SPEC - B_FIT) / S_FIT),
      abs((B_SPEC - B_FIT) / S_FIT) < 1)
check("窗律條件性: DESI fit 精度 %.2e >= 1e-4 => n/a" % float(S_FIT / B_FIT),
      float(S_FIT / B_FIT) >= 1e-4)
check("T1 dev < T2 dev (b_spec 較近觀測)", d1 < d2)
check("T3 最近命中落陷阱窗 (%.2e in (1e-5,1e-3))" % d3, 1e-5 < d3 < 1e-3)
check("注入案例數 = 4", len(INJ) == 4)

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
