#!/usr/bin/env python3
"""
O206 — Script 01: F1 存在性審計
=========================================================
問題 (SESSION_START §F1):
  O169 docs/13 確立鏈嘅 44 個模態係【共同頻率】ω_n = μ² = 2
  ⟹ 質量只能係投影/幾何副產品。
  問: 呢個共同頻率係【結構強制】抑或【約定】?

審計設計 (SESSION_START 指定 5 個必做子項):
  1. 44-site D-D 鏈 Laplacian 本徵值 → ω_n 是否全部相同
  2. Z₂ 扇區分解 (奇/偶) 下 ω 之行為
  3. 邊界條件掃描 (D-D / D-N / N-N / 週期)
  4. 歸一化慣例掃描 (44-鏈 / 88-鏈 / 176-鏈)
  5. 判定: 「約定」⟹ 問題降級為參數化; 「強制」⟹ 需新機制

★ 紀律: 每個 check 名必須報告【慣例】; 度量用對數值 (O136 判準③)
★ 零新常數; 唔准改上游任何檔案
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import mp, mpf, pi, sin, cos, sqrt

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, MU4, B_, E_ring44, E_dd88, E_o159_88,
                      V_position, logscore, sum_V2_dE, LM)

mp.dps = 50
OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)

checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


print("=" * 100)
print("O206 Script 01: F1 存在性審計 — ω = μ² 係結構強制抑或約定?")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§一 譜定義與慣例掃描 (mpmath dps=50, 精確代數)\n{'─'*100}")

# [慣例 = 44-site ring]
dev_a = max(abs(4 * sin(pi * n / 88) ** 2 - (2 - 2 * cos(pi * n / 44))) for n in range(1, ND + 1))
chk("C1 [慣例=44-site ring] γ_n = 4sin²(πn/88) ≡ 2−2cos(πn/44), n=1..44",
    dev_a < mpf('1e-45'), f"max dev = {mp.nstr(dev_a, 3)}")

S44 = sum(4 * sin(pi * n / 88) ** 2 for n in range(1, ND + 1))
chk("C2 [慣例=44-site ring] Σγ_{1..44} = 90 = 2N_d + μ²",
    abs(S44 - 90) < mpf('1e-45'), f"Σγ = {mp.nstr(S44, 25)}")

g44_ring = 4 * sin(pi * 44 / 88) ** 2
chk("C3 [慣例=44-site ring] γ_44 = 4 = μ⁴ = γ_max ⟹ √γ_max = μ² = 2",
    abs(g44_ring - 4) < mpf('1e-45'), f"γ_44 = {mp.nstr(g44_ring, 25)}")

# [慣例 = 88-site O159 半格]
dev_b = max(abs(abs(1 - mp.e ** (1j * pi * k / 88)) ** 2 - 4 * sin(pi * k / 176) ** 2)
            for k in range(1, NC + 1))
chk("C4 [慣例=88-site O159] γ_k = |1−e^{ikπ/88}|² ≡ 4sin²(kπ/176), k=1..88",
    dev_b < mpf('1e-45'), f"max dev = {mp.nstr(dev_b, 3)}")

g44_o159 = 4 * sin(pi * 44 / 176) ** 2
chk("C5 [慣例=88-site O159] γ_44 = 2 = μ² (中點模!) ⟹ μ² = γ_44 (O159 三合一)",
    abs(g44_o159 - 2) < mpf('1e-45'), f"γ_44 = {mp.nstr(g44_o159, 25)}")

S88 = sum(2 - 2 * cos(pi * k / 88) for k in range(1, NC + 1))
chk("C6 [慣例=88-site O159] Σγ_{1..88} = 178 = 2F₁₁",
    abs(S88 - 178) < mpf('1e-45'), f"Σγ = {mp.nstr(S88, 25)}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§二 邊界條件掃描 (BC scan) — μ² 喺邊個慣例下出現?\n{'─'*100}")

N = NC


def lam_dd():
    return np.sort(np.linalg.eigvalsh(2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)))


def lam_dn():
    L = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
    L[-1, -1] = 1.0
    return np.sort(np.linalg.eigvalsh(L))


def lam_nn():
    L = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
    L[0, 0] = 1.0
    L[-1, -1] = 1.0
    return np.sort(np.linalg.eigvalsh(L))


def lam_ring():
    L = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
    L[0, -1] = -1.0
    L[-1, 0] = -1.0
    return np.sort(np.linalg.eigvalsh(L))


BC = {"D-D": lam_dd(), "D-N": lam_dn(), "N-N": lam_nn(), "ring(週期)": lam_ring()}
print(f"\n  {'BC':>10} {'λ_max':>14} {'√λ_max':>12} {'λ_44(升序第44)':>16} {'√λ_max = μ²?':>14}")
print("  " + "-" * 70)
bc_rows = {}
for k, lam in BC.items():
    lmax = float(lam[-1])
    l44 = float(lam[ND - 1])
    bc_rows[k] = {"lam_max": lmax, "sqrt_lam_max": math.sqrt(lmax), "lam_44": l44}
    print(f"  {k:>10} {lmax:>14.10f} {math.sqrt(lmax):>12.8f} {l44:>16.10f} "
          f"{'YES' if abs(math.sqrt(lmax) - MU2) < 1e-12 else 'no':>14}")

chk("C7 [BC=ring] √λ_max = 2 = μ² EXACT (λ_max = 4 = μ⁴)",
    abs(math.sqrt(float(BC["ring(週期)"][-1])) - MU2) < 1e-12,
    f"√λ_max = {math.sqrt(float(BC['ring(週期)'][-1])):.12f}")
chk("C8 [BC=D-D] √λ_max = μ² 只到 0.03% (唔係 EXACT) ⟹ 值 4 係 ring 特有",
    abs(math.sqrt(float(BC["D-D"][-1])) - MU2) > 1e-4,
    f"√λ_max = {math.sqrt(float(BC['D-D'][-1])):.10f}, dev = "
    f"{abs(math.sqrt(float(BC['D-D'][-1]))-MU2)/MU2*100:.4f}%")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§三 頻率定義掃描 — 「共同頻率」係邊個量?\n{'─'*100}")
print("""
  ★ 兩個候選定義 (必須分清):
    (i)  ω_n^dyn = √λ_n          鏈/環本徵頻率  → 逐模不同 (非簡併)
    (ii) ω^circle = √(k_n² + m_n²)  色散圓半徑 (fiducial) → 恆等常數 (定義使然)
