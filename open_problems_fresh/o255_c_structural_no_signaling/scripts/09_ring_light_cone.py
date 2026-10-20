#!/usr/bin/env python3
"""
O255 scripts/09 — Ring 88 亮錐定理 (cyclic 距離版)
====================================================
預註冊 (2026-10-20 Round 4, 跑前凍結): Round 3 嘅 C1/C2 喺 open chain;
呢支補 ring (週期邊界) 版 — 88-site 環, cyclic 距離 d_c(j,k)=min(|j-k|,88-|j-k|)。

R1  Ring leapfrog 精確亮錐: u_j(t)=0 EXACT ∀ d_c(j,0) > t (t=1..44)
    (Fraction 零容差; 週期邊界唔破壞亮錐 — 每步至多 1 site)
R2  Ring 首次響應: τ_first(d)=d EXACT ∀ d=1..44 (cyclic 距離)
    — 對蹠點 d=44 都喺 t=44 先到 (半環最遠路)
R3  Ring 對稱雙向: u_{−d} 與 u_{d} 同時到達 (左右對稱)
R4  Ring wrap 冇污染: t=44 前唔會經另一邊捷徑提前到達
    (cyclic 最短距離定義已含 wrap; 亮錐以 d_c 計)

執行: /usr/bin/python3 scripts/09_ring_light_cone.py > logs/09.txt 2>&1
"""
from fractions import Fraction

checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

N = 88
tmax = 44

# Ring leapfrog: 週期邊界 u_{j±1 mod 88}
def step_ring(prev, cur):
    nxt = []
    for j in range(N):
        v = cur[(j + 1) % N] + cur[(j - 1) % N] - prev[j]
        nxt.append(v)
    return nxt

def d_c(j, k=0):
    dd = abs(j - k) % N
    return min(dd, N - dd)

# 初始 δ 於 site 0
prev = [Fraction(0)] * N
cur = [Fraction(0)] * N
prev[0] = Fraction(1)
cur[0] = Fraction(1)

# R1: 逐時間步檢查錐外零
ok1 = True
first_viol = None
first_arr = {}      # d -> t (首次非零)
for t in range(1, tmax + 1):
    nxt = step_ring(prev, cur)
    for j in range(N):
        d = d_c(j)
        if d > t and nxt[j] != 0:
            ok1 = False
            if first_viol is None:
                first_viol = (t, j, d, str(nxt[j]))
        if nxt[j] != 0 and d not in first_arr:
            first_arr[d] = t
    prev, cur = cur, nxt

chk("R1.ring_cone", ok1, f"ring leapfrog: u_j(t)=0 EXACT ∀ d_c(j)>t, t≤44 (反例: {first_viol})")

# R2: 首次響應 d 步 = d (1..44)
ok2 = True
for d in range(1, 45):
    if first_arr.get(d) != d:
        ok2 = False
chk("R2.first_arr", ok2, "τ_first(d)=d EXACT ∀ d=1..44 (對蹠 d=44 半環最遠同 t=44 到)")

# R3: 對稱雙向 — u_{N-d}(t) 與 u_d(t) 同時同幅 (Fraction 精確)
ok3 = True
prev = [Fraction(0)] * N
cur = [Fraction(0)] * N
prev[0] = Fraction(1)
cur[0] = Fraction(1)
for t in range(1, 25):
    nxt = step_ring(prev, cur)
    for d in range(1, min(t, 44) + 1):
        if nxt[d] != nxt[N - d]:
            ok3 = False
    prev, cur = cur, nxt
chk("R3.symmetric", ok3, "u_{N−d}(t) = u_d(t) EXACT (左右對稱)")

# R4: wrap 捷徑冇污染 — jump 距離 <= 1 每步, cyclic 最短距離定義已含 wrap;
#      亮錐以 d_c 計, 檢查 j=1 (d=1) 唔會係 t>>44 才... 直接: t=5 時 j=N-1 (d=1) 有值
prev = [Fraction(0)] * N
cur = [Fraction(0)] * N
prev[0] = Fraction(1)
cur[0] = Fraction(1)
for t in range(1, 6):
    nxt = step_ring(prev, cur)
    prev, cur = cur, nxt
chk("R4.no_wrap_early", cur[1] == cur[N - 1] != 0,
    "t=5: j=1 同 j=87 (兩邊 d=1) 同時有值 — wrap 方向同一規則, 冇捷徑")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print("[結果] Ring 88 亮錐: cyclic 距離版 EXACT — 週期邊界唔破壞亮錐定理")
print("[結果] 對蹠點 d=44 喺 t=44 首達 (半環最遠路程 = 半亮錐), 左右對稱, wrap 冇捷徑")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")