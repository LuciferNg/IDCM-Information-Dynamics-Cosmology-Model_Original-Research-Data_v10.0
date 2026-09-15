#!/usr/bin/env python3
# O200 scripts/12 — 攻堅: δ=±1 根譜 j_k 統一 (|r_k| ≈ j_k/2)
# 觀察: |r₁| = 1.202532 ≈ j₁/2; |r₃| = 2.760318 ≈ j₂/2; |r₅| = 4.3273 ≈ j₃/2
# 假說: δ=±1 根配對 (r_k, r_{k+1}) 貼近 j_k/2 (J₀ 第 k 個零點嘅一半)
# 機制: 88·I₀(2t) = sinh(2t); I₀(ij_k) = J₀(j_k) = 0 ⟹ 2t ≈ ij_k ⟹ t ≈ ij_k/2
#        sinh 相位推離 ⟹ Re ≠ 0, |t| 微偏離 j_k/2
# 驗證: 掃描頭 8 對根, |t| vs j_k/2 dev, 推離量 Re(r) 結構
import mpmath as mp

mp.mp.dps = 60
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def find_pairs(NPAIRS):
    """搵 δ=+1 根 (上半平面), 每對 (k 偶數=2j-1 index) 對應 j_j"""
    roots = []
    # 初始猜測: j_k/2 附近
    for k in range(1, NPAIRS+1):
        jk = mp.besseljzero(0, k)
        t0 = mp.mpc(0, jk/2)
        # 用牛頓 (複平面) — 88I₀(2t) − sinh(2t) = 0
        r = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), 
                        mp.mpc('0.0074' if k == 1 else '0.01', jk/2), 
                        tol=1e-40, maxsteps=100)
        roots.append(r)
    return roots

print("== δ=+1 根譜 vs j_k/2 (J₀ 零點) ==")
print(f"{'k':>2} {'j_k':>12} {'j_k/2':>12} {'|r|':>12} {'dev':>12} {'Re(r)':>12} {'Im(r)':>12}")
pairs = find_pairs(8)
ok = True
for k, r in enumerate(pairs, start=1):
    jk = mp.besseljzero(0, k)
    dev = abs(abs(r) - jk/2)/(jk/2)
    if dev > 1e-3: ok = False
    print(f"{k:>2} {mp.nstr(jk, 10):>12} {mp.nstr(jk/2, 12):>12} {mp.nstr(abs(r), 12):>12} "
          f"{mp.nstr(dev, 10):>12} {mp.nstr(r.real, 10):>12} {mp.nstr(r.imag, 10):>12}")
check(f"δ=+1 根 |r_k| ≈ j_k/2 (dev < 1e-3, 頭 8 對)", ok)

# 推離量 Re(r_k) 結構
print("\n== Re(r_k) 推離量結構 ==")
Re_vals = [r.real for r in pairs]
print("  Re(r_k):", " ".join(mp.nstr(x, 8) for x in Re_vals))
# 一階公式 (k=1 已推): Re ≈ sin(j_k)/(176·J₁(j_k)·?) — 一般化
# 88·ε·i·J₁(j_k) = i·sin(j_k) + ε·cos(j_k) ⟹ ε = i·sin(j_k)/(88·i·J₁(j_k) − cos(j_k))
print("\n  一階極點推離 (一般 k): ε_k = i·sin(j_k)/(88·i·J₁(j_k) − cos(j_k)), Re = Re(ε)/2")
for k, r in enumerate(pairs, start=1):
    jk = mp.besseljzero(0, k)
    J1k = mp.besselj(1, jk)
    sk, ck = mp.sin(jk), mp.cos(jk)
    eps = mp.mpc(0, sk)/(88*mp.mpc(0, J1k) - ck)
    Re_pred = eps.real/2
    dev = abs(Re_pred - r.real)/abs(r.real)
    print(f"  k={k}: 一階 Re = {mp.nstr(Re_pred, 10)}, 實際 = {mp.nstr(r.real, 10)}, dev = {mp.nstr(dev, 8)}")

# sin(j_k) 符號: j_k 喺 (0,π) 間隔, sin 正負交替?
print("\n  sin(j_k) 符號:", " ".join("+" if mp.sin(mp.besseljzero(0,k)) > 0 else "-" for k in range(1, 9)))
print("  cos(j_k) 符號:", " ".join("+" if mp.cos(mp.besseljzero(0,k)) > 0 else "-" for k in range(1, 9)))
# 呢個決定 Re 符號 (推離方向)

# j_k 統一嘅物理讀取
print("\n== 結構讀取 ==")
print("  δ=±1 根譜 = {t: 88I₀(2t) = ±sinh(2t)} — I₀ 零點 ij_k/2 附近")
print("  J₀ 零點 j_k = 觀察者/世界界面振盪節點 (O195: 4/j₁² 控制 κ)")
print("  ⟹ 奇異點譜由 J₀ 零點決定, sinh 係推離勢")
print("  |r_k| ≈ j_k/2 dev ~1e-4: 極點吸引 (I₀ 零點) vs sinh 推離 (相位) 平衡")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
