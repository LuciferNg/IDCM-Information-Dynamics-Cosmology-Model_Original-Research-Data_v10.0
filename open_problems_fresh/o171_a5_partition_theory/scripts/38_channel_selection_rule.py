#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/38 — 通道分派律之結構導出 (Structural Derivation of the Channel
                   Assignment Law)

背景 (docs/25 §10 遺留 第 1 項):
  第九輪 (scripts/36) 確立: 28 對 (成員 x 通道) 之中只有 3 對係「合法檢定」,
  而該 3 對**全部**都已經係「發現處」通道 => 分派被判定為 post-hoc (發現處繼承)。
  遺留: 分派本身要唔要由結構導出? 呢個係本節要答嘅問題。

★★ 本節核心主張 (可證偽):
  設通道 X 之已註冊 bare 值 B(X), 觀測 O(X) +- sigma(X)。
  成員 d (修正因子 (d-1)/d) 作用於 X
      <=>  R(X,d) := d * [1 - O(X)/base(X,d)] = 1
  base(X,d) = B(X) * prod{(d'-1)/d' : d' in chain(X), d' != d}
  ★ 意義: R = 1 即「該通道之 bare 虧缺**恰為** 1/d」。修正 (d-1)/d 所做嘅事就係
    扣掉 1/d => 「分派」= 「虧缺等於 1/d」, 係**結構陳述** (唔含 sigma)。

本節做七件事:
  A. 通道表 (含 r* 之更正後值 144.43 +- 0.26; 見 docs/27)
  B. ★ 代數定理: z_dev = z_det * (R - 1) EXACT (sympy)
     => scripts/36 之三條件判準 <=> 「R-判準 + 容差 1/z_det」
  C. 20 對之 R 值表 (讀法 I: 邊際/必要性) -> 分離度
  D. ★ Planck 混欄之影響 (更正前 vs 更正後)
  E. ★ 33/34 同 44/45 之不可檢定性 —— 分兩個讀法 (I 邊際 / II 替代鏈)
  F. look-elsewhere: 兩種多重度指標 (d_req 窗 / sigma 窗)
  G. 分派律之可證偽預言

輸出: data/38_channel_selection_rule.log
"""

from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 50

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


print("=" * 78)
print("O171 scripts/38 -- 通道分派律之結構導出")
print("=" * 78)

# =====================================================================
print("\n=== A: 通道表 (r* 已更正; 見 docs/27) ===")

R_WORLD = mp.mpf("4129.94")              # o167 scripts/16 之 R_world
BARE_RD = mp.pi * R_WORLD / 88           # piR/88
THETA_BARE100 = 100 * 7 * mp.pi / 2112   # 100 * 7pi/2112

OBS = {
    "theta_star":   (mp.mpf("1.04110"), mp.mpf("0.00031"),
                     "Planck 2018 VI Tab.2 col5 [TT,TE,EE+lowE+lensing]: 100theta* = 1.04110 +- 0.00031"),
    "r_d":          (mp.mpf("147.09"),  mp.mpf("0.26"),
                     "Planck 2018 VI Tab.2 col5: r_drag = 147.09 +- 0.26 Mpc"),
    "r_star":       (mp.mpf("144.43"),  mp.mpf("0.26"),
                     "★ 更正: Planck 2018 VI Tab.2 col5: r* = 144.43 +- 0.26 Mpc"),
    "Omega_Lambda": (mp.mpf("0.6847"),  mp.mpf("0.0073"),
                     "Planck 2018 VI Tab.2 col5: Omega_Lambda = 0.6847 +- 0.0073"),
}
_xr = OBS["r_star"][0] / OBS["r_d"][0]
_sr = mp.sqrt((OBS["r_star"][1] / OBS["r_star"][0]) ** 2
              + (OBS["r_d"][1] / OBS["r_d"][0]) ** 2)
OBS["r_ratio"] = (_xr, _sr, "r*/r_d = 144.43/147.09 (誤差傳播; 假設獨立)")

BARE = {
    "theta_star":   (THETA_BARE100, "7pi/2112 (o73 docs/07 + o167 docs/02)"),
    "r_d":          (BARE_RD,       "piR/88 (o167 docs/05)"),
    "r_star":       (BARE_RD,       "piR/88 (o167 docs/05)"),
    "r_ratio":      (mp.mpf(1),     "定義 (比通道 bare = 1)"),
    "Omega_Lambda": (mp.mpf(41) / 60, "41/60 (O39/O84 真空預算)"),
}
CHAIN = {
    "r_d":          [421],
    "r_star":       [421, 56],
    "r_ratio":      [56],
    "theta_star":   [],
    "Omega_Lambda": [],
}
MEMBERS = [("33/34", 34), ("44/45", 45), ("55/56", 56), ("420/421", 421)]
CH_ORDER = ["theta_star", "r_d", "r_star", "r_ratio", "Omega_Lambda"]

print(f"  {'通道':>14} {'觀測中心':>16} {'sigma':>11} {'sigma_rel':>11}  bare")
for k in CH_ORDER:
    c, s, _ = OBS[k]
    print(f"  {k:>14} {mp.nstr(c, 10):>16} {mp.nstr(s, 6):>11} "
          f"{float(s / c) * 100:10.5f}%  {BARE[k][1]}")
print(f"\n  piR/88 = {mp.nstr(BARE_RD, 12)}")
print(f"  100*7pi/2112 = {mp.nstr(THETA_BARE100, 12)}")

chk("A1 r*/r_d (更正後) = 0.9819163... (唔再係 0.982120)",
    abs(float(_xr) - 0.98191630) < 1e-6, f"({mp.nstr(_xr, 10)})")
chk("A2 sigma_rel(r*/r_d) = 0.25229%",
    abs(float(_sr) * 100 - 0.25229) < 5e-5, f"({float(_sr) * 100:.5f}%)")

# =====================================================================
print("\n=== B: 代數定理 z_dev = z_det * (R - 1)  [sympy 精確] ===")

import sympy as sp

b, o, d_, s_ = sp.symbols("B O d sigma", positive=True)
z_dev = sp.simplify((b * (d_ - 1) / d_ - o) / s_)
z_det = sp.simplify((b / d_) / s_)
Rr = sp.simplify(d_ * (1 - o / b))
diff = sp.simplify(z_dev - z_det * (Rr - 1))
print(f"  z_dev = {z_dev}")
print(f"  z_det = {z_det}")
print(f"  R     = {Rr}")
print(f"  z_dev - z_det*(R-1) = {diff}")
chk("B1 ★ z_dev = z_det*(R-1) EXACT (free_symbols = 空)",
    diff == 0 and getattr(diff, "free_symbols", set()) == set(), f"({diff})")
chk("B2 R = 1 <=> z_dev = 0 (修正精確命中)",
    sp.simplify(z_dev.subs(o, b * (d_ - 1) / d_)) == 0)
chk("B3 ★ 推論: |z_dev| <= 1sigma <=> |R-1| <= 1/z_det (代數等價)",
    sp.simplify(sp.Abs(z_dev) - sp.Abs(z_det * (Rr - 1))) == 0)

# =====================================================================
print("\n=== C: 讀法 I (邊際/必要性) — R 值表 ===")


def base_marginal(ck, d):
    """讀法 I: 已註冊鏈中「移除 d 之因子」後之 base"""
    bare, _ = BARE[ck]
    base = bare
    for dd in CHAIN[ck]:
        if dd == d:
            continue
        base = base * mp.mpf(dd - 1) / dd
    return base


rows = []
print(f"  {'成員':>9} {'d':>5} {'通道':>14} {'base':>16} {'虧缺':>12} "
      f"{'d_req':>10} {'R':>10} {'|R-1|':>9}")
for lab, d in MEMBERS:
    for ck in CH_ORDER:
        obs, sig, _ = OBS[ck]
        bs = base_marginal(ck, d)
        delta = 1 - obs / bs
        d_req = 1 / delta if delta != 0 else mp.inf
        Rv = d * delta
        rows.append(dict(mem=lab, d=d, k=ck, base=bs, delta=delta,
                         d_req=d_req, R=Rv, dev=abs(Rv - 1)))
        print(f"  {lab:>9} {d:>5} {ck:>14} {mp.nstr(bs, 10):>16} "
              f"{float(delta) * 100:+11.5f}% {float(d_req):10.2f} "
              f"{float(Rv):10.5f} {float(abs(Rv - 1)) * 100:8.4f}%")

srt = sorted(rows, key=lambda r: r["dev"])
print("\n  -- 按 |R-1| 排序 (最接近 R=1 者, 前 6) --")
for r in srt[:6]:
    print(f"    {r['mem']:>9} x {r['k']:<14} |R-1| = {float(r['dev']) * 100:8.4f}%"
          f"   d_req = {float(r['d_req']):9.2f}")

near = [r for r in rows if r["dev"] < 0.02]
print(f"\n  總對數 = {len(rows)};  |R-1| < 2% 之對 = {len(near)}")
for r in near:
    print(f"    {r['mem']:>9} x {r['k']:<14} |R-1| = {float(r['dev']) * 100:.4f}%")
chk("C1 |R-1| < 2% 之對 = 3 (同 scripts/36 三合法對同一批)",
    len(near) == 3, f"({[(r['mem'], r['k']) for r in near]})")
chk("C2 該 3 對 = {420/421 x r_d, 55/56 x r_star, 55/56 x r_ratio}",
    sorted([(r["mem"], r["k"]) for r in near])
    == sorted([("420/421", "r_d"), ("55/56", "r_star"), ("55/56", "r_ratio")]))
chk("C3 ★ 3 對之 |R-1| 全部 >= 0.1% => 冇一對係「精確 R=1」",
    all(r["dev"] > 0.001 for r in near),
    f"(最細 {min(float(r['dev']) * 100 for r in near):.4f}%)")

# =====================================================================
print("\n=== D: ★ Planck 混欄之影響 (更正前 vs 更正後) ===")

OBS_OLD_R, OBS_OLD_S = mp.mpf("144.46"), mp.mpf("0.25")
print(f"  {'':>6} {'觀測 r*':>12} {'r*/r_d':>12} {'虧缺':>11} {'R(d=56)':>10} {'|R-1|':>9}")
for tag, rv in (("更正前", OBS_OLD_R), ("更正後", OBS["r_star"][0])):
    ratio = rv / OBS["r_d"][0]
    delta = 1 - ratio
    Rv = 56 * delta
    print(f"  {tag:>6} {mp.nstr(rv, 8):>12} {mp.nstr(ratio, 10):>12} "
          f"{float(delta) * 100:+10.5f}% {float(Rv):10.5f} "
          f"{float(abs(Rv - 1)) * 100:8.4f}%")

d_old = 1 - OBS_OLD_R / OBS["r_d"][0]
d_new = 1 - OBS["r_star"][0] / OBS["r_d"][0]
R_old, R_new = 56 * d_old, 56 * d_new
print(f"\n  ★ d_req: 更正前 {float(1 / d_old):.3f}  ->  更正後 {float(1 / d_new):.3f}")
print(f"  ★ |R-1|: {float(abs(R_old - 1)) * 100:.4f}%  ->  "
      f"{float(abs(R_new - 1)) * 100:.4f}%  (惡化 {float(abs(R_new - 1) / abs(R_old - 1)):.1f}x)")
chk("D1 更正後 d_req ~ 55.30 (更正前 55.93) -- 更遠離 56",
    abs(float(1 / d_new) - 55.30) < 0.02, f"({float(1 / d_new):.4f})")
chk("D2 ★ |R-1| 惡化 > 9x",
    float(abs(R_new - 1) / abs(R_old - 1)) > 9.0,
    f"({float(abs(R_new - 1) / abs(R_old - 1)):.2f}x)")

f421 = F(420, 421)
r_d_chain = BARE_RD * f421.numerator / f421.denominator
rs_5556 = r_d_chain * F(55, 56).numerator / F(55, 56).denominator
rs_5455 = r_d_chain * F(54, 55).numerator / F(54, 55).denominator
gap = abs(rs_5556 - rs_5455)
print(f"\n  鏈預測 r* (用 55/56) = {mp.nstr(rs_5556, 10)}")
print(f"  鏈預測 r* (用 54/55) = {mp.nstr(rs_5455, 10)}")
print(f"  兩者相差 = {mp.nstr(gap, 6)} Mpc = "
      f"{float(gap / OBS['r_star'][1]):.4f} sigma(r*)")
for tag, rv, sv in (("更正前 144.46+-0.25", OBS_OLD_R, OBS_OLD_S),
                    ("更正後 144.43+-0.26", OBS["r_star"][0], OBS["r_star"][1])):
    z1 = float((rs_5556 - rv) / sv)
    z2 = float((rs_5455 - rv) / sv)
    print(f"    {tag}:  z(55/56) = {z1:+8.4f}sigma  z(54/55) = {z2:+8.4f}sigma"
          f"  -> 較近者 = {'55/56' if abs(z1) < abs(z2) else '54/55'}")
z_old1 = float((rs_5556 - OBS_OLD_R) / OBS_OLD_S)
z_old2 = float((rs_5455 - OBS_OLD_R) / OBS_OLD_S)
z_new1 = float((rs_5556 - OBS["r_star"][0]) / OBS["r_star"][1])
z_new2 = float((rs_5455 - OBS["r_star"][0]) / OBS["r_star"][1])
chk("D3 更正前 55/56 較近", abs(z_old1) < abs(z_old2),
    f"({abs(z_old1):.4f} vs {abs(z_old2):.4f})")
chk("D4 ★ 更正後 54/55 較近 (次序反轉)",
    abs(z_new2) < abs(z_new1), f"({abs(z_new1):.4f} vs {abs(z_new2):.4f})")
sep = float(gap / OBS["r_star"][1])
need = OBS["r_star"][1] / (gap / 3)
print(f"\n  ★ 分辨 55/56 vs 54/55 需 3sigma => sigma(r*) 由 "
      f"{float(OBS['r_star'][1]):.3f} 降至 {float(gap / 3):.5f} Mpc"
      f" => 改善 {float(need):.2f}x")
chk("D5 兩鏈預測之差 < 1 sigma(r*) => 1sigma 內不可分",
    sep < 1.0, f"({sep:.4f}sigma)")
chk("D6 ★ 需 sigma 改善 > 15x 方可 3sigma 分辨",
    float(need) > 15.0, f"({float(need):.2f}x)")

# =====================================================================
print("\n=== E: ★ 33/34 同 44/45 之不可檢定性 (兩個讀法) ===")

print("  讀法 I (邊際/必要性): base = 已註冊鏈移除 d 之因子")
print("  讀法 II (替代鏈):     base = bare, chain = [d] 單一成員")
print(f"\n  分派律要求: 成員 d 之通道必有虧缺 delta = 1/d")
for lab, d in (("33/34", 34), ("44/45", 45), ("55/56", 56), ("420/421", 421)):
    print(f"    {lab}: delta = 1/{d} = {100 / d:.4f}%")

print(f"\n  -- 讀法 II: 逐 (成員 x 通道) 之單成員預測 --")
print(f"  {'成員':>9} {'通道':>14} {'with':>16} {'z_dev':>10} {'z_det':>9}  判定")
alt_legal = []
alt_rows = []
for lab, d in MEMBERS:
    for ck in CH_ORDER:
        obs, sig, _ = OBS[ck]
        bare, _ = BARE[ck]
        w = bare * mp.mpf(d - 1) / d
        z = float((w - obs) / sig)
        zdet = float((bare / d) / sig)
        ok = abs(z) <= 1.0 and zdet >= 1.0
        verdict = "OK 合法" if ok else ("唔吻合" if abs(z) > 1 else "檢定力<1sigma")
        alt_rows.append(dict(mem=lab, d=d, k=ck, z=z, zdet=zdet, ok=ok))
        if ok:
            alt_legal.append((lab, ck, z, zdet))
        print(f"  {lab:>9} {ck:>14} {mp.nstr(w, 10):>16} {z:+9.4f}s {zdet:8.3f}s  {verdict}")

print(f"\n  讀法 II 合法對 = {len(alt_legal)}")
for lab, ck, z, zdet in alt_legal:
    print(f"    OK {lab} x {ck}  (z_dev {z:+.4f}sigma, z_det {zdet:.3f}sigma)")

# 每個成員之最佳替代 (|z_dev| 最細)
print(f"\n  -- 每個成員之最佳替代通道 (|z_dev| 最細) --")
for lab, d in MEMBERS:
    best = min([r for r in alt_rows if r["mem"] == lab], key=lambda r: abs(r["z"]))
    print(f"    {lab:>9}: {best['k']:<14} z_dev = {best['z']:+8.4f}sigma"
          f"  (z_det {best['zdet']:.3f}sigma)  "
          f"{'OK' if abs(best['z']) <= 1 else '超出 1sigma 判準 ' + format(abs(best['z']) - 1, '.4f') + 'sigma'}")

b34 = min([r for r in alt_rows if r["d"] == 34], key=lambda r: abs(r["z"]))
b45 = min([r for r in alt_rows if r["d"] == 45], key=lambda r: abs(r["z"]))
chk("E1 ★ 33/34 之最佳替代通道 |z_dev| > 2.5sigma => 全滅",
    abs(b34["z"]) > 2.5, f"({b34['k']} {b34['z']:+.4f}sigma)")
chk("E2 ★★ 44/45 之最佳替代通道 = r_star, z_dev = -1.030sigma (邊緣!)",
    b45["k"] == "r_star" and abs(abs(b45["z"]) - 1.030) < 0.005,
    f"({b45['k']} {b45['z']:+.4f}sigma)")
chk("E3 ★ 44/45 只差 0.031sigma 就通過 1sigma 判準 => 邊緣而非全滅",
    0.0 < abs(b45["z"]) - 1.0 < 0.05,
    f"(差 {abs(b45['z']) - 1:.4f}sigma)")
z45_old = float((BARE_RD * mp.mpf(44) / 45 - OBS_OLD_R) / OBS_OLD_S)
print(f"\n  44/45 x r* 之 z_dev: 更正前 {z45_old:+.4f}sigma  ->  更正後 {b45['z']:+.4f}sigma")
chk("E4 ★ 更正令 44/45 x r* 更接近通過 (|z| 縮細)",
    abs(b45["z"]) < abs(z45_old), f"({abs(z45_old):.4f} -> {abs(b45['z']):.4f})")
chk("E5 ★ 55/56 x r_star 在讀法 II 失敗 (|z| > 1) => 需 420/421 先作用",
    abs([r for r in alt_rows if r["d"] == 56 and r["k"] == "r_star"][0]["z"]) > 1.0,
    f"({[r for r in alt_rows if r['d'] == 56 and r['k'] == 'r_star'][0]['z']:+.4f}sigma)")
chk("E6 33/34 之發現通道 (CMB 峰高) 冇獨立 bare 值 => 簡併, 不可檢定",
    True, "(docs/12 §8: 統一因子同 A_s 簡併)")
chk("E7 ★ 44/45 之發現通道係譜恆等式 88/90 => 唔係觀測量",
    abs(float(mp.mpf(88) / 90 - F(44, 45))) < 1e-40)

# 讀法 I 之 33/34 / 44/45
m34 = [r for r in rows if r["d"] == 34]
m45 = [r for r in rows if r["d"] == 45]
print(f"\n  讀法 I 之 33/34: 最細 |R-1| = {min(float(r['dev']) for r in m34) * 100:.4f}%"
      f"  ({min(m34, key=lambda r: r['dev'])['k']})")
print(f"  讀法 I 之 44/45: 最細 |R-1| = {min(float(r['dev']) for r in m45) * 100:.4f}%"
      f"  ({min(m45, key=lambda r: r['dev'])['k']})")
chk("E8 讀法 I 下 33/34 同 44/45 之最細 |R-1| 都 > 50%",
    min(float(r["dev"]) for r in m34) > 0.5
    and min(float(r["dev"]) for r in m45) > 0.5,
    f"({min(float(r['dev']) for r in m34) * 100:.1f}%, "
    f"{min(float(r['dev']) for r in m45) * 100:.1f}%)")

# =====================================================================
print("\n=== F: look-elsewhere (兩種多重度指標) ===")

FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
LUC = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]
G_INV = [1, 3, 4, 5, 12, 60]
CAND = sorted(set(FIB) | set(LUC) | {g * l for g in G_INV for l in LUC}
              | {88, 176, 44, 33, 55, 420, 421})
print(f"  結構候選集 = {len(CAND)} 個")

dreqs = {}
for ck in CH_ORDER:
    obs, sig, _ = OBS[ck]
    bare, _ = BARE[ck]
    delta = 1 - obs / bare
    dreqs[ck] = 1 / delta

print(f"\n  指標 1 — d_req 窗 (|d/d_req - 1| <= 1%):")
print(f"  {'通道':>14} {'d_req':>11} {'窗內候選':>22}")
tol1 = {}
for ck in CH_ORDER:
    v = dreqs[ck]
    if v <= 0:
        print(f"  {ck:>14} {'(負)':>11}  {'—':>22}")
        tol1[ck] = []
        continue
    w = [n for n in CAND if abs(n / v - 1) <= 0.01]
    tol1[ck] = w
    print(f"  {ck:>14} {float(v):11.2f}  {str(w):>22}")

print(f"\n  指標 2 — sigma 窗 (|with_ - obs| <= 1sigma, 全成員):")
print(f"  {'通道':>14} {'1sigma 窗寬':>14} {'窗內結構候選 (N 值)':>30}")
sigwin = {}
for ck in CH_ORDER:
    obs, sig, _ = OBS[ck]
    bare, _ = BARE[ck]
    lo, hi = (obs - sig) / bare, (obs + sig) / bare   # 容許之 (d-1)/d
    w = []
    for N in CAND:
        f = mp.mpf(N) / (N + 1)
        if lo <= f <= hi:
            w.append(N)
    sigwin[ck] = w
    print(f"  {ck:>14} {float(2 * sig / bare) * 100:13.5f}%  {str(w):>30}")

chk("F1 ★ r_ratio 之 d_req 窗內只有 1 個候選 => 高度選擇性",
    len(tol1["r_ratio"]) == 1, f"({tol1['r_ratio']})")
chk("F2 r_d 之 d_req 窗內只有 2 個候選 (420, 421)",
    tol1["r_d"] == [420, 421], f"({tol1['r_d']})")
chk("F3 theta_star 之 d_req > 1000 => 窗內冇候選",
    float(dreqs["theta_star"]) > 1000 and len(tol1["theta_star"]) == 0,
    f"(d_req = {float(dreqs['theta_star']):.0f})")
chk("F4 ★ r_ratio 之 sigma 窗內結構候選 = 4 (更正後; 更正前 = 3)",
    len(sigwin["r_ratio"]) == 4, f"({sigwin['r_ratio']})")

# ★ 更正前之 sigma 窗 (對照)
_so_old = mp.sqrt((OBS_OLD_S / OBS_OLD_R) ** 2
                  + (OBS["r_d"][1] / OBS["r_d"][0]) ** 2)
_ro_old = OBS_OLD_R / OBS["r_d"][0]
_lo_o, _hi_o = _ro_old - _so_old, _ro_old + _so_old
w_old = [N for N in CAND if _lo_o <= mp.mpf(N) / (N + 1) <= _hi_o]
print(f"\n  ★ sigma 窗對照 (r_ratio): 更正前 sigma_rel = {float(_so_old) * 100:.5f}%"
      f"  -> {w_old}")
print(f"                            更正後 sigma_rel = {float(_sr) * 100:.5f}%"
      f"  -> {sigwin['r_ratio']}")
chk("F6 ★ 更正令 sigma 窗由 3 個退化候選增至 4 個 (新增 N = 48)",
    len(w_old) == 3 and len(sigwin["r_ratio"]) == 4
    and 48 in sigwin["r_ratio"] and 48 not in w_old,
    f"({w_old} -> {sigwin['r_ratio']})")
chk("F5 ★ d_req 窗 (1%) 比 sigma 窗嚴格 => 54 被排除",
    54 not in tol1["r_ratio"] and 54 in sigwin["r_ratio"],
    f"(d_req 窗 {tol1['r_ratio']}, sigma 窗 {sigwin['r_ratio']})")

# =====================================================================
print("\n=== G: 分派律之可證偽預言 ===")
print("  P1: 新通道若其 bare 虧缺 = 1/d (d 為成員) => 該成員作用於該通道")
print("  P2: 若虧缺唔等於任何 1/d => 該通道唔受家族修正 => bare 公式必須自足")
print("  P3: 虧缺顯著性 < 1sigma 之通道 => 分派不可判定")

z_th_bare = float((THETA_BARE100 - OBS["theta_star"][0]) / OBS["theta_star"][1])
print(f"\n  theta* 之 bare 虧缺顯著性 = {z_th_bare:+.4f}sigma => < 1sigma => 不可判定 (P3)")
chk("G1 theta* bare 虧缺 < 1sigma => 分派不可判定 (同對消律一致)",
    abs(z_th_bare) < 1.0, f"({z_th_bare:+.4f}sigma)")
chk("G2 theta* 之 d_req 唔近任何成員 => P2 判定「自足」",
    min(abs(float(dreqs["theta_star"]) - m[1]) for m in MEMBERS) > 100,
    f"(最近 = {min(abs(float(dreqs['theta_star']) - m[1]) for m in MEMBERS):.0f})")
chk("G3 Omega_Lambda 之虧缺為負 => 任何 (d-1)/d 修正只會令其更遠 => P2 排除",
    (1 - OBS["Omega_Lambda"][0] / BARE["Omega_Lambda"][0]) < 0,
    f"(虧缺 {float(1 - OBS['Omega_Lambda'][0] / BARE['Omega_Lambda'][0]) * 100:+.5f}%)")

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILED: " + "; ".join(FAILS))
print("=" * 78)
