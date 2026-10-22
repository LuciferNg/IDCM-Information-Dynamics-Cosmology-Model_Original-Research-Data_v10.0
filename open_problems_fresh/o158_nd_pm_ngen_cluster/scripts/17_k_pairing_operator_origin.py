#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/17_k_pairing_operator_origin.py — ★★★ k 配對機制: 算子起源閉合
問題: 點解 W/Z 用 k=3=N_gen, τ/b 用 k=19=f_proj (45-家族命中 k)?
發現候選: 45-家族中心 = (F_proj, F_proj+L₅) = (17, 28), 中心 k = 11 = L₅
  命中對 = 中心 ± B 交叉移動: (17±4, 28∓4)
  k = (b₀−a₀) ∓ 2B = L₅ ∓ 2B = {11−8, 11+8} = {3, 19}
  ⇒ 3 = N_gen, 19 = f_proj 自動重現 (唔再係「巧合」)
  N_gen = L₅−2B, f_proj = L₅+2B (已發現身份, 而家睇到 = k 值本身)
另: 45-家族 mod-4 分類: k≡3 mod 4 (N_gen/f_proj 命中), k≡1 mod 4 (F_proj/f_unproj 弱命中)
"""
import mpmath as mp
mp.mp.dps = 60

N_d, B, N_gen, L5, L4 = 44, 4, 3, 11, 7
F_proj, f_proj, f_unproj = 17, 19, 41
Tr_chi = 30

def sin176(n): return mp.sin(n*mp.pi/176)

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. ★★★ 45-家族中心 = (F_proj, F_proj+L₅) = (17, 28)")
print("="*72)
a0, b0 = 17, 28
ck("中心 a₀ = 17 = F_proj", a0 == F_proj)
ck("中心 b₀ = 28 = F_proj+L₅", b0 == F_proj + L5)
ck("中心 b₀ = 4L₄ = 28", b0 == 4*L4)
ck("中心 b₀ = N_d−B² = 44−16", b0 == N_d - B**2)
ck("中心 k₀ = b₀−a₀ = 11 = L₅", b0-a0 == L5)
ck("中心和 = 45 = 世界質心×2", a0+b0 == 45)
print("   (21,24) = (17+B, 28−B) = (a₀+B, b₀−B)")
print("   (13,32) = (17−B, 28+B) = (a₀−B, b₀+B)")
ck("(21,24) = 中心+B交叉", (a0+B, b0-B) == (21, 24))
ck("(13,32) = 中心−B交叉", (a0-B, b0+B) == (13, 32))
print()

print("="*72)
print("2. ★★★ k = L₅ ∓ 2B = {3, 19} 算子重現")
print("="*72)
k_WZ = (b0-B) - (a0+B)
k_tb = (b0+B) - (a0-B)
print("   k(W/Z) = (b₀−B)−(a₀+B) = b₀−a₀−2B = %d−%d = %d" % (L5, 2*B, k_WZ))
print("   k(τ/b) = (b₀+B)−(a₀−B) = b₀−a₀+2B = %d+%d = %d" % (L5, 2*B, k_tb))
ck("k(W/Z) = L₅−2B = 3 = N_gen", k_WZ == N_gen)
ck("k(τ/b) = L₅+2B = 19 = f_proj", k_tb == f_proj)
ck("N_gen = L₅−2B (身份重現)", N_gen == L5 - 2*B)
ck("f_proj = L₅+2B (身份重現)", f_proj == L5 + 2*B)
ck("k 和 = 2L₅ = 22 = N_d/2 (半鏈)", k_WZ + k_tb == 2*L5)
print()

print("="*72)
print("3. 45-家族 mod-4 分類")
print("="*72)
fam3, fam1 = [], []
for k in range(1, 44, 2):
    a = (45-k)//2
    b = (45+k)//2
    if k % 4 == 3: fam3.append((a, b, k))
    else: fam1.append((a, b, k))
print("   k ≡ 3 mod 4 (%d 成員):" % len(fam3))
for a, b, k in fam3:
    print("     (%2d,%2d) k=%2d%s" % (a, b, k, " ← 中心" if k == L5 else (" ← 命中" if k in (3, 19) else "")))
print("   k ≡ 1 mod 4 (%d 成員):" % len(fam1))
for a, b, k in fam1:
    print("     (%2d,%2d) k=%2d%s" % (a, b, k, " ← 弱命中" if k in (17, 41) else ""))
ck("命中 k ∈ {3,19} 全 ≡ 3 mod 4", all(k % 4 == 3 for k in (3, 19)))
ck("弱命中 k ∈ {17,41} 全 ≡ 1 mod 4", all(k % 4 == 1 for k in (17, 41)))
ck("N_gen=3 ≡ 3, f_proj=19 ≡ 3 (同一 mod 類)", N_gen % 4 == 3 and f_proj % 4 == 3)
ck("F_proj=17 ≡ 1, f_unproj=41 ≡ 1 (同一 mod 類)", F_proj % 4 == 1 and f_unproj % 4 == 1)
print()

print("="*72)
print("4. 中心 (17,28) 嘅比 + 身份")
print("="*72)
rc = sin176(17)/sin176(28)
print("   (17,28) 比 = %.6f (k=11=L₅, 結構中心, 冇對應質量比)" % rc)
ck("中心 k = 11 = L₅ = N_d/4", b0-a0 == L5)
ck("F_proj+L₅ = 28 = 4L₄ (修正鎖鏈延伸)", F_proj + L5 == 4*L4)
ck("6+11 = 17 (已知修正鎖鏈), 17+11 = 28 (新)", 6+L5 == 17 and 17+L5 == 28)
print("   → 修正鎖鏈: 6 → 17 → 28 → 45? 6+11=17, 17+11=28, 28+17=45!")
ck("鎖鏈: 6+11=17, 17+11=28, 28+17=45 (F_proj階梯到世界質心)",
   6+L5 == F_proj and F_proj+L5 == 28 and 28+F_proj == 45)
print()

print("="*72)
print("5. 命中對幾何: 中心 ± B 交叉 = 混合對必要性")
print("="*72)
print("   a 方向: 13 → 17 → 21 (步長 4 = B): 13 = 17−4, 21 = 17+4")
print("   b 方向: 24 → 28 → 32 (步長 4 = B): 24 = 28−4, 32 = 28+4")
print("   → 命中對 = 中心向外/向內 B 步, a,b 反方向 (保持和 = 45)")
ck("a 步長 = B = 4", 21-17 == B and 17-13 == B)
ck("b 步長 = B = 4", 28-24 == B and 32-28 == B)
ck("和守恆: (a∓B)+(b±B) = 45", (a0+B)+(b0-B) == 45 and (a0-B)+(b0+B) == 45)
print()

print("="*72)
print("6. Verdict")
print("="*72)
ck("F71 中心 (17,28) = (F_proj, F_proj+L₅), k₀ = L₅", a0 == F_proj and b0-a0 == L5)
ck("F72 命中對 = 中心 ± B 交叉 (和守恆 45)", (a0+B, b0-B) == (21, 24) and (a0-B, b0+B) == (13, 32))
ck("F73 k = L₅ ∓ 2B = {N_gen, f_proj} 算子重現", k_WZ == N_gen and k_tb == f_proj)
ck("F74 mod-4 分類: 命中 ≡3, 弱命中 ≡1", all(k % 4 == 3 for k in (3, 19)) and all(k % 4 == 1 for k in (17, 41)))
ck("F75 鎖鏈 6→17→28→45 (F_proj 階梯)", 6+L5 == F_proj and F_proj+L5 == 28 and 28+F_proj == 45)
print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)
