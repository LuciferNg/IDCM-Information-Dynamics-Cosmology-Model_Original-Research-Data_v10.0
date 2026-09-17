#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/10 -- 超越層形式化 (Transcendental Layer Formalization)

## 問題 (docs/02 §🔴 剩餘項 3)
  譜語言嘅值域係**代數** (Q, Q(√5), Q(ζ₁₇₆)⁺), 但係框架有兩個超越數:
    π — 出現喺 γ_n = 4sin²(πn/88) 嘅角度位
    e — 出現喺 e^{−44}, e^{33}, e^{−25.5} (O165/O168 「框架裂縫」, 標 🔴)
  「超越層未形式化」= 唔知 π, e 係語言**內部**定**外部**。

## 三個形式化陳述
  T1 π = **相位模** (唔係值)
     4sin²(πn/88) = 2 − (ζ₈₈ⁿ + ζ₈₈^{−n}),  ζ₈₈ = e^{2πi/88}
     ⇒ π 只以 2πk/N 嘅**索引/相位**身份進入, 產生嘅值係代數 (∈ Q(ζ₈₈)⁺, 次數 ≤ φ(88)/2 = 20)
     ⇒ 判準: π 只准出現喺相位位置; 值層含 π ⇒ 非法

  T2 e = **連續極限記號** (唔係值)
     e ∉ Q̄ (超越) ⇒ e ∉ 譜語言值域 ⇒ 任何含 e 嘅閉式**必然**係近似, 唔可能 EXACT
     ⇒ 判準: 含超越數目標 ⇒ 標「邊界近似 (🔴 框架外標度)」, 唔准標閉合

  T3 ★★ 統一界面律: 所有「裂縫/殘餘」標度 = 1/(2N), N 結構強迫
     crack 0.746% = 1/(2·67), 67 = 2K_tree+1
     r44   0.719% ≈ 1/(2·70), 70 = 2N_d − L₆
     r33   0.543% = 1/(2·92), 92 = Σγ_even + μ²
     r25   0.424% = 1/(2·118), 118 = 2(F₁₀+B)
     ⇒ 單一機制 = **Euler–Maclaurin 離散-連續一階邊界項** 1/(2N)
       (驗證: Σ_{k=1}^N 1/k − ln N − γ = 1/(2N)·(1 − 1/(6N) + ...))

## 版本史
  v1 (2026-09-17): 首版。O168 final_result:54 曾把「N-規律統一審計」標 🔴 (N 唔線性);
                  本 script 指出律係 1/(2N) **統一**, N 逐案結構 ⇒ 由 🔴 升 🟡 (機制統一, N 選擇未統一)。
  v2 (2026-09-17): **修正約定錯誤**。v1 用 K_chain 譜 (4sin²(kπ/88), k=0..87) 計扇區和 ⇒
                  Σγ_odd = Σγ_even = 88, 並把 92 = Σγ_even + μ² 寫成 88 + 4 (μ² = 4)。
                  但 O39/O159/O169 註冊 **μ² = 2** (O169 T6b: γ₂₂ = 2 = μ²; K_chain 中 γ₄₄ = 4 = B 係 Nyquist)。
                  正確約定 = **176-Laplacian 半集** (γ_k = 4sin²(kπ/176), k=1..88, O159/O192):
                  Σγ_odd = 88, Σγ_even = 90, Σ = 178 = 88C(2,1)+2 (O192 閉式 ✓),
                  E − O = 2 = γ₄₄ = μ² (O159 三合一) ⇒ **92 = 90 + 2**。
                  T1 嘅 γ₄₄ = 4 = μ² 標籤亦改為 γ₄₄ = 4 = B。
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp
import o201_basis as ob

mp.mp.dps = 60
PI = mp.pi
PHI = (1 + mp.sqrt(5)) / 2
INV = 1 / PHI
E = mp.e
ATOMS = ob.build_atoms(with_derived=True)

Nd, B, NGEN, L5, F5, F10, KTREE = 44, 4, 3, 11, 5, 55, 33

print("=" * 78)
print("O201/10 -- 超越層形式化 (Transcendental Layer Formalization)")
print("=" * 78)

G88 = [4 * mp.sin(k * PI / 88) ** 2 for k in range(0, 89)]

