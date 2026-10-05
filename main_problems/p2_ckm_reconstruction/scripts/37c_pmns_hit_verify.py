#!/usr/bin/env python3
"""37c — θ₁₃ hit 驗證 + full-beat-class null-control @1e-8
問題: 37b 揾到 θ₁₃ tan 一個 hit ((16,19),(34,64)) — 驗證係咪真 + 隨機 target 命中率
"""
import numpy as np, random

N = 88
sinv = np.sin(np.arange(1, N+1)*np.pi/176.0)
pairs = [(a,b) for a in range(1,N) for b in range(a+1,N+1)]
beats = np.array([2*abs(sinv[a-1]-sinv[b-1]) for a,b in pairs])
M = len(pairs)

# 1) 直接驗證 θ₁₃ hit
t13 = np.tan(np.radians(8.54))
i = pairs.index((16,19)); j = pairs.index((34,64))
r = beats[i]/beats[j]
print(f"θ13 hit 驗證: beat(16,19)/beat(34,64) = {r:.12f}, tan(8.54°) = {t13:.12f}, |Δ| = {abs(r-t13):.3e}")
print(f"  (16,19): d={3} s={35}; (34,64): d={30} s={98}")

# 2) null-control: 100 random targets @1e-8
rng = random.Random(7)
hits_all = []
for k in range(100):
    t = 10**rng.uniform(-1.5, 0.5)  # 0.03..3.2
    cnt = 0
    for i in range(M):
        cnt += int((np.abs(beats[i]/beats - t) < 1e-8).sum())
    hits_all.append(cnt)
hits_all = np.array(hits_all)
print(f"\nnull-control @1e-8 (100 random targets): hits/target: mean={hits_all.mean():.3f}, "
      f"max={hits_all.max()}, P(≥1 hit)={(hits_all>=1).mean()*100:.0f}%")

# 3) 對照: 三個真實 PMNS target
for name, deg in [("θ12",33.41),("θ23",42.2),("θ13",8.54)]:
    t = np.tan(np.radians(deg))
    cnt = 0
    for i in range(M):
        cnt += int((np.abs(beats[i]/beats - t) < 1e-8).sum())
    print(f"  {name} tan={t:.8f}: {cnt} hits @1e-8")

print("\nRESULT: 驗證完成")
