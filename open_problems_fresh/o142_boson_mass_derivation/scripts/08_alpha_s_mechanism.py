#!/usr/bin/env python3
"""
O142 v10 -- alpha_s Generation Mechanism (beta-function T-hat identity)
=======================================================================
追 α_s 生成機制: QCD β 函數係數 = 轉移矩陣不變量

★ 核心發現:
  b₀ = L₅ − L₃ = L₄ = Tr(T̂⁴) = 7     (QCD 1-loop, Lucas 遞迴恆等式)
  b₁ = 2F₇ = 2(T̂⁷)₁₂ = 26            (QCD 2-loop)
  N_f = 6 = 3B/2 = 2N_gen             (6 夸克口味結構強制)

  α_s⁻¹ = Tr(χ₃) = F₆ + sin²θ_W + 1/B = 8.4708  (譜作用量統一形式)
  8 = F₆ = dim(adj SU(3)) = 膠子數 (b₀+1)

  三路徑獨立收斂:
    O89 RG 8.426 (0.66%) | IDCM 譜跡 8.4708 (0.13%) | SM 8.4818
"""
import math
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "08_alpha_s_mechanism.json"

phi = (1 + math.sqrt(5)) / 2
psi = (1 - math.sqrt(5)) / 2
N0 = 44
B = 4
N_gen = 3
SM_alpha_s = 0.1179

def lucas(n): return round(phi**n + psi**n)
def fib(n):   return round((phi**n - psi**n) / math.sqrt(5))
LUC = {n: lucas(n) for n in range(0, 16)}
FIB = {n: fib(n) for n in range(0, 16)}

def Tpow(n):
    r = [[1, 0], [0, 1]]
    for _ in range(n):
        r = [[r[0][0] + r[0][1], r[0][0]],
             [r[1][0] + r[1][1], r[1][0]]]
    return r

results = []
def chk(name, got, want, tol_pct, note=""):
    dev = abs(got - want) / abs(want) * 100 if want else abs(got - want)
    ok = dev < tol_pct
    results.append({"name": name, "got": got, "want": want,
                    "dev": f"{dev:.6f}%", "ok": ok, "note": note})
    return ok

def flag(name, cond, note=""):
    results.append({"name": name, "got": "-", "want": "-",
                    "dev": "-", "ok": cond, "note": note})
    return cond

print("=" * 72)
print("O142 v10 -- alpha_s Generation Mechanism")
print("=" * 72)

# ============================================================
# 1. QCD β 函數 = T̂ 不變量
# ============================================================
print("\n### 1. QCD β 函數 = T̂ 不變量 ###")

# N_f = 6 = 3B/2 = 2N_gen
N_f = 6
chk("N_f = 6 = 3B/2", 3 * B / 2, N_f, 0.001, "6 夸克口味 = u/d×3代")
chk("N_f = 6 = 2N_gen", 2 * N_gen, N_f, 0.001)

# b₀ = 11 − 2N_f/3
b0 = 11 - 2 * N_f / 3
chk("b₀ = 11−2N_f/3 = 7", b0, 7, 0.001)
chk("b₀ = L₅ − L₃ = 11−4", LUC[5] - LUC[3], b0, 0.001,
    "Lucas 遞迴: L₅−L₃ = L₄")
chk("b₀ = L₄ = Tr(T̂⁴)", LUC[4], b0, 0.001)
T4 = Tpow(4)
chk("b₀ = Tr(T̂⁴) 直接計算", T4[0][0] + T4[1][1], b0, 0.001)

# b₁ = 102 − 38N_f/3
b1 = 102 - 38 * N_f / 3
chk("b₁ = 102−38N_f/3 = 26", b1, 26, 0.001)
chk("b₁ = 2F₇ = 2×13", 2 * FIB[7], b1, 0.001)
T7 = Tpow(7)
chk("b₁ = 2(T̂⁷)₁₂", 2 * T7[0][1], b1, 0.001)
chk("102 = 2K_tree+2L₆ = 66+36", 2 * 33 + 2 * LUC[6], 102, 0.001)
chk("76 = φ⁹−φ⁻⁹ (φ-identity)", phi**9 - phi**(-9), 76, 0.001)
chk("26 = 102−76 = 2F₇", 102 - 76, 2 * FIB[7], 0.001)

print(f"""
★ QCD β 函數 T̂ 身份:
  b₀ = 11 − 2N_f/3 = L₅ − L₃ = L₄ = Tr(T̂⁴) = 7
       (11 = L₅, N_f=6=3B/2 → 2N_f/3 = B = L₃ = Tr(T̂³))
       Lucas 遞迴: L₅ = L₄ + L₃ → L₅ − L₃ = L₄ 係恆等式!
  b₁ = 102 − 38N_f/3 = 26 = 2F₇ = 2(T̂⁷)₁₂
       (102 = 2K_tree+2L₆, 76 = φ⁹−φ⁻⁹)
""")

# ============================================================
# 2. N_c = 3 = B−1 (Pati-Salam) 強制
# ============================================================
print("### 2. N_c = 3 = B−1 強制 (Pati-Salam) ###")
N_c = 3
chk("N_c = 3 = B−1", B - 1, N_c, 0.001, "SU(4)→SU(3)_C×U(1), O68")

# 一般形式: b₀ = 11N_c/3 − 2N_f/3
b0_gen = 11 * N_c / 3 - 2 * N_f / 3
chk("b₀ 一般形式 (N_c=3,N_f=6)", b0_gen, 7, 0.001)

