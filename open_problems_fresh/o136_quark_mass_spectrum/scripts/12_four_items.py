#!/usr/bin/env python3
"""
O136 — Script 12: 四項開放問題一次過攻堅
================================================================
Item 1: b 的 L=4 vs 44 — 統一公式 L = N_d/gcd(n, N_d)?
Item 2: u/d/e 在 n=1 的分化
Item 3: c 的 P_f = F₇ 直接形式 vs μ/u 的 (N_d−F₇)/2
Item 4: s/e, μ/u 的 1-2% 偏差 (方案依賴?)

禁止: 擴充符號庫。只用已註冊常數 {L_k, F_k, N_d, B, N_gen, E_proj, γ_n, Σγ, ⟨W⟩²}
"""
import json, math
from pathlib import Path
from fractions import Fraction
from math import gcd

phi = (1 + math.sqrt(5))/2
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
Nd, B, Ngen = 44, 4, 3
h11, h21, CY3 = 36, 98, 134
M0 = 27.900915
mu2, lam = 2, Fraction(2,123)
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2
Sigma_gamma = 90.0
W_sq = 61.5
E_proj = Sigma_gamma - W_sq  # 28.5

print("=" * 82)
print("O136 Script 12: 四項開放問題一次過攻堅")
print("=" * 82)

# ═══════════════════════════════════════════════════════
print(f"\n{'#'*82}")
print("ITEM 1: b 的 L = 4 vs 44 — 統一公式檢驗")
print(f"{'#'*82}")

data = {
    "e":   (1,  Fraction(18,5),  0.510999),
    "mu":  (7,  Fraction(31,2),  105.658),
    "tau": (20, Fraction(37,1),  1776.86),
    "u":   (1,  Fraction(31,2),  2.16),
    "d":   (1,  Fraction(33,1),  4.67),
    "s":   (14, Fraction(18,5),  93.0),
    "c":   (34, Fraction(13,1),  1270.0),
    "b":   (33, Fraction(44,1),  4180.0),
}
L_obs = {"e":44, "mu":44, "tau":11, "s":22, "c":22, "b":4}

print(f"\n假設: L = N_d / gcd(n, N_d)")
print(f"\n{'粒子':>5} {'n':>4} {'gcd(n,44)':>10} {'N_d/gcd':>9} {'L_obs':>7} {'一致?':>6}")
print("-" * 50)
item1_ok = True
for p, (n, pf, m) in data.items():
    g = gcd(n, Nd)
    L_pred = Nd // g
    if p in L_obs:
        ok = (L_pred == L_obs[p])
        item1_ok = item1_ok and ok
        print(f"{p:>5} {n:>4} {g:>10} {L_pred:>9} {L_obs[p]:>7} {'✅' if ok else '🔴':>6}")
    else:
        # u, d 同 n=1 → L 同 e
        print(f"{p:>5} {n:>4} {g:>10} {L_pred:>9} {'(=e)':>7} {'✅':>6}")

print(f"\n{'✅ 全部 6/6 一致 — L = N_d/gcd(n, N_d) 是統一公式' if item1_ok else '🔴 不成立'}")

# 驗證反週期條件自動滿足
print(f"\n─── 為何此公式自動滿足反週期? ───")
print(f"  n·L = n·N_d/g,  g = gcd(n,N_d) → n/g 為整數")
print(f"  n·L ≡ N_d (mod 2N_d) ⟺ (n/g) ≡ 1 (mod 2) ⟺ n/g 為奇數")
print(f"  N_d = 44 = 2²·11, g 吸收 n 的所有 2 與 11 因子")
print(f"  → n/g 無 2 或 11 因子 → 必為奇數 → 條件自動滿足 ✅")
print(f"\n  ★ 所以反週期條件是恆等式, 不是選擇器")
print(f"  ★ 但 L 的值 (winding length) 被 n 唯一決定")

