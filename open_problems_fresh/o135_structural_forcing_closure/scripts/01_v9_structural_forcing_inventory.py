#!/usr/bin/env python3
"""
O135 — scripts/01: v9.0 structural_forcing.py 完整盤點 (Inventory)
==================================================================
目的: 逐項重算 v9.0 `wfield_lattice/structural_forcing.py` 全部輸出值 (mpmath dps=50),
      落盤做遷移判決嘅輸入。本 script **唔做** v10.0 交叉核對 (見 scripts/02)。

來源: /home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/wfield_lattice/structural_forcing.py
零改動原則: 只重算, 唔修正 v9.0 公式。

每個 check 斷言「重算值 == v9.0 腳本 print 出嘅值」— 驗證盤點本身無誤。
"""
import json, os
import mpmath as mp

mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
PHI_INV = 1 / PHI

# ── L2 Lucas (v9.0: L_n = φⁿ + (−1)ⁿφ⁻ⁿ) ───────────────────────────────
L = [mp.nint(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]
# ── L3 Fibonacci ──────────────────────────────────────────────────────
F = [mp.mpf(0), mp.mpf(1)]
for n in range(2, 12):
    F.append(F[n-1] + F[n-2])

# ── L4 CY₃ ────────────────────────────────────────────────────────────
h11 = L[2]**2 * L[3]          # 36
h21 = 2 * L[4]**2             # 98
CY3 = h11 + h21               # 134

# ── L5 管道 ───────────────────────────────────────────────────────────
SYNC = mp.mpf(2)
B = mp.mpf(4)
M = mp.floor((CY3 - SYNC) / L[3])      # 33
EPS = PHI_INV / 4             # 0.1545085...
KAPPA = mp.mpf(1) / 16

# ── L6 VEV ────────────────────────────────────────────────────────────
VEV_nat = mp.sqrt(EPS / (2 * KAPPA))       # √(2/φ)

# ── L7 EW scale ───────────────────────────────────────────────────────
V_EW = PHI**8 * (PHI**3 + 1)               # φ¹¹ + φ⁸
SCALE = V_EW / VEV_nat

# ── L8 sector gaps ────────────────────────────────────────────────────
k_u = M * PHI_INV / 2
k_d = (M - L[4]) * PHI_INV / 2 - PHI_INV**4
k_l = (M - 2 * L[4]) * PHI_INV / 2

# ── L9a D_quark ───────────────────────────────────────────────────────
D_quark = 1 + (h11 / h21) * EPS * (1 + EPS)
D_lep = mp.mpf(1)

# ── L9b masses ────────────────────────────────────────────────────────
M_Pl = mp.mpf('2.435e18')
delta = PHI**88 / M_Pl - 1
m_H_nat = 2 * mp.sqrt(KAPPA)
m_H = m_H_nat * V_EW
m_t_nat = VEV_nat / mp.sqrt(2)
m_t = m_t_nat * SCALE
m_b_nat = m_t_nat * PHI_INV**k_d * D_quark
m_b = m_b_nat * SCALE
m_tau_nat = m_t_nat * delta
m_tau = m_tau_nat * SCALE

def mass_at_k(ref_nat, k, D=1):
    return ref_nat * PHI_INV**k * D * SCALE

m_charm = mass_at_k(m_t_nat, k_u)
m_strange = mass_at_k(m_b_nat, k_d)
m_muon = mass_at_k(m_tau_nat, k_l)

def compute_K(fib_idx, s, k, extra_a=0):
    sign = (-1)**(k + s + 1)
    Fn = F[fib_idx]
    a = k - 3 * (s - 1) + extra_a
    return sign * Fn * CY3 * PHI_INV**a

def first_gen_ratio(fib_idx, s, k, extra_a=0):
    Fn = F[fib_idx]
    Kn = compute_K(fib_idx, s, k, extra_a)
    return (Fn + EPS**3 * Kn) / CY3**s

m_electron = m_tau * first_gen_ratio(5, 2, 5, L[0]**2 - PHI_INV**2)
m_down = m_b * first_gen_ratio(8, 2, 8, 0)
m_up = m_t * first_gen_ratio(9, 3, 9, 0)

fermions = {
    "top": m_t, "charm": m_charm, "up": m_up,
    "bottom": m_b, "strange": m_strange, "down": m_down,
    "tau": m_tau, "muon": m_muon, "electron": m_electron,
}

# ── L11 CKM ───────────────────────────────────────────────────────────
Vcb = PHI**2 / 64
lam = PHI_INV**3 - 3 * EPS**3
eta = (M - 2 * L[4]) * PHI / (4 * (L[5] + L[4] + L[3]))
rho = PHI_INV**4
Vub = lam**3 * mp.sqrt(rho**2 + eta**2) / (1 - lam**2 / 2)

# ── L12 α⁻¹ ───────────────────────────────────────────────────────────
alpha_inv = CY3 + 3 + 15 * PHI_INV / 256

# ── L13 宇宙學 ────────────────────────────────────────────────────────
omega_L = 4 / (PHI**4 - 1)
H0 = mp.mpf('72.59')
z_c = mp.mpf(3) / 5
bump = EPS * mp.e**-1
T_CMB = 2 * mp.mpf('1.4168e32') * mp.e**-74 * (CY3 / (L[0]+L[1]+L[2]+L[3])**2) * (1 - PHI_INV**(L[2]**2))

# ── PDG (v9.0 對照值) ─────────────────────────────────────────────────
PDG = {
    "top": 172.76, "charm": 1.27, "up": 0.00216,
    "bottom": 4.18, "strange": 0.093, "down": 0.00467,
    "tau": 1.77686, "muon": 0.10566, "electron": 0.000511,
}

# ═══ checks: 重算 == v9.0 腳本 print 值 (stdout 逐項對) ═════════════════
results = []
def chk(name, got, want_str, tol=mp.mpf('1e-5')):
    want = mp.mpf(want_str)
    dev = abs(got / want - 1) if want != 0 else abs(got - want)
    ok = dev < tol
    results.append((name, ok, got, want, dev))
    print(f"  [{'✔' if ok else '✘'}] {name:<26} got={mp.nstr(got,12):>16} want={want_str:>14} dev={mp.nstr(dev,3)}")
    return ok

print("=" * 78)
print("O135 scripts/01 — v9.0 structural_forcing.py 完整盤點 (mpmath dps=50)")
print("=" * 78)

print("\n[L1-L4] 種子 / Lucas / Fibonacci / CY₃")
chk("φ = (1+√5)/2", PHI, "1.618033988749895")
chk("L₀", L[0], "2"); chk("L₄", L[4], "7"); chk("L₅", L[5], "11"); chk("L₆", L[6], "18")
chk("F₅", F[5], "5"); chk("F₈", F[8], "21"); chk("F₉", F[9], "34")
chk("h¹¹ = L₂²L₃", h11, "36"); chk("h²¹ = 2L₄²", h21, "98"); chk("CY₃ = h¹¹+h²¹", CY3, "134")

print("\n[L5-L7] 管道 / VEV / EW scale")
chk("SYNC", SYNC, "2"); chk("B", B, "4"); chk("M = (CY₃−2)/4", M, "33")
chk("ε = φ⁻¹/4", EPS, "0.1545084972"); chk("κ = 1/16", KAPPA, "0.0625")
chk("VEV_nat = √(ε/2κ)", VEV_nat, "1.1117859405")
chk("V_EW = φ¹¹+φ⁸", V_EW, "245.983739")
chk("SCALE", SCALE, "221.2510")

print("\n[L8] sector gaps (⚠️ v9.0 腳本冇 print — 只作記錄, 不入 PASS 計數)")
print(f"  k_u = {mp.nstr(k_u,10)}   k_d = {mp.nstr(k_d,10)}   k_l = {mp.nstr(k_l,10)}")

print("\n[L9] 質量")
chk("m_H", m_H, "122.9919"); chk("m_t", m_t, "173.936770")
chk("m_b", m_b, "4.162441"); chk("m_τ", m_tau, "1.776588")
chk("m_c", m_charm, "1.285959"); chk("m_s", m_strange, "0.093485"); chk("m_μ", m_muon, "0.105330")
chk("m_e", m_electron, "0.000511", tol=mp.mpf('3e-3'))
chk("m_d", m_down, "0.004651", tol=mp.mpf('1e-4'))
chk("m_u", m_up, "0.002171", tol=mp.mpf('1e-4'))
chk("D_quark", D_quark, "1.065528"); chk("δ = φ⁸⁸/M_Pl−1", delta, "0.010214", tol=mp.mpf('1e-4'))

print("\n[L11-L13] CKM / α⁻¹ / 宇宙學")
chk("Vcb = φ²/64", Vcb, "0.040907"); chk("λ = φ⁻³−3ε³", lam, "0.225002")
chk("Vub", Vub, "0.004425", tol=mp.mpf('1e-3'))
chk("α⁻¹ = CY₃+3+15φ⁻¹/256", alpha_inv, "137.0362")
chk("Ω_Λ = 4/(φ⁴−1)", omega_L, "0.683282")
chk("H₀ (v9.0 硬設)", H0, "72.59"); chk("z_c", z_c, "0.6")
chk("T_CMB = 2T_Pl e⁻⁷⁴ CY₃/10² (1−φ⁻⁹)", T_CMB, "2.7283", tol=mp.mpf('1e-4'))

npass = sum(1 for r in results if r[1])
print(f"\n{'='*78}\nRESULT: {npass}/{len(results)} PASS — v9.0 盤點完成\n{'='*78}")

# ── 落盤 ──────────────────────────────────────────────────────────────
out = {
    "source": "IDCM-v9.0--W-Field-Lattice/wfield_lattice/structural_forcing.py",
    "phi": mp.nstr(PHI, 30),
    "constants": {k: mp.nstr(v, 20) for k, v in {
        "SYNC": SYNC, "B": B, "M": M, "EPS": EPS, "KAPPA": KAPPA,
        "h11": h11, "h21": h21, "CY3": CY3, "VEV_nat": VEV_nat,
        "V_EW": V_EW, "SCALE": SCALE}.items()},
    "sector_gaps": {k: mp.nstr(v, 20) for k, v in {"k_u": k_u, "k_d": k_d, "k_l": k_l}.items()},
    "masses_GeV": {k: mp.nstr(v, 12) for k, v in fermions.items()},
    "m_H": mp.nstr(m_H, 12), "delta": mp.nstr(delta, 12), "D_quark": mp.nstr(D_quark, 12),
    "ckm": {k: mp.nstr(v, 12) for k, v in {"Vcb": Vcb, "lam": lam, "eta": eta, "rho": rho, "Vub": Vub}.items()},
    "alpha_inv": mp.nstr(alpha_inv, 12),
    "cosmology": {"omega_L": mp.nstr(omega_L, 12), "H0": mp.nstr(H0, 8),
                  "z_c": mp.nstr(z_c, 4), "bump": mp.nstr(bump, 8), "T_CMB": mp.nstr(T_CMB, 12)},
    "pdg": PDG,
    "result": f"{npass}/{len(results)} PASS",
}
os.makedirs("data", exist_ok=True)
with open("data/01_v9_inventory.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/01_v9_inventory.json")
