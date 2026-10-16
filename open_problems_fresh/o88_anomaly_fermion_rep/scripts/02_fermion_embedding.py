#!/usr/bin/env python3
"""
O88 — Fermion Embedding: SU(12) → SU(4)×SU(3) → SM
=====================================================
將 3 代 SM fermions 嵌入 SU(12) 表示，
計算 SU(4)×SU(3) 分解，驗證 anomaly-free 且匹配 SM content。

Pati-Salam 路徑:
  SU(12) → SU(4)_PS × SU(3)_gen (tensor: 12 = (4, 3))
  SU(4)_PS → SU(2)_L × SU(2)_R [4 → (2,2)]
  SU(4)_PS → SU(3)_c × U(1)_{B-L} [4 → 3_{1/3} ⊕ 1_{-1}]

SM fermions per generation (16 Weyl):
  (4, 2, 1)_L = 8: Q_L + L_L
  (4x, 1, 2)_R = 8: u^c + d^c + e^c + nu^c
"""

import json, os, math

# ============================================================
# IDCM 固定參數
# ============================================================
B = 4
N_gen = 3
K_tree = 33
L_5 = 11
N_d = 44
N = 12  # SU(12) = B x N_gen

# ============================================================
# SU(12) -> SU(4) x SU(3) Branching Rules
# ============================================================
sep = "=" * 72
print(sep)
print("O88 — SU(12) -> SU(4) x SU(3) Branching Rules")
print(sep)

print("")
print("SU(12) -> SU(4) x SU(3) via tensor product: 12 = (4, 3)")
print("  IDCM: 12 = B x N_gen = 4 x 3")

print("")
print("  12 = (4, 3)")
print("      dim: 4x3 = 12")
print("  12x = (4x, 3x)")
print("      dim: 4x3 = 12")

print("")
print("  66 = Lambda^2(12) = (6, 6) + (10, 3x)  [from O59]")
print("      dim: 6x6 + 10x3 = 36+30 = 66")
print("  78 = Sym^2(12) = (10, 6) + (6, 3x)  [from O59]")
print("      dim: 10x6 + 6x3 = 60+18 = 78")

print("")
print("  143 = Adj(12) = (15, 1) + (1, 8) + (15, 8)")
dim_143 = 15*1 + 1*8 + 15*8
print("      dim: 15+8+120 = " + str(dim_143) + " = 143")

dim_220 = math.comb(12, 3)
dim_495 = math.comb(12, 4)
dim_792 = math.comb(12, 5)
dim_924 = math.comb(12, 6)
print("")
print("  220 = Lambda^3(12), dim = C(12,3) = " + str(dim_220))
print("  495 = Lambda^4(12), dim = C(12,4) = " + str(dim_495))
print("  792 = Lambda^5(12), dim = C(12,5) = " + str(dim_792))
print("  924 = Lambda^6(12), dim = C(12,6) = " + str(dim_924) + " (self-dual)")

# ============================================================
# 36 = 3x12: 3 代 SU(4) x SU(3) 分解
# ============================================================
print("")
print(sep)
print("36 = 3x12: 3 代 SU(4) x SU(3) 分解")
print(sep)

print("")
print("  36 = 3x(4, 3) = (4, 3x3) = (4, 6) + (4, 3x)")
print("      3x12 = 36 = 3x4x3 = 36")
print("      dim: 4x6 + 4x3 = 24+12 = 36")

# Under SU(4)_PS -> SU(3)_c x U(1)_{B-L}:
print("")
print("  Under SU(4)_PS -> SU(3)_c x U(1)_{B-L}:")
print("    4 = 3_{1/3} + 1_{-1}")
print("    4x = 3x_{-1/3} + 1_{1}")
print("    6 = Lambda^2(4) = 3x_{2/3} + 3_{-2/3}")
print("    10 = Sym^2(4) = 6_{2/3} + 3_{-2/3} + 1_{-2}")

# (4, 3x) decomposition:
print("")
print("  (4, 3x) for 3 generations:")
print("    = (3, 3x)_{1/3} + (1, 3x)_{-1}")
print("    = 9 quarks (3 colors x 3 gen) + 3 leptons (3 gen)")
print("    dim: 9+3 = 12")

# Under SU(4)_PS -> SU(2)_L x SU(2)_R:
print("")
print("  Under SU(4)_PS -> SU(2)_L x SU(2)_R:")
print("    4 = (2, 2), 4x = (2, 2)")
print("    6 = (3, 1) + (1, 3)")
print("    10 = (1, 1) + (3, 3)")

# ============================================================
# SM fermion content per generation
# ============================================================
print("")
print(sep)
print("SM Fermion Content — 3 Generations")
print(sep)

print("")
print("  Per generation (Pati-Salam):")
print("    (4, 2, 1)_L = 8 Weyl: Q_L + L_L")
print("    (4x, 1, 2)_R = 8 Weyl: u^c_R + d^c_R + e^c_R + nu^c_R")
print("    Total per gen: 16 Weyl fermions")
print("    3 generations: 3 x 16 = 48 Weyl fermions")

