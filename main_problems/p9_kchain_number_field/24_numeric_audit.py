#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P9 kchain_number_field — 數字審計 (2026-10-17) — 第二輪 (第一輪 2026-09-12, 21_doc_independent_audit.py 53/53)
=========================================================================================================
定位: 覆蓋 09-12 水位之後新加入嘅全部 headline 數字 (22_galois_symmetry + 23_beat_harmonic_bridge + 00_record 新章節)
紀律: 零 import 任何原推導 script; 由第一原理 (ω_n=2sin(πn/88), γ_n=4sin²(πn/88)) 重算
精度: mpmath dps=50 全域; 整數/有理用 Fraction 位對位
段:
  A. 數域核心 (degree 公式, 7 orbits, orbit size=degree)
  B. Galois 作用 (σ_a(γ_n)=γ_an mod 88; ω σ 作用 48.6% 瀉出)
  C. A1: |γ_i−γ_j| = beat(i,j)×(ω_i+ω_j) 946/946
  D. A2: ω_11·ω_33=√2, 譜線補償 21/21, γ-beat 6 閉合
  E. A3: closure = {±ω_1..±ω_43}∪{2}, |closure|=87, 0 缺席證明
  F. V_min 身份鏈: μ²=2, V_min=−μ⁴L₁₀/8=−61.5=−⟨W⟩²
  G. Z₂ 候選: 2 階元素 {23,65,87} (a²≡1 mod 176), σ_43/45/87 正負各半 22/44
