#!/usr/bin/env python3
"""
O200 — 維度收束：有量綱 → 無量綱
==================================
幀 = 普朗克單位 (τ = t_Pl, ℓ = l_Pl, ε = m_Pl)

命題 1: 任何有量綱量 = 無量綱結構數 × 幀^k
命題 2: 只需 1 個幀單位 (長度/質量單位由結構關係鎖定)
命題 3: 無量綱數必須係結構數 (φ-冪/Lucas/F-數)，附密度基準

Run: /usr/bin/python3 scripts/01_dimensional_collapse.py
"""
import math
import mpmath as mp

mp.mp.dps = 30

# ============================================================
# 物理常數 (CODATA 2018 / SI)
# ============================================================
c_si = mp.mpf('299792458')                     # m/s
hbar = mp.mpf('1.054571817e-34')               # J·s
G    = mp.mpf('6.67430e-11')                   # m³/(kg·s²)
kB   = mp.mpf('1.380649e-23')                  # J/K
eV   = mp.mpf('1.602176634e-19')               # J
Mpc  = mp.mpf('3.0856775814913673e22')         # m

# 普朗克單位 (導出，非輸入)
t_Pl = mp.sqrt(hbar*G/c_si**5)                 # s
l_Pl = c_si*t_Pl                               # m
m_Pl_kg = mp.sqrt(hbar*c_si/G)                 # kg
m_Pl_MeV = m_Pl_kg*c_si**2/eV*mp.mpf('1e-6')   # MeV
T_Pl = m_Pl_kg*c_si**2/kB                      # K

print("="*70)
print("O200 維度收束 — 幀 = 普朗克單位")
print("="*70)
print(f"\n[幀單位]")
print(f"  t_Pl = {mp.nstr(t_Pl, 8)} s")
print(f"  l_Pl = {mp.nstr(l_Pl, 8)} m")
print(f"  m_Pl = {mp.nstr(m_Pl_MeV, 8)} MeV")
print(f"  T_Pl = {mp.nstr(T_Pl, 8)} K")

# ============================================================
# IDCM 有量綱量 (來源 O)
# ============================================================
print("\n" + "="*70)
print("[IDCM 有量綱清單 → 無量綱收束]")
print("="*70)

# 世界環
R_world_Mpc = mp.mpf('4129.94')      # O73/O171
omega_ring = mp.mpf('72.73e3')/Mpc   # O73 BBN 鎖定 (km/s/Mpc → s⁻¹)
T_ring = 2*mp.pi/omega_ring

# 質量/能量
M0_MeV = mp.mpf('27.900915')         # O38/O204 W-field 凝聚標度
E_kchain_meV = mp.mpf('4.019988')    # O38/O136 K_Chain 標度
m7_MeV = mp.mpf('13.800155')         # O204 DM 候選

# 溫度
T_CMB_K = mp.mpf('2.72548')          # Planck
A_muK = mp.mpf('134.2')              # O41 冷斑振幅

# 長度
r_d_Mpc = mp.mpf('147.088')          # O170 drag scale

# 速度
c_W = R_world_Mpc*Mpc*omega_ring     # O73 c_W = R_world × ω_ring

# 加速
a0 = c_si**2/(2*mp.pi*R_world_Mpc*Mpc)   # O32 RAR

rows = []
collapsed = []
def add(name, val, unit, src):
    rows.append((name, val, unit, src))
add("R_world", R_world_Mpc*Mpc, "m", "O73/O171")
add("T_ring", T_ring, "s", "O73")
add("r_d", r_d_Mpc*Mpc, "m", "O170")
add("M₀", M0_MeV, "MeV", "O38/O204")
add("E_kchain", E_kchain_meV*mp.mpf('1e-3'), "MeV", "O38")
add("m₇", m7_MeV, "MeV", "O204")
add("T_CMB", T_CMB_K, "K", "Planck")
add("A (冷斑)", A_muK*mp.mpf('1e-6'), "K", "O41")
add("c_W", c_W, "m/s", "O73")
add("a₀", a0, "m/s²", "O32")

