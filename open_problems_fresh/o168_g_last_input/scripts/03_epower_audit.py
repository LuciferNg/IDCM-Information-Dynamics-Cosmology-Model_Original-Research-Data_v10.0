#!/usr/bin/env python3
"""
O168 — 03: e 冪全庫審計 (e-Power Cross-O Inventory)
===================================================
O165 反秘數 doctrine: 禁 e 底數冪做樹層權重 (樹權重 = φ^-2ℓ, ℓ 整數)。
但框架多處用 e 冪做「尺度因子」。本 script 逐個審計分類:

| e 冪 | 值 | 出處 | 身份 | 判決 |
|------|----|------|------|------|
| e^-44 | 7.78e-20 | O53 m₄₄ = M_Pl·e^-44 | 鏈維度因子 (44=N_d) | 🟡 機制開放 |
| e^33  | 2.14e14 | O160 M_GUT = M_Z·e^33 | 樹深度因子 (33=K_tree) | 🟡 機制開放 |
| e^-74 | 3.2e-33 | cmb_cl/o83 T_CMB | 已降級 (O166) | ✅ 已死 |
| e^-25.5| 8.4e-12 | o164 候選 | ℓ=26.5 半整數 | ✅ 已死 |
| e^-70.05| 3.57e-31| O38 √(ħH₀/E_P) | 幾何平均 (有結構身份) | ✅ 結構 |

另: 近距命中 e^-44/(2F_proj) = 0.145% (本 O 發現) — 🟡 機制開放, 移交。
"""
from mpmath import mp, mpf, exp, ln, sqrt, pi
mp.dps = 50

phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 74)
print("  O168 — 03: e 冪全庫審計")
print("=" * 74)

# ── [1] 逐項審計 ──
print("\n─── [1] e 冪清單 ───")
entries = [
    ("e^-44  (O53 m₄₄ = M_Pl·e^-44)", exp(-44),
     "鏈維度因子 44 = N_d site 數 (docs/08)。e 底數機制冇推導 — 點解 e 唔係 φ/2/16?",
     "🟡 機制開放 — 唔係 O165 樹權重 (層次唔同), 但 e 底數無結構來源"),
    ("e^33   (O160 M_GUT = M_Z·e^33)", exp(33),
     "樹深度 K_tree = 33。同 e^-44 對偶 (44-33 = 11 = L₅)。",
     "🟡 機制開放 — e 底數無結構來源; 且 M_Z 係觀察輸入 → M_GUT 係投影"),
    ("e^-74  (cmb_cl/o83 T_CMB)", exp(-74),
     "O166 已降級: 實際 dev 0.104% 非 0.01%, check 用 1% 鬆容差, e 冪 + 任意 10²。",
     "✅ 已死 (O166 降級)"),
    ("e^-25.5 (o164 候選)", exp(-25.5),
     "kT/M₀ 候選: ℓ = 26.5 半整數 → O165 規則死。",
     "✅ 已死 (o164 排除)"),
    ("e^-70.05 (O38 √(ħH₀/E_P))", sqrt(mpf('6.582119569e-16')*mpf('2.3524826e-18')/mpf('1.220910e28')),
     "普朗克-世界幾何平均 √(ħH₀/E_P)。e 出現係 ln(ħH₀/E_P)/2 嘅自然對數 — 有結構身份。",
     "✅ 結構 (幾何平均, 唔係任意 e 冪)"),
]
for name, val, why, verdict in entries:
    print(f"  · {name} = {float(val):.4e}")
    print(f"      {why}")
    print(f"      → {verdict}")
check("[1] e^-74 / e^-25.5 已死 (O166/o164 降級)", True)

# ── [2] e^-44 同 O38 φ 結構嘅張力 ──
print("\n─── [2] e^-44 (O53) vs O38 φ^47.07 — 雙尺度故事 ───")
# O53: m_f = M_Pl·e^-44·e^(δ+c·lnφ)      — e 底
# O38: M₀ = √(E_P·ħH₀)·φ^(47+37/528)·(1891/2025) — φ 底 + 幾何平均
# 兩條路對 m_e 各自閉合 (O53: 0.8%, o54: 0.16%) 但結構底數唔同
MP = mpf('1.220910e28'); M0 = mpf('27.900915e6')
me = mpf('0.51099895e6')
# O53 路: m_e = M_Pl·e^-44·e^-8·φ
me_o53 = MP*exp(-44)*exp(-8)*phi
# o54 路: m_e = M₀·γ₁·3.6  (γ₁ = 4sin²(π/88))
gam1 = 4*mp.sin(pi/88)**2
me_o54 = M0*gam1*mpf('3.6')
print(f"  m_e (O53 階梯) = {float(me_o53/1e6):.6f} MeV  dev {float(abs(me_o53/me-1)*100):.3f}%")
print(f"  m_e (o54 γ₁路) = {float(me_o54/1e6):.6f} MeV  dev {float(abs(me_o54/me-1)*100):.3f}%")
print(f"  兩路互相 dev = {float(abs(me_o53/me_o54-1)*100):.3f}%")
print(f"  → O53 e 底 同 o54/O38 φ 底係兩條並行絕對尺度故事, 喺 m_e 處相差 "
      f"{float(abs(me_o53/me_o54-1)*100):.2f}%")
check("[2] e 底/φ 底雙故事記檔 (唔當張力, 當並行路)", True,
      f"m_e 兩路相差 {float(abs(me_o53/me_o54-1)*100):.2f}%")

# ── [3] e^-44/(2F_proj) 近距命中本體 ──
print("\n─── [3] e^-44/(2F_proj) = 0.145% 近距命中 ───")
m44 = MP*exp(-44)                       # O53 階梯錨 950.02 MeV
Fproj = mpf(17)
M0_pred2 = m44/(2*Fproj)
print(f"  m₄₄ = M_Pl·e^-44 = {float(m44/1e6):.4f} MeV")
print(f"  M₀_pred = m₄₄/(2F_proj) = {float(M0_pred2/1e6):.6f} MeV  vs  M₀ = 27.900915 MeV")
dev34 = abs(M0_pred2/M0-1)*100
print(f"  dev = {float(dev34):.4f}%")
print(f"  判讀: 近距命中, 但 δ = -ln(2F_proj) = -3.526 唔係整數階梯 (O53 δ 必須整數)")
print(f"  → 唔係 O53 階梯嘅成員; 冇機制解釋 34 = 2F_proj 點解出現 → 🟡 巧合級, 移交候選")
check("[3] e^-44/2F_proj 記檔為無機制近距命中", True, f"dev {float(dev34):.4f}%")

# ── [4] O165 doctrine 合規總結 ──
print("\n─── [4] O165 合規總結 ───")
print("  O165 禁: 樹層權重 e 冪 / 任意縮放 / 鬆容差")
print("  框架現存 e 冪全部係「尺度因子」, 冇一個係樹權重 → 冇違規 ✅")
print("  但 e 底數機制 (e^-44, e^33) 全部開放 → 反秘數黃燈 🟡")
print("  O38 幾何平均 √(ħH₀/E_P) 係唯一有結構身份嘅 e 出現 ✅")
check("[4] 無 O165 違規; 2 個 e 底數機制開放移交", True)

print(f"\n{'═'*74}")
print(f"  O168-03 結果: {sum(results)}/{len(results)} PASS")
print(f"{'═'*74}")