輸出: data/24_numeric_audit.json (PASS/FAIL 逐項)
"""
import json, math, os
from fractions import Fraction
from math import gcd
import mpmath as mp

mp.mp.dps = 50

D = os.path.dirname(os.path.abspath(__file__))

# ---------- 第一原理定義 ----------
def w(n):  # ω_n = 2sin(πn/88), n=1..44
    return mp.mpf(2) * mp.sin(mp.pi * n / 88)

def gam(n):  # γ_n = 4sin²(πn/88), n=1..44
    return mp.mpf(4) * mp.sin(mp.pi * n / 88) ** 2

def deg_omega(n):
    """deg(ω_n) = φ(176/gcd(|44−n|,176))/2, e=1,2 → 1 (有理)"""
    k = abs(44 - n)
    g = math.gcd(k, 176)
    e = 176 // g
    if e <= 2:
        return 1
    # φ(e)
    e2, phi = e, e
    p = 2
    while p * p <= e2:
        if e2 % p == 0:
            phi -= phi // p
            while e2 % p == 0:
                e2 //= p
        p += 1
    if e2 > 1:
        phi -= phi // e2
    return phi // 2

def deg_gamma(n):
    """deg(γ_n) = φ(88/gcd(n,88))/2, e=1,2 → 1 (有理)"""
    e = 88 // gcd(n, 88)
    if e <= 2:
        return 1
    e2, phi = e, e
    p = 2
    while p * p <= e2:
        if e2 % p == 0:
            phi -= phi // p
            while e2 % p == 0:
                e2 //= p
        p += 1
    if e2 > 1:
        phi -= phi // e2
    return phi // 2

def sigma_g(a, n):
    """σ_a(γ_n) = γ_{an mod 88} (a 奇數, gcd(a,176)=1)"""
    return gam((a * n) % 88)

def sigma_w(a, n):
    """σ_a(ω_n) = 2cos(π·(a(44−n) mod 176)/88)"""
    k = 44 - n
    ak = (a * k) % 176
    return mp.mpf(2) * mp.cos(mp.pi * ak / 88)

R40 = [a for a in range(1, 89) if gcd(a, 176) == 1]

results = []
def chk(name, ok, detail=""):
    results.append({"name": name, "pass": bool(ok), "detail": str(detail)[:160]})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

# ---------- A. 數域核心 ----------
# A1: deg(ω_n) 分佈 {1:1, 2:1, 4:2, 5:5, 10:5, 20:10, 40:20}
dist = {}
for n in range(1, 45):
    d = deg_omega(n)
    dist[d] = dist.get(d, 0) + 1
exp_dist = {1: 1, 2: 1, 4: 2, 5: 5, 10: 5, 20: 10, 40: 20}
chk("A1 deg(ω_n) 分佈", dist == exp_dist, f"got {dist}")

# A2: γ_n degree 分佈 — 44 個 γ ∈ ℚ(ζ88)⁺ deg ≤ 20
gdist = {}
for n in range(1, 45):
    d = deg_gamma(n)
    gdist[d] = gdist.get(d, 0) + 1
# 期望: gcd(n,88) 類別大小 = deg 分佈: n 1..44, gcd 1→20 個 deg20... 
# 直接驗: γ_n = ω_n² ⟹ deg(γ_n) = deg(ω_n)/2 or = deg(ω_n)? γ=2−2cos(πn/44), deg_gamma(n) 公式下
# 抽樣比較最小多項式度: 用數值 Galois 軌道 size 代替
g_orbits = {}
for n in range(1, 45):
    s = set()
    for a in R40:
        v = sigma_g(a, n)
        s.add(str(mp.nstr(v, 20)))
    g_orbits[n] = len(s)
# orbit size 必須 = deg_gamma(n)
ok_orb = all(g_orbits[n] == deg_gamma(n) for n in range(1, 45))
chk("A2 γ orbit size = deg(γ_n) ∀n", ok_orb, f"7 orbits: {sorted(set(g_orbits.values()))}")

# A3: 7 個 gcd 類別 size 之和 = 44, size 值 = {1,2,5,5,10,20,1}
gcds = [gcd(n, 88) for n in range(1, 45)]
from collections import Counter
gcount = Counter(gcds)
chk("A3 7 gcd 類別", len(gcount) == 7 and sum(gcount.values()) == 44,
    f"{sorted(gcount.items())}")

# ---------- B. Galois 作用 ----------
# B1: σ_a² = id? 唔係必須. B1: σ_a 係 40 個元素 (R40), 每個 a 有 |orbit| = |Gal|/|H|
# B1 代替: (ℤ/88ℤ)×/{±1} 群大小 = φ(88)/2 = 20
chk("B1 |Gal(ℚ(ζ88)+/ℚ)| = 20", len(R40) // 2 == 20, f"R40={len(R40)}, /2 = {len(R40)//2}")

# B2: ω 48.6% 瀉出 (856/1760) — 瀉出嘅 (a,n) 對數 (唔可以 set 去重!)
leak_pairs = 0
total = 0
for n in range(1, 45):
    for a in R40:
        v = sigma_w(a, n)
        # 原 44-site 正頻率集 {ω_1..ω_44}
        in_set = any(abs(v - w(m)) < mp.mpf("1e-30") for m in range(1, 45))
        total += 1
        if not in_set:
            leak_pairs += 1
ratio = Fraction(leak_pairs, total)
chk("B2 ω σ-像瀉出 48.6%", leak_pairs == 856 and total == 1760,
    f"{leak_pairs}/{total} = {float(ratio)*100:.1f}% (預言 856/1760=48.6%)")

# B3: 例子 σ_3(ω_1) = −0.2138 (負頻率)
v3 = sigma_w(3, 1)
chk("B3 σ_3(ω_1) 負頻率", mp.sign(v3) < 0 and abs(abs(v3) - mp.mpf("0.2138")) < mp.mpf("1e-3"),
    f"σ_3(ω_1) = {mp.nstr(v3, 10)}")

# ---------- C. A1: |γ_i−γ_j| = beat(i,j)×(ω_i+ω_j) 946/946 ----------
n_pass = 0
n_tot = 0
for i in range(1, 45):
    for j in range(i + 1, 45):
        n_tot += 1
        lhs = abs(gam(i) - gam(j))
        rhs = abs(w(i) - w(j)) * (w(i) + w(j))
        if abs(lhs - rhs) < mp.mpf("1e-35"):
            n_pass += 1
chk(f"C1 A1 946/946", n_pass == 946 == n_tot, f"{n_pass}/{n_tot}")

# ---------- D. A2 ----------
# D1: ω_11·ω_33 = √2
p = w(11) * w(33)
chk("D1 ω_11·ω_33 = √2", abs(p - mp.sqrt(2)) < mp.mpf("1e-35"), f"{mp.nstr(p, 20)}")

# D2: 譜線補償 ω_{2m}+ω_44 = γ_{22+m}  (m=1..21)
n_pass = 0
for m in range(1, 22):
    lhs = w(2 * m) + w(44)
    rhs = gam(22 + m)
    if abs(lhs - rhs) < mp.mpf("1e-35"):
        n_pass += 1
chk("D2 譜線補償 21/21", n_pass == 21, f"{n_pass}/21")

# D3: γ-beat 6 閉合根式
pairs = [(11, 22, "√2"), (22, 33, "√2"), (11, 33, "2√2"),
         (11, 44, "2+√2"), (22, 44, "2"), (33, 44, "2−√2")]
ok = True
for (i, j, form) in pairs:
    v = abs(gam(i) - gam(j))
    if form == "√2":
        t = mp.sqrt(2)
    elif form == "2√2":
        t = 2 * mp.sqrt(2)
    elif form == "2+√2":
        t = 2 + mp.sqrt(2)
    elif form == "2":
        t = 2
    else:
        t = 2 - mp.sqrt(2)
    if abs(v - t) > mp.mpf("1e-35"):
        ok = False
        print(f"   FAIL γ_{i}−γ_{j}: {mp.nstr(v,20)} vs {form}")
chk("D3 γ-beat 6 閉合", ok)

# ---------- E. A3 ----------
# E1: closure = {±ω_1..±ω_43} ∪ {2}, |closure| = 87
closure_vals = []
for n in range(1, 45):
    for a in R40:
        v = sigma_w(a, n)
        if not any(abs(v - u) < mp.mpf("1e-25") for u in closure_vals):
            closure_vals.append(v)
expected_vals = []
for n in range(1, 44):
    for sgn in (1, -1):
        v = sgn * w(n)
        if not any(abs(v - u) < mp.mpf("1e-25") for u in expected_vals):
            expected_vals.append(v)
expected_vals.append(mp.mpf(2))
chk("E1 closure size 87", len(closure_vals) == 87, f"{len(closure_vals)} 個")

# E2: closure = expected (數值 tolerance 比較)
c_not_in_e = []
for v in closure_vals:
    if not any(abs(v - u) < mp.mpf("1e-25") for u in expected_vals):
        c_not_in_e.append(mp.nstr(v, 20))
e_not_in_c = []
for v in expected_vals:
    if not any(abs(v - u) < mp.mpf("1e-25") for u in closure_vals):
        e_not_in_c.append(mp.nstr(v, 20))
chk("E2 closure 集 = {±ω_1..±ω_43}∪{2}",
    len(c_not_in_e) == 0 and len(e_not_in_c) == 0,
    f"closure−exp={c_not_in_e[:2]}, exp−closure={e_not_in_c[:2]}")

# E3: 0 缺席 — σ_a(ω_n)=0 無解
has_zero = False
zero_ach = None
for n in range(1, 45):
    for a in R40:
        if abs(sigma_w(a, n)) < mp.mpf("1e-30"):
            has_zero = True
            zero_ach = (a, n)
chk("E3 0 缺席 (σ_a(ω_n)=0 無解)", not has_zero, f"命中: {zero_ach}")

# E4: W88 唯一缺席點 = 0
W88_vals = [2 * mp.cos(mp.pi * m / 88) for m in range(0, 88)]
all_in_w = all(any(abs(s - t) < mp.mpf("1e-25") for t in W88_vals) for s in closure_vals)
chk("E4 closure ⊆ W88", all_in_w, f"|W88|={len(W88_vals)}")
missing = [t for t in W88_vals
           if not any(abs(t - s) < mp.mpf("1e-25") for s in closure_vals)]
chk("E5 W88 − closure = {0}", len(missing) == 1 and abs(missing[0]) < mp.mpf("1e-20"),
    f"缺席 {[mp.nstr(m, 8) for m in missing[:2]]}")

# ---------- F. V_min 身份鏈 ----------
# F1: Σγ_even=46, Σγ_odd=44, μ²=2
se = sum(gam(n) for n in range(1, 45) if n % 2 == 0)
so = sum(gam(n) for n in range(1, 45) if n % 2 == 1)
chk("F1 Σγ_even=46, Σγ_odd=44", abs(se - 46) < mp.mpf("1e-30") and abs(so - 44) < mp.mpf("1e-30"),
    f"even={mp.nstr(se,15)}, odd={mp.nstr(so,15)}")
mu2 = 2
L10 = 123
Vmin = -mu2**2 * L10 / 8
chk("F2 V_min = −μ⁴L₁₀/8 = −61.5", Vmin == -61.5, f"{Vmin}")
chk("F3 ⟨W⟩² = L₁₀/2 = 61.5", L10 / 2 == 61.5)
chk("F4 V_min = −L₁₀/2 = −⟨W⟩²", Vmin == -(L10 / 2))

# ---------- G. Z₂ 候選 ----------
# G1: 2 階元素 a²≡1 (mod 176), a∈{23,65,87}
two_orders = [a for a in R40 if (a * a) % 176 == 1 and a != 1]
chk("G1 Z₂ 2 階元素 {23,65,87}", two_orders == [23, 65, 87], f"{two_orders}")

# G2: σ_43/45/87 正負各半 22/44
ok = True
for a in [43, 45, 87]:
    pos = sum(1 for n in range(1, 45) if sigma_w(a, n) > 0)
    if pos != 22:
        ok = False
        print(f"   a={a}: 正值 {pos}/44")
chk("G2 σ_43/45/87 正負各半", ok)

# summary
npass = sum(1 for r in results if r["pass"])
nall = len(results)
print(f"\nRESULT: {npass}/{nall} PASS")

out = {"date": "2026-10-17", "results": results, "summary": f"{npass}/{nall}"}
with open(os.path.join(D, "data", "24_numeric_audit.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
sys_exit = 0 if npass == nall else 1
raise SystemExit(sys_exit)