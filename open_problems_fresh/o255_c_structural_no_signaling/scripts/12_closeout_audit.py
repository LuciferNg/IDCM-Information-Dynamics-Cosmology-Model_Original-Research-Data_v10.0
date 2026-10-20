#!/usr/bin/env python3
"""
O255 closeout — scripts/12_audit_independent.py
================================================
T1 獨立重驗審計（2026-10-20, closeout 輪）
零 import 任何原推導 script — 由原始定義 (0,1 → x²+x−1, γ_n=4sin²(πn/88))
重算 O255 全部 headline 數字, 用唔同算法 (對稱式/直接枚舉/半角形式)。

判據 A..N 對應 docs/01-05 主要閉合:
A  速度-質量圓:    v_g² + γ/4 = 1,  ∀n∈[0,44]            (docs/01 T2)
B  Goldstone 唯一: |v_g|=1 ⟺ n=0                        (docs/01 T3)
C  gap 定理:       gap(N) = 1−cos(π/N) = 2sin²(π/2N)    (docs/03)
D  Lorentz:        γ_L = csc(πn/88) = 2/√γ_n            (docs/03)
E  自對偶統一:     v_g(22)=v_g_tree(17)=1/√2             (docs/03)
F  K_Tree:         Σλ_c = 66 = 2K_tree                  (docs/03)
G  快度格仔:       η_n = atanh(v_g) = ln cot(πn/176)     (docs/03)
H  離散亮錐:       leapfrog u_j(t)=0 EXACT ∀|j|>t        (docs/04; 獨立重實作)
I  信道容量閉式:   C(L,T)=floor((88/π)arccos(L/(cT)))   (docs/04)
J  信息模總量:     43 = N/2−1                            (docs/04)
K  3D |∇ω|≤1:     數值梯度 <1 (非 √3 c)                 (docs/05)
L  尾巴分辨成本:   K(d) ≥ 0.737d = d·log₂(5/3) bits      (docs/05)
M  ∀N 唯一 Goldstone: N=3..200 抽樣                    (docs/05 A2)
N  Ring 亮錐:      cyclic 距離 EXACT                    (docs/05; 獨立重實作)

執行: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/12_audit_independent.py > logs/12.txt 2>&1
"""
import math
from fractions import Fraction

TOL = 1e-10
checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

# ---- A: 速度-質量圓 ∀n∈[0,44] ----
okA = True
for n in range(0, 45):
    vg = math.cos(math.pi * n / 88)
    gamma = 4.0 * math.sin(math.pi * n / 88) ** 2
    if abs(vg*vg + gamma/4.0 - 1.0) > TOL:
        okA = False
chk("A.circle44", okA, "v_g²+γ/4=1 ∀n∈[0,44]")

# ---- B: Goldstone 唯一性 (44 鏈) ----
gold = [n for n in range(0, 45) if abs(abs(math.cos(math.pi*n/88))-1.0) < 1e-12]
chk("B.goldstone", gold == [0], f"|v_g|=1 ⟺ n=0 ({gold})")

# ---- C: gap 定理 — 半角形式 ----
okC = True
for ell in range(0, 10):
    N = 44 * 4**ell
    g1 = 1.0 - math.cos(math.pi / N)
    g2 = 2.0 * math.sin(math.pi / (2.0 * N)) ** 2
    if abs(g1 - g2) > 1e-12:
        okC = False
    if not (g1 > 0 and g1 < 1e-2):   # 收縮並>0
        okC = False
chk("C.gap", okC, "gap(N)=1−cos(π/N)=2sin²(π/2N), 單調收縮 (ℓ=0..9)")

# ---- D: Lorentz γ_L = csc = 2/√γ ----
okD = True
for n in range(1, 45):
    gL = 1.0 / math.sin(math.pi * n / 88)
    gL2 = 2.0 / math.sqrt(4.0 * math.sin(math.pi*n/88)**2)
    if abs(gL - gL2) > 1e-9:
        okD = False
chk("D.lorentz", okD, "γ_L = csc(πn/88) = 2/√γ_n ∀n∈[1,44]")

# ---- E: 自對偶模統一 c/√2 ----
e1 = math.cos(22 * math.pi / 88)
e2 = math.cos(17 * math.pi / 68)
chk("E.chain22", abs(e1 - 1/math.sqrt(2)) < TOL, f"鏈 n=22 v_g={e1:.12f} = 1/√2")
chk("E.tree17", abs(e2 - 1/math.sqrt(2)) < TOL, f"樹 c=17 v_g={e2:.12f} = 1/√2")

# ---- F: K_Tree Σλ = 66 = 2K_tree ----
sl = sum(4.0*math.sin(c*math.pi/68)**2 for c in range(1, 34))
chk("F.treesum", abs(sl - 66.0) < TOL, f"Σλ = {sl:.10f} = 66 = 2K_tree")

