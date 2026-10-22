#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O241 R10 — F-Q4.3 高 ℓ 尾段判準實跑 (docs/04 判準執行, 預期 FAIL 照記錄)
================================================================================
判準 F-Q4.3 (docs/04): IDCM 結構譜尾段 (Silk 阻尼) 預言 ℓ_D=9055
`ℓ_D = 88 × (N_d + M + 2F₇) − F₄² = 88×103 − 9 = 9055` (O48 scripts/06 結構推導)
實測層: Planck TT 高 ℓ 段阻尼包絡 D(ℓ) = A·exp[-(ℓ/ℓ_D)^(3/2)] 之 ℓ_D,obs
預期 (docs/04 風險註明): 實測 ℓ_D ~ 1000-2000 量級 (ΛCDM Silk ~1411) ⟹ 預期 FAIL
本 script: 照跑照記錄 (誠實負結果 = 交付), 唔重推譜閉合 (cmb_cl 已閉合 0.83%).

方法:
  (a) 讀 Planck TT (o9 data/planck_tt.txt, ℓ 到 2492)
  (b) D_ℓ = C_ℓ·ℓ(ℓ+1)/2π, 搵局部峰 (振幅 > 500)
  (c) 對峰列 fit damping 包絡, 抽 ℓ_D,obs
  (d) 對比 IDCM 9055: dev -> FAIL (預期) 照記錄
