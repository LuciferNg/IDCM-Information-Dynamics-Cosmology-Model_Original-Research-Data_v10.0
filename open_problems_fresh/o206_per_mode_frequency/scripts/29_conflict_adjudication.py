#!/usr/bin/env python3
"""
O206 — 第十輪 scripts/29: C_f 衝突裁決（Conflict Adjudication）
================================================================
承接: O221 併入 O206（2026-09-25）+ O120 closeout handoff（2026-10-06）

裁決目標（O221 首要任務）: O64 vs O206-CSSG-v3 vs O137 R19 三方 C_f 衝突，
必須有明確結論，唔可以並存。

判準優先序（不可被數值覆蓋）:
  A. 模式合法性定理（O137 docs/35 + O120 closeout 重證）:
     合法模式集 = {1,2,3,4,5,7,9,11,13}（兩條獨立判準一致）
  B. 若 assignment 用非法模式 ⟹ 該 assignment 之 C_f 數值閉合【唔可作結構證據】
  C. t 夸克: M₀γₙC_f 天花板 = M₀γ₁₃·Φ_max = 1431 MeV ≪ 172690 MeV ⟹ VEV 機制（R19）
  D. C_f 目錄成員: Φ 目錄 18 值 {1,2,4,5,7,8,10,16,21,28,31,36,37,55,64}
     （Φ_ij = 1 + x₃ᵢ·x₃'ⱼ, x₃∈{1,5,9}, x₃'∈{0,1,3,4,6,7}; 3×6 = 18 項）
"""
import math, json, os, sys

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  [{detail}]" if detail and not cond else ""))

M0 = 27.900915
gam = lambda n: 4 * math.sin(n * math.pi / 88)**2
PDG = {"e":0.51099895, "u":2.16, "d":4.67, "s":93.4, "mu":105.6583755,
       "c":1270.0, "tau":1776.86, "b":4180.0}
A5_N = {"e":1, "u":2, "d":3, "s":4, "mu":5, "c":7, "tau":9, "b":11}

# ── A. 合法性定理重證 ──────────────────────────────────────────────
print("=" * 78); print("A. 模式合法性（兩條獨立判準 → 同一集）"); print("=" * 78)
H_NZ = {6,10,12,15,16,18,20,21,22,24,25,26}
def protected(n):
    return all(j not in H_NZ for j in range(1, n+1) if j % 2 == n % 2)
P1 = [n for n in range(1, 45) if protected(n)]
P2 = sorted({n for n in range(1, 45) if (n % 2 == 1 and n < 15) or (n % 2 == 0 and n < 6)})
LEGAL = [1,2,3,4,5,7,9,11,13]
print(f"  判準① 全息保護   = {P1}")
print(f"  判準② O209 閾值  = {P2}")
check("兩判準逐元素一致且 = A₅ 集", P1 == P2 == LEGAL)

# ── B. 三方 assignment 合法性裁決 ───────────────────────────────────
print("\n" + "=" * 78); print("B. 三方 assignment 合法性裁決"); print("=" * 78)
cssg = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "d":(1,33),
        "s":(14,3.6), "c":(34,13), "b":(33,44), "t":(44,1554)}
o64  = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,3.6), "d":(2,3.6),
        "s":(5,15.5), "c":(18,15.5), "b":(16,37), "t":(44,37)}
def illegals(assign):
    return {f: n for f, (n, cf) in assign.items() if n not in LEGAL}
il_c, il_o = illegals(cssg), illegals(o64)
print(f"  CSSG-v3 (O206 docs/25): 非法模式 = {il_c}  ({len(il_c)}/9)")
print(f"  O64 (docs/03):           非法模式 = {il_o}  ({len(il_o)}/9)")
check("CSSG-v3 5/9 非法 (τ20,s14,c34,b33,t44)", len(il_c) == 5 and il_c == {"tau":20,"s":14,"c":34,"b":33,"t":44})
check("O64 4/9 非法 (τ20,c18,t44,b16)", len(il_o) == 4 and il_o == {"tau":20,"c":18,"t":44,"b":16})
# 模式共享
check("CSSG-v3 u/d 共享 n=1（P_f zombie 特徵）", cssg["u"][0] == cssg["d"][0] == 1)
check("O64 e/u 共享 n=1（+χSB 後驗修正）", o64["e"][0] == o64["u"][0] == 1)

