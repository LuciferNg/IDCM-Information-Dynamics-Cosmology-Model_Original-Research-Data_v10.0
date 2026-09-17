#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/31 — 家族可檢定性「通道分裂」矩陣

背景 (docs/20 §7 遺留 🔴):
  docs/20 得出「家族成員之『識別』全部不可達 (≥ 60×)」, 並用**單一通道**
  (Planck D₁ 峰高 σ = 2.844%) 對所有成員計偵測門檻。

本節檢驗該做法係否正確: 每個成員嘅修正因子 U = (d−1)/d 究竟作用於**邊個觀測量**?
若唔同成員作用於唔同通道, 而各通道精度差 16×, 則「單一通道」計法會**系統性低估**
部分成員嘅可檢定性。

通道精度 (真實數據):
  CMB 峰高 D₁  : 5816.48 ± 165.42 μK²      (2.844%)  [Planck binned, O10]
  CMB 振幅 A_s : ln(10^10 A_s) = 3.044 ± 0.014      (1.400%)  [Planck 2018 VI Tab.2]
  BAO 尺 r_d   : 147.09 ± 0.26 Mpc                  (0.1767%) [Planck 2018 VI]
  BAO 尺 r*    : 144.46 ± 0.25 Mpc                  (0.1730%)
  r*/r_d 比    : 0.982122, σ = √(0.001730²+0.001767²) (0.2473%)

顯著性定義 (docs/16 §9 用同一約定):
  偵測 z = (1/d) / σ_channel        [兩假設 U=1 vs U=(d−1)/d 之差距 = 1/d]
  識別 z = (1/(d(d−1))) / σ_channel
  (docs/20 §3 之「差 X×」= 2/z, 同一信息)
