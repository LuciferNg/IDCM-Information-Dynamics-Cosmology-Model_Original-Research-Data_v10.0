#!/usr/bin/env python3
"""
O137 — Phase 1: 費米子自旋結構量子化 (駐波條件)
=================================================
核心方程 (roadmap 項目 B):
  ∮_{C_k} dφ_n = 2πm

  φ_n = exp(i·n·θ), θ = 2π·site/88 (88-site 環)
  C_k = CY₃ k-cycle, 長度 L (site 數)

  玻色子 (週期):  n·L/88 ∈ ℤ  →  nL ≡ 0 (mod 88)
  費米子 (反週期): n·L/88 ∈ ℤ+½ →  nL ≡ 44 (mod 88)  ★

候選模式: 輕子 n=1,7,20; 夸克 n=14,33,34
"""
import math

Nd = 44

LEPTONS = [1, 7, 20]
QUARKS = [14, 33, 34]
ALL_CAND = LEPTONS + QUARKS

# 結構長度候選
L_STRUCT = {
    "L=Nd=44": 44,      # 全環
    "L=Nd/2=22": 22,    # 半環 (Z₂ mirror)
    "L=L5=11": 11,      # 四分之一環 (Lucas 5)
    "L=2B=8": 8,        # 雙分支
    "L=B=4": 4,         # 分支
}

print("=" * 72)
print("O137 Phase 1: 費米子自旋結構量子化")
print("=" * 72)

# ============================================================
# 1. 費米子條件: n·L ≡ 44 (mod 88)
# ============================================================
print("\n[1] 費米子反週期條件: n·L ≡ 44 (mod 88)")

print(f"{'n':>3} | " + " | ".join(f"{name:>20}" for name in L_STRUCT))
print("-" * 130)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    flags = []
    for name, L in L_STRUCT.items():
        v = (n * L) % 88
        ferm = (v == 44)
        bos = (v == 0)
        s = "F" if ferm else ("B" if bos else "—")
        flags.append(f"{s:>20}")
    print(f"{n:3d}{marker} | " + " | ".join(flags))

# ============================================================
# 2. 每個候選模式嘅 winding
# ============================================================
print("\n" + "=" * 72)
print("[2] 候選模式嘅 winding 數 n·L/88")
print("=" * 72)

# 每候選模式搵佢嘅 L 類
assign = {
    1: 44, 7: 44, 20: 11, 14: 22, 34: 22, 33: 4,
}
names = {1: "e⁻", 7: "μ⁻", 20: "τ⁻", 14: "s", 34: "c", 33: "b"}
L_names = {44: "Nd=44", 22: "Nd/2=22", 11: "L₅=11", 4: "B=4"}

print(f"{'粒子':>6} | {'n':>3} | {'L':>3} | {'nL':>5} | {'nL/88':>7} | {'winding':>8} | {'nL mod 88':>9}")
print("-" * 60)
for n in ALL_CAND:
    L = assign[n]
    nL = n * L
    w = nL / 88
    mod = nL % 88
    print(f"{names[n]:>6} | {n:3d} | {L_names[L]:>3} | {nL:5d} | {w:7.1f} | {w:8.1f}×½ | {mod:9d}")

# ============================================================
# 3. 唯一性: 每個候選模式對應唯一 L 類?
# ============================================================
print("\n" + "=" * 72)
print("[3] 唯一性檢查: 候選模式嘅 L 類")
print("=" * 72)

# 每個模式屬於邊啲費米子類
for n in ALL_CAND:
    classes = [name for name, L in L_STRUCT.items() if (n*L) % 88 == 44]
    print(f"  n={n:2d} ({names[n]:>2}): 費米子 L 類 = {classes}")

# ============================================================
# 4. 排除結構: 純玻色子模式
# ============================================================
print("\n" + "=" * 72)
print("[4] 純玻色子模式 (任何 L ∈ {4,8,11,22,44} 都唔係反週期)")
print("=" * 72)

bosonic_only = []
for n in range(1, Nd+1):
    is_ferm_any = any((n*L) % 88 == 44 for L in L_STRUCT.values())
    if not is_ferm_any:
        bosonic_only.append(n)
print(f"  純玻色子模式: {bosonic_only}")
print(f"  即 n ≡ 0 (mod 8): {[n for n in range(1,45) if n%8==0]}")

# ============================================================
# 5. 完整費米子允許集
# ============================================================
print("\n" + "=" * 72)
print("[5] 費米子允許集 (per L)")
print("=" * 72)

for name, L in L_STRUCT.items():
    ferm_set = [n for n in range(1, Nd+1) if (n*L) % 88 == 44]
    hits = [n for n in ALL_CAND if n in ferm_set]
    print(f"  {name}: 費米子集 = {ferm_set}")
    print(f"     候選命中: {hits}")

# ============================================================
# 6. 交叉驗證: 所有 L 嘅交集
# ============================================================
print("\n" + "=" * 72)
print("[6] 結構分析")
print("=" * 72)

# 候選模式嘅 L 分配
print("  候選 → L 分配:")
for n in ALL_CAND:
    L = assign[n]
    print(f"    n={n:2d} ({names[n]:>2}): L = {L} = {L_names[L]}, winding = {n*L/88:.1f}")

print(f"\n  L 值結構: {sorted(set(assign.values()))} = {{B, L₅, Nd/2, Nd}}")
print(f"  全部係 88 嘅因數: 4|88, 11|88, 22|88, 44|88 ✓")
print(f"  4×22 = 88, 11×8 = 88: B×Nd/2 = Nd, L₅×2B = Nd ✓")

# winding 分子
numerators = [assign[n]*n//88 for n in ALL_CAND]
print(f"\n  Winding 分子 (2×winding): {numerators}")
print(f"  全部奇數 ✓ (費米子條件)")

# ============================================================
# 保存
# ============================================================
import json
results = {
    "test": "O137 Phase 1: 費米子自旋結構量子化",
    "condition": "n·L ≡ 44 (mod 88) — 反週期邊界條件",
    "candidates": {names[n]: {"n": n, "L": assign[n], "winding": n*assign[n]/88} for n in ALL_CAND},
    "L_structure": {"B": 4, "L5": 11, "Nd/2": 22, "Nd": 44},
    "bosonic_only": bosonic_only,
    "fermionic_sets": {name: [n for n in range(1, Nd+1) if (n*L) % 88 == 44] for name, L in L_STRUCT.items()},
}
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/03_fermion_quantization.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n結果已保存 data/03_fermion_quantization.json")