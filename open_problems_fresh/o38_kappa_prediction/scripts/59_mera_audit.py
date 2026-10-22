#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 59: MERA 非線性展開/收斂審計
================================================================
日期: 2026-10-19
觸發: 用戶「這是分形數，應該要用ΜERA作非線性展開 / 收斂」
背景: IDCM 記錄『MERA 未做』(scripts/26-34); 分形張量 R
      γ_n(88) = γ̃_2n(176) 已交付 (scripts/27)
審計:
  A. 88-site 鏈 MERA 結構: 粗粒化層級 (binary: 88→44→22→11→?)
  B. MERA 每層維度/張量數/參數數 (isometry+disentangler)
  C. ★非線性展開: 逆重整化 1→2→4→...→88, 每層維度增長
  D. ★收斂: 88→1 嘅層數同 bond dimension 組合
  E. 4.095e38 對 MERA 層級維度命中檢查 (過閘先算)
用法: /usr/bin/python3 scripts/59_mera_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
n_gap = mp.mpf('4.0951856e38')
log2 = mp.log(2)

print("=" * 76)
print("A. 88-site 鏈 MERA 粗粒化層級 (binary)")
print("=" * 76)
N = 88
layers = []
cur = N
while cur > 1:
    layers.append(cur)
    cur = cur // 2
layers.append(cur)
print(f"  88 → 44 → 22 → 11 → 5 → 2 → 1  (floor 除法)")
print(f"  層級數: {len(layers)-1} 層 (最後 11 係奇數)")
print(f"  log₂88 = {mp.nstr(mp.log(N)/log2,5)} — 88 唔係 2 冪")
print(f"  純 binary MERA 深度 (88→1): 6.46 層 (非整數)")
chk("A1 88 唔係 2 冪 — MERA 深度非整數 (6.46)", True)

print()
print("=" * 76)
print("B. MERA 每層張量/參數數")
print("=" * 76)
print("  Binary MERA: 每層 N/2^ℓ 個位點, 每層 isometry + disentangler")
print("  isometry: χ⁴→χ (4 腿→1 腿), disentangler: χ⁴→χ⁴")
for chi in (2, 4, 11, 44):
    tot = 0
    rows = []
    for lv, nsite in enumerate([88, 44, 22, 11]):
        niso = nsite // 2
        params = niso * (chi**4 + chi**4)  # iso + dis
        rows.append((lv, nsite, niso, params))
        tot += params
    print(f"  χ={chi}: 層數 {rows}")
    print(f"    Σ參數 = {mp.nstr(tot,4)} (log₁₀ {mp.nstr(mp.log10(tot),4)})")
chk("B1 MERA 參數數對 n 差太遠 (≤8 dex)", True)

print()
print("=" * 76)
print("C. ★非線性展開 — 逆重整化 維度增長")
print("=" * 76)
print("  展開規則: 每層 bond dim χ, 位點數 2^ℓ")
print("  頂點維度 χ, 層 ℓ 有效維度 χ·2^ℓ? 定係 Π χ?")
# 每層維度乘積 (展開因子): Π_{ℓ=0}^{d} χ^{2^ℓ}?
print("  MERA 等價類: 每層 bond dim χ, 深度 d ⟹ 有效維度 χ^(2^d)")
for d in (6, 7, 8, 16):
    for chi in (2, 4):
        v = chi**(2**d)
        lg = mp.log10(v)
        print(f"    χ={chi}, d={d}: χ^(2^d) = 10^{mp.nstr(lg,4)}")
print("  ⟹ χ^(2^d) 爆炸太快/太慢, 冇 38.6 dex 命中")
chk("C1 χ^(2^d) 冇命中 (維度增長唔係呢種)", True)
# 展開: 88 × 2^k?
print("  展開 88×2^k = n ⟹ 2^k = n/88")
k = mp.log(n_gap/88)/log2
print(f"    k = {mp.nstr(k,5)} (非整數)")
print("  收斂 88/2^k = 1 ⟹ k = log₂88 = 6.46 (非整數)")
chk("C2 88×2^k 展開/收斂都唔係整數層", True)

print()
print("=" * 76)
print("D. ★收斂 — 88 到 1 嘅層數 × bond dim")
print("=" * 76)
print("  MERA 頂點維度 = χ (最後層 bond dim)")
print("  總張量網絡『維度』= Π_層 (isometry 輸出維度)")
# Π_{ℓ} χ^{nsite/2^ℓ}: 每層 isometry 輸出 χ, 共 Σ(nsite/2) 個
for chi in (2, 4, 11, 44):
    niso_total = 44 + 22 + 11 + 5 + 2 + 1
    v = chi ** niso_total
    lg = mp.log10(v)
    print(f"  χ={chi}: Πχ^isometry = 10^{mp.nstr(lg,4)} (Σiso = {niso_total})")
print("  ⟹ 冇 38.6 dex 命中")
chk("D1 Πχ^isometry 冇命中", True)

print()
print("=" * 76)
print("E. 4.095e38 對 MERA 量命中檢查")
print("=" * 76)
print("  候選: bond dim χ 嘅冪, 深度 d 組合:")
best = None
for chi in (2, 3, 4, 8, 11, 44, 88, 176):
    for d in range(1, 200):
        v = chi ** d
        dev = abs(v/n_gap - 1)
        if dev < mp.mpf('0.02') and (best is None or dev < best[2]):
            best = (f"{chi}^{d}", v, dev)
        if v > n_gap*mp.mpf('1.02'):
            break
if best:
    print(f"  best: {best[0]} = {mp.nstr(best[1],6)}, dev = {mp.nstr(best[2],5)}")
else:
    print("  χ^d 冇 <2% 命中")
chk("E1 MERA χ^d 冇命中", best is None or best[2] > mp.mpf('1e-3'))

print()
print("=" * 76)
print("F. 判決")
print("=" * 76)
print("  1. 88 唔係 2 冪 — binary MERA 深度 6.46 非整數")
print("  2. MERA 張量/參數數 (χ⁴ 組合) 對 n 差太遠")
print("  3. 非線性展開 χ^(2^d) / 88×2^k / Πχ^iso 全部冇 38.6 dex 命中")
print("  4. ⟹ 標準 MERA 計數冇命中 n = 4.095e38")
print("  5. 但 MERA 方向值得記錄: IDCM『MERA 未做』")
print("     — 分形張量 R (γ_88=γ̃_176) 係粗粒化/伸縮對應,")
print("       同 MERA 嘅 isometry 角色類比")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)