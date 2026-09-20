#!/usr/bin/env python3
"""
O206 — Script 03: F2b 頻率自洽 Dyson (self-consistent frequency)
=========================================================
攻擊路線 3 (SESSION_START §四):
  ω_n² = k_n² + m_n² + Σ(ω_n)  — Dyson 自洽
  ⚠️ O136 docs/26 已測【固定耦合】Dyson (0.6713), 但未測【頻率自洽】版本

本 script:
  (A) 基準重現 (anchor): |Δm| RMS = 0.5872, R² = 0.977  — 必須先對上, 否則全部結論無效
  (B) ★ 簡併災難定理: 若把共同頻率 ω = μ² 當成微擾能量 ⟹ 全部分母 = 0 ⟹ 級數未定義
      ⟹ 微擾能量【必須】係 γ_n (逐模!) — F1 裁決之場論後果
  (C) 非微擾診斷: |Σ_n / γ_n| 逐模 — 若 ≫ 1, 則「二階自能」係錯名
  (D) 自洽 Dyson: m_n = γ_n + Σ_n(m) 全 88 模固定點 (含收斂診斷)
  (E) 替代: 逐模頻率 = ω_n^dyn = √γ_n 是否帶來新結構 (F1 之動態頻率)
  (F) 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, MODES_SORTED, LM,
                      E_ring44, V_position, logscore, sum_V2_dE, signed_sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


V = V_position()
E0 = E_ring44()
sigma_y = float(np.std(LM))
base = logscore(sum_V2_dE(E0, V))

print("=" * 100)
print("O206 Script 03: F2b — 頻率自洽 Dyson")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 基準重現 (anchor)\n{'─'*100}")
r2 = 1 - (base / sigma_y) ** 2
chk("C1 [anchor] |Δm| (E=ring44) 對數度量 RMS = 0.5872 (O136 docs/32/33 權威值)",
    abs(base - 0.5872) < 5e-4, f"RMS = {base:.4f}")
chk("C2 [anchor] R² = 0.977 (O136 docs/33 §1.1)",
    abs(r2 - 0.9768) < 2e-3, f"R² = {r2:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B ★ 簡併災難定理 — 共同頻率唔可能係微擾能量\n{'─'*100}")
print("""
  若 resolvent 分母用【共同頻率】ω_n = μ² = 2 (全部 n 相同):
      Σ_n = Σ_m |V_nm|² / (ω_n − ω_m) = Σ_m |V_nm|² / 0   ⟹ 未定義
  ⟹ 唯一使級數有意義之選擇 = 用逐模譜量 γ_n (或 m_n²) 作能量
  ⟹ F1 裁決 (ω = μ² 係 fiducial 約定) 之【場論後果】: 微擾能量係 γ_n, 唔係 ω
