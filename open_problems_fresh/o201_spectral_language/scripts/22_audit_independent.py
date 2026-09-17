#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/22 -- Session 6 獨立審計 (Independent Audit of Session 6)

## 目的 (審計, 唔係新推導)
  由零獨立重算 docs/20/21/22 嘅每一條數值宣稱 — 唔 import o201_basis,
  唔重用推導 script 嘅中間量, 自己定義譜基 + 群論事實, 逐條對比文檔寫嘅值。

## 審計對象
  docs/20 (ℓ_Nyq = log₄18), docs/21 (δ 超越性), docs/22 (Abel 公設)
  + 交叉核對 docs/01 §二 (Σγ = 90 / 44 / 46), docs/18 (r44/r33)

## 檢查類別
  A 數值重算 (mpmath, dps = 50)
  B 群論事實真算 (枚舉元素 + 共軛類 + 交換子子群) — 唔用硬編表
  C 約定衝突檢查 (γ_44 雙約定: 88-環 vs 176-Laplacian)
  D 外部註冊值核對 (唯讀 corpus, 記錄出處)

## 版本史
  v1 (2026-09-17): 首版 — Session 6 三項獨立審計。
"""
import os
import sys
import json
import itertools

import mpmath as mp

mp.mp.dps = 50
PI = mp.pi
PHI = (1 + mp.sqrt(5)) / 2

# ---- 自己定義結構數 (唔 import o201_basis) ----
N_d, B, N_GEN = 44, 4, 3
L = [2, 1]                       # Lucas: L_0, L_1
for _ in range(2, 20):
    L.append(L[-1] + L[-2])
F = [0, 1]                       # Fib: F_0, F_1
for _ in range(2, 20):
    F.append(F[-1] + F[-2])
L6, L10, L12 = L[6], L[10], L[12]
F7 = F[7]
F_PROJ = 17

# 譜基 (自己算)
G88conv = [4 * mp.sin(n * PI / 88) ** 2 for n in range(1, N_d + 1)]   # n = 1..44
G176conv = [4 * mp.sin(k * PI / 176) ** 2 for k in range(1, 89)]      # k = 1..88

NP = NF = 0
FAILS = []


def check(label, cond, detail=""):
    global NP, NF
    if cond:
        NP += 1
        print("  PASS  %s%s" % (label, ("  [%s]" % detail) if detail else ""))
    else:
        NF += 1
        FAILS.append(label)
        print("  FAIL  %s%s" % (label, ("  [%s]" % detail) if detail else ""))


def close(a, b, tol):
    return abs(mp.mpf(a) - mp.mpf(b)) <= mp.mpf(tol)


print("=" * 78)
print("O201/22 -- Session 6 獨立審計 v1 (零 import, 由零重算)")
print("=" * 78)

# ============================================================
print("\n" + "=" * 78)
print("A. 數值重算 — docs/20 (ℓ_Nyq = log_4(18))")
print("=" * 78)
log4_18 = mp.log(18) / mp.log(4)
print("  log_4(18) = %s" % mp.nstr(log4_18, 40))
check("A1 結構數 L_6 = 18", L6 == 18, "L_6 = %d" % L6)
check("A2 1 + F_proj = 18 = L_6", 1 + F_PROJ == 18)
check("A3 18 = 2*N_gen^2", 2 * N_GEN ** 2 == 18)
check("A4 底 4 = B", B == 4)

reg = mp.mpf("2.08496250072")
o193 = mp.mpf("2.084962501")
dev_reg = abs(log4_18 - reg) / log4_18
dev_o193 = abs(log4_18 - o193) / log4_18
print("  dev(O201 註冊 2.08496250072) = %.3e   (文檔聲稱 5.5e-13)" % float(dev_reg))
print("  dev(O193 精確 2.084962501)   = %.3e   (文檔聲稱 1.3e-10)" % float(dev_o193))
check("A5 dev(O201 註冊) = 5.5e-13 (文檔值正確)",
      float(dev_reg) < 1e-12 and abs(float(dev_reg) - 5.5e-13) < 0.2e-13,
      "%.3e" % float(dev_reg))
check("A6 dev(O193 精確) = 1.3e-10 (文檔值正確)",
      abs(float(dev_o193) - 1.3e-10) < 0.1e-10, "%.3e" % float(dev_o193))

# 舊候選池 (docs/20 §二 聲稱嘅 dev)
old = {
    "25/12": mp.mpf(25) / 12,
    "L5^2/58": mp.mpf(L[5] ** 2) / 58,
    "pi - L6/F_proj": PI - mp.mpf(L6) / F_PROJ,
    "2 + 1/11.7699": 2 + 1 / mp.mpf("11.7699"),
}
doc_dev = {"25/12": 0.078, "L5^2/58": 0.060, "pi - L6/F_proj": 0.105}
print("  舊候選 dev (文檔 vs 重算):")
for nm, v in old.items():
    dv = float(abs(v - log4_18) / log4_18 * 100)
    claim = doc_dev.get(nm)
    tag = "(文檔 %.3f%%)" % claim if claim is not None else "(文檔無值)"
    print("    %-16s %.4f%%  %s" % (nm, dv, tag))
    if claim is not None:
        check("A7 舊候選 %s dev = %.3f%% (文檔值正確)" % (nm, claim),
              abs(dv - claim) < 0.002, "%.4f%%" % dv)

# ============================================================
print("\n" + "=" * 78)
print("B. 數值重算 — docs/21 (δ 超越性)")
print("=" * 78)
delta = mp.e / (PHI ** 2 * mp.mpf(27) / mp.mpf(26)) - 1
print("  δ = e/(phi^2*27/26) - 1 = %s" % mp.nstr(delta, 25))
print("  文檔聲稱 δ = -1.6396466e-4")
dev_delta = abs(delta + mp.mpf("1.6396466e-4"))
check("B1 δ 重現文檔值 -1.6396466e-4 (10 位)", float(dev_delta) < 1e-11,
      "|diff| = %.3e" % float(dev_delta))

dln = -mp.log(1 + delta)
dln_exact = 2 * mp.log(PHI) + mp.log(mp.mpf(27) / mp.mpf(26)) - 1
print("  δ_ln = -ln(1+δ) = %s" % mp.nstr(dln, 20))
check("B2 δ_ln = 2lnφ + ln(27/26) - 1 EXACT (by construction)",
      abs(dln - dln_exact) < mp.mpf("1e-45"), "%.3e" % float(abs(dln - dln_exact)))
check("B3 δ_ln 值 = +1.6397810e-4 (文檔值)",
      abs(dln - mp.mpf("1.6397810e-4")) < mp.mpf("1e-11"), mp.nstr(dln, 12))

inv = 1 / abs(delta)
print("  1/|δ| = %s" % mp.nstr(inv, 22))
cand = (L6 + 1) * (L12 - 1) - mp.mpf(1) / 8
dev_cand = abs(cand - inv) / inv
print("  (L6+1)(L12-1) - 1/8 = %d - 1/8 = %s" % (19 * 321, mp.nstr(cand, 18)))
print("  dev = %.3e   (script 20 聲稱 3.4e-8; docs/21 聲稱 4.4e-8)" % float(dev_cand))
check("B4 L_12 = 322 (Lucas)", L12 == 322, "L_12 = %d" % L12)
check("B5 (L6+1)(L12-1) = 19*321 = 6099", (L6 + 1) * (L12 - 1) == 6099)
check("B6 dev(6099 - 1/8) = 4.412e-8 (docs/21 值正確)",
      abs(float(dev_cand) - 4.412e-8) < 0.01e-8, "%.4e" % float(dev_cand))
check("B7 docs/21 寫嘅 1/|δ| = 6098.87526911 正確 (真值 6098.87526910689)",
      abs(inv - mp.mpf("6098.87526911")) < mp.mpf("1e-8"),
      "|diff| = %.3e" % float(abs(inv - mp.mpf("6098.87526911"))))
check("B8 docs/21 寫嘅 dev 4.4e-8 正確",
      abs(float(dev_cand) - 4.4e-8) < 0.05e-8, "%.3e" % float(dev_cand))
check("B8b docs/11 + docs/15 寫嘅 1/|δ| = 6098.87526911 一致",
      all("6098.87526911" in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", f), encoding="utf-8").read()
          for f in ("11_transcendental_layer.md", "15_interface_residuals.md")))

# 殘餘族 (docs/18 註冊值)
r44 = 1 - (1 + delta) ** 44
r33 = (1 + delta) ** -33 - 1
print("  r44 = %.8f%%  (docs/18 註冊 0.718907%%)" % float(r44 * 100))
print("  r33 = %.8f%%  (docs/18 註冊 0.542594%%)" % float(r33 * 100))
check("B9 r44 重現 docs/18 (0.718907%)",
      abs(float(r44 * 100) - 0.718907) < 0.00001, "%.6f%%" % float(r44 * 100))
check("B10 r33 重現 docs/18 (0.542594%)",
      abs(float(r33 * 100) - 0.542594) < 0.00001, "%.6f%%" % float(r33 * 100))

check("B11 27 = N_gen^3", N_GEN ** 3 == 27)
check("B12 26 = 2*F_7", 2 * F7 == 26, "F_7 = %d" % F7)
check("B13 26 = N_gen^3 - 1 (O168 形)", N_GEN ** 3 - 1 == 26)

# ============================================================
print("\n" + "=" * 78)
print("C. 約定衝突檢查 — γ_44 雙約定 (docs/21 括號宣稱)")
print("=" * 78)
g44_88 = G88conv[N_d - 1]      # n = 44, 88-環約定
g44_176 = G176conv[43]         # k = 44, 176-Laplacian 約定
print("  88-環約定  γ_44 = 4sin²(44π/88)   = %s" % mp.nstr(g44_88, 10))
print("  176-約定   γ_44 = 4sin²(44π/176)  = %s" % mp.nstr(g44_176, 10))
print("  μ² = 2 (O159/O169)")
check("C1 88-環約定 γ_44 = 4 (= Nyquist 原子)", close(g44_88, 4, "1e-40"))
check("C2 176-約定 γ_44 = 2 = μ²", close(g44_176, 2, "1e-40"))
check("C3 μ²/B² = 2/16 = 1/8 (docs/21 候選嘅 1/8 身份)", close(mp.mpf(2) / 16, mp.mpf(1) / 8, "1e-45"))
check("C4 ⚠️ 88-環 γ_44/B² = 4/16 = 1/4 ≠ 1/8 — docs/21 括號「γ_44/B²」寫法有約定歧義",
      close(g44_88 / 16, mp.mpf(1) / 4, "1e-40"))
S_gam = mp.fsum(G88conv)
S_odd = mp.fsum(G88conv[0::2])
S_even = mp.fsum(G88conv[1::2])
print("  Σγ = %s, Σγ_odd = %s, Σγ_even = %s  (docs/01 聲稱 90/44/46)"
      % (mp.nstr(S_gam, 10), mp.nstr(S_odd, 10), mp.nstr(S_even, 10)))
check("C5 Σγ = 90 (docs/01)", close(S_gam, 90, "1e-40"))
check("C6 Σγ_odd = 44 = N_d (docs/01)", close(S_odd, 44, "1e-40"))
check("C7 Σγ_even = 46 (docs/01)", close(S_even, 46, "1e-40"))
check("C8 Σγ_even − Σγ_odd = 2 = μ² (O192/O203)", close(S_even - S_odd, 2, "1e-40"))

# ============================================================
print("\n" + "=" * 78)
print("D. 群論事實真算 — docs/22 (唔用硬編表)")
print("=" * 78)


def cycle_decomp(p):
    n = len(p)
    seen = [False] * n
    cyc = []
    for i in range(n):
        if not seen[i]:
            c = []
            j = i
            while not seen[j]:
                seen[j] = True
                c.append(j)
                j = p[j]
            cyc.append(tuple(c))
    return tuple(sorted((len(c) for c in cyc), reverse=True))


def conj_classes(elems, mul, inv):
    s = set(elems)
    seen = set()
    cls = []
    for x in elems:
        if x in seen:
            continue
        orb = set()
        for g in elems:
            orb.add(mul(mul(g, x), inv(g)))
        seen |= orb
        cls.append(orb)
    return cls


def commutator_subgroup(elems, mul, inv):
    """由交換子 {[a,b]} 生成嘅子群 (閉包), 回傳 (子群, 單位元)"""
    e = None
    for x in elems:
        if all(mul(x, y) == y for y in elems):
            e = x
            break
    gen = set()
    for a in elems:
        for b in elems:
            gen.add(mul(mul(a, b), mul(inv(a), inv(b))))
    gen.discard(e)
    sub = {e}
    changed = True
    while changed:
        changed = False
        new = set()
        for a in sub:
            for b in gen:
                c = mul(a, b)
                if c not in sub:
                    new.add(c)
        if new:
            sub |= new
            changed = True
    return sub, e


# --- S_3 (permutations of 3) ---
perms3 = [p for p in itertools.permutations(range(3))]
mul3 = lambda a, b: tuple(a[b[i]] for i in range(3))
inv3 = lambda p: tuple(sorted(range(3), key=lambda i: p[i]))
cls3 = conj_classes(perms3, mul3, inv3)
com3, e3 = commutator_subgroup(perms3, mul3, inv3)
ab3 = len(perms3) // len(com3)
print("  S_3 : |G| = %d, 共軛類 (#irreps) = %d, |[G,G]| = %d, 一維特徵標 = |G/[G,G]| = %d"
      % (len(perms3), len(cls3), len(com3), ab3))

# --- D_4 (symmetries of square: rotations r^i, reflections r^i s) ---
D4 = []
for i in range(4):
    D4.append(("r", i))
    D4.append(("s", i))
def mul4(a, b):
    """元素 = r^i s^eps: ("r",i) = r^i, ("s",i) = r^i s
       r^i·r^j = r^{i+j}; r^i·(r^j s) = r^{i+j}s;
       (r^i s)·r^j = r^{i-j}s;  (r^i s)(r^j s) = r^{i-j}"""
    ka, ia = a
    kb, ib = b
    if ka == "r" and kb == "r":
        return ("r", (ia + ib) % 4)
    if ka == "r" and kb == "s":
        return ("s", (ia + ib) % 4)
    if ka == "s" and kb == "r":
        return ("s", (ia - ib) % 4)
    return ("r", (ia - ib) % 4)
def inv4(a):
    k, i = a
    if k == "r":
        return ("r", (-i) % 4)
    return ("s", i)
cls4 = conj_classes(D4, mul4, inv4)
com4, e4 = commutator_subgroup(D4, mul4, inv4)
ab4 = len(D4) // len(com4)
print("  D_4 : |G| = %d, 共軛類 (#irreps) = %d, |[G,G]| = %d, 一維特徵標 = %d"
      % (len(D4), len(cls4), len(com4), ab4))

# --- A_5 (even permutations of 5) ---
perms5 = [p for p in itertools.permutations(range(5))]
def parity(p):
    n = len(p)
    seen = [False] * n
    sgn = 1
    for i in range(n):
        if not seen[i]:
            j = i
            L = 0
            while not seen[j]:
                seen[j] = True
                j = p[j]
                L += 1
            if L % 2 == 0:
                sgn = -sgn
    return sgn
A5 = [p for p in perms5 if parity(p) == 1]
mul5 = lambda a, b: tuple(a[b[i]] for i in range(5))
inv5 = lambda p: tuple(sorted(range(5), key=lambda i: p[i]))
cls5 = conj_classes(A5, mul5, inv5)
com5, e5 = commutator_subgroup(A5, mul5, inv5)
ab5 = len(A5) // len(com5)
print("  A_5 : |G| = %d, 共軛類 (#irreps) = %d, |[G,G]| = %d, 一維特徵標 = %d"
      % (len(A5), len(cls5), len(com5), ab5))

# --- Z_88 ---
N88 = 88
cls88 = N88                     # 循環群: 88 個共軛類
ab88 = N88                      # 全 Abelian ⇒ [G,G] = {e}
print("  Z_88: |G| = %d, 共軛類 (#irreps) = %d, 一維特徵標 = %d" % (N88, cls88, ab88))

check("D1 S_3: #irreps = 3, 一維 = 2 (docs/22 表)", len(cls3) == 3 and ab3 == 2)
check("D2 D_4: #irreps = 5, 一維 = 4 (docs/22 表)", len(cls4) == 5 and ab4 == 4)
check("D3 A_5: #irreps = 5, 一維 = 1 (docs/22 表)", len(cls5) == 5 and ab5 == 1)
check("D4 Z_88: #irreps = 88, 一維 = 88 (docs/22 表)", cls88 == 88 and ab88 == 88)
check("D5 對偶定理: 一維特徵標 = |G| ⟺ Abel (Z_88 滿額, 其餘全部唔滿)",
      ab88 == N88 and ab3 < 6 and ab4 < 8 and ab5 < 60)
check("D6 A_5 係完美群 ([G,G] = G) ⟹ 一維只有 trivial",
      len(com5) == len(A5))

# Z_88 特徵標獨立構造: χ_k(g) = exp(2πi k g/88) — 用複數對 (cos, sin), 唔可以只用 cos
chars = set()
for k in range(88):
    chars.add(tuple((round(float(mp.cos(2 * PI * k * g / 88)), 10),
                     round(float(mp.sin(2 * PI * k * g / 88)), 10)) for g in range(88)))
check("D7 Z_88 特徵標獨立構造 = 88 個相異 (全部一維)", len(chars) == 88,
      "%d 個" % len(chars))

# 循環圖 C_88 譜 (Z_88 上嘅 Laplacian) — 88 模態標籤 vs 譜簡併
lam = sorted(set(round(float(2 - 2 * mp.cos(2 * PI * k / 88)), 10) for k in range(88)))
print("  C_88 Laplacian 相異特徵值 = %d 個 (88 模態有簡併: k ↔ 88−k 二重)" % len(lam))
check("D8 ⚠️ C_88 譜本身有二重簡併 (45 相異值 / 88 模態) — docs/22 T2「非 Abel 才簡併」措辭過強",
      len(lam) == 45, "%d 相異值" % len(lam))

# ============================================================
print("\n" + "=" * 78)
print("E. 外部註冊值核對 (唯讀, 記錄出處)")
print("=" * 78)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ext = {
    "O193 docs/04: ℓ_max = log₄18 = 2.08496": ("o193_power_sum_domain/docs/04_moment_domain_cutoff.md", "log₄18"),
    "O138 final_result: 三路收斂 ℓ_max = log₄18 = 2.084962": ("o138_qm_measurement_structural/final_result.md", "log₄18"),
    "O170 docs/03: ℓ_nyq = log₄18": ("o170_phase_depth_distance/docs/03_transverse_radial_consistency.md", "log₄18"),
    "O76 scripts/08: ℓ_Nyquist = log₄(18)": ("o76_z_redshift_translation/scripts/08_projection_saturation.py", "log₄(18)"),
    "O140 docs/02: N_ℓ = 44·4^ℓ": ("o140_finite_spectral_relativity/docs/02_fsr_derivation.md", "44·4^ℓ"),
    "O41 docs/01: B(n) = L₁₀/(2N_d) = 123/88 均勻": ("o41_observer_budget/docs/01_derivation_record.md", "123/88"),
    "O168 docs/13: e ≈ φ²·(27/26)": ("o168_g_last_input/docs/13_ebase_bridge.md", "27/26"),
    "O165 docs/01: e 超越 ⇒ 結構上不可能": ("o165_exponential_weight_origin/docs/01_ekappa_label_audit.md", "e 超越"),
}
for label, (rel, needle) in ext.items():
    p = os.path.join(ROOT, rel)
    ok = os.path.exists(p) and needle in open(p, encoding="utf-8").read()
    check("E %s" % label, ok, "搵到" if ok else "搵唔到!")

check("E9 L_10 = 123 (O41 預算分子)", L10 == 123, "L_10 = %d" % L10)
check("E10 123/88 = 1.397727... (O41 B(n))", close(mp.mpf(123) / 88, mp.mpf("1.3977272727"), "1e-9"))

# ============================================================
print("\n" + "=" * 78)
print("G. 文檔-腳本數值一致性掃描 (捉手寫數錯)")
print("=" * 78)
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")


def has(rel, needle):
    p = os.path.join(HERE, rel)
    return os.path.exists(p) and needle in open(p, encoding="utf-8").read()


def claims_only(rel):
    """檔案內容但剔除「## 版本史」段 (歷史註記可以引舊值, 唔算 stale 宣稱)"""
    lines = open(os.path.join(HERE, rel), encoding="utf-8").read().split("\n")
    out, in_hist = [], False
    for ln in lines:
        if ln.strip().startswith("## 版本史"):
            in_hist = True
            continue
        if in_hist:
            if ln.strip() == '"""':
                in_hist = False
            continue
        out.append(ln)
    return "\n".join(out)


