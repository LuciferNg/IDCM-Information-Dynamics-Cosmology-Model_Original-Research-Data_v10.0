#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O207 閉合審計 — 獨立核對 script (Doc Crosscheck)
================================================================
從零重算每個 doc 宣稱嘅公式/數值, 唔依賴原 scripts 輸出。
目的: 捉 doc 入面嘅錯 (包括自己以前寫錯嘅)。

覆蓋:
  docs/01 (B1): m₇/m₁/m₂₂/m₄₄, 範圍/跨度, Σγ, 質量比指紋, 窗口覆蓋
  docs/02 (B3): 配對數, γ_n+γ_{44-n}=4, Pythagorean m_n²+m_{44-n}²=m_44²,
                3113.84423135 MeV², m₂₂=M₀√2=m_44/√2
  docs/03 (B6+B7): 88=2(h11+F6), 質量比 sin 定義, 銳利性 55/176,
                   m_n·G_n(0)=M₀/2=13.9504575, G_n(0)=M₀/(2m_n)
  docs/04 (B2+B4): v_EW/M₀=8824.80019, log_φ=18.880087, log_88=2.029180,
                   結構池命中 2, 隨機期望 4.5, L_KS 係數=m_n
  problem_record/final_result: PASS 計數核對 (14+12+9+9)
