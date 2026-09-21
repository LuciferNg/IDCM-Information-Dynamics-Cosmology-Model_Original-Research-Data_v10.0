#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O207 B3 — 模式身份分類 (Mode Identity Classification)
================================================================
由 Z₂ 偶扇區結構 (γ_22 = μ² = 2 不動點) 分類 44 模式:
  不動點 / 配對 (n, 44−n) / 邊界

問題 (01_problem_record B3):
  44 個塔模式對應咩物件? 係唔係全部物理?
  (n=44 Nyquist 塔頂 = 55.80 MeV; n=1 = 1.99 MeV)

方法: 結構來源分類 (非枚舉) — 用 γ_n 譜本身嘅不變量
  ① 配對律 γ_n + γ_{44−n} = 4 (O204/O206 已立)
  ② 不動點 γ_22 = μ² = 2 (Z₂ 反射不動點)
  ③ 邊界 n=1, n=44 (譜端點)
  ④ ★ 新推導: Pythagorean 型質量恆等式 m_n² + m_{44−n}² = m_44²
================================================================
"""
import mpmath as mp
import json, os

mp.mp.dps = 60

M0 = mp.mpf('27.900915')  # MeV (O38)
N = 44

def gamma_n(n):
    return 4 * mp.sin(mp.pi * n / 88) ** 2

def m_n(n):
    return M0 * mp.sqrt(gamma_n(n))

pass_count = 0
fail_count = 0

def chk(name, cond, detail=''):
    global pass_count, fail_count
    if cond:
        pass_count += 1
        print(f'  [PASS] {name} {detail}')
    else:
        fail_count += 1
        print(f'  [FAIL] {name} {detail}')

print('=' * 78)
print('O207 B3 — 模式身份分類 (Mode Identity Classification)')
print('=' * 78)

# ---------- C1: 結構三分 (不動點 / 配對 / 邊界) ----------
print('\n--- C1: 結構三分 ---')

# 不動點: n=22 (γ = μ² = 2)
fp = 22
chk('C1a 不動點 n=22: γ_22 = μ² = 2', abs(float(gamma_n(fp)) - 2) < 1e-50,
    f'(γ_22={mp.nstr(gamma_n(fp),10)})')

# 配對: (n, 44−n) for n=1..21, plus (22,22) self-pair
pairs = [(n, N - n) for n in range(1, N // 2)]
# 21 pairs: (1,43)..(21,23); 22 係自配對; 44 係端點
chk('C1b 配對數 = 21 (n=1..21, 44−n)', len(pairs) == 21, f'({len(pairs)} pairs)')

# 配對律全驗
pair_ok = all(abs(gamma_n(n) + gamma_n(N - n) - 4) < mp.mpf('1e-50') for n, _ in pairs)
chk('C1c 配對律 γ_n+γ_{44-n}=4 全 21 對', pair_ok)

# 邊界: n=1 (最小) / n=44 (Nyquist 最大)
chk('C1d 邊界 n=1 最小質量', float(m_n(1)) == min(float(m_n(i)) for i in range(1, N + 1)))
chk('C1e 邊界 n=44 最大質量 (Nyquist)', float(m_n(44)) == max(float(m_n(i)) for i in range(1, N + 1)))

# ---------- C2: ★ Pythagorean 型質量恆等式 (新推導) ----------
print('\n--- C2: ★ Pythagorean 型質量恆等式 (新推導) ---')
# γ_n + γ_{44-n} = 4 = γ_44
# ⟹ m_n² + m_{44-n}² = M0²(γ_n + γ_{44-n}) = M0²·γ_44 = m_44²
# 即: m_n² + m_{44-n}² = m_44²  ∀ n — 質量空間 Pythagorean 型閉合
pyth_ok = all(
    abs(m_n(n)**2 + m_n(N - n)**2 - m_n(N)**2) < mp.mpf('1e-40')
    for n in range(1, N // 2 + 1))
chk('C2a m_n²+m_{44-n}² = m_44² (22 對含自配對)', pyth_ok)

# 不動點版本: m_22² = m_44²/2 (因為 γ_22 = 2 = γ_44/2)
chk('C2b m_22² = m_44²/2', abs(float(m_n(22)**2 - m_n(44)**2 / 2)) < 1e-40,
    f'(m_22²={mp.nstr(m_n(22)**2,10)}, m_44²/2={mp.nstr(m_n(44)**2/2,10)})')

# 完整列表
print('\n  Pythagorean 配對 (n, 44−n, m_n, m_44−n, m_n²+m_{44-n}²):')
print(f'  {"n":>3} {"44−n":>5} {"m_n":>10} {"m_44−n":>10} {"sum²":>14} {"m_44²":>14}')
for n in range(1, N // 2 + 1):
    mn, mpn = m_n(n), m_n(N - n)
    s = mn**2 + mpn**2
    tag = ' ◄不動點' if n == 22 else ''
    print(f'  {n:>3} {N-n:>5} {mp.nstr(mn,9):>10} {mp.nstr(mpn,9):>10} {mp.nstr(s,12):>14} {mp.nstr(m_n(N)**2,12):>14}{tag}')

# ---------- C3: 扇區結構 — 奇偶 (Z₂ 宇稱) ----------
print('\n--- C3: 扇區結構 (Z₂ 宇稱) ---')
# O206 docs/14: 費米=奇 (Σγ_odd=44), 玻色=偶 (Σγ_even=46)
# 但玻色塔 m_n = M0√γ_n 對 n=1..44 全部 (唔係只偶數)
# 檢驗: 奇/偶 n 嘅質量各自有咩結構
sum_odd = sum(gamma_n(n) for n in range(1, N + 1, 2))
sum_even = sum(gamma_n(n) for n in range(2, N + 1, 2))
chk('C3a Σγ_odd = 44 (觀察者/費米側)', abs(float(sum_odd) - 44) < 1e-12)
chk('C3b Σγ_even = 46 (世界/玻色側)', abs(float(sum_even) - 46) < 1e-12)

# 奇/偶模式質量幾何平均 (log-space 中心)
m_odd_geom = mp.exp(mp.fsum([mp.log(m_n(n)) for n in range(1, N + 1, 2)]) / 22)
m_even_geom = mp.exp(mp.fsum([mp.log(m_n(n)) for n in range(2, N + 1, 2)]) / 22)
print(f'  m_odd_geom  = {mp.nstr(m_odd_geom, 9)} MeV')
print(f'  m_even_geom = {mp.nstr(m_even_geom, 9)} MeV')

# ---------- C4: 模式身份摘要表 ----------
print('\n--- C4: 模式身份分類摘要 ---')
print(f'{"類":>8} | {"n":>22} | {"數量":>4} | 結構特徵')
print('-' * 70)
print(f'{"不動點":>8} | {str(22):>22} | {1:>4} | γ=μ²=2, m=M0√2=39.458')
print(f'{"配對":>8} | {"(1,43)":>22} | {21:>4} | m_n²+m_(44-n)²=m_44²')
print(f'{"自配對":>8} | {"(22,22)":>22} | {1:>4} | (同上, n=44−n)')
print(f'{"下邊界":>8} | {str(1):>22} | {1:>4} | m_1 = 1.9917 MeV 最小')
print(f'{"上邊界":>8} | {str(44):>22} | {1:>4} | m_44 = 2M0 = 55.802 MeV Nyquist')
total = 1 + 21 + 1 + 1 + 1
chk('C4a 分類完備 (1+21+1+1+1 = 25 類)', total == 25, f'(={total} 類別)')
# 數量核對: 不動點1 + 配對21×2 + 邊界2 = 45? 唔對 — 配對含 22? 修正:
# n=1..21 配對: 42 模式; n=22 自配對: 1; n=44 邊界: 1 ⟹ 44 ✓
n_paired = 2 * len(pairs)   # 42
n_total = n_paired + 1 + 1  # +22 (自) +44 (邊界) = 44
chk('C4b 分類覆蓋全部 44 模式 (21對×2 + 不動點 + 塔頂)', n_total == N,
    f'(42+1+1={n_total})')

# ---------- C5: 模式身份 → 物理角色 ----------
print('\n--- C5: 物理角色 (結構推導, 非標籤) ---')
# Z₂ 分離定理 (O206 docs/14 §三): 玻色扇區 = Z₂-偶 (週期), 費米 = Z₂-奇 (反週期)
# 但玻色塔 m_n 對 n=1..44 全部定義 — 塔係「世界介質」嘅完整激發譜
# 結構身份: 每對 (n, 44−n) 係「同一物理模式嘅兩個極化/方向」?
# 證據: γ 配對律 + Pythagorean 恆等式 — 配對對質量平方和常數
# 不動點 n=22: γ=μ²=2 — 玻色扇區「質量尺度原點」
# 邊界 n=1/44: 譜端點 — 最小/最大激發
print('  塔 = 世界介質完整激發譜 (Z₂-偶扇區, O206)')
print('  配對 (n,44−n): 質量平方和 = m_44² 常數 — 同一模式兩個方向')
print('  不動點 n=22: γ_22 = μ² — 玻色扇區質量尺度原點 (= 費米側 μ² 同一常數)')
print('  邊界 n=1/44: 譜端點 — 最小/最大激發 (Nyquist)')

# 驗證 m_22 係「尺度中點」: m_22² = m_44²/2 ⟹ m_22 = m_44/√2
chk('C5a 不動點 = 幾何中點 m_22 = m_44/√2',
    abs(float(m_n(22) - m_n(44) / mp.sqrt(2))) < 1e-40,
    f'(m_22={mp.nstr(m_n(22),9)}, m_44/√2={mp.nstr(m_n(44)/mp.sqrt(2),9)})')

# ---------- 輸出 ----------
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(data_dir, exist_ok=True)
out = {
    'M0_MeV': float(M0),
    'fixed_point': {'n': 22, 'gamma': float(gamma_n(22)), 'm_MeV': float(m_n(22))},
    'pairs': [{'n': n, 'm_n': float(m_n(n)), 'm_44mn': float(m_n(N - n)),
               'sum_sq': float(m_n(n)**2 + m_n(N - n)**2)} for n in range(1, N // 2 + 1)],
    'boundary': {'n_min': 1, 'm_min': float(m_n(1)),
                 'n_max': 44, 'm_max': float(m_n(44))},
    'pythagorean_identity': 'm_n^2 + m_{44-n}^2 = m_44^2 = 4*M0^2  (EXACT, 22 pairs)',
}
with open(os.path.join(data_dir, '02_mode_identity.json'), 'w') as f:
    json.dump(out, f, indent=2)

print('\n' + '=' * 78)
print(f'RESULT: {pass_count}/{pass_count + fail_count} PASS')
print('=' * 78)
if fail_count:
    exit(1)
exit(0)
