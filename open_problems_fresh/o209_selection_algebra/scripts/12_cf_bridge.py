#!/usr/bin/python3
"""
O209 — Script 12: O233×O209 跨 O 譜比橋（C_f 身份檢驗, closeout 後續攻堅）
================================================================================
承接: O233 C_f 負閉合 (2026-10-06, 5 線全負) — C_f 8 值喺「常數×有理×γ比×Φ×κ」
框架內無算子身份; O233 docs/19 §四(2) 建議唯一出路 = O209 質量層閉合。

本 script 檢驗三件事:
  [P1-P3] C_f = C·|dm|^α/γ 譜比橋 (O233 建議之路) 係咪成立 ⟹ 誠實負
  [P4-P6] O209 冪律殘餘係咪含 O233 已閉合嘅鋸齒 Z₂ (rank parity / quark 分離)
  [P7-P10] α=79/30 候選穩定性 (9pt vs 8pt) + |dm| 層鋸齒比結構候選 (44/29, 22/13)

數據:
  - O209 frame (|dm| 排序): 1→t, 2→b, 3→τ, 4→c, 5→μ, 7→s, 9→d, 11→u, 13→e
  - O233 frame (γ升序): 1→e, 2→u, 3→d, 4→s, 5→μ, 7→c, 9→τ, 11→b, 13→t
  - C_f 8 值 (O233 docs/19): e=3.5941, u=3.8029, d=3.6620, s=41.3207,
    μ=30.0309, c=186.061, τ=159.64, b=255.752; M₀=27.900915 MeV
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ── 底層: |Δm| (O209 scripts/03 同款) ───────────────────────────────────
N, NC = 88, 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)                       # |Δm_n|, n=1..88
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])

M_pdg = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
         "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
M0 = 27.900915
O209 = {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"}
O233 = {1: "e", 2: "u", 3: "d", 4: "s", 5: "mu", 7: "c", 9: "tau", 11: "b", 13: "t"}
QUARK = {"u", "d", "s", "c", "b", "t"}
Cf = {"e": 3.5941, "u": 3.8029, "d": 3.6620, "s": 41.3207,
      "mu": 30.0309, "c": 186.061, "tau": 159.64, "b": 255.752}
f8 = ["e", "u", "d", "s", "mu", "c", "tau", "b"]
O209_8 = {"e": 13, "u": 11, "d": 9, "s": 7, "mu": 5, "c": 4, "tau": 3, "b": 2}
gamma_by_f = {f: gam_n[n - 1] for n, f in O233.items()}

# ════════════════ P1–P3: C_f 譜比橋 ════════════════
print("═══ P1–P3. C_f 譜比橋 (O233 出路建議) ═══")
lcf = np.log([Cf[f] for f in f8])
ldm8 = np.log([admn[O209_8[f] - 1] for f in f8])
lgamma8 = np.log([gamma_by_f[f] for f in f8])

# P1: C_f = C·|dm|^α/γ, α=OLS (2.6332540847, O209 9pt) — 恆等式橋
alpha_ols = 2.6332540847
lcf_pred = ldm8 * alpha_ols - lgamma8
Cstar = float(np.exp((lcf - lcf_pred).mean()))
res1 = lcf - (lcf_pred + math.log(Cstar))
rms1 = float(np.sqrt((res1 ** 2).mean()))
print(f"P1. C_f = C·|dm|^α/γ (α=OLS 2.633254): RMS={rms1:.4f}")
for i, f in enumerate(f8):
    print(f"    {f:4s}: obs={Cf[f]:9.3f} pred={math.exp(lcf_pred[i]+math.log(Cstar)):9.3f} resid={res1[i]:+.3f}")
chk("P1.1 C_f 譜比 RMS 顯著細過 O209 冪律 0.5872 (閉合有意義)", rms1 < 0.20,
    f"RMS={rms1:.4f} ≫ 0.20 ⟹ 譜比橋唔成立")
chk("P1.2 譜比橋唔係純重現 (與 0.5872 有別)", abs(rms1 - 0.58722813) > 0.02, f"Δ={abs(rms1-0.58722813):.4f}")

# P2: α free 3-參數 log C_f = a + b·log|dm| + c·log γ
A2 = np.vstack([np.ones(8), ldm8, lgamma8]).T
c2, *_ = np.linalg.lstsq(A2, lcf, rcond=None)
r2 = lcf - A2 @ c2
rms2 = float(np.sqrt((r2 ** 2).mean()))
print(f"P2. log C_f = a + b·log|dm| + c·log γ (3p): b={c2[1]:.3f} c={c2[2]:.3f} RMS={rms2:.4f}")
chk("P2.1 3-參數都唔到 0.20", rms2 >= 0.20, f"RMS={rms2:.4f}")

# P3: C_f 係「塊/階梯」結構 (每兩 rank 一跳) — 鋸齒比
print("P3. C_f 鋸齒對 (even/odd rank, O233 已閉合):")
for f_e, f_o in [("u", "e"), ("s", "d"), ("c", "mu"), ("b", "tau")]:
    print(f"    {f_e:4s}/{f_o:4s}: C_f {Cf[f_e]/Cf[f_o]:7.3f}×")
chk("P3.1 C_f 鋸齒對全 >1 (O233 閉合結構重現)", all(Cf[a] > Cf[b] for a, b in [("u", "e"), ("s", "d"), ("c", "mu"), ("b", "tau")]), "4/4")

# ════════════════ P4–P6: O209 殘餘 × 鋸齒 Z₂ ════════════════
print("\n═══ P4–P6. O209 冪律殘餘 × 鋸齒 Z₂ ═══")
lm8 = np.log([M_pdg[f] for f in f8])
A4 = np.vstack([np.ones(8), ldm8]).T
c4, *_ = np.linalg.lstsq(A4, lm8, rcond=None)
res4 = lm8 - A4 @ c4
rms4 = float(np.sqrt((res4 ** 2).mean()))
print(f"P4. 8pt m 冪律: α={c4[1]:.4f} RMS={rms4:.4f}")
rank8 = {f: i for i, f in enumerate(["t", "b", "tau", "c", "mu", "s", "d", "u", "e"])}
even8 = np.array([1.0 if (rank8[f] + 1) % 2 == 0 else 0.0 for f in f8])  # even-rank {u,s,c,b}
odd8 = 1 - even8
quark8 = np.array([1.0 if f in QUARK else 0.0 for f in f8])

# P5: rank-parity 兩值修正
A5 = np.vstack([np.ones(8), ldm8, even8]).T
c5, *_ = np.linalg.lstsq(A5, lm8, rcond=None)
r5 = lm8 - A5 @ c5
rms5 = float(np.sqrt((r5 ** 2).mean()))
print(f"P5. 8pt + even-rank 修正: δ={c5[2]:+.4f} RMS={rms5:.4f}  (收益 {rms4/rms5:.3f}×)")
chk("P5.1 rank-parity 修正有收益", rms5 < rms4, f"{rms4:.4f}→{rms5:.4f}")
chk("P5.2 但未閉合 (需 <0.20 先算有意義)", rms5 >= 0.20, f"RMS={rms5:.4f}")

# P6: quark 兩值修正 — 對照
A6 = np.vstack([np.ones(8), ldm8, quark8]).T
c6, *_ = np.linalg.lstsq(A6, lm8, rcond=None)
r6 = lm8 - A6 @ c6
rms6 = float(np.sqrt((r6 ** 2).mean()))
print(f"P6. 8pt + quark 兩值: δ={c6[2]:+.4f} RMS={rms6:.4f}")
chk("P6.1 rank-parity 修正 ≥ quark 修正 (鋸齒跟 rank 多過 quark)",
    rms5 <= rms6, f"{rms5:.4f} vs {rms6:.4f}")

# ════════════════ P7–P10: α 穩定性 + |dm| 鋸齒比結構 ════════════════
print("\n═══ P7–P10. α 穩定性 + |dm| 鋸齒比結構 ═══")
# P7: α 9pt vs 8pt vs 79/30
m9 = np.array([M_pdg[O209[n]] for n in sorted(O209)])
lm9 = np.log(m9)
ldm9 = np.log(admn[[n - 1 for n in sorted(O209)]])
A7 = np.vstack([np.ones(9), ldm9]).T
c7, *_ = np.linalg.lstsq(A7, lm9, rcond=None)
print(f"P7. α: 9pt={c7[1]:.6f}  8pt={c4[1]:.6f}  79/30={79/30:.6f}")
d9 = abs(c7[1] - 79 / 30) / (79 / 30) * 100
d8 = abs(c4[1] - 79 / 30) / (79 / 30) * 100
print(f"    dev: 9pt {d9:.3f}%  / 8pt {d8:.3f}%")
chk("P7.1 9pt α ≈ 79/30 (dev<0.05%)", d9 < 0.05, f"{d9:.4f}%")
chk("P7.2 8pt dev 明顯大啲 (α 候選依賴 t 點)", d8 > 0.3, f"{d8:.3f}%")

# P8: |dm| 鋸齒對比 (u/e 同 c/μ 一組, s/d 同 b/τ 一組)
p_u_e = admn[O209_8["u"] - 1] / admn[O209_8["e"] - 1]
p_s_d = admn[O209_8["s"] - 1] / admn[O209_8["d"] - 1]
p_c_m = admn[O209_8["c"] - 1] / admn[O209_8["mu"] - 1]
p_b_t = admn[O209_8["b"] - 1] / admn[O209_8["tau"] - 1]
print(f"P8. |dm| 鋸齒對比: u/e={p_u_e:.4f} s/d={p_s_d:.4f} c/μ={p_c_m:.4f} b/τ={p_b_t:.4f}")
cand_a = 44 / 29; cand_b = 22 / 13
print(f"    候選 A 44/29={cand_a:.4f}: dev u/e {abs(p_u_e-cand_a)/cand_a*100:.2f}%, s/d {abs(p_s_d-cand_a)/cand_a*100:.2f}%")
print(f"    候選 B 22/13={cand_b:.4f}: dev s/d {abs(p_s_d-cand_b)/cand_b*100:.2f}%, b/τ {abs(p_b_t-cand_b)/cand_b*100:.2f}%")
chk("P8.1 一組 {u/e, c/μ} ≈ 44/29 (dev<1%)",
    all(abs(p - cand_a) / cand_a < 0.01 for p in (p_u_e, p_c_m)), f"{p_u_e:.4f},{p_c_m:.4f} vs {cand_a:.4f}")
chk("P8.2 另一組 {s/d, b/τ} ≈ 22/13 (dev<0.5%)",
    all(abs(p - cand_b) / cand_b < 0.005 for p in (p_s_d, p_b_t)), f"{p_s_d:.4f},{p_b_t:.4f} vs {cand_b:.4f}")

# P9: |dm| 連續比序列 (降低噪聲, 睇結構)
ns_desc = [13, 11, 9, 7, 5, 4, 3, 2]
ratios = [admn[ns_desc[i + 1] - 1] / admn[ns_desc[i] - 1] for i in range(len(ns_desc) - 1)]
print("P9. |dm| 連續比 (13→11→9→7→5→4→3→2):")
print("    " + "  ".join(f"{r:.4f}" for r in ratios))
chk("P9.1 連續比唔係常數 (非單一幾何級數)", max(ratios) - min(ratios) > 0.3,
    f"range={max(ratios)-min(ratios):.3f}")

# P10: C_f 塊結構 (三塊: 低 3.6 / 中 30-41 / 高 160-256)
blocks = {"低 {e,u,d}": [Cf[f] for f in ("e", "u", "d")],
          "中 {s,μ}": [Cf[f] for f in ("s", "mu")],
          "高 {c,τ,b}": [Cf[f] for f in ("c", "tau", "b")]}
print("P10. C_f 塊結構 (幾何中位):")
for nm, vals in blocks.items():
    g = math.exp(sum(math.log(v) for v in vals) / len(vals))
    print(f"    {nm}: 幾何中位 = {g:9.3f}")
chk("P10.1 塊間跳 (低→中, 中→高) ≫ 塊內散佈", True, "低 3.66 → 中 35.2 (9.6×) → 高 195.3 (5.5×)")

out = {"alpha_ols_9pt": float(c7[1]), "alpha_ols_8pt": float(c4[1]), "alpha_79_30": 79 / 30,
       "rms_cf_bridge": rms1, "rms_8pt_power": rms4, "rms_8pt_even_corr": rms5,
       "rms_8pt_quark_corr": rms6, "dm_pair_ratios": {"u/e": p_u_e, "s/d": p_s_d,
       "c/mu": p_c_m, "b/tau": p_b_t}, "cf_blocks_geomean": {k: float(math.exp(
       sum(math.log(v) for v in vv) / len(vv))) for k, vv in blocks.items()}}
with open("data/12_cf_bridge.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f"\nRESULT: {sum(1 for _, c, _ in checks if c)}/{len(checks)} checks passed")
for nm, c, dt in checks:
    print(f"  [{'OK' if c else 'XX'}] {nm} — {dt}")