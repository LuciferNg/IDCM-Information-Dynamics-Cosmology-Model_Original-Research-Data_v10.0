#!/usr/bin/env python3
"""
O136 — Script 10: T3 費米子反週期條件核對
================================================================
核對 O136 docs/04 的線索: n·L ≡ 44 (mod 88), L ∈ {B=4, 2B=8, L5=11, Nd/2=22, Nd=44}

目標 (誠實核對, 非擬合):
  1. 驗證 6 個費米子的 (n, L) 配對是否滿足反週期條件
  2. 測試 L 是否被 n 唯一鎖定 (剛性檢驗)
  3. 檢驗 2B=8 是否有解
  4. 檢查 u, d 的 L 值 (docs/04 未列)
  5. 找出 L 與 v2(n) 的結構關係

反週期物理意義:
  phase = 2πi·n·L/88, 條件 n·L ≡ 44 (mod 88)
  → phase = 2πi·(44+88k)/88 = πi(1+2k) → e^{iπ·odd} = -1
  → 模式繞 L 個 site 後返回 -1 = 費米子反週期邊界條件
"""
import json, math
from pathlib import Path

Nd, B = 44, 4
N88 = 88
L5 = 11

print("=" * 78)
print("O136 Script 10: T3 費米子反週期條件核對")
print("=" * 78)

# ─── 1. docs/04 的 (n, L) 配對 ─────────────────────────
print(f"\n─── 1. docs/04 已知 (n, L) 配對核對 ───")

known = {
    "e":  (1, 44, 3.6),
    "mu": (7, 44, 15.5),
    "tau":(20, 11, 37.0),
    "s":  (14, 22, 3.6),
    "c":  (34, 22, 13.0),
    "b":  (33, 4, 44.0),
}

print(f"\n{'粒子':>6} {'n':>4} {'L':>4} {'n·L':>6} {'mod 88':>8} {'≡44?':>6} {'v2(n)':>6} {'v2(L)':>6} {'Σ':>4}")
print("-" * 60)

def v2(x):
    if x == 0: return float('inf')
    k = 0
    while x % 2 == 0:
        x //= 2; k += 1
    return k

all_pass = True
for p, (n, L, pf) in known.items():
    prod = n * L
    mod88 = prod % 88
    ok = (mod88 == 44)
    all_pass = all_pass and ok
    print(f"{p:>6} {n:>4} {L:>4} {prod:>6} {mod88:>8} {'✅' if ok else '🔴':>6} {v2(n):>6} {v2(L):>6} {v2(n)+v2(L):>4}")

print(f"\n全部滿足反週期條件: {'✅' if all_pass else '🔴'}")

# ─── 2. 關鍵結構: v2(n) + v2(L) = v2(Nd) ──────────────
print(f"\n─── 2. 結構關係: v2(n·L) = v2(Nd) = {v2(Nd)} ───")
print(f"\nN_d = {Nd} = 4 × 11, v2(N_d) = {v2(Nd)}")
print(f"條件 n·L ≡ N_d (mod 2N_d) ⟺ v2(n·L) = v2(N_d) = 2")
for p, (n, L, pf) in known.items():
    print(f"  {p:>4}: v2({n}) + v2({L}) = {v2(n)} + {v2(L)} = {v2(n)+v2(L)} {'✅' if v2(n)+v2(L)==2 else '🔴'}")

# ─── 3. 剛性檢驗: L 是否被 n 唯一鎖定 ─────────────────
print(f"\n─── 3. 剛性檢驗: 給定 n, 哪些 L ∈ {{4,8,11,22,44}} 滿足條件? ───")

L_set = [4, 8, 11, 22, 44]
print(f"\n{'n':>4} {'v2(n)':>6} {'n mod 22':>9} {'可行 L':>20} {'唯一?':>8} {'實際用':>8}")
print("-" * 62)

rigidity = {}
for p, (n, L, pf) in known.items():
    feasible = [Lc for Lc in L_set if (n * Lc) % 88 == 44]
    unique = len(feasible) == 1
    rigidity[p] = feasible
    print(f"{n:>4} {v2(n):>6} {n % 22:>9} {str(feasible):>20} {'✅' if unique else '🔴':>8} {L:>8}")

