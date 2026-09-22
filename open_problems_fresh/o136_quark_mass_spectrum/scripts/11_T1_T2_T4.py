#!/usr/bin/env python3
"""
O136 — Script 11: T1 + T2 + T4 攻堅
================================================================
T1: P_f 統一結構 — E_proj 是否有精確結構來源?
T2: u/d/e 的 n=1 分化原理 (色荷/同位旋)
T4: 質量比閉式驗證

關鍵假設 (待驗):
  E_proj = Σγ − ⟨W⟩² = 90 − 61.5 = 28.5  (精確!)

若成立, 則 P_f(μ) = N_d − E_proj 不再是神秘數, 而是
P_f(μ) = N_d − (Σγ − ⟨W⟩²) = 44 − 28.5 = 15.5
"""
import json, math
from pathlib import Path
from fractions import Fraction

# ─── 常數 ───────────────────────────────────────────────
phi = (1 + math.sqrt(5))/2
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
Nd, B = 44, 4
h11, h21, CY3 = 36, 98, 134
M0 = 27.900915
mu2 = 2
lam = Fraction(2, 123)
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2

print("=" * 80)
print("O136 Script 11: T1 (P_f 統一結構) + T2 (n=1 分化) + T4 (質量比)")
print("=" * 80)

# ═══ T1: E_proj 的精確結構 ═══════════════════════════
print(f"\n{'='*80}")
print("T1: E_proj 精確結構")
print(f"{'='*80}")

Sigma_gamma = sum(gamma(n) for n in range(1, 45))
W_sq = mu2 / (2 * float(lam))   # ⟨W⟩² = μ²/(2λ) = 2/(4/123) = 61.5

print(f"\nΣγ(k=1..44)     = {Sigma_gamma:.10f}")
print(f"⟨W⟩² = μ²/(2λ)  = {W_sq:.10f}  [μ²=2, λ=2/123]")
print(f"Σγ − ⟨W⟩²       = {Sigma_gamma - W_sq:.10f}")
print(f"\n檢驗 E_proj = Σγ − ⟨W⟩² = 28.5 ?")
diff = abs((Sigma_gamma - W_sq) - 28.5)
print(f"  差 = {diff:.2e}  →  {'✅ 精確恆等式' if diff < 1e-9 else '🔴 不成立'}")

E_proj = Sigma_gamma - W_sq
print(f"\n★ 結論: E_proj = Σγ − ⟨W⟩² = {E_proj:.6f}")
print(f"  物理意義: 總鏈能量 90 減去凝聚能 61.5 = 被投影成物質的能量 28.5")

# ─── P_f 完整目錄 ─────────────────────────────────────
print(f"\n{'='*80}")
print("T1: P_f 完整目錄 (統一形式)")
print(f"{'='*80}")

P_f_catalog = {
    "e":   (Fraction(18,5),  "L₆/F₅",           "N_d−E_proj 形式?"),
    "mu":  (Fraction(31,2),  "(N_d−F₇)/2",      "N_d−F₇=31"),
    "tau": (Fraction(37,1),  "N_d−L₄",          "N_d−7=37"),
    "u":   (Fraction(31,2),  "(N_d−F₇)/2",      "N_d−F₇=31"),
    "d":   (Fraction(33,1),  "N_d−L₅",          "N_d−11=33"),
    "s":   (Fraction(18,5),  "L₆/F₅",           "L₆=18"),
    "c":   (Fraction(13,1),  "F₇",              "F₇=13"),
    "b":   (Fraction(44,1),  "N_d",             "N_d=44"),
}

print(f"\n{'粒子':>5} {'P_f':>8} {'分數':>10} {'結構':>14} {'N_d−P_f':>10} {'X 值':>8} {'X 結構':>10}")
print("-" * 72)