"""

import json
import math
from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
N_PASS = 0
N_FAIL = 0
FAILS = []


def chk(name, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        N_FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


print("=" * 72)
print("O171 scripts/31 — 家族可檢定性「通道分裂」矩陣")
print("=" * 72)

# ---------------------------------------------------------------- 數據
CH = {
    "D1_peak":   dict(sig=165.4180814864716 / 5816.479677744882,
                      src="Planck binned D₁ 峰高 5816.48±165.42"),
    "A_s":       dict(sig=0.014,     src="Planck 2018 VI Tab.2: ln(1e10 As)=3.044±0.014"),
    "r_d":       dict(sig=0.26 / 147.09, src="Planck 2018 VI: r_d=147.09±0.26 Mpc"),
    "r_star":    dict(sig=0.25 / 144.46, src="Planck 2018 VI: r*=144.46±0.25 Mpc"),
    "r_ratio":   dict(sig=math.hypot(0.25 / 144.46, 0.26 / 147.09),
                      src="r*/r_d = 144.46/147.09 = 0.982122"),
}
for k, v in CH.items():
    print(f"  σ({k:9s}) = {v['sig']*100:7.4f}%   [{v['src']}]")

MEMBERS = [
    # (label, d, channel, 來源)
    ("33/34", 34, "A_s", "O10 質數峰 (K_tree+1)"),
    ("44/45", 45, "A_s", "O10 質數峰 (N_d+1)"),
    ("55/56", 56, "r_ratio", "O167 (F₁₀+1) — r*/r_d"),
    ("420/421", 421, "r_d", "O167 (L₇²+1)/2 — r_d 絕對"),
]

print("\n=== A: 通道精度比 (為何單一通道計法會出錯) ===")
r_prec = CH["D1_peak"]["sig"] / CH["r_d"]["sig"]
print(f"  σ(D₁ 峰高) / σ(r_d) = {r_prec:.3f}×")
chk("A1 ★ BAO 尺精度比 CMB 峰高好 16.09×",
    abs(r_prec - 16.089) < 0.01, f"({r_prec:.3f}×)")
r_prec2 = CH["D1_peak"]["sig"] / CH["r_ratio"]["sig"]
print(f"  σ(D₁ 峰高) / σ(r*/r_d) = {r_prec2:.3f}×")
chk("A2 ★ r*/r_d 比更佳: 好 11.50×", abs(r_prec2 - 11.500) < 0.01, f"({r_prec2:.3f}×)")

print("\n=== B: 逐成員 × 逐通道 顯著性矩陣 ===")
print(f"  {'成員':>9} {'d':>5} {'通道':>9} {'1/d':>9} {'σ_ch':>9} {'z_偵測':>9} {'z_識別':>9} {'狀態':>6}")
rows = {}
for lab, d, chan, src in MEMBERS:
    sig = CH[chan]["sig"]
    sep = 1.0 / d
    z_det = sep / sig
    z_id = (1.0 / (d * (d - 1))) / sig
    st = "🟢" if z_det >= 3 else ("🟡" if z_det >= 1 else "🔴")
    rows[lab] = dict(d=d, chan=chan, sep=sep, sig=sig, z_det=z_det, z_id=z_id, st=st)
    print(f"  {lab:>9} {d:>5} {chan:>9} {sep*100:8.4f}% {sig*100:8.4f}% "
          f"{z_det:8.2f}σ {z_id:8.3f}σ {st:>6}")

chk("B1 ★ 55/56 經 r*/r_d 通道: z_偵測 = 7.22σ (可檢定)",
    abs(rows["55/56"]["z_det"] - 7.222) < 0.01,
    f"({rows['55/56']['z_det']:.3f}σ)")
chk("B2 420/421 經 r_d 通道: z = 1.34σ (邊緣)",
    abs(rows["420/421"]["z_det"] - 1.344) < 0.01,
    f"({rows['420/421']['z_det']:.3f}σ)")
chk("B3 33/34 經 A_s 通道: z = 2.10σ (比 D₁ 通道 1.03σ 好 2.03×)",
    abs(rows["33/34"]["z_det"] - 2.101) < 0.01,
    f"({rows['33/34']['z_det']:.3f}σ)")
chk("B4 44/45 經 A_s 通道: z = 1.59σ",
    abs(rows["44/45"]["z_det"] - 1.587) < 0.01,
    f"({rows['44/45']['z_det']:.3f}σ)")
chk("B5 ★ 全部成員之 z_識別 < 0.2σ ⇒ 識別仍全部不可達 (docs/20 結論保留)",
    all(r["z_id"] < 0.2 for r in rows.values()),
    f"(max {max(r['z_id'] for r in rows.values()):.3f}σ)")

print("\n=== C: 55/56 之實際吻合 (r*/r_d 比) ===")
r_obs = mp.mpf('144.46') / mp.mpf('147.09')
r_pred = mp.mpf(55) / mp.mpf(56)
dev = (r_obs / r_pred - 1) * 100
print(f"  觀測 r*/r_d = 144.46/147.09 = {mp.nstr(r_obs, 10)}")
print(f"  預言 55/56  = {mp.nstr(r_pred, 10)}")
print(f"  dev = {float(dev):+.5f}%")
chk("C1 ★ r*/r_d 觀測 = 0.982120 (55/56 預言 dev −0.0024%)",
    abs(float(r_obs) - 0.982120) < 1e-6 and abs(float(dev)) < 0.01,
    f"({float(r_obs):.6f}, dev {float(dev):+.5f}%)")
# 無修正假設 (r*/r_d = 1) 之偏離
dev_no = (r_obs / 1 - 1) * 100
print(f"  無修正 (r*/r_d = 1) 之偏離 = {float(dev_no):+.4f}% ⇒ z = {float(dev_no)/100/CH['r_ratio']['sig']:.2f}σ")
chk("C2 ★ 55/56 對「無修正」之判別力 = 7.22σ ⇒ 檢定已成立",
    abs(abs(float(dev_no)) / 100 / CH['r_ratio']['sig'] - 7.222) < 0.01)

print("\n=== D: 420/421 之實際吻合 (r_d 絕對) + CMB-S4 投影 ===")
rd_pred = mp.mpf('147.0883')
rd_obs = mp.mpf('147.09')
dev_rd = (rd_pred / rd_obs - 1) * 100
print(f"  IDCM r_d = 147.0883 vs 觀測 147.09 ± 0.26 ⇒ dev {float(dev_rd):+.4f}%")
chk("D1 420/421 修正後 r_d dev = 0.0012%",
    abs(float(dev_rd)) < 0.005, f"({float(dev_rd):+.5f}%)")
# 無修正值 (πR/88 = 147.4385)
rd_bare = mp.mpf('147.4385')
dev_bare = (rd_bare / rd_obs - 1) * 100
z_bare = float(dev_bare) / 100 / CH['r_d']['sig']
print(f"  無修正值 147.4385 ⇒ dev {float(dev_bare):+.4f}%, z = {z_bare:.2f}σ")
chk("D2 ★ 420/421 對無修正之判別力 = 1.34σ (未達 3σ, 邊緣)",
    abs(z_bare - 1.344) < 0.01, f"({z_bare:.3f}σ)")
for tag, sg in (("CMB-S4 (σ_r_d = 0.05%)", 0.0005), ("CMB-S4+DESI (0.02%)", 0.0002)):
    z = float(dev_bare) / 100 / sg
    print(f"  {tag:26s} ⇒ z = {z:.1f}σ  ({'🟢 可檢定' if z >= 3 else '🔴'})")
chk("D3 ★ CMB-S4 (0.05%) ⇒ 420/421 z = 4.75σ 可檢定",
    abs(float(dev_bare) / 100 / 0.0005 - 4.75) < 0.05)

print("\n=== E: 更正 docs/20 §7 之斷言 ===")
print("  舊 (docs/20 §7): 「家族成員之識別全部不可達」+ 單一通道 (D₁ 2.844%) 計偵測")
print("  新 (本節):")
print("    (i) 識別: 維持不可達 (全部 z_id < 0.2σ) ✓ 舊斷言成立")
print("    (ii) 偵測: **通道分裂** —— 唔可以單一通道計")
print("         BAO 通道 (55/56): z = 7.22σ 🟢 已檢定通過")
print("         BAO 通道 (420/421): z = 1.34σ 🟡 → CMB-S4 4.75σ")
print("         CMB 振幅通道 (33/34, 44/45): z = 1.03–2.10σ 🔴")
chk("E1 ★ 通道分裂: 至少一個成員 (55/56) z ≥ 3σ ⇒ 舊「全部不可達」過寬",
    max(r["z_det"] for r in rows.values()) >= 3)

print("\n=== F: 通道分裂定理 ===")
print("  定理: 家族成員之可檢定性由 **其作用通道之精度** 決定, 唔係由 d 單獨決定。")
print("  推論: 單一通道計法 (docs/20 §4) 對 BAO 通道成員系統性低估 11.5–16.1×。")
n_bao = sum(1 for r in rows.values() if r["chan"] in ("r_d", "r_ratio"))
print(f"  統計: BAO 通道成員 {n_bao} 個 (z̄ = "
      f"{sum(r['z_det'] for r in rows.values() if r['chan'] in ('r_d','r_ratio'))/n_bao:.2f}σ), "
      f"CMB 振幅通道成員 {len(rows)-n_bao} 個 (z̄ = "
      f"{sum(r['z_det'] for r in rows.values() if r['chan'] not in ('r_d','r_ratio'))/(len(rows)-n_bao):.2f}σ)")
chk("F1 ★ BAO 通道平均 z 比 CMB 振幅通道高 ≥ 2× (實測 2.33×)",
    (sum(r['z_det'] for r in rows.values() if r['chan'] in ('r_d', 'r_ratio')) / n_bao) >=
    2 * (sum(r['z_det'] for r in rows.values() if r['chan'] not in ('r_d', 'r_ratio')) / (len(rows) - n_bao)))

# ---------------------------------------------------------------- 輸出
out = {
    "channel_precision": {k: v["sig"] for k, v in CH.items()},
    "precision_ratio_D1_over_rd": r_prec,
    "matrix": {k: {kk: (float(vv) if isinstance(vv, float) else vv)
                   for kk, vv in v.items()} for k, v in rows.items()},
    "r_ratio_obs": float(r_obs),
    "r_ratio_pred": float(r_pred),
    "r_ratio_dev_pct": float(dev),
    "z_bare_rd": z_bare,
    "verdict": "通道分裂定理: 55/56 (r*/r_d) z=7.22σ 已檢定通過; 420/421 z=1.34σ (CMB-S4 4.75σ); "
               "CMB 振幅通道 33/34 2.10σ / 44/45 1.59σ; 識別全部仍不可達",
}
(BASE / "data" / "31_channel_split_matrix.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

print("\n" + "=" * 72)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 72)
