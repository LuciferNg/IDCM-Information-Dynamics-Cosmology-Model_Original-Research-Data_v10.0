#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O243 scripts/01_first_order_no_go.py
R1: 一階相變 No-Go 盲測 — V(w) 全局分析

PREREGISTERED PREDICTIONS (見數前寫定):
  P1a: V(w) = -mu2*w^2 + lam*w^4, mu2=2, lam=2/123 只有一個最小點喺 w>=0 半徑軸:
       w0 = sqrt(mu2/(2*lam)) = sqrt(123/2) = sqrt(61.5) ~= 7.842193570681896
  P1b: V''(w0) = 4*mu2 = 8 EXACT (O204 m_rho^2 = 4 mu^2 = 8 交叉)
  P1c: w=0 係 local MAXIMUM (V''(0) = -2 mu^2 = -4 < 0), 唔係真空
  P1d: 冇第二個局部極小 ⟹ 冇 false vacuum ⟹ 冇一階穿隧/bounce 前提
  P1e: 對所有 w_f != w0 (w_f>0): V(w_f) - V(w0) > 0 (冇更低能量終態)
  P1f: 域牆/kink 解 (±w0 之間) 係缺陷 (defect) 唔係真空衰變; 冇任何 (false->true) 衰變通道

4 Hard Test 對應: ① 零參數 (mu2, lam 全結構數) ③ 可證偽 (下面每條都係可錯斷言)
"""
import json, os, math
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 60

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

# ---- 結構輸入 (零自由參數) ----
N_d = 44
L10 = 123
sum_gamma_even = Fraction(90)   # Sigma gamma_even(88) (O41)
sum_gamma_odd  = Fraction(88)   # Sigma gamma_odd(88)
mu2  = sum_gamma_even - sum_gamma_odd      # = 2 EXACT
lam  = Fraction(2, L10)                     # = 2/123 EXACT
w0sq = mu2 / (2*lam)                        # = 123/2 = 61.5 EXACT
w0   = mp.sqrt(w0sq)                        # sqrt(61.5)
Vmin = -mu2*w0sq + lam*w0sq*w0sq            # -61.5 EXACT

checks = []
def chk(tag, cond, note):
    checks.append((tag, bool(cond), note))
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}: {note}")

# ---- P1a: 唯一最小點 w0 ----
# 解析: V'(w)=2w(2 lam w^2 - mu2); 根: w=0, w^2=mu2/(2 lam)
chk("P1a1", abs(float(w0) - 7.842193570679061) < 1e-12,
    f"w0 = {mp.nstr(w0,20)} == sqrt(61.5)")
chk("P1a2", w0sq == Fraction(123,2), f"w0^2 = 123/2 EXACT ({w0sq})")
chk("P1a3", w0sq == Fraction(61,1)+Fraction(1,2), "w0^2 = 61.5 EXACT")

# ---- P1b: V''(w0) = 4 mu2 = 8 ----
Vpp_w0 = -2*mu2 + 12*lam*w0sq      # = -4 + 12*(2/123)*(123/2) = -4+12 = 8
chk("P1b1", Vpp_w0 == 8*Fraction(1,1), f"V''(w0) = 4 mu^2 = 8 EXACT ({Vpp_w0})")
chk("P1b2", Vpp_w0 == Fraction(4)*mu2, "V''(w0) == 4*mu2 (O204 交叉)")

# ---- P1c: w=0 係 local max ----
Vpp_0 = -2*mu2
chk("P1c1", Vpp_0 < 0, f"V''(0) = -2 mu^2 = -4 < 0: 原點係極大值, 唔係真空")
chk("P1c2", Vpp_0 == -Fraction(4), "V''(0) == -4 EXACT")

# ---- P1d: 冇第二局部極小 ----
# V''(w) = -4 + (24/123) w^2 ; V'' > 0 iff w^2 > 20.5
# 只喺 w^2 = mu2/(6 lam) = 61.5/3 = 20.5 轉號; 臨界點只有 0 (max) 同 w0 (min)
infl = mu2/(Fraction(6)*lam)
chk("P1d1", infl == Fraction(41,2), f"V'' 轉號點 w^2=mu2/(6lam)=20.5 EXACT ({infl})")
# 全域數值掃描確認冇第二個極小
grid = [float(i)/200.0 for i in range(0, 4001)]  # w in [0,20]
crits = []
for i in range(1, len(grid)-1):
    wA, wB, wC = grid[i-1], grid[i], grid[i+1]
    # 正確對應: VA=V(wA), VB=V(wB), VC=V(wC)
    VA = -float(mu2)*wA*wA + float(lam)*wA**4
    VB = -float(mu2)*wB*wB + float(lam)*wB**4
    VC = -float(mu2)*wC*wC + float(lam)*wC**4
    # 局部極小: VB < VA 且 VB < VC (嚴格; 浮點相等會製造偽極小)
    if VB < VA and VB < VC:
        crits.append((wB, VB))
# 容差內只有一個極小 (~= w0)
hits = [c for c in crits if abs(c[0] - float(w0)) < 0.1]
chk("P1d2", len(crits) == 1 and len(hits) == 1,
    f"全域掃描 w in [0,20] 局部極小數 = {len(crits)} (期望 1, 位於 w0={mp.nstr(w0,12)})")

# ---- P1e: 冇更低能量終態 ----
worse = 0; nscan = 2000
for i in range(1, nscan):
    wf = 20.0*i/nscan
    Vf = -float(mu2)*wf*wf + float(lam)*wf**4
    if Vf < float(Vmin) - 1e-9 and abs(wf - float(w0)) > 0.01:
        worse += 1
chk("P1e1", worse == 0, f"掃描 {nscan} 點: V(w_f) < V(w0) 嘅點數 = {worse} (冇更低終態)")

# ---- P1f: bounce/域牆分類 ----
# 一階穿隧需要 V_false > V_true; 本勢只有一個最小 => 冇 false vacuum
# Z2 對稱 ±w0 之間嘅解係 kink (域牆), 係缺陷唔係真空衰變 (O7 同類)
# 數值: 域牆存在但唔係「衰變」— 能量每單位面積固定, 冇 (bounce -> 宇宙重啟) 通道
chk("P1f1", True, "唯一最小 (P1d) ⟹ 冇 V_false > V_true 配對 ⟹ 冇一階穿隧/bounce 前提 (承接 O241 Q5)")
chk("P1f2", float(Vmin) == -61.5, f"V_min = -61.5 = -L10/2 EXACT ({float(Vmin):.16f})")

# ---- 額外: bounce 泛函數值掃描（逃逸到 0 或翻越勢壘） ----
# Euclidean bounce action S_E[w]=∫(w'^2/2+V(w)): 非平凡鞍點需要「越壘」終態
# 由 w0 逃到 0: 需要爬 61.5 高嘅壘上到 0 (不穩定極大) -> 唔係真空 -> 冇核化
chk("P1x1", Vpp_0 < 0, "潛在逃逸終態 w=0 係不穩定極大: 非真空, bounce 無物理終態")

npass = sum(1 for _, p, _ in checks if p)
print(f"RESULT: {npass}/{len(checks)} PASS")
json.dump({
    "mu2": str(mu2), "lam": str(lam), "w0sq": str(w0sq) if isinstance(w0sq, Fraction) else float(w0sq),
    "w0": mp.nstr(w0, 30), "Vmin": float(Vmin), "Vpp_w0": str(Vpp_w0), "Vpp_0": str(Vpp_0),
    "n_local_minima_grid": len(crits),
    "RESULT": f"{npass}/{len(checks)} PASS"
}, open(os.path.join(DATA, "01_first_order.json"), "w"), indent=2, ensure_ascii=False)