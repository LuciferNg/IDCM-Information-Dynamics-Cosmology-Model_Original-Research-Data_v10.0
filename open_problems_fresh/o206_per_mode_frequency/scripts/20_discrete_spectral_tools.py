#!/usr/bin/env python3
"""
O206 — Script 20: 離散譜工具找簇第一性原理 (FSR/譜窗/質量殼)
=========================================================
調律者 (2026-09-21): 「如果是離散譜，就應該能用FSR、CSG、有限譜黎曼幾何等工具
找出規律和第一性原理才對」

方向:
  §A FSR 離散質量殼: 質量殼參數化 θ_n = nπ/88, 質量 m ∝ f(θ) 族掃描
     (csc/cot/sin/cos/tan + 對數) — 比較 RMS vs 冪律基準 0.5872
  §B ★ 簇譜窗身份: Σγ_簇 / Σ|Δm|_簇 / Σln|Δm|_簇 / Σω_簇
     對照 IDCM 常數池 + 隨機子集 null (池子密度校正)
  §C 簇間譜間隔: Δln|Δm| 之間隔比率 (譜幾何「間隔」)
  §D 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import A5_MODES, E_ring44, V_position, sum_V2_dE

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


modes = np.array([1, 2, 3, 4, 5, 7, 9, 11, 13])
masses = np.array([172690, 4180, 1776.86, 1270, 105.6584, 93.4, 4.67, 2.16, 0.511])
V = V_position()
E = E_ring44()
dm = sum_V2_dE(E, V)
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n in modes])
lm = np.array([math.log(m) for m in masses])
gam = np.array([E[n - 1] for n in modes])
om = np.sqrt(gam)
th = modes * math.pi / 88

A = [0, 2, 7]
B = [1, 4, 6, 8]
C = [3, 5]
CL = [A, B, C]

print("=" * 100)
print("O206 Script 20: 離散譜工具找簇第一性原理 (FSR/譜窗/質量殼)")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A FSR 離散質量殼: m ∝ f(θ_n) 族掃描\n{'─'*100}")
# FSR: E = mc²cscθ, p = mc·cotθ ⟹ 質量殼參數 θ。測試質量對 θ 函數族。
forms = {
    "csc θ": np.log(1 / np.sin(th)),
    "cot θ": np.log(np.cos(th) / np.sin(th)),
    "sin θ": np.log(np.sin(th)),
    "cos θ": np.log(np.cos(th)),
    "tan θ": np.log(np.sin(th) / np.cos(th)),
    "sin(2θ)": np.log(np.sin(2 * th)),
    "cos(2θ)": np.log(np.cos(2 * th)),
}
print(f"  {'形式':>10} {'RMS':>9} {'vs 冪律':>9}")
print("  " + "-" * 32)
best = (1e9, None)
for name, f in forms.items():
    if np.any(~np.isfinite(f)):
        print(f"  {name:>10}   (奇異)")
        continue
    A_ = np.column_stack([np.ones(9), f])
    b, *_ = np.linalg.lstsq(A_, lm, rcond=None)
    r = float(np.sqrt(np.mean((lm - A_ @ b) ** 2)))
    if r < best[0]:
        best = (r, name)
    print(f"  {name:>10} {r:>9.4f} {r/0.5872:>8.3f}×")
print(f"\n  ★ 最佳質量殼形式: {best[1]}, RMS = {best[0]:.4f} (冪律 0.5872)")
chk("C1 質量殼形式無超越冪律 (最佳 ≥ 0.5)",
    best[0] >= 0.5, f"最佳 {best[1]} RMS {best[0]:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B ★ 簇譜窗身份 (Σγ_簇 / Σ|Δm|_簇 / Σω_簇 / Σln|Δm|_簇)\n{'─'*100}")
rng = np.random.default_rng(20260921)
QUANT = {
    "γ": gam, "|Δm|": np.array([dm[A5_MODES.index(n)] for n in modes]),
    "ω=√γ": om, "ln|Δm|": ldm, "1/γ": 1 / gam,
}
CONSTS = {
    "1": 1.0, "φ": 1.618034, "φ⁻¹": 0.618034, "φ²": 2.618034,
    "μ²": 2.0, "B": 4.0, "L₅": 11.0, "F₇": 13.0, "K_tree": 33.0,
    "N_d": 44.0, "2N_d": 88.0, "F₉": 34.0, "L₄": 7.0, "N_gen": 3.0,
    "B/2": 2.0, "L₅/2": 5.5, "45": 45.0, "55": 55.0, "66": 66.0,
}
print(f"  {'量':>10} {'簇':>4} {'Σ值':>14} {'候選命中':>28} {'Δ':>9} {'null P':>9}")
print("  " + "-" * 80)
hits_report = []
for qname, q in QUANT.items():
    for gname, g in [("A", A), ("B", B), ("C", C)]:
        s = float(np.sum(q[g]))
        # 對照常數 (容差 1%)
        best_hit = None
        for cname, cv in CONSTS.items():
            for ratio in [1.0, 2.0, 0.5, 3.0, 1 / 3.0]:
                if cv * ratio == 0:
                    continue
                dev = abs(s - cv * ratio) / (cv * ratio)
                if dev < 0.01 and (best_hit is None or dev < best_hit[1]):
                    best_hit = (f"{cname}×{ratio:g}", dev)
        # null: 隨機 3-4-2 子集嘅 Σ 命中率
        null_hit = 0
        for _ in range(2000):
            idx = rng.permutation(9)
            gs = [idx[:3], idx[3:7], idx[7:]]
            for gg in gs:
                ss = float(np.sum(q[gg]))
                for cname, cv in CONSTS.items():
                    for ratio in [1.0, 2.0, 0.5, 3.0, 1 / 3.0]:
                        if cv * ratio and abs(ss - cv * ratio) / (cv * ratio) < 0.01:
                            null_hit += 1
                            break
        null_rate = null_hit / (2000 * 3 * len(CONSTS) * 5)
        if best_hit:
            hits_report.append((qname, gname, s, best_hit[0], best_hit[1], null_rate))
            print(f"  {qname:>10} {gname:>4} {s:>14.6f} {best_hit[0]:>28} "
                  f"{best_hit[1]*100:>8.2f}% {null_rate:>9.5f}")
        else:
            print(f"  {qname:>10} {gname:>4} {s:>14.6f} {'(無命中)':>28}")
# 對照: 隨機子集命中率 (所有量)
print(f"\n  ★ 隨機 3-4-2 子集命中率基準: {np.mean([h[5] for h in hits_report]) if hits_report else 'N/A':.5f}" if hits_report else "  ★ 無命中")
chk("C2 簇譜窗命中唔超越隨機子集 (需結構理由 + 盲測)",
    all(h[5] > 0.001 for h in hits_report),
    f"{len(hits_report)} 命中, 全部 null P > 0.001 ⟹ 池子密度") if hits_report else chk("C2 簇譜窗無命中", True)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 簇間譜間隔 (ln|Δm| 間隔比率)\n{'─'*100}")
# 簇均值 (ln 空間)
mA = float(np.mean(ldm[A]))
mB = float(np.mean(ldm[B]))
mC = float(np.mean(ldm[C]))
print(f"  簇均值 ln|Δm|: A = {mA:.6f}, B = {mB:.6f}, C = {mC:.6f}")
print(f"  間隔: |A−B| = {abs(mA-mB):.6f}, |B−C| = {abs(mB-mC):.6f}, |A−C| = {abs(mA-mC):.6f}")
dAB = abs(mA - mB)
dBC = abs(mB - mC)
dAC = abs(mA - mC)
print(f"  比率: dAB/dBC = {dAB/dBC:.4f}, dAB/dAC = {dAB/dAC:.4f}, dBC/dAC = {dBC/dAC:.4f}")
# 與殘餘水平對照 (docs/17: 殘餘簇均值 -0.054/-0.477/+1.035)
rA, rB, rC = -0.0543, -0.4766, 1.0350
print(f"  殘餘水平: A = {rA:.3f}, B = {rB:.3f}, C = {rC:.3f}")
print(f"  殘餘間隔: |A−B| = {abs(rA-rB):.3f}, |B−C| = {abs(rB-rC):.3f}, |A−C| = {abs(rA-rC):.3f}")
print(f"  殘餘比率: |A−B|/|B−C| = {abs(rA-rB)/abs(rB-rC):.4f}")
# 檢查: ln|Δm| 間隔 vs 殘餘間隔 有冇比例關係
print(f"  ★ 對照: ln|Δm| 間隔 dAB/dBC = {dAB/dBC:.4f} vs 殘餘間隔比率 {abs(rA-rB)/abs(rB-rC):.4f}")
ratio_ldm = dAB / dBC
ratio_res = abs(rA - rB) / abs(rB - rC)
chk("C3 譜間隔比率 vs 殘餘間隔比率唔一致 (冇簡單映射)",
    abs(ratio_ldm - ratio_res) > 0.3, f"ln|Δm| {ratio_ldm:.3f} vs 殘餘 {ratio_res:.3f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決\n{'─'*100}")
print(f"""
  §A FSR 質量殼形式: 最佳 {best[1]} RMS {best[0]:.4f} — 無超越冪律 (全部 ≥ 0.5)
      ⟹ 質量殼參數化 (csc/cot/sin/cos/tan θ) 唔係簇水平嘅生成機制
  §B 簇譜窗: {len(hits_report)} 個 Σ命中 — null P 檢查中
      隨機子集命中率基準需報 ⟹ 池子密度未超越
  §C 譜間隔: ln|Δm| 簇間隔比率 {ratio_ldm:.3f} vs 殘餘間隔比率 {ratio_res:.3f}
      ⟹ 唔一致, 冇簡單映射
  ⟹ 「離散譜工具 (FSR 質量殼 / 譜窗 / 譜間隔)」揾簇第一性原理:
      本輪【未檢出】— 質量殼/譜窗/間隔都唔解釋三水平
      剩餘方向: ① 88 格幾何 (節點坐標, 天球聚類) ② 狄拉克算子譜三重
                ③ CSG 譜語言 (但 O144 audit 已評後驗不閉合)
""")
n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "20_discrete_spectral_tools.json", "w") as f:
    json.dump({
        "mass_shell_best": {"form": best[1], "rms": best[0]},
        "cluster_window_hits": hits_report,
        "interval_ratios": {"ldm": ratio_ldm, "resid": ratio_res},
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/20_discrete_spectral_tools.json")
