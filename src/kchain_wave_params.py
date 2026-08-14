"""
K_Chain 44 個模式嘅完整波參數
===============================
波長、頻率、群速度、相速度、能量、振幅、阻抗
"""

import math
from dataclasses import dataclass, field

# ============================================================
# 基本常數
# ============================================================
R_H = 4129.94        # Mpc, K_Chain 環周長
Nd = 44              # site 數
c = 299792.458       # km/s, 光速
H0 = 72.59           # km/s/Mpc

# 單位轉換
Mpc_to_km = 3.085677581e19
Gyr = 3.15576e16     # s/Gyr
hbar = 6.582119569e-16  # eV·s

# 導出量
dx = R_H / Nd        # Mpc, site 間距
c_ms = c * 1e3       # m/s
omega_scale = 88 * c_ms / (R_H * Mpc_to_km * 1e3)  # rad/s 標度因子


@dataclass
class KChainMode:
    """K_Chain 單個模式嘅波參數"""
    n: int                    # 模式編號 (1..44)
    wavelength: float         # Mpc
    omega: float              # rad/s
    frequency: float          # 1/Gyr
    period: float             # Gyr
    v_g: float                # km/s, 群速度
    v_p: float                # km/s, 相速度
    gamma: float              # eigenvalue (能量)
    amplitude: float          # 振幅
    impedance: float          # 阻抗
    z2_dual_n: int            # Z₂ 對偶模式編號
    z2_dual_gamma: float      # Z₂ 對偶 eigenvalue

    def __repr__(self) -> str:
        return (f"n={self.n:2d} | λ={self.wavelength:8.2f} Mpc | "
                f"f={self.frequency:10.4f} 1/Gyr | v_g={self.v_g/c:6.4f}c | "
                f"γ={self.gamma:6.4f} | A={self.amplitude:6.4f}")


def compute_modes() -> list[KChainMode]:
    """計算全部 44 個 K_Chain 模式嘅波參數"""
    modes = []
    for n in range(1, Nd + 1):
        # 波長
        λ_n = R_H / n

        # 角頻率 (rad/s)
        ω_n = omega_scale * math.sin(math.pi * n / 88)
        
        # 頻率 (1/Gyr)
        f_n = ω_n * Gyr / (2 * math.pi)
        
        # 周期 (Gyr)
        T_n = 1.0 / f_n if f_n > 0 else float('inf')

        # 群速度
        v_g = c * math.cos(math.pi * n / 88)
        
        # 相速度
        v_p = c * math.sin(math.pi * n / 88) / (math.pi * n / 88)

        # 能量 (eigenvalue)
        γ_n = 4 * math.sin(math.pi * n / 88) ** 2
        
        # 振幅
        A_n = 2 * abs(math.sin(math.pi * n / 88))
        
        # 阻抗 Z_n = γ_n / |cos(πn/88)|
        cos_val = abs(math.cos(math.pi * n / 88))
        Z_n = γ_n / cos_val if cos_val > 1e-12 else float('inf')

        # Z₂ 對偶: γ_n + γ_{44-n} = 4
        n_dual = Nd - n
        if n_dual == 0:
            n_dual = Nd
        γ_dual = 4 * math.sin(math.pi * n_dual / 88) ** 2

        modes.append(KChainMode(
            n=n, wavelength=λ_n, omega=ω_n, frequency=f_n,
            period=T_n, v_g=v_g, v_p=v_p, gamma=γ_n,
            amplitude=A_n, impedance=Z_n,
            z2_dual_n=n_dual, z2_dual_gamma=γ_dual
        ))
    return modes


def print_all_modes(modes: list[KChainMode]):
    """打印全部 44 個模式"""
    print(f"{'n':>3} | {'λ(Mpc)':>10} | {'f(1/Gyr)':>11} | {'T(Gyr)':>10} | "
          f"{'v_g/c':>7} | {'v_p/c':>7} | {'γ':>6} | {'A':>6} | {'Z':>8} | "
          f"{'Z₂ 對偶':>8}")
    print("-" * 95)
    for m in modes:
        print(f"{m.n:3d} | {m.wavelength:10.2f} | {m.frequency:11.4f} | "
              f"{m.period:10.6f} | {m.v_g/c:7.4f} | {m.v_p/c:7.4f} | "
              f"{m.gamma:6.4f} | {m.amplitude:6.4f} | {m.impedance:8.2f} | "
              f"{m.z2_dual_n:2d} γ={m.z2_dual_gamma:5.4f}")


def summary(modes: list[KChainMode]):
    """關鍵模式摘要"""
    print("\n=== 關鍵模式 ===")
    for n in [1, 2, 4, 11, 22, 33, 44]:
        m = modes[n - 1]
        print(f"n={n:2d}: λ={m.wavelength:8.2f} Mpc, "
              f"f={m.frequency:10.4f} 1/Gyr, "
              f"v_g={m.v_g/c:.4f}c, "
              f"γ={m.gamma:.4f}, "
              f"Z={m.impedance:8.2f}")


if __name__ == "__main__":
    modes = compute_modes()
    print_all_modes(modes)
    summary(modes)
    
    # Z₂ 對偶驗證
    print("\n=== Z₂ 對偶驗證: γ_n + γ_{44-n} = 4 ===")
    for n in range(1, 23):
        m = modes[n - 1]
        dual = modes[m.z2_dual_n - 1]
        s = m.gamma + dual.gamma
        status = "✅" if abs(s - 4.0) < 1e-12 else "❌"
        print(f"n={n:2d}: γ_{n}={m.gamma:6.4f} + γ_{m.z2_dual_n:2d}={dual.gamma:6.4f} = {s:.4f} {status}")