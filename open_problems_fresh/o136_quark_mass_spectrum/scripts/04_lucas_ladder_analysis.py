#!/usr/bin/env python3
"""
O136 -- Lucas 阶梯选择律推导
================================================================
从方向二 (Z2xZ2 宇称截断与 Lucas 阶梯) 推导模式分配原理。

核心问题: 为什么轻子选择 n=1, 7, 20？
方法: 检查 gamma_n/gamma_1 比值是否精确等于 Lucas 数组合。
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1 + mp.sqrt(5))/2
pi = mp.pi

# Lucas 数 (Python int)
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]

Nd = 44

# K_Chain 谱 (返回 float)
gamma = lambda n: float(4 * mp.sin(n * pi / 88)**2)

print("=" * 78)
print("Lucas 阶梯选择律 -- gamma_n/gamma_1 比值分析")
print("=" * 78)

g1 = gamma(1)
print(f"\ngamma_1 = 4sin^2(pi/88) = {g1:.12f}")

# 计算所有 n 的 gamma_n/gamma_1 比值
print(f"\n{'n':>3} {'gamma_n':>14} {'ratio':>14} {'Lucas 候选':>20} {'偏差':>10}")
print("-" * 65)

for n in range(1, 45):
    g = gamma(n)
    ratio = g / g1
    marker = ""
    candidate = ""
    dev = ""
    
    if n == 1:
        candidate = "1 = L1"
        dev = "0%"
        marker = "  <- 轻子"
    elif n == 7:
        target = Nd + L[3]  # 48
        dev = f"{abs(ratio - target) / target * 100:.6f}%"
        candidate = f"{Nd}+L3={target}"
        marker = "  <- 轻子"
    elif n == 20:
        target = L[4] * (Nd + L[3])  # 336
        dev = f"{abs(ratio - target) / target * 100:.6f}%"
        candidate = f"L4x({Nd}+L3)={target}"
        marker = "  <- 轻子"
    else:
        # Try to find Lucas match
        for i, li in enumerate(L):
            if li > 0:
                dev_f = abs(ratio - li) / li * 100
                if dev_f < 1.0:
                    candidate = f"L{i}={li}"
                    dev = f"{dev_f:.4f}%"
                    break
        if not candidate:
            for i, li in enumerate(L):
                for op, val in [("+", Nd + li), ("-", Nd - li)]:
                    if val > 0:
                        dev_f = abs(ratio - val) / val * 100
                        if dev_f < 1.0:
                            candidate = f"Nd{op}L{i}={val}"
                            dev = f"{dev_f:.4f}%"
                            break
                if candidate:
                    break
    
    print(f"{n:>3} {g:>14.8f} {ratio:>14.6f} {candidate:>20} {dev:>10}{marker}")

# 精确检查
print(f"\n{'='*78}")
print("精确恒等式验证:")
print(f"{'='*78}")

# gamma_7/gamma_1
r7 = gamma(7) / gamma(1)
t7 = Nd + L[3]
print(f"\ngamma_7/gamma_1 = {r7:.15f}")
print(f"Nd + L3 = {Nd} + {L[3]} = {t7}")
print(f"差 = {r7 - t7}")
print(f"偏差 = {abs(r7 - t7) / t7 * 100:.10f}%")

# gamma_20/gamma_1
r20 = gamma(20) / gamma(1)
t20 = L[4] * (Nd + L[3])
print(f"\ngamma_20/gamma_1 = {r20:.15f}")
print(f"L4 x (Nd + L3) = {L[4]} x ({Nd + L[3]}) = {t20}")
print(f"差 = {r20 - t20}")
print(f"偏差 = {abs(r20 - t20) / t20 * 100:.10f}%")

# gamma_20/gamma_7
r20_7 = gamma(20) / gamma(7)
print(f"\ngamma_20/gamma_7 = {r20_7:.15f}")
print(f"L4 = {L[4]}")
print(f"差 = {r20_7 - L[4]}")
print(f"偏差 = {abs(r20_7 - L[4]) / L[4] * 100:.10f}%")

# 世代关系总结
print(f"\n{'='*78}")
print("世代关系总结:")
print(f"{'='*78}")

print(f"\n第1代 (n=1):  gamma_1/gamma_1 = 1 = L1")
print(f"第2代 (n=7):  gamma_7/gamma_1 = Nd + L3 = {Nd} + {L[3]} = {Nd + L[3]}")
print(f"第3代 (n=20): gamma_20/gamma_1 = L4 x (Nd + L3) = {L[4]} x {Nd + L[3]} = {L[4] * (Nd + L[3])}")
print(f"\ngamma_20/gamma_7 = L4 = {L[4]}")

# 检查 n=1,7,20 与 Lucas 数的直接关系
print(f"\n{'='*78}")
print("n值与Lucas数的关系:")
print(f"{'='*78}")

print(f"\nn=1  = L1 = {L[1]}")
print(f"n=7  = L4 = {L[4]}")
print(f"n=20 = L6 + L0 = {L[6]} + {L[0]} = {L[6] + L[0]}")
print(f"     = L5 + L4 + L2 - L1 = {L[5]} + {L[4]} + {L[2]} - {L[1]} = {L[5]+L[4]+L[2]-L[1]}")

# 检查所有 n 的精确 Lucas 关系
print(f"\n{'='*78}")
print("所有 n 的精确 Lucas 关系搜索 (gamma_n/gamma_1):")
print(f"{'='*78}")

print(f"\n{'n':>3} {'ratio':>12} {'候选':>24} {'val':>8} {'dev%':>10}")
print("-" * 60)
for n in range(1, 45):
    ratio = gamma(n) / gamma(1)
    best = (float('inf'), "", 0)
    # 单 Lucas
    for i, li in enumerate(L):
        if li > 0:
            dev_f = abs(ratio - li) / li * 100
            if dev_f < best[0]:
                best = (dev_f, f"L{i}", li)
    # Nd +/- Lucas
    for i, li in enumerate(L):
        for op, val in [("+", Nd + li), ("-", Nd - li)]:
            if val > 0:
                dev_f = abs(ratio - val) / val * 100
                if dev_f < best[0] and dev_f < 1.0:
                    best = (dev_f, f"Nd{op}L{i}", val)
    # L * (Nd + L)
    for i, li in enumerate(L):
        for j, lj in enumerate(L):
            val = li * (Nd + lj)
            if val > 0:
                dev_f = abs(ratio - val) / val * 100
                if dev_f < best[0] and dev_f < 1.0:
                    best = (dev_f, f"L{i}x(Nd+L{j})", val)
    
    dev, label, val = best
    if dev < 1.0:
        print(f"{n:>3} {ratio:>12.6f} {label:>24} {val:>8} {dev:>9.4f}%")