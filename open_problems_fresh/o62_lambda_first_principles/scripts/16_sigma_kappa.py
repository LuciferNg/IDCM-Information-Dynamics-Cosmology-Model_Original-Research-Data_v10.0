#!/usr/bin/env python3
"""
O62 五期 16: Σκ 身份 + rem 系統搜索
=====================================
1. Σκ = −8 驗證 + 結構身份 (−8 = −2B?)
2. Σ|κ| = 198? (b₃, O57)
3. rem 系統搜索: rem = γ_a ± γ_b ± γ_c (係數 ±1, ±2)
4. rem = γ_k/N 精確化
5. F(γ) 唔同 slice (3×12 block) 分解
"""
import sys, os, math, json
import numpy as np
import mpmath as mp
mp.mp.dps = 50

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 五期 16: Σκ 身份 + rem 系統搜索")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
S_kappa = int(kappa.sum())
S_abs = int(np.abs(kappa).sum())
nnz = np.count_nonzero(kappa)

print("\n[1] κ 基本身份")
print(f"  Σκ = {S_kappa}")
print(f"  Σ|κ| = {S_abs}")
print(f"  nnz = {nnz}")
check("Σκ = −8 = −2B", S_kappa == -8, f"(Σκ={S_kappa}, −2B=−8)")
check("Σ|κ| = 198 = 6K_tree", S_abs == 198, f"(實際 {S_abs})")
check("Σ|κ| = 2×99 = 2×b₃?", S_abs == 2*99, f"(實際 {S_abs})")

# 正/負分離
S_pos = int(kappa[kappa > 0].sum())
S_neg = int(kappa[kappa < 0].sum())
n_pos = np.count_nonzero(kappa > 0)
n_neg = np.count_nonzero(kappa < 0)
print(f"\n  正 entries: Σ={S_pos}, n={n_pos}")
print(f"  負 entries: Σ={S_neg}, n={n_neg}")
check("Σκ = Σ⁺ + Σ⁻", S_pos + S_neg == S_kappa)
check("Σ⁺ − Σ⁻ = Σ|κ|?", S_pos - S_neg == S_abs, f"(Σ⁺={S_pos}, Σ⁻={S_neg})")
check("n_pos + n_neg = nnz", n_pos + n_neg == nnz)

# 198 有冇喺其他 slice?
print(f"\n  b₃ = 198 係 Σ|κ|? {'✅' if S_abs == 198 else '❌'}")

# ============ 2. κ 3×12 block 和 ============
print("\n[2] κ 3×12 block 和 (block 對角)")
# 每個 block (a,b,c) ∈ {0,1,2}³ 嘅 Σκ
blocks = {}
for a in range(3):
    for b in range(3):
        for c in range(3):
            sub = kappa[a*12:(a+1)*12, b*12:(b+1)*12, c*12:(c+1)*12]
            blocks[(a,b,c)] = int(sub.sum())
print("  Block 和 (行=block a, 列=block b, 深=block c):")
for a in range(3):
    for b in range(3):
        row = [f"({a},{b},{c}):{blocks[(a,b,c)]}" for c in range(3)]
        print(f"    {'  '.join(row)}")

# ============ 3. rem 系統搜索 ============
print("\n[3] rem = ±γ_a ± γ_b ± γ_c 搜索")
gamma44_mp = [4*mp.sin(mp.pi*i/88)**2 for i in range(1, 45)]
rem_mp = mp.mpf('0.0821292325802448541101854337443526542058467051')
best3 = []
# 3 項, 係數 ±1
for a in range(1, 45):
    ga = gamma44_mp[a-1]
    for b in range(a, 45):
        gb = gamma44_mp[b-1]
        for c in range(b, 45):
            gc = gamma44_mp[c-1]
            for sa in [-1, 1]:
                for sb in [-1, 1]:
                    for sc in [-1, 1]:
                        val = sa*ga + sb*gb + sc*gc
                        if abs(val) < 1e-15:
                            continue
                        err = abs(val - rem_mp)/abs(rem_mp)
                        if err < 0.005:
                            best3.append((err, f"{sa:+d}γ_{a}{sb:+d}γ_{b}{sc:+d}γ_{c}", val))
best3.sort()
print(f"  3 項 ±1 top 10 (誤差<0.5%):")
for err, name, val in best3[:10]:
    print(f"    {name:22s} = {mp.nstr(val, 15)} (誤差 {mp.nstr(err*100, 6)}%)")

