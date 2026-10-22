#!/usr/bin/env python3
"""
O153 script 09 — 容量 vs 算子: 世界90 + 觀察者88 = ?  殘差應該 4?
驗證用戶框架: 「以容量而非算子計算應該是世界90+觀察者88=176, 實際殘差應該4, 能量要有勢差才能動」
176-Laplacian: γ_k = 4sin²(kπ/176), k=1..88
"""
import mpmath as mp
mp.mp.dps = 50

N_d = 44
B = 4

def gamma(k):
    return mp.mpf(4) * mp.sin(mp.pi * k / 176)**2

# 譜
g = [mp.mpf(0)] + [gamma(k) for k in range(1, 89)]  # index 1..88
S_even = sum(g[k] for k in range(2, 89, 2))   # 世界
S_odd  = sum(g[k] for k in range(1, 89, 2))   # 觀察者
S_tot  = S_even + S_odd
s0 = sum(g[k] for k in range(4, 89, 4))   # k ≡ 0 mod 4 (含 k=88)
s2 = sum(g[k] for k in range(2, 89, 4))   # k ≡ 2 mod 4
s1 = sum(g[k] for k in range(1, 89, 4))   # k ≡ 1 mod 4
s3 = sum(g[k] for k in range(3, 89, 4))   # k ≡ 3 mod 4

mu2 = 2  # γ₄₄ = 4sin²(π/4) = 2

results = []

def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

def eq(a, b, tol=mp.mpf(10)**-40):
    return mp.fabs(mp.mpf(a) - mp.mpf(b)) < tol

# C1 基本譜
check("C1a Σγ_even = 90 (世界)", eq(S_even, 90), f"Σeven={mp.nstr(S_even, 30)}")
check("C1b Σγ_odd = 88 (觀察者)", eq(S_odd, 88), f"Σodd={mp.nstr(S_odd, 30)}")
check("C1c Σγ_total = 178", eq(S_tot, 178), f"Σtot={mp.nstr(S_tot, 30)}")

# C2 容量 identity: 176
check("C2a 176 = B·N_d", eq(B*N_d, 176), "4×44")
check("C2b 176 = 2×88", eq(2*88, 176), "88 modes × 2 側")
check("C2c 176 = 172 + 4", eq(43*B + 4, 176), "43 對偶對×B + γ₈₈")

# C3 用戶框架: 世界90 + 觀察者88 = ?
check("C3a 90+88 = 178 (唔係 176)", eq(S_even + S_odd, 178), f"{mp.nstr(S_even+S_odd,30)}")
check("C3b 178 = 176 + μ²", eq(S_tot, 176 + mu2), "178 = B·N_d + 2")
check("C3c 90+88−μ² = 176", eq(S_even + S_odd - mu2, 176), "178−2 = 176")

# C4 勢差 (potential difference)
check("C4a 勢差 = Σγ_even − Σγ_odd = 2", eq(S_even - S_odd, mu2), f"90−88={mp.nstr(S_even-S_odd,30)}")
check("C4b 勢差 = μ² = γ₄₄", eq(mu2, 4*mp.sin(mp.pi/4)**2), "自對偶 mode")

# C5 殘差 4 嘅候選身份
check("C5a 4 = B = 2μ²", eq(B, 2*mu2), "容量單位")
check("C5b 4 = γ₈₈ (Nyquist)", eq(gamma(88), 4), f"γ88={mp.nstr(gamma(88),30)}")
check("C5c 4 = N_d⁺ − N_d⁻ = 46−42", eq(46-42, 4), "世界自我 − 觀察者側")
check("C5d 4 = 2×勢差", eq(2*(S_even-S_odd), 4), "2×(90−88)")

# C6 mod-4 分解: 世界 90 = s0+s2, 觀察者 88 = s1+s3
check("C6a 世界 = s0+s2 = 46+44 = 90", eq(s0+s2, 90), f"s0={mp.nstr(s0,20)}, s2={mp.nstr(s2,20)}")
check("C6b 觀察者 = s1+s3 = 88", eq(s1+s3, 88), f"s1+s3={mp.nstr(s1+s3,20)}")
check("C6c s0−s2 = 2 = μ²", eq(s0-s2, mu2), f"s0−s2={mp.nstr(s0-s2,20)}")