# ── C. t 夸克 VEV 判定 ─────────────────────────────────────────────
print("\n" + "=" * 78); print("C. t 夸克: VEV 機制（R19 判定複驗）"); print("=" * 78)
m_t = 172690.0; v_sm = 246219.6
y_t = m_t * math.sqrt(2) / v_sm
ceiling_13 = M0 * gam(13) * 64   # Φ_max = 64, 最大合法模式 n = 13
print(f"  y_t = √2·m_t/v_SM = {y_t:.6f}")
print(f"  M₀γ₁₃·Φ_max = {ceiling_13:.1f} MeV  vs  m_t = {m_t:.0f} MeV")
check("y_t ≈ 1 (VEV 機制可行)", abs(y_t - 1.0) < 0.01)
check("天花板 ≪ m_t (γC_f 機制結構上不可能)", ceiling_13 < m_t / 100)

# ── D. C_f 目錄成員（A₅ 值 vs Φ 目錄）───────────────────────────────
print("\n" + "=" * 78); print("D. A₅ C_f 值 vs Φ=9 目錄（精確成員）"); print("=" * 78)
Phi = sorted({1 + x3*x3p for x3 in (1,5,9) for x3p in (0,1,3,4,6,7)})
print(f"  Φ 目錄 18 項去重 = {Phi}  (max = {max(Phi)})")
Cf = {f: PDG[f] / (M0 * gam(A5_N[f])) for f in PDG}
for f, n in A5_N.items():
    print(f"  {f:>4} n={n:>2}  C_f = {Cf[f]:>10.4f}   {'∈目錄' if any(abs(Cf[f]-v)<1e-9 for v in Phi) else '∉目錄'}")
n_in = sum(1 for f in PDG if any(abs(Cf[f]-v)<1e-9 for v in Phi))
check("A₅ 8 值 0/8 喺 Φ 目錄內（R19 否定成立且更強）", n_in == 0)
exceed = [f for f in PDG if Cf[f] > 64]
check(">64 之費米子 = {c, τ, b}（3/8；t 已歸 VEV 機制）", exceed == ["c", "tau", "b"])
span8 = max(Cf.values()) / min(Cf.values())
print(f"  ★ 重框: C_f 跨度（t 除外）= {span8:.2f}×（非 2149×）")
check("跨度重框 = 71.2× (C_b/C_e)", abs(span8 - 71.16) < 0.1)

# ── E. 4.969≈F₅ 與「41 缺位」裁決 ──────────────────────────────────
print("\n" + "=" * 78); print("E. 附帶裁決"); print("=" * 78)
check("7722.8/1554 = 4.969 爭議 moot: 1554 基於非法模式 n=44", 44 not in LEGAL)
check("「41 缺位」已現身: C_s = 41.32 ≈ N_d−L₂ = 41 (dev 0.78%, 弱)", abs(Cf["s"] - 41) / 41 < 0.008)
check("C_e ≈ L₆/F₅ = 18/5 (第一代錨, dev 0.164%)", abs((Cf["e"] - 3.6) / 3.6) < 0.002)

# ── 輸出裁決 JSON ──────────────────────────────────────────────────
verdict = {
    "legal_modes": LEGAL,
    "cssg3_illegal": il_c, "o64_illegal": il_o,
    "catalog": Phi, "cf_in_catalog": 0,
    "t_mechanism": "VEV (y_t=0.9919)",
    "span_8": span8, "exceed_64": exceed,
    "verdict": "O137 R19 勝出；CSSG-v3/O64 9/9 閉合降級為後驗池擬合（非法模式）",
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "29_conflict_adjudication.json"), "w") as f:
    json.dump({k: (v if isinstance(v, (int, float, str, list, dict, bool)) else str(v))
               for k, v in verdict.items()}, f, ensure_ascii=False, indent=1)
print("\n" + "=" * 78)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)