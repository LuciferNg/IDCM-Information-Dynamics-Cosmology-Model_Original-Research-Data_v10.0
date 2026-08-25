"""
IDCM v10.0 — 選擇律 (Selection Rules)
======================================
從 K_Chain 拓撲推導量子數選擇律
"""

import math
from itertools import combinations

# ============================================================
# 基本常數
# ============================================================
φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
R_world = 4129.94
R_H = R_world  # deprecated alias (O73)
Nd = 44

# ============================================================
# K_Chain 拓撲結構
# ============================================================
class KChainTopology:
    """
    K_Chain 44-site 閉合環嘅拓撲性質
    """

    def __init__(self):
        self.Nd = 44
        self.modes = list(range(1, 45))

    # ---- Z₂ 對偶 ----
    def z2_dual(self, n: int) -> int:
        """Z₂ 對偶模式: n -> 44-n (當 n=44 時返回 44)"""
        if n == 44:
            return 44
        return self.Nd - n

    @property
    def z2_symmetric_modes(self) -> list[int]:
        """Z₂ 自對偶模式: n=22, n=44"""
        return [22, 44]

    @property
    def z2_paired_modes(self) -> list[tuple[int, int]]:
        """Z₂ 配對模式: (1,43), (2,42), ..."""
        return [(n, self.Nd - n) for n in range(1, 22)]

    # ---- 奇偶性 (Parity) ----
    def parity(self, n: int) -> int:
        """模式 parity: n 嘅奇偶"""
        return n % 2  # 0 = even, 1 = odd

    def parity_class(self, n: int) -> str:
        """parity 類別: even/odd"""
        return "even" if n % 2 == 0 else "odd"

    # ---- 四象限 (Quadrant) ----
    def quadrant(self, n: int) -> int:
        """
        模式喺環上嘅象限:
        1: n=1-11 (長波)
        2: n=12-22 (中波, 含光速模式)
        3: n=23-33 (短波)
        4: n=34-44 (近極限)
        """
        if 1 <= n <= 11:
            return 1
        elif 12 <= n <= 22:
            return 2
        elif 23 <= n <= 33:
            return 3
        else:
            return 4

    # ---- 群速度符號 ----
    def vg_sign(self, n: int) -> int:
        """群速度符號: n<22 正, n>22 負, n=22 零"""
        if n < 22:
            return 1
        elif n > 22:
            return -1
        return 0

    # ---- 能量帶 ----
    def energy_band(self, n: int) -> str:
        """
        能量帶分類:
        band I:  γ < 1 (n=1-14, 低能)
        band II: 1 ≤ γ < 2 (n=15-21, 中能)
        band III: 2 ≤ γ < 3 (n=22-28, 高能)
        band IV: 3 ≤ γ < 4 (n=29-43, 超高能)
        band V:  γ = 4 (n=44, 駐波極限)
        """
        gamma = 4 * math.sin(math.pi * n / 88) ** 2
        if gamma < 1:
            return "I"
        elif gamma < 2:
            return "II"
        elif gamma < 3:
            return "III"
        elif gamma < 4:
            return "IV"
        else:
            return "V"

    # ---- 量子數表 ----
    def quantum_numbers(self, n: int) -> dict:
        """模式 n 嘅完整量子數"""
        gamma = 4 * math.sin(math.pi * n / 88) ** 2
        return {
            "n": n,
            "Z₂ dual": self.z2_dual(n),
            "parity": self.parity_class(n),
            "quadrant": self.quadrant(n),
            "v_g sign": self.vg_sign(n),
            "energy band": self.energy_band(n),
            "γ": gamma,
            "v_g/c": math.cos(math.pi * n / 88)
        }