""")

lam_ring_44 = [2 - 2 * math.cos(math.pi * n / 44) for n in range(1, ND + 1)]
wdyn = [math.sqrt(x) for x in lam_ring_44]
chk("C9 [慣例=44-site ring] ω_n^dyn = √γ_n = 2sin(πn/88) 逐模不同 (非簡併)",
    len(set(round(x, 10) for x in wdyn)) == ND,
    f"範圍 [{min(wdyn):.6f}, {max(wdyn):.6f}], 相異值 = {len(set(round(x,10) for x in wdyn))}/{ND}")

# 圓半徑掃描: ω 任意 ≥ √γ_max 都令 ω² = k² + γ_n 成立
print(f"\n  {'ω (fiducial)':>14} {'min k_n':>12} {'ω²=k²+γ 恆等?':>16} {'k_44':>12}")
print("  " + "-" * 60)
circ_rows = {}
for w in [2.0, 2.5, 3.0, 5.0]:
    kn = [math.sqrt(w * w - g) for g in lam_ring_44]
    dev = max(abs((k * k + g) - w * w) for k, g in zip(kn, lam_ring_44))
    circ_rows[w] = {"k44": kn[-1], "dev": dev}
    print(f"  {w:>14.4f} {min(kn):>12.8f} {('YES' if dev < 1e-12 else 'no'):>16} {kn[-1]:>12.8f}")

chk("C10 [定義(ii)] ω² = k² + m² 對【任何】ω ≥ √γ_max 都恆等成立 ⟹ 唔可能唯一確定 ω",
    all(v["dev"] < 1e-12 for v in circ_rows.values()),
    "ω ∈ {2, 2.5, 3, 5} 全部成立 ⟹ 恆等式無判別力")
chk("C11 [定義(ii)] 唯一性只能由額外條件 k_44 = 0 提供 ⟹ ω = √γ_44 = μ²",
    abs(circ_rows[2.0]["k44"]) < 1e-12,
    f"k_44(ω=2) = {circ_rows[2.0]['k44']:.2e}; k_44(ω=2.5) = {circ_rows[2.5]['k44']:.6f} ≠ 0")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§四 Z₂ 扇區分解 (奇/偶)\n{'─'*100}")

odd = sum(4 * sin(pi * n / 88) ** 2 for n in range(1, ND + 1) if n % 2 == 1)
even = sum(4 * sin(pi * n / 88) ** 2 for n in range(1, ND + 1) if n % 2 == 0)
chk("C12 [慣例=44-site] Σγ_odd = 44 = N_d EXACT",
    abs(odd - 44) < mpf('1e-45'), f"Σγ_odd = {mp.nstr(odd, 25)}")
chk("C13 [慣例=44-site] Σγ_even = 46; 差 = μ² = 2 EXACT",
    abs(even - 46) < mpf('1e-45') and abs((even - odd) - 2) < mpf('1e-45'),
    f"Σγ_even = {mp.nstr(even, 25)}, 差 = {mp.nstr(even-odd, 25)}")
chk("C14 [慣例=44-site] ⟨γ⟩_odd = Σγ_odd/22 = μ² = 2 EXACT (a = 1 身份, O169 docs/12)",
    abs(odd / 22 - 2) < mpf('1e-45'), f"⟨γ⟩_odd = {mp.nstr(odd/22, 25)}")

dev_refl = max(abs((4 * sin(pi * (44 - n) / 88) ** 2 - 2) + (4 * sin(pi * n / 88) ** 2 - 2))
               for n in range(1, ND + 1))
chk("C15 [慣例=44-site] 反射對稱 γ_{44−n} − μ² = −(γ_n − μ²) EXACT (奇扇區零殘餘)",
    dev_refl < mpf('1e-45'), f"max dev = {mp.nstr(dev_refl, 3)}")
chk("C16 [44-site] 反射不動點 n=22: γ_22 = μ² EXACT (偶扇區殘餘 2/44 非整數)",
    abs(4 * sin(pi * 22 / 88) ** 2 - 2) < mpf('1e-45'), "γ_22 = 2")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§五 ⚠️ 慣例混用檢查 (O136 上游)\n{'─'*100}")
print("""
  O136 scripts/59 (權威 |Δm|):  ψ_n(i) = sin(nπi/89)   ← D-D 鏈模 (88 site)
                                E_n    = 4sin²(nπ/88)   ← 環譜 (44/88 慣例)
  ⟹ ⚠️ 兩者屬【唔同慣例】: ψ_n 之真本徵值 = 2−2cos(nπ/89)
     呢個係【標記】而非錯誤 (|Δm| 度量係秩配對, 只讀排序), 但必須量化慣例敏感度
