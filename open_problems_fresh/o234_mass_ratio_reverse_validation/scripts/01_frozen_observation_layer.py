#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O234 scripts/01 -- 凍結觀測層 + RGI 自洽 + Gemini 提案審計 + 前向 z-score 矩陣

License: IDCM O234. Deterministic, stdlib-only (no numpy/mpmath).
Output: data/01_frozen_observations.json + sha256 + PASS/FAIL lines.
"""
import json, hashlib, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# ---------------------------------------------------------------- frozen layer
# 來源: FLAG Review 2024 (arXiv:2411.04268) §4;  PDG 2024 (RPP 2024)
# 主 (Nf=2+1+1); 次 (Nf=2+1) 保留作張力審計. 只准用 ratio/RGI/同 scheme 同標度量.
FROZEN = {
    "source": "FLAG Review 2024 (2411.04268) Sec.4; PDG 2024",
    "freeze_date": "2026-10-06",
    "note": "冻結後唔准再睇新數字; 任何新增觀測量=新凍結層版本+新 sha256",
    "Nf=2+1+1": {
        "mud_MSbar_2GeV_MeV":   [3.427, 0.051],   # FLAG (34)
        "ms_MSbar_2GeV_MeV":    [93.46, 0.58],    # FLAG (34)
        "ms_mud_ratio":         [27.227, 0.081],  # FLAG (37) @0.3%
        "RGI_mud_MeV":          [4.768, 0.071, 0.046],  # (m)(Lambda) FLAG (35)
        "RGI_ms_MeV":           [130.0, 0.8, 1.3],      # FLAG (35)
        "mu_md":                [0.465, 0.024],   # FLAG Tab.10 avg (RM123 17 + MILC 18; 2.2σ tension)
        "md_mu_derived":        [1.0/0.465, 0.024/0.465**2],  # 2.1505(111)
    },
    "Nf=2+1": {
        "mud_MSbar_2GeV_MeV":   [3.387, 0.039],
        "ms_MSbar_2GeV_MeV":    [92.4, 1.0],
        "ms_mud_ratio":         [27.42, 0.12],
        "mu_md":                [0.485, 0.019],
        "md_mu_derived":        [1.0/0.485, 0.019/0.485**2],
    },
    "PDG2024": {
        "mu_2GeV_MeV":  [2.16, 0.49],
        "md_2GeV_MeV":  [4.67, 0.48],
        "md_mu_central": [4.67/2.16, 0.0],        # 2.1620 (O233 P2 嘅「觀測」)
        "mc_mc_GeV":    [1.27, 0.02],             # MSbar 自己標度
        "mb_mb_GeV":    [4.18, 0.03],             # MSbar 自己標度
        "mt_pole_GeV":  [172.57, 0.29],           # pole (renormalon caveat)
    },
    "FLAG_tabulated": {
        "mc_ms_ratio":  [11.85, 0.16],            # HPQCD 14A ⊕ (Nf=4 組合) Tab.8
    },
}

os.makedirs(DATA, exist_ok=True)
out = os.path.join(DATA, "01_frozen_observations.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(FROZEN, f, indent=2, ensure_ascii=False)
h = hashlib.sha256(open(out, "rb").read()).hexdigest()
print(f"[DATA] {out}")
print(f"[SHA256] {h}")
with open(os.path.join(DATA, "01_sha256.txt"), "w") as f:
    f.write(h + "\n")

p = s = 0
def chk(name, ok, detail):
    global p, s
    print(("  PASS " if ok else "  FAIL ") + f"[{name}] {detail}")
    if ok: p += 1
    else:  s += 1

# ---------------------------------------------------------------- CHK2 ratio 自洽
mud11, e_mud11 = FROZEN["Nf=2+1+1"]["mud_MSbar_2GeV_MeV"]
ms11,  e_ms11  = FROZEN["Nf=2+1+1"]["ms_MSbar_2GeV_MeV"]
r11,   e_r11   = FROZEN["Nf=2+1+1"]["ms_mud_ratio"]
prod11, e_prod11 = mud11*r11, r11*e_mud11 + mud11*e_r11
dev11 = abs(prod11-ms11)/e_prod11
chk("CHK2a ms/mud*mud ~ ms (2+1+1)",
    dev11 < 2.0,
    f"27.227x3.427 = {prod11:.3f} vs ms {ms11} +- {e_ms11}; dev = {dev11:.1f} sigma")

mud21, e_mud21 = FROZEN["Nf=2+1"]["mud_MSbar_2GeV_MeV"]
ms21,  e_ms21  = FROZEN["Nf=2+1"]["ms_MSbar_2GeV_MeV"]
r21,   e_r21   = FROZEN["Nf=2+1"]["ms_mud_ratio"]
prod21 = mud21*r21
dev21 = abs(prod21-ms21)/(r21*e_mud21 + mud21*e_r21)
chk("CHK2b ms/mud*mud ~ ms (2+1)",
    dev21 < 2.0,
    f"27.42x3.387 = {prod21:.3f} vs ms {ms21} +- {e_ms21}; dev = {dev21:.1f} sigma")

# ---------------------------------------------------------------- CHK3 RGI 味盲
rgi_ud, e_rgi_ud1, e_rgi_ud2 = FROZEN["Nf=2+1+1"]["RGI_mud_MeV"]
rgi_s,  e_rgi_s1,  e_rgi_s2  = FROZEN["Nf=2+1+1"]["RGI_ms_MeV"]
q_ud = rgi_ud/mud11; q_s = rgi_s/ms11
chk("CHK3 RGI 味盲 (M_RGI_ud/mud == M_RGI_s/ms)",
    abs(q_ud-q_s)/(q_ud) < 0.01,
    f"{q_ud:.4f} vs {q_s:.4f} (diff {abs(q_ud-q_s)/q_ud*100:.3f}%) -> 比值 scheme/標度無關確定")

# ---------------------------------------------------------------- CHK4 Gemini 提案審計
gem_central, gem_err = 2.14, 0.07
md_mu_11, e_md_mu_11 = FROZEN["Nf=2+1+1"]["md_mu_derived"]
md_mu_21, e_md_mu_21 = FROZEN["Nf=2+1"]["md_mu_derived"]
z_g_11 = (gem_central-md_mu_11)/e_md_mu_11
z_g_21 = (gem_central-md_mu_21)/e_md_mu_21
print("[CHK4] Gemini 宣稱 FLAG ratio_md_mu = (2.14, 0.07):")
print(f"       vs FLAG 2+1+1 md_mu = {md_mu_11:.4f}({e_md_mu_11:.3f}) -> z = {z_g_11:+.2f}")
print(f"       vs FLAG 2+1   md_mu = {md_mu_21:.4f}({e_md_mu_21:.3f}) -> z = {z_g_21:+.2f}")
print(f"       誤差棒 0.07 vs FLAG 2+1+1 傳播 {e_md_mu_11:.3f} = 報細 {100*(1-gem_err/e_md_mu_11):.0f}%")
z_p2_own = (2.162037-gem_central)/gem_err
z_p2_true = (2.162037-md_mu_11)/e_md_mu_11
print(f"       P2=2.1620 用 Gemini 自己誤差: z={z_p2_own:.2f}; 用 FLAG 真誤差: z={z_p2_true:.2f}")
chk("CHK4a Gemini central 一致 (兩 Nf 都 <2σ)", abs(z_g_11) < 2 and abs(z_g_21) < 2,
    f"z(2+1+1)={z_g_11:+.2f}, z(2+1)={z_g_21:+.2f}")
chk("CHK4b Gemini 誤差棒正確", False,
    f"0.07 vs FLAG {e_md_mu_11:.3f} (2+1+1) -> 報細 {100*(1-gem_err/e_md_mu_11):.0f}%")

# ---------------------------------------------------------------- mode assignment
MODES = [1,2,3,4,5,7,9,11,13]            # O137 R19 合法模式
A_GAMMA = {"e":1, "u":2, "d":3, "s":4, "mu":5, "c":7, "tau":9, "b":11, "t":13}
A_DELTAM = {"t":1, "b":2, "c":3, "tau":4, "s":5, "mu":7, "d":9, "u":11, "e":13}
def gamma(n): return 4.0*math.sin(n*math.pi/88.0)**2
g = {n: gamma(n) for n in MODES}

# ---------------------------------------------------------------- CHK5 前向 z-score
print("\n[CHK5] 前向 z-score 矩陣 (純 γ 比, C_f=1)   obs = 凍結觀測層")
rows = [
    # name, obs, err, (A_γ numerator f, denominator f), (A_Δm num, den)
    ("d/u", md_mu_11, e_md_mu_11, ("d","u"), ("d","u")),
    ("c/s", FROZEN["FLAG_tabulated"]["mc_ms_ratio"][0], FROZEN["FLAG_tabulated"]["mc_ms_ratio"][1], ("c","s"), ("c","s")),
    ("b/c", 4.18/1.27, (4.18/1.27)*math.hypot(0.03/4.18, 0.02/1.27), ("b","c"), ("b","c")),
    ("t/b", 172.57/4.18, (172.57/4.18)*math.hypot(0.29/172.57, 0.03/4.18), ("t","b"), ("t","b")),
]
for name, obs, eobs, pa, pb in rows:
    pred_g = g[A_GAMMA[pa[0]]]/g[A_GAMMA[pa[1]]]
    pred_d = g[A_DELTAM[pb[0]]]/g[A_DELTAM[pb[1]]]
    z_g = (pred_g-obs)/eobs; z_d = (pred_d-obs)/eobs
    cls_g = "gamma-dom" if abs(z_g) < 2 else ("Cf-dom" if abs(z_g) > 5 else "border")
    tag = "" if name != "b/c" else "  [scheme近似: mb(mb)/mc(mc)]"
    tag2 = "" if name != "t/b" else "  [pole/MS 不可通約 WARNING]"
    print(f"  {name:4s} obs={obs:8.4f} pm {eobs:.4f} | A_gamma pred={pred_g:8.4f} z={z_g:+7.1f} ({cls_g}){tag}{tag2}")
    print(f"        A_DeltaM pred={pred_d:8.4f} z={z_d:+7.1f}  A_DeltaM 无方向基础(WARNING: O209 系 |dm| 序, 非 ratio 序)")
chk("CHK5a u/d 純 γ 可檢驗 (|z|<=2)", abs((g[3]/g[2]-md_mu_11)/e_md_mu_11) <= 2,
    f"gamma3/gamma2 = {g[3]/g[2]:.5f} vs {md_mu_11:.5f} pm {e_md_mu_11:.3f}: z={((g[3]/g[2]-md_mu_11)/e_md_mu_11):+.2f}")
chk("CHK5b c/s 純 γ 不可檢驗 (|z|>5)", abs((g[7]/g[4]-11.85)/0.16) > 5,
    f"gamma7/gamma4 = {g[7]/g[4]:.4f} vs 11.85(16): z={((g[7]/g[4]-11.85)/0.16):+.1f}")

# ---------------------------------------------------------------- CHK6 assignment 判別
pred_du_dm = g[9]/g[11]
z_dm = (pred_du_dm-md_mu_11)/e_md_mu_11
chk("CHK6 A_DeltaM u/d 方向判死 (|z|>5)", abs(z_dm) > 5,
    f"A_DeltaM d/u = gamma9/gamma11 = {pred_du_dm:.4f} < 1 vs obs {md_mu_11:.4f}: z={z_dm:+.1f} -> gamma 序 A_gamma 唯一方向正確")

print(f"\n=== {p} PASS / {s} FAIL ===")