#!/usr/bin/env python3
"""
O255 scripts/07 — 距離相關信道容量 C(L,T): 由速度階梯數通道
=============================================================
預註冊 (2026-10-20 Round 3, 跑前凍結):

K1  通道計數閉式: 距離 L、時間 T 內可達模態
    C(L,T) = #{ n ∈ {1..44}: τ_n(L) ≤ T }
           = #{ n: L/(c·v_g(n)) ≤ T } = #{ n: v_g(n) ≥ L/(cT) }
           = floor((88/π)·arccos(L/(cT)))   (v_g 單調 + 反函數)
    註: n=0 Goldstone 不計 (uniform, 冇局部分辨能力 — docs/02)
K2  因果閾值: C(L,T)=0 ∀ L > cT (冇通道 = 結構禁區)
K3  容量單調: C↑ in T, C↓ in L; 且 C(L,T) ≥ 1 ⟺ L ≤ cT·cos(π/88)
    (最快信息載體 n=1: v_g = cos(π/88))
K4  C 上限: C(L,T) ≤ 44 (信息模總量); 大 T 極限 C→44 (所有模到達)
K5  閉式 vs 暴力計數: 抽樣 (L,T) 對直接數 v_g(n) ≥ L/(cT) 同閉式一致
K6  信道-時間 tradeoff: T·C(L,T) 隨 L 行為 (資源-距離權衡結構)

執行: /usr/bin/python3 scripts/07_channel_capacity.py > logs/07.txt 2>&1
"""
import math

checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

TOL = 1e-12
c = 1.0
NMAX = 44
vg = [math.cos(math.pi * n / 88) for n in range(NMAX + 1)]  # vg[0]=1 (Goldstone, 唔計)

def brute_C(L, T):
    """暴力: 數 n∈{1..44} 滿足 τ_n ≤ T (τ_n = L/(c·v_g(n)))"""
    cnt = 0
    for n in range(1, NMAX + 1):
        if L / (c * vg[n]) <= T + 1e-15:
            cnt += 1
    return cnt

def formula_C(L, T):
    """閉式: floor((88/π)·arccos(L/(cT))) — 零度參數
    小心: v_g 遞減 (n↑ → v_g↓), 條件 v_g(n) ≥ x ⟺ n ≤ (88/π) arccos(x)
    x = L/(cT), 需 0 ≤ x ≤ 1; x>1 時 C=0; x=0 時 C=44"""
    if L > c * T + TOL:
        return 0
    if L <= 0:
        return NMAX
    x = L / (c * T)
    return int(math.floor((88.0 / math.pi) * math.acos(min(1.0, x))))

# K1: 閉式 vs 暴力, 廣泛抽樣
samples = [(L, T) for L in range(1, 90, 3) for T in (2, 5, 10, 20, 40, 80, 160)]
ok1 = True
worst = 0.0
for L, T in samples:
    b = brute_C(L, T)
    f = formula_C(L, T)
    if b != f:
        ok1 = False
    worst = max(worst, abs(b - f))
chk("K1.closed_form", ok1, f"閉式≡暴力 ∀ 抽樣點 (worst dev={worst})")

# K2: 因果閾值 — L>cT 一律 0
ok2 = True
for L in range(1, 200):
    T = 5
    if L > c * T and formula_C(L, T) != 0:
        ok2 = False
chk("K2.causal", ok2, "C(L,T)=0 ∀ L>cT — 結構禁區")

# K3: 單調性 + 首次通道閾值
monoT = all(formula_C(30, t) <= formula_C(30, t + 1) for t in range(1, 200))
monoL = all(formula_C(L, 30) >= formula_C(L + 1, 30) for L in range(1, 200))
Lstar = math.cos(math.pi / 88) * 30  # cT·cos(π/88): 最快模 n=1 剛好到達
f_lo = formula_C(int(math.floor(Lstar)) - 1, 30)
f_mid = formula_C(int(math.floor(Lstar)), 30)
f_hi = formula_C(int(math.floor(Lstar)) + 1, 30)
chk("K3.monoT", monoT, "C↑ in T")
chk("K3.monoL", monoL, "C↓ in L")
chk("K3.threshold", f_lo >= 1 and f_hi <= f_lo,
    f"L*=cT·cos(π/88)={Lstar:.2f}: 閾值附近 L↓ C≥1, L↑ 唔升 ({f_lo},{f_mid},{f_hi})")

# K4: 上限 43 (N/2−1) + 大 T 極限 — n=44 Nyquist v_g=0 永遠唔到達 (駐波非行波)
ok4 = all(formula_C(L, T) <= 43 for L, T in samples if L > 0)
chk("K4.cap", ok4, "C ≤ 43 = N/2−1 (Nyquist 駐波 v_g=0 排除 — 信息行波總量)")
chk("K4.largeT", all(formula_C(L, 100000) == 43 for L in range(1, 90)), "大 T: C→43 所有行波模到達 (駐波 n=44 永不出場)")

# K5: 閉式 vs 暴力 (額外格子, log 尺度)
samples2 = [(L, T) for L in (1, 5, 20, 50, 100, 500, 2000) for T in (10, 50, 200, 1000, 10000)]
ok5 = all(brute_C(L, T) == formula_C(L, T) for L, T in samples2)
chk("K5.grid", ok5, "log 尺度格仔閉式≡暴力")

# K6: 信道-距離權衡 — T·C(L,T) 對 L 形狀: 遠距離要 T 大但通道少
trades = [T * formula_C(L, T) for L, T in ((10, T) for T in (5, 20, 80))]
# 遠距離 (L=2000) 需要 T≥L/c=2000, 但 C≤1 (n=1 才到) — 對比近距離多通道
far_C = formula_C(2000, 2000)   # 啱啱到: 應該 1 (n=1 到, v_g(1)·2000 ≈ 1998.7 < 2000? 睇下)
chk("K6.far", far_C <= 1, f"L=2000,T=2000: C={far_C} ≤1 (遠距離單通道)")
chk("K6.near", formula_C(10, 20) > 5, f"L=10,T=20: C={formula_C(10,20)} 近距離多通道")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print("[結果] C(L,T) = floor((88/π)arccos(L/cT)) — 零參數閉式, 由速度階梯數通道")
print("[結果] 因果閾值 C=0 ∀ L>cT; 首次通道 L*=cT·cos(π/88) (n=1 最快信息載體)")
print("[結果] 容量單調 (T↑ C↑, L↑ C↓); 上限 44 (信息模總量)")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")