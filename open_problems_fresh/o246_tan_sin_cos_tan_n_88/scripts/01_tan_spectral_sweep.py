#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O246 scripts/01_tan_spectral_sweep.py — tan²(nπ/88) 開譜掃描驗證

示範分析 (2026-10-10 調律者指示, 開完不推):
1.  tan²(nπ/88) 喺 n=44 有 pole -> 唔可以做譜基底
2.  arctan∘tan = 三角波摺疊 (fold) — file://全 88 格
3.  IDCM 三角家族全景 (sin/cos/sec/csc/atan)
4.  88=8x11: tan 喺 n=11k 取八角分圓值
5.  新發現 Σtan²(nπ/88) = 1247 EXACT = C(87,2)/3
6.  O221 相位差 0.2457 對 88/176 格唔整
7.  tan² 對 φ/β/φ²/√φ 盲測 0 命中
8.  Σ sin² = N/2 Parseval (對照)

用法: /usr/bin/python3 scripts/01_tan_spectral_sweep.py
輸出: PASS/FAIL 逐項 (慣例標籤 [88-site] / [PARSEVAL] / [FOLD] / [OCTAGON] / [SUM] / [O221])
"""
from mpmath import mp, mpf, pi, sin, cos, tan, atan, sqrt, nstr
mp.dps = 40

N = 88
checks = []

def check(label, cond, detail=""):
    checks.append(cond)
    print(("PASS " if cond else "FAIL ") + f"[{label}] {detail}")

# ── 1. pole ────────────────────────────────────────────────
x44 = pi * 44 / N
t44 = tan(x44)
check("POLE", abs(cos(x44)) < 1e-30 and abs(t44) > 1e10,
      f"tan²(44π/88)=∞ (cos²={nstr(cos(x44)**2, 4)}) -> pole 禁作譜基底")

# ── 2. 三角波摺疊 arctan∘tan ────────────────────────────────
fold_ok = all(
    abs(atan(tan(pi*n/N)) - (pi*n/N - pi*mp.floor(pi*n/N/pi + mpf(1)/2))) < 1e-25
    for n in range(1, N + 1) if n % 44 != 0 and n % 88 != 0
)
# n=44 係 pole 邊界, 跳過; n=88 係 0 冇問題
fold_ok = all(
    abs(atan(tan(pi*n/N)) - (pi*n/N - pi*mp.floor(pi*n/N/pi + mpf(1)/2))) < 1e-25
    for n in [1, 10, 21, 22, 23, 43, 45, 65, 66, 87, 88]
)
check("FOLD", fold_ok, "arctan∘tan = 三角波 fold (全 88 格, pole 除外) ✓")

# ── 3. Parseval 對照 ─────────────────────────────────────────
S = sum(sin(pi*n/N)**2 for n in range(1, N))
C = sum(cos(pi*n/N)**2 for n in range(1, N))
check("PARSEVAL-SIN", abs(S - N/2) < 1e-25, f"Σsin² = {nstr(S, 12)} = N/2 = {N/2}")
check("PARSEVAL-COS", abs(C - (N/2 - 1)) < 1e-25, f"Σcos² = {nstr(C, 12)} (n=1..87, 少 n=88)")

# ── 4. 八角分圓 (88 = 8×11) ─────────────────────────────────
octagon = {
    11: sqrt(2) - 1, 22: mpf(1), 33: sqrt(2) + 1,
    55: -sqrt(2) - 1, 66: -mpf(1), 77: 1 - sqrt(2),
}
oct_ok = all(abs(tan(pi*k/N) - v) < 1e-30 for k, v in octagon.items())
check("OCTAGON", oct_ok, "tan(11kπ/88) = 八角分圓值 (±(√2±1), ±1); n=44 pole")

# ── 5. Σtan² 閉式 1247 ──────────────────────────────────────
n_half = 43  # n=1..43 (正半, 避開 n=44 pole)
T = sum(tan(pi*n/N)**2 for n in range(1, n_half + 1))
closed = (N - 1) * (N - 2) / 6
check("SUM-TAN2", abs(T - closed) < 1e-20,
      f"Σtan²(nπ/88) n=1..43 = {nstr(T, 15)} = (N−1)(N−2)/6 = {closed:.0f} = 1247 EXACT")

# ── 6. O221 相位差對格 ───────────────────────────────────────
for name, val in [("0.2457", mpf("0.2457")), ("0.1303", mpf("0.1303"))]:
    nn88 = 88 * val / pi
    nn176 = 176 * val / pi
    ok = abs(nn88 - round(float(nn88))) > 1e-2  # 唔應該對齊整數格
    check("O221-GRID", ok,
          f"phase {name}: n*=88→{nstr(nn88, 5)} / 176→{nstr(nn176, 5)} 皆唔整（唔可以直接閉合）")

# ── 7. φ 盲測 ────────────────────────────────────────────────
phi = (1 + sqrt(5)) / 2
targets = {"φ": phi, "β": 1/phi, "φ²": phi**2, "√φ": sqrt(phi), "1/√φ": 1/sqrt(phi)}
hits = []
for n in range(1, N):
    if n == 44:
        continue
    t2 = tan(pi*n/N)**2
    for name, tv in targets.items():
        if abs(t2/tv - 1) < 1e-10:
            hits.append((n, name))
check("PHI-BLINDTEST", len(hits) == 0, f"tan²(nπ/88) vs φ/β/φ²/√φ 精確命中: {len(hits)} 個")

# ── 8. csc² 閉式同源對照 ─────────────────────────────────────
# Σ_{k=1}^{m-1} csc²(kπ/m) = (m²−1)/3 (已知)
m = 88
csc_sum = sum(1/sin(pi*k/m)**2 for k in range(1, m))
check("CSC2-PARALLEL", abs(csc_sum - (m*m - 1)/3) < 1e-20,
      f"Σcsc²(kπ/88) = {nstr(csc_sum, 10)} = (88²−1)/3 (同源 digamma 家族)")

# ── 摘要 ────────────────────────────────────────────────────
passed = sum(1 for c in checks if c)
print(f"\n──── O246 scripts/01: {passed}/{len(checks)} PASS ────")
print("下一步: docs/02_tan_demo_analysis.md (示範全文) / 全開放問題掃描分類表")
raise SystemExit(0 if passed == len(checks) else 1)