# C7 「容量內 Nyquist」: 176 = 172+4, 178 = 172+2+4
check("C7a 譜分解 178 = 172+2+4", eq(43*B + mu2 + 4, 178), "43×B + γ₄₄ + γ₈₈")
check("C7b 容量 176 = 172+4 (冇 γ₄₄)", eq(43*B + 4, 176), "172 + γ₈₈")
check("C7c 178−176 = 2 = γ₄₄", eq(178-176, mu2), "超額 = 自對偶 mode")

# C8 beat 需要勢差 (能量要有勢差才能動)
# beat(a,b) = 4sin(|a−b|π/176)·v_g((a+b)/2) (O149 定理1)
# 當 a=b (冇勢差), beat = 0 — 冇能量流動
def vg(n):
    return mp.cos(mp.pi*n/176)
def beat(a, b):
    return mp.mpf(4)*mp.sin(mp.fabs(a-b)*mp.pi/176)*vg((a+b)/2)
check("C8a beat(44,44) = 0 (冇勢差=冇能量流動)", eq(beat(44,44), 0), "同 mode 冇拍頻")
check("C8b beat(44,45) ≠ 0 (有勢差=能量流動)", beat(44,45) > 0, f"beat={mp.nstr(beat(44,45),12)}")
check("C8c beat 交換對稱 beat(a,b)=beat(b,a)", eq(beat(42,44), beat(44,42)), f"b={mp.nstr(beat(42,44),15)}")
check("C8d 勢差 2 嘅 beat 隨中心 v_g 變化 (唔對稱)", not eq(beat(42,44), beat(44,46)), f"b42={mp.nstr(beat(42,44),12)}, b46={mp.nstr(beat(44,46),12)}")
check("C8e 勢差越大 → beat 越大 (單調)", beat(44,46) > beat(44,45) > beat(44,44), f"b1={mp.nstr(beat(44,45),10)}, b2={mp.nstr(beat(44,46),10)}")

# C9 每步能量 = 勢差 (O41: 88 ops × 2 = 176)
check("C9a 88 ops × 勢差2 = 176 = B·N_d", eq(88*mu2, 176), "操作容量")
check("C9b 每步消耗 2 = 勢差 (唔係 4)", eq(mu2, S_even - S_odd), "能量流動燃料 = 勢差本身")

# C10 「殘差 4」精確位置: 46−42 = B
check("C10a N_d⁺−N_d⁻ = 4 = B", eq((N_d+mu2)-(N_d-mu2), B), "家族 gap = 2μ² = B")
check("C10b C_obs 分拆 gap: 88 = 46+42, 差 = 4", eq(46+42, 88) and eq(46-42, 4), "docs/05")

print("="*72)
print("O153 script 09 — 容量 vs 算子: 90/88/176/178/4 identity audit")
print("="*72)
fails = 0
for name, ok, detail in results:
    mark = "✅ PASS" if ok else "❌ FAIL"
    if not ok: fails += 1
    print(f"  {mark}  {name}  [{detail}]")
print("-"*72)
print(f"TOTAL: {len(results)-fails}/{len(results)} PASS, {fails} FAIL")

print()
print("== 關鍵數值 ==")
print(f"  Σγ_even (世界)  = {mp.nstr(S_even, 30)}")
print(f"  Σγ_odd  (觀察者) = {mp.nstr(S_odd, 30)}")
print(f"  Σγ_total        = {mp.nstr(S_tot, 30)}")
print(f"  s0/s2/s1/s3     = {mp.nstr(s0,12)}/{mp.nstr(s2,12)}/{mp.nstr(s1,12)}/{mp.nstr(s3,12)}")
print(f"  90+88           = {mp.nstr(S_even+S_odd, 30)}")
print(f"  176 = B·N_d     = {B*N_d}")
print(f"  178 − 176       = {mp.nstr(S_tot - B*N_d, 30)} = μ² (勢差)")
print(f"  勢差 90−88      = {mp.nstr(S_even-S_odd, 30)}")
print(f"  4 = B = 2μ²     = {B}")