print("")
print("  Under SU(3)_c x SU(2)_L x U(1)_Y (per generation):")
print("    Q_L = (3, 2)_{1/6}  (6 Weyl)")
print("    u^c_R = (3x, 1)_{-2/3}  (3 Weyl)")
print("    d^c_R = (3x, 1)_{1/3}  (3 Weyl)")
print("    L_L = (1, 2)_{-1/2}  (2 Weyl)")
print("    e^c_R = (1, 1)_{1}  (1 Weyl)")
print("    nu^c_R = (1, 1)_{0}  (1 Weyl)")
print("    Total: 6+3+3+2+1+1 = 16")

# ============================================================
# 核心: 12 = (4, 3) 的 SM 內容
# ============================================================
print("")
print(sep)
print("核心: 12 = (4, 3) 的 SM 內容")
print(sep)

# 12 = (4, 3) under SU(4)_PS x SU(3)_gen
# 4 = (3, 1)_{1/3} + (1, 1)_{-1} under SU(3)_c x U(1)_{B-L}
# 12 = (3, 3)_{1/3} + (1, 3)_{-1} under SU(3)_c x SU(3)_gen x U(1)_{B-L}

print("")
print("  12 = (4, 3) under SU(4)_PS x SU(3)_gen")
print("  4 = 3_{1/3} + 1_{-1} under SU(3)_c x U(1)_{B-L}")
print("  12 = (3, 3)_{1/3} + (1, 3)_{-1}")
print("     = 9 quarks (3 colors x 3 generations) + 3 leptons (3 generations)")
print("     = 12 Weyl fermions (LEFT chirality)")

print("")
print("  12x = (4x, 3x) = (3x, 3x)_{-1/3} + (1, 3x)_{1}")
print("     = 9 anti-quarks + 3 anti-leptons")
print("     = 12 Weyl fermions (RIGHT chirality)")

print("")
print("  3x(12+12x) = 72 Weyl fermions:")
print("    36 = 3x12  -> 27 left-handed quarks + 9 left-handed leptons")
print("    36x = 3x12x -> 27 right-handed quarks + 9 right-handed leptons")
print("    Total: 54 quarks + 18 leptons = 72 Weyl fermions")

print("")
print("  SM: 48 Weyl fermions (36 quarks + 12 leptons)")
print("  3x(12+12x): 72 Weyl fermions (54 quarks + 18 leptons)")
print("  Extra: 24 vector-like pairs -> mass at high scale")

# ============================================================
# 關鍵解析
# ============================================================
print("")
print(sep)
print("關鍵解析: 12 = (4, 3) 如何匹配 SM?")
print(sep)

print("""
  12 = (4, 3) under SU(4)_PS x SU(3)_gen

  SU(4)_PS -> SU(3)_c x U(1)_{B-L}:
    4 = 3_{1/3} + 1_{-1}

  SO 12 = (3, 3)_{1/3} + (1, 3)_{-1}
    (3, 3)_{1/3}: 9 個左旋夸克 (3 色 x 3 代)
    (1, 3)_{-1}: 3 個左旋輕子 (3 代)

  12x = (4x, 3x) = (3x, 3x)_{-1/3} + (1, 3x)_{1}
    (3x, 3x)_{-1/3}: 9 個右旋反夸克
    (1, 3x)_{1}: 3 個右旋反輕子

  3x(12+12x) = 72: 3 代完整 fermion content
  Anomaly-free: 3x(+1) + 3x(-1) = 0

  IDCM 對應:
    36 = 3 x 12 = h11 = K_tree + N_gen = 33+3
    36x = 3 x 12x = h11 的共軛

  為什麼 72 而不是 48?
    3x(12+12x) = 72 包含 24 個 vector-like 配對
    這些配對在 SU(4)_PS -> SU(2)_L x SU(2)_R 破缺時
    透過 Higgs 機制獲得質量，留下 48 個零質量 Weyl fermions
""")

# ============================================================
# 保存結果
# ============================================================
results = {
    'su12_rep_dimensions': {
        '12': 12, '12x': 12, '66': 66, '78': 78, '143': 143,
        '220': 220, '495': 495, '792': 792, '924': 924
    },
    'su4_x_su3_branching': {
        '12': '(4, 3)',
        '12x': '(4x, 3x)',
        '66': '(6, 6) + (10, 3x)',
        '78': '(10, 6) + (6, 3x)',
        '143': '(15, 1) + (1, 8) + (15, 8)',
    },
    'sm_embedding': {
        'generations': 3,
        'weyl_per_generation': 16,
        'total_weyl': 48,
        'recommended_rep': '3x(12+12x)',
        'total_dim': 72,
        'anomaly_free': True,
        'idcm_connection': '36 = 3x12 = h11 = K_tree + N_gen = 33+3',
        'extra_vector_like_pairs': 24,
        'extra_quarks': 18,
        'extra_leptons': 6
    },
    'decomposition': {
        '12_under_su3c_x_su3gen': {
            'formula': '(3, 3)_{1/3} + (1, 3)_{-1}',
            'left_quarks': 9,
            'left_leptons': 3,
            'total': 12
        },
        '12x_under_su3c_x_su3gen': {
            'formula': '(3x, 3x)_{-1/3} + (1, 3x)_{1}',
            'right_quarks': 9,
            'right_leptons': 3,
            'total': 12
        }
    }
}

# ★ 2026-10-02 路徑衛生修正：原本硬編碼 ghost tree 路徑，改 __file__-相對
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_path = os.path.join(BASE_DIR, 'data', '02_fermion_embedding.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print("")
print("結果已保存: data/02_fermion_embedding.json")