"""

import json, os, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []
def check(name, cond, detail=""):
    results.append({"check": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

DATADIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks/data"
data = np.loadtxt(os.path.join(DATADIR, "planck_tt.txt"))
ell = data[:, 0]; C = data[:, 1]
D = C * ell*(ell+1)/(2*math.pi)

print("="*72)
print("R10: F-Q4.3 高 ℓ 尾段 — Silk 阻尼尺度判準實跑 (預期 FAIL)")
print("="*72)

# (b) 峰列 (振幅 > 400, 局部極大)
peaks = []
for i in range(1, len(D)-1):
    if D[i] > D[i-1] and D[i] > D[i+1] and D[i] > 400:
        peaks.append((ell[i], D[i]))
print(f"\n  峰列 (振幅>400): {len(peaks)} 個")
for l, v in peaks:
    print(f"    ℓ={l:6.0f}  D={v:8.1f}")

# (c) damping 包絡 fit: D(ℓ) = A·exp[-(ℓ/ℓ_D)^(3/2)]
# 峰頂有 acoustic oscillation 重疊 (非單調), 先用 upper-envelope (滑動窗局部最大)
def upper_env(ls, ds, halfw=250):
    """upper envelope: 每點取其 +-halfw 內最大值"""
    env = []
    n = len(ls)
    for i in range(n):
        lo = max(0, i - halfw); hi = min(n, i + halfw + 1)
        j = lo + list(ds[lo:hi]).index(max(ds[lo:hi]))
        env.append((ls[j], ds[j]))
    # 只保留真正嘅包絡點 (連續下降段)
    return np.array(env)

# 先用峰列做 upper envelope (對峰列嚟講, 窗細啲)
peaks_arr = np.array(peaks)
l_arr = peaks_arr[:, 0]; d_arr = peaks_arr[:, 1]

# 直接方法: 喺阻尼區 (ℓ>1000) 對「峰包絡」fit.
# 峰包絡 = 只取局部極大中「高於前後峰」嘅點, 再 fit exp 衰減
mask_hi = l_arr > 1000
l_hi = l_arr[mask_hi]; d_hi = d_arr[mask_hi]
x_hi = l_hi**1.5
y_hi = np.log(d_hi)
if len(l_hi) >= 3:
    A_fit, B_fit = np.polyfit(x_hi, y_hi, 1)
    if B_fit < 0:
        ellD_obs = (-B_fit) ** (-2.0/3.0)
    else:
        # 斜率正 => 冇明顯 damping fit, 用直接衰減比抽尺度
        ellD_obs = float('nan')
    print(f"\n  阻尼區 fit (ℓ>1000, {len(l_hi)} 峰): ln D = {A_fit:.3f} {B_fit:+.6e} x")
else:
    ellD_obs = float('nan')
    print("\n  阻尼區峰太少, 用衰減比法")

# 無論如何, 用「峰振幅衰減比」直接判準 (穩陣, 唔靠 fit):
# 錨點: m≈5 最後清晰回彈窗 (ℓ≈1100, D≈1246) vs 高 ℓ 尾窗 (ℓ≈1730, D≈408)
# 呢兩個窗口都係「peak-top envelope」, 唔涉及冇阻尼嘅谷底
anchor_lo = 1121.0; Dlo = 1246.3
anchor_hi = 1733.0; Dhi = 407.6
ratio = Dhi/Dlo
# IDCM ℓ_D=9055 預言 damping 比率: exp[-(ℓ_hi/9055)^1.5] / exp[-(ℓ_lo/9055)^1.5]
# (只計 Silk 阻尼包絡; acoustic 結構兩窗口同相位唔會差太多)
d_idcm = math.exp(-(anchor_hi/9055.0)**1.5) / math.exp(-(anchor_lo/9055.0)**1.5)
d_lcdm = math.exp(-(anchor_hi/1411.0)**1.5) / math.exp(-(anchor_lo/1411.0)**1.5)
dev_ratio_idcm = abs(ratio - d_idcm)/d_idcm
dev_ratio_lcdm = abs(ratio - d_lcdm)/d_lcdm
print("\n  包絡衰減比 (佐證, 峰振幅受 acoustic T(ℓ) 污染, 唔係純 damping):")
print(f"    Planck 實測      = D({anchor_hi:.0f})/D({anchor_lo:.0f}) = {Dhi:.0f}/{Dlo:.0f} = {ratio:.3f}")
print(f"    IDCM ℓ_D=9055    = {d_idcm:.3f}  (~冇衰減)")
print(f"    ΛCDM ℓ_D=1411    = {d_lcdm:.3f}")
print(f"    dev(IDCM)={dev_ratio_idcm:.1%}  dev(ΛCDM)={dev_ratio_lcdm:.1%} (量級比較, 唔作 pass/fail)")

# 判準主體: 文獻阻尼尺度比較 (乾淨, 唔受峰結構污染)
# IDCM O48 結構式 ℓ_D = 88×(44+33+2×13) − 9 = 9055
# Planck 2018 TT Silk damping scale ℓ_D ≈ 1411 (LoVerde/Zaldarriaga 形式)
ellD_idcm = 9055.0
ellD_lcdm = 1411.0
ratio_scale = ellD_idcm / ellD_lcdm
print(f"\n  判準主體 — 阻尼尺度: IDCM ℓ_D = {ellD_idcm:.0f} vs Planck ΛCDM ℓ_D = {ellD_lcdm:.0f}")
print(f"    IDCM/ΛCDM = {ratio_scale:.2f}×  (6.4× 偏大 ⟹ IDCM 預言阻尼太弱)")
check("F-Q4.3: IDCM 尾段阻尼尺度 (ℓ_D,IDCM = 9055) 對文獻 (1411) dev<50% 為過",
      abs(ellD_idcm - ellD_lcdm)/ellD_lcdm < 0.50,
      f"dev = {(abs(ellD_idcm-ellD_lcdm)/ellD_lcdm):.0%}  (預期 FAIL: 結構式 9055 與文獻差 6.4×)")

with open(os.path.join(BASE, "data", "10_r10_high_ell.json"), "w") as f:
    json.dump({"ellD_idcm": ellD_idcm, "ellD_lcdm": ellD_lcdm,
               "ratio_scale": ratio_scale,
               "envelope": {"anchor_lo": anchor_lo, "Dlo": Dlo,
                            "anchor_hi": anchor_hi, "Dhi": Dhi, "ratio": ratio},
               "peaks": [[l, v] for l, v in peaks]}, f, indent=2)

npass = sum(1 for r in results if r["pass"])
nfail = sum(1 for r in results if not r["pass"])
print(f"\n{'='*72}\nRESULT: {npass}/{len(results)} PASS\n{'='*72}")