""")
V = V_position()
scores = {}
for name, E in [("E_ring44 (O136 權威)", E_ring44()),
                ("E_dd88 (ψ_n 真本徵值)", E_dd88()),
                ("E_o159_88 (O159 半格)", E_o159_88())]:
    s = logscore(sum_V2_dE(E, V))
    scores[name] = s
    print(f"  {name:>26}: |Δm| 對數度量 RMS = {s:.4f}")
chk("C17 [慣例敏感度] 三個譜慣例之 |Δm| RMS 都 < 0.60 (形狀結論唔係慣例 artifact)",
    all(v < 0.60 for v in scores.values()),
    f"範圍 [{min(scores.values()):.4f}, {max(scores.values()):.4f}]")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§六 裁決 (F1)\n{'─'*100}")
print("""
  ① 譜結構 (44-site ring): γ_n = 4sin²(πn/88) = 2−2cos(πn/44)  [精確]
     γ_max = γ_44 = 4 = μ⁴  ⟹  √γ_max = μ² = 2
  ② 動態頻率 ω_n^dyn = √γ_n = 2sin(πn/88) 逐模【不同】(44 個相異值)
     ⟹ 鏈本身【冇】頻率簡併
  ③ 「共同頻率」ω = μ² 係色散圓半徑 (fiducial), 由 k_44 = 0 唯一選定;
     ω² = k² + m² 對任何 ω ≥ √γ_max 都恆等成立 ⟹ 恆等式本身零判別力
  ④ 慣例依賴: √γ_max = μ² 只喺 ring 慣例 EXACT; D-D/D-N/N-N 差 0.03%
     88-site O159 慣例下 μ² = γ_44 (中點模) — 同一個值, 兩個唔同身份
     ⟹ 值穩健, 身份唔唯一 = 【約定】之簽名
""")

verdict = ("約定 (normalization convention) + 唯一性條件 (k_44 = 0)。"
           "共同頻率係 fiducial 圓半徑, 唔係動態簡併; 鏈之動態頻率 ω_n^dyn = √γ_n 逐模不同。")
print(f"  ★ F1 裁決 = {verdict}")

n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "01_f1_audit.json", "w") as f:
    json.dump({
        "F1_verdict": verdict,
        "checks_pass": n_pass, "checks_total": len(checks),
        "bc_scan": bc_rows,
        "circle_scan": {str(k): v for k, v in circ_rows.items()},
        "convention_scores": scores,
        "gamma_max_ring44": 4.0, "mu2": MU2,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/01_f1_audit.json")
