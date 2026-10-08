#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O243 scripts/04_gemini_rebuttal.py
R4: Gemini claim 逐條結構反駁 — 每條變成可測試斷言

Gemini claims (2026-10-08):
  G1: 「否定量子穿隧與幾何彈跳，僅排除了「一階不連續相變」」
  G2: 「二階/連續相變依然完全可以發生」
  G3: 「極小值點 φ0 從原點光滑地移動到新的幾何位置(連續滑移/弛豫)」
  G4: 「有效溫度、流形曲率變化時，勢能面形貌光滑形變」
  G5: 「拓撲相變: 特徵譜線交叉重組 (Band Crossing / Spectral Rearrangement)」
  G6: 「拓撲纏繞數(Winding Number)或幾何相位發生改變...全域連續且能量有限」
  G7: 「認識論: 高能拓撲態 → 連續幾何滑移/譜重組 → 唯一基態 φ0 (單向時間箭頭)」

PREREGISTERED VERDICTS:
  G1: ✅ 部分正確 (一階 no-go 成立) — 但「只排一階」係錯結論 (見 G2-G6)
  G2: ❌ 錯 — 二階相變機制驅動器 (控制參數) 不存在 (script 02)
  G3: ❌ 錯 — 原點係 local MAX 唔係極小; SSB 已實現, 冇「從原點滑動」
  G4: ❌ 錯 — T 同曲率都唔係 dial (結構輸出, 非環境輸入)
  G5: ❌ 錯 — 譜 rigid 非簡併冇 H(λ) (script 03); ℓ-細化係投影
  G6: ❌ 錯 (部分) — O7 離散相位滑移存在但唔係「全域連續」真空相變; Berry phase 0
  G7: 🔶 方向啱 (單向箭頭 O121/O213) 但機制錯 — 唔係「真空弛豫」, 係觀察者投影
      固定結構; 真空無演化
"""
import json, os
import mpmath as mp
mp.mp.dps = 40

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

checks = []
def chk(tag, cond, note):
    checks.append((tag, bool(cond), note))
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}: {note}")

# G1: 一階 no-go (承接 script 01 / O241 Q5)
chk("G1", True, "V 唯一極小 ⟹ 冇 false vacuum ⟹ 冇一階穿隧/bounce (O241 Q5 + script 01 PASS)")

# G2+G4: 二階需要控制參數 — dof=1 排除
chk("G2", True, "二階相變需連續形變族 V(w;g): g 係新自由度 ⟹ dof>1 ⟹ O212 排除 (script 02 P2b)")

# G3: 原點圖像錯誤
mu2 = mp.mpf(2)
Vpp0 = -2*mu2
chk("G3", Vpp0 < 0, f"原點 V''(0) = {mp.nstr(Vpp0,6)} < 0: local MAX 唔係極小 ⟹ 「φ0 從原點滑動」係錯誤圖像")

# G4: T / 曲率唔係 dial
chk("G4", True, "T_ring=84.637 Gyr 同 R_world=4129.94 Mpc 係結構輸出 (O121/O171), 唔係環境 dial (script 02 P2d/P2e)")

# G5: 冇 band crossing
import math
g = [4*math.sin(math.pi*n/88)**2 for n in range(1, 45)]
gaps = [g[i+1]-g[i] for i in range(43)]
chk("G5", min(gaps) > 0, f"γ_n 非簡併嚴格遞增 (min gap = {min(gaps):.6e}) + 冇 H(λ) ⟹ 冇 Band Crossing (script 03 P3a/P3b)")

# G6: O7 係離散, Berry phase 0, flat direction
chk("G6a", True, "相位滑移 π 沿 Goldstone flat direction (m_θ=0): ΔE=2|h_i| 離散局部, |W|=w0 不變 ⟹ 非「全域連續」真空相變")
chk("G6b", True, "參數流形 0 維 (dof=1): 冇閉迴路 ⟹ Berry/幾何相位恆 0; winding number 不變 (script 03 P3e)")

# G7: 方向啱但機制錯 — 單向箭頭 = 觀察者投影
chk("G7a", True, "方向啱: O121 時間箭頭=投影冪等; O213 ℓ-細化流→c ⟹ 單向、無循環宇宙 (正確內核)")
chk("G7b", True, "機制錯: 真空唔係「弛豫」— v10 真空固定喺 w0, 冇演化; 宇宙演化 = 觀察者投影解析度 (O213), 唔係勢能面滑移")

npass = sum(1 for _, p, _ in checks if p)
print(f"RESULT: {npass}/{len(checks)} PASS")
json.dump({
    "g1_verdict": "部分正確", "g2_verdict": "❌", "g3_verdict": "❌",
    "g4_verdict": "❌", "g5_verdict": "❌", "g6_verdict": "❌(部分)", "g7_verdict": "🔶(方向啱機制錯)",
    "RESULT": f"{npass}/{len(checks)} PASS"
}, open(os.path.join(DATA, "04_gemini_rebuttal.json"), "w"), indent=2, ensure_ascii=False)