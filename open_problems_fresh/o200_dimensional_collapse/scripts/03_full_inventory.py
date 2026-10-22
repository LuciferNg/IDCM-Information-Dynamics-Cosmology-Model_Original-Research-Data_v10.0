#!/usr/bin/env python3
"""
O200 script 03 — 完整有量綱清單 + 收束
=========================================
① 補齊清單：IDCM 全部有量綱量（唔止 script 01 嘅 10 個）

Run: /usr/bin/python3 scripts/03_full_inventory.py
"""
import mpmath as mp
mp.mp.dps = 30

# 常數
c_si = mp.mpf('299792458'); hbar = mp.mpf('1.054571817e-34')
G = mp.mpf('6.67430e-11'); kB = mp.mpf('1.380649e-23')
eV = mp.mpf('1.602176634e-19'); Mpc = mp.mpf('3.0856775814913673e22')
Gyr = mp.mpf('3.1556952e16')  # s
t_Pl = mp.sqrt(hbar*G/c_si**5); l_Pl = c_si*t_Pl
m_Pl_MeV = mp.sqrt(hbar*c_si/G)*c_si**2/eV*mp.mpf('1e-6')
T_Pl = mp.sqrt(hbar*c_si/G)*c_si**2/kB

# 世界環
R_world = mp.mpf('4129.94')*Mpc
omega_ring = mp.mpf('72.73e3')/Mpc
T_ring = 2*mp.pi/omega_ring
tau = 1/omega_ring
H0 = mp.mpf('71.157e3')/Mpc          # O170
T_sync = 2*mp.pi/H0

# 完整清單: (名, 值, 單位, 維度, 來源)
INV = [
    # --- 長度 (m) ---
    ("R_world",        R_world,                    "m", "L", "O73/O171"),
    ("r_d",            mp.mpf('147.088')*Mpc,      "m", "L", "O170"),
    ("λ_sync",         mp.mpf('294.8770')*Mpc,     "m", "L", "O73"),
    ("a (格點)",       R_world/88,                 "m", "L", "O36 (R_world/88)"),
    # --- 時間 (s) ---
    ("τ (幀=1/ω_ring)", tau,                       "s", "T", "O73"),
    ("T_ring",         T_ring,                     "s", "T", "O73"),
    ("T_sync",         T_sync,                     "s", "T", "O40"),
    ("T_age",          mp.mpf('11100.64')*Gyr,     "s", "T", "O51"),
    ("Γ⁻¹",            mp.mpf('1.6474e-17')**-1,   "s", "T", "O138"),
    # --- 質量/能量 (MeV) ---
    ("M₀",             mp.mpf('27.900915'),        "MeV", "M", "O38/O204"),
    ("m₇",             mp.mpf('13.800155'),        "MeV", "M", "O204"),
    ("m_δW",           mp.mpf('13.9505'),          "MeV", "M", "O204"),
    ("E_kchain",       mp.mpf('4.019988e-3'),      "MeV", "M", "O38"),
    ("m_ν (M₂₃)",      mp.mpf('22.1e-9'),          "MeV", "M", "O49"),
    ("v_SM",           mp.mpf('246.22e3'),         "MeV", "M", "O40"),
    ("M_Z (SM)",       mp.mpf('91.1876e3'),        "MeV", "M", "PDG"),
    # --- 溫度 (K) ---
    ("T_CMB",          mp.mpf('2.72548'),          "K", "Θ", "Planck"),
    ("A (冷斑)",       mp.mpf('134.2e-6'),         "K", "Θ", "O41"),
    ("A_5節點",        mp.mpf('12271.55091e-6'),   "K", "Θ", "O3"),
    # --- 速度 (m/s) ---
    ("c_W",            R_world*omega_ring,         "m/s", "V", "O73"),
    ("c/45 (分支)",    c_si/45,                    "m/s", "V", "O203"),
    # --- 加速 (m/s²) ---
    ("a₀ (RAR)",       c_si**2/(2*mp.pi*R_world),  "m/s²", "A", "O32"),
]

FRAME = {"L": ("l_Pl", l_Pl), "T": ("t_Pl", t_Pl), "M": ("m_Pl", m_Pl_MeV),
         "Θ": ("T_Pl", T_Pl), "V": ("c", c_si), "A": ("l_Pl/t_Pl²", l_Pl/t_Pl**2)}

print("="*88)
print("O200 ① 完整有量綱清單 → 收束 (幀 = 普朗克單位)")
print("="*88)
print(f"\n{'量':<16} {'值':>16} {'單位':<7} {'÷幀':>16} {'幀^k':<10} {'來源'}")
print("-"*88)
for name, val, unit, dim, src in INV:
    fname, fval = FRAME[dim]
    N = val/fval
    print(f"{name:<16} {mp.nstr(val, 8):>16} {unit:<7} {mp.nstr(N, 10):>16} {fname:<10} {src}")

print(f"\n總數: {len(INV)} 個有量綱量")
print(f"維度類別: L={sum(1 for x in INV if x[3]=='L')}, T={sum(1 for x in INV if x[3]=='T')}, "
      f"M={sum(1 for x in INV if x[3]=='M')}, Θ={sum(1 for x in INV if x[3]=='Θ')}, "
      f"V={sum(1 for x in INV if x[3]=='V')}, A={sum(1 for x in INV if x[3]=='A')}")

# 無量綱量 (對照組 — 唔需要收束)
print(f"\n[無量綱量 — 唔需要收束, 對照組]")
DIMLESS = [
    ("η_B", "6.0636e-10", "O13 BBN"),
    ("Y_p", "0.2496", "O13 BBN"),
    ("⁷Li/H", "1.5843e-10", "O13 BBN"),
    ("σ_8", "0.748", "O100"),
    ("α⁻¹(0)", "137", "O139"),
    ("sin²θ_W", "0.2208", "O142"),
    ("Ω_Λ", "41/60", "O39/O148"),
    ("Ω_b", "19/450", "O13"),
]
for n, v, s in DIMLESS:
    print(f"  {n:<12} = {v:<14} [{s}]")

# 幀無關比例 (收束後唯一有物理意義嘅量)
print(f"\n[收束後幀無關比例 (選樣)]")
pairs = [
    ("R_world/r_d", R_world/(mp.mpf('147.088')*Mpc)),
    ("R_world/λ_sync", R_world/(mp.mpf('294.8770')*Mpc)),
    ("R_world/a", mp.mpf(88)),
    ("T_ring/T_sync", T_ring/T_sync),
    ("T_age/T_ring", mp.mpf('11100.64')*Gyr/T_ring),
    ("M₀/m₇", mp.mpf('27.900915')/mp.mpf('13.800155')),
    ("M₀/E_kchain", mp.mpf('27.900915')/mp.mpf('4.019988e-3')),
    ("M₀/m_ν", mp.mpf('27.900915')/mp.mpf('22.1e-9')),
    ("v_SM/M₀", mp.mpf('246.22e3')/mp.mpf('27.900915')),
    ("T_CMB/A", mp.mpf('2.72548')/mp.mpf('134.2e-6')),
]
for n, v in pairs:
    print(f"  {n:<20} = {mp.nstr(v, 10)}")
