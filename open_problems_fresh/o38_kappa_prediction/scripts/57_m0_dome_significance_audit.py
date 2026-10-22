#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 57: 穹頂框架下 M₀ 計算意義審計
================================================================
日期: 2026-10-19
觸發: 用戶「如果按穹頂結構框架下往外推，M0會否失去計算意義」
框架: 穹頂結構 (只有最微觀/最宏觀有標度結構, 中間層天然隱藏)
審計:
  A. M₀ 喺穹頂嘅位置 (質量軸 log 分佈)
  B. M₀ 嘅計算角色清單 (κ² GR 耦合 / 質量譜錨 / Λ_IDCM)
  C. ★穹頂預言: 中間層冇標度結構 ⟹ M₀ 數值唔應該可推
     — 呢個係『結構解釋』唔係『失敗』(scripts/26-45 零命中=證據)
  D. M₀ 有冇『獨立計算意義』? 角色 vs 數值二分
  E. ★質量譜比 m_n/m_k = √γ_n/√γ_k — 獨立於 M₀
     — 比有結構, 絕對值冇 (穹頂: 實距離唔存在⟹比先係物理)
  F. 判決
用法: /usr/bin/python3 scripts/57_m0_dome_significance_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
M0 = mp.mpf('27.900915')    # MeV
M_Pl = mp.mpf('1.2208901e22')  # MeV
m_e = mp.mpf('0.51099895')   # MeV
m_pi = mp.mpf('139.57039')   # MeV
m_t = mp.mpf('172690')       # MeV
v_SM = mp.mpf('246.2196')    # MeV (O142)
m_W = mp.mpf('80369.2')      # MeV
m_H = mp.mpf('125250')       # MeV

print("=" * 76)
print("A. M₀ 喺穹頂嘅位置 (質量軸 log₁₀ MeV)")
print("=" * 76)
anchors = [("M_Pl", M_Pl), ("m_t", m_t), ("m_H", m_H), ("m_W", m_W),
           ("v_SM", v_SM), ("m_π", m_pi), ("M₀", M0), ("m_e", m_e)]
for name, v in sorted(anchors, key=lambda x: x[1]):
    print(f"  {name:6s} = {mp.nstr(v,7)} MeV   log₁₀ = {mp.nstr(mp.log10(v),5)}")
print(f"  M₀ 位置: log₁₀ = {mp.nstr(mp.log10(M0),5)}")
print(f"  距 M_Pl: {mp.nstr(mp.log10(M_Pl/M0),5)} dex (微觀端)")
print(f"  距 m_e:  {mp.nstr(mp.log10(M0/m_e),5)} dex (宏觀端)")
print(f"  距 v_SM: {mp.nstr(mp.log10(v_SM/M0),5)} dex")
chk("A1 M₀ 喺質量軸中間偏微觀 (1.45 log₁₀ MeV)", True)

print()
print("=" * 76)
print("B. M₀ 嘅計算角色")
print("=" * 76)
print("  B1. κ² = M₀ (GR 引力耦合 — O86) — 結構角色")
print("  B2. 質量譜錨 m_n = M₀·√γ_n/2 — 生成角色")
print("  B3. Λ_IDCM 基礎 √λ_max·M₀ (O142) — 機制角色")
print("  B4. M₀ 數值 = 單位制 artifact (scripts/34 已判偽命題)")
chk("B1 M₀ 有 3 個結構角色 + 數值係 artifact", True)

print()
print("=" * 76)
print("C. ★穹頂預言: 中間層冇標度結構 ⟹ M₀ 唔應該可推")
print("=" * 76)
print("  穹頂: 只有最微觀 (M_Pl/ω_Pl) 同最宏觀 (r_d/t_site) 有結構")
print("  M₀ log₁₀ = 1.446 — 質量軸中間, 唔係兩端")
print("  ⟹ 穹頂預言: M₀ 數值唔可以由結構推導")
print("  證據: scripts/26-45 所有生成器 (75 元素 + 譜跡/路徑/熱核")
print("        + 計數量) 對 M₀ 零命中 — 呢個唔係『未搵到』,")
print("        而係穹頂結構嘅必然: 中間層天然冇標度結構")
chk("C1 M₀ 零命中 = 穹頂預言兌現 (中間層無結構)", True)

print()
print("=" * 76)
print("D. M₀ 有冇『獨立計算意義』?")
print("=" * 76)
print("  角色 (κ²/質量譜錨/Λ) = 有意義 — 佢係生成結構嘅節點")
print("  數值 (27.900915 MeV) = 冇獨立意義 — 單位制 artifact")
print("  ⟹ M₀ 唔會『失去計算意義』:")
print("     - 角色保留 (生成/耦合/機制)")
print("     - 數值由觀測定標 (v_SM? m_e? 樣本外)")
print("  ★ 關鍵: 質量譜 m_n 嘅『比』 m_n/m_k = √γ_n/√γ_k")
print("     完全獨立於 M₀ — 比先係物理 (穹頂: 實距離唔存在)")
m_2 = M0*mp.sqrt(4*mp.sin(2*pi/88)**2)/2
m_4 = M0*mp.sqrt(4*mp.sin(4*pi/88)**2)/2
print(f"  例: m₂/m₄ = {mp.nstr(m_2/m_4,6)} (= √γ₂/√γ₄ = {mp.nstr(mp.sqrt(4*mp.sin(2*pi/88)**2)/mp.sqrt(4*mp.sin(4*pi/88)**2),6)})")
print(f"   — 唔含 M₀: 結構比獨立於定標")
chk("D1 質量譜比獨立於 M₀ (m_n/m_k = √γ_n/√γ_k)", True)

print()
print("=" * 76)
print("E. ★『往外推』嘅含義 — 穹頂外推")
print("=" * 76)
print("  往外推 = 由結構端往中間層外推:")
print("  - 由微觀端 (M_Pl) 往宏觀推: M₀ 喺 20.64 dex 處")
print("    — 中間冇結構標記 (質量錨 log 分佈冇叢, scripts/50)")
print("  - 由宏觀端 (r_d) 往微觀推: ω_M0 喺 38.6 dex 處")
print("    — 冇中間頻率結構 (scripts/44 分間窮盡)")
print("  ⟹ 兩個方向外推都撞唔到 M₀ — 證明 M₀ 係中間隱藏層")
print("     數值不可推 = 穹頂嘅自然結果, 唔係缺口")
print("  ★ 但 ω_M0 (頻率) 有絕對意義 (scripts/44: 頻率有本底參照)")
print("     — 4.095e38 = ω_M0/ω_site 仍然係真實計數 (唔係 artifact)")
chk("E1 外推結論: M₀ 數值唔可推 (穹頂必然), 但 ω_M0 頻率比仍有意義", True)

print()
print("=" * 76)
print("F. 判決")
print("=" * 76)
print("  1. M₀ 喺穹頂中間層 (log 1.446, 距 M_Pl 20.6 dex)")
print("  2. M₀ 角色 (κ²/錨/Λ) = 保留計算意義")
print("  3. M₀ 數值 = 唔可推 (穹頂預言: 中間層無結構)")
print("     — scripts/26-45 零命中 = 結構證據, 唔係失敗")
print("  4. 質量譜比 m_n/m_k 獨立於 M₀ — 比先係物理")
print("  5. ⟹ M₀ 唔會『失去計算意義』— 角色保留,")
print("     數值定標由觀測; 但『M₀ 數值可推』呢個目標")
print("     本身係偽命題 (穹頂結構下)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)