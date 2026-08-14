"""
IDCM v10.0 — 幾何指數壓抑 (Geometric Exponential Suppression)
=============================================================
質量層級 m ∝ M_Pl × exp(-V_cycle) 嘅 CY₃(36,98) 推導
"""

import math

# ============================================================
# 基本常數
# ============================================================
φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
R_H = 4129.94  # Mpc
Nd = 44
hbar = 6.582119569e-16  # eV·s
c = 299792.458  # km/s

# Planck 質量
M_Pl = 1.220890e22  # MeV/c²
M_Pl_eV = 1.220890e28  # eV

# SM 粒子質量 (MeV)
SM_MASSES = {
    "e": 0.51099895,
    "u": 2.16,
    "d": 4.67,
    "s": 93.4,
    "mu": 105.6583745,
    "c": 1270.0,
    "tau": 1776.86,
    "b": 4180.0,
    "W": 80377.0,
    "Z": 91187.6,
    "H": 125250.0,
    "t": 172760.0,
}

# ============================================================
# CY₃(36,98) 幾何參數
# ============================================================
class CY3Geometry:
    """
    CY₃(36,98) Calabi-Yau 三維流形嘅幾何參數
    h¹¹ = 36 Kähler moduli (尺度參數)
    h²¹ = 98 complex structure moduli (形狀參數)
    """

    def __init__(self):
        self.h11 = 36  # Kähler moduli
        self.h21 = 98  # Complex structure moduli
        self.chi = 2 * (self.h11 - self.h21)  # Euler 示性數 = -124
        self.total_moduli = self.h11 + self.h21  # 134

    def cycle_volume(self, n: int) -> float:
        """
        CY₃ 上第 n 個 cycle 嘅體積 (Planck 單位)
        假設: cycle 體積由 K_Chain mode 嘅 eigenvalue 決定
        V_cycle(n) ∝ exp(-γ_n) 或某種函數
        """
        gamma_n = 4 * math.sin(math.pi * n / 88) ** 2
        # 模型: cycle 體積 = φ^(-γ_n) 或類似
        return φ ** (-gamma_n)

    def mass_from_cycle(self, n: int, scale: float = 1.0) -> float:
        """
        從 CY₃ cycle 體積計算粒子質量
        m = M_Pl × exp(-V_cycle) × scale
        """
        V = self.cycle_volume(n)
        return M_Pl * math.exp(-V) * scale

    def mass_ratio_from_cycles(self, n1: int, n2: int) -> float:
        """兩個 cycle 嘅質量比"""
        return self.mass_from_cycle(n1) / self.mass_from_cycle(n2)


# ============================================================
# 指數壓抑模型
# ============================================================
class ExponentialSuppression:
    """
    幾何指數壓抑模型
    m_i = M_Pl × exp(-S_i) × f_i
    其中 S_i 係 instanton action 或 cycle volume
    """

    def __init__(self):
        self.cy3 = CY3Geometry()

    def compute_suppression(self, target_mass: float, name: str = "") -> dict:
        """
        對一個目標質量，計算需要嘅壓抑因子
        返回: exp(-S) = m_target / M_Pl
        """
        needed_S = -math.log(target_mass / M_Pl)
        return {
            "name": name,
            "mass_MeV": target_mass,
            "mass_ratio": target_mass / M_Pl,
            "needed_S": needed_S,
            "needed_cycles": int(needed_S / 4.0),  # 每個 cycle 貢獻 ~4
        }

    def analyze_mass_hierarchy(self):
        """分析整個質量層級嘅指數壓抑結構"""
        particles = sorted(SM_MASSES.items(), key=lambda x: x[1])

        print("=" * 70)
        print("SM 粒子質量嘅指數壓抑分析")
        print("=" * 70)
        print(f"Planck 質量 M_Pl = {M_Pl:.4e} MeV")
        print(f"最大質量比 (m_t/m_e) = {SM_MASSES['t'] / SM_MASSES['e']:.2e}")
        print(f"最小壓抑 exp(-S) = {SM_MASSES['e'] / M_Pl:.2e}")
        print()

        print(f"{'粒子':>5} | {'質量(MeV)':>12} | {'log(M_Pl/m)':>12} | {'S需要的':>10} | {'cycle數':>7}")
        print("-" * 55)
        for name, mass in particles:
            info = self.compute_suppression(mass, name)
            print(f"{name:>5} | {mass:>12.4f} | "
                  f"{info['needed_S']:>12.4f} | "
                  f"{info['needed_S']:>10.2f} | "
                  f"{info['needed_cycles']:>7d}")

        # 質量間距分析
        print("\n" + "=" * 70)
        print("質量間距嘅指數壓抑")
        print("=" * 70)
        print(f"{'間距':>20} | {'質量比':>12} | {'ΔS':>10} | {'Δcycle':>8}")
        print("-" * 55)
        gaps = [
            ("e → u", "e", "u"),
            ("u → d", "u", "d"),
            ("d → s", "d", "s"),
            ("s → mu", "s", "mu"),
            ("mu → c", "mu", "c"),
            ("c → tau", "c", "tau"),
            ("tau → b", "tau", "b"),
            ("b → W", "b", "W"),
            ("W → Z", "W", "Z"),
            ("Z → H", "Z", "H"),
            ("H → t", "H", "t"),
        ]
        for label, p1, p2 in gaps:
            m1 = SM_MASSES[p1]
            m2 = SM_MASSES[p2]
            ratio = m2 / m1
            dS = math.log(M_Pl / m1) - math.log(M_Pl / m2)
            dcycle = int(dS / 4.0)
            print(f"{label:>20} | {ratio:>12.4f} | {dS:>10.4f} | {dcycle:>8d}")


