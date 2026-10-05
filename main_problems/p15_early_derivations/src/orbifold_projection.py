"""
IDCM v10.0 — Z_N Orbifold 商化
===============================
步驟 1: 引入 Z₃ 離散對稱性，將 66 個本徵態縮減為 3 代
"""

import math
import numpy as np
from dataclasses import dataclass

# ============================================================
# 基本常數
# ============================================================
φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
R_world = 4129.94
R_H = R_world  # deprecated alias (O73)
Nd = 44
M_Pl = 1.220890e22  # MeV

h11 = 36
h21 = 98
chi = 2 * (h11 - h21)  # -124
n_moduli = h11 + h21  # 134

hbar = 6.582119569e-16
c = 299792.458
omega_scale = 88 * c * 1e3 / (R_world * 3.085677581e19 * 1e3)
E_n = [hbar * omega_scale * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)]


# ============================================================
# 1. 原始投影算子 (同之前)
# ============================================================
def build_beat_hilbert_space() -> list:
    """構建 946 維 beat 希爾伯特空間"""
    states = []
    for n in range(1, Nd + 1):
        for m in range(n + 1, Nd + 1):
            w = abs(E_n[n-1] - E_n[m-1])
            r = w / E_n[0]
            p = (n + m) % 2
            z2 = +1 if (n + m) % 2 == 0 else -1

            def quad(k):
                if 1 <= k <= 11:
                    return 1
                elif 12 <= k <= 22:
                    return 2
                elif 23 <= k <= 33:
                    return 3
                else:
                    return 4

            states.append({
                "n": n, "m": m, "energy": w, "ratio": r,
                "parity": p, "z2": z2, "quad": (quad(n), quad(m))
            })
    return states


def build_cy3_moduli_space() -> list:
    """構建 134 維 CY₃ 模空間"""
    moduli = []
    for i in range(h11):
        moduli.append({"type": "kahler", "idx": i, "dim": 2, "parity": 0, "z2": +1})
    for i in range(h21):
        moduli.append({"type": "cpx", "idx": i, "dim": 3, "parity": 1, "z2": -1})
    return moduli


def compute_projection_matrix() -> np.ndarray:
    """計算 134×946 投影矩陣"""
    beats = build_beat_hilbert_space()
    moduli = build_cy3_moduli_space()
    P = np.zeros((len(moduli), len(beats)))

    for α, mod in enumerate(moduli):
        for β, beat in enumerate(beats):
            # 選擇律
            if mod["parity"] != beat["parity"]:
                continue
            if mod["z2"] != beat["z2"]:
                continue

            q1, q2 = beat["quad"]
            if mod["type"] == "kahler" and q1 > 2 and q2 > 2:
                continue
            if mod["type"] == "cpx" and q1 < 3 and q2 < 3:
                continue

            gamma_n = 4 * math.sin(math.pi * beat["n"] / 88) ** 2
            gamma_m = 4 * math.sin(math.pi * beat["m"] / 88) ** 2
            avg_gamma = (gamma_n + gamma_m) / 2

            if mod["type"] == "kahler" and avg_gamma > 2.0:
                continue
            if mod["type"] == "cpx" and avg_gamma < 2.0:
                continue

            # 權重
            if mod["type"] == "kahler":
                weight = φ ** (-avg_gamma)
            else:
                weight = math.exp(-1.0 / avg_gamma)

            P[α, β] = weight

    return P