# ============================================================
# 選擇律 (Selection Rules)
# ============================================================
class SelectionRules:
    """
    K_Chain mode 之間嘅選擇律
    只有滿足以下條件嘅 beat 先係物理容許嘅
    """

    def __init__(self):
        self.topology = KChainTopology()

    def allowed_beat(self, n: int, m: int) -> tuple[bool, list[str]]:
        """
        檢查 beat (n,m) 是否物理容許
        返回 (allowed, reasons)
        """
        reasons = []
        allowed = True

        # Rule 1: Z₂ 共軛守恆
        # 如果 n 同 m 嘅 Z₂ 對偶相同，呢個係自相互作用，唔係物理 beat
        d_n = self.topology.z2_dual(n)
        d_m = self.topology.z2_dual(m)
        if n == d_m or m == d_n:
            reasons.append(f"Z₂ 共軛: n={n} 與 m={m} 互為對偶")
            # 呢個係允許嘅——Z₂ 對偶之間嘅 beat 產生 neutral 粒子
            reasons.append("  -> 中性粒子金色通道")
        else:
            reasons.append(f"Z₂ 非共軛: 帶電通道")

        # Rule 2: Parity 守恆
        # 只有相同 parity 嘅 mode 之間嘅 beat 係 allowed
        # (因為 K_Chain 波動方程係 parity-even)
        if self.topology.parity(n) == self.topology.parity(m):
            reasons.append("Parity 守恆 ✅")
        else:
            reasons.append("Parity 破缺 ❌")
            allowed = False

        # Rule 3: 象限躍遷選擇
        # 只有相鄰象限或同象限之間嘅 beat 係 allowed
        q_n = self.topology.quadrant(n)
        q_m = self.topology.quadrant(m)
        if abs(q_n - q_m) <= 1 or (q_n == 1 and q_m == 4) or (q_n == 4 and q_m == 1):
            reasons.append(f"象限躍遷: {q_n}->{q_m} 允許 ✅")
        else:
            reasons.append(f"象限躍遷: {q_n}->{q_m} 禁止 ❌")
            allowed = False

        # Rule 4: 能量帶選擇
        # 只有相近能量帶之間嘅躍遷係 allowed
        bands = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4}
        b_n = bands[self.topology.energy_band(n)]
        b_m = bands[self.topology.energy_band(m)]
        if abs(b_n - b_m) <= 1:
            reasons.append(f"能量帶躍遷: {abs(b_n - b_m)} 級 ✅")
        else:
            reasons.append(f"能量帶躍遷: {abs(b_n - b_m)} 級 ❌ (禁止)")
            allowed = False

        # Rule 5: 群速度守恆
        # 總群速度守恆: v_g(n) + v_g(m) 必須接近 0 或接近 c
        v_sum = abs(self.topology.vg_sign(n) + self.topology.vg_sign(m))
        if v_sum == 0:
            reasons.append("群速度: 反向傳播 (駐波) ✅")
        elif v_sum == 1:
            reasons.append("群速度: 單向傳播 ✅")
        else:
            reasons.append(f"群速度: 同向傳播 (v_sum={v_sum}) ⚠️")

        return allowed, reasons

    def allowed_beats(self) -> list[tuple[int, int, dict]]:
        """列出所有物理容許嘅 beat"""
        allowed = []
        for n in range(1, self.topology.Nd + 1):
            for m in range(n + 1, self.topology.Nd + 1):
                ok, reasons = self.allowed_beat(n, m)
                qn = self.topology.quantum_numbers(n)
                qm = self.topology.quantum_numbers(m)
                if ok:
                    allowed.append((n, m, {"n_qn": qn, "m_qn": qm, "reasons": reasons}))
        return allowed

    def print_allowed_summary(self):
        """打印選擇律摘要"""
        allowed = self.allowed_beats()
        total = 44 * 43 // 2

        print(f"總共 beat 數: {total}")
        print(f"選擇律允許: {len(allowed)}")
        print(f"選擇律禁止: {total - len(allowed)}")
        print(f"比例: {len(allowed)/total*100:.1f}%")
        print()

        # 按象限分類
        print("按象限分類:")
        quad_counts = {}
        for n, m, info in allowed:
            qn = info["n_qn"]["quadrant"]
            qm = info["m_qn"]["quadrant"]
            key = f"{qn}-{qm}"
            quad_counts[key] = quad_counts.get(key, 0) + 1
        for key, count in sorted(quad_counts.items()):
            print(f"  象限 {key}: {count}")

        print("\n按能量帶分類:")
        band_counts = {}
        for n, m, info in allowed:
            bn = info["n_qn"]["energy band"]
            bm = info["m_qn"]["energy band"]
            key = f"{bn}-{bm}"
            band_counts[key] = band_counts.get(key, 0) + 1
        for key, count in sorted(band_counts.items()):
            print(f"  帶 {key}: {count}")

        # 列出關鍵 beat
        print("\n關鍵 beat 嘅選擇律檢查:")
        key_beats = [(1, 2), (3, 22), (13, 14), (18, 20), (24, 25), (36, 44)]
        for n, m in key_beats:
            ok, reasons = self.allowed_beat(n, m)
            status = "✅" if ok else "❌"
            print(f"\n  Beat ({n:2d},{m:2d}) {status}:")
            for r in reasons:
                print(f"    {r}")


# ============================================================
# 主程式
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — K_Chain 選擇律分析")
    print("=" * 70)

    rules = SelectionRules()

    print("\n[1/3] K_Chain 拓撲量子數")
    print("-" * 50)
    topo = KChainTopology()
    print(f"{'n':>3} | {'Z₂':>3} | {'Parity':>6} | {'Quad':>4} | {'Band':>4} | {'v_g/c':>6} | {'γ':>6}")
    print("-" * 50)
    for n in range(1, 45):
        qn = topo.quantum_numbers(n)
        print(f"{n:3d} | {qn['Z₂ dual']:3d} | {qn['parity']:>6} | "
              f"{qn['quadrant']:4d} | {qn['energy band']:>4} | "
              f"{qn['v_g/c']:>6.3f} | {qn['γ']:>6.4f}")

    print("\n[2/3] 選擇律掃描")
    print("-" * 50)
    rules.print_allowed_summary()

    print("\n[3/3] 被選擇律過濾後嘅物理 beat")
    print("-" * 50)
    allowed = rules.allowed_beats()

    # 基本常數
    hbar = 6.582119569e-16
    c = 299792.458
    R_world = 4129.94
    R_H = R_world  # deprecated alias (O73)
    omega_scale = 88 * c * 1e3 / (R_world * 3.085677581e19 * 1e3)
    E_n = [hbar * omega_scale * math.sin(math.pi * n / 88) for n in range(1, 45)]

    # 過濾後嘅 SM 匹配

    # 檢查之前嘅關鍵 match 仲有冇效
    print("\n選擇律過濾後嘅關鍵匹配復查:")
    targets = {
        "m_tau/m_mu": 16.8170,
        "m_Z/m_W": 1.1345,
        "m_H/m_W": 0.6417,
        "m_u/m_e": 4.2270,
    }
    for name, target in targets.items():
        best_err = 999
        best_beat = None
        for n, m, info in allowed:
            r = abs(E_n[n-1] - E_n[m-1]) / E_n[0]
            err = abs(r / target - 1) * 100
            if err < best_err and err < 1.0:
                best_err = err
                best_beat = (n, m)
        if best_beat:
            print(f"  {name} = {target:.4f} -> beat {best_beat}, err={best_err:.4f}% ✅")
        else:
            print(f"  {name} = {target:.4f} -> 被選擇律排除 ❌")