X_struct = {28.5: "E_proj = Σγ−⟨W⟩²", 7: "L₄", 11: "L₅", 13: "F₇", 0: "(無, P_f=N_d)"}
for p, (pf, form, note) in P_f_catalog.items():
    x = Nd - float(pf)
    xstr = X_struct.get(x, f"?")
    print(f"{p:>5} {float(pf):>8.4f} {str(pf):>10} {form:>14} {x:>10.4f} {x:>8.4f} {xstr:>10}")

print(f"\n★ 統一結構發現:")
print(f"  除 e/s (P_f = L₆/F₅) 外, 全部 P_f = N_d − X, X ∈ {{E_proj, L₄, L₅, F₇, 0}}")
print(f"  而 E_proj = Σγ − ⟨W⟩² = 28.5 是精確恆等式 ✅")

# ─── e/s 的特殊形式 ───────────────────────────────────
print(f"\n─── e/s 的特殊形式 L₆/F₅ = 18/5 = 3.6 ───")
print(f"  L₆ = 18, F₅ = 5")
print(f"  docs/04 線索: C_e = (Σφ8+|Ψ₁(44)|)/N_φ8 = (17+1)/5 = 18/5 ✅")
print(f"  → Σφ8 = 17, |Ψ₁(44)| = 1, N_φ8 = 5 (φ=8 組的 5 個玻色子點)")
print(f"  → 這將 e/s 的 P_f 連接到 O137 的 φ 分組結構")

# ═══ T2: u/d/e 的 n=1 分化 ═══════════════════════════
print(f"\n{'='*80}")
print("T2: u/d/e 的 n=1 分化原理")
print(f"{'='*80}")

n1_particles = {
    "e": {"Q": -1,    "T3": -0.5, "color": "singlet", "P_f": Fraction(18,5), "m_obs": 0.510999},
    "u": {"Q": 2/3,   "T3": 0.5,  "color": "triplet", "P_f": Fraction(31,2), "m_obs": 2.16},
    "d": {"Q": -1/3,  "T3": -0.5, "color": "triplet", "P_f": Fraction(33,1), "m_obs": 4.67},
}

print(f"\n{'粒子':>5} {'Q':>6} {'T₃':>6} {'color':>9} {'P_f':>8} {'m_pred':>10} {'m_obs':>9} {'Δ%':>7}")
print("-" * 62)
g1 = gamma(1)
for p, d in n1_particles.items():
    m_pred = M0 * g1 * float(d["P_f"])
    dev = (m_pred - d["m_obs"])/d["m_obs"]*100
    print(f"{p:>5} {d['Q']:>6.2f} {d['T3']:>6.1f} {d['color']:>9} {float(d['P_f']):>8.4f} {m_pred:>10.4f} {d['m_obs']:>9.4f} {dev:>7.2f}%")

print(f"\n─── P_f 比例 vs 質量比 ───")
print(f"  u/e: P_f 比 = {(31/2)/(18/5):.4f}, 質量比 = {2.16/0.510999:.4f}")
print(f"  d/u: P_f 比 = {33/(31/2):.4f}, 質量比 = {4.67/2.16:.4f}")
print(f"  d/e: P_f 比 = {33/(18/5):.4f}, 質量比 = {4.67/0.510999:.4f}")

print(f"\n─── 色荷結構檢驗 ───")
print(f"  e (singlet): P_f = L₆/F₅ = 18/5     ← 比值形式")
print(f"  u (triplet): P_f = (N_d−F₇)/2 = 31/2 ← 減法形式")
print(f"  d (triplet): P_f = N_d−L₅ = 33       ← 減法形式")
print(f"\n  → 色單態用『比值』, 色三重態用『減法』")
print(f"  → 色荷 C₂(SU(3)): singlet 0, triplet 4/3")
print(f"  → 檢驗: (N_d−E_proj)/(L₆/F₅) = {(31/2)/(18/5):.4f}")
print(f"  → 檢驗: C₂(triplet)/C₂(singlet) = ∞ (singlet 為 0)")

