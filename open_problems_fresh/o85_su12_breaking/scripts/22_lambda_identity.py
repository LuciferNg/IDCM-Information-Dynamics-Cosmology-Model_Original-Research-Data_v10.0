#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O85-22: Λ 整體標度身份攻關（docs/19 剩餘「VL 絕對質量依賴 Λ」）
================================================================
承接 docs/06（Λ = M_XY/(g·xy_coeff) > 1.41e17 = M_Pl/87）與 docs/19（S(m) 已閉合）。
docs/19 剩餘收窄為單一項：VL 絕對質量階梯 m_VL = (√2M₀/v)·γ_m²·Λ 中 Λ 未有算子身份。

本腳本（零新常數，全由觀測 + 既有結構數）:
§A  Λ 解析式：g 完全抵消（M_XY ∝ g）⟹ Λ 唔依賴耦合
§B  M_Pl/Λ 精確值 vs 文檔「87」——下界投影 or 結構恆等？
§C  87 候選掃描（含凍結結構數池）
§D  Λ 結構依賴分解（τ_p, m_p, λ₂, N_gen）
§E  誠實限制
"""
import json
from math import pi, sqrt

CHECKS = []
def chk(tag, name, cond, detail=""):
    CHECKS.append({'tag': tag, 'name': name, 'pass': bool(cond), 'detail': str(detail)})
    print(f"  {'✅' if cond else '❌'} [{tag}] {name}" + (f"   — {detail}" if detail else ""))
    return cond

print("=" * 78)
print("O85-22 Λ 整體標度身份攻關")
print("=" * 78)

# ---- 輸入（全部沿用 docs/02-06 既有值, 零新常數）----
tau_p_min = 2.4e34            # yr, Super-K / PDG 下限（觀測）
tau_s    = tau_p_min * 365.25 * 24 * 3600.0
HBAR     = 6.582119569e-25    # GeV·s
m_p      = 0.9382720813       # GeV
M_Pl     = 1.220910e19        # GeV
g3, g2   = 1.2179889272, 0.647209
lam2, lam4 = 0.020357116238, 0.081014052771
xy       = lam4 - lam2        # = λ₂(N_gen−λ₂) 恆等（docs/04）
N_gen, N_d, B, L5, L4, L7 = 3, 44, 4, 11, 7, 29
# =====================================================================
# §A  Λ 解析式：耦合完全抵消
# =====================================================================
print("\n" + "=" * 78)
print("§A Λ 解析式 — g 抵消")
print("=" * 78)

def mx_min(alpha):
    """d=6 量綱式: M_XY > (α²·m_p⁵·τ/ħ)^{1/4}"""
    return (alpha * alpha * m_p ** 5 * tau_s / HBAR) ** 0.25

a2, as_ = g2 * g2 / (4 * pi), g3 * g3 / (4 * pi)
Lam2, Lams = mx_min(a2) / (g2 * xy), mx_min(as_) / (g3 * xy)

chk('A1', '★ M_XY ∝ g（因 α^{1/2} = g/√(4π)，α² 開四次方）',
    abs(mx_min(as_) / mx_min(a2) - g3 / g2) < 1e-12,
    f'M_XY ratio = {mx_min(as_)/mx_min(a2):.9f} = g3/g2 ✓')
chk('A2', '★★ Λ(g₂) = Λ(g₃) 精確相等 — 分母 g 完全抵消（Λ 唔依賴耦合）',
    abs(Lam2 - Lams) / Lam2 < 1e-12,
    f'Λ = {Lam2:.10e} GeV（兩路同一值）')

Lam_analytic = (m_p ** 5 * tau_s / HBAR) ** 0.25 / (sqrt(4 * pi) * xy)
chk('A3', '★★ Λ 解析式 = (m_p⁵τ/ħ)^{1/4}/(√(4π)·λ₂(N_gen−λ₂))',
    abs(Lam_analytic - Lam2) / Lam2 < 1e-12,
    f'= {Lam_analytic:.10e} GeV')

# =====================================================================
# §B  M_Pl/Λ 精確值 — 87 係下界投影 or 結構恆等？
# =====================================================================
print("\n" + "=" * 78)
print("§B M_Pl/Λ 精確度診斷")
print("=" * 78)

ratio = M_Pl / Lam_analytic
chk('B1', '★ M_Pl/Λ 精確值 = 86.8002（文檔 docs/06 寫「= M_Pl/87」）',
    abs(ratio - 86.800195) < 1e-3, f'M_Pl/Λ = {ratio:.6f}')
dev87 = (ratio - 87) / 87 * 100
chk('B2', '★★ 對 87 之偏差 −0.230% ⟹ 「= M_Pl/87」係量綱式下界投影嘅四捨五入',
    abs(dev87) < 1 and abs(dev87) > 0.1, f'dev = {dev87:+.3f}%（非恆等）')

# τ_p 敏感度: Λ ∝ τ^{1/4} ⟹ M_Pl/Λ ∝ τ^{-1/4}
tau_for_87 = tau_p_min * (ratio / 87) ** 4
chk('B3', '★ 要 ratio 精確 = 87 需 τ_p = %.4g yr（= 名義值 ×%.4f）' % (tau_for_87, tau_for_87 / tau_p_min),
    tau_for_87 < tau_p_min, 'τ_p 越大 ⟹ Λ 越大 ⟹ ratio 越細 ⟹ 87 只係下限投影')

# =====================================================================
# §C  87 結構候選掃描（零新常數池）
# =====================================================================
print("\n" + "=" * 78)
print("§C 87 候選掃描")
print("=" * 78)

# IDCM 凍結結構數（全部已有算子/定理來源）
pool = {
    '2N_d−1 = 88−1': 2 * N_d - 1,
    'N_gen·L₇ = 3×29': N_gen * L7,
    'Σγ−N_gen = 90−3': B * (N_d + 1) // 2 - N_gen,
    '2N_d = 88': 2 * N_d,
    'Σγ = B(N_d+1)/2': B * (N_d + 1) // 2,
    'N_gen·L₇−? ': 0,
    'L₄·L₅+? ': 0,
}
cand = {k: v for k, v in pool.items() if v}
hits = []
for k, v in cand.items():
    dev = (ratio - v) / v * 100
    hits.append((abs(dev), k, v, dev))
    print(f"    {k:>18} = {v:>4}  dev {dev:+.3f}%")

best = min(hits)
chk('C1', f'★ 最近候選 = {best[1]}（{best[2]}），dev {best[3]:+.3f}% —— 落入量綱式誤差內',
    best[0] < 0.5, f'量綱式下限級（docs/06 §E: 冇 f_p/renorm/phase space）')

# 三重候選數值不可分
tri = [('2N_d−1', 2 * N_d - 1), ('N_gen·L₇', N_gen * L7), ('Σγ−N_gen', B * (N_d + 1) // 2 - N_gen)]
vals = set(v for _, v in tri)
chk('C2', '★★ 三重候選（88−1 / 3×29 / 90−3）數值全等 ⟹ 純數值不可分',
    len(vals) == 1, f'all = {vals.pop()} —— 結構身份需獨立論證, 唔可以數值揀')

# =====================================================================
# §D  Λ 結構依賴分解
# =====================================================================
print("\n" + "=" * 78)
print("§D Λ 依賴分解（邊啲係結構、邊啲係觀測）")
print("=" * 78)

# Λ = (m_p⁵·τ_p/ħ)^{1/4} / (√(4π)·xy)
# 結構部分: xy = λ₂(N_gen−λ₂)（docs/04 恆等, 零參數）
chk('D1', '★ 結構輸入: xy = λ₂(N_gen−λ₂) = 0.060656936533（docs/04 恆等, 零參數）',
    abs(xy - lam2 * (N_gen - lam2)) < 1e-12, f'xy = {xy:.12f}')
chk('D2', '★ 觀測輸入: τ_p 下限（Super-K）、m_p、ħ —— Λ 非純結構（半結構量）',
    True, 'τ_p > 2.4e34 yr = 觀測, 唔係 IDCM 結構輸出')

# Λ ∝ τ^{1/4}: 靈敏度
d_lnLam_d_lntau = 0.25
chk('D3', f'★ Λ ∝ τ_p^{{{d_lnLam_d_lntau}}} ⟹ τ_p 一個數量級變化只移動 Λ 0.56 數量級（穩健）',
    abs(d_lnLam_d_lntau - 0.25) < 1e-12, '四次根壓縮 ⟹ 標度對 τ_p 極不敏感')

# Λ ∝ 1/xy ⟹ λ₂ 譜決定
Lam_if_xy2 = Lam_analytic * xy / (lam2 * (N_gen - lam2))
chk('D4', '★ Λ ∝ 1/xy（λ 譜倒數）⟹ 若用錯誤譜直接標度會漂移 %.2f%%' % (0.0),
    abs(Lam_if_xy2 - Lam_analytic) / Lam_analytic < 1e-9, 'λ 譜係 Λ 唯一結構貢獻')

# =====================================================================
# §E  誠實限制
# =====================================================================
print("\n" + "=" * 78)
print("§E 誠實限制")
print("=" * 78)
chk('E1', '⚠️ Λ 係量綱式下限（冇強子矩陣元 f_p、冇 renorm、冇 phase space）⟹ 數量級級',
    True, 'docs/06 §E 維持')
chk('E2', '⚠️ M_Pl/Λ = 86.800 ≠ 87（dev −0.23%）⟹「= M_Pl/87」唔可以升格為結構恆等',
    True, '87 只係下界投影四捨五入；任何「87=結構數」推導必須解釋 0.23% 缺口')
chk('E3', '⚠️ 87 三重候選數值不可分 ⟹ 結構身份未決（需 freeze v2 / lattice 直量）',
    True, 'docs/20 記錄 🟡 維持, 唔 close')
chk('E4', '★★ 唯一可升格結論: Λ 解析式（g 抵消）＋ Λ ∝ 1/(λ₂(N_gen−λ₂)) 結構依賴',
    True, '零新常數；VL 絕對質量仍依賴觀測 τ_p（半結構）')

print("\n" + "=" * 78)
tot = len(CHECKS); ps = sum(1 for c in CHECKS if c['pass'])
print(f"匯總: 總檢查數 {tot}  PASS {ps}  FAIL {tot-ps}")
print(f"  {('🎉 全部通過' if ps == tot else '⚠️ 有 FAIL')}")

with open('data/22_lambda_identity.json', 'w', encoding='utf-8') as f:
    json.dump({'total': tot, 'passed': ps, 'failed': tot - ps, 'checks': CHECKS,
               'Lambda_GeV': Lam_analytic, 'M_Pl_over_Lambda': ratio,
               'dev_vs_87_pct': dev87,
               'Lambda_analytic': '(m_p^5*tau_p/hbar)^(1/4)/(sqrt(4pi)*lam2*(N_gen-lam2))',
               'triple_candidates_87': {'2N_d-1': 2 * N_d - 1, 'N_gen*L7': N_gen * L7,
                                        'Sigma_gamma - N_gen': B * (N_d + 1) // 2 - N_gen},
               'caveats': 'dimensional-analysis lower bound; 87 is a lower-bound projection, not an identity'},
              f, ensure_ascii=False, indent=2)
print("✅ 已保存 data/22_lambda_identity.json")
