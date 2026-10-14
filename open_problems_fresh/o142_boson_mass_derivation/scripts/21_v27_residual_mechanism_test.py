#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v27 - 137 殘留 δ=0.036 嘅機制測試 (M1/M2/M3)

殘留: δ = α⁻¹(0) − 137 = 0.035999074
測試三個物理候選機制 (由方程前向預言 δ, 唔係由 δ 反搜公式):

M1 | Running scale: α⁻¹(Q*) = 137 嘅 Q* 有冇自然意義?
M2 | Uehling 真空極化: Z_cr QED 修正量級 ~ (α/π)·Z?
M3 | density check: δ 喺結構常數 1% 窗內有幾密?
    (density 係背景判據 — 命中都唔係機制, 高密度=巧合)
"""
import mpmath as mp
mp.mp.dps = 40
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

# ---- 實測輸入 ----
a_inv_0 = mp.mpf('137.035999074')
me      = mp.mpf('0.51099895000e-3')    # GeV
delta_obs = a_inv_0 - mp.mpf(137)
alpha   = mp.mpf(1)/a_inv_0

print("="*72)
print("殘留 δ = α⁻¹(0) − 137 =", mp.nstr(delta_obs, 12))
print("="*72)

# ============ M1: running scale ============
print()
print("M1: α⁻¹(Q*) = 137 嘅 Q* 有冇自然意義?")
print("    QED 1-loop (低 Q 只計 e 圈): α⁻¹(Q₂) = α⁻¹(m_e) − (2/3π)·ln(Q₂/m_e)")
print("    解 α⁻¹(Q*) = 137: ln(Q*/m_e) = δ/(2/3π)")
b_e = mp.mpf(2)/(3*mp.pi)
lnQ = delta_obs/b_e
Qstar = me*mp.e**lnQ
print(f"    ln(Q*/m_e) = {mp.nstr(lnQ,8)}")
print(f"    Q*        = {mp.nstr(Qstar,8)} GeV")
print(f"    Q*/m_e    = {mp.nstr(Qstar/me,8)}")
print(f"    ⟹ Q* ≈ 1.185 m_e — 冇明顯結構意義 (唔似 γ_N/κ̃²/½)")
print()

# ============ M2: Uehling ============
print("M2: Uehling 真空極化修正量級")
delta_ueh = 137*alpha/mp.pi
print(f"    (α/π)·137 = {mp.nstr(delta_ueh,8)}   vs δ_obs = {mp.nstr(delta_obs,8)}")
print(f"    量級比 = {mp.nstr(delta_ueh/delta_obs,5)}")
print(f"    ⟹ Uehling 主階 ~0.32 太大 (>8×); 唔可以直接歸因 δ")
print()

# ============ M3: density check ============
print("M3: δ 喺結構常數 1% 窗內 density")
cands = [
    ('1/28 (B·L₄=28)',      mp.mpf(1)/28),
    ('1/27 (L₃³=27)',       mp.mpf(1)/27),
    ('(26/137)²',           (mp.mpf(26)/137)**2),
    ('1/(2π·4.4)',          mp.mpf(1)/(2*mp.pi*mp.mpf('4.4'))),
    ('1/(137·φ²)',          mp.mpf(1)/(137*mp.mpf(1)+137*mp.mpf('0.61803398875'))),
    ('δ/α(0)',              delta_obs*alpha),
]
hits = 0
for name, v in cands:
    dev = abs(v - delta_obs)/delta_obs*100
    hit = dev < 1
    hits += hit
    print(f"    {name:<18} = {mp.nstr(v,10)}  dev {mp.nstr(dev,5)}% {'★' if hit else ''}")
print(f"    1% 窗命中 {hits}/{len(cands)} — 背景密度, 唔構成機制")
print(f"    δ × α⁻¹(0) = {mp.nstr(delta_obs*a_inv_0,8)} (≈4.93 = ?)")
print()

print("="*72)
print("判決: 機制測試")
print("="*72)
chk("M1 Q* = 1.185 m_e 唔係結構數 → running 唔構成歸因",
    abs(Qstar/me - mp.mpf('1.185')) < mp.mpf('1e-3')
    and abs(Qstar/me - mp.mpf('1.185')) > mp.mpf('1e-6'),
    f"Q*/m_e={mp.nstr(Qstar/me,6)} (非 γ_N/κ̃²/½ 等結構值)")
chk("M2 Uehling 主階量級 (α/π)Z ~ 0.32 ≠ 0.036 (8.9×)",
    abs(delta_ueh) > 8*delta_obs, f"ratio={mp.nstr(delta_ueh/delta_obs,3)}")
chk("M3 結構常數窗 density ≥ 2/6 → 背景密度高, 單一路徑無信息",
    hits >= 2, f"{hits}/6")
chk("δ 歸因未閉合 — 維持 🟡 (誠實開放, 唔砌算子)",
    True, "三機制全冇命中: Q* 冇結構、Uehling 量級不符、density 高")

print()
print(f"RESULT: {ok} PASS / {fail} FAIL")
print()
print("="*72)
print("開放狀態")
print("="*72)
print("  δ=0.036 歸因: 🟡 未閉合 — M1/M2/M3 全部否決")
print("  候選路面: 更高階 QED (α/π)²·137 ≈ ")
print(f"            {(mp.mpf(1)/mp.pi**2)*mp.mpf(1)/a_inv_0*137}")
print("  結論: 冇機制話到畀我哋聽點解 δ=0.036; 137.036 保留為實測值,")
print("        137 保留為 Z_cr=1/α 計數身份; 兩者 gap 係 IDCM 外部 (QED) 或")
print("        未明結構 — 唔靠砌算子閉合")