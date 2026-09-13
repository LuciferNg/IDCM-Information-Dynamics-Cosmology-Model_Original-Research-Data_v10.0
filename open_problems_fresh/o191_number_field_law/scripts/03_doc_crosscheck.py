#!/usr/bin/env python3
"""O191 scripts/03 — 獨立核對 (O153 審計模式): docs/01 + docs/02 全部 headline 公式

從零重算 (mpmath 60 dps), 唔依賴 scripts/01/02 輸出。目的: 捉 doc 錯誤。
用法: python3 03_doc_crosscheck.py
"""
import mpmath as mp
mp.mp.dps = 60

phi = (1 + mp.sqrt(5)) / 2

F = {0: mp.mpf(0), 1: mp.mpf(1)}
def fib(n):
    if n not in F:
        F[n] = fib(n-1) + fib(n-2)
    return F[n]

L = {0: mp.mpf(2), 1: mp.mpf(1)}
def luc(n):
    if n not in L:
        L[n] = luc(n-1) + luc(n-2)
    return L[n]

B, Ngen, Nd = 4, 3, 44
L4, L5, L6 = luc(4), luc(5), luc(6)
F4, F5, F9, F10, F11, F12, F13 = fib(4), fib(5), fib(9), fib(10), fib(11), fib(12), fib(13)

checks = []
def chk(doc, claim, computed, docval, tol=mp.mpf("1e-30")):
    ok = abs(computed - docval) <= tol * max(1, abs(docval))
    checks.append((doc, claim, ok, f"{mp.nstr(computed, 15)} vs {mp.nstr(docval, 15)}"))
    return ok

# ===== docs/01: 二模量定理 =====
chk("01", "F9 = 34", fib(9), 34)
chk("01", "F11 = 89", fib(11), 89)
chk("01", "N = 88 = F11 - 1", F11 - 1, 88)
chk("01", "M = 33 = F9 - 1", F9 - 1, 33)
chk("01", "M+1 = 34 = F9 (tree 節點數)", F9, 34)

# 譜和: 176-Laplacian 奇偶
def g176(k): return 4 * mp.sin(mp.pi * k / 176)**2
S_even = sum(g176(k) for k in range(2, 89, 2))
S_odd = sum(g176(k) for k in range(1, 88, 2))
chk("01", "chain Σγ = 178 = 2F11", S_even + S_odd, 2 * F11)
chk("01", "Σγ_even = 90 = F11+1", S_even, 90)
chk("01", "Σγ_odd = 88 = F11-1", S_odd, 88)
chk("01", "E-O = 2 = mu^2", S_even - S_odd, 2)

# tree 譜和: 34-node path Laplacian trace
lam = [2 - 2 * mp.cos(k * mp.pi / 34) for k in range(1, 34)]
chk("01", "tree Σλ = 66 = 2M", sum(lam), 66)

# ===== docs/01: F-1 家族 =====
fam = {m: fib(m) - 1 for m in range(4, 13)}
expected = {4: 2, 5: 4, 6: 7, 7: 12, 8: 20, 9: 33, 10: 54, 11: 88, 12: 143}
for m, v in expected.items():
    chk("01", f"F{m}-1 = {v}", fam[m], v)

# ===== docs/01: 截斷定理 =====
chk("01", "F12-1 = 143 <= 178", F12 - 1, 143)
chk("01", "F13-1 = 232 > 178", F13 - 1, 232)
chk("01", "143 = 12^2-1 = 66+77", 12**2 - 1, 66 + 77)

# ===== docs/01: m-鎖定鏈 =====
mlock = {4: B, 5: F5, 6: 2 * Ngen, 7: L4, 8: 2 * B, 9: Ngen**2, 10: L5 - 1, 11: L5, 12: B * Ngen}
mlock_names = {4: "B", 5: "F5", 6: "2N_gen", 7: "L4", 8: "2B", 9: "N_gen^2", 10: "L5-1", 11: "L5", 12: "B*N_gen"}
for m, v in mlock.items():
    chk("01", f"m={m} = {mlock_names[m]}", v, m)

# ===== docs/02: 54 身份裁決 =====
chk("02", "54 = N_gen x L6 = 3x18", Ngen * L6, 54)
chk("02", "L6 = L5 + L4 = 18", L6, 18)
chk("02", "h21 = BxL5 + N_genxL6 = 98 (O56)", B * L5 + Ngen * L6, 98)
chk("02", "h11 = 2L6 = 36 (O56)", 2 * L6, 36)
chk("02", "h21 - h11 = Nd + L6 = 62", (B * L5 + Ngen * L6) - 2 * L6, Nd + L6)
chk("02", "Σ_even - h11 = 90 - 36 = 54", 90 - 36, 54)
chk("02", "5L6 - 2L6 = 3L6 = 54 (候選 2 等價)", 5 * L6 - 2 * L6, 54)
chk("02", "AP {6,11,16,21} 和 = 54 (O155)", 6 + 11 + 16 + 21, 54)
chk("02", "2 x N_gen^3 = 2x27 = 54 (候選 3)", 2 * Ngen**3, 54)

# ===== docs/02: m-鎖定鏈 O95 級 =====
chk("02", "m_min = 4 = B", B, 4)
chk("02", "m_max = 12 = B x N_gen = L5+1", B * Ngen, L5 + 1)
chk("02", "88 = 2B x L5 (O95 交叉)", 2 * B * L5, 88)
chk("02", "33 = N_gen x L5 (O95 交叉)", Ngen * L5, 33)

# ===== docs/02: 截斷統一 =====
mu2 = 2
chk("02", "88 = Nd x mu^2 = 44x2", Nd * mu2, 88)
chk("02", "90 = (Nd+1) x mu^2 = 45x2", (Nd + 1) * mu2, 90)
chk("02", "178 = F11 x mu^2 = 89x2", F11 * mu2, 178)
chk("02", "k_max = 88/11 = 8 = Z2 x B", 88 // 11, 8)

# ===== docs/02: tree 推廣 =====
chk("02", "291.5 = L5 x (Nd + N_gen^2) / 2 = 11x53/2", L5 * (Nd + Ngen**2) / 2, mp.mpf("291.5"))
chk("02", "53 = Nd + N_gen^2", Nd + Ngen**2, 53)
chk("02", "μ0 = phi^291.5, μ33 = phi^258.5 (指數範圍)", 291.5 - 33, 258.5)
chk("02", "68 = 2F9 = B x F_proj (17)", 2 * F9, B * 17)
chk("02", "F_proj = 17 = L6 - 1", L6 - 1, 17)
chk("02", "μ_{m+1}/μ_m = phi^-1", phi**mp.mpf(290.5) / phi**mp.mpf(291.5), phi**(-1))

# ===== 輸出 =====
print(f"O191 docs/01-02 獨立核對 ({len(checks)} 項, 從零重算)")
npass = 0
for doc, claim, ok, detail in checks:
    tag = "OK" if ok else "XX"
    print(f"  [{tag}] {doc} {claim}  [{detail}]")
    npass += ok
print(f"\nAUDIT RESULT: {npass}/{len(checks)} 核對通過")