# ─── 4. L=8 (2B) 是否有解 ────────────────────────────
print(f"\n─── 4. L = 2B = 8 的解存在性 ───")
print(f"\nn·8 ≡ 44 (mod 88)")
print(f"→ 8n = 44 + 88k → n = 5.5 + 11k")
print(f"→ n 非整數, 對所有 k ∈ ℤ 無解 🔴")
sol8 = [n for n in range(1, 45) if (n*8) % 88 == 44]
print(f"窮舉 n=1..44: 解集 = {sol8} {'(空集 ✅ 確認無解)' if not sol8 else ''}")

# ─── 5. 反週期條件等價於 v2(n) ≤ 2? ──────────────────
print(f"\n─── 5. 反週期條件 vs v2(n) ≤ 2 的等價性 ───")
print(f"\n對每個 n=1..44, 檢查是否存在 L ∈ {{4,8,11,22,44}} 滿足反週期:")
print(f"{'n':>4} {'v2(n)':>6} {'可行 L':>22} {'有解?':>6}")
print("-" * 45)
fermion_candidates = []
boson_candidates = []
for n in range(1, 45):
    feas = [Lc for Lc in L_set if (n*Lc) % 88 == 44]
    has = len(feas) > 0
    if has:
        fermion_candidates.append(n)
    else:
        boson_candidates.append(n)
    if n <= 12 or n in [20, 22, 33, 34, 44]:
        print(f"{n:>4} {v2(n):>6} {str(feas):>22} {'✅' if has else '🔴':>6}")

print(f"\n有解 (費米子候選): {len(fermion_candidates)} 個")
print(f"無解 (玻色子候選): {len(boson_candidates)} 個 = {boson_candidates}")

# 檢查是否 = v2(n) ≥ 3
v2_ge3 = [n for n in range(1, 45) if v2(n) >= 3]
print(f"\nv2(n) ≥ 3 的 n: {v2_ge3}")
print(f"無解的 n:        {boson_candidates}")
print(f"完全一致: {'✅' if v2_ge3 == boson_candidates else '🔴'}")

# ─── 6. u, d 的 L 值 ─────────────────────────────────
print(f"\n─── 6. u, d (n=1) 的 L 值 ───")
for p in ["u", "d"]:
    n = 1
    feas = [Lc for Lc in L_set if (n*Lc) % 88 == 44]
    print(f"  {p}: n=1 → 可行 L = {feas}")
print(f"\n注意: e 亦為 n=1, L=44。u/d/e 同 n=1 → L 亦同 (L=44)")
print(f"→ u/d/e 的分化不能靠 (n, L), 必須靠 P_f (色荷/同位旋)")

# ─── 7. 結論 ─────────────────────────────────────────
print(f"\n{'='*78}")
print("結論")
print(f"{'='*78}")
print(f"""
✅ 反週期條件 n·L ≡ N_d (mod 2N_d) 對 6 個費米子全部成立 (6/6)
✅ 結構形式: v2(n·L) = v2(N_d) = 2
✅ L=2B=8 無解 (n = 5.5 + 11k 非整數)
✅ 反週期條件 ⟺ v2(n) ≤ 2 (與 O137 Phase 2 玻色子排除 v2(n)≥3 完全一致)
✅ 5/6 費米子的 L 被 n 唯一鎖定 (L = N_d/2^{{v2(n)}}: 44, 22, 11)
🔴 例外: b (n=33, v2=0) 的 L 有兩個選擇 {{4, 44}}, 實際用 4
🔴 u/d/e 同為 n=1 → 反週期條件無法分化三者

關鍵未解: b 為何選 L=4 而非 L=44?
""")

# 保存
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "10_antiperiodicity_T3.json", "w") as f:
    json.dump({
        "known_pairs": {p: {"n": n, "L": L, "P_f": pf, "v2_n": v2(n), "v2_L": v2(L)} 
                        for p, (n, L, pf) in known.items()},
        "all_satisfy": all_pass,
        "L8_has_solution": False,
        "fermion_candidates": fermion_candidates,
        "boson_candidates": boson_candidates,
        "equivalence_v2le2": v2_ge3 == boson_candidates,
        "rigidity": {p: feas for p, feas in rigidity.items()},
        "open": "b (n=33) L 不唯一: {4,44}; u/d/e 同 n=1 無法分化",
    }, f, indent=2, ensure_ascii=False)
print("✅ 結果已寫入 data/10_antiperiodicity_T3.json")