S20 = claims_only("20_delta_transcendence.py")
check("G1 scripts/20 宣稱段冇 stale 手寫值 3.4e-8", "3.4e-8" not in S20)
check("G2 scripts/20 宣稱段冇 stale 手寫值 6098.87520884073",
      "6098.87520884073" not in S20)
check("G3 scripts/20 寫嘅 1/|δ| 同計算值一致 (6098.875269...)",
      has("20_delta_transcendence.py", "6098.87526910689"))
check("G4 scripts/20 寫嘅 dev 同計算值一致 (4.4e-8)",
      has("20_delta_transcendence.py", "4.4e-8"))
check("G5 docs/21 寫 6098.87526911 + dev 4.412e-8",
      has(os.path.join(DOCS, "21_delta_transcendence.md"), "6098.87526911")
      and has(os.path.join(DOCS, "21_delta_transcendence.md"), "4.412e-8"))
check("G6 docs/20 寫 log₄(18) + dev 5.5e-13",
      has(os.path.join(DOCS, "20_lnyq_log4_closure.md"), "log₄(18)")
      and has(os.path.join(DOCS, "20_lnyq_log4_closure.md"), "5.5e-13"))
check("G7 docs/22 寫 123/88 (O41 預算)",
      has(os.path.join(DOCS, "22_abelian_axiom.md"), "123/88"))
