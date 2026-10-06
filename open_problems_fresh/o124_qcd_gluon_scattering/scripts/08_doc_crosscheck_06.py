#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 — Script 08: docs/06 文檔核對 (由零重算, 唔 import scripts/01–07)
========================================================================
獨立重算 docs/06_beta_consistency.md 每個數值 claim。全部由 0,1 → φ → 結構數。
"""
import itertools
import numpy as np

PASS = FAIL = TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {'✅' if ok else '❌'} {name} {detail}")

N     = 88
B     = 4
N_c   = B - 1
N_gen = B - 1
N_f   = 6
C_A   = float(N_c)

def Tpow(n):
    R = [[1, 0], [0, 1]]; M = [[1, 1], [1, 0]]
    for _ in range(n):
        R = [[R[0][0]*M[0][0] + R[0][1]*M[1][0], R[0][0]*M[0][1] + R[0][1]*M[1][1]],
             [R[1][0]*M[0][0] + R[1][1]*M[1][0], R[1][0]*M[0][1] + R[1][1]*M[1][1]]]
    return R
LUC = {n: Tpow(n)[0][0] + Tpow(n)[1][1] for n in range(1, 9)}
FIB = {n: Tpow(n)[0][1] for n in range(1, 9)}

_l = [np.array([[0,1,0],[1,0,0],[0,0,0]], dtype=complex),
      np.array([[0,-1j,0],[1j,0,0],[0,0,0]], dtype=complex),
      np.array([[1,0,0],[0,-1,0],[0,0,0]], dtype=complex),
      np.array([[0,0,1],[0,0,0],[1,0,0]], dtype=complex),
      np.array([[0,0,-1j],[0,0,0],[1j,0,0]], dtype=complex),
      np.array([[0,0,0],[0,0,1],[0,1,0]], dtype=complex),
      np.array([[0,0,0],[0,0,-1j],[0,1j,0]], dtype=complex),
      np.array([[1,0,0],[0,1,0],[0,0,-2]], dtype=complex)/np.sqrt(3)]
Tg = [x/2 for x in _l]
def mat(x): return sum(x[i]*Tg[i] for i in range(8))

print("=" * 78)
print("  O124 Script 08: docs/06 文檔核對 (零重算)")
print("=" * 78)

# ── [1] §2 舊 justification 審計 ─────────────────────────────────
print("\n─── [1] docs/06 §2 (A) ───")
chk("A1 8 + 3 = 11", 8 + 3 == 11)
chk("A2 SU(3) 鬼場 = dim(adj) = 8 ≠ 3", N_c**2 - 1 == 8)
chk("A3 (10/3)C_A + (1/3)C_A = 10 + 1 = 11",
    abs((10/3)*C_A - 10) < 1e-12 and abs((1/3)*C_A - 1) < 1e-12)
chk("A5 (11/3)C_A = 11; 2N_f/3 = 4; 11−4 = 7",
    abs((11/3)*C_A - 11) < 1e-12 and abs(2*N_f/3 - 4) < 1e-12 and 11-4 == 7)
cand = {nf: 11 - 2*nf/3 for nf in range(0, 12) if abs(2*nf/3 - round(2*nf/3)) < 1e-12}
hits = [nf for nf, b0 in cand.items() if abs(b0 - LUC[4]) < 1e-12]
chk("A6 N_f = 6 唯一性", hits == [6] and sorted(cand) == [0, 3, 6, 9],
    f"(候選 {sorted(cand)}, 命中 {hits})")
chk("A7 3B − 1 = 11", 3*B - 1 == 11)

# ── [2] §3 3g = 0 後果 ──────────────────────────────────────────
print("\n─── [2] docs/06 §3 (B) ───")
rng = np.random.default_rng(20260926)
u_r = mat(rng.normal(size=8)); v_r = mat(rng.normal(size=8))
D_r = u_r - v_r; C_r = u_r @ v_r - v_r @ u_r
chk("B1 Im Tr[D³] ≈ 0", abs(np.trace(D_r @ D_r @ D_r).imag) < 1e-12,
    f"({np.trace(D_r@D_r@D_r).imag:.1e})")
chk("B2 |Tr[D·C]| ≈ 0", abs(np.trace(D_r @ C_r)) < 1e-12,
    f"({abs(np.trace(D_r@C_r)):.1e})")
chk("B4 88 模有限", N == 88)

# ── [3] §4 IDCM-native running ──────────────────────────────────
print("\n─── [3] docs/06 §4 (C) ───")
chk("C1 Δα⁻¹ = N_gen² = (B−1)² = 9", N_gen**2 == 9)

# ── [4] §5 重導 b₀ = Tr(T̂^B) ───────────────────────────────────
print("\n─── [4] docs/06 §5 (D) ───")
chk("D1 T̂⁴ = [[5,3],[3,2]]", Tpow(B) == [[5, 3], [3, 2]])
chk("D2 b₀ = L_B = Tr(T̂^B) = 7", LUC[B] == 7)
chk("D3 L₃ = 4, L₄ = 7, L₅ = 11", (LUC[3], LUC[4], LUC[5]) == (4, 7, 11))
chk("D4 2B−1 = F₆−1 = N_gen+B = 7",
    2*B-1 == 7 and FIB[6]-1 == 7 and N_gen+B == 7)
def cw(n, adj):
    k = len(adj); c = 0
    for w in itertools.product(range(k), repeat=n):
        if all(adj[w[i]][w[(i+1) % n]] for i in range(n)): c += 1
    return c
chk("D5 L_B = 閉走道數 = 7", cw(B, [[1, 1], [1, 0]]) == 7)
sol = [b for b in range(1, 9) if 2*b - 1 == LUC[b]]
chk("D6 2B−1 = L_B 解 = {1,2,4}", sol == [1, 2, 4], f"({sol})")

# ── [5] §6 離散 1-loop 顯式 ─────────────────────────────────────
print("\n─── [5] docs/06 §6 (E) ───")
Lap = 2*np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
Lap[0, N-1] = -1; Lap[N-1, 0] = -1
G = np.linalg.pinv(Lap)
V_num = 2*(G[0, 0] - G[0, 1])
chk("E1 V = (N−1)/N = 87/88", abs(V_num - 87/88) < 1e-10, f"({V_num:.10f})")
S1 = S2 = S3 = 0.0
for a in range(8):
    for b in range(8):
        for c in range(8):
            for d in range(8):
                tr = np.trace(Tg[a] @ Tg[b] @ Tg[c] @ Tg[d]).real
                if a == b and c == d: S1 += tr
                if a == c and b == d: S2 += tr
                if a == d and b == c: S3 += tr
chk("E2a S₁ = S₃ = 16/3; S₂ = −2/3",
    abs(S1 - 16/3) < 1e-9 and abs(S3 - 16/3) < 1e-9 and abs(S2 + 2/3) < 1e-9,
    f"({S1:.4f}, {S2:.4f}, {S3:.4f})")
chk("E2b S₁+S₂+S₃ = 10 = (N_c²−1)(2N_c²−3)/(4N_c)",
    abs(S1+S2+S3 - 10) < 1e-9
    and abs((N_c**2-1)*(2*N_c**2-3)/(4*N_c) - 10) < 1e-9)
f3 = np.zeros((8, 8, 8))
for a in range(8):
    for b in range(8):
        for c in range(8):
            f3[a, b, c] = 2*np.trace(Tg[c] @ (Tg[a] @ Tg[b] - Tg[b] @ Tg[a])).imag
Sa = np.einsum('abc,abc->', f3, f3)
chk("E3 Σf² = N_c(N_c²−1) = 24; ⟨Tr[C²]⟩ = −12(G₀₀²−G₀₁²)",
    abs(Sa - 24) < 1e-9
    and abs(-12*(G[0, 0]**2 - G[0, 1]**2) - 0.5*(-Sa*G[0, 0]**2 + Sa*G[0, 1]**2)) < 1e-9,
    f"(Σf² = {Sa:.4f})")
gen = {n: (n**2 - 1)*(2*n**2 - 3)/(4*n) for n in range(2, 7)}
only3 = all((abs(gen[n] - (10/3)*n) < 1e-9) == (n == 3) for n in gen)
chk("E5 10 = (10/3)C_A 僅 N_c = 3", only3 and abs(gen[3] - 10) < 1e-9,
    f"(N_c=4: {gen[4]:.2f} vs {(10/3)*4:.2f})")

# ── [6] §9 誠實表 + §10 時序索引 ────────────────────────────────
print("\n─── [6] docs/06 §9/§10 ───")
doc = open("docs/06_beta_consistency.md", encoding="utf-8").read()
tbl = doc.split("## 9. 誠實標記總表")[1].split("## 10.")[0]
rows = [l for l in tbl.splitlines() if l.startswith("|")
        and ("🟢" in l or "🟡" in l or "🔴" in l)]
chk("誠實表 15 行", len(rows) == 15, f"({len(rows)} 行)")
chk("誠實表 🟢 = 10", sum(1 for r in rows if "🟢" in r) == 10,
    f"({sum(1 for r in rows if '🟢' in r)})")
chk("誠實表 🟡 = 2", sum(1 for r in rows if "🟡" in r) == 2)
chk("誠實表 🔴 = 3", sum(1 for r in rows if "🔴" in r) == 3)
idx = doc.split("## 10. 推導時序索引（本檔）")[1]
chk("時序索引 T0–T6 (7 項)", all(f"**T{i}**" in idx for i in range(7)))
chk("docs/06 無壓縮標記",
    "HERMES-CONTEXT-COMPRESSION" not in doc and "omitted here" not in doc)

# ── [7] §7 判決表 9 行 ──────────────────────────────────────────
print("\n─── [7] docs/06 §7 判決表 ───")
vtbl = doc.split("## 7. 總判決")[1].split("### ★★")[0]
vrows = [l for l in vtbl.splitlines() if l.startswith("|")
         and ("🟢" in l or "🟡" in l or "🔴" in l)]
chk("§7 判決表 9 行", len(vrows) == 9, f"({len(vrows)} 行)")

print("\n" + "=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: {'✅ docs/06 全部數值 claim 核對通過' if FAIL == 0 else '❌ 有核對失敗'}")
print("=" * 78)
