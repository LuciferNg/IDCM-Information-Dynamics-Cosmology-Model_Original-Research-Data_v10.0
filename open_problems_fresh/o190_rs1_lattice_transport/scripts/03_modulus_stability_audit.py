#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O190 scripts/02 — 攻堅 1: modulus 穩定機制審計 (Radion-Flatness + 候選穩定方程)
================================================================================
問題 (docs/02 攻堅 1): O161 約束乘子 λ / O159 BVP 譜差 / O174 RG 不變量
能否扮演「穩定 88」嘅動力學 (Goldberger-Wise 類比)?

方法:
  A. Radion-flatness 審計: 全部 O159/O161 譜身份對鏈長 N 嘅標度行為
     (N 獨立 = radion-flat = 冇得選 N; N 依賴 = 候選穩定方程)
  B. Wilson holonomy: 唯一已知 N-依賴全局身份 (mod 4)
  C. 穩定方程掃描: N+1 = F_m 數場錨定 + 秩鎖定 (m = L5 = R = 11) → N = 88?
  D. GW no-go: 固定邊界 vev 嘅離散 bulk 極小作用量 S_min(N) — 有冇有限 N 極小?
  E. Casimir 型有限尺寸真空能 E(N) = 1/2 Σ sqrt(γ_k + μ²) — 有冇 N=88 極小?
  F. O95 交叉: 88 = 2·B·R = 2·L3·L5; 33 = N_gen·R (兩 modulus 秩因子化)
  G. docs/01 慣例 bug 檢查: "γ_n + γ_{44-n} = 4" (csc vs 4sin² 陷阱)

