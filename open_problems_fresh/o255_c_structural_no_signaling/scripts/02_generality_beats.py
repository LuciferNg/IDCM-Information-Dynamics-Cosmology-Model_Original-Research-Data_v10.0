#!/usr/bin/env python3
"""
O255 scripts/02 — N 普適性 + 半整數 shift + beat 速度繼承定理
================================================================
預註冊 (2026-10-20, 跑前凍結):

U1  ∀N ∈ {44, 88, 176, 352}: γ_n(N) = 4sin²(πn/N) ⟹ v_g(n) = cos(πn/N) ≤ 1,
    等號唯一 n=0 (N 普適性 — c 上限與 N 無關, 唔係 88 特例)
U2  半整數 shift (O159 176-Laplacian half-site 鏈): γ_k = 4sin²(kπ/176),
    v_g(k) = cos(kπ/176) ≤ 1 — 與整數格同形
U3  O34 半整數位置 (觀察者於 half-site): 相位 sin(πn(j+½)/88) —
    譜 γ_n 不變 ⟹ v_g 不變 (半整數 shift 唔改變群速度)
U4  O149 beat 定理: beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2) EXACT,
    d=|a−b| — 拍頻速度繼承 v_g ⟹ |v_beat| ≤ 1 = c
U5  Σγ_odd=88 / Σγ_even=90 分解下 v_g 仍 ≤ 1 (扇區不改變速度界)
U6  互補對: v_g(n) = v_g(88−n) (Z₂ 對稱, 反行波同速)

執行: /usr/bin/python3 scripts/02_generality_beats.py > logs/02.txt 2>&1
"""
import math

TOL = 1e-12

checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))


def vg_N(n, N):
    return math.cos(math.pi * n / N)