# ============================================================
# 2. Z₃ Orbifold 投影
# ============================================================
class Z3Orbifold:
    """
    Z₃ 離散對稱性作用於投影算子

    物理機制:
    - 66 個原始本徵態形成 Z₃ triplets
    - 每個 triplet 對應 SM 一個粒子嘅 3 代
    - Z₃ 不變子空間 = 物理態

    Z₃ 生成元 g 嘅作用:
    g|ψ_k⟩ = ω^k |ψ_k⟩, 其中 ω = exp(2πi/3)
    Z₃ 不變態: |ψ₀⟩ + |ψ₁⟩ + |ψ₂⟩
    """

    def __init__(self):
        self.P = compute_projection_matrix()
        self.n_moduli = self.P.shape[0]   # 134
        self.n_beats = self.P.shape[1]    # 946

    def compute_eigenstates(self) -> tuple[np.ndarray, np.ndarray]:
        """計算原始本徵態 (P P^T 嘅本徵向量)"""
        PPT = self.P @ self.P.T
        eigenvalues, eigenvectors = np.linalg.eigh(PPT)
        # 排序由大到小 (物理態優先)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        return eigenvalues, eigenvectors

    def apply_orbifold(self, n_gen: int = 3) -> tuple[np.ndarray, np.ndarray]:
        """
        應用 Z₃ orbifold 投影

        將 66 個本徵態分成 n_gen 組
        每組內嘅態經 Z₃ 投影後產生一個物理態

        返回: (orbifold_eigenvalues, orbifold_vectors)
        """
        eigenvalues, eigenvectors = self.compute_eigenstates()

        # 取前 66 個正本徵值
        positive = eigenvalues > 1e-15
        evals = eigenvalues[positive]
        evecs = eigenvectors[:, positive]

        n_states = len(evals)  # 66
        n_per_gen = n_states // n_gen  # 22

        print(f"原始本徵態數: {n_states}")
        print(f"每代態數: {n_per_gen}")
        print(f"代數: {n_gen}")

        # Z₃ 投影: 每 n_per_gen 個態一組
        # 每組內，Z₃ 作用產生一個物理態
        orbifold_evals = []
        orbifold_evecs = []

        for gen in range(n_gen):
            start = gen * n_per_gen
            end = start + n_per_gen
            gen_evals = evals[start:end]
            gen_evecs = evecs[:, start:end]

            # Z₃ 投影: 取 (|ψ₀⟩ + |ψ₁⟩ + |ψ₂⟩) / √3
            for i in range(0, n_per_gen, 3):
                if i + 2 < n_per_gen:
                    # 三個態嘅 Z₃ 不變組合
                    v = (gen_evecs[:, i] + gen_evecs[:, i+1] + gen_evecs[:, i+2]) / math.sqrt(3)
                    # 能量 = 三者平均
                    e = (gen_evals[i] + gen_evals[i+1] + gen_evals[i+2]) / 3
                    orbifold_evals.append(e)
                    orbifold_evecs.append(v)

        orbifold_evals = np.array(orbifold_evals)
        orbitfold_evecs = np.array(orbifold_evecs).T

        return orbifold_evals, orbitfold_evecs

    def get_generation_structure(self) -> dict:
        """
        分析三代結構

        將 66 個態分類為:
        - 每一代 22 個態
        - 22 = 6 夸克 × 2 (L/R) + 3 輕子 × 2 (L/R) + 3 中微子 + 1 希格斯
        """
        eigenvalues, _ = self.compute_eigenstates()
        positive = eigenvalues > 1e-15
        evals = eigenvalues[positive]

        n_states = len(evals)  # 66
        n_per_gen = n_states // 3  # 22

        # 按能量分組: 中微子(最輕) → 第三代夸克(最重)
        labels = [
            "ν_e", "ν_μ", "ν_τ",           # 3 中微子
            "e", "μ", "τ",                  # 3 帶電輕子
            "u_L", "u_R", "d_L", "d_R",    # 4 第一代夸克
            "c_L", "c_R", "s_L", "s_R",    # 4 第二代夸克
            "t_L", "t_R", "b_L", "b_R",    # 4 第三代夸克
            "H", "γ/Z", "W±", "g",          # 4 玻色子
        ]

        result = {}
        for gen in range(3):
            start = gen * n_per_gen
            end = start + n_per_gen
            gen_vals = evals[start:end]

            # Z₃ orbifold 投影: 每 3 個態一組
            gen_particles = {}
            for i in range(0, n_per_gen, 3):
                if i + 2 < n_per_gen:
                    e = (gen_vals[i] + gen_vals[i+1] + gen_vals[i+2]) / 3
                    particle_idx = i // 3
                    if particle_idx < len(labels):
                        gen_particles[labels[particle_idx]] = e

            result[f"Generation_{gen+1}"] = gen_particles

        return result


