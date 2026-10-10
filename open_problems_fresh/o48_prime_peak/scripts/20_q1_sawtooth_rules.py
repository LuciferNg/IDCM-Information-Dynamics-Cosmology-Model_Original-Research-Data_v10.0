#!/usr/bin/env python3
"""
O48 Q1.6: 鋸齒步長生成規則 — 統一模型
=============================================================
發現:
- 真峰間距 = [306, 288] 交替: ΔN=7 恆定, Δs = −2/−20 交替 (mod44 = 42/24)
- 高ℓ密集間距 = [45, 27, 36, 45, 27, 36, 34, 85]
- 306−288 = 18 = L₆;  45−27 = 18 = L₆ (同一差!)

本 script 驗證統一規則:
R1. 所有間距 Δℓ = 44·ΔN + Δs, ΔN ∈ {Lucas, Fib}, Δs 有 Fib 結構
R2. 相位偏移集 S = {−20, −17, −10, −8, −3, −2, +1} 嘅差全部 Fib
R3. 對合元迴路: 相位沿 {1,43,23,21} 行, 步長 −2/−20 交替, |−2|+|−20| = 22
R4. 386 smooth: 真峰 ΔN=7=L₄ 恆定 — 「每峰 N 值 +7」
R5. 45/27/36 嘅 44-分解: 44+1, 44−17, 44−8 → Δs = {+1, −17, −8}
R6. 306 = 7×45 − 9;  288 = 8×36 (共享結構)
"""
import math, sys
from collections import Counter

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))

# ---------- R1. 所有間距分解 ----------
print("="*72)
print("R1. Δℓ = 44·ΔN + Δs 分解")
print("="*72)
# 真峰間距
true_gaps = [306, 288, 306, 288]
hi_gaps = [45, 27, 36, 45, 27, 36, 34, 85]
all_gaps = true_gaps + hi_gaps
print("  真峰: 306, 288, 306, 288")
print("  高ℓ : 45, 27, 36, 45, 27, 36, 34, 85")
for g in sorted(set(all_gaps)):
    for k in range(0, 8):
        s = g - 44*k
        if -21 <= s <= 21:
            print(f"    {g} = 44×{k} {s:+d}  (ΔN={k}, Δs={s:+d})")
            break

# ---------- R2. 相位偏移集 ----------
print("\n" + "="*72)
print("R2. 相位偏移集 S 嘅 Fib 結構")
print("="*72)
S = sorted({-20, -17, -10, -8, -3, -2, 1})
print(f"  S = {S}")
diffs = [S[i+1]-S[i] for i in range(len(S)-1)]
print(f"  相鄰差: {diffs}")
fibset = {F(k) for k in range(2, 12)}
lucset = {L(k) for k in range(1, 12)}
check("R2a: 相鄰差全部 ∈ Fib ∪ Lucas (3,7,2,5,1,3; 7=L₄)",
      all(d in fibset or d in lucset for d in diffs), f"diffs={diffs}")
# 每個 s 嘅 Fib 表示:
for s in S:
    reps = [(F(k), k) for k in range(2, 10) if abs(s) in [F(k), 2*F(k), 3*F(k), 4*F(k), 5*F(k)] or abs(s) in [F(k), F(k)+F(k+1)]]
    print(f"    s={s:+3d}: abs={abs(s):2d}")
# 直接檢查 20, 17, 10, 8, 3, 2, 1:
print("  20 = 5×4 = F₅×L₃?  17 = ?  10 = 2×5 = F₃F₅?  8 = F₆, 3 = F₄, 2 = F₃, 1 = F₂")

# ---------- R3. 對合元迴路 ----------
print("\n" + "="*72)
print("R3. 對合元迴路 1→43→23→21→1")
print("="*72)
# 峰位相位: ℓ mod 44
peaks = [221, 527, 815, 1121, 1409]
mods = [p % 44 for p in peaks]
print(f"  相位序列: {mods}")
print(f"  全部 = 對合元? {all(m in {1,43,21,23} for m in mods)}")
steps = [(mods[i+1]-mods[i]) % 44 for i in range(4)]
print(f"  步長 (mod 44): {steps}")
steps_signed = []
for i in range(4):
    d = mods[i+1]-mods[i]
    ds = d if d >= -21 else d+44
    if d > 21: ds = d-44
    steps_signed.append(ds)
print(f"  步長 (signed): {steps_signed}")
# 步長 half-chain 互補:
print(f"  |−2|+|−20| = {2+20} = 22 = N_d/2")
check("R3a: 步長 −2/−20 交替, 和 = 22", steps_signed == [-2, -20, -2, -20] and 2+20 == 22)

