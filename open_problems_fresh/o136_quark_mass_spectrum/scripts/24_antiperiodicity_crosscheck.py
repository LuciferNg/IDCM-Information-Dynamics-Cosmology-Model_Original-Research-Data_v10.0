#!/usr/bin/env python3
"""
O136 — Script 24: 交叉檢驗 — O34/O35 模式 vs 反週期選擇律
================================================================
反週期選擇律 (O136 Item 1 / O137 Phase 2, 獨立於質量推導):
  L = N_d/gcd(n, N_d)
  n·L ≡ N_d (mod 2N_d)   ⟺  v₂(n) ≤ 2

本 script: 檢驗 O34/O35 的模式分配是否滿足此獨立約束。
"""
import math, json
from pathlib import Path
from math import gcd

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

print("=" * 92)
print("O136 Script 24: O34/O35 模式 vs 反週期選擇律 (獨立約束)")
print("=" * 92)

# O34/O35 模式分配
modes = {"mu": 1, "tau": 18, "u": 10, "d": 24, "s": 22, "c": 8, "b": 33, "t": 19,
         "W": 30, "Z": 41, "H": 38}
# O136/O54 框架的模式
modes_o136 = {"e": 1, "mu": 7, "tau": 20, "s": 14, "c": 34, "b": 33}

print(f"\n{'─'*92}")
print("1. 反週期約束檢驗 (v₂(n) ≤ 2, 即 n 不被 8 整除)")
print(f"{'─'*92}")

print(f"\n{'框架':>8} {'粒子':>6} {'n':>4} {'v₂(n)':>6} {'L':>4} {'n·L mod 2N_d':>14} {'要求':>6} {'驗證':>6}")
print("-" * 62)

results = {}
for frame, mm in [("O34/O35", modes), ("O136/O54", modes_o136)]:
    ok_count, fail_count = 0, 0
    for p, n in mm.items():
        L_ = Nd // gcd(n, Nd)
        val = (n * L_) % (2*Nd)
        v = v2(n)
        ok = (val == Nd) and (v <= 2)
        if ok: ok_count += 1
        else: fail_count += 1
        results[(frame, p)] = {"n": n, "v2": v, "L": L_, "val": val, "ok": ok}
        print(f"{frame:>8} {p:>6} {n:>4} {v:>6} {L_:>4} {val:>14} {Nd:>6} {'✅' if ok else '🔴':>6}")
    print(f"{'':>8} {'合計':>6} {'':>4} {'':>6} {'':>4} {'':>14} {'':>6} {ok_count}/{ok_count+fail_count:>6}")
    print()

print(f"{'─'*92}")
print("2. 判決")
print(f"{'─'*92}")

o35_fail = [p for p, n in modes.items() if v2(n) >= 3]
print(f"\nO34/O35 違反反週期律的模式: {o35_fail}")
print(f"  → n=8 (c 夸克): v₂(8) = {v2(8)} ≥ 3 🔴")
print(f"  → n=24 (d 夸克): v₂(24) = {v2(24)} ≥ 3 🔴")
print(f"\nO136/O54 全部通過: {list(modes_o136.values())}")
print(f"  → v₂ 值: {[v2(n) for n in modes_o136.values()]} 全部 ≤ 2 ✅")

print(f"""
★ 結論: O34/O35 的 8 個費米子模式中, 2 個 (c=8, d=24) 違反
   由 88-site 鏈結構獨立推導的反週期選擇律。
   
   O136/O54 的 6 個模式全部滿足。
   
   → 反週期律 (獨立於質量) 支持 O136/O54 模式, 反對 O34/O35 模式
""")

# ═══ 3. 兩個框架的對比 ═══════════════════════════════
print(f"{'─'*92}")
print("3. 兩框架全面對比")
print(f"{'─'*92}")

print(f"""
{'維度':>22} {'O34/O35 (sin比)':>24} {'O136/O54 (γ比×P_f)':>26}
{'-'*76}
{'質量比閉合數':>22} {'8/8 (但密度效應)':>24} {'8/9 (部分)':>26}
{'模式全局一致':>22} {'🔴 d,W 衝突':>24} {'🟡 部分':>26}
{'反週期約束':>22} {'🔴 2/8 違反':>24} {'✅ 6/6 通過':>26}
{'密度檢驗':>22} {'🔴 0/8 超越隨機':>24} {'🔴 未測':>26}
{'選擇規則':>22} {'Δn = B²−2 = 14':>24} {'L = N_d/gcd(n,N_d)':>26}
{'自由參數':>22} {'0 (但模式係搜索得來)':>24} {'0 (但 P_f 字典未推導)':>26}
""")

print(f"""
★ 兩個框架都未通過嚴格檢驗:
   - O34/O35: 匹配係密度效應 + 模式衝突 + 違反獨立約束
   - O136/O54: P_f 字典未推導 (u, τ 未閉合)
   
★ 唯一通過獨立約束的是: 反週期選擇律 (v₂(n) ≤ 2)
   → 這是唯一「非質量擬合」的結構約束
""")

# ═══ 4. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "24_antiperiodicity_crosscheck.json", "w") as f:
    json.dump({
        "o35_modes": modes, "o136_modes": modes_o136,
        "o35_violations": o35_fail,
        "o35_pass": sum(1 for n in modes.values() if v2(n) <= 2),
        "o35_total": len(modes),
        "o136_pass": sum(1 for n in modes_o136.values() if v2(n) <= 2),
        "o136_total": len(modes_o136),
        "verdict": "O34/O35 2/8 模式違反獨立反週期約束; O136/O54 6/6 通過",
        "density_verdict": "0/8 公式超越隨機 (觀測中位數 0.146% ≈ 隨機 0.176%)",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/24_antiperiodicity_crosscheck.json")