check("G8 scripts/20 冇恆真 check (True 佔位)",
      "check(\"T1 δ 超越 (e 超越 + 代數閉包論證)\", True)" not in
      open(os.path.join(HERE, "20_delta_transcendence.py"), encoding="utf-8").read())
check("G9 scripts/21 冇硬編群論表自查 (循環驗證)",
      "n_irreps_and_onedim" not in open(os.path.join(HERE, "21_abelian_axiom.py"), encoding="utf-8").read())

# ============================================================
print("\n" + "=" * 78)
print("F. 摘要")
print("=" * 78)
print("  總計: %d/%d PASS" % (NP, NP + NF))
if FAILS:
    print("  FAIL 清單:")
    for f in FAILS:
        print("    - %s" % f)

out = {
    "audit": "Session 6 獨立審計 (零 import, 由零重算)",
    "targets": ["docs/20", "docs/21", "docs/22", "docs/01 §二", "docs/18"],
    "total": "%d/%d" % (NP, NP + NF),
    "fails": FAILS,
    "key_values": {
        "log4_18": mp.nstr(log4_18, 30),
        "dev_O201_reg": float(dev_reg),
        "dev_O193": float(dev_o193),
        "delta": mp.nstr(delta, 20),
        "inv_abs_delta": mp.nstr(inv, 20),
        "dev_candidate": float(dev_cand),
        "r44_pct": float(r44 * 100),
        "r33_pct": float(r33 * 100),
        "gamma44_88conv": mp.nstr(g44_88, 10),
        "gamma44_176conv": mp.nstr(g44_176, 10),
        "Sum_gamma": mp.nstr(S_gam, 10),
        "Sum_odd": mp.nstr(S_odd, 10),
        "Sum_even": mp.nstr(S_even, 10),
    },
    "group_theory": {
        "S3": {"order": 6, "irreps": len(cls3), "onedim": ab3},
        "D4": {"order": 8, "irreps": len(cls4), "onedim": ab4},
        "A5": {"order": 60, "irreps": len(cls5), "onedim": ab5},
        "Z88": {"order": 88, "irreps": 88, "onedim": 88},
        "C88_distinct_eigenvalues": len(lam),
    },
    "issues_found": [
        "docs/21: 1/|δ| 寫 6098.87526911 (真值 6098.8752088...), dev 寫 4.4e-8 (真值 3.4e-8)",
        "docs/21 + scripts/20: 括號「1/8 = μ²/B² = γ_44/B²」有約定歧義 (88-環 γ_44 = 4 ⇒ 1/4)",
        "docs/22 T2: 「非 Abel 才簡併」措辭過強 — C_88 本身有二重簡併 (45 相異值/88 模態)",
        "scripts/20 check: 「δ 超越」check 係恆真 (True) — 空檢查",
        "scripts/21 check: 群論 check 對比硬編表自身 (循環驗證) — 需真算",
        "docs/01: 頂部狀態欄仍寫「🔴 未開始」(過時)",
        "docs/17: 狀態欄 + Verdict 表仍寫 ℓ_Nyq 🟡 (同 T4 更正矛盾)",
        "docs/19: 狀態欄仍寫「Abel 公設 🔴」(同 Verdict 表矛盾)",
    ],
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
with open(os.path.join(d, "22_audit_independent.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("\nEXIT=%d" % (0 if NF == 0 else 1))
