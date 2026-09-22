#!/usr/bin/env python3
"""
O136 — Script 33: A₅ 投影譜 — 質量無關模式選擇
================================================================
基礎 (O81 §7.3, 🟢 已閉合):
  c_{i,n} = cos²(n·β_i/2) = (1 + T_n(cos β_i))/2
  β_i = 節點 i 到冷斑 (209°, −57°) 之角距離
  Σ_i c_{i,n} = 30 (奇 n) / 20 (偶 n)
  來源: (i) 雙路徑干涉 (相位差 2nβ_i); (ii) A₅ orbit 中心對稱 ⟹ Σ_i T_n = 0 (奇 n)

★ 這是質量無關的幾何結構!
本 script: 計算完整投影譜, 找模式選擇規則。
"""
import numpy as np, math, json
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
OUT = Path(__file__).parent.parent / "data"

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def q_of(n): return n // math.gcd(n, Nd)
def L_of(n): return Nd // math.gcd(n, Nd)

print("=" * 96)
print("O136 Script 33: A₅ 投影譜 — 質量無關模式選擇")
print("=" * 96)

# ═══ 1. 重建 A₅ 幾何 + 投影 ══════════════════════════
print(f"\n{'─'*96}")
print("1. A₅ 幾何 + 冷斑投影")
print(f"{'─'*96}")

nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
print(f"\nA₅ 節點數: {len(U)}")

l, b = math.radians(209.0), math.radians(-57.0)
cold = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
cold /= np.linalg.norm(cold)
print(f"冷斑方向 (209°, −57°): {np.round(cold,6)}")

beta = np.arccos(np.clip(U @ cold, -1, 1))
print(f"\nβ_i (弧度): min={beta.min():.6f}, max={beta.max():.6f}, mean={beta.mean():.6f}")
print(f"β_i (度):   min={np.degrees(beta).min():.3f}, max={np.degrees(beta).max():.3f}")

# 中心對稱檢驗
print(f"\n★ 中心對稱檢驗 (V → −V 封閉):")
Uneg = -U
D = np.arccos(np.clip(Uneg @ U.T, -1, 1))
perm = np.argmin(D, axis=1)
sym_ok = (D[np.arange(60), perm].max() < 1e-3) and (len(set(perm.tolist())) == 60)
print(f"  max match dist = {D[np.arange(60), perm].max():.3e}, 排列有效 = {len(set(perm.tolist()))==60}")
print(f"  中心對稱: {'✅' if sym_ok else '🔴'}")

# ═══ 2. ★ 投影譜 ═════════════════════════════════════
print(f"\n{'─'*96}")
print("2. ★ A₅ 投影譜: Σ_i T_n(cos β_i) 與 Σ_i c_{i,n}")
print(f"{'─'*96}")

Tn = np.polynomial.chebyshev.Chebyshev.basis
def S_T(n): return float(Tn(n)(np.cos(beta)).sum())
def S_c(n): return float((np.cos(n*beta/2)**2).sum())

print(f"\n{'n':>3} {'v₂':>4} {'奇偶':>5} {'Σ_i T_n':>14} {'Σ_i c_{i,n}':>13} {'O136':>5}")
print("-" * 48)
O136 = {1, 7, 14, 20, 33, 34}
Svals = {}
for n in range(1, 45):
    s = S_T(n); c = S_c(n)
    Svals[n] = (s, c)
    print(f"{n:>3} {v2(n):>4} {'奇' if n%2 else '偶':>5} {s:>14.6f} {c:>13.6f} {'★' if n in O136 else '':>5}")

# ═══ 3. 奇偶分裂確認 ═════════════════════════════════
print(f"\n{'─'*96}")
print("3. 奇偶分裂 (O81 §7.3 確認)")
print(f"{'─'*96}")

odd_n = [n for n in range(1,45) if n%2==1]
even_n = [n for n in range(1,45) if n%2==0]
print(f"\n奇 n: Σ T_n 範圍 [{min(Svals[n][0] for n in odd_n):.6f}, {max(Svals[n][0] for n in odd_n):.6f}]")
print(f"      Σ c  範圍 [{min(Svals[n][1] for n in odd_n):.6f}, {max(Svals[n][1] for n in odd_n):.6f}]")
print(f"偶 n: Σ T_n 範圍 [{min(Svals[n][0] for n in even_n):.6f}, {max(Svals[n][0] for n in even_n):.6f}]")
print(f"      Σ c  範圍 [{min(Svals[n][1] for n in even_n):.6f}, {max(Svals[n][1] for n in even_n):.6f}]")

print(f"\n✅ 奇 n: Σ_i T_n = 0 EXACT (中心對稱) → Σ c = 30")
print(f"✅ 偶 n: Σ_i T_n ≠ 0 → Σ c ≠ 30")