# ============================================================
# K_Chain 模式與 CY₃ cycle 嘅對應
# ============================================================
class KChainToCY3Projection:
    """
    K_Chain 44 個模式到 CY₃(36,98) 134 個 cycle 嘅投影
    每個 K_Chain mode 對應一個 CY₃ cycle
    """

    def __init__(self):
        self.cy3 = CY3Geometry()

    def mode_to_cycle_volume(self, n: int) -> float:
        """
        K_Chain mode n 對應嘅 CY₃ cycle 體積
        模型: cycle volume ∝ 1/γ_n × φ^(n/44)
        """
        gamma_n = 4 * math.sin(math.pi * n / 88) ** 2
        # 高 n (高能量) → 小 cycle volume → 大質量
        # 低 n (低能量) → 大 cycle volume → 小質量
        if gamma_n < 0.01:
            gamma_n = 0.01  # 避免除零
        V = 1.0 / gamma_n * φ_inv ** (n / 11)
        return V

    def predicted_mass(self, n: int) -> float:
        """從 mode n 預測粒子質量 (MeV)"""
        V = self.mode_to_cycle_volume(n)
        m = M_Pl * math.exp(-V)
        return m

    def scan_all_modes(self):
        """掃描所有 44 個 mode 嘅預測質量"""
        print("=" * 70)
        print("K_Chain → CY₃ 投影質量預測")
        print("=" * 70)
        print(f"{'n':>3} | {'γ_n':>8} | {'V_cycle':>10} | {'exp(-V)':>12} | {'預測質量(MeV)':>16} | {'match SM?':>10}")
        print("-" * 70)
        for n in range(1, 45):
            m = self.predicted_mass(n)
            # 檢查最近嘅 SM 粒子
            best_match = ""
            best_err = 999
            for name, mass in SM_MASSES.items():
                err = abs(m / mass - 1) * 100
                if err < best_err:
                    best_err = err
                    best_match = f"{name}:{err:.1f}%"
            gamma_n = 4 * math.sin(math.pi * n / 88) ** 2
            V = self.mode_to_cycle_volume(n)
            expV = math.exp(-V)
            if m < 1e-10:
                print(f"{n:3d} | {gamma_n:8.4f} | {V:10.4f} | {expV:12.4e} | {m:>16.4e} | {best_match:>10}")
            else:
                print(f"{n:3d} | {gamma_n:8.4f} | {V:10.4f} | {expV:12.4e} | {m:>16.4f} | {best_match:>10}")


# ============================================================
# 主程式
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — 幾何指數壓抑")
    print("質量層級 = M_Pl × exp(-V_cycle) × K_Chain beat")
    print("=" * 70)

    # 1. 分析質量層級
    exp_sup = ExponentialSuppression()
    exp_sup.analyze_mass_hierarchy()

    # 2. K_Chain → CY₃ 投影
    proj = KChainToCY3Projection()
    proj.scan_all_modes()

    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
🚫 停止：高階 beat 搜尋 (密集度陷阱)
✅ 開始：幾何指數壓抑模型

機制:
  質量 = M_Pl × exp(-V_cycle) × f(K_Chain beat)

其中:
  - V_cycle = CY₃(36,98) 上某個 cycle 嘅體積 (Planck unit)
  - exp(-V_cycle) 提供 6 個數量級嘅質量層級
  - f(K_Chain beat) 提供代間精細結構

關鍵問題:
  1. 134 個 CY₃ cycle 點樣對應到 SM 粒子?
     (36 Kähler + 98 complex structure)
  2. 點樣保證只有特定 cycle 被激發?
     (選擇律 = 拓撲量子數守恆)
  3. 點樣做盲測預測?
     (預測一個未測定嘅 CKM 角或中微子質量)
""")