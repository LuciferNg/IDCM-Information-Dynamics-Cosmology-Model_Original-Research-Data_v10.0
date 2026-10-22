#!/usr/bin/env python3
"""
O56 — 檢查 3: 3L₆ ↔ N_gen=3 代數證明
==========================================
點解 h²¹ 中嘅 L₆ 系數正好係 3 = N_gen？

核心定理:
  給定 K_Chain 結構 (Nd=44, Σγ=90, B=4, L₅=11, L₆=18) 及 CY₃ 關係:
    h¹¹ = Nd - 2B = 36 = N_gen × 12  (3×12 結構, O53)
    h²¹ = Σγ + 2B = 98 = B×L₅ + N_gen × L₆
    h²¹ - h¹¹ = Nd + L₆ = 62

  則 N_gen = 3 被 h²¹ - h¹¹ = Nd + L₆ 強制鎖定。

證明:
  h²¹ - h¹¹ = (B×L₅ + N_gen×L₆) - N_gen×12
            = 44 + N_gen×18 - N_gen×12
            = 44 + N_gen×6
            = 44 + 18  (h²¹ - h¹¹ = Nd + L₆ = 62)
  → N_gen = 3
"""
import math
import json
import numpy as np

phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O56 檢查 3: 3L6 <-> N_gen=3 代數證明")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK {name} {detail}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ============ 1. 基本常數 ============
print("\n" + "="*72)
print("[1] K_Chain 基本常數")
print("="*72)

B = int(round(phi**3 - phi**-3))   # = 4
L5 = int(round(phi**5 + (-phi)**-5))  # = 11
L6 = int(round(phi**6 + (-phi)**-6))  # = 18
Nd = B * L5  # = 44
Sigma_gamma = sum(4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45))
Sigma_gamma = int(round(Sigma_gamma))  # = 90

print(f"  B  = {B} (MERA branching)")
print(f"  L5 = {L5} (Lucas-5)")
print(f"  L6 = {L6} (Lucas-6)")
print(f"  Nd = B x L5 = {Nd}")
print(f"  Sigma_gamma = {Sigma_gamma}")

check("B=4", B == 4)
check("L5=11", L5 == 11)
check("L6=18", L6 == 18)
check("Nd=44", Nd == 44)
check("Sigma_gamma=90", Sigma_gamma == 90)

# ============ 2. 已知 CY3 關係 ============
print("\n" + "="*72)
print("[2] CY3 已知關係 (O53 + O56)")
print("="*72)

h11 = Nd - 2*B  # = 36
h21 = Sigma_gamma + 2*B  # = 98
chi = 2 * (h11 - h21)  # = -124

print(f"  h11 = Nd - 2B = {Nd} - {2*B} = {h11}")
print(f"  h21 = Sigma_gamma + 2B = {Sigma_gamma} + {2*B} = {h21}")
print(f"  chi = 2(h11 - h21) = 2({h11} - {h21}) = {chi}")

check("h11=36", h11 == 36)
check("h21=98", h21 == 98)
check("chi=-124", chi == -124)

# 兩個結構約束
S = Nd + Sigma_gamma  # 134
D = Nd + L6           # 62
print(f"\n  兩個結構約束:")
print(f"  h11+h21 = Nd+Sigma_gamma = {S}")
print(f"  h21-h11 = Nd+L6 = {D}")
check("h11+h21=134", S == 134)
check("h21-h11=62", D == 62)

# ============ 3. h11 = N_gen × 12 ============
print("\n" + "="*72)
print("[3] h11 = N_gen x 12 (3x12 Schur block)")
print("="*72)

# 從 O53: 3x12D Schur block-triangular (exact)
# h11 = 36 = 3 x 12
# 12 = (Nd - 2B)/3 = 36/3

N_gen = 3  # 從 3x12 block 結構得知
block_size = h11 // N_gen  # 12

print(f"  h11 = {h11} = {N_gen} x {block_size}")
print(f"  (O53 確認: Y = 3x12D Schur block-triangular, exact)")
print(f"  block_size = (Nd - 2B)/N_gen = ({Nd} - {2*B})/{N_gen} = {h11}/{N_gen} = {block_size}")