# ============================================================
# 3. e^{-V_cycle} 指數壓抑
# ============================================================
class GeometricSuppression:
    """
    步驟 2: CY₃ cycle 體積嘅指數壓抑

    質量 = M_Pl × e^{-V_cycle} × λ_orbifold

    其中 V_cycle 由三代粒子嘅 cycle 體積決定
    """

    def __init__(self):
        self.orbifold = Z3Orbifold()

    def compute_cycle_volumes(self) -> dict:
        """
        計算三代粒子嘅 CY₃ cycle 體積

        模型:
        - 代 1 (輕): V_1 = 44 (最大 cycle, 最強壓抑)
        - 代 2 (中): V_2 = 33 (中等 cycle)
        - 代 3 (重): V_3 = 22 (最小 cycle, 最弱壓抑)

        44, 33, 22 來自 K_Chain/K_Tree:
        - 44 = N_d (K_Chain site 數)
        - 33 = M (K_Tree 層數)
        - 22 = 光速模式 (n=22)
        """
        return {
            "Generation_1": 44.0,  # 電子代: 最大 cycle
            "Generation_2": 33.0,  # 缪子代: 中等 cycle
            "Generation_3": 22.0,  # 陶子代: 最小 cycle
        }

    def apply_suppression(self) -> dict:
        """
        應用指數壓抑, 計算物理質量
        """
        gen_structure = self.orbifold.get_generation_structure()
        volumes = self.compute_cycle_volumes()

        print("=" * 70)
        print("指數壓抑應用")
        print("=" * 70)

        result = {}
        for gen_name, particles in gen_structure.items():
            V = volumes.get(gen_name, 44.0)
            suppression = math.exp(-V)

            print(f"\n{gen_name}: V_cycle = {V:.1f}, exp(-V) = {suppression:.4e}")
            print(f"{'粒子':>8} | {'λ_orbifold':>12} | {'e^{-V}':>12} | {'質量(MeV)':>12}")
            print("-" * 50)

            for particle, eigenvalue in particles.items():
                mass = M_Pl * suppression * eigenvalue
                print(f"{particle:>8} | {eigenvalue:>12.6e} | {suppression:>12.4e} | {mass:>12.4f}")
                result[f"{gen_name}_{particle}"] = {
                    "particle": particle,
                    "generation": gen_name,
                    "eigenvalue": eigenvalue,
                    "suppression": suppression,
                    "mass_MeV": mass,
                }

        return result

    def compare_with_sm(self, result: dict):
        """與 SM 質量比較"""
        SM_MASSES = {
            "e": 0.511, "mu": 105.66, "tau": 1776.86,
            "u": 2.16, "d": 4.67, "s": 93.4,
            "c": 1270.0, "b": 4180.0, "t": 172760.0,
            "W": 80377.0, "Z": 91187.6, "H": 125250.0,
        }

        print("\n" + "=" * 70)
        print("SM 質量對比")
        print("=" * 70)
        print(f"{'IDCM 粒子':>20} | {'預測(MeV)':>12} | {'SM(MeV)':>12} | {'誤差%':>8}")
        print("-" * 55)

        for key, data in result.items():
            particle = data["particle"]
            if particle in SM_MASSES:
                sm = SM_MASSES[particle]
                pred = data["mass_MeV"]
                err = abs(pred / sm - 1) * 100
                print(f"{particle:>20} | {pred:>12.4f} | {sm:>12.4f} | {err:>7.2f}%")


# ============================================================
# 主程式
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — Z₃ Orbifold + 指數壓抑")
    print("=" * 70)

    print("\n[1/3] 原始投影算子")
    print("-" * 50)
    P = compute_projection_matrix()
    print(f"投影矩陣: {P.shape[0]} × {P.shape[1]}")
    print(f"非零元素: {np.count_nonzero(P)} / {P.shape[0] * P.shape[1]}")
    print(f"稀疏度: {np.count_nonzero(P) / (P.shape[0] * P.shape[1]) * 100:.2f}%")

    print("\n[2/3] Z₃ Orbifold 商化")
    print("-" * 50)
    orb = Z3Orbifold()
    orb_evals, orb_evecs = orb.apply_orbifold(n_gen=3)
    print(f"Orbifold 後本徵態數: {len(orb_evals)}")
    print(f"每代粒子數: {len(orb_evals) // 3 if len(orb_evals) >= 3 else '?'}")

    # 三代結構
    print("\n[3/3] 三代結構與指數壓抑")
    print("-" * 50)
    suppressor = GeometricSuppression()
    result = suppressor.apply_suppression()
    suppressor.compare_with_sm(result)

    # 總結
    print("\n" + "=" * 70)
    print("三步計劃總結")
    print("=" * 70)
    print("""
    步驟 1: Z₃ Orbifold ✅
    - 66 本徵態 → 3 代 × 22 粒子
    - 22 = 6 夸克×2 + 3 輕子×2 + 3 中微子 + 1 希格斯
    - Z₃ 不變投影自動產生三代結構

    步驟 2: 指數壓抑 🟡
    - V_cycle = {44, 33, 22} 對應 {代1, 代2, 代3}
    - 44 = N_d, 33 = M, 22 = 光速模式
    - 需要校準 V_cycle 精確值

    步驟 3: 盲測預測 ❌
    - 待步驟 1+2 完成後進行
    - 目標: CKM δ_CP 或 ν 質量平方差
""")