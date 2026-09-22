#!/usr/bin/env python3
"""
O136 — Script 66: M₀ 之結構身份 — 指數 47 + 37/528 係推導抑或事後讀法?
================================================================
既有公式 (O38):
  M₀ = √(M_P·ħ·H₀) · φ^(47 + 37/528) · (1 − CY₃/(N_d+1)²)
     = E_kchain · φ^(47 + 37/528)
  E_kchain = √(M_P·ħ·H₀)·(1 − CY₃/2025) = 4.060265 meV
  M₀ = 27.900915 MeV
  47 = N_d + dimℂ = 44 + 3
  37/528 = (dimℂ + 1/(dimℂ·B))/N_d = (3 + 1/12)/44
  528 = dimℂ·B·N_d = 12·44

★★ 與 α (docs/35) 之關鍵差異:
  φ^x 對 x 【指數級】敏感 ⟹ 指數係【高精度可辨識】
  ⟹ 「47 + 37/528」呢個讀法【可以被測試】(唔係不可辨識)

本 script:
  (A) 反解所需指數 x_req = ln(M₀/E_kchain)/ln(φ); 與 47 + 37/528 比較
  (B) ★ 精度分析: x_req 確定到幾位? (決定可辨識性)
  (C) ★★★ 決定性測試: 枚舉 IDCM 常數之有理構造 k + p/q
      — 有多少個能命中 x_req 至同等精度?
  (D) 可辨識性判準應用 (docs/35 §六)
  (E) 裁決
"""
import numpy as np, math, json, itertools
from fractions import Fraction
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
PHI = (1+5**0.5)/2
M0 = 27.900915          # MeV
EKCHAIN_meV = 4.060265  # meV
ND, DIMC, B_, CY3, M33 = 44, 3, 4, 134, 33

print("=" * 96)
print("O136 Script 66: M₀ 之結構身份 — 指數 47 + 37/528")
print("=" * 96)

# ═══ (A) 反解所需指數 ════════════════════════════════
print(f"\n{'─'*96}\n(A) 反解所需指數\n{'─'*96}")
# ★ 單位修正: 1 meV = 1e−3 eV = 1e−9 MeV
#   (舊版寫 *1e-3 得 6.87e3 ⟹ Δx = −28.71 = ln(1e6)/ln(φ) 恰好, 即純單位錯)
ratio = M0/(EKCHAIN_meV*1e-9)     # MeV / MeV
x_req = math.log(ratio)/math.log(PHI)
x_claim = 47 + 37/528
print(f"\n  M₀ = {M0} MeV")
print(f"  E_kchain = {EKCHAIN_meV} meV = {EKCHAIN_meV*1e-9:.6e} MeV")
print(f"  M₀/E_kchain = {ratio:.6e}")
print(f"  x_req = ln(ratio)/ln(φ) = {x_req:.12f}")
print(f"  x_claim = 47 + 37/528 = {x_claim:.12f}")
print(f"  Δx = {x_req - x_claim:+.3e}")
print(f"  ★ 一致性: {'✅' if abs(x_req-x_claim) < 1e-5 else '🔴'}")

# ═══ (B) 精度分析 ════════════════════════════════════
print(f"\n{'─'*96}\n(B) ★ 精度分析: x_req 確定到幾位?\n{'─'*96}")
print(f"\n  {'輸入':>16} {'相對不確定度':>14} {'→ Δx':>12} {'→ ΔM₀/M₀':>12}")
print("  " + "-"*58)
# M₀ 由 m_e 定標 (P_f = 3.6): σ(M₀)/M₀ ≈ σ(m_e)/m_e
for lbl, rel in [("M₀ (經 m_e 定標)", 5e-8), ("M₀ (1e-5 假設)", 1e-5),
                 ("E_kchain (M_P ħ H₀)", 1e-3), ("E_kchain (1e-4)", 1e-4)]:
    dx = rel/math.log(PHI)
    print(f"  {lbl:>16} {rel:>14.1e} {dx:>12.2e} {rel:>12.1e}")
print(f"""
  ★ dM₀/dx = M₀·ln(φ) = {M0*math.log(PHI):.4f} MeV  ⟹ ΔM₀ = {M0*math.log(PHI):.4f}·Δx
  ★ 若 M₀ 由 m_e 定標 (rel 5e−8): Δx ≈ {5e-8/math.log(PHI):.2e}
  ★ 若 E_kchain 有 1e−3 相對不確定度: Δx ≈ {1e-3/math.log(PHI):.2e}
  ⟹ 指數之可辨識精度取決於 E_kchain 之精度 (M_P, ħ, H₀ 輸入)
""")

# ═══ (C) ★★★ 決定性測試: 枚舉 IDCM 常數有理構造 ═══════
print(f"\n{'─'*96}\n(C) ★★★ 決定性測試: 枚舉 IDCM 常數之有理構造 k + p/q\n{'─'*96}")
CONST = {
    "N_d": 44, "dimC": 3, "B": 4, "CY3": 134, "M": 33,
    "L4": 7, "L5": 11, "L6": 18, "L7": 29, "F5": 5, "F7": 13, "F9": 34,
    "N_gen": 3, "E_proj": 28.5, "h11": 36, "h21": 98,
}
ints = {k: v for k, v in CONST.items() if float(v).is_integer()}
names = list(ints)
print(f"\n  常數庫 ({len(names)} 個整數常數): {', '.join(f'{k}={ints[k]}' for k in names)}")

