#!/usr/bin/env python3
"""35 — (c1) co-closure 測試: δ 嘅 shared-sum s 由 θ₂₃ 閉合條件強制?
假說: θ₂₃ 分母 (d19, s) 同 δ 兩對 (d21,s)+(d9,s) 共享 column; s 一變, θ₂₃ 值變。
邊個 s ∈ {23..67} 令 θ₂₃(s) 保持 2.379994° (tol)? 如果唯一 = s=25, (c1) 閉合。
"""
import math

w = lambda n: 2*math.sin(n*math.pi/88)
beat = lambda a,b: abs(w(a)-w(b))
THETA23 = math.atan(beat(33,35)/beat(3,22))   # 框架值 2.379994°
THETA23D = math.degrees(THETA23)
print(f"框架 θ₂₃ = {THETA23D:.6f}°  (分母 (3,22) = d19, s25)")

def cdist(a, b):
    d = abs(a - b) % 5
    return min(d, 5 - d)

print(f"\n{'s':>3} {'δnum (d21)':>12} {'δden (d9)':>12} {'θ₂₃den (d19)':>13}  charges(δnum,δden,θ23den)  θ₂₃(s)°   Δθ₂₃°")
results = []
for s in range(23, 68, 2):
    # 三個對: (d21,s), (d9,s), (d19,s) — 全部由 (d,s) 唯一確定
    a1, b1 = (s+21)//2, (s-21)//2   # δ numerator  (d=21)
    a2, b2 = (s+9)//2, (s-9)//2     # δ denominator (d=9)
    a3, b3 = (s+19)//2, (s-19)//2   # θ₂₃ denominator (d=19)
    # validity: indices in [1,44], Z5-adjacent
    ok = all(1 <= x <= 44 for x in (a1,b1,a2,b2,a3,b3))
    adj = cdist(a1,b1)==1 and cdist(a2,b2)==1 and cdist(a3,b3)==1
    if not (ok and adj):
        continue
    t23 = math.degrees(math.atan(beat(33,35)/beat(a3,b3)))
    dt = t23 - THETA23D
    c1, c2, c3 = (a1%5,b1%5), (a2%5,b2%5), (a3%5,b3%5)
    results.append((s, dt, t23, (c1,c2,c3)))
    print(f"{s:3d} ({a1:2d},{b1:2d})  ({a2:2d},{b2:2d})  ({a3:2d},{b3:2d})   {c1}{c2}{c3}  {t23:9.4f}  {dt:+8.4f}")

print(f"\n--- tol 分析 (Δθ₂₃ 絕對值) ---")
for tol in (0.02, 0.05, 0.1):
    hits = [(s, r[1]) for s, r in zip([x[0] for x in results], results) if abs(r[1]) < tol]
    print(f"tol={tol}°: {len(hits)} 個 s → {hits if hits else '無'}")

print("\n--- charges 結構 (θ₁₃ num (42,43)=(3,2); θ₂₃ den 框架 (3,22)=(2,3)) ---")
for s, dt, t23, c in results:
    mark = "  ← δnum=(3,2)且δden=(2,3)" if c[0]==(3,2) and c[1]==(2,3) else ""
    print(f"s={s:2d}: δnum{c[0]} δden{c[1]} θ23den{c[2]}{mark}")

print("\n--- 結論 ---")
hits25 = [r for r in results if abs(r[1]) < 0.02]
if len(hits25) == 1 and hits25[0][0] == 25:
    print("s=25 係 tol 0.02° 內唯一令 θ₂₃ 閉合嘅 shared-sum → (c1) 閉合: δ 嘅 s 由 θ₂₃ co-closure 強制")
else:
    print(f"tol 0.02° 內 {len(hits25)} 個: {hits25} — (c1) 未閉合")