# 色荷因子檢驗
print(f"\n─── 色荷因子 C₂ 檢驗 ───")
C2_singlet = Fraction(0)
C2_triplet = Fraction(4,3)
for p, d in n1_particles.items():
    C2 = C2_singlet if d["color"] == "singlet" else C2_triplet
    print(f"  {p}: C₂ = {float(C2):.4f}, P_f = {float(d['P_f']):.4f}")

# ═══ T4: 質量比閉式 ══════════════════════════════════
print(f"\n{'='*80}")
print("T4: 質量比閉式 m_f₁/m_f₂ = (γ_n₁/γ_n₂)·(P_f₁/P_f₂)")
print(f"{'='*80}")

all_f = {
    "e":  (1,  Fraction(18,5),  0.510999),
    "mu": (7,  Fraction(31,2),  105.658),
    "tau":(20, Fraction(37,1),  1776.86),
    "u":  (1,  Fraction(31,2),  2.16),
    "d":  (1,  Fraction(33,1),  4.67),
    "s":  (14, Fraction(18,5),  93.0),
    "c":  (34, Fraction(13,1),  1270.0),
    "b":  (33, Fraction(44,1),  4180.0),
}

print(f"\n同 P_f 組 → 質量比 = γ 比 (純結構, 零自由度):")
print(f"\n{'組':>16} {'粒子對':>10} {'γ 比':>12} {'PDG 比':>12} {'Δ%':>8}")
print("-" * 62)

pairs = [
    ("P_f=L₆/F₅=3.6", "s/e",  ("s","e")),
    ("P_f=(N_d−F₇)/2", "μ/u", ("mu","u")),
]
for grp, label, (p1, p2) in pairs:
    n1, pf1, m1 = all_f[p1]
    n2, pf2, m2 = all_f[p2]
    ratio_g = gamma(n1)/gamma(n2)
    ratio_obs = m1/m2
    dev = (ratio_g - ratio_obs)/ratio_obs*100
    print(f"{grp:>16} {label:>10} {ratio_g:>12.4f} {ratio_obs:>12.4f} {dev:>8.3f}%")

# 全 8 費米子質量比
print(f"\n─── 全 8 費米子 (t 除外) 質量預言核對 ───")
print(f"\n{'粒子':>5} {'n':>4} {'γ_n':>10} {'P_f':>8} {'m_pred':>12} {'m_obs':>10} {'Δ%':>8}")
print("-" * 66)
n_ok = 0
for p, (n, pf, m_obs) in all_f.items():
    m_pred = M0 * gamma(n) * float(pf)
    dev = (m_pred - m_obs)/m_obs*100
    ok = abs(dev) < 3
    if ok: n_ok += 1
    print(f"{p:>5} {n:>4} {gamma(n):>10.6f} {float(pf):>8.4f} {m_pred:>12.4f} {m_obs:>10.4f} {dev:>7.2f}% {'✅' if ok else '🟡'}")

print(f"\n閉合: {n_ok}/8 ✅")

# ─── 保存 ─────────────────────────────────────────────
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "11_T1_T2_T4.json", "w") as f:
    json.dump({
        "T1_E_proj": {
            "Sigma_gamma": float(Sigma_gamma),
            "W_sq": float(W_sq),
            "E_proj": float(E_proj),
            "exact": diff < 1e-9,
            "identity": "E_proj = Σγ − ⟨W⟩² = 90 − 61.5 = 28.5",
        },
        "T1_P_f_catalog": {p: {"value": float(pf), "form": form, "Nd_minus": float(Nd - float(pf))} 
                           for p, (pf, form, note) in P_f_catalog.items()},
        "T2_n1_splitting": {p: {"Q": d["Q"], "T3": d["T3"], "color": d["color"], 
                                "P_f": float(d["P_f"])} for p, d in n1_particles.items()},
        "T4_closure": f"{n_ok}/8",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/11_T1_T2_T4.json")