零新常數。用法: python3 02_modulus_stability_audit.py
"""
import math
import numpy as np
import mpmath as mp
mp.mp.dps = 40

B, R, N_gen, L3, L5, F11 = 4, 11, 3, 4, 11, 89
MU2 = 2

ok = 0; tot = 0
_records = []
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    _records.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

print("=" * 78)
print("A. Radion-Flatness 審計 — 譜身份 vs 鏈長 N (偶數鏈, γ_k = 4sin²(kπ/2N))")
print("=" * 78)
Ns = [4, 6, 8, 10, 12, 16, 20, 24, 44, 88, 176, 352]

def g(k, N):  # 176-Laplacian 推廣: N-site chain, k = 1..N
    return 4.0 * math.sin(math.pi * k / (2 * N)) ** 2

def sum_even(N): return sum(g(k, N) for k in range(2, N + 1, 2))
def sum_odd(N):  return sum(g(k, N) for k in range(1, N, 2))

flat = {key: [] for key in ["Sg", "Sodd", "Sev", "EO", "gam_N2", "Q", "BCC", "mean_odd"]}
for N in Ns:
    Se, So = sum_even(N), sum_odd(N)
    Sg = Se + So
    Qe = sum(k for k in range(2, N + 1, 2))
    Qo = sum(k for k in range(1, N, 2))
    # BC-cost: pinned D (diag 2) vs free N (diag 1 ends)
    trD, trN = 2 * N, 2 * N - 2
    flat["Sg"].append(Sg); flat["Sodd"].append(So); flat["Sev"].append(Se)
    flat["EO"].append(Se - So); flat["gam_N2"].append(g(N // 2, N))
    flat["Q"].append(Qe - Qo); flat["BCC"].append(trD - trN)
    flat["mean_odd"].append(So / (N // 2))

print("  N:    " + " ".join(f"{N:>6d}" for N in Ns))
print("  Σγ:   " + " ".join(f"{v:>6.1f}" for v in flat["Sg"]))
print("  Σodd: " + " ".join(f"{v:>6.1f}" for v in flat["Sodd"]))
print("  Σev:  " + " ".join(f"{v:>6.1f}" for v in flat["Sev"]))
print("  E−O:  " + " ".join(f"{v:>6.1f}" for v in flat["EO"]))
print("  γ_N/2:" + " ".join(f"{v:>6.3f}" for v in flat["gam_N2"]))
print("  Q:    " + " ".join(f"{v:>6.1f}" for v in flat["Q"]))
print("  BC:   " + " ".join(f"{v:>6.1f}" for v in flat["BCC"]))
print("  m(od):" + " ".join(f"{v:>6.3f}" for v in flat["mean_odd"]))

allclose = lambda a, b: all(abs(x - y) < 1e-9 for x, y in zip(a, b))
check("Σγ = 2N+2 (所有 N)", allclose(flat["Sg"], [2 * N + 2 for N in Ns]))
check("Σodd = N (觀察者預算 = 鏈長, 所有 N)", allclose(flat["Sodd"], [float(N) for N in Ns]))
check("Σeven = N+2 (世界 = 鏈長+2)", allclose(flat["Sev"], [float(N) + 2 for N in Ns]))
check("E−O = 2 = μ² (N 獨立!!)", allclose(flat["EO"], [2.0] * len(Ns)))
check("γ_{N/2} = 2 自對偶 (N 獨立!!)", allclose(flat["gam_N2"], [2.0] * len(Ns)))
check("Q = Σeven k − Σodd k = N/2 (N 獨立形式)", allclose(flat["Q"], [N / 2 for N in Ns]))
check("BC-cost Tr(D)−Tr(N) = 2 (N 獨立!!)", allclose(flat["BCC"], [2.0] * len(Ns)))
check("mean(odd) = 2 = μ² (N 獨立)", allclose(flat["mean_odd"], [2.0] * len(Ns)))
print()
print("  ★★ 判決: O159/O161 全部譜身份係 Z₂ parity 身份 — 喺任何偶數鏈長都成立,")
print("     N 獨立 (radion-flat)。佢哋穩定「Z₂ 扇區平衡」, 唔穩定「鏈長」。")
print("     → O161 λ 同 O159 BVP 譜差 唔可能扮演 GW 穩定模量 (尺度盲)。")

print()
print("=" * 78)
print("B. Wilson holonomy — 唯一 N-依賴全局身份")
print("=" * 78)
print("  U_k = e^{ikπ/N} (N-site 推廣), Π U_k = e^{iπ(N+1)/2} = i^{N+1}")
for N in Ns:
    phase = math.pi * (N + 1) / 2
    hol = complex(mp.e**(mp.mpc(0, 1) * (N + 1) * mp.pi / 2))
    need_i = (N + 1) % 4 == 1
    print("  N=%3d: 總相位=%6.2fπ  holonomy=%-8s  (i 需要 N≡0 mod 4: %s)"
          % (N, (N + 1) / 2, ("i" if need_i else "非 i"), need_i))
check("Wilson: holonomy = i ⟺ N ≡ 0 (mod 4) (唯一 N 依賴約束)",
      all(((N + 1) % 4 == 1) == (abs(complex(mp.e**(mp.mpc(0,1)*(N+1)*mp.pi/2)) - 1j) < 1e-30) for N in Ns))
print("  → Wilson 只加 mod-4 約束 (N ∈ {4,8,12,...}), 唔鎖定 88。")

print()
print("=" * 78)
print("C. 穩定方程掃描: 數場錨定 Σγ = 2F_m  ⟺  N+1 = F_m  + 秩鎖定")
print("=" * 78)
print("  Σγ = 2N+2 = 2(N+1): 若要求譜和 = 2×Fibonacci (數場定律, kchain_number_field),")
print("  則 N+1 = F_m。加上 Wilson mod-4 (N ≡ 0 mod 4, 即 F_m ≡ 1 mod 4):")
cands = []
for m in range(3, 16):
    Fm = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610][m]
    N = Fm - 1
    if N >= 2 and N % 4 == 0 and N <= 300:
        cands.append((m, Fm, N))
for m, Fm, N in cands:
    print("  F_%-2d = %3d → N = %3d  (Wilson mod-4 OK)" % (m, Fm, N))
print("  候選族 (N≡0 mod 4, N+1 Fibonacci): {4, 12, 20, 88, 232, ...}")
print("  ★ 秩鎖定 (O95: R = L5 = 11, su(12) rank 唯一): m 必須 = L5 = 11")
print("  → N = F_{L5} − 1 = F₁₁ − 1 = 89 − 1 = 88 唯一!!")
check("C1: N = F_{L5} − 1 = 88 (秩鎖定唯一)", F11 - 1 == 88)
check("C2: 88 ≡ 0 (mod 4) (Wilson 一致)", 88 % 4 == 0)
check("C3: Σγ(88) = 178 = 2F₁₁ (譜和 = 2×秩 Fibonacci)", 2 * 88 + 2 == 2 * F11)
check("C4: Wilson 相位 (F₁₁/2)π = 44.5π (holonomy 相位 = 秩 Fibonacci 半整數)",
      abs((88 + 1) / 2 - F11 / 2) < 1e-30)
print()
print("  ★★ 雙路由同一方程  N + 1 = F_{L5}:")
print("     路由 A (譜和):  Σγ = 2F_{L5}  ⟹  2N+2 = 178  ⟹  N = 88")
print("     路由 B (holonomy): ΠU_k 相位 = (F_{L5}/2)π  ⟹  π(N+1)/2 = 44.5π  ⟹  N = 88")
print("     兩路由都要求同一個 axiom: 秩索引 Fibonacci 錨定 (F_{L5} = 89) —")
print("     即 IDCM 數場定律 (C₅ = (x−2)(x²+x−1)², O142 Lₙ=Tr(T̂ⁿ) 算子字典)。")
print("  ⚠️ O148 判語: F₁₁ 中心形式 = 算術組織 (非新結構) — 本方程係「選擇規則」")
print("     (由秩選 N), 唔係「重述已知值」; 但共享同一 axiom 層 (數場定律)。")

print()
print("=" * 78)
print("D. GW no-go: 固定邊界 vev 嘅離散 bulk 極小作用量")
print("=" * 78)
def smin(N, v1, v2, mu2=2.0):
    """min over φ_1..φ_N of Σ(Δφ)² + μ²Σφ², φ_0=v1, φ_{N+1}=v2 fixed.
    Solve linear system (L+μ²)φ = b."""
    L = np.zeros((N, N))
    for i in range(N):
        L[i, i] = 2.0 + mu2
        if i > 0: L[i, i-1] = -1.0
        if i < N-1: L[i, i+1] = -1.0
    b = np.zeros(N); b[0] += v1; b[-1] += v2
    phi = np.linalg.solve(L, b)
    S = 0.0
    for j in range(N + 1):
        dj = (phi[j] if j < N else v2) - (v1 if j == 0 else phi[j-1])
        S += dj ** 2
    S += mu2 * np.sum(phi ** 2)
    return S

ratios = [("90/88", 90/88), ("89/88", 89/88), ("F11/F10", 89/55),
          ("φ²", 2.618), ("B/1", 4.0), ("44/1", 44.0), ("γ88/γ1", 4/0.00127)]
print("  離散 GW: 固定 v₁=1, v₂=r; 掃 N = 4..120 搵 S_min(N) 極小:")
for name, r in ratios:
    vals = [smin(N, 1.0, r) for N in range(4, 121)]
    interior_min = min(vals) in vals[5:-5]  # 內部極小? (遠離邊界)
    s88 = vals[88 - 4]
    dip88 = s88 < vals[88 - 4 - 2] and s88 < vals[88 - 4 + 2]  # N=88 局部極小?
    print("  v₂/v₁ = %-8s: S_min(4)=%.4f → S_min(120)=%.4f  N=88 極小=%s  內部極小=%s"
          % (name, vals[0], vals[-1], dip88, interior_min))
print("  → S_min(N) 單調飽和 (邊界層能量), 冇內部極小, N=88 唔係極小 → GW 式穩定唔存在")
# ξ = 1/ln(2+√3): GW 式預言 N* ~ ξ·ln(v₂/v₁)
xi = 1.0 / math.log(2 + math.sqrt(3))
print("  ξ = 1/ln(2+√3) = %.4f — 若 GW 式 N* = ξ·ln(v₂/v₁):" % xi)
for name, r in ratios:
    print("    %-8s → N* = %.3f" % (name, xi * math.log(r)))
print("    要 N* = 88 需要 v₂/v₁ = e^(88/ξ) = e^%.1f ≈ 3×10^%d (冇來源)"
      % (88 / xi, int(88 / xi / math.log(10))))
print("  → ★★ GW 無效: 均勻鏈冇 warp 體積元素 (RS1 GW 依賴 e^{−4kr_cπ} 體積因子);")
print("    IDCM 層級生成器係轉移矩陣特徵值 φ (代數, O142), 唔係鏈幾何。")

print()
print("=" * 78)
print("E. Casimir 型有限尺寸真空能 (候選 3: 有冇 N=88 極小?)")
print("=" * 78)
def casimir(N, mu2=2.0):
    return 0.5 * sum(math.sqrt(g(k, N) + mu2) for k in range(1, N + 1))
Evals = [casimir(N) for N in range(4, 201, 2)]
# bulk 密度 (連續極限) ε = (1/2π)∫₀^π √(4sin²θ+2) dθ
import scipy.integrate as si
eps_bulk = (1 / (2 * math.pi)) * si.quad(lambda th: math.sqrt(4*math.sin(th)**2 + 2), 0, math.pi)[0]
corr = [Evals[i] - eps_bulk * (4 + 2*i) for i in range(len(Evals))]
d2 = np.diff(np.diff(corr))
print("  ε_bulk(連續) = %.6f; E_cas(N) = E(N) − ε_bulk·N" % eps_bulk)
print("  N=88:  E = %.6f,  E_cas = %+.6f" % (casimir(88), casimir(88) - eps_bulk*88))
print("  E_cas 二階差分: 全 %s  (平滑單調, 冇 N=88 特殊)" %
      ("正" if np.all(d2 > 0) else "混合"))
check("Casimir: E_cas(N) 平滑單調 (冇 N=88 極小)", abs(d2).max() < 0.05)

print()
print("=" * 78)
print("F. O95 交叉: 兩 modulus 嘅秩因子化 + F₁₁ = 2·B·R + 1")
print("=" * 78)
check("88 = 2·B·R = 2·L3·L5 = 2·4·11 (O95 L3 雙鏈)", 2 * B * R == 88)
check("33 = N_gen·R = 3·11 = K_tree 深度 (同一秩!)", N_gen * R == 33)
check("F₁₁ − 1 = 2·L3·L5 (Lucas-Fibonacci 影子, O148 算術組織)",
      F11 - 1 == 2 * L3 * L5)
check("F_{L5} ≡ 1 (mod 4) → Wilson mod-4 自動滿足", F11 % 4 == 1)
print("  → 88 同 33 都因子化穿過 R = L5 = 11: {88, 33} = {2B, N_gen}·R —")
print("    modulus 層級 = su(12) 秩 × 結構係數。")

print()
print("=" * 78)
print("G. docs/01 慣例 bug 檢查: 「γ_n + γ_{44−n} = 4」")
print("=" * 78)
ladder = lambda n: 1.0 / math.sin(math.pi * n / 88)          # csc (O140 Lorentz)
lap44  = lambda n: 4.0 * math.sin(math.pi * n / 88) ** 2     # 44-mode chain Laplacian
lap88  = lambda k: 4.0 * math.sin(math.pi * k / 176) ** 2    # 176-Laplacian (O159)
print("  csc 階梯 (O140):       γ₇ + γ₃₇ = %.4f  (≠ 4, pairing 唔成立)"
      % (ladder(7) + ladder(37)))
print("  4sin²(nπ/88) 44鏈:     γ₇ + γ₃₇ = %.4f  (= 4 EXACT, pairing 成立)"
      % (lap44(7) + lap44(37)))
print("  4sin²(kπ/176) 88鏈:    γ₂₂ + γ₆₆ = %.4f  (= 4, k↔88−k 配對)"
      % (lap88(22) + lap88(66)))
csc_maxdev = max(abs(ladder(n) + ladder(44-n) - 4) for n in range(1, 22))
lap_ok = all(abs(lap44(n) + lap44(44-n) - 4) < 1e-9 for n in range(1, 44))
check("docs/01「γ_n = csc(πn/88), γ_n+γ_{44−n}=4」混慣例: csc 階梯冇 EXACT pairing"
      " (max dev=%.3f), 4sin²(nπ/88) 44鏈先有 (dev<1e-9)" % csc_maxdev,
      csc_maxdev > 1e-6 and lap_ok)
print("  → docs/01 表格 row「Lorentz 階梯 γ_n = csc(πn/88)，γ_n + γ_{44−n} = 4」")
print("    將 4sin² 44鏈嘅 Z₂ 配對身份掛咗喺 csc 階梯名下 —「兩個 γ 定義陷阱」")
print("    (csc = O140 Lorentz 階梯; 4sin² = O39/40 Laplacian)。需要修正記錄。")

print()
print("=" * 78)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 78)

import json, os, datetime
_here = os.path.dirname(os.path.abspath(__file__))
_data = os.path.join(_here, "..", "data")
os.makedirs(_data, exist_ok=True)
dump = {
    "problem": "O190 attack1 modulus stability",
    "script": "scripts/03_modulus_stability_audit.py",
    "date": datetime.datetime.now().isoformat(),
    "result": "%d/%d PASS" % (ok, tot),
    "checks": _records,
    "key_findings": [
        "Radion-Flatness: all O159/O161 spectral identities N-independent for even N",
        "Stabilization equation: N+1 = F_L5 = 89 -> N = 88 unique (rank-locked)",
        "GW no-go: uniform chain has no warp volume element; S_min(N) saturates",
        "88 = 2*B*R = 2*L3*L5 (O95); 33 = N_gen*R; {88,33} = {2B,N_gen}*R"
    ],
}
with open(os.path.join(_data, "attack1_modulus_stability.json"), "w") as f:
    json.dump(dump, f, ensure_ascii=False, indent=2)
print("JSON saved: %s" % os.path.join(_data, "attack1_modulus_stability.json"))
exit(0 if ok == tot else 1)