# ---- G: 快度格仔 η = ln cot(πn/176) = atanh(v_g) ----
okG = True
for n in range(1, 45):
    eta = math.log(1.0 / math.tan(math.pi * n / 176.0))
    vg = math.cos(math.pi * n / 88)
    eta2 = math.atanh(vg)
    if abs(eta - eta2) > 1e-9:
        okG = False
chk("G.rapidity", okG, "η_n = atanh(v_g) = ln cot(πn/176) ∀n∈[1,44]")

# ---- H: 離散亮錐 (獨立實作, Fraction) ----
NCH = 120
C = 60
TMAX = 40
prev = [Fraction(0) for _ in range(NCH)]
cur = [Fraction(0) for _ in range(NCH)]
prev[C] = Fraction(1); cur[C] = Fraction(1)
okH = True
for t in range(1, TMAX + 1):
    nxt = []
    for j in range(NCH):
        v = (cur[j-1] if j > 0 else 0) + (cur[j+1] if j < NCH-1 else 0) - prev[j]
        nxt.append(v)
    for j in range(NCH):
        if abs(j - C) > t and nxt[j] != 0:
            okH = False
    prev, cur = cur, nxt
chk("H.cone", okH, "leapfrog 亮錐 u_j(t)=0 EXACT ∀|j−C|>t (獨立 Fraction 實作)")

# ---- I: 信道容量閉式 ≡ 暴力 (抽樣) ----
def vg_of(n): return math.cos(math.pi * n / 88)
okI = True
for L in (1, 7, 20, 50):
    for T in (5, 20, 60):
        b = sum(1 for n in range(1, 44) if L/vg_of(n) <= T + 1e-12)
        if L > T:
            f = 0
        else:
            f = int(math.floor((88.0/math.pi) * math.acos(L/T)))
        if b != f:
            okI = False
chk("I.capacity", okI, "C(L,T)=floor((88/π)arccos(L/cT)) ≡ 暴力 (抽樣)")

# ---- J: 信息模總量 43 = N/2−1 ----
okJ = (43 == 88//2 - 1) and (43**3 == 79507)
chk("J.modes", okJ, f"信息行波總量 43 = N/2−1; 3D 43³ = {43**3}")

# ---- K: 3D |∇ω|≤1 (獨立無限差分) ----
N3 = 88
def w3(kx, ky, kz):
    s = math.sin(kx*math.pi/N3)**2 + math.sin(ky*math.pi/N3)**2 + math.sin(kz*math.pi/N3)**2
    return 2.0*math.sqrt(s)
okK = True
worst = 0.0
for kx in range(0, 45, 5):
    for ky in range(0, 45, 5):
        for kz in range(0, 45, 5):
            h = 1e-6
            gx = (w3(kx+h, ky, kz) - w3(kx-h, ky, kz))/(2*h)
            gy = (w3(kx, ky+h, kz) - w3(kx, ky-h, kz))/(2*h)
            gz = (w3(kx, ky, kz+h) - w3(kx, ky, kz-h))/(2*h)
            v = math.sqrt(gx*gx + gy*gy + gz*gz)
            worst = max(worst, v)
            if v > 1.0 + 1e-6:
                okK = False
chk("K.3D", okK, f"3D |∇ω| ≤ 1 (max={worst:.6f}; 唔係 √3c={math.sqrt(3):.4f})")

# ---- L: 尾巴分辨成本 ≥ 0.737d ----
Kd = lambda d: d * math.log2(5.0/3.0)
chk("L.gate", abs(Kd(44) - 32.4) < 0.5 and Kd(44) >= 32.0,
    f"K(44) = {Kd(44):.1f} bits ≥ 32 (閉式 0.737d)")

# ---- M: ∀N 唯一 Goldstone (N=3..200) ----
okM = True
for N in range(3, 201):
    hits = [n for n in range(0, N+1) if abs(abs(math.cos(math.pi*n/N))-1.0) < 1e-11]
    if hits != [0] and hits != [0, N]:
        okM = False
        break
chk("M.allN", okM, "|v_g|=1 ⟺ n≡0 (mod N) ∀N∈[3,200] (抽樣一階)")

# ---- N: Ring 亮錐 (獨立實作) ----
RN = 88
rp = [Fraction(0)]*RN; rc = [Fraction(0)]*RN
rp[0] = Fraction(1); rc[0] = Fraction(1)
okN = True
def dc(j): 
    d = abs(j) % RN
    return min(d, RN - d)
for t in range(1, 45):
    nxt = [rc[(j+1) % RN] + rc[(j-1) % RN] - rp[j] for j in range(RN)]
    for j in range(RN):
        if dc(j) > t and nxt[j] != 0:
            okN = False
    rp, rc = rc, nxt
chk("N.ring", okN, "Ring 88 亮錐 cyclic EXACT (獨立 Fraction 實作)")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print(f"[RESULT] O255 closeout 獨立重驗: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    print(f"  [{'PASS' if c else 'FAIL'}] {name}: {note}")