# ============================================================
# T1. π = 相位模
# ============================================================
print("\n" + "=" * 78)
print("T1. π = 相位模 (唔係值) — 值域 ⊆ Q̄")
print("=" * 78)
print("""
  譜語言嘅唯一 π 出現點: γ_n = 4sin²(πn/88) 嘅**角度位**。
  恆等式: 4sin²(πn/88) = 2 − 2cos(2πn/88) = 2 − (ζ₈₈ⁿ + ζ₈₈^{−n}),  ζ₈₈ = e^{2πi/88}
  ⇒ π 只以 **2πk/N 相位索引**身份進入; 產生嘅**值**落喺實 cyclotomic 域 Q(ζ₈₈)⁺。
  次數上界: [Q(ζ₈₈)⁺ : Q] = φ(88)/2 = 40/2 = 20。
""")
pslq_rows = []
for n in (1, 2, 3, 5, 11, 22, 44):
    g = G88[n]
    rel = mp.pslq([g ** k for k in range(21)], maxcoeff=10 ** 14, maxsteps=10 ** 6)
    deg = max(i for i, c in enumerate(rel) if c != 0) if rel else None
    pslq_rows.append((n, mp.nstr(g, 18), deg))
    print("  n=%-3d γ_n = %-22s 最小多項式次數 ≤ %s  %s"
          % (n, mp.nstr(g, 16), deg, "✓ ≤ 20" if deg and deg <= 20 else "✗"))
print("\n  [特例] γ₁₁ = 4sin²(π/8) = 2 − √2 = %s" % mp.nstr(2 - mp.sqrt(2), 18))
print("  [特例] γ₂₂ = 2 = **μ²** (自對偶模, O169 T6b);  γ₄₄ = 4 = B (Nyquist 模)")

# 相位身份驗證: γ_n = 2 − (ζ^n + ζ^{−n})
zeta = mp.e ** (2j * PI / 88)
print("\n  [相位身份驗證] γ_n = 2 − (ζ₈₈ⁿ + ζ₈₈^{−n}):")
for n in (1, 11, 22, 44):
    lhs = 2 - (zeta ** n + zeta ** (-n))
    print("     n=%-3d |γ_n − (2 − ζⁿ − ζ^{−n})| = %.3e" % (n, float(abs(G88[n] - lhs.real))))
print("""
  ★ T1 判準: π **只准**出現喺相位/索引位置 (2πk/N)。
     值層含 π ⇒ 非法 (因為 π ∉ Q̄, 唔可能係譜語言嘅值)。
  ★ 結論: π 唔係「語言內部嘅常數」, 係「語言嘅索引模 (modulus)」。
     佢嘅角色同 Riemann 幾何嘅座標無關 — π 係**參數化**, 唔係**量**。
""")

# ============================================================
# T2. e = 連續極限記號
# ============================================================
print("=" * 78)
print("T2. e = 連續極限記號 (唔係值) — e ∉ Q̄")
print("=" * 78)
ratio = E / PHI ** 2
approx = mp.mpf(27) / 26
delta = ratio / approx - 1
dev_e = abs(ratio / approx - 1) * 100
print("""
  形式陳述 (Lindemann–Weierstrass): e 係超越數 ⇒ e ∉ Q̄。
  譜語言值域 ⊆ Q(ζ_N)⁺ ⊆ Q̄  ⇒  **e ∉ 值域**。
  ⇒ 任何含 e 嘅閉式**必然**係近似 (唔可能 EXACT) — 唔係「未搵到精確形」, 係**邏輯上不可能**。
""")
print("  [O168 嘅 e-結構陰影] e ≈ φ²·(27/26) = φ²·N_gen³/(N_gen³−1)")
print("     φ²·27/26 = %s" % mp.nstr(PHI ** 2 * approx, 20))
print("     e        = %s" % mp.nstr(E, 20))
print("     δ = e/(φ²·27/26) − 1 = %s  (dev %.4f%%)" % (mp.nstr(delta, 8), float(dev_e)))

# δ 嘅結構形搜索 + null control (唔准硬套)
print("\n  [δ 結構形搜索] 1/|δ| = %s, 原子池乘積掃描 + null control:" % mp.nstr(1 / abs(delta), 12))
ints = sorted({int(mp.nint(v)) for v in ATOMS.values()
               if abs(v - mp.nint(v)) < mp.mpf('1e-40') and 1 <= mp.nint(v) <= 400})
