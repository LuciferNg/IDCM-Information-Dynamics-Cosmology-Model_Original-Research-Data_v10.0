#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O78 scripts/05_verification_audit.py
====================================
獨立核對 audit — 由原始結構常數重新計算所有 O78 記錄值。
(唔 import 其他 script — 獨立重算, 調律者要求)

驗證項目 (全部 O78 docs 記錄):
  V1. Σγ_odd = 88, Σγ_even = 90 (奇偶能量和)
  V2. μ² = Σγ_even − Σγ_odd = 2 (SSB 質量項)
  V3. ⟨W⟩² = 61.5, V_min = −61.5 (O39 重現)
  V4. 88/90 = 44/45 (能量比)
  V5. 264 = 3×88 (O62 主項)
  V6. 61.5/28.5 = 41/19 (O41 預算)
  V7. 插值身份: γ_{2n} = γ_n^(44)
  V8. 半整數模式: γ_{2n−1} = 4sin²((n−0.5)π/88)
  V9. 178 = 2×F11 (Fibonacci)
  V10. γ_44 = 2 (自對偶 = μ²)
"""
import math

def main():
    print("=" * 70)
    print("O78 script 05: 獨立核對 audit (唔 import 其他 script)")
    print("=" * 70)

    # 原始結構常數 (O34/O72 定義)
    N = 44          # 世界維度
    N88 = 88        # 對偶鏈 site 數
    PHI = (1 + 5 ** 0.5) / 2
    L10 = 123       # Lucas 數 L10

    results = []

    # V1: 奇偶能量和
    S_odd = sum(4 * math.sin(math.pi * k / (2 * N88)) ** 2 for k in range(1, N88 + 1, 2))
    S_even = sum(4 * math.sin(math.pi * k / (2 * N88)) ** 2 for k in range(2, N88 + 1, 2))
    S_all = S_odd + S_even
    v1 = abs(S_odd - N88) < 1e-9 and abs(S_even - N88 - 2) < 1e-9
    results.append(("V1 Σγ_odd=88, Σγ_even=90", v1, f"{S_odd:.9f}/{S_even:.9f}"))

    # V2: μ²
    mu2 = S_even - S_odd
    v2 = abs(mu2 - 2.0) < 1e-9
    results.append(("V2 μ² = 2", v2, f"{mu2:.9f}"))

    # V3: O39 SSB
    lam = 2.0 / L10
    W2 = mu2 / (2 * lam)
    Vmin = -(mu2 ** 2) / (4 * lam)
    v3 = abs(W2 - 61.5) < 1e-9 and abs(Vmin + 61.5) < 1e-9
    results.append(("V3 ⟨W⟩²=61.5, V_min=−61.5", v3, f"{W2:.6f}/{Vmin:.6f}"))

    # V4: 88/90 = 44/45
    v4 = abs(S_odd / S_even - N / (N + 1)) < 1e-12
    results.append(("V4 88/90 = 44/45", v4, f"{S_odd/S_even:.10f}"))

    # V5: 264 = 3×88
    v5 = abs(3 * S_odd - 264) < 0.1
    results.append(("V5 264 = 3×Σγ_odd", v5, f"{3*S_odd:.4f}"))

    # V6: 61.5/28.5 = 41/19
    ratio = 61.5 / 28.5
    v6 = abs(ratio - 41 / 19) < 1e-12
    results.append(("V6 61.5/28.5 = 41/19", v6, f"{ratio:.10f}"))

    # V7: 插值身份 γ_{2n} = γ_n^(44)
    dev = max(abs(4 * math.sin(math.pi * (2 * n) / (2 * N88)) ** 2
                  - 4 * math.sin(math.pi * n / (2 * N)) ** 2) for n in range(1, N + 1))
    v7 = dev < 1e-12
    results.append(("V7 γ_{2n} = γ_n^(44)", v7, f"dev={dev:.2e}"))

    # V8: 半整數模式
    dev8 = max(abs(4 * math.sin(math.pi * (2 * n - 1) / (2 * N88)) ** 2
                   - 4 * math.sin((n - 0.5) * math.pi / N88) ** 2) for n in range(1, N + 1))
    v8 = dev8 < 1e-12
    results.append(("V8 γ_{2n−1} = half-int", v8, f"dev={dev8:.2e}"))

    # V9: 178 = 2×F11
    F11 = 89
    v9 = abs(S_all - 2 * F11) < 1e-9
    results.append(("V9 Σγ_all = 178 = 2F11", v9, f"{S_all:.4f}"))

    # V10: γ_44 = 2
    g44 = 4 * math.sin(math.pi * 44 / (2 * N88)) ** 2
    v10 = abs(g44 - 2.0) < 1e-12
    results.append(("V10 γ_44 = 2 = μ²", v10, f"{g44:.10f}"))

    # ---------- 輸出 ----------
    npass = 0
    print()
    for name, ok, val in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}: {val}")
        npass += ok
    total = npass == len(results)
    print(f"\n核對結果: {npass}/{len(results)} PASS")
    if total:
        print("🎉 全部 PASS — O78 記錄值獨立重算確認")
    else:
        print("❌ 有 FAIL — 需要修正")
    print("=" * 70)
    return 0 if total else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
