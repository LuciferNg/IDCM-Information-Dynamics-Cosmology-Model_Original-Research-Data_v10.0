#!/usr/bin/env python3
"""37a — V_ub 張力: 結構修正搜尋
s₁₃(beat) = 0.0035074294 vs PDG V_ub = 0.00369 → 修正因子 C = 1.05219
搜尋: (1) rational a/b (a,b 結構數), (2) beat-ratio corrections, (3) trig corrections
判準: 唔可以 φ-trap (φ-power 禁), 要 R12 合規 (有理 or Q(ζ₁₇₆)⁺)
"""
import math

w = lambda n: 2*abs(math.sin(math.pi*n/88))
beat = lambda i,j: abs(w(i)-w(j))

s13 = 0.0035074294
target = 0.00369
C = target / s13
print(f"s₁₃ = {s13:.10f}, target = {target}, C = {C:.6f}")

# 結構數集 (framework 常用)
S = [1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,27,29,30,31,32,33,34,35,36,38,39,40,41,42,43,44,47,55,60,63,66,68,77,85,88]

print("\n=== 1) rational 修正 a/b ≈ C ===")
hits = []
for a in S:
    for b in S:
        if b == 0: continue
        r = a/b
        if abs(r - C) < 5e-4:
            hits.append((a, b, r, abs(r-C)))
hits.sort(key=lambda x: x[3])
for a, b, r, e in hits[:15]:
    print(f"  {a:3d}/{b:3d} = {r:.6f} (err {e:.2e})")

print("\n=== 2) beat-ratio 修正 beat(i,j)/beat(k,l) ≈ C (結構 pairs) ===")
# 用 D6/S6 web 嘅 15 個有效組合 + 常用對
web_pairs = [(5,6),(19,25),(33,35),(3,22),(42,43),(10,31),(2,23),(8,17),
             (13,12),(21,20),(37,31),(10,1),(25,16),(30,11),(23,21)]
hits2 = []
for p1 in web_pairs:
    for p2 in web_pairs:
        if p1 == p2: continue
        b1, b2 = beat(*p1), beat(*p2)
        if b2 < 1e-12: continue
        r = b1/b2
        if abs(r - C) < 5e-3:
            hits2.append((p1, p2, r, abs(r-C)))
hits2.sort(key=lambda x: x[3])
for p1, p2, r, e in hits2[:10]:
    print(f"  beat{p1}/beat{p2} = {r:.6f} (err {e:.2e})")

print("\n=== 3) trig 修正 sin(aπ/176)/sin(bπ/176) ≈ C ===")
hits3 = []
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        r = math.sin(a*math.pi/176)/math.sin(b*math.pi/176)
        if 0.8 < r < 1.3 and abs(r - C) < 5e-3:
            hits3.append((a, b, r, abs(r-C)))
hits3.sort(key=lambda x: x[3])
for a, b, r, e in hits3[:10]:
    print(f"  sin({a})/sin({b}) = {r:.6f} (err {e:.2e})")

print("\n=== 4) C 嘅精確分解: 1 + 1/19 = 20/19? ===")
print(f"  20/19 = {20/19:.6f} vs C = {C:.6f} (err {abs(20/19-C):.2e})")
print(f"  s₁₃×20/19 = {s13*20/19:.6f} vs PDG 0.00369 (err {abs(s13*20/19-0.00369)/0.00369*100:.3f}%)")
# 檢查 19 同 20 嘅身份
print(f"  19 = L₆+1 (D6 成員), 20 = B×F₅ = N_d−B")
# 有冇 chain 角度: 0.0104° = ?
dang = math.degrees(math.asin(target)) - math.degrees(math.asin(s13))
print(f"\nθ₁₃ 差 = {dang:.6f}° = {math.radians(dang):.6f} rad")
for k in range(1, 30):
    v = k*math.pi/176
    if abs(v - math.radians(dang)) < 0.01*math.radians(dang):
        print(f"  近似 kπ/176: k={k} ({math.degrees(v):.6f}°)")
# 1/19 rad?
print(f"  1/19 rad = {math.degrees(1/19):.4f}°; 1/19 對應 sin 修正 sin(1)/sin(19)? = {math.sin(math.pi/176)/math.sin(19*math.pi/176):.6f}")