# ═══ 4. ★ 精細結構: Σ T_n 的規律 ════════════════════
print(f"\n{'─'*96}")
print("4. ★ 精細結構: 偶 n 的 Σ_i T_n 值")
print(f"{'─'*96}")

print(f"\n{'n':>3} {'v₂':>4} {'Σ_i T_n':>14} {'Σ_i T_n / 20':>14} {'結構?':>20}")
print("-" * 58)
for n in even_n:
    s = Svals[n][0]
    print(f"{n:>3} {v2(n):>4} {s:>14.6f} {s/20:>14.6f} {'':>20}")

# ═══ 5. ★ 關鍵: 投影譜能否選模式? ════════════════════
print(f"\n{'─'*96}")
print("5. ★ 投影譜的選擇力")
print(f"{'─'*96}")

# (a) Σ c = 30 選奇 n
odd_sel = {n for n in range(1,45) if abs(Svals[n][1] - 30) < 1e-9}
print("\n(a) Σ_i c_{i,n} = 30  → 選出 " + str(len(odd_sel)) + " 個 (奇 n)")
print(f"    含 O136? {O136.issubset(odd_sel)} (O136 全部奇 n? {all(n%2==1 for n in O136)})")
print(f"    O136 的奇 n: {sorted(n for n in O136 if n%2==1)}")
print(f"    O136 的偶 n: {sorted(n for n in O136 if n%2==0)}")

# (b) 奇 n ∩ v₂ ≤ 2
sel_b = {n for n in odd_sel if v2(n) <= 2}
print(f"\n(b) 奇 n ∩ v₂≤2 → {len(sel_b)} 個 (奇 n 全部 v₂=0, 故無縮減)")

# (c) 極值 n
print(f"\n(c) Σ_i T_n 的極值 (偶 n):")
even_sorted = sorted(even_n, key=lambda n: Svals[n][0])
print(f"    最小 5: {[(n, round(Svals[n][0],4)) for n in even_sorted[:5]]}")
print(f"    最大 5: {[(n, round(Svals[n][0],4)) for n in even_sorted[-5:]]}")

# ═══ 6. ★★ 新方向: c_{i,n} 向量的結構 ═══════════════
print(f"\n{'─'*96}")
print("6. ★★ c_{i,n} 向量的結構 — 模式間的重疊")
print(f"{'─'*96}")

C = np.zeros((45, 60))
for n in range(1, 45):
    C[n] = np.cos(n*beta/2)**2

print("\nc_{i,n} 統計: min=" + f"{C[1:].min():.6f}" + ", max=" + f"{C[1:].max():.6f}" + ", mean=" + f"{C[1:].mean():.6f}")

# 模式間相關
print(f"\n模式間相關矩陣 (選樣):")
print(f"{'':>5}", end="")
for n in [1, 7, 14, 20, 33, 34]:
    print(f"{n:>9}", end="")
print()
for n in [1, 7, 14, 20, 33, 34]:
    print(f"{n:>5}", end="")
    for m in [1, 7, 14, 20, 33, 34]:
        r = np.corrcoef(C[n], C[m])[0,1]
        print(f"{r:>9.4f}", end="")
    print()

# ═══ 7. ★★ 關鍵測試: 投影權重的「有效維度」 ═════════
print(f"\n{'─'*96}")
print("7. ★★ 投影權重的有效維度 (participation ratio)")
print(f"{'─'*96}")

print(f"\n{'n':>3} {'v₂':>4} {'Σ c':>8} {'Σ c²':>10} {'PR = (Σc)²/Σc²':>16} {'O136':>5}")
print("-" * 52)
PR = {}
for n in range(1, 45):
    s1 = C[n].sum(); s2 = (C[n]**2).sum()
    pr = s1**2/s2
    PR[n] = pr
    print(f"{n:>3} {v2(n):>4} {s1:>8.4f} {s2:>10.4f} {pr:>16.6f} {'★' if n in O136 else '':>5}")

print(f"\n★ PR 範圍: [{min(PR.values()):.4f}, {max(PR.values()):.4f}]")
print(f"★ O136 的 PR: {{{', '.join(f'{n}:{PR[n]:.4f}' for n in sorted(O136))}}}")

# ═══ 8. 保存 ════════════════════════════════════════
with open(OUT / "33_a5_projection_spectrum.json", "w") as f:
    json.dump({
        "n_nodes": 60, "cold_spot": [209.0, -57.0],
        "beta_rad": {"min": float(beta.min()), "max": float(beta.max()), "mean": float(beta.mean())},
        "center_symmetric": bool(sym_ok),
        "spectrum": {str(n): {"v2": v2(n), "sum_T": Svals[n][0], "sum_c": Svals[n][1],
                              "PR": PR[n]} for n in range(1,45)},
        "odd_n_sum_c": 30.0, "even_n_sum_c": 20.0,
        "o136_modes": sorted(O136),
        "verdict": "待分析",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/33_a5_projection_spectrum.json")