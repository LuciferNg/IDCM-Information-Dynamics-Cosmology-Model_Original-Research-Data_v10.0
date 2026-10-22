#!/usr/bin/env python3
"""
O154 S02: 鏈聲子 DOS + beat 膠譜 — 配對「膠水」候選
================================================================
A. 鏈聲子譜: ω_k = 2sin(kπ/176), k=1..88
   DOS g(ω) ∝ 1/√(1−(ω/2)²) — 1D 鏈, ω_max=2 有 van Hove 奇異點
   → α²F 形狀: 高頻權重峰值 (H 聲子主導 = 氫化物高 Tc 嘅結構原因)

B. O149 定理 1 驗證 (946/946): beat(a,b) = 4sin(dπ/176)·v_g((a+b)/2)
   v_g(m) = c·cos(πm/88)  (44-chain 語言, O149 定理 2: ω_n = 2v_g(44−n))

C. Beat 譜統計: 946 個拍頻嘅分佈、極值、中位數
   → 拍頻 = 聲子差頻 = 配對能量窗口候選

D. 鏈聲子譜矩: ω_log, ⟨ω⟩, ⟨ω²⟩, ω_max/ω_log — 餵入 Eliashberg (S03)
"""
import numpy as np
from itertools import combinations

print("=" * 78)
print("  O154 S02: 鏈聲子 DOS + beat 膠譜")
print("=" * 78)

# ---- A. 鏈聲子譜 ----
N88 = 88
k = np.arange(1, N88 + 1)
omega = 2.0 * np.sin(k * np.pi / 176)   # ω_max = 2
gamma = omega ** 2

print("\n[A] 鏈聲子譜 ω_k = 2sin(kπ/176)")
print(f"  ω_max = {omega.max():.6f} (k=88), ω_min = ω₁ = {omega.min():.8f}")
print(f"  ⟨ω⟩ = {omega.mean():.8f}, ⟨ω²⟩ = ⟨γ⟩ = {gamma.mean():.8f} = 178/88 = 89/44")
print(f"  ω_log = {np.exp(np.mean(np.log(omega))):.8f} = 352^(1/176)")
print(f"  1D 鏈 DOS: g(ω) ∝ 1/√(1−(ω/2)²) — van Hove 奇異點 @ ω_max=2")

# DOS 直方圖 (van Hove 峰)
hist, edges = np.histogram(omega, bins=20, range=(0, 2.05))
print("  DOS 直方圖 (van Hove 峰應喺最高頻 bin):")
for i, (h, e) in enumerate(zip(hist, edges[:-1])):
    bar = "#" * int(h / hist.max() * 40)
    print(f"    ω ∈ [{e:.2f},{edges[i+1]:.2f}): {h:3d} {bar}")

# ---- B. O149 定理 1 驗證 ----
print("\n[B] O149 定理 1 驗證: beat(a,b) = 4sin(dπ/176)·v_g((a+b)/2)")
# 44-chain 模式 n=1..44, ω_n = 2sin(nπ/88) (O149 定理 2: ω_n = 2v_g(44−n))
n = np.arange(1, 45)
w44 = 2.0 * np.sin(n * np.pi / 88)
vg = lambda m: np.cos(m * np.pi / 88)  # v_g 喺 c 單位 (O149)

count = 0
max_dev = 0.0
for a, b in combinations(range(1, 45), 2):
    d = abs(a - b)
    beat_lhs = abs(w44[a - 1] - w44[b - 1])            # |ω_a − ω_b|
    beat_rhs = 4.0 * np.sin(d * np.pi / 176) * vg((a + b) / 2.0)
    dev = abs(beat_lhs - beat_rhs)
    max_dev = max(max_dev, dev)
    if dev < 1e-12:
        count += 1
print(f"  beat 恆等: {count}/946 PASS, max dev = {max_dev:.2e}")
assert count == 946

# ---- C. Beat 譜統計 ----
print("\n[C] Beat 譜 (946 個差頻)")
beats = []
for a, b in combinations(range(1, 45), 2):
    beats.append(abs(w44[a - 1] - w44[b - 1]))
beats = np.array(beats)
print(f"  beats: min = {beats.min():.8f}, max = {beats.max():.6f}, mean = {beats.mean():.8f}")
print(f"  中位數 = {np.median(beats):.8f}")
# 最大 beats 嘅 (a,b)
idx = np.argsort(beats)[-10:][::-1]
pairs = list(combinations(range(1, 45), 2))
print("  最大 10 個 beat:")
for i in idx:
    a, b = pairs[i]
    print(f"    beat({a},{b}) = {beats[i]:.6f}  (d={abs(a-b)}, (a+b)/2={(a+b)/2})")

# beat 嘅對數平均 (膠水 ω_log 候選)
bl_log = np.exp(np.mean(np.log(beats[beats > 0])))
print(f"  beat 幾何平均 = {bl_log:.8f}")

# ---- D. 譜矩 (Eliashberg 輸入) ----
print("\n[D] 譜矩 (S03 Eliashberg 輸入)")
print(f"  ω_log = {np.exp(np.mean(np.log(omega))):.8f} (鏈單位, ω_max=2)")
print(f"  ω²_avg = ⟨γ⟩ = {gamma.mean():.8f}")
print(f"  ω_log/ω_max = {np.exp(np.mean(np.log(omega)))/2.0:.6f}")
print()
print("PASS")
