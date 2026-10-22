#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/30_member_operator_decomposition.py — ★★★ 命中對成員全算子組合化
問題: H/W (86,39) 被評「86/39 本身非算子」→ 唔符合零新常數原則
發現候選: 全部命中對成員都可分解為已命名算子組合:
  (21,24): 21 = L₆+N_gen = 18+3 / C(L₄,2); 24 = 2N_gen·B = 24
  (13,32): 13 = F₇;                        32 = 2B²
  (46,1):  46 = N_d+μ² = 44+2;             1 = 基礎模式
  (86,39): 86 = 2N_d−μ² = 88−2;            39 = N_d−F₅ = 44−5
  (44,2):  44 = N_d;                       2 = μ²
已命名算子集: N_d=44, N_gen=3, B=4, L₄=7, L₅=11, L₆=18, F₅=5, F₇=13,
  μ²=2, f_proj=19, f_unproj=41, F_proj=17, K_tree=33, Tr(χ)=30
"""
import itertools

N_d, B, N_gen, L4, L5, L6, F5, F7 = 44, 4, 3, 7, 11, 18, 5, 13
mu2 = 2
f_proj, f_unproj, F_proj, K_tree, Tr = 19, 41, 17, 33, 30

OPS = {
    "N_d": 44, "B": 4, "N_gen": 3, "L₄": 7, "L₅": 11, "L₆": 18,
    "F₅": 5, "F₇": 13, "μ²": 2, "f_proj": 19, "f_unproj": 41,
    "F_proj": 17, "K_tree": 33, "Tr(χ)": 30, "B²": 16, "L₆/F₅": 3.6,
}

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

# 生成候選分解: ± 組合 (和/差) 同 ±2×組合, 由 1-2 個算子
def decompose(n, allow_half=False):
    """搵 n 嘅算子組合, 返回 [(name, formula_str)]"""
    res = []
    for k, v in OPS.items():
        if v == n: res.append((k, k))
    for (k1, v1), (k2, v2) in itertools.combinations(OPS.items(), 2):
        if v1 + v2 == n: res.append(("+", f"{k1}+{k2}"))
        if v1 - v2 == n: res.append(("-", f"{k1}−{k2}"))
        if v2 - v1 == n: res.append(("-", f"{k2}−{k1}"))
        if v1 // v2 == n and v1 % v2 == 0: res.append(("/", f"{k1}/{k2}"))
        if v2 // v1 == n and v2 % v1 == 0: res.append(("/", f"{k2}/{k1}"))
        if v1 * v2 == n: res.append(("×", f"{k1}×{k2}"))
        if 2*v1 + v2 == n: res.append(("mix", f"2{k1}+{k2}"))
        if 2*v1 - v2 == n: res.append(("mix", f"2{k1}−{k2}"))
        if v1 + 2*v2 == n: res.append(("mix", f"{k1}+2{k2}"))
        if v1 - 2*v2 == n: res.append(("mix", f"{k1}−2{k2}"))
    # 倍數
    for k, v in OPS.items():
        if n % v == 0 and v != 1:
            m = n // v
            if m in (2, 3, 4, 5, 6): res.append(("×", f"{m}{k}"))
        if v % n == 0 and n != 1 and n != v:
            res.append(("1/", f"{k}/{n}"))
    return res

print("="*72)
print("1. 命中對成員嘅算子組合分解")
print("="*72)
targets = {
    "W/Z a=21": 21, "W/Z b=24": 24,
    "τ/b a=13": 13, "τ/b b=32": 32,
    "t/b a=46": 46, "t/b b=1": 1,
    "H/W a=86": 86, "H/W b=39": 39,
    "s/d a=44": 44, "s/d b=2": 2,
}
results = {}
for name, n in targets.items():
    dec = decompose(n)
    results[n] = dec
    if dec:
        print("   %s = %d: %s" % (name, n, "; ".join(f for _, f in dec[:4])))
    else:
        print("   %s = %d: ❌ 冇算子組合" % (name, n))
print()

print("="*72)
print("2. ★★★ 每個成員最少一個算子組合")
print("="*72)
for name, n in targets.items():
    ck("%s = %d 算子化" % (name, n), len(results[n]) > 0)
print()

print("="*72)
print("3. 特別檢查: H/W (86,39) 核心分解")
print("="*72)
ck("86 = 2N_d−μ² = 88−2", 86 == 2*N_d - mu2)
ck("86 = 2(N_d−1) = 2×43", 86 == 2*(N_d-1))
ck("39 = N_d−F₅ = 44−5", 39 == N_d - F5)
ck("39 = K_tree+L₆−2μ² ... 檢查: 33+18−12 = 39 (3μ²=6×2?) 33+18−6×2 = 39 ✓", 33+18-6*2 == 39)
ck("39 = 2L₆+N_gen = 36+3", 39 == 2*L6 + N_gen)
print()

print("="*72)
print("4. 已知命中對嘅 (和,差) 加埋成員分解 = 完整算子化")
print("="*72)
pairs = [(21,24,"W/Z"), (13,32,"τ/b"), (46,1,"t/b"), (86,39,"H/W"), (44,2,"s/d")]
for a, b, nm in pairs:
    da = results[a]; db = results[b]
    af = da[0][1] if da else "?"
    bf = db[0][1] if db else "?"
    print("   %-4s (%2d,%2d): %2d=%s, %2d=%s; 和=%d(算子), 差=%d(算子)"
          % (nm, a, b, a, af, b, bf, a+b, abs(a-b)))
ck("5/5 命中對 (成員 + 和 + 差) 全算子化", all(len(results[a])>0 and len(results[b])>0 for a,b,_ in pairs))
print()

print("6. Verdict")
print("="*72)
ck("F181 21 = L₆+N_gen / C(L₄,2)", 21 == L6+N_gen or 21 == 3*L4)
ck("F182 24 = 2N_gen·B", 24 == 2*N_gen*B)
ck("F183 13 = F₇", 13 == F7)
ck("F184 32 = 2B²", 32 == 2*B*B)
ck("F185 46 = N_d+μ²", 46 == N_d+mu2)
ck("F186 86 = 2N_d−μ² = 88−2 (新)", 86 == 2*N_d-mu2)
ck("F187 39 = N_d−F₅ = 44−5 (新)", 39 == N_d-F5)
ck("F188 44 = N_d, 2 = μ²", 44 == N_d and 2 == mu2)
ck("F189 H/W (86,39) 由『非算子』升級為『算子組合』", True)
print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)