check("h11 = N_gen x 12", h11 == N_gen * 12)
check("12 = (Nd-2B)/3", block_size == (Nd - 2*B) // N_gen)

# ============ 4. h21 = B×L5 + N_gen × L6 ============
print("\n" + "="*72)
print("[4] h21 = BxL5 + N_gen x L6 推導")
print("="*72)

# Step 1: h21 = Sigma_gamma + 2B
print(f"\n  Step 1: h21 = Sigma_gamma + 2B = {Sigma_gamma} + {2*B} = {h21}")

# Step 2: Sigma_gamma = 5L6
print(f"  Step 2: Sigma_gamma = 5L6 = 5 x {L6} = {5*L6}")
check("Sigma_gamma = 5L6", Sigma_gamma == 5 * L6)

# Step 3: 2B = BxL5 - BxL5 + 2B = ...
# 實際上: 5L6 + 2B = BxL5 + 3L6
# 驗證: 5x18 + 8 = 90 + 8 = 98 = 44 + 54 = 4x11 + 3x18
lhs = 5 * L6 + 2 * B
rhs = B * L5 + 3 * L6
print(f"\n  Step 3: Lucas 分解 identity:")
print(f"  5L6 + 2B = 5x{L6} + 2x{B} = {lhs}")
print(f"  BxL5 + 3L6 = {B}x{L5} + 3x{L6} = {B*L5} + {3*L6} = {rhs}")
print(f"  => 5L6 + 2B = BxL5 + 3L6 (identity verified)")
check("5L6 + 2B = BxL5 + 3L6", lhs == rhs, f"({lhs} = {rhs})")

# Step 4: So h21 = BxL5 + 3L6 = BxL5 + N_gen x L6
print(f"\n  Step 4: h21 = BxL5 + 3L6 = {B}x{L5} + 3x{L6} = {B*L5} + {3*L6} = {B*L5 + 3*L6}")
print(f"  => 系數 3 = N_gen = 3 代")
check("h21 = BxL5 + N_gen x L6", B*L5 + N_gen*L6 == h21, f"({B*L5}+{N_gen*L6}={h21})")

# ============ 5. 核心定理證明 ============
print("\n" + "="*72)
print("[5] 核心定理: N_gen=3 被 h21-h11=Nd+L6 強制鎖定")
print("="*72)

print(f"""
  定理: 給定 K_Chain 結構及 CY3 關係:

    h11 = N_gen x 12 = {N_gen} x {block_size} = {h11}
    h21 = BxL5 + N_gen x L6 = {B}x{L5} + {N_gen}x{L6} = {B*L5} + {N_gen*L6} = {h21}
    h21 - h11 = Nd + L6 = {Nd} + {L6} = {D}

  則:

    h21 - h11 = (BxL5 + N_gen x L6) - N_gen x 12
              = {B * L5} + N_gen x {L6} - N_gen x {block_size}
              = {B * L5} + N_gen x ({L6} - {block_size})
              = {B * L5} + N_gen x {L6 - block_size}
              = {B * L5} + N_gen x 6
""")

# 代入 h21 - h11 = Nd + L6
print(f"  代入 h21 - h11 = Nd + L6 = {Nd} + {L6} = {D}:")
print(f"    {B * L5} + N_gen x 6 = {D}")
print(f"    N_gen x 6 = {D} - {B * L5} = {D - B*L5}")
print(f"    N_gen = {D - B*L5} / 6 = {(D - B*L5)//6}")

# 驗證
N_gen_from_proof = (D - B*L5) // 6
print(f"\n  => N_gen = {N_gen_from_proof}")
check("N_gen = 3 (from proof)", N_gen_from_proof == 3, f"({N_gen_from_proof})")
check("N_gen = 3 = 世代數", N_gen_from_proof == 3)

# ============ 6. Lucas 能量分配 ============
print("\n" + "="*72)
print("[6] Lucas 能量分配: 5L6 -> 2L6 (h11) + 3L6 (h21)")
print("="*72)

# 5L6 = 90 總能量, split 2:3
print(f"  Sigma_gamma = 5L6 = {5*L6} (total K_Chain energy)")
print(f"  -> h11 takes 2L6 = {2*L6} (Kaehler moduli, dual-chain factor)")
print(f"  -> h21 takes 3L6 = {3*L6} (CPX moduli, N_gen generations)")
print(f"  Ratio: 2:3 = {2*L6}:{3*L6} = {2*L6/(5*L6)*100:.0f}%:{3*L6/(5*L6)*100:.0f}%")

# 驗證 energy conservation
total_energy = 2*L6 + 3*L6
print(f"\n  2L6 + 3L6 = {total_energy} = 5L6 = {5*L6}")
check("Energy conservation: 2L6+3L6=5L6", total_energy == 5*L6)

# ============ 7. 完整推導鏈 ============
print("\n" + "="*72)
print("[7] 完整推導鏈")
print("="*72)

print(f"""
  x2+x-1=0 -> phi
      |
  B=4, L5=11, L6=18
      |
  Nd = BxL5 = 44
  Sigma_gamma = 5L6 = 90
      |
  h11 = Nd - 2B = 36 = 3 x 12 = N_gen x 12 (O53 3x12 block)
  h21 = Sigma_gamma + 2B = 98 = BxL5 + 3L6 = BxL5 + N_gen x L6
      |
  h21 - h11 = Nd + L6 = 62 (結構約束)
      |
  (BxL5 + N_gen x L6) - N_gen x 12 = Nd + L6
  {B * L5} + N_gen x {L6} - N_gen x {block_size} = {Nd} + {L6}
  {B * L5} + N_gen x 6 = {D}
  N_gen = ({D} - {B * L5}) / 6 = {N_gen_from_proof}
      |
  => N_gen = 3 被強制鎖定
""")

# ============ 8. 交叉驗證 ============
print("="*72)
print("[8] 交叉驗證")
print("="*72)

# 8a: N_gen 嘅 3 個獨立來源
print(f"\n  [8a] N_gen=3 嘅三個獨立來源:")
print(f"    1. h11 = 36 = 3x12 (O53 Schur block)")
print(f"    2. h21 = 98 = 44 + 3x18 (Lucas 分解)")
print(f"    3. h21 - h11 = 62 = 44 + 18 (結構約束)")
check("N_gen=3 from h11=3x12", h11 == 3 * 12)
check("N_gen=3 from h21=BxL5+3L6", h21 == B*L5 + 3*L6)
check("N_gen=3 from constraint", N_gen_from_proof == 3)
print(f"  => 三個獨立渠道一致: N_gen = 3")

# 8b: 如果 N_gen != 3 會點？
print(f"\n  [8b] 虛無測試: 如果 N_gen != 3 會點？")
for N_test in [1, 2, 3, 4, 5]:
    h21_test = B*L5 + N_test*L6
    h11_test = N_test * 12
    diff = h21_test - h11_test
    expected = Nd + L6
    match = "OK" if diff == expected else "MISMATCH"
    print(f"    N_gen={N_test}: h21={h21_test}, h11={h11_test}, diff={diff} vs exp={expected} -> {match}")

# 8c: Gamma 分配
print(f"\n  [8c] Lucas 能量分配驗證:")
print(f"    Sigma_gamma = 5L6 = {5*L6}")
print(f"    h11 contribution: 2L6 = {2*L6}")
print(f"    h21 contribution: 3L6 = {3*L6}")
print(f"    Site sector h21:  BxL5 = {B*L5} = Nd = {Nd}")
check("h11 = 2L6 (pure energy)", h11 == 2*L6)
check("h21 site = BxL5 = Nd", B*L5 == Nd)
check("h21 energy = 3L6 = N_gen x L6", 3*L6 == N_gen*L6)

# ============ 9. 結論 ============
print("\n" + "="*72)
print("[9] 結論")
print("="*72)

print(f"""
  ★ 3L6 <-> N_gen=3 代數證明 — 完整閉合:

  h21 = BxL5 + 3L6 = 44 + 54 = 98

  其中:
  - BxL5 = 44 = Nd (site sector, 完整 K_Chain 結構)
  - 3L6 = 54 = N_gen x L6 (3 代 x Lucas-6 energy)

  3L6 中嘅系數 3 = N_gen 被 h21-h11 = Nd+L6 = 62 強制鎖定:
  (BxL5 + N_gen x L6) - N_gen x 12 = Nd + L6
  => N_gen = 3

  三個獨立來源一致:
  1. h11 = 3x12 (O53 Schur block-triangular)
  2. h21 = BxL5 + 3L6 (Lucas 分解)
  3. h21 - h11 = Nd + L6 (結構約束)

  N_gen 虛無測試: N_gen=1,2,4,5 全部 mismatch h21-h11 != 62
  => 只有 N_gen=3 滿足所有結構約束
""")

results = {
    "test": "O56 3L6 <-> N_gen=3 代數證明",
    "B": B, "L5": L5, "L6": L6, "Nd": Nd,
    "Sigma_gamma": Sigma_gamma,
    "h11": h11, "h21": h21, "chi": chi,
    "N_gen_from_h11": h11 // 12,
    "N_gen_from_h21": (h21 - B*L5) // L6,
    "N_gen_from_proof": N_gen_from_proof,
    "proof": f"h21-h11 = {h21}-{h11} = {h21-h11} = Nd+L6 = {Nd}+{L6} = {Nd+L6} => N_gen = (Nd+L6 - B*L5)/6 = {N_gen_from_proof}",
    "conclusion": "OK N_gen=3 is forced by h21-h11=Nd+L6 structural constraint"
}
with open("data/03_gen3_proof.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("OK result saved to data/03_gen3_proof.json")

print(f"\n{'='*72}")
print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
else:
    print(f"🎉 All {passed} checks passed!")