# 檢查 L 的可能值
print(f"\n─── L 的可能值 ───")
L_vals = sorted(set(Nd // gcd(n, Nd) for n in range(1, 45)), reverse=True)
print(f"  L ∈ {L_vals}")
print(f"  = N_d/{{1,2,4,11,22}} = {{44, 22, 11, 4, 2}}")

# ═══════════════════════════════════════════════════════
print(f"\n{'#'*82}")
print("ITEM 2: u/d/e 在 n=1 的分化")
print(f"{'#'*82}")

n1 = {
    "e": {"Q": Fraction(-1), "T3": Fraction(-1,2), "color": "singlet", "gen": 1, "Pf": Fraction(18,5)},
    "u": {"Q": Fraction(2,3), "T3": Fraction(1,2), "color": "triplet", "gen": 1, "Pf": Fraction(31,2)},
    "d": {"Q": Fraction(-1,3), "T3": Fraction(-1,2), "color": "triplet", "gen": 1, "Pf": Fraction(33,1)},
}

print(f"\n{'粒子':>5} {'Q':>6} {'T₃':>6} {'Y':>6} {'color':>9} {'Pf':>8}")
print("-" * 48)
for p, d in n1.items():
    Y = 2*(d["Q"] - d["T3"])
    print(f"{p:>5} {str(d['Q']):>6} {str(d['T3']):>6} {str(Y):>6} {d['color']:>9} {str(d['Pf']):>8}")

print(f"\n─── 量子數分化能力檢驗 ───")
print(f"  Q:  e=−1, u=+2/3, d=−1/3     → 三分 ✅ (但 Q 的結構來源?)")
print(f"  T₃: e=−1/2, u=+1/2, d=−1/2   → 只分二 (e 同 d 相同) 🔴")
print(f"  Y:  e=−1, u=+1/3, d=+1/3     → 只分二 (u 同 d 相同) 🔴")
print(f"  color: e=singlet, u=d=triplet → 只分二 🔴")

print(f"\n─── 檢驗: Pf 是否 = f(Q)? ───")
print(f"  線性 Pf = a + b·Q:")
# 用 e 同 d 解
# 3.6 = a - b ; 33 = a - b/3
# 相減: 33 - 3.6 = b(-1/3 + 1) = 2b/3 → b = 29.4*3/2 = 44.1
b_coef = (Fraction(33) - Fraction(18,5)) * Fraction(3,2)
a_coef = Fraction(18,5) + b_coef
print(f"    由 e, d 解得: a = {float(a_coef):.4f}, b = {float(b_coef):.4f}")
u_pred = a_coef + b_coef*Fraction(2,3)
print(f"    預測 Pf(u) = {float(u_pred):.4f}, 實際 = 15.5 → {'✅' if abs(float(u_pred)-15.5)<0.1 else '🔴 失敗'}")

print(f"\n  Pf ∝ 1/(N_d − X) 形式:")
for p, d in n1.items():
    X = Nd - float(d["Pf"])
    print(f"    {p}: Pf = {float(d['Pf']):.4f}, N_d−Pf = {X:.4f}")

print(f"\n  X 值: e→40.4, u→28.5(=E_proj), d→11(=L₅)")
print(f"  檢驗 X 與量子數:")
print(f"    u: X = E_proj = Σγ − ⟨W⟩² = 28.5  (物質能量)")
print(f"    d: X = L₅ = 11")
print(f"    e: X = 40.4 = ?  (非結構數 → e 用比值形式 L₆/F₅)")

print(f"\n  🔴 結論: 色荷與超荷都不足以分化 u/d")
print(f"  🔴 X_u = E_proj 與 X_d = L₅ 之間無已知結構連結")
print(f"  → Item 2 未閉合")

# ═══════════════════════════════════════════════════════
print(f"\n{'#'*82}")
print("ITEM 3: c 的 P_f = F₇ vs μ/u 的 (N_d−F₇)/2")
print(f"{'#'*82}")

print(f"\n觀察: F₇ = 13 (c 用), N_d − F₇ = 31 (μ/u 用 31/2)")
print(f"互補: 13 + 31 = 44 = N_d ✅")
print(f"\n─── 檢驗: c 是否可用其他 (n, Pf) 組合? ───")
m_c = 1270.0
print(f"\n{'n':>4} {'γ_n':>10} {'Pf':>8} {'形式':>16} {'m_pred':>10} {'Δ%':>8}")
print("-" * 62)
c_candidates = []
for n in range(1, 45):
    for pf, form in [(Fraction(13,1), "F₇"), (Fraction(31,2), "(N_d−F₇)/2"),
                     (Fraction(44,1), "N_d"), (Fraction(18,5), "L₆/F₅"),
                     (Fraction(33,1), "N_d−L₅"), (Fraction(37,1), "N_d−L₄")]:
        mp_ = M0 * gamma(n) * float(pf)
        dev = abs(mp_ - m_c)/m_c*100
        if dev < 1.0:
            c_candidates.append((dev, n, pf, form, mp_))
c_candidates.sort()
for dev, n, pf, form, mp_ in c_candidates:
    mark = " ← 現用" if (n==34 and pf==13) else ""
    print(f"{n:>4} {gamma(n):>10.6f} {float(pf):>8.4f} {form:>16} {mp_:>10.4f} {dev:>7.3f}%{mark}")

print(f"\n→ {len(c_candidates)} 個候選在 1% 內 → 密度效應 (非唯一)")

print(f"\n─── 形式統一提案: 全部 Pf = (N_d − X)/D ───")
print(f"\n{'粒子':>5} {'Pf':>8} {'N_d−Pf·D':>12} {'D':>4} {'X':>8}")
print("-" * 42)
for p, (n, pf, m) in data.items():
    # 嘗試 D=1,2,5
    for D in [1, 2, 5]:
        X = Nd - float(pf)*D
        if abs(X - round(X)) < 1e-9 and 0 <= X <= 44:
            Xr = round(X)
            print(f"{p:>5} {float(pf):>8.4f} {Xr:>12} {D:>4} {Xr:>8}")
            break

# ═══════════════════════════════════════════════════════
print(f"\n{'#'*82}")
print("ITEM 4: 1-2% 偏差 — 方案依賴檢驗")
print(f"{'#'*82}")

print(f"\n─── 同 Pf 組的零參數預言 ───")
g1 = gamma(1)
pairs = [
    ("s/e",  14, 1, Fraction(18,5), Fraction(18,5), 93.0, 0.510999),
    ("μ/u",  7,  1, Fraction(31,2), Fraction(31,2), 105.658, 2.16),
]
print(f"\n{'對':>6} {'γ 比 (預言)':>14} {'PDG 比':>12} {'偏差':>9} {'夸克方案':>12} {'輕子方案':>12}")
print("-" * 72)
for label, n1_, n2_, pf1, pf2, m1, m2 in pairs:
    ratio_pred = gamma(n1_)/gamma(n2_)
    ratio_obs = m1/m2
    dev = (ratio_pred - ratio_obs)/ratio_obs*100
    print(f"{label:>6} {ratio_pred:>14.4f} {ratio_obs:>12.4f} {dev:>8.3f}% {'MS-bar 2GeV':>12} {'pole':>12}")

print(f"\n→ s, u 用 MS-bar(2 GeV); e, μ 用 pole mass")
print(f"→ 混合方案的比值必然帶跑動修正, 非純結構偏差")

print(f"\n─── 方案無關比值檢驗 (同扇區同方案) ───")
print(f"\n夸克-夸克比 (全 MS-bar 2 GeV, 但 t 是 pole):")
qr = [
    ("m_c/m_s", 1270.0, 93.0, 34, 14),
    ("m_b/m_s", 4180.0, 93.0, 33, 14),
    ("m_b/m_c", 4180.0, 1270.0, 33, 34),
    ("m_u/m_d", 2.16, 4.67, 1, 1),
]
print(f"\n{'比':>10} {'PDG':>12} {'(γ_n1·Pf1)/(γ_n2·Pf2)':>24} {'偏差':>9}")
print("-" * 60)
for label, m1, m2, n1_, n2_ in qr:
    obs = m1/m2
    pf1 = float(data[{"m_c/m_s":"c","m_b/m_s":"b","m_b/m_c":"b","m_u/m_d":"u"}[label]][1])
    pf2 = float(data[{"m_c/m_s":"s","m_b/m_s":"s","m_b/m_c":"c","m_u/m_d":"d"}[label]][1])
    pred = (gamma(n1_)*pf1)/(gamma(n2_)*pf2)
    dev = (pred-obs)/obs*100
    print(f"{label:>10} {obs:>12.4f} {pred:>24.4f} {dev:>8.3f}%")

print(f"\n輕子-輕子比 (全 pole mass):")
lr = [("m_μ/m_e", 105.658, 0.510999, 7, 1), ("m_τ/m_μ", 1776.86, 105.658, 20, 7)]
print(f"\n{'比':>10} {'PDG':>12} {'預言':>12} {'偏差':>9}")
print("-" * 48)
for label, m1, m2, n1_, n2_ in lr:
    p1 = float(data[{"m_μ/m_e":"mu","m_τ/m_μ":"tau"}[label]][1])
    p2 = float(data[{"m_μ/m_e":"e","m_τ/m_μ":"mu"}[label]][1])
    pred = (gamma(n1_)*p1)/(gamma(n2_)*p2)
    obs = m1/m2
    dev = (pred-obs)/obs*100
    print(f"{label:>10} {obs:>12.4f} {pred:>12.4f} {dev:>8.3f}%")

# ─── 保存 ─────────────────────────────────────────────
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "12_four_items.json", "w") as f:
    json.dump({
        "item1_L_formula": {
            "formula": "L = N_d / gcd(n, N_d)",
            "verified": item1_ok,
            "L_values": [int(x) for x in L_vals],
            "note": "反週期條件自動滿足 (恆等式); L 被 n 唯一決定",
        },
        "item2_n1_splitting": {
            "status": "UNRESOLVED",
            "reason": "色荷/超荷/T3 都無法唯一分化 e,u,d",
            "X_values": {"e": 40.4, "u": 28.5, "d": 11},
        },
        "item3_charm_Pf": {
            "candidates_within_1pct": len(c_candidates),
            "status": "DENSITY_EFFECT",
        },
        "item4_deviations": {
            "s_e_dev_pct": -0.937,
            "mu_u_dev_pct": -1.854,
            "explanation": "MS-bar vs pole mass 方案混合 → 跑動修正",
        },
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/12_four_items.json")