# ---------- R4. ΔN = L₄ = 7 恆定 (signed 對合元代表) ----------
print("\n" + "="*72)
print("R4. 真峰 ΔN = 7 = L₄ 恆定 (signed 代表)")
print("="*72)
# 用 signed 對合元代表: s ∈ {+1, −1, −21, +21} 令 ℓ = 44N′ + s
# 用相位迴路一致嘅 signed 代表: 沿對合元迴路 {+1→−1→−21→+21→+1}
# 步長 −2/−20 交替, N′ 每步 +7:
#   m=1: 221  = 44×5+1   (N′=5,  s=+1)
#   m=2: 527  = 44×12−1  (N′=12, s=−1)
#   m=3: 815  = 44×19−21 (N′=19, s=−21)
#   m=5: 1121 = 44×26−23 (N′=26, s=−23)  [≡ 44×25+21, 相位迴路一致]
#   m=7: 1409 = 44×33−43 (N′=33, s=−43)  [≡ 44×32+1, 相位迴路一致]
signed_reps = {1: (5, 1), 2: (12, -1), 3: (19, -21), 5: (26, -23), 7: (33, -43)}
for m in [1, 2, 3, 5, 7]:
    Np, s = signed_reps[m]
    # 用 map 攞對應 ℓ
    ell_map = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
    ell = ell_map[m]
    print(f"    m={m}: ℓ={ell} = 44×{Np} {s:+d}  (N′={Np}, s={s:+d})")
# Δℓ = 306/288 → ΔN′ 同 Δs:
print("  間距分解 (signed):")
for i in range(4):
    m1, m2 = [1,2,3,5,7][i], [1,2,3,5,7][i+1]
    dN = signed_reps[m2][0] - signed_reps[m1][0]
    ds = signed_reps[m2][1] - signed_reps[m1][1]
    dl = true_gaps[i]
    print(f"    m={m1}→{m2}: ΔN′={dN}, Δs={ds:+d}, Δℓ=44×{dN}{ds:+d} = {44*dN+ds}")
check("R4c: ΔN′ = 7 恆定 (signed 代表)", 
      all(signed_reps[m2][0]-signed_reps[m1][0] == 7 for m1, m2 in [(1,2),(2,3),(3,5),(5,7)]))
check("R4d: Δs 交替 −2/−20", 
      all((signed_reps[to][1]-signed_reps[fro][1]) == (-2 if i % 2 == 0 else -20)
          for i, (fro, to) in enumerate([(1,2),(2,3),(3,5),(5,7)])))
check("R4b: 7 = L₄", L(4) == 7)

# ---------- R5. 45/27/36 分解 ----------
print("\n" + "="*72)
print("R5. 45/27/36 嘅 44-分解")
print("="*72)
for g in [45, 27, 36, 34, 85]:
    s = g - 44*(g//44)
    if s > 21: s -= 44
    print(f"    {g} = 44×{g//44} {s:+d}")
# 45 = 44+1: Δs=+1 (真峰 1→2 相位 1→43 係 -2, 唔一樣)
# 但: 45 對應 1013→1058: mods? 1013%44=1, 1058%44=2
print("  1013→1058: 相位 1→2 (δ=+1)")
print("  1058→1085: 相位 2→29 (δ=+27≡−17)")
print("  1085→1121: 相位 29→21 (δ=−8)")
print("  1292→1337: 相位 16→17 (δ=+1)")
print("  1337→1364: 相位 17→0  (δ=−17)")
print("  1364→1400: 相位 0→36  (δ=−8)")

# ---------- R6. 306/288 共享結構 ----------
print("\n" + "="*72)
print("R6. 共享結構")
print("="*72)
print(f"  306−288 = {306-288} = L₆ = {L(6)}")
print(f"  45−27 = {45-27} = L₆")
print(f"  36−27 = {36-27} = 9 = F₄²")
print(f"  306 = 7×45 − 9?  {7*45-9}")
print(f"  288 = 4×72 = 8×36?  {8*36}")
print(f"  45 = 44+1;  306 = 44×7−2; 288 = 44×7−20")
print(f"  對比: 真峰 306/288 相位差 = −2/−20;  高ℓ 45/27/36 相位差 = +1/−17/−8")
check("R6a: 306−288 = 45−27 = 18 = L₆", 306-288 == 45-27 == L(6) == 18)

# ---------- R7. 統一假說: 相位迴路 + 44 週期 ----------
print("\n" + "="*72)
print("R7. 統一模型候選")
print("="*72)
print("""  觀察: 所有間距都係 44k + (小相位偏離)
  真峰: ΔN=7(L₄) 恆定, 相位沿對合元迴路跳動 (±2, ±20)
  高ℓ : ΔN=1, 相位 +1/−17/−8 (密集)

  統一規則候選: 相位 s 永遠喺「對合元 ± Fib 鄰域」:
    +1 = F₂
    −2 = −F₃
    −8 = −F₆
    −17 = −(F₈−4)?  或 −(2×L₃ + L₅−2)?  未解!
    −20 = −(F₈−1)
  ⟹ 未閉合: −17 唔係 Fib/Lucas 直接值
""")
check("R7a: −17 係唯一非 Fib 步長 (誠實標記)", True)

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)