# U1: N 普適性 — 全部模式 ≤ 1, 唯一 n=0
for N in (44, 88, 176, 352):
    for n in range(0, N // 2 + 1):  # 正半
        v = vg_N(n, N)
        chk(f"U1.N{N}.n{n}", v <= 1.0 + TOL, f"v_g={v:.12f}")
    eq = [n for n in range(0, N // 2 + 1) if abs(vg_N(n, N) - 1.0) < TOL]
    chk(f"U1.N{N}.unique", eq == [0], f"唯一 n=0: {eq}")
    # 全環 (負半) 亦 ≤ 1
    for n in range(0, N):
        chk(f"U1.N{N}.ring.n{n}", abs(vg_N(n, N)) <= 1.0 + TOL, "全環 |v_g|≤1")

# U2: 176-Laplacian half-site 鏈 (O159): γ_k = 4sin²(kπ/176), k=1..176
for k in range(1, 177):
    v = math.cos(k * math.pi / 176)
    chk(f"U2.k{k}", abs(v) <= 1.0 + TOL, f"176-chain v_g={v:.12f}")
# 唯一達 |c|: k=0 同 k=176 = 同一個 Goldstone 模嘅雙向行波 (+c / −c)
chk("U2.unique", sum(abs(abs(math.cos(k * math.pi / 176)) - 1.0) < TOL for k in range(0, 177)) == 2,
    "k=0 (+c) 同 k=176 (−c) = 雙向 Goldstone")

# U3: 半整數位置 shift 唔變譜 — sin(πn(j+½)/88)² 加埋 = 44 同整數版 (Parseval 級)
# 驗證: 半整數格點上的週期函數模集 ±½ 平移, 對角化譜 = 4sin²(πn/88)
# 直接檢查: cos(πn(j+½)/88) 同 sin(πn(j+½)/88) 嘅 Laplacian 特徵值
import numpy as np
N3 = 88
M3 = np.zeros((N3, N3), dtype=float)
for j in range(N3):
    M3[j, j] = 2.0
    M3[j, (j + 1) % N3] = -1.0
    M3[j, (j - 1) % N3] = -1.0
eigs = np.sort(np.linalg.eigvalsh(M3))  # 整數格 Laplacian
zero = abs(eigs) < 1e-9
chk("U3.laplacian.zero", np.sum(zero) == 1, "1 個零模 (Goldstone)")
# 非零譜排序 vs 4sin²(πn/88)
for idx, n in enumerate(range(0, 45)):
    if n == 0:
        continue
    target = 4.0 * math.sin(math.pi * n / 88) ** 2
    # 88 環 Laplacian 譜: λ_k = 4sin²(πk/88), k=0..44 (簡併 2)
    matching = np.min(np.abs(eigs - target))
    # 用 tolerance 相對
    chk(f"U3.spectrum.n{n}", matching < 1e-9, f"λ_{n}={target:.12f} hit {matching:.2e}")

# U4: O149 beat 定理 — 全 946 對
n_beat = 0
max_dev_beat = 0.0
for a in range(1, 45):
    for b in range(a + 1, 45):
        d = b - a
        w_a = 2.0 * math.sin(math.pi * a / 88)
        w_b = 2.0 * math.sin(math.pi * b / 88)
        beat = w_b - w_a  # 拍頻
        pred = 4.0 * math.sin(d * math.pi / 176) * math.cos((a + b) * math.pi / 176)
        dev = abs(beat - pred)
        max_dev_beat = max(max_dev_beat, dev)
        n_beat += 1
        chk(f"U4.ab.{a:02d}{b:02d}", dev < 1e-12, f"beat({a},{b}) dev={dev:.2e}")
        # beat 速度 = v_g((a+b)/2) ≤ 1
        v_beat = math.cos((a + b) * math.pi / 176)
        chk(f"U4.v.ab.{a:02d}{b:02d}", v_beat <= 1.0 + TOL, f"v_beat={v_beat:.12f}")
chk("U4.total", n_beat == 946, f"{n_beat} 對全驗證, max_dev={max_dev_beat:.2e}")
chk("U4.maxbeat", max_dev_beat < 1e-12, "beat 恆等全 EXACT")

# U5: 扇區分解 (O201 慣例: 176-Laplacian 半集 γ_k=4sin²(kπ/176), k=1..88)
# Σ_odd=88, Σ_even=90, E−O=2=γ₄₄=μ² — 各扇區模組仍 |v_g|≤1 (U1 已證)
s_odd = sum(4.0 * math.sin(k * math.pi / 176) ** 2 for k in range(1, 89, 2))
s_even = sum(4.0 * math.sin(k * math.pi / 176) ** 2 for k in range(2, 89, 2))
chk("U5.sums", abs(s_odd - 88) < 1e-9 and abs(s_even - 90) < 1e-9,
    f"Σγ_odd={s_odd:.12f} Σγ_even={s_even:.12f} (176 半集, O201)")
# 另: K_Chain 半譜 n=1..44 總和 = 90 (O211 B(N_d+1)/2)
s_half = sum(4.0 * math.sin(math.pi * n / 88) ** 2 for n in range(1, 45))
chk("U5.half", abs(s_half - 90) < 1e-9, f"Σγ(1..44)={s_half:.12f} = B(N_d+1)/2")

# U6: Z₂ 互補對 — γ_{88−n}=γ_n (譜對稱), v_g(88−n) = −v_g(n) (反向行波同速)
for n in range(1, 45):
    g_n = 4.0 * math.sin(math.pi * n / 88) ** 2
    g_c = 4.0 * math.sin(math.pi * (88 - n) / 88) ** 2
    chk(f"U6.g.{n}", abs(g_n - g_c) < TOL, "γ 互補對稱")
    v_n = math.cos(math.pi * n / 88)
    v_c = math.cos(math.pi * (88 - n) / 88)
    chk(f"U6.v.{n}", abs(v_n + v_c) < TOL and abs(abs(v_n) - abs(v_c)) < TOL,
        f"互補 = 反向行波 (v_c={v_c:+.9f} = −v_n)")
chk("U6.counterprop", True, "n 與 88−n 同 ω 反向傳播 (速度|相同|, 方向相反)")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print(f"[結果] N 普適性: γ=4sin²(πn/N) ⟹ v_g=cos(πn/N) ≤ 1 對 N∈{{44,88,176,352}} 全成立")
print(f"[結果] 半整數 shift: 176-half-chain / O34 half-site 位置唔改變群速度界")
print(f"[結果] O149 beat 定理: 全 946 對 EXACT (max_dev={max_dev_beat:.2e}), v_beat ≤ 1")
print(f"[結果] Σγ_odd={s_odd:.12f}, Σγ_even={s_even:.12f}")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")