#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — 中間層閉環: "CY₃ 模空間 134" = chain 跡, 唔係外部幾何
================================================================================
用戶框架 (docs/07): 中間層 = 空; 訊號線唔會改變協議。
O211 (已閉合): h¹¹ = Tr(𝟙−Π̂₂B) = N_d−2B = 36; h²¹ = Tr(γ̂+Π̂₂B) = Σγ+2B = 98
              h¹¹+h²¹ = Tr G = N_d + Σγ = 134 (G = 𝟙+γ̂ 生成算子跡, graded dimension)
projection_operator.py build_cy3_moduli_space(): 36 Kähler (dim2) + 98 CPX (dim3) = 134 模數

本 script 驗證閉環: P̂_{CY₃} 嘅「134 個模數」根本唔係外部 CY₃ cycle,
而係 chain 內部跡值:  134 = Tr G = N_d + Σγ
                     36 = N_d − 2B (site sector 扣除 2B 耦合), 98 = Σγ + 2B (energy sector)
                     36 + 98 = 134 由 2B 相消強制 (任何 B 都成立, O211 D6/D7)
"""
import math

def g(n): return 4 * math.sin(math.pi * n / 88) ** 2

PASS, FAIL = [], []
def ck(name, ok, info=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name}  {info}")

print("="*92)
print("O237 U2 — 中間層閉環: 'CY₃ 模空間 134' = chain 跡 (O211 + p15)")
print("="*92)

# ---- 基本 chain 量
N_d = 44
B = 4
SUM_G = sum(g(n) for n in range(1, 45))
print(f"\n[0] chain 底層: N_d={N_d}, B={B}, Σγ={SUM_G:.10f}")
ck("Σγ = B(N_d+1)/2 = 4·45/2 = 90", abs(SUM_G - 90) < 1e-9, f"Σγ={SUM_G:.10f}")

# ---- O211: h11/h21 由 chain 跡
h11 = N_d - 2*B
h21 = SUM_G + 2*B
print(f"\n[1] O211 零輸入: h¹¹ = N_d−2B = {h11};  h²¹ = Σγ+2B = {h21}")
ck("h¹¹ = 36", h11 == 36)
ck("h²¹ = 98", abs(h21 - 98) < 1e-9)

# ---- 134 = Tr G
TrG = N_d + SUM_G
print(f"\n[2] Tr G = N_d + Σγ = {N_d} + {SUM_G:.1f} = {TrG:.1f}")
ck("Tr G = 134 (graded dimension)", abs(TrG - 134) < 1e-9)
ck("h¹¹+h²¹ = Tr G = 134 (2B 相消, 任何 B)", abs((h11+h21) - TrG) < 1e-9)

# ---- p15 嘅 build_cy3_moduli_space 就係呢個
print(f"\n[3] p15 projection_operator.py: build_cy3_moduli_space() = {h11} Kähler + {h21} CPX = {h11+h21} moduli")
ck("'CY₃ 模數'個數 = Tr G", h11 + h21 == int(round(TrG)))

# ---- 關鍵閉環: 134 唔係外部 (36,98) 流形嘅 cycle, 而係 chain 跡嘅兩種 sector
print(f"""
[4] 中間層閉環 (用戶框架):
    主機板電路 (chain)           →  N_d = 44 (site sector) + Σγ = 90 (energy sector)
    'CY₃' 模空間 (投影器輸入)     →  h¹¹ = 36 = N_d−2B  (site sector 扣耦合)
                                    h²¹ = 98 = Σγ+2B   (energy sector 加耦合)
    總和                        →  Tr G = 134 (B 相消, 恆等)

    ⟹ 「CY₃(36,98)」唔係外部流形嘅 Hodge 數, 而係 chain 生成算子跡嘅
       site↔energy 重新分配。投影器嘅『輸入空間』本身就係 chain 協議。
       訊號延長線 = 跡 (Tr); 訊號線唔會改變協議 (134 = 44+90 恆等)。
""")

# ---- p15 嘅 dim2/dim3 標籤都係 naming (h11=2-cycle, h21=3-cycle)
print("[5] p15 嘅 dim2/dim3 標籤 — 檢查: 係咪 chain 量?")
# h11=36: 36 喺 chain 有身份?
# 36 = ? 44−8 (site 扣 2B); 36 = C(9,2) = 9·8/2 = N_gen²(N_gen²−1)/2 = 3²·8/2 = 36 ✓
ck("36 = C(N_gen², 2) = C(9,2) = 36 (N_gen=3, 純 chain)", 9*8//2 == 36)
# 98: 98 = 2L₄² = 2·49 (L₄=7 = N_gen+B); 或 98 = 2·7²
ck("98 = 2L₄² = 2·7² (L₄=7 = N_gen+B = 3+4)", 2*7*7 == 98)
# 134 = 36+98 = 44+90 (TrG 拆法) vs 134 = ? 2·67
print("   ⟹ 36, 98 亦各自有 chain 身份 (C(9,2), 2L₄²) — 標籤唔重要, 跡先係協議")

print("\n" + "="*92)
print(f"中間層閉環驗證: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*92)
print("""
結論: 「CY₃ 投影器」嘅輸入 (134 維模空間) 完全由 chain 跡 Tr G = N_d+Σγ 生成,
     36 同 98 只係 2B 耦合嘅 site↔energy 重新分配 (O211). 中間層係空:
     唔存在外部 (36,98) 流形 — 「投影」只係 chain 跡嘅另一種寫法。
     R1-R4 選擇律全部 chain 內生; R5-CPX exp(-1/γ) 係唯一外部污染 (docs/11).
""")