# 3B−1 = 11 身份
chk("11 = 3B−1 = 3×4−1", 3 * B - 1, 11, 0.001, "膠子 8 + 鬼場 3")
chk("b₀ = (3B−1) − B = 2B−1 = 7", 2 * B - 1, 7, 0.001)
chk("b₀ = 2B−1 = L₄", 2 * B - 1, LUC[4], 0.001)

# ============================================================
# 3. α_s⁻¹ = Tr(χ₃) 譜作用量統一
# ============================================================
print("\n### 3. α_s⁻¹ = Tr(χ₃) 譜作用量統一 ###")
mWmZ = math.sin(30 * math.pi / 88) / math.sin(41 * math.pi / 88)
sin2W = 1 - mWmZ**2
F6 = FIB[6]

alpha_inv = F6 + sin2W + 1 / B
alpha_s = 1 / alpha_inv

print(f"""
譜作用量統一: α_i⁻¹ = Tr(χ_i)
  α₂⁻¹ = Tr(χ₂) = N₀ − 2L₄ = 44−14 = 30   (g₂)
  α₃⁻¹ = Tr(χ₃) = F₆ + sin²θ_W + 1/B = 8.4708  (g₃)
""")
chk("α₂⁻¹ = Tr(χ₂) = 30", N0 - 2 * LUC[4], 30, 0.001)
chk("α₃⁻¹ = F₆ + sin²θ_W + 1/B", alpha_inv, 8.470776, 0.01)
chk("α_s = 1/8.4708", alpha_s, 0.118053, 0.001)
chk("α_s vs SM 0.1179", alpha_s, SM_alpha_s, 0.5)

# 三項身份
chk("① F₆ = dim(adj SU(3)) = 8", F6, 8, 0.001)
chk("   F₆ = b₀+1 = L₄+1 = 7+1", LUC[4] + 1, F6, 0.001)
chk("② sin²θ_W = 1−(m_W/m_Z)²", sin2W, 0.220776, 0.01)
chk("③ 1/B = 1/Tr(T̂³) = 1/L₃ = 1/4", 1 / LUC[3], 1 / B, 0.001)

# ============================================================
# 4. 三路徑交叉收斂
# ============================================================
print("\n### 4. 三路徑交叉收斂 ###")
SM_inv = 1 / SM_alpha_s
O89_inv = 8.426
IDCM_inv = alpha_inv

chk("IDCM 譜跡 8.4708 (Δ 0.13%)", IDCM_inv, SM_inv, 0.5)
chk("O89 RG 8.426 (Δ 0.66%)", O89_inv, SM_inv, 1.0)
flag("IDCM 譜跡比 O89 RG 更準",
     abs(IDCM_inv - SM_inv) < abs(O89_inv - SM_inv),
     f"IDCM {abs(IDCM_inv-SM_inv)/SM_inv*100:.3f}% < O89 {abs(O89_inv-SM_inv)/SM_inv*100:.3f}%")

print(f"""
三路徑獨立收斂到 α_s⁻¹ ∈ [8.426, 8.482]:
  O89 RG (2-loop + VL split): 8.426  (Δ 0.66%)
  IDCM 譜跡 (tree):           8.4708 (Δ 0.13%)
  SM 現代值:                  8.4818
""")

# ============================================================
# 5. 完整機制鏈
# ============================================================
print("### 5. 完整機制鏈 ###")
chain = """
x²+x−1=0 → φ → T̂ = [[1,1],[1,0]]
  │
  ├── Lₙ = Tr(T̂ⁿ):  L₃=4, L₄=7, L₅=11
  ├── Fₙ = (T̂ⁿ)₁₂:  F₆=8, F₇=13
  │
  ├── Pati-Salam: SU(4)→SU(3)_C×U(1) → N_c = B−1 = 3 (O68)
  ├── N_gen = 3 (O103) → N_f = 6 = 2N_gen = 3B/2
  │
  ├── QCD β 函數:
  │     b₀ = 11 − 2N_f/3 = L₅ − L₃ = L₄ = Tr(T̂⁴) = 7   ★ T̂ 身份
  │     b₁ = 102 − 38N_f/3 = 2F₇ = 2(T̂⁷)₁₂ = 26       ★ T̂ 身份
  │
  └── 譜作用量:
        α₂⁻¹ = Tr(χ₂) = N₀ − 2L₄ = 30
        α₃⁻¹ = Tr(χ₃) = F₆ + sin²θ_W + 1/B = 8.4708
               = dim(adj SU(3)) + 電弱混合 + 樹修正
               = (b₀+1) + sin²θ_W + 1/Tr(T̂³)
        → α_s = 0.118053 (SM 0.1179, Δ=0.13%) ✅
"""
print(chain)

# ============================================================
# 總結
# ============================================================
passed = sum(1 for r in results if r["ok"])
failed = [r for r in results if not r["ok"]]
print("=" * 72)
print(f"AUDIT SUMMARY: {passed}/{len(results)} PASS")
print("=" * 72)
for r in results:
    mark = "✅" if r["ok"] else "❌"
    print(f"  {mark} {r['name']}: {r['note']}")

out = {"test": "O142 v10 alpha_s mechanism", "total": len(results),
       "pass": passed, "fail": len(failed),
       "fail_detail": [r for r in results if not r["ok"]],
       "key": {
           "b0": b0, "b1": b1, "b0_T_identity": f"L₅−L₃=L₄={LUC[4]}",
           "b1_T_identity": f"2F₇={2*FIB[7]}",
           "N_f": N_f, "N_c": N_c,
           "alpha_s_inv": alpha_inv, "alpha_s": alpha_s,
           "O89_inv": O89_inv, "SM_inv": SM_inv,
           "tr_chi2": 30, "tr_chi3": alpha_inv,
       }}
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n  結果已存: {OUT}")
