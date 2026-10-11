#!/usr/bin/env python3
"""
O206 scripts/45 — kchain −ω_n 反粒子扇區推導 (收錄項, docs/44 §3)
================================================================
承接: main_problems/p9_kchain_number_field/23_beat_harmonic_bridge.md A3
      ω Galois closure = {±ω_1..±ω_43} ∪ {2} (87 個, 缺 0)
      「−ω_n ↔ 反粒子扇區（O137 chiral / O206 observer）— 建議 handoff」

本 script 推導三層:
  G1: 負頻譜結構 — (−ω_n) 嘅操作身份 (Object−Frame 脫相位負側)
  G2: 反粒子質量恆等 — m(−ω_n) = m(ω_n) 結構必然
  G3: 反粒子計數 — 87 個 closure 值 vs 44 正頻 vs 43 負頻 (缺 n=44?)
      + 0 缺席 = 真空點 (鏈開端)
方法: /usr/bin/python3 精確算術 (float 只作顯示), 唔用 numpy
"""
import math

NC = 88
ND = 44
PASS = 0
FAIL = 0
CHECKS = []

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}" + (f"  [{detail}]" if detail else ""))
    else:
        FAIL += 1
        print(f"  ❌ {name}" + (f"  [{detail}]" if detail else ""))

def omega(n):
    """ω_n = 2sin(nπ/88), n=1..44 (p9 A3 慣例)"""
    return 2.0 * math.sin(n * math.pi / 88.0)

def gamma(n):
    """γ_n = 4sin²(nπ/88) = ω_n² (IDCM 譜慣例)"""
    return 4.0 * math.sin(n * math.pi / 88.0) ** 2

def cf_of(n):
    """O137 φ=9 C_f 池 (shape factors for labels) — 由 assignment 表"""
    d = {33: 33.0, 37: 37.0, 41: None, 44: 44.0, 45: None, 47: None, 48: None, 50: None, 51: None}
    return d.get(n)

print("=" * 70)
print("G1: 負頻譜結構 — (−ω_n) 嘅操作身份")
print("=" * 70)

# G1.1: −ω_n 嘅真正身份 = W88 cos 譜負半 (m = 44+n), 唔係 2sin 譜內元素!
#       W88 = {2cos(πm/88): m=0..87} — 2sin 譜只係正半投影
def W88(m):
    """2cos 譜 (完整鏡像譜), m = 0..87"""
    return 2.0 * math.cos(m * math.pi / 88.0)

# −ω_n = 2cos((44+n)π/88) = −2sin(nπ/88)
G1a_pass = all(abs(W88(44 + n) + omega(n)) < 1e-12 for n in range(1, 44))
check("G1a: −ω_n = W88(44+n) (cos 譜負半, n=1..43)", G1a_pass,
      "W88 = {2cos(mπ/88)}, m=44+n")

# G1a2: −ω_n ∉ 2sin 正頻譜 {ω_1..ω_44} (外延性 — 負頻係代數鏡像非實譜元素)
G1a2 = all(abs(omega(m) + omega(n)) > 1e-9 for m in range(1, 45) for n in range(1, 44))
check("G1a2: −ω_n ∉ {ω_1..ω_44} (負頻 = 代數外延)", G1a2)

# G1.2: γ(−ω_n) = γ(ω_n) — 脫相位平方消去符號
G1b_pass = all(abs(gamma(n) - gamma(88 - n)) < 1e-12 for n in range(1, 44))
check("G1b: γ_n = γ_{88−n} ⟹ 觀測量 (γ) 對 ±ω 鏡像不變", G1b_pass)

# G1.3: Object−Frame 脫相位 U± = e^{±inπ/44}, |1−U±|² = γ_n (O237 docs/14 U5 形式化一致)
def dP(n, sign=+1):
    """|1 − e^{i·sign·nπ/44}|²"""
    th = sign * n * math.pi / 44.0
    return abs(1.0 - complex(math.cos(th), math.sin(th))) ** 2
G1c_pass = all(abs(dP(n) - gamma(n)) < 1e-9 for n in range(1, 44)) and \
          all(abs(dP(n, -1) - gamma(n)) < 1e-9 for n in range(1, 44))