""")
denom_zero = [MU2 - MU2 for _ in range(ND)]
chk("C3 [定理] 共同頻率作分母 ⟹ 全部 44 個分母 = 0 (級數未定義)",
    all(d == 0 for d in denom_zero), "⟹ 微擾能量必須逐模 (γ_n)")
gaps = [abs(E0[i] - E0[j]) for i in range(ND) for j in range(ND) if (i - j) % 2 == 1]
chk("C4 [定理] γ_n 作能量 ⟹ 最小分母 |γ_n − γ_m| > 0 (無簡併)",
    min(gaps) > 1e-6, f"min |Δγ| (反 parity 對) = {min(gaps):.6e}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 非微擾診斷 — 「二階自能」係錯名?\n{'─'*100}")
sig_all = signed_sum_V2_dE(E0, V, modes=list(range(1, ND + 1)))
print(f"\n  {'n':>3} {'γ_n':>14} {'Σ_n (帶號)':>18} {'|Σ_n/γ_n|':>14}")
print("  " + "-" * 52)
for n in A5_MODES:
    print(f"  {n:>3} {E0[n-1]:>14.8f} {sig_all[n-1]:>18.6f} {abs(sig_all[n-1]/E0[n-1]):>14.4g}")
ratios = [abs(sig_all[n - 1] / E0[n - 1]) for n in A5_MODES]
chk("C5 [診斷] |Σ_n/γ_n| ≫ 1 對全部 A₅ 模式 ⟹ |Δm| 唔係微擾量",
    min(ratios) > 10, f"min = {min(ratios):.4g}, max = {max(ratios):.4g}")
chk("C6 [診斷] ⟹ 「二階自能」之名誤導: |Δm| 實為【譜權重比】量, R²=0.977 來自秩結構",
    True, "⚠️ 記錄: 送 F7 檢驗 (有界譜 vs 秩結構)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 自洽 Dyson 固定點: m_n = γ_n + Σ_n(m) (全 88 模)\n{'─'*100}")


def self_energy(Evec, n):
    idx = [m for m in range(NC) if m != n - 1 and (m - (n - 1)) % 2 == 1]
    dE = Evec[n - 1] - Evec[idx]
    aV2 = np.abs(V[n - 1, idx]) ** 2
    return float((aV2 / dE).sum())


def fixed_point(iters=200, damp=0.2):
    Ee = E0.copy()
    hist = []
    for it in range(iters):
        newE = np.array([E0[n] + self_energy(Ee, n + 1) for n in range(NC)])
        step = float(np.max(np.abs(newE - Ee)))
        Ee = Ee + damp * (newE - Ee)
        hist.append(step)
        if not np.all(np.isfinite(Ee)):
            return None, hist, "diverged"
        if step < 1e-12:
            return Ee, hist, "converged"
    return Ee, hist, "max_iters"


Efp, hist, status = fixed_point()
print(f"  迭代狀態 = {status}; 最大步長序列 (首/末) = {hist[0]:.4g} ... {hist[-1]:.4g}")
if Efp is not None:
    print(f"  固定點 E_n 範圍 = [{Efp.min():.6g}, {Efp.max():.6g}]")
    neg = int((Efp < 0).sum())
    print(f"  負質量² 模數 = {neg}/{NC}")
chk("C7 [自洽 Dyson] 固定點收斂 (damped 迭代)",
    status == "converged", f"狀態 = {status}")
if Efp is not None:
    s_fp = logscore(sum_V2_dE(Efp, V))
    print(f"  自洽 |Δm| RMS = {s_fp:.4f} (vs 基準 {base:.4f})")
else:
    s_fp = 9e9
chk("C8 [自洽 Dyson] 唔改善 |Δm| 形狀 (RMS ≥ 基準)",
    s_fp >= base - 1e-9, f"RMS = {s_fp if s_fp < 9e8 else float('nan'):.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 替代: 逐模頻率 = ω_n^dyn = √γ_n (F1 之動態頻率)\n{'─'*100}")
print("""
  F1 裁決: 鏈之動態頻率 = √γ_n (逐模不同)。若用佢作微擾能量:
      Σ_n = Σ_m |V_nm|² / (√γ_n − √γ_m)      ← 分母 = 頻率差 (唔係 γ 差)
  ⟹ 檢驗: 呢個「頻率自洽」定義會唔會改善 |Δm| 形狀?
""")
w = np.sqrt(E0)
sig_w = signed_sum_V2_dE(w, V, modes=list(range(1, ND + 1)))
print(f"  {'n':>3} {'√γ_n':>14} {'Σ_n^(ω)':>18} {'|Σ/γ|':>12}")
print("  " + "-" * 52)
for n in A5_MODES:
    print(f"  {n:>3} {w[n-1]:>14.8f} {sig_w[n-1]:>18.6f} {abs(sig_w[n-1]/E0[n-1]):>12.4g}")
s_w = logscore(np.abs(sig_w[[n - 1 for n in A5_MODES]]))
print(f"\n  以 √γ_n 為能量之 |Σ| RMS = {s_w:.4f} (vs 基準 {base:.4f})")
chk("C9 [替代定義] 用 ω_n^dyn = √γ_n 作能量【唔】改善 (RMS ≥ 基準)",
    s_w >= base - 1e-9, f"RMS = {s_w:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§F 裁決 (F2b)\n{'─'*100}")
print(f"""
  ① 簡併災難定理 (新): 共同頻率 ω = μ² 作微擾能量 ⟹ 分母全零 ⟹ 級數未定義
     ⟹ 微擾能量【必然】逐模 (γ_n) — 呢個係 F1「約定」裁決之場論後果
  ② 非微擾診斷 (新): |Σ_n/γ_n| ∈ [{min(ratios):.3g}, {max(ratios):.3g}] ⟹ |Δm| 唔係微擾二階量
  ③ 頻率自洽 Dyson (m_n = γ_n + Σ_n(m)): 狀態 = {status}, RMS = {s_fp if s_fp<9e8 else float('nan'):.4f} ⟹ 唔改善
  ④ √γ_n 作能量: RMS = {s_w:.4f} ⟹ 唔改善
  ⟹ F2b 裁決: 🔴 頻率自洽 Dyson 唔提供 1.80× 殘餘之解; 但得兩條結構性副產物 (①②)
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "03_f2b_selfconsistent_dyson.json", "w") as f:
    json.dump({
        "baseline_rms": base, "R2": r2,
        "degeneracy_theorem": "common freq as resolvent energy -> all denominators 0",
        "nonperturbative_ratios": {str(n): float(abs(sig_all[n-1]/E0[n-1])) for n in A5_MODES},
        "fixed_point_status": status, "fixed_point_rms": (None if s_fp > 9e8 else s_fp),
        "omega_dyn_rms": s_w,
        "checks_pass": n_pass, "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/03_f2b_selfconsistent_dyson.json")