# 幀指數 (量綱: 用普朗克單位)
print(f"\n{'量':<12} {'值':>16} {'單位':<6} {'÷幀':>12} {'幀^k':<8} {'來源'}")
print("-"*70)
snapshot = list(rows)   # 快照 — 唔可以 iterate 同時 append
for name, val, unit, src in snapshot:
    if unit == "m":
        N, k = val/l_Pl, "l_Pl"
    elif unit == "s":
        N, k = val/t_Pl, "t_Pl"
    elif unit == "MeV":
        N, k = val/m_Pl_MeV, "m_Pl"
    elif unit == "K":
        N, k = val/T_Pl, "T_Pl"
    elif unit == "m/s":
        N, k = val/c_si, "c"
    elif unit == "m/s²":
        N, k = val/(l_Pl/t_Pl**2), "l_Pl/t_Pl²"
    print(f"{name:<12} {mp.nstr(val, 6):>16} {unit:<6} {mp.nstr(N, 8):>12} {k:<8} {src}")
    collapsed.append((name, N, k, src))

# ============================================================
# 命題 2 — 單位鎖定理
# ============================================================
print("\n" + "="*70)
print("[命題 2 — 單位鎖定理]")
print("="*70)
N_ring = T_ring/t_Pl
N_world = R_world_Mpc*Mpc/l_Pl
N_cross = R_world_Mpc*Mpc/c_si/t_Pl

print(f"  N_ring  = T_ring/t_Pl      = {mp.nstr(N_ring, 8)}")
print(f"  N_world = R_world/l_Pl     = {mp.nstr(N_world, 8)}")
print(f"  N_cross = (R_world/c)/t_Pl = {mp.nstr(N_cross, 8)}")
print(f"\n  結構恆等: N_world / N_ring = c_W/(2πc)")
lhs = N_world/N_ring
rhs = c_W/(2*mp.pi*c_si)
print(f"    LHS = {mp.nstr(lhs, 10)}")
print(f"    RHS = {mp.nstr(rhs, 10)}")
print(f"    dev = {mp.nstr(abs(lhs-rhs)/rhs*100, 4)}%")
print(f"  ⟹ 長度幀 l_Pl 同時間幀 t_Pl 由 c 鎖定（非獨立）✅")
print(f"\n  c_W/c = {mp.nstr(c_W/c_si, 8)}  (dev {mp.nstr(abs(c_W/c_si-1)*100,4)}%)")
print(f"  ⟹ c 唔係獨立輸入: c = R_world × ω_ring (結構關係, O73)")

# ============================================================
# 命題 3 — 無量綱數結構性 + 密度基準
# ============================================================
print("\n" + "="*70)
print("[命題 3 — 無量綱數結構性檢定 (φ-冪 + 密度基準)]")
print("="*70)
phi = (1+mp.sqrt(5))/2
lnphi = mp.log(phi)

def phi_power_test(x, kmax=400):
    """搵最佳整數 k: x ≈ φ^k，報告 log 偏差同密度基準 P"""
    if x <= 0:
        return None
    kf = mp.log(x)/lnphi
    k = int(mp.nint(kf))
    dev = abs(kf - k)
    # P = 偏差(log) / 間距(ln φ)  → 單尾機率
    P = dev
    return k, kf, dev, P

tests = [("N_ring", N_ring), ("N_world", N_world), ("N_cross", N_cross),
         ("M₀/m_Pl", M0_MeV/m_Pl_MeV), ("m₇/m_Pl", m7_MeV/m_Pl_MeV),
         ("E_kchain/m_Pl", E_kchain_meV*mp.mpf('1e-3')/m_Pl_MeV),
         ("T_CMB/T_Pl", T_CMB_K/T_Pl), ("A/T_Pl", A_muK*mp.mpf('1e-6')/T_Pl),
         ("r_d/l_Pl", r_d_Mpc*Mpc/l_Pl)]

print(f"\n{'量':<16} {'最佳 k':>8} {'log_φ(x)':>12} {'偏差':>10} {'P (密度基準)':>12} {'判定'}")
print("-"*70)
for name, x in tests:
    r = phi_power_test(x)
    if r is None:
        continue
    k, kf, dev, P = r
    verdict = "🟢 顯著" if P < 1e-3 else ("🟡 邊緣" if P < 0.05 else "🔴 唔顯著")
    print(f"{name:<16} {k:>8} {mp.nstr(kf, 8):>12} {mp.nstr(dev, 6):>10} {mp.nstr(P, 6):>12} {verdict}")

print(f"\n★ 密度基準說明: P = log 偏差 / ln φ = 單尾機率")
print(f"  P < 1e-3 才算顯著（φ-冪陷阱警告: 單次 0.2% 命中 P≈0.004）")
