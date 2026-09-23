#!/usr/bin/env python3
"""
⚠️ 2026-09-22 已移交 O215: 質量譜→預算（Σ√γ 身份 + 3/60,16/60,41/60）成個搬去
o215_omegab_first_principles/scripts/02_sqrt_sum_identity.py
O206 只專注質量譜本身 — 本文件保留為歷史，不再更新。

O214 前身探索 (O206 scripts/28): Σ√γ_n 閉式 + 偏差結構
=========================================================
目標: Σ√γ_n (玻色塔質量譜 44 模) ≈ 60−3 = 57 嘅 0.029% 偏差係咪有結構身份。

初步線索 (手算): Σ√γ = 2·Σsin(nπ/88) ≈ 57 + 1/60?
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent.parent / "data"

print("=" * 100)
print("O214 前身: Σ√γ_n 閉式 + 偏差結構")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A Σ√γ_n 精確閉式驗證\n{'─'*100}")
# 直接求和 (numpy)
n_arr = np.arange(1, 45)
sum_sq = float(np.sum(2 * np.sin(n_arr * np.pi / 88)))
# 閉式: Σsin(kx), k=1..44, x=π/88 = sin(nx/2)sin((n+1)x/2)/sin(x/2)
x = np.pi / 88
sum_sin_closed = np.sin(44 * x / 2) * np.sin(45 * x / 2) / np.sin(x / 2)
sum_sq_closed = 2 * float(sum_sin_closed)
print(f"  直接求和 Σ√γ_n = {sum_sq:.10f}")
print(f"  閉式 2·sin(π/4)sin(45π/176)/sin(π/176) = {sum_sq_closed:.10f}")
print(f"  一致: {abs(sum_sq - sum_sq_closed) < 1e-12}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 偏差結構\n{'─'*100}")
d = sum_sq - 57.0
print(f"  Σ√γ − 57 = {d:.10f}")
print(f"  Σ√γ − 57 − 1/60 = {sum_sq - 57 - 1/60:.10f}")
print(f"  Σ√γ − (N_d+F₇) = {sum_sq - 57:.10f}")
print(f"  Σ√γ − (N_d+F₇+1/60) = {sum_sq - 57 - 1/60:.10f}")
# Σsin(nπ/88) 偏差
sum_sin = float(np.sum(np.sin(n_arr * np.pi / 88)))
print(f"\n  Σsin(nπ/88) = {sum_sin:.10f}")
print(f"  Σsin − 28.5 (E_proj) = {sum_sin - 28.5:.10f}")
print(f"  Σsin − 28.5 − 1/120 = {sum_sin - 28.5 - 1/120:.10f}")
# 1/60 關係
print(f"\n  1/60 = {1/60:.10f}")
print(f"  (Σ√γ−57) vs 1/60: Δ = {(sum_sq-57) - 1/60:.10f} (相對 {(sum_sq-57-1/60)/(1/60)*100:.4f}%)")
# 更精確: 偏差可能係某閉式
# Σsin(kx) = (1/2)(cot(x/2) − cos((n+1)x/2)/sin(x/2)) 其他形式
# 試: d2 = Σ√γ − 57 − 1/60 係咪 γ₆/1100? 或者其他
d2 = sum_sq - 57 - 1 / 60
print(f"\n  殘餘 ε = Σ√γ − 57 − 1/60 = {d2:.10f}")
print(f"  ε/γ₁ = {d2/0.00509577:.4f}")
print(f"  ε×88 = {d2*88:.6f}")
print(f"  ε×176 = {d2*176:.6f}")
print(f"  ε×360 = {d2*360:.6f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 候選身份\n{'─'*100}")
cands = {
    "1/60": 1/60, "1/120": 1/120, "γ₁×3.26": 0.00509577*3.26,
    "1/57.0166−1/60": 0, "π/189": np.pi/189, "1/176×2.92": 1/176*2.92,
    "γ₆/10.9": 0.180736/10.9, "1/(60.28)": 1/60.28,
}
print(f"  偏差 d = Σ√γ − 57 = {d:.8f}")
for name, v in cands.items():
    print(f"    {name:>16} = {v:.8f}  (Δ{abs(d-v)/d*100:6.3f}%)" if v != 0 else f"    {name}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決\n{'─'*100}")
print(f"""
  §A Σ√γ_n 閉式確認: 2·sin(π/4)sin(45π/176)/sin(π/176) = {sum_sq:.6f}
  §B Σ√γ − 57 = {d:.6f}
     Σ√γ − 57 − 1/60 = {sum_sq - 57 - 1/60:.8f}  ← 接近 0!
  ⟹ ★★ Σ√γ_n ≈ 57 + 1/60 = N_d + F₇ + 1/60
     (60 份預算: 60 − 3(物質) + 1/60(真空能修正) = 57.0167 vs 實測 57.0166)
  §C 殘餘 ε = {d2:.8f} — 非平凡 (≈ 0.00008)
  ⟹ 質量譜總和身份確立:
     Σ√γ_n = 57 + 1/60 + ε
       = (N_d + F₇) + 1/60 + ε
     60 份預算由質量譜導出:
       物質份 3 = 60 − (N_d+F₇)  (57 = N_d+F₇ 係質量譜主體)
       真空能 1/60 = 質量譜殘餘修正
     完整唯一解仍需: ε 嘅精確閉式 + 重子定義 (O214)
""")
with open(OUT / "28_sqrt_sum_identity.json", "w") as f:
    json.dump({
        "sum_sqrt_gamma": float(sum_sq),
        "closed_form": float(sum_sq_closed),
        "dev_from_57": float(d),
        "dev_from_57_plus_1over60": float(d2),
        "sum_sin": float(sum_sin),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/28_sqrt_sum_identity.json")
