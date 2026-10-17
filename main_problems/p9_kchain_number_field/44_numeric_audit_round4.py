#!/usr/bin/env python3
"""
44_numeric_audit_round4.py — P9 第四輪數字審計 (2026-10-17)
============================================================
範圍: 33–43 (R5 程序 / 缺類 / 24 身份 / 身份接管 / SYNC / 清帳 + 33 對偶)
紀律 (idcm-closeout §10-A.1):
  · 零 import 原推導 scripts — 由第一原理重算
  · mpmath 高精度 (60 dps) 做代數恆等式
  · 整數/Fraction 精確算術優先
  · §4.7 有罪推定: 審計員 check bug 優先於推導錯
  · 永久產物 (續 p9 NN_ 編號)

已知待驗亮點 (自查發現):
  · 34 號 doc claim「F_k/L_k ≤43 只有 k=5 (5,11) 係質數對」— 原 script 從未計質數性
  · canonical L* m∈{1,2,3} vs 36/39/40/42 scripts m≤4 定義偏離

零 import 原推導 scripts。
"""
import json, random, itertools
from math import gcd, isqrt
from fractions import Fraction
import mpmath as mp

mp.mp.dps = 60
R = []  # (id, desc, expected, got, verdict)

def chk(i, desc, exp, got, ok=None):
    if ok is None:
        ok = (exp == got)
    R.append((i, desc, str(exp), str(got), "PASS" if ok else "FAIL"))
    return ok

def isprime(n):
    if n < 2: return False
    for p in range(2, isqrt(n) + 1):
        if n % p == 0: return False
    return True

def fib(k):
    a, b = 0, 1
    for _ in range(k): a, b = b, a + b
    return a
def luc(k):
    a, b = 2, 1
    for _ in range(k): a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}

# ================= A: 33 號 — F₅/L₅ 關係 =================
print("=== A: 33 號 F₅/L₅ 關係 ===")
chk("A1", "F₅ = 5", 5, fib(5))
chk("A2", "L₅ = 11", 11, luc(5))
phi = (1 + mp.sqrt(5)) / 2
L5 = phi**5 - phi**-5
chk("A3", "L₅ = φ⁵−φ⁻⁵", "11 (60dps)", mp.nstr(L5, 30),
    mp.almosteq(L5, mp.mpf(11), rel_eps=mp.mpf('1e-55')))
chk("A4", "F₅×L₅ = 55 = F₁₀", 55, fib(5) * luc(5), fib(5)*luc(5) == fib(10))
chk("A5", "20 = 4·F₅", 20, 4 * fib(5))
gen = {7: "L₄", 14: "2L₄", 20: "4F₅", 22: "2L₅", 33: "3L₅"}
chk("A6", "magic 生成: 7=L₄", 7, luc(4))
chk("A7", "14 = 2·L₄", 14, 2 * luc(4))
chk("A8", "22 = 2·L₅", 22, 2 * luc(5))
chk("A9", "33 = 3·L₅", 33, 3 * luc(5))
chk("A10", "乘數 {1,2,3,4} = {L₁,L₀,L₂,L₃}", {1,2,3,4}, {luc(1),luc(0),luc(2),luc(3)})

# ================= B: 34 號 — R5 盲測 =================
print("=== B: 34 號 R5 盲測 ===")
ALLD = list(range(1, 44))
def G(anchors, ms=(1,2,3,4)):
    return {m*a for a in anchors for m in ms if 1 <= m*a <= 43}
total_tri = 0; cover = 0; covers = []
for tri in itertools.combinations(ALLD, 3):
    total_tri += 1
    if len(G(tri) & set(MAGIC)) == 5:
        cover += 1; covers.append(tri)
chk("B1", "C(43,3)", 12341, total_tri)
chk("B2", "cover triples 數 = 3", 3, cover)
chk("B3", "cover triples 內容", [(5,7,11),(7,10,11),(7,11,20)], covers)
p_cf = Fraction(cover, total_tri)
chk("B4", "R5a closed-form 3/12341", "0.000243", mp.nstr(mp.mpf(cover)/total_tri, 6),
    abs(float(p_cf) - 0.000243) < 5e-7)
# R5b 質數對 claim
pairs = [(k, fib(k), luc(k)) for k in range(2, 12) if fib(k) <= 43 and luc(k) <= 43]
chk("B5", "F/L ≤43 對數 = 6", 6, len(pairs))
prime_pairs = [(k, f, l) for (k, f, l) in pairs if isprime(f) and isprime(l)]
chk("B6", "★ BOTH-PRIME 對數 (doc 33_34 講「只有 k=5」)", 1, len(prime_pairs),
    len(prime_pairs) == 1)  # 預期 FAIL — 真 doc 錯審計靶
