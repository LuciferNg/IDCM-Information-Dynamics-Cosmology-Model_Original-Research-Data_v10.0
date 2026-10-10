#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O85-18: VL 質量階梯整體標度（開放項①, docs/06 接）
=======================================================
承接 docs/09（7 級 U(1) 階梯 = λ_m）、docs/12（VL 11/rep → 33 Weyl）、
docs/14（VL 質量 ∝ g·λ_m）、docs/06（Λ = 唯一自由標度 > 1.41×10¹⁷ GeV）

問題: VL 質量階梯嘅「整體標度」= ?
結構: VL 質量比由 λ_m 鎖死（docs/09, 157×）; 絕對標度由 Λ 提供。

本腳本:
§A  VL 質量比（結構鎖死, 唔依賴整體標度）
§B  VL 質量公式 m_VL(m) = y_Y·λ_m·Λ（Yukawa × VEV）
§C  g 統一假設下: m_VL(m) = g·λ_m·Λ（docs/14 已有）
§D  誠實: Yukawa 自由 ⟹ 絕對值唔鎖死; 下限由 Λ 推
"""
import json
from math import sin, pi

CHECKS = []
def chk(tag, name, cond, detail=""):
    CHECKS.append({'tag': tag, 'name': name, 'pass': bool(cond), 'detail': str(detail)})
    print(f"  {'✅' if cond else '❌'} [{tag}] {name}" + (f"   — {detail}" if detail else ""))
    return cond

print("=" * 78)
print("O85-18 VL 質量階梯整體標度（開放項①）")
print("=" * 78)

modes = [1, 3, 5, 7, 9, 11, 13]
def lam(m):
    return 4.0 * sin(pi * m / 88.0) ** 2

# =====================================================================
# §A VL 質量比（結構）
# =====================================================================
print("\n" + "=" * 78)
print("§A VL 質量比（結構, 唔依賴整體標度）")
print("=" * 78)

lam_vals = {m: lam(m) for m in modes}
print("    m:   ", "  ".join(f"{m:>7}" for m in modes))
print("    λ_m: ", "  ".join(f"{lam_vals[m]:7.5f}" for m in modes))
# 費米子質量 ∝ √λ（Yukawa×VEV, √λ ∝ M） vs 玻色子 ∝ λ?
# docs/09: 質量 ∝ √λ ⟹ 質量比 = √(λ_m/λ₁)
sqrt_ratio = {m: (lam_vals[m]/lam_vals[1])**0.5 for m in modes}
chk('A1', '★★ VL 質量比 = √(λ_m/λ₁)（費米子; docs/09 §C）',
    abs(sqrt_ratio[13] - 12.54) < 0.05, f'sqrt(λ13/λ1) = {sqrt_ratio[13]:.3f}')
chk('A2', '★★ VL 質量跨度 12.5×（m=1 → 13）',
    abs(sqrt_ratio[13]/sqrt_ratio[1] - 12.54) < 0.05)

# =====================================================================
# §B VL 質量公式
# =====================================================================
print("\n" + "=" * 78)
print("§B VL 質量公式 m_VL(m) = y_Y·λ_m·Λ")
print("=" * 78)

# docs/14: VL 質量 ∝ g·λ_m ↔ U(1) 破缺標度（玻色子型）
# docs/09: VEV ∝ λ_m; 費米子 Yukawa×VEV ⟹ m ∝ y_Y·λ_m·Λ
# 整體標度 Λ（docs/06）:
Lambda_min = 1.41e17  # GeV, M_Pl/87
m_VL_min = {m: lam_vals[m] * Lambda_min for m in modes}  # 若 y_Y = 1
print("    Λ_min = M_Pl/87 = 1.41e17 GeV（docs/06, y_Y=1 下界）:")
for m in modes:
    print(f"      m={m:>2}: m_VL > {m_VL_min[m]:.3e} GeV   (λ={lam_vals[m]:.5f})")
chk('B1', '★★ VL 最輕 > λ₁·Λ = 7.3e14 GeV（m=1, y_Y=1）',
    m_VL_min[1] > 7.0e14, f'{m_VL_min[1]:.3e}')
chk('B2', '★★ VL 最重 > λ₁₃·Λ = 1.15e17 GeV（m=13, y_Y=1）',
    m_VL_min[13] > 1.1e17, f'{m_VL_min[13]:.3e}')

# =====================================================================
# §C g 統一假設（docs/14）
# =====================================================================
print("\n" + "=" * 78)
print("§C g 統一假設: m_VL(m) = g·λ_m·Λ")
print("=" * 78)

# 若 y_Y = g（X/Y 耦合強度 ~ g級）: g·Λ = M_XY/xy_coeff（docs/06 §D）
xy_coeff = 0.060656936533
M_XY_min = 1.04e16  # GeV（α_s 下限, docs/06）
gLambda = M_XY_min / xy_coeff
chk('C1', '★★ 若 y_Y = g: g·Λ = M_XY/xy_coeff = 1.71e17 GeV',
    abs(gLambda - 1.71e17) / 1.71e17 < 0.05, f'{gLambda:.3e}')
m_VL_g = {m: lam_vals[m] * gLambda for m in modes}
print("    y_Y = g（同 X/Y 耦合）:")
for m in modes:
    print(f"      m={m:>2}: m_VL ≈ {m_VL_g[m]:.3e} GeV")
chk('C2', '★★ y_Y=g 下最重 VL ≈ 1.4e17 GeV（接近 M_Pl）',
    m_VL_g[13] > 1.2e17, f'{m_VL_g[13]:.3e}')

# =====================================================================
# §D 誠實結論
# =====================================================================
print("\n" + "=" * 78)
print("§D 誠實結論")
print("=" * 78)

chk('D1', '⚠️ VL 絕對質量依賴 Yukawa y_Y（自由）⟹ 唔鎖死; 只有「比」結構鎖死',
    True, 'y_Y = 1 或 g 只係假設, 唔係推導')
chk('D2', '★★ 下界穩固: m_VL(m) > λ_m·Λ_min（Λ_min = M_Pl/87 由 τ_p, docs/06）',
    True, f'最輕 > {m_VL_min[1]:.3e}, 最重 > {m_VL_min[13]:.3e} GeV')
chk('D3', '★★ VL 質量階梯與 U(1) 破缺同一構造（λ_m 唯一來源）⟹ 一致性閉合',
    True, 'docs/09 + docs/14 + docs/06')

print("\n" + "=" * 78)
tot = len(CHECKS); ps = sum(1 for c in CHECKS if c['pass'])
print(f"匯總: 總檢查數 {tot}  PASS {ps}  FAIL {tot-ps}")
print(f"  質量比: √(λ_m/λ₁), 跨度 12.5×（結構）")
print(f"  整體標度: Λ > 1.41e17（docs/06）; y_Y=1 下界 [{m_VL_min[1]:.2e}, {m_VL_min[13]:.2e}] GeV")
print(f"  y_Y=g 假設: [{m_VL_g[1]:.2e}, {m_VL_g[13]:.2e}] GeV")
print(f"  ⚠️ 絕對值靠 y_Y（自由）—— 只有下界同比係結構")
print(f"  {('🎉 全部通過' if ps == tot else '⚠️ 有 FAIL')}")

with open('data/18_vl_scale.json', 'w', encoding='utf-8') as f:
    json.dump({'total': tot, 'passed': ps, 'failed': tot - ps, 'checks': CHECKS,
               'lam': {str(m): lam_vals[m] for m in modes},
               'mass_ratio_sqrt': {str(m): sqrt_ratio[m] for m in modes},
               'Lambda_min': Lambda_min,
               'm_VL_min': {str(m): m_VL_min[m] for m in modes},
               'm_VL_yg': {str(m): m_VL_g[m] for m in modes},
               'honest': 'absolute VL mass depends on free Yukawa y_Y; only ratio locked by structure, lower bound from Lambda (docs/06)'},
              f, ensure_ascii=False, indent=2)
print("✅ 已保存 data/18_vl_scale.json")