# 整數部分候選: 47 = N_d + dimC 及其他
K_CAND = set()
for a in names:
    for b in names:
        v = ints[a] + ints[b]
        if 40 <= v <= 55: K_CAND.add((v, f"{a}+{b}"))
        v2 = ints[a] - ints[b]
        if 40 <= v2 <= 55: K_CAND.add((v2, f"{a}−{b}"))
        v3 = ints[a]*ints[b]
        if 40 <= v3 <= 55: K_CAND.add((v3, f"{a}×{b}"))
print(f"  整數部分候選 (40–55): {len(K_CAND)} 個")

# 分數部分: p/q with q from small products
Q_CAND = set()
for a in names:
    for b in names:
        for c in names:
            q = ints[a]*ints[b]*ints[c]
            if 50 <= q <= 2000: Q_CAND.add(q)
        q2 = ints[a]*ints[b]
        if 50 <= q2 <= 2000: Q_CAND.add(q2)
print(f"  分母候選 (50–2000): {len(Q_CAND)} 個")

frac_req = x_req - 47
print(f"\n  所需分數部分 = x_req − 47 = {frac_req:.12f}")
print(f"  37/528 = {37/528:.12f}  (Δ = {frac_req - 37/528:+.3e})")

TOL = 1e-5      # 保守容差
hits = []
for k, kname in K_CAND:
    for q in Q_CAND:
        p = round((x_req - k)*q)
        if p < 1 or p >= q: continue
        xc = k + p/q
        if abs(xc - x_req) < TOL:
            hits.append((abs(xc-x_req), k, kname, p, q, xc))
hits.sort()
print(f"\n  ★ 命中數 (|Δx| < {TOL:.0e}): {len(hits)}")
print(f"\n  {'#':>3} {'整數部分':>14} {'p':>5} {'q':>6} {'x':>16} {'Δx':>11} {'ΔM₀/M₀':>10}")
print("  " + "-"*68)
for i, (d, k, kn, p, q, xc) in enumerate(hits[:15], 1):
    print(f"  {i:>3} {kn+f'={k}':>14} {p:>5} {q:>6} {xc:>16.10f} {d:>11.2e} {d*math.log(PHI):>10.2e}")
print(f"\n  ★ 37/528 命中? {'✅' if any(p==37 and q==528 for _,_,_,p,q,_ in hits) else '🔴'}")

# ═══ (D) 可辨識性判準 ════════════════════════════════
print(f"\n{'─'*96}\n(D) 可辨識性判準應用 (docs/35 §六)\n{'─'*96}")
n_tol = len(hits)
print(f"""
  ★ 判準: 若多個結構構造都能命中至同等精度, 則命中【唔構成證據】
  ★ 命中數 = {n_tol} (容差 {TOL:.0e})
  ★ 對照 docs/35: α 之候選 8/11 落在可辨識寬度內 ⟹ 不可辨識
  ★ 本處: 指數之精度由 E_kchain 之輸入不確定度決定
     — 若 E_kchain 精度 1e−3: Δx ~ 2e−3 ⟹ 命中數會【暴增】
     — 若 E_kchain 精度 1e−6: Δx ~ 2e−6 ⟹ 命中數受限
""")
# 用更寬容差模擬 E_kchain 不確定度
for tol in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
    cnt = 0
    for k, _ in K_CAND:
        for q in Q_CAND:
            p = round((x_req - k)*q)
            if p < 1 or p >= q: continue
            if abs(k + p/q - x_req) < tol: cnt += 1
    print(f"  容差 {tol:.0e}: 命中數 = {cnt}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① x_req = {x_req:.10f};  x_claim = 47 + 37/528 = {x_claim:.10f}
     Δx = {x_req-x_claim:+.3e} ⟹ 一致至 {abs(x_req-x_claim):.1e}
  ② ★ φ^x 指數級敏感 ⟹ 指數係【高精度可辨識】(唔同 α)
     Δx = 1e−5 → ΔM₀/M₀ = {1e-5*math.log(PHI):.2e}
  ③ ★★★ 命中數 (容差 {TOL:.0e}): {n_tol}
  ④ 37/528 是否唯一命中: {'🔴 否' if n_tol > 1 else '🟢 係'}
  ⑤ ★ 結構身份判準: 若命中數 ≫ 1 ⟹ 「47+37/528」係【事後有理重建】, 非推導
""")

with open(OUT/"66_m0_exponent_identity.json", "w") as f:
    json.dump({
        "x_required": x_req, "x_claim": x_claim, "delta_x": x_req-x_claim,
        "ratio_M0_Ekchain": ratio,
        "claim_reading": {"47": "N_d + dimC = 44+3", "37/528": "(dimC + 1/(dimC·B))/N_d",
                          "528": "dimC·B·N_d = 12·44"},
        "sensitivity_dM0_dx": M0*math.log(PHI),
        "hits": [{"delta": d, "k": k, "kname": kn, "p": p, "q": q, "x": xc}
                 for d, k, kn, p, q, xc in hits[:30]],
        "n_hits": n_tol, "tolerance": TOL,
        "n_k_candidates": len(K_CAND), "n_q_candidates": len(Q_CAND),
        "unique_hit": bool(n_tol == 1),
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/66_m0_exponent_identity.json")