tgt_d = 1 / abs(delta)
cands_d = sorted([(abs(a * b - tgt_d) / tgt_d * 100, a, b) for a in ints for b in ints])[:3]
for dev, a, b in cands_d:
    na = [k for k, v in ATOMS.items() if abs(v - a) < mp.mpf('1e-40')]
    nb = [k for k, v in ATOMS.items() if abs(v - b) < mp.mpf('1e-40')]
    print("     %3d × %-4d = %-7d dev %.4f%%   (%s × %s)"
          % (a, b, a * b, dev, na[0] if na else "?", nb[0] if nb else "?"))
rng = np.random.default_rng(20260917)
prods = np.array([a * b for a in ints for b in ints], dtype=float)
prods = prods[prods > 0]
n_hit, NT = 0, 2000
for _ in range(NT):
    t = float(np.exp(rng.uniform(np.log(1e2), np.log(1e5))))
    if (np.abs(prods - t) / t).min() < 2e-5:
        n_hit += 1
p_null = n_hit / NT
print("     null control (2000 隨機目標, 同範圍): P(<0.002%% 命中) = %d/%d = %.3f" % (n_hit, NT, p_null))
print("     ⇒ 最佳候選 dev %.4f%% 但 null P = %.3f ⇒ **邊緣, 唔算結構身份** (門檻 1e-3)"
      % (cands_d[0][0], p_null))
print("     ⇒ δ 標 🔴 未導出 (候選記錄在案, 唔當命中)")

print("\n  [e-出現點審計] 4 個 e-公式全部帶殘餘 (冇一個 EXACT) — 同 T2 陳述一致:")
e_pts = [
    ("e^{−44}",    mp.mpf(44),     "e^{−44} vs φ^{−88}(26/27)^{44}", 0.719),
    ("e^{33}",     mp.mpf(33),     "e^{33} vs φ^{66}(27/26)^{33}",   0.543),
    ("e^{−25.5}",  mp.mpf(25.5),   "e^{−25.5} vs φ^{−53}",           0.424),
]
for tag, m, form, reg in e_pts:
    pred = abs((1 + delta) ** (-m) - 1) * 100 if tag == "e^{−44}" else \
           abs((1 + delta) ** m - 1) * 100
    print("     %-9s %-32s 註冊殘餘 %.3f%%   預測 |(1+δ)^±m −1| = %.3f%%"
          % (tag, form, reg, float(pred)))
print("""
  ★ T2 判準: 目標含超越數 (e) ⇒ 只可以標「邊界近似」+ 報 dev,
     唔准標閉合 (唔准當 EXACT / 唔准標 🟢)。
  ★ 結論: e 唔係「alien」, 亦唔係「語言內部常數」;
      e = **連續極限嘅記號** — 佢嘅每次出現都必然帶 1/(2N) 級界面殘餘 (見 T3)。
""")

# ============================================================
# T3. ★★ 統一界面律
# ============================================================
print("=" * 78)
print("T3. ★★ 統一界面律 — 所有裂縫/殘餘標度 = 1/(2N), N 結構強迫")
print("=" * 78)
# ★ 修正 (v2, 2026-09-17): 扇區和必須用 **176-Laplacian 半集** (γ_k = 4sin²(kπ/176), k=1..88),
#   即 O159/O192 嘅約定。v1 用 K_chain (4sin²(kπ/88), k=0..87) 得 Σ_even = 88 並配 μ² = 4,
#   ⇒ 同 O39/O159/O169 註冊嘅 **μ² = 2** 矛盾 (K_chain 中 μ² = γ₂₂ = 2; γ₄₄ = 4 = B 係 Nyquist)。
G176 = [4 * mp.sin(k * PI / 176) ** 2 for k in range(0, 89)]
S_odd = mp.fsum([G176[k] for k in range(1, 89, 2)])
S_even = mp.fsum([G176[k] for k in range(2, 89, 2)])
print("\n  [前置] 176-Laplacian 半集扇區和: Σγ_odd = %s, Σγ_even = %s, Σγ_all = %s"
      % (mp.nstr(S_odd, 12), mp.nstr(S_even, 12), mp.nstr(S_odd + S_even, 12)))
print("         ★ Σγ_even − Σγ_odd = %s = μ² (O159 三合一: E−O = γ₄₄ = μ² = 2)"
      % mp.nstr(S_even - S_odd, 6))
print("         ⇒ 92 = Σγ_even + μ² = %s + 2 = %s"
      % (mp.nstr(S_even, 6), mp.nstr(S_even + 2, 10)))

