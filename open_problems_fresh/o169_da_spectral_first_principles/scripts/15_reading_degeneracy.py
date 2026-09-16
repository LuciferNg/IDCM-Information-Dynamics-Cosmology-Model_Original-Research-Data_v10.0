#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/15 — B2: 截距讀法簡併 (數域分離 + 三方簡併表)
===========================================================
原狀 (docs/04 §B2): 譜讀法 1/<v_g>_{1..22} vs φ讀法 sqrt5/2, 差 0.097%, Δχ² = 0.012
本腳本:
  U1  數域分離: 譜值 ∈ Q(ζ_176) vs φ值 ∈ Q(√5) — mp.identify 全 miss ⇒ 兩者唔可能相等
  U2  完整 K 掃描: 邊個 (統計量, K) 過 |σ|max ≤ 1 ⇒ 實際上係**三方**簡併 (唔係兩方)
  U3  結構主張對照表 (譜 vs φ 各自嘅賣點)
  U4  δ(1/2) 檢驗 (Z2 自對偶點)
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi; phi = (1 + mp.sqrt(5)) / 2; inv = 1 / phi
R = mp.mpf('4129.94'); rd = pi * R / 88 * mp.mpf(420) / 421
N = 44
vg  = {n: mp.cos(pi * n / 88) for n in range(1, N + 1)}
sec = {n: 1 / mp.cos(pi * n / 88) for n in range(1, N + 1)}
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]

def chi2(b):
    t = mx = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = mp.log(1 + mp.mpf(z), 4)
        s = (R * (1 - 4 ** (-l)) * (l + b) / rd - mp.mpf(dm)) / mp.mpf(em)
        t += s * s; mx = max(mx, abs(s))
    return t, mx

b_spec = 1 / (mp.fsum(vg[n] for n in range(1, 23)) / 22)
b_phi  = mp.sqrt(5) / 2
b_sec  = mp.fsum(sec[n] for n in range(1, 22)) / 21

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 78)
print("O169/15 — B2: 截距讀法簡併")
print("=" * 78)

# ---------- U1: 數域分離 ----------
print("\nU1. 數域分離 (兩讀法係唔係同一個數?)")
print(f"  譜 b_spec = 1/<v_g>_{{1..22}} = {mp.nstr(b_spec, 16)}")
print(f"  φ  b_phi  = sqrt5/2            = {mp.nstr(b_phi, 16)}")
print(f"  差 = {mp.nstr(abs(b_spec - b_phi), 8)}  (相對 {float(abs(b_spec-b_phi)/b_spec*100):.4f}%)")
found = False
for basis in (['sqrt(5)'], ['sqrt(5)', 'sqrt(2)', 'sqrt(3)'], ['pi'], ['sqrt(5)', 'pi']):
    r = None
    try:
        r = mp.identify(b_spec, basis, tol=mp.mpf('1e-25'), maxcoeff=10**6)
    except Exception:
        r = None
    print(f"    mp.identify(b_spec, {basis}) -> {r}")
    if r: found = True
chk("U1  b_spec 唔係 φ-代數/π-代數 (identify 全 miss)", not found)
print(f"      解析: <v_g> = sin(pi/8)cos(23pi/176)/(22 sin(pi/176))")
print(f"            ⇒ b_spec ∈ Q(ζ_176), 176 = 16·11 (φ(176) = 80) — 次數遠高於 Q(√5) 嘅 2")
chk("U1b 兩值唔相等 (差 > 1e-3)", abs(b_spec - b_phi) > mp.mpf('1e-3'),
    f"差 = {mp.nstr(abs(b_spec-b_phi), 6)}")

# ---------- U2: 完整 K 掃描 ----------
print("\nU2. 完整 K 掃描 (a = 1 固定): 邊個 (統計量, K) 過 |σ|max ≤ 1")
passers = []
for stat, f in (('1/<v_g>', lambda K: 1 / (mp.fsum(vg[n] for n in range(1, K + 1)) / K)),
                ('<sec>',   lambda K: mp.fsum(sec[n] for n in range(1, K + 1)) / K),
                ('1/sqrt<v_g^2>', lambda K: 1 / mp.sqrt(mp.fsum(vg[n] ** 2 for n in range(1, K + 1)) / K))):
    ok = []
    for K in range(1, 44):
        t, mx = chi2(f(K))
        if mx <= 1: ok.append((K, f(K), t, mx))
    print(f"    {stat:<14} 過 |σ|max≤1: " + (", ".join(f"K={K}" for K, *_ in ok) if ok else "(冇)"))
    passers += [(stat, K, v, t, mx) for K, v, t, mx in ok]