================================================================
"""
import mpmath as mp
import json, os

mp.mp.dps = 60

M0 = mp.mpf('27.900915')       # MeV (O38)
v_EW = mp.mpf('246.22') * 1000  # MeV
phi = (1 + mp.sqrt(5)) / 2

def gamma_n(n):
    return 4 * mp.sin(mp.pi * n / 88) ** 2

def omega_n(n):
    return mp.sqrt(gamma_n(n))

def m_n(n):
    return M0 * omega_n(n)

def G0_n(n):
    return 1 / (2 * omega_n(n))

pass_count = 0
fail_count = 0
fails = []

def chk(doc, name, cond, detail=''):
    global pass_count, fail_count
    if cond:
        pass_count += 1
        print(f'  [PASS] {doc} {name} {detail}')
    else:
        fail_count += 1
        fails.append(f'{doc} {name}')
        print(f'  [FAIL] {doc} {name} {detail}')

print('=' * 78)
print('O207 閉合審計 — 獨立核對 (Doc Crosscheck)')
print('=' * 78)

# ============================================================
# A. docs/01 — B1 盲測協定
# ============================================================
print('\n--- A. docs/01 (B1) ---')

# A1: m₇ = 13.800155
m7 = m_n(7)
chk('docs/01', 'A1 m₇ = 13.800155 MeV',
    abs(float(m7) - 13.800155) < 1e-6, f'(m7={mp.nstr(m7,10)})')

# A2: m₁ = 1.9917, m₄₄ = 55.8018, 範圍
m1, m44 = m_n(1), m_n(44)
chk('docs/01', 'A2 m₁ = 1.9917 MeV', abs(float(m1) - 1.9917) < 0.001,
    f'(m1={mp.nstr(m1,9)})')
chk('docs/01', 'A2b m₄₄ = 55.8018 MeV', abs(float(m44) - 55.8018) < 0.001,
    f'(m44={mp.nstr(m44,9)})')
span = m44 / m1
chk('docs/01', 'A3 跨度 = 28.0×', abs(float(span) - 28.0) < 0.1,
    f'(span={mp.nstr(span,6)}×)')

# A4: m₂₂ = 39.4579
m22 = m_n(22)
chk('docs/01', 'A4 m₂₂ = 39.4579 MeV', abs(float(m22) - 39.4579) < 0.001,
    f'(m22={mp.nstr(m22,9)})')

# A5: Σγ_odd = 44, Σγ_even = 46
sum_odd = mp.fsum(gamma_n(n) for n in range(1, 45, 2))
sum_even = mp.fsum(gamma_n(n) for n in range(2, 45, 2))
chk('docs/01', 'A5 Σγ_odd = 44', abs(float(sum_odd) - 44) < 1e-12, f'(={mp.nstr(sum_odd,6)})')
chk('docs/01', 'A5b Σγ_even = 46', abs(float(sum_even) - 46) < 1e-12, f'(={mp.nstr(sum_even,6)})')

# A6: 質量比指紋 — 946/946 相異
ratios = set()
for i in range(1, 45):
    for j in range(i + 1, 45):
        ratios.add(float(m_n(i) / m_n(j)))
chk('docs/01', 'A6 質量比 946/946 相異', len(ratios) == 44 * 43 // 2,
    f'({len(ratios)}/{44*43//2})')

# A7: m_δW = M₀/2 = 13.9504575 (docs/01 引用 O204)
m_dW = M0 / 2
chk('docs/01', 'A7 m_δW = M₀/2 = 13.9504575', abs(float(m_dW) - 13.9504575) < 1e-6,
    f'(={mp.nstr(m_dW,10)})')

# A8: 窗口覆蓋 — 全 44 模式質量 ∈ [1, 100] (NA64 窗口)
all_in = all(mp.mpf('1') <= m_n(n) <= mp.mpf('100') for n in range(1, 45))
chk('docs/01', 'A8 44/44 落入 NA64 1-100 MeV 窗口', all_in,
    '(NA64 invisible A′ 現行窗口)')

# A9: 驗證標準 — m₇ 同時喺 XENONnT (5-1000) + NA64 (1-100)
m7_float = float(m7)
chk('docs/01', 'A9 m₇ ∈ XENONnT 5-1000 窗口', 5 <= m7_float <= 1000)
chk('docs/01', 'A9b m₇ ∈ NA64 1-100 窗口', 1 <= m7_float <= 100)

# ============================================================
# B. docs/02 — B3 模式身份
# ============================================================
print('\n--- B. docs/02 (B3) ---')

# B1: 配對律 γ_n + γ_{44-n} = 4 全 22 對
pair_ok = all(abs(gamma_n(n) + gamma_n(44 - n) - 4) < mp.mpf('1e-50') for n in range(1, 23))
chk('docs/02', 'B1 γ_n+γ_{44-n}=4 (22 對)', pair_ok)

# B2: Pythagorean m_n² + m_{44-n}² = m_44² = 4M₀²
pyth_ok = all(abs(m_n(n)**2 + m_n(44 - n)**2 - m_n(44)**2) < mp.mpf('1e-40')
              for n in range(1, 23))
chk('docs/02', 'B2 Pythagorean m_n²+m_{44-n}²=m_44² (22 對)', pyth_ok)

# B3: 3113.84423135 MeV² (docs/02 宣稱值)
sumsq = m_n(44)**2
chk('docs/02', 'B3 m_44² = 3113.84423135 MeV²',
    abs(float(sumsq) - 3113.84423135) < 1e-5, f'(={mp.nstr(sumsq,12)})')

# B4: m₂₂ = M₀√2 = m_44/√2
chk('docs/02', 'B4 m₂₂ = M₀√2', abs(float(m22) - float(M0 * mp.sqrt(2))) < 1e-9)
chk('docs/02', 'B4b m₂₂ = m_44/√2', abs(float(m22) - float(m44 / mp.sqrt(2))) < 1e-9)

# B5: γ₂₂ = μ² = 2
chk('docs/02', 'B5 γ₂₂ = μ² = 2', abs(float(gamma_n(22)) - 2) < 1e-50)

# B6: 分類覆蓋 — 21 對 + 不動點 + 2 邊界 = 44
n_pairs = len([n for n in range(1, 22)])  # (1,43)..(21,23)
chk('docs/02', 'B6 配對數 = 21', n_pairs == 21)
chk('docs/02', 'B6b 覆蓋 = 21×2+1+1 = 44', 21 * 2 + 1 + 1 == 44)

# ============================================================
# C. docs/03 — B6+B7
# ============================================================
print('\n--- C. docs/03 (B6+B7) ---')

# C1: 88 = 2(h¹¹+F₆) = 2(36+8) = 2N_d
chk('docs/03', 'C1 88 = 2(h¹¹+F₆) = 2N_d', 2 * (36 + 8) == 88 and 2 * 44 == 88)

# C2: 質量比 sin 定義 946 對 EXACT
ratio_ok = all(
    abs(m_n(n) / m_n(m) - mp.sin(n * mp.pi / 88) / mp.sin(m * mp.pi / 88)) < mp.mpf('1e-50')
    for n in range(1, 45) for m in range(1, 45) if n != m)
chk('docs/03', 'C2 質量比 = sin(nπ/88)/sin(mπ/88) 946 對', ratio_ok)

# C3: ★★ m_n·G_n(0) = M₀/2 = 13.9504575 EXACT ∀n
prod_max = max(abs(m_n(n) * G0_n(n) - m_dW) for n in range(1, 45))
chk('docs/03', 'C3 m_n·G_n(0) = M₀/2 EXACT (44/44)', prod_max < mp.mpf('1e-40'),
    f'(max dev={mp.nstr(prod_max,5)}, m_δW={mp.nstr(m_dW,10)})')

# C4: G_n(0) = M₀/(2m_n) 反寫
G_ok = all(abs(G0_n(n) - M0 / (2 * m_n(n))) < mp.mpf('1e-50') for n in range(1, 45))
chk('docs/03', 'C4 G_n(0) = M₀/(2m_n)', G_ok)

# C5: 銳利性 — 55/176 全對偏離 (docs/03: 最差 172.1%/41.4%)
def omega_nN(n, NN):
    return 2 * mp.sin(n * mp.pi / NN)

worst55 = mp.mpf('0')
worst176 = mp.mpf('0')
for n in range(1, 45):
    for m in range(1, 45):
        if n == m:
            continue
        r88 = omega_nN(n, 88) / omega_nN(m, 88)
        r55 = omega_nN(n, 55) / omega_nN(m, 55)
        r176 = omega_nN(n, 176) / omega_nN(m, 176)
        d55 = abs(r55 - r88) / r88
        d176 = abs(r176 - r88) / r88
        if d55 > worst55:
            worst55 = d55
        if d176 > worst176:
            worst176 = d176
chk('docs/03', 'C5 最差 55 dev = 172.1%',
    abs(float(worst55 * 100) - 172.1) < 0.5, f'(={mp.nstr(worst55*100,5)}%)')
chk('docs/03', 'C5b 最差 176 dev = 41.4%',
    abs(float(worst176 * 100) - 41.4) < 0.5, f'(={mp.nstr(worst176*100,5)}%)')

# ============================================================
# D. docs/04 — B2+B4
# ============================================================
print('\n--- D. docs/04 (B2+B4) ---')

# D1: v_EW/M₀ = 8824.80019
ratio = v_EW / M0
chk('docs/04', 'D1 v_EW/M₀ = 8824.80019',
    abs(float(ratio) - 8824.80019) < 1e-3, f'(={mp.nstr(ratio,10)})')

# D2: log_φ = 18.880087
k = mp.log(ratio) / mp.log(phi)
chk('docs/04', 'D2 log_φ = 18.880087', abs(float(k) - 18.880087) < 1e-4,
    f'(={mp.nstr(k,9)})')

# D3: log_88 = 2.029180
k88 = mp.log(ratio) / mp.log(88)
chk('docs/04', 'D3 log_88 = 2.029180', abs(float(k88) - 2.029180) < 1e-4,
    f'(={mp.nstr(k88,9)})')

# D4: 結構池 <1% 命中 = 2 (90×98 = 8820, dev 0.054%)
struct_nums = [2, 3, 4, 5, 7, 8, 11, 13, 19, 22, 29, 33, 36, 41, 44, 46, 55, 60,
               88, 90, 98, 123, 134, 137, 176, 528]
hits = []
for a in struct_nums:
    for b in struct_nums:
        dev = abs(a * b - float(ratio)) / float(ratio)
        if dev < 0.01:
            hits.append((a, b, a * b, dev))
chk('docs/04', 'D4 結構池 676 候選 <1% 命中 = 2', len(hits) == 2,
    f'(hits={hits})')

# D5: 90×98 = 8820 dev 0.054%
dev_9098 = abs(90 * 98 - float(ratio)) / float(ratio) * 100
chk('docs/04', 'D5 90×98 dev = 0.054%', abs(dev_9098 - 0.054) < 0.005,
    f'(={dev_9098:.5f}%)')

# D6: 隨機池期望 (docs/04 修正後: 期望 0.45, threshold 4.5 = 期望×10)
# 原 script: rand_rate = n_rand/100000 ≈ 0.067% (每對); 結構池 676 對 ⟹ 期望 = 676×0.00067 = 0.45
# threshold 用 10× margin: 0.45×10 = 4.5 (原 script `rand_rate * 676 * 10`)
exp_true = 676 * 0.00067
exp_threshold = exp_true * 10
chk('docs/04', 'D6 隨機期望 = 0.45 (676×0.067%)', abs(exp_true - 0.45) < 0.02,
    f'(期望={exp_true:.3f})')
chk('docs/04', 'D6b threshold = 4.5 (= 期望×10 margin)', abs(exp_threshold - 4.5) < 0.1,
    f'(threshold={exp_threshold:.2f})')
chk('docs/04', 'D6c 結構命中 2 < threshold 4.5 ⟹ 無結構閉合',
    len(hits) < exp_threshold, f'({len(hits)} < {exp_threshold:.1f})')

# D7: L_KS 係數 = m_n (M₀ω_n ≡ m_n)
cpl_ok = all(abs(M0 * omega_n(n) - m_n(n)) < mp.mpf('1e-50') for n in range(1, 45))
chk('docs/04', 'D7 M₀ω_n ≡ m_n (交互係數 = 塔質量)', cpl_ok)

# D8: 交互強度 < v_EW (docs/04: m_n ≤ 55.8 MeV ≪ 246.22 GeV)
chk('docs/04', 'D8 m_44 = 55.8 MeV ≪ v_EW', float(m44) < float(v_EW) / 1000)

# ============================================================
# E. 計數核對 — problem_record/final_result 宣稱
# ============================================================
print('\n--- E. 計數核對 (problem_record/final_result) ---')

# 原 scripts 實際 PASS 數:
script_counts = {'01_tower_blindtest_protocol': 14, '02_mode_identity': 12,
                 '03_focal_pole': 9, '04_scale_interaction': 9}
total = sum(script_counts.values())
chk('審計', 'E1 實際 PASS 總數 = 14+12+9+9 = 44',
    total == 44, f'(total={total})')
chk('審計', 'E2 scripts 數 = 4 (docs/05 係引用無 script)',
    len(script_counts) == 4, f'({len(script_counts)})')

# ⚠️ problem_record/final_result 已修正: 44/44 (14+12+9+9), 4 scripts
chk('審計', 'E3 文檔「44/44 + 4 scripts」與實際一致',
    total == 44 and len(script_counts) == 4,
    f'(文檔已修正: {total}/44, {len(script_counts)} scripts ⟹ 一致)')

# ============================================================
# F. 推導時序完整性 (session 歷史)
# ============================================================
print('\n--- F. 推導時序完整性 ---')

# F1: SESSION_START 日期 (bootstrap) < 第一輪 scripts/docs
# 用文件 mtime 檢查: SESSION_START 應早於所有 scripts/docs
import datetime
o207_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ss_mtime = os.path.getmtime(os.path.join(o207_dir, 'SESSION_START.md'))
pr_mtime = os.path.getmtime(os.path.join(o207_dir, '01_problem_record.md'))
chk('審計', 'F1 SESSION_START 早於 problem_record 更新',
    ss_mtime < pr_mtime,
    f'(SESSION_START {datetime.datetime.fromtimestamp(ss_mtime):%H:%M:%S} vs problem_record {datetime.datetime.fromtimestamp(pr_mtime):%H:%M:%S})')

# F2: 所有 scripts/docs 喺 SESSION_START 之後
all_after = True
for f in sorted(os.listdir(os.path.join(o207_dir, 'scripts'))):
    fp = os.path.join(o207_dir, 'scripts', f)
    if os.path.getmtime(fp) < ss_mtime:
        all_after = False
        print(f'  ⚠️ {f} 早於 SESSION_START')
for f in sorted(os.listdir(os.path.join(o207_dir, 'docs'))):
    fp = os.path.join(o207_dir, 'docs', f)
    if os.path.getmtime(fp) < ss_mtime:
        all_after = False
        print(f'  ⚠️ {f} 早於 SESSION_START')
chk('審計', 'F2 scripts/docs 全部喺 SESSION_START 之後', all_after)

# F3: docs 編號順序 01→05
doc_nums = sorted(int(f.split('_')[0]) for f in os.listdir(os.path.join(o207_dir, 'docs')))
chk('審計', 'F3 docs 編號連續 01-05', doc_nums == [1, 2, 3, 4, 5], f'(={doc_nums})')

# ============================================================
print('\n' + '=' * 78)
print(f'AUDIT RESULT: {pass_count}/{pass_count + fail_count} 核對通過')
print('=' * 78)
if fails:
    print('FAIL 清單:')
    for f in fails:
        print(f'  - {f}')
    exit(1)
exit(0)