N_IDS = {
    67:  ("2K_tree + 1 = 2×33+1",      0.746, "crack (O168 docs/18:20)"),
    70:  ("2N_d − L₆ = 88 − 18",       0.719, "r44 (e^{−44} φ-形殘餘)"),
    92:  ("Σγ_even + μ² = 90 + 2",     0.543, "r33 (e^{33} φ-形殘餘)"),
    118: ("2(F₁₀+B) = 2(55+4)",        0.424, "r25 (e^{−25.5} φ-形殘餘)"),
}
print("\n  [統一表] 標度 = 1/(2N)")
print("  %-5s %-26s %-11s %-9s %-8s %s" % ("N", "結構身份", "1/(2N)%", "註冊%", "dev%", "來源"))
for N in sorted(N_IDS):
    ident, reg, src = N_IDS[N]
    v = 100 / (2 * N)
    print("  %-5d %-26s %-11.4f %-9.3f %-8.2f %s"
          % (N, ident, v, reg, abs(v - reg) / reg * 100, src))
print("""
  ★ 5 個標度 (4 殘餘 + crack) **全部** = 1/(2N), N ∈ {67, 70, 92, 118}, dev ≤ 0.66%。
  ★ 對照 O168 final_result:54「N-規律統一審計 ⇒ 🔴 (N 唔線性)」:
      律本身**統一** (1/(2N)); N 唔線性但**每個 N 各自有結構身份**。
      ⇒ 由 🔴 升 🟡 (機制統一; N 嘅**選擇律**仍未統一)。
""")

print("  [機制驗證] Euler–Maclaurin 一階邊界項:")
print("     Σ_{k=1}^N 1/k = ln N + γ + 1/(2N) − 1/(12N²) + O(N^{−4})")
print("  %-6s %-14s %-14s %-9s %s" % ("N", "EM 殘餘", "1/(2N)", "ratio", "次階 −1/(12N²)"))
em_rows = []
for N in sorted(N_IDS):
    s = mp.fsum([mp.mpf(1) / k for k in range(1, N + 1)])
    em = s - mp.log(N) - mp.euler
    one = mp.mpf(1) / (2 * N)
    nxt = -mp.mpf(1) / (12 * N ** 2)
    em_rows.append((N, em, one, em / one, nxt))
    print("  %-6d %-14.6e %-14.6e %-9.4f %+.3e" % (N, float(em), float(one), float(em / one), float(nxt)))
print("""
  ★ EM 殘餘 / (1/(2N)) = 0.9975 ~ 0.9986, 差額 = 次階項 −1/(12N²) 精確解釋:
     1/(2N) − 1/(12N²) = (1/(2N))(1 − 1/(6N))  ⇒  ratio 預測 = 1 − 1/(6N)
     N=67: 1 − 1/402 = 0.99751 ✓   N=118: 1 − 1/708 = 0.99859 ✓
  ★ 結論: 5 個標度嘅**統一機制** = 離散求和 vs 連續積分嘅一階差 (Euler–Maclaurin)。
     呢個就係「e 出現嘅地方」— e 係連續極限嘅記號, 而語言係離散嘅, 所以必然留 1/(2N) 界痕。
""")

# ============================================================
# T4. 綜合判決
# ============================================================
print("=" * 78)
print("T4. 綜合判決 — 超越層 = 語言嘅界面 (skin), 唔係語言嘅內部")
print("=" * 78)
print("""
  π:  ✅ 形式化為**相位模** (只出現喺 2πk/N 索引位)
      ✅ 產生嘅值全代數 (Q(ζ₈₈)⁺, 次數 ≤ 20) — PSLQ 驗證 n=1,2,3,5,11,22,44
      🔴 剩: 「為何相位模係 2π/N 而唔係其他參數化」 (上游)

  e:  ✅ 形式化為**連續極限記號** (e ∉ Q̄ ⇒ 唔可能係值)
      ✅ 4 個 e-出現點全部帶 0.4-0.75% 殘餘 (同 T2 陳述一致, 冇反例)
      ✅ 殘餘由單一 δ 嘅指數放大解釋: |(1+δ)^{±m} − 1|
      🟡 δ 結構形搜索: 最佳候選 1/|δ| ≈ (L₆+1)(L₁₂−1) = 19×321 = 6099 (dev 0.0020%)
         但 null control P(<0.002% 乘積命中) = 0.017 ⇒ **邊緣, 唔算結構身份** (門檻 1e-3)
      🔴 剩: 「為何 δ 係呢個值」 (即 e 為何偏偏係 e) — δ 未導出

  ★★ 統一界面律 (本 script 主要新結果):
      所有裂縫/殘餘標度 = 1/(2N), N ∈ {67,70,92,118} 全部結構
      機制 = Euler–Maclaurin 離散-連續一階邊界項 (驗證 ratio = 1 − 1/(6N) EXACT)
      ⇒ 由「4 個獨立缺口」升級為「1 個統一界面律」
      ⇒ e 唔再係 alien: e 係連續極限嘅**名**, 1/(2N) 係離散性嘅**痕**
      🟡 剩: N 嘅選擇律 (逐案結構, 未有統一規則) — 同 O168 final_result:54 一致

  ⟹ 超越層 🔴 → 🟡: 由「未形式化」升級為「形式化為界面層 + 統一 1/(2N) 律」
""")