# 2 項
best2 = []
for a in range(1, 45):
    ga = gamma44_mp[a-1]
    for b in range(a, 45):
        gb = gamma44_mp[b-1]
        for sa in [-2, -1, 1, 2]:
            for sb in [-2, -1, 1, 2]:
                val = sa*ga + sb*gb
                if abs(val) < 1e-15:
                    continue
                err = abs(val - rem_mp)/abs(rem_mp)
                if err < 0.001:
                    best2.append((err, f"{sa:+d}γ_{a}{sb:+d}γ_{b}", val))
best2.sort()
print(f"\n  2 項 ±{{1,2}} top 10 (誤差<0.1%):")
for err, name, val in best2[:10]:
    print(f"    {name:16s} = {mp.nstr(val, 15)} (誤差 {mp.nstr(err*100, 6)}%)")

# ============ 4. rem = γ_k/N ============
print("\n[4] rem = γ_k/N (N 整數)")
for k in range(1, 45):
    gk = gamma44_mp[k-1]
    N = gk/rem_mp
    Nf = float(N)
    if abs(Nf - round(Nf)) < 0.02 and round(Nf) > 10:
        print(f"  γ_{k}/{round(Nf)} = {mp.nstr(gk/round(Nf), 18)} (誤差 {mp.nstr(abs(gk/round(Nf)-rem_mp)/abs(rem_mp)*100, 6)}%)")
# 1/N 直接
for N in [994, 995, 993, 990, 1000, 1980, 198, 9900, 1780, 88*11.3]:
    print(f"  1/{N} = {1.0/N:.10f} (rem×{N} = {float(rem_mp)*N:.6f})")

# ============ 5. 12.1759 身份 ============
print("\n[5] 1/rem = 12.1759 身份")
inv = mp.mpf(1)/rem_mp
print(f"  1/rem = {mp.nstr(inv, 30)}")
print(f"  1522/125 = 12.176 (誤差 {mp.nstr(abs(inv - mp.mpf(1522)/125)/abs(inv)*100, 8)}%)")
# 1522 = ? 44×34.59, 90×16.91, 134×11.36, 946×1.609
print(f"  1522 = 2×761 = {2*761}")
print(f"  1522 − 44×34 = {1522 - 44*34}")
print(f"  1522 − 90×16 = {1522 - 90*16}")
print(f"  1522 − 134×11 = {1522 - 134*11}")
print(f"  1522 − 946 = {1522 - 946}")
print(f"  1522 − 178×8 = {1522 - 178*8}")
# 12.1759 ≈ 12 + 0.1759
# 0.1759 ≈ γ_7/1.028? γ_7 = 0.180736, /1.028 = 0.1758
print(f"  12.1759 − 12 = {float(inv - 12):.8f}")
print(f"  γ_7 = {float(gamma44_mp[6]):.8f}")
print(f"  γ_7/1.028 = {float(gamma44_mp[6])/1.028:.8f}")
# 0.1759 ≈ 11/62.5? 11/62.5 = 0.176
print(f"  11/62.5 = 0.176, 62.5 = 125/2")
print(f"  12 + 11/62.5 = 12.176 = 1522/125 ✓")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("五期 16 總結:")
print("=" * 72)
print(f"""
  Σκ = {S_kappa} = −2B (B=4) ★★★
  Σ|κ| = {S_abs} ({'= 6K_tree = 198' if S_abs == 198 else '≠ 198'})

  rem = {mp.nstr(rem_mp, 25)}
  1/rem = {mp.nstr(inv, 20)} ≈ 1522/125 = 12.176 ({mp.nstr(abs(inv-mp.mpf(1522)/125)/abs(inv)*100, 6)}%)

  {'✓ rem ≈ 125/1522 係最佳閉合候選' if abs(inv-mp.mpf(1522)/125)/abs(inv) < 1e-5 else '⋯'}
""")
out = {
    "test": "O62 五期 16: Σκ 身份 + rem",
    "S_kappa": int(S_kappa), "S_abs": int(S_abs), "nnz": int(nnz),
    "S_pos": int(S_pos), "S_neg": int(S_neg), "n_pos": int(n_pos), "n_neg": int(n_neg),
    "block_sums": {f"{k}": int(v) for k, v in blocks.items()},
    "best3": [{"name": n, "val": mp.nstr(v, 15), "err": mp.nstr(e*100, 8)} for e, n, v in best3[:10]],
    "best2": [{"name": n, "val": mp.nstr(v, 15), "err": mp.nstr(e*100, 8)} for e, n, v in best2[:10]],
    "inv_rem": mp.nstr(inv, 30),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "16_sigma_kappa.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 16 完成!")