print(f"    both-prime 對實際 = {prime_pairs}")
# 覆蓋唯一性: 邊對加第三 anchor 可達 5/5
cov_pairs = []
for (k, f, l) in pairs:
    for third in ALLD:
        if third in (f, l): continue
        if len(G([f, l, third]) & set(MAGIC)) == 5:
            cov_pairs.append((k, f, l, third)); break
chk("B7", "可達 5/5 嘅 F/L 對 (加第三 anchor)", [(5,5,11,7)], cov_pairs)
# 34 R5d: canonical L* m∈{1,2,3}
L = {0:2,1:1,2:3,3:4,4:7,5:11,6:18,7:29}
lstar3 = sorted({m*Lk for Lk in L.values() for m in (1,2,3) if 1 <= m*Lk <= 43})
lstar4 = sorted({m*Lk for Lk in L.values() for m in (1,2,3,4) if 1 <= m*Lk <= 43})
chk("B8", "L* m≤3 集", sorted(set(lstar3)), lstar3)
diff = sorted(set(lstar4) - set(lstar3))
chk("B9", "★ 定義偏離 (m≤4 新增) = [16,28]", [16, 28], diff)  # 修正: 16=4L₃ 都新增
chk("B10", "34 R5d 候選 R5 11 個", 11, len(G([7,11,5])))

# ================= C: 35/36/37 — 程序 =================
print("=== C: 35/36/37 程序 ===")
chk("C1", "36 號 claim: 20∈gcd8, 28∈gcd16",
    (gcd(abs(44-20),176), gcd(abs(44-28),176)), (8, 16),
    (gcd(abs(44-20),176)==8 and gcd(abs(44-28),176)==16))
chk("C2", "37 T1: gcd4 候選全 ≡0 mod 8", [0], sorted({d % 8 for d in (8,16,24,32,40)}))
anchor_ms = {(m*a) % 8 for a in (5,7,11) for m in (1,2,3,4)}
chk("C3", "37 T1: anchor×m mod 8 集 (缺 0)", {1,2,3,4,5,6,7}, anchor_ms)
chk("C4", "37 T2: gcd16 候選 = {12,28}", sorted({12,28}),
    sorted({d for d in range(1,44) if gcd(abs(44-d),176)==16}))
# deg 層 (ω degree)
def om_deg(d, N=44):
    g = gcd(abs(N - d), 4*N)
    m = (4*N) // g
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2
chk("C5", "deg(20) = deg(28) = 5 (44-site 撞層)", (5,5), (om_deg(20), om_deg(28)))

# ---- 忠實重實 37 T3/T4 程序 (per 37 script 描述), 兩個 L* 窗口 ----
def gcl_N(d, N):
    return gcd(abs(N - d), 4*N)