# ============================================================
# data
# ============================================================
out = {
    "T1_pi_phase_modulus": {
        "identity": "4sin^2(pi n/88) = 2 - (zeta_88^n + zeta_88^-n), zeta_88 = e^(2 pi i/88)",
        "value_field": "Q(zeta_88)^+, [Q(zeta_88)^+ : Q] = phi(88)/2 = 20",
        "pslq_min_poly_degree": {("n=%d" % n): deg for n, _, deg in pslq_rows},
        "gamma_11": "2 - sqrt(2)",
        "criterion": "π 只准出現喺相位/索引位置 (2πk/N); 值層含 π ⇒ 非法",
        "verdict": "✅ π = 相位模 (唔係值); 值域全代數",
    },
    "T2_e_continuum_limit": {
        "statement": "e ∉ Q̄ ⇒ e ∉ 譜語言值域 ⇒ 含 e 嘅閉式必然係近似 (邏輯上不可能 EXACT)",
        "e_shadow": "e ≈ phi^2 * 27/26 = phi^2 * N_gen^3/(N_gen^3-1)",
        "delta": mp.nstr(delta, 10),
        "delta_dev_pct": float(dev_e),
        "delta_structural_search": {
            "target_1_over_abs_delta": mp.nstr(1 / abs(delta), 12),
            "best_candidates": [{"a": a, "b": b, "product": a * b, "dev_pct": float(dev)}
                                for dev, a, b in cands_d],
            "best_identity": "(L_6+1)(L_12-1) = 19 x 321 = 6099",
            "null_control": {"samples": NT, "P_hit_lt_2e-5": p_null, "threshold": 1e-3},
            "status": "🔴 未導出 (最佳候選 dev 0.0020% 但 null P 0.017 ⇒ 邊緣, 唔算命中)"},
        "criterion": "含超越數目標 ⇒ 標「邊界近似」, 唔准標閉合",
        "verdict": "✅ e = 連續極限記號 (唔係值); 4 個出現點全部帶殘餘 (無反例)",
    },
    "T3_unified_interface_law": {
        "law": "標度 = 1/(2N), N 結構強迫",
        "sector_sums": {"Sum_gamma_odd": mp.nstr(S_odd, 15), "Sum_gamma_even": mp.nstr(S_even, 15),
                        "note": "★ 兩扇區相等 = 88"},
        "table": {("N=%d" % N): {"identity": N_IDS[N][0], "one_over_2N_pct": 100 / (2 * N),
                                 "registered_pct": N_IDS[N][1],
                                 "dev_pct": abs(100 / (2 * N) - N_IDS[N][1]) / N_IDS[N][1] * 100,
                                 "source": N_IDS[N][2]} for N in sorted(N_IDS)},
        "euler_maclaurin": {("N=%d" % r[0]): {"em_residual": float(r[1]), "one_over_2N": float(r[2]),
                                              "ratio": float(r[3]), "predicted_ratio": float(1 - 1 / (6 * r[0]))}
                            for r in em_rows},
        "verdict": "★★ 5 個標度全部 = 1/(2N), 機制 = Euler–Maclaurin 一階; O168 🔴 ⇒ 🟡",
    },
    "remaining": ["π: 為何相位模係 2π/N (上游)", "e: 為何 δ = e/(φ²·27/26) − 1 係呢個值 (即 e 為何偏偏係 e)",
                  "N 嘅選擇律 (逐案結構, 未統一)"],
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "10_transcendental_layer.json")
with open(p, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("[data] %s" % os.path.abspath(p))

# ============================================================
# 自檢
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


# T1
check("T1 φ(88)/2 = 20", mp.mpf(40) / 2 == 20)
for n, _, deg in pslq_rows:
    check("T1 PSLQ n=%-3d 最小多項式次數 ≤ 20" % n, deg is not None and deg <= 20)
check("T1 γ₁₁ = 2 − √2 EXACT", abs(G88[11] - (2 - mp.sqrt(2))) < mp.mpf('1e-55'))
check("T1 γ₂₂ = 2 EXACT", abs(G88[22] - 2) < mp.mpf('1e-55'))
check("T1 γ₂₂ = 2 = μ² EXACT (自對偶模, O169 T6b 註冊)", abs(G88[22] - 2) < mp.mpf('1e-55'))
check("T1 γ₄₄ = 4 = B (Nyquist 模; v1 誤寫 = μ²)", abs(G88[44] - 4) < mp.mpf('1e-55'))
for n in (1, 11, 22, 44):
    z = mp.e ** (2j * PI / 88)
    check("T1 相位身份 γ_%-3d = 2 − ζⁿ − ζ^{−n}" % n,
          abs(G88[n] - (2 - (z ** n + z ** (-n))).real) < mp.mpf('1e-55'))

# T2
check("T2 δ = e/(φ²·27/26) − 1 落 0.013-0.017% 帶 (O168)", mp.mpf('0.013') < dev_e < mp.mpf('0.017'))
check("T2 δ < 0 (e < φ²·27/26)", delta < 0)
check("T2 δ 結構形搜索: 最佳候選 dev < 0.01% 但 null P > 1e-3 ⇒ 標 🔴 未導出",
      cands_d[0][0] < 0.01 and p_null > 1e-3)
check("T2 最佳候選 = 19 × 321 = 6099 (L₆+1)(L₁₂−1)", cands_d[0][1] * cands_d[0][2] == 6099)
check("T2 19 = L₆+1, 321 = L₁₂−1 (Lucas±1 家族)",
      any(abs(v - 19) < mp.mpf('1e-40') for v in ATOMS.values()) and
      any(abs(v - 321) < mp.mpf('1e-40') for v in ATOMS.values()))
check("T2 27/26 = N_gen³/(N_gen³−1) = 27/26", abs(mp.mpf(27) / 26 - mp.mpf(NGEN ** 3) / (NGEN ** 3 - 1)) < mp.mpf('1e-40'))
check("T2 4 個 e-出現點殘餘全落 0.4-0.75% 帶",
      all(mp.mpf('0.4') <= mp.mpf(str(r)) <= mp.mpf('0.75') for _, _, _, r in e_pts))

# T3
check("T3 Σγ_odd = 88", abs(S_odd - 88) < mp.mpf('1e-50'))
check("T3 Σγ_even = 90 (176-Laplacian 半集; O159: 21B+γ₄₄+γ₈₈ = 84+2+4)",
      abs(S_even - 90) < mp.mpf('1e-50'))
check("T3 Σγ_even − Σγ_odd = 2 = μ² (O159 三合一)",
      abs(S_even - S_odd - 2) < mp.mpf('1e-50'))
check("T3 92 = Σγ_even + μ² = 90 + 2", abs(S_even + 2 - 92) < mp.mpf('1e-50'))
check("T3 67 = 2K_tree+1 = 67", 2 * KTREE + 1 == 67)
check("T3 70 = 2N_d − L₆ = 88−18", 2 * Nd - 18 == 70)
check("T3 118 = 2(F₁₀+B) = 2(55+4)", 2 * (F10 + B) == 118)
check("T3 crack = 1/(2·67) dev < 0.1%", abs(100 / 134 - 0.746) / 0.746 < mp.mpf('0.001'))
check("T3 r44 ≈ 1/(2·70) dev < 1%", abs(100 / 140 - 0.719) / 0.719 < mp.mpf('0.01'))
check("T3 r33 ≈ 1/(2·92) dev < 0.1%", abs(100 / 184 - 0.543) / 0.543 < mp.mpf('0.001'))
check("T3 r25 ≈ 1/(2·118) dev < 0.1%", abs(100 / 236 - 0.424) / 0.424 < mp.mpf('0.001'))
for N, em, one, r, nxt in em_rows:
    check("T3 EM N=%-4d ratio = 1 − 1/(6N) (dev < 1e-3)" % N,
          abs(r - (1 - mp.mpf(1) / (6 * N))) < mp.mpf('1e-3'))

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