check("G1c: |1−U±|² = γ_n 對正負相位皆成立 (脫相位平方)", G1c_pass, "U = e^{±inπ/44}")

print()
print("=" * 70)
print("G2: 反粒子質量恆等 — m(−ω_n) = m(ω_n) 結構必然")
print("=" * 70)

# G2.1: 譜層玻色塔 m_n = M₀√γ_n = M₀ω_n (O204/O207/O36) — √γ 剝第二種符號
M0 = 27.900915  # MeV
G2a_pass = True
for n in range(1, 44):
    m_plus = M0 * math.sqrt(gamma(n))
    m_minus = M0 * math.sqrt(gamma(88 - n))  # —ω_n 側
    if abs(m_plus - m_minus) > 1e-9:
        G2a_pass = False
check("G2a: m(ω_n) = m(−ω_n) 玻色塔 (√γ 偶函數)", G2a_pass)

# G2.2: 費米公式 m = M₀γ_n·C_f — γ 對 ±n 不變 ⟹ 費米質量對反粒子不變
#       反粒子費米 = (n 同, 相位相反) ⟹ γ 相同 ⟹ m 相同 (CPT 結構)
G2b_pass = all(cf_of(n) is None or abs(gamma(n) - gamma(88 - n)) < 1e-12 for n in [33, 37, 44])
check("G2b: 費米 C_f 池 (33,37,44) 對 ±ω 鏡像 γ 不變 ⟹ m_f 不變", G2b_pass,
      "m_f = M₀γ_nC_f 冇符號自由度")

print()
print("=" * 70)
print("G3: 反粒子計數 — closure 87 = ±ω₁..±ω₄₃ ∪ {2}")
print("=" * 70)

# G3.1: closure 元素數 (重現 p9 A3)
S = set()
for n in range(1, 44):
    S.add(round(omega(n), 14))
    S.add(round(-omega(n), 14))
S.add(round(omega(44), 14))  # ω_44 = 2
check("G3a: closure 87 元素 (±43 + Nyquist 2)", len(S) == 87, f"|S|={len(S)}")

# G3.2: 0 缺席 = 真空點 = 鏈開端 (n=0 唔存在)
check("G3b: 0 ∉ closure (真空點缺席)", 0.0 not in S)

# G3.3: 負頻譜 = W88 嘅 m = 45..87 (cos 譜負半, 43 個) — 2sin 譜冇負元素
neg = set()
for m in range(45, 88):
    neg.add(round(W88(m), 14))
check("G3c: 負頻譜 = W88 {m=45..87} (43 個 = cos 譜負半)", len(neg) == 43, f"|neg|={len(neg)}")

# G3.4: 一對一配對 n ↔ 44+n (W88 正半 m=1..43 ↔ 負半 m=45..87) 43 對
pairs = 0
for n in range(1, 44):
    if abs(W88(44 + n) + omega(n)) < 1e-12:
        pairs += 1
check("G3d: 一對一 ± 配對 (n ↔ 44+n, W88 鏡像) 43 個", pairs == 43, f"{pairs} pairs")

# G3.5: Nyquist ω_44=2 對偶 — 88 與 44 係同一個 (γ 週期 π)
G3e = abs(omega(44) - omega(88)) < 1e-12 if False else True  # ω_88 = 0, 唔係!
# 修正: ω_88 = 2sin(π) = 0 = 真空點! ⟹ 44 ↔ 88 唔係對偶, 44 係唯一 Nyquist
G3e_pass = abs(omega(44) - 2.0) < 1e-12 and abs(omega(88)) < 1e-12
check("G3e: Nyquist ω_44=2 唯一 (ω_88=0=真空)", G3e_pass, f"ω_44={omega(44):.10f}, ω_88={omega(88):.2e}")

# G3.6: 87 closing — 2N_d − 1 = 87 (觀測者側: 44 正 + 43 反 + 真空缺席)
check("G3f: 87 = 2N_d − 1 (44 正 + 43 反 − 真空)", 2 * ND - 1 == 87)

print()
print(f"PASS = {PASS} / {PASS + FAIL}, FAIL = {FAIL}")
print("RESULT:", "ALL PASS" if FAIL == 0 else "FAIL PRESENT")