print(f"\n  候選截距全表 (含 φ 影子):")
allc = [(s, K, v, *chi2(v)) for s, K, v, _, _ in passers] + [('φ-代數', 0, b_phi, *chi2(b_phi))]
allc.sort(key=lambda r: r[3])
print(f"    {'來源':<14}{'K':>4}{'值':>15}{'chi2/5':>10}{'|s|max':>9}")
for s, K, v, t, mx in allc:
    print(f"    {s:<14}{K if K else '-':>4}{mp.nstr(v, 12):>15}{float(t):>10.4f}{float(mx):>9.3f}")
chk("U2  通過者 >= 3 個 (三方簡併, 唔止兩方)", len(allc) >= 3, f"共 {len(allc)} 個")
dchi = max(r[3] for r in allc) - min(r[3] for r in allc)
chk("U2b Δχ²(最大-最小) < 1 ⇒ 數據無法分辨", dchi < 1, f"Δχ² = {float(dchi):.4f}")

# ---------- U3: 結構主張對照 ----------
print("\nU3. 結構主張對照")
print(f"    {'讀法':<26}{'值':>14}{'χ²/5':>9}{'結構主張'}")
rows = [
    ('譜 1/<v_g>_{1..22}', b_spec, 'E(0) = 逆平均群速度; 窗口 K=22 由數據唯一選出 (43 掃描)'),
    ('譜 <sec>_{1..21}',   b_sec,  'E(0) = 平均群延遲; 窗口 K=21 由數據唯一選出; 同 <sec>_{1..28} 同族'),
    ('φ √5/2',             b_phi,  '√5/2 = 1/2+φ⁻¹ = 1+φ⁻³/2 (三形); δ(1/2) = 0; E(1/2) = φ'),
]
for nm, v, claim in rows:
    t, mx = chi2(v)
    print(f"    {nm:<26}{mp.nstr(v, 12):>14}{float(t):>9.4f}  {claim}")

# ---------- U4: δ(1/2) ----------
print("\nU4. Z2 自對偶點 ℓ = 1/2 (z = 1) 嘅 δ")
for nm, b in (('譜 1/<v_g>', b_spec), ('譜 <sec>', b_sec), ('φ √5/2', b_phi)):
    d12 = (1 - 2 * inv) * mp.mpf('0.5') + (b - 1)
    print(f"    {nm:<12} δ(1/2) = {mp.nstr(d12, 10):<16} E(1/2) = {mp.nstr(mp.mpf('0.5')+b, 12)}  (φ = {mp.nstr(phi, 12)})")
chk("U4  只有 φ 讀法 δ(1/2) = 0 EXACT",
    abs((1 - 2 * inv) * mp.mpf('0.5') + (b_phi - 1)) < mp.mpf('1e-35'),
    f"φ: {mp.nstr((1-2*inv)*mp.mpf('0.5')+(b_phi-1), 5)}")
chk("U4b 譜讀法 δ(1/2) != 0 (差 ~1.1e-3)", abs((1 - 2 * inv) * mp.mpf('0.5') + (b_spec - 1)) > mp.mpf('1e-3'),
    f"譜: {mp.nstr((1-2*inv)*mp.mpf('0.5')+(b_spec-1), 8)}")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS) + len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 78)
print(f"""
結論 (B2 狀態: 🔴 維持, 但已精確刻畫):
  U1  兩讀法**證明唔相等**: b_spec ∈ Q(ζ_176) (80 次) vs √5/2 ∈ Q(√5) (2 次);
      0.0965% 一致 = 數值巧合 (唔係同一個結構常數)。
  U2  實際上係**三方**簡併 (唔止兩方): 1/<v_g>_{{1..22}} / <sec>_{{1..21}} / √5/2,
      Δχ² = {float(dchi):.4f} ⇒ 數據完全無法分辨。
  U3  各讀法嘅結構主張: 譜族有「窗口由數據唯一選出」+ 群速度/群延遲物理讀法;
      φ 族有 δ(1/2) = 0 + E(1/2) = φ 精確 (Z2 自對偶點)。
  U4  B3 嘅 T3 發現 (piR 所需截距 = <sec>_{{1..28}}) **支持譜族** (sec 家族),
      但 DESI 區間嘅窗口 (21/22) 同 Nyquist (28) 之間嘅 K(ℓ) 律未導出。
  🔴 裁決需要: 截距嘅第一原理推導 (E(0) = 逆群速度? 定 E(1/2) = φ?)。
""")
