#!/usr/bin/env python3
"""
O134 — scripts/01: v9.0 CY3 拓撲算子 完整盤點 (Inventory)
==========================================================
目的: 逐項重算 v9.0 `wfield_lattice/cy3_topological_operator.md` (304 行)
      + `wfield_lattice/verify_cy3_operator.py` (84 行) 嘅全部輸出值 (mpmath dps=50),
      落盤做遷移判決嘅輸入。本 script **唔做** v10.0 交叉核對 (見 scripts/02)。

來源:
  /home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/wfield_lattice/cy3_topological_operator.md
  /home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/wfield_lattice/verify_cy3_operator.py

零改動原則: 只重算, 唔修正 v9.0 公式。
每個 check 斷言「重算值 == v9.0 文件/腳本 印出嘅值」— 驗證盤點本身無誤。
⚠️ md 內部有三套互不相容嘅 K_n 正規化 (§5.2/§5.3/§5.4 vs §5.6/§5.7 vs script),
   本 script 逐套獨立盤點 (記錄, 唔當錯誤 — 判決見 scripts/03)。
"""
import json, os
import mpmath as mp

mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
PHI_INV = 1 / PHI
L = [mp.nint(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]   # Lucas
F = [mp.mpf(0), mp.mpf(1)]
for n in range(2, 12):
    F.append(F[n-1] + F[n-2])                                    # Fibonacci

# ── v9.0 常數 (cy3_topological_operator.md + verify_cy3_operator.py) ────
h11 = L[2]**2 * L[3]          # L₂²L₃ = 9·4 = 36
h21 = 2 * L[4]**2             # 2L₄² = 2·49 = 98
CY3 = h11 + h21               # 134
EPS = PHI_INV / 4             # ε = φ⁻¹/4
KAPPA = mp.mpf(1) / 16
M = mp.floor((CY3 - 2) / L[3])                    # 33
VEV_nat = mp.sqrt(EPS / (2 * KAPPA))
V_EW = PHI**8 * (PHI**3 + 1)                      # φ¹¹ + φ⁸
SCALE = V_EW / VEV_nat
M_Pl = mp.mpf('2.435e18')

# ── §3 D_lattice 拓撲干涉項 ────────────────────────────────────────────
I_intersect = h11 - h21                            # −62
ratio = h11 / h21                                  # 36/98 = 18/49

# ── §4 一階/二階/無窮級數 ──────────────────────────────────────────────
D1 = 1 + ratio * EPS                               # 一階
D2 = 1 + ratio * EPS * (1 + EPS)                   # 二階 (自能)
Dinf = 1 + ratio * EPS / (1 - EPS)                 # 無窮幾何級數

# ── verify_cy3_operator.py 質量鏈 ──────────────────────────────────────
k_d = (M - L[4]) * PHI_INV / 2 - PHI_INV**4
m_t_nat = VEV_nat / mp.sqrt(2)
m_t = m_t_nat * SCALE
m_b_bare = m_t_nat * PHI_INV**k_d * SCALE
ratio_d = PHI_INV**k_d                             # m_s/m_b 比 (script: 再乘一次)
m_b_1 = m_b_bare * D1
m_s_1 = m_b_bare * ratio_d * D1
m_b_2 = m_b_bare * D2
m_s_2 = m_b_bare * ratio_d * D2

# ── §5 第一代: F_n/CY₃^s × (1+ε³K_n) ─────────────────────────────────
E3 = EPS**3
# §5.3 K_n = k_mode × (h¹¹/h²¹) × φ^(−s)
def K_53(k_mode, s):
    return k_mode * ratio * PHI_INV**s
# §5.7 K_n = sign × F_n × CY₃ × φ^(−a),  a = k − 3(s−1) + Δa
def K_57(fib_idx, s, k, extra_a=0):
    sign = (-1)**(k + s + 1)
    a = k - 3 * (s - 1) + extra_a
    return sign * F[fib_idx] * CY3 * PHI_INV**a
# script 正規化: (F_n + ε³K_n)/CY₃^s
def ratio_script(fib_idx, s, k, extra_a=0):
    return (F[fib_idx] + E3 * K_57(fib_idx, s, k, extra_a)) / CY3**s
# md §5.2 正規化: F_n/CY₃^s × (1 + ε³K_n)
def ratio_md(fib_idx, s, Kn):
    return F[fib_idx] / CY3**s * (1 + E3 * Kn)

PDG = {"top": mp.mpf('172.76'), "charm": mp.mpf('1.27'), "up": mp.mpf('0.00216'),
       "bottom": mp.mpf('4.18'), "strange": mp.mpf('0.093'), "down": mp.mpf('0.00467'),
       "tau": mp.mpf('1.77686'), "muon": mp.mpf('0.10566'), "electron": mp.mpf('0.000511')}

m_electron = PDG["tau"] * ratio_script(5, 2, 5, L[0]**2 - PHI_INV**2)
m_t_computed = V_EW / mp.sqrt(2)                       # v9.0 script: m_t = V_EW/√2 = 173.93677
m_b_computed = m_b_bare * D2                           # v9.0 script: m_b = m_b_bare × D_quark (=D2)
m_down_ref = m_b_computed * ratio_script(8, 2, 8, 0)   # m_d = m_b × ratio (computed m_b)
m_up_ref = m_t_computed * ratio_script(9, 3, 9, 0)     # m_u = m_t × ratio (computed m_t)

# ── §6 CMB ────────────────────────────────────────────────────────────
T_Pl = mp.mpf('1.4168e32')
T_CMB_bare = 2 * T_Pl * mp.e**(-74)
T_CMB = T_CMB_bare * (CY3 / (L[0]+L[1]+L[2]+L[3])**2) * (1 - PHI_INV**(L[2]**2))

# ═══ checks ══════════════════════════════════════════════════════════
results = []
def chk(name, got, want_str, tol=mp.mpf('1e-6')):
    want = mp.mpf(want_str)
    dev = abs(got / want - 1) if want != 0 else abs(got - want)
    ok = dev < tol
    results.append((name, bool(ok), mp.nstr(got, 12), want_str, mp.nstr(dev, 3)))
    print(f"  [{'✔' if ok else '✘'}] {name:<34} got={mp.nstr(got,12):>18} "
          f"want={want_str:>16} dev={mp.nstr(dev,3)}")
    return ok

print("=" * 84)
print("O134 scripts/01 — v9.0 cy3_topological_operator.md + verify_cy3_operator.py 盤點 (dps=50)")
print("=" * 84)

print("\n[§2-§3] CY₃ 幾何 / 投影維度 / 交點數")
chk("h¹¹ = L₂²L₃ = 36", h11, "36")
chk("h²¹ = 2L₄² = 98", h21, "98")
chk("P_CY₃ = h¹¹+h²¹ = 134", CY3, "134")
chk("I(h¹¹,h²¹) = h¹¹−h²¹ = −62", I_intersect, "-62")
chk("|h¹¹/h²¹| = 36/98", ratio, "0.3673469388")
chk("§2 色三重態投影 = 98/134", h21 / CY3, "0.7313432836")

print("\n[§4] D_lattice 一階 / 二階 / 無窮級數 (md 值)")
chk("D⁽¹⁾ md = 1.056758", D1, "1.056758", tol=mp.mpf('1e-6'))
chk("D⁽²⁾ md = 1.065528", D2, "1.065528", tol=mp.mpf('1e-6'))
chk("D(∞) md = 1.0671", Dinf, "1.0671", tol=mp.mpf('1e-4'))
chk("m_b (D⁽¹⁾) md = 4.128", m_b_bare * D1, "4.128", tol=mp.mpf('1e-3'))
chk("m_s (D⁽¹⁾) md = 0.0927", m_s_1, "0.0927", tol=mp.mpf('1e-3'))
chk("m_b (D(∞)) md = 4.169", m_b_bare * Dinf, "4.169", tol=mp.mpf('1e-3'))
chk("m_s (D(∞)) md = 0.0936", m_s_1 / D1 * Dinf, "0.0936", tol=mp.mpf('1e-3'))

print("\n[verify_cy3_operator.py stdout] (逐項對 v9.0 腳本 print 值)")
chk("D1 stdout = 1.05675822", D1, "1.05675822")
chk("D2 stdout = 1.06552785", D2, "1.06552785")
chk("m_b (D1) stdout = 4.128182", m_b_1, "4.128182")
chk("m_s (D1) stdout = 0.092715", m_s_1, "0.092715", tol=mp.mpf('1e-5'))
chk("m_b (D2) stdout = 4.162441", m_b_2, "4.162441")
chk("m_s (D2) stdout = 0.093485", m_s_2, "0.093485", tol=mp.mpf('1e-5'))
chk("m_b_bare = 3.9065 (md §4)", m_b_bare, "3.9065", tol=mp.mpf('1e-4'))
chk("m_s/m_b_bare 比 = 0.02246 (md §4)", ratio_d, "0.02246", tol=mp.mpf('2e-3'))

print("\n[§5.4 表 — md §5.2/§5.3 正規化 F_n/CY₃^s × (1+ε³K_n)]")
chk("Base e/τ = 5/134²", F[5] / CY3**2, "0.0002785", tol=mp.mpf('1e-3'))
chk("Base d/b = 21/134²", F[8] / CY3**2, "0.001169", tol=mp.mpf('1e-3'))
chk("Base u/t = 34/134³", F[9] / CY3**3, "0.00001413", tol=mp.mpf('1e-3'))
chk("§5.4 K_n(e) = 0.697", K_53(5, 2), "0.697", tol=mp.mpf('1e-2'))
chk("§5.4 K_n(d) = 1.115", K_53(8, 2), "1.115", tol=mp.mpf('1e-2'))
# ★ 發現類 check: md §5.4 表列 K_n(u)=0.689, 但 §5.3 公式 (k_mode×h¹¹/h²¹×φ⁻ˢ) 給 0.7805
#   ⟹ §5.4 表與 §5.3 公式在 u 項唔一致 (dev 13.3%); 而 e/d 兩項一致 (dev ~0.7%)
k_u_53 = K_53(9, 3)
chk("★§5.4 K_n(u)=0.689 ≠ §5.3 公式 0.7805 (發現: 內部不一致)",
    abs(k_u_53 / mp.mpf('0.689') - 1) > mp.mpf('0.1'),
    "1", tol=mp.mpf('1e-6'))
chk("§5.4 預測比 e/τ = 0.0002792", ratio_md(5, 2, mp.mpf('0.697')), "0.0002792", tol=mp.mpf('1e-3'))
chk("§5.4 預測比 d/b = 0.001174", ratio_md(8, 2, mp.mpf('1.115')), "0.001174", tol=mp.mpf('1e-3'))
chk("§5.4 預測比 u/t = 0.00001416", ratio_md(9, 3, mp.mpf('0.689')), "0.00001416", tol=mp.mpf('1e-3'))
chk("§5.4 實際比 e/τ = 0.0002876", PDG["electron"]/PDG["tau"], "0.0002876", tol=mp.mpf('1e-3'))
chk("§5.4 實際比 d/b = 0.001117", PDG["down"]/PDG["bottom"], "0.001117", tol=mp.mpf('1e-3'))
chk("§5.4 實際比 u/t = 0.00001250", PDG["up"]/PDG["top"], "0.00001250", tol=mp.mpf('1e-3'))

print("\n[§5.6/§5.7 — 反推 K_n (由 PDG 解出) 同 §5.7 預測 K_n]")
chk("K_5 actual = +44.43", (PDG["electron"]/PDG["tau"]*CY3**2 - F[5]) / E3, "44.43", tol=mp.mpf('2e-3'))
chk("K_8 actual = −254.60", (PDG["down"]/PDG["bottom"]*CY3**2 - F[8]) / E3, "-254.60", tol=mp.mpf('2e-3'))
chk("K_9 actual = −1061.86", (PDG["up"]/PDG["top"]*CY3**3 - F[9]) / E3, "-1061.86", tol=mp.mpf('2e-3'))
chk("§5.7 K_8 pred = −253.9", K_57(8, 2, 8, 0), "-253.9", tol=mp.mpf('3e-3'))
chk("§5.7 K_9 pred = −1075.3", K_57(9, 3, 9, 0), "-1075.3", tol=mp.mpf('3e-3'))
chk("§5.7 K_5 pred = +44.87", K_57(5, 2, 5, L[0]**2 - PHI_INV**2), "44.87", tol=mp.mpf('3e-3'))

print("\n[§5 — script 正規化 (F_n+ε³K_n)/CY₃^s 之質量]")
chk("m_e = 0.000511 (PDG)", m_electron, "0.000511", tol=mp.mpf('3e-3'))
chk("m_d = 0.004651 (md §5.4 腳本值)", m_down_ref, "0.004651", tol=mp.mpf('3e-3'))
chk("m_u = 0.002171 (md §5.4 腳本值)", m_up_ref, "0.002171", tol=mp.mpf('3e-3'))

print("\n[§6 CMB]")
chk("T_bare = 2·T_Pl·e⁻⁷⁴ = 2.06", T_CMB_bare, "2.06", tol=mp.mpf('3e-3'))
chk("CY₃/10² = 1.34 → 2.765 K", T_CMB_bare * 1.34, "2.765", tol=mp.mpf('3e-3'))
chk("T_CMB = 2.728 K (md §6.4)", T_CMB, "2.728", tol=mp.mpf('1e-3'))
chk("修正因子 = 2.73/2.06 = 1.323", mp.mpf('2.73') / T_CMB_bare, "1.323", tol=mp.mpf('3e-3'))

npass = sum(1 for r in results if r[1])
print(f"\n{'='*84}\nRESULT: {npass}/{len(results)} PASS — v9.0 CY₃ 拓撲算子盤點完成\n{'='*84}")

out = {
    "source_md": "IDCM-v9.0--W-Field-Lattice/wfield_lattice/cy3_topological_operator.md",
    "source_py": "IDCM-v9.0--W-Field-Lattice/wfield_lattice/verify_cy3_operator.py",
    "phi": mp.nstr(PHI, 30),
    "geometry": {"h11": mp.nstr(h11, 12), "h21": mp.nstr(h21, 12), "CY3": mp.nstr(CY3, 12),
                 "I_intersect": mp.nstr(I_intersect, 12), "ratio_h11_h21": mp.nstr(ratio, 20)},
    "eps_phi_form": mp.nstr(EPS, 20),
    "D_operators": {"D1": mp.nstr(D1, 12), "D2": mp.nstr(D2, 12), "Dinf": mp.nstr(Dinf, 12)},
    "masses_GeV": {"m_b_D1": mp.nstr(m_b_1, 10), "m_s_D1": mp.nstr(m_s_1, 10),
                   "m_b_D2": mp.nstr(m_b_2, 10), "m_s_D2": mp.nstr(m_s_2, 10),
                   "m_b_bare": mp.nstr(m_b_bare, 10),
                   "m_e": mp.nstr(m_electron, 10), "m_d": mp.nstr(m_down_ref, 10),
                   "m_u": mp.nstr(m_up_ref, 10)},
    "K_n_sets": {
        "sec5_3_formula": {k: mp.nstr(K_53(a, b), 10) for k, (a, b) in
                           {"e": (5, 2), "d": (8, 2), "u": (9, 3)}.items()},
        "sec5_4_stated": {"e": "0.697", "d": "1.115", "u": "0.689"},
        "sec5_7_pred": {"K5": mp.nstr(K_57(5, 2, 5, L[0]**2 - PHI_INV**2), 10),
                        "K8": mp.nstr(K_57(8, 2, 8, 0), 10),
                        "K9": mp.nstr(K_57(9, 3, 9, 0), 10)},
        "reverse_engineered_from_PDG": {
            "K5": mp.nstr((PDG["electron"]/PDG["tau"]*CY3**2 - F[5]) / E3, 10),
            "K8": mp.nstr((PDG["down"]/PDG["bottom"]*CY3**2 - F[8]) / E3, 10),
            "K9": mp.nstr((PDG["up"]/PDG["top"]*CY3**3 - F[9]) / E3, 10)},
    },
    "T_CMB_v9": {"bare_2TPl_em74": mp.nstr(T_CMB_bare, 10), "final_K": mp.nstr(T_CMB, 10),
                 "e_folds": 74, "decomposition": "74 = 59(inflation) + 15(radiation)"},
    "pdg": {k: mp.nstr(v, 10) for k, v in PDG.items()},
    "result": f"{npass}/{len(results)} PASS",
}
os.makedirs("data", exist_ok=True)
with open("data/01_v9_cy3_inventory.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/01_v9_cy3_inventory.json")