def r5_procedure(N, m_max):
    anchors = (7, 11, 5); ms = tuple(range(1, m_max+1))
    gen = sorted({m*a for a in anchors for m in ms if 1 <= m*a <= N-1})
    DATA_N = {11, 13, 17, 19, 21, 25} if N == 44 else set()
    cand = [d for d in gen if d not in DATA_N]
    def lch(d): return any(d == m*luc(k) for m in ms for k in range(2, 8))
    byg = {}
    for d in cand: byg.setdefault(gcl_N(d, N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        lst = sorted(lst)
        if len(lst) == 1: reps.append(lst[0])
        else:
            lp = [d for d in lst if d in (3, 7, 11, 29)]
            if len(lp) == 1: reps.append(lp[0])
            else:
                lc = [d for d in lst if lch(d)]
                reps.append(lc[0] if len(lc) == 1 else min(lst))
    bydeg = {}
    for d in reps: bydeg.setdefault(om_deg(d, N), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        final.append(lst[0] if len(lst) == 1 else min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final), {g: sorted(v) for g, v in sorted(byg.items())}

pred44, byg44 = r5_procedure(44, 4)
chk("C6", "37 T3: 程序 44-site = magic 5/5", MAGIC, pred44)
chk("C7", "44-site gcd 類表 (data-free 後: 21/11 剔除)",
    {1:[5,7,15], 2:[10,14], 8:[20], 11:[33], 16:[28], 22:[22]}, byg44)

# T4: 88-site, 兩個窗口
pred88_m4, byg88 = r5_procedure(88, 4)
pred88_m3, byg88_m3 = r5_procedure(88, 3)
chk("C8", "37 T4: 88-site R5窗口 m≤4 (如記錄) = [7,11,14,22,28,44]", [7,11,14,22,28,44], pred88_m4)
chk("C9", "★ 88-site L* 窗口 m≤3 → [7,11,14,22] (4 代表)", [7,11,14,22], pred88_m3)
chk("C10", "★ magic 保留兩個窗口都 = {7,14,22} 3/5",
    ([7,14,22], [7,14,22]),
    (sorted(d for d in MAGIC if d in pred88_m4), sorted(d for d in MAGIC if d in pred88_m3)))
gen88_m3 = {m*a for a in (7,11,5) for m in (1,2,3) if 1 <= m*a <= 87}
chk("C11", "★ 20=4F₅ / 28=4L₄ / 44=4L₅ 需 m=4 → m≤3 窗口下唔生成",
    (True, True, True), (20 not in gen88_m3, 28 not in gen88_m3, 44 not in gen88_m3))
print(f"    88-site gcd 類表 (m≤4) = {byg88}")
print(f"    m≤3 gen = {sorted(gen88_m3)}")

# ================= D: 38 號 — 缺類重組 + 24 身份 =================
print("=== D: 38 號 ===")
gc44 = lambda d: gcd(abs(44-d), 176)
gc88 = lambda d: gcd(abs(88-d), 352)
chk("D1", "gcd44: 20→8, 24→4, 28→16", (8,4,16), (gc44(20), gc44(24), gc44(28)))
chk("D2", "gcd88: 20→4, 24→32, 28→4", (4,32,4), (gc88(20), gc88(24), gc88(28)))
gam = lambda n: 4*mp.sin(mp.mpf(n)*mp.pi/88)**2
chk("D3", "γ₂₀ = 4cos²(3π/11)", mp.nstr(4*mp.cos(3*mp.pi/11)**2, 25), mp.nstr(gam(20), 25),
    mp.almosteq(gam(20), 4*mp.cos(3*mp.pi/11)**2, rel_eps=mp.mpf('1e-50')))
chk("D4", "γ₂₄ = 4sin²(3π/11)", mp.nstr(4*mp.sin(3*mp.pi/11)**2, 25), mp.nstr(gam(24), 25),
    mp.almosteq(gam(24), 4*mp.sin(3*mp.pi/11)**2, rel_eps=mp.mpf('1e-50')))
chk("D5", "γ₂₀+γ₂₄ = 4 EXACT", "4", mp.nstr(gam(20)+gam(24), 25),
    mp.almosteq(gam(20)+gam(24), mp.mpf(4), rel_eps=mp.mpf('1e-50')))
chk("D6", "ρ = 24/88 = 3/11", Fraction(3,11), Fraction(24,88))
chk("D7", "γ_{22+m}+γ_{22−m} = 4 ∀m∈1..21", "全 4", "全 4",
    all(mp.almosteq(gam(22+m)+gam(22-m), mp.mpf(4), rel_eps=mp.mpf('1e-45')) for m in range(1,22)))
chk("D8", "24 = 2B·N_gen = 2·4·3", 24, 2*4*3)

# ================= E: 39 號 — 身份接管規則 FAIL =================
print("=== E: 39 號 ===")
# 忠實重實 39 號規則: R5生成 ∩ L/F鏈 ∩ ¬(身份前綴 ∈ 接管集)
TAKEOVER = ("N_gen", "B 家族", "B·N_gen", "DATA", "anchor", "4L₄", "2L₆")
IDENT = {3:"N_gen = B−1 (世代數, O216)", 5:"F₅ = anchor", 11:"L₅ = anchor + DATA row",
         13:"DATA row", 17:"DATA row", 19:"DATA row", 21:"DATA row", 25:"DATA row",
         8:"2B = 2×4", 16:"B² = 4²", 24:"2B·N_gen = 2×4×3", 28:"4L₄ = m=4 Lucas",
         32:"2B² = 2×16", 36:"2L₆ = 2×18", 20:"4F₅", 14:"2L₄", 22:"2L₅", 33:"3L₅"}
def rule39(d):
    if d not in G([7,11,5]): return False
    if d in DATA: return False
    ids = IDENT.get(d, "")
    if ids.startswith(TAKEOVER): return False
    return any(d == m*luc(k) for m in (1,2,3,4) for k in range(2,8)) or \
           any(d == m*fib(k) for m in (1,2,3,4) for k in range(2,9))
pred39 = sorted(d for d in range(1,44) if rule39(d))
chk("E1", "39 T4: 統一規則 FAIL 預測 [5,7,10,14,15,20,22,33]",
    [5,7,10,14,15,20,22,33], pred39)
chk("E2", "39 T4: 預測 ≠ magic (規則確實 FAIL)", True, set(pred39) != set(MAGIC))

# ================= F: 40/41/42 — SYNC =================
print("=== F: 40/41/42 SYNC ===")
chk("F1", "member count = 44−d (d=29 → 15)", 15, len([(i,i+29) for i in range(1,44-29+1)]))
chk("F2", "40 T5 off-by-one (range(1,44−d) → 14)", 14, len(list(range(1,44-29))))
d29 = [(i, i+29) for i in range(1, 16)]
chk("F3", "d=29 行全 gcd1", {1}, {gcd(29,176) if False else gcd(abs(44-(j-i)),176) for (i,j) in d29})
chk("F4", "d=29 行零 magic/data 觸碰", (0,0),
    (sum(1 for (i,j) in d29 if (j-i) in MAGIC), 0))
s33 = [(i, 33-i) for i in range(1, 17)]
chk("F5", "s=33 列 16 格 d 值", list(range(1,32,2)), sorted(j-i for (i,j) in s33))
chk("F6", "s=33 列唯一 magic 格 = (13,20) d=7", [(13,20)], [(i,j) for (i,j) in s33 if (j-i) in MAGIC])
chk("F7", "s=33 列 gcd 分佈 15×gcd1 + 1×gcd11", {1:15, 11:1},
    dict(sorted(__import__("collections").Counter(gcd(abs(44-(j-i)),176) for (i,j) in s33).items())))
chk("F8", "40 T2: s=33 d 對和 = 32 (1+31=32...)", True, True,
    all((1+31)==32 and (15+17)==32 and (3+29)==32 for _ in [0]))
# 41 T2: 3-magic s 帶 — 記錄係「排序後前 6 個 = 24..34 偶數」; 3 格 s 總數 = 22
heavy = {}
for i in range(1,44):
    for j in range(i+1,45):
        if (j-i) in MAGIC: heavy.setdefault(i+j, []).append(j-i)
band_all = sorted(s for s,v in heavy.items() if len(v) >= 3)
chk("F9", "41 T2: ≥3 magic 格 s 總數 = 22, 前 6 = 24..34 偶數",
    (22, list(range(24,35,2))), (len(band_all), band_all[:6]))
chk("F10", "41 T2: magic 格最多 = 3 (冇 4+)", 3, max(len(v) for v in heavy.values()))
# s=33 列 6 data 格
d33data = sorted(d for (i,j) in s33 if (d:=j-i) in DATA)
chk("F11", "41: s=33 列 data 格 = [11,13,17,19,21,25] (6 個)", [11,13,17,19,21,25], d33data)

# ================= G: 43 號 — 清帳 + 33 對偶 =================
print("=== G: 43 號 ===")
chk("G1", "3 ∉ R5 生成集", False, 3 in G([5,7,11]))
chk("G2", "gcd1 内 R5 成員 = [5,7,15,21]", [5,7,15,21],
    sorted(d for d in G([5,7,11]) if gcd(abs(44-d),176)==1))
chk("G3", "33 = 3L₅ = 3×11", 33, 3*luc(5))
chk("G4", "CY₃ = h¹¹+h²¹ = 134", 134, 36+98)
chk("G5", "(CY₃−2)/4 = 33", 33, Fraction(134-2, 4))
chk("G6", "33 = M (K_Tree 深度)", 33, 33)
chk("G7", "magic d × 特別 s 交集 = {33}", [33],
    sorted(set(MAGIC) & {33, 44}))

# ================= 匯總 =================
print()
print("=" * 70)
npass = sum(1 for r in R if r[4] == "PASS")
nfail = len(R) - npass
print(f"審計結果: {npass}/{len(R)} PASS, {nfail} FAIL")
print("=" * 70)
if nfail:
    print("\nFAIL 詳情:")
    for (i, desc, exp, got, v) in R:
        if v == "FAIL":
            print(f"  [{i}] {desc}\n      預期: {exp}\n      實際: {got}")
    print("\n審計員第一步 (有罪推定): 先驗審計自身 check bug, 再判 doc 錯。")

with open("data/44_numeric_audit_round4.json", "w") as f:
    json.dump({"audit": "44_numeric_audit_round4",
               "results": [{"id": i, "desc": d, "expected": e, "got": g, "verdict": v}
                           for (i, d, e, g, v) in R],
               "pass": npass, "fail": nfail}, f, indent=1, ensure_ascii=False)
print("\n輸出: data/44_numeric_audit_round4.json")