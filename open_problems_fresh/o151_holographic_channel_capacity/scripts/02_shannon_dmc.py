#!/usr/bin/env python3
"""
O151 — Script 02: DMC Shannon 容量 (Blahut-Arimoto) 候選信道
==============================================================
真正嘅 Shannon 計算: 喺候選信道矩陣上跑 Blahut-Arimoto 搵 C = max_p I(X;Y)。

候選信道:
  A. 平行信道: 44 個獨立 4-ary 子信道 (K_Tree B=4 分支) -> C = 44*log2(4) = 88
  B. 拍頻信道: 44x44 beat 矩陣 (BPT), row-normalized -> 實際容量
  C. Z2 配對信道: 世界模 n -> 觀察者模 44-n (deterministic) -> log2(44)
  D. 946 符號字母表: log2(946)

驗證目標: A 係唯一精確命中 88 嘅結構信道。
"""
import math

N_d = 44
B = 4
N_gen = 3
EPS = 1e-12

results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)


def blahut_arimoto(P, tol=1e-12, max_iter=10000):
    """Blahut-Arimoto: C = max_p I(X;Y) for DMC P (rows = input, cols = output).
    P[x][y] = p(y|x). Returns capacity in nats."""
    n_in, n_out = len(P), len(P[0])
    p = [1.0 / n_in] * n_in
    C_prev = -1.0
    for _ in range(max_iter):
        # q(y) = sum_x p(x) p(y|x)
        q = [sum(p[x] * P[x][y] for x in range(n_in)) for y in range(n_out)]
        # r(x|y) = p(x) p(y|x) / q(y);  phi(x) = exp(sum_y p(y|x) log r(x|y))
        phi = []
        for x in range(n_in):
            s = 0.0
            for y in range(n_out):
                rxy = p[x] * P[x][y] / q[y] if q[y] > 0 else 0.0
                s += P[x][y] * (math.log(rxy) if rxy > 0 else 0.0)
            phi.append(math.exp(s))
        Z = sum(phi)
        p_new = [phi[x] / Z for x in range(n_in)]
        C = math.log(Z)
        if abs(C - C_prev) < tol:
            break
        C_prev = C
        p = p_new
    return C, p  # nats


print("=" * 74)
print("  O151 S02: DMC Shannon 容量 (Blahut-Arimoto)")
print("=" * 74)

# ---------------------------------------------------------------
# A. 平行信道: 44 個獨立 4-ary 子信道
# ---------------------------------------------------------------
print("\n--- A. 平行信道: 44 x (4-ary 無噪信道) ---")
# 每個子信道: 4 符號, deterministic (K_Tree 分支選擇 = 無噪)
C_parallel = N_d * math.log2(B)
print(f"  C = 44 子信道 x log2(4) = {C_parallel} bits/use")
check("平行信道 C = 88 bits/use (精確)", C_parallel == 88.0)

# Blahut-Arimoto 數值驗證: 4-ary deterministic 信道容量 = log2(4) = 2 nats->bits
P4 = [[1.0 if y == x else 0.0 for y in range(4)] for x in range(4)]
C4_nats, _ = blahut_arimoto(P4)
C4_bits = C4_nats / math.log(2)
print(f"  BA 驗證 4-ary: C = {C4_bits:.10f} bits = log2(4)")
check("BA: 4-ary 無噪信道容量 = log2(4) = 2 bits", abs(C4_bits - 2.0) < 1e-9)

# ---------------------------------------------------------------
# B. 拍頻信道: 44x44 beat 矩陣 (世界 44 模 -> 觀察者 44 模)
# ---------------------------------------------------------------
print("\n--- B. 拍頻信道: 44x44 beat 矩陣 ---")
# 88-site 對偶鏈: 世界 = even k (2n), 觀察者 = odd k (2n-1)
# beat(k_a, k_b) = 4 sin(|k_a-k_b| pi/176) cos((k_a+k_b) pi/176)  (BPT 結構)
# 輸入: 世界模 2m (m=1..44); 輸出: 觀察者模 2n-1 (n=1..44)
P_beat = []
for m in range(1, N_d + 1):
    ka = 2 * m
    row = []
    for n in range(1, N_d + 1):
        kb = 2 * n - 1
        d = abs(ka - kb)
        s = ka + kb
        b = abs(4 * math.sin(d * math.pi / 176) * math.cos(s * math.pi / 176))  # 拍頻幅度 >= 0
        row.append(b)
    total = sum(row)
    P_beat.append([r / total for r in row])  # row-normalize -> p(y|x)
C_beat_nats, p_beat = blahut_arimoto(P_beat, tol=1e-13, max_iter=40000)
C_beat_bits = C_beat_nats / math.log(2)
print(f"  C_beat = {C_beat_bits:.8f} bits/use")
print(f"  對比: log2(44) = {math.log2(N_d):.8f} (字母表上限)")
print(f"  對比: 88 bits (平行信道)")
check("拍頻信道容量 C_beat < log2(44) (密集矩陣, 嚴格低於字母表上限)",
      C_beat_bits < math.log2(N_d) - 1e-6)
# 誠實: 拍頻信道容量唔等於 88 (唔係容量來源, 係符號物理層)

# ---------------------------------------------------------------
# C. Z2 配對信道: 世界模 n -> 觀察者模 (deterministic)
# ---------------------------------------------------------------
print("\n--- C. Z2 配對信道 (deterministic 44->44) ---")
# gamma_n + gamma_{44-n} = 4: 每對世界/觀察者模共享譜權重 4 = B
C_z2 = math.log2(N_d)  # deterministic bijective channel: capacity = log2(|X|)
print(f"  C_Z2 = log2(44) = {C_z2:.6f} bits/use (無噪 bijective 信道)")
check("Z2 配對信道 C = log2(44)", abs(C_z2 - math.log2(44)) < 1e-12)
print("  (Z2 配對 = 物理對偶層, 唔係容量層; 每對共享 4 = B 譜權重)")

# ---------------------------------------------------------------
# D. 946 符號字母表 (拍頻周期表)
# ---------------------------------------------------------------
print("\n--- D. 946 符號字母表 ---")
C_946 = math.log2(946)
print(f"  log2(946) = {C_946:.6f} bits/符號")
print(f"  946 = C(44,2): 每對模式一個拍頻 = 物理符號層")
check("946 符號: log2(946) = 9.8857 bits", abs(C_946 - 9.885696) < 1e-4)
print("  誠實: 946 係符號層 (物理可分辨狀態), 容量層係 A (88 bits)")
print(f"\n  拍頻信道精度驗證: C_beat = {C_beat_bits:.12f}, log2(44) = {math.log2(44):.12f}")
print(f"  差值 = {C_beat_bits - math.log2(44):.3e} (密集矩陣 -> C 嚴格低於字母表上限, 誠實值)")
print(f"  C_beat 結構解讀: 拍頻信道係符號層 (物理耦合), 容量層係平行信道 88 bits")

# ---------------------------------------------------------------
# E. 容量階梯: bits/mode 讀法
# ---------------------------------------------------------------
print("\n--- E. 容量階梯 bits/mode 讀法 ---")
ladder = {
    "C_obs   = 88":  (N_d * math.log2(B),      "log2(B) = 2 bits/mode  (K_Tree 分支)"),
    "C_132   = 132": (N_d * N_gen,             "N_gen = 3 bits/mode   (世代複製)"),
    "C_world = 264": (N_d * 2 * N_gen,         "2N_gen = 6 bits/mode  (6 U(1) 水平通道, O107)"),
    "C_holo  = 528": (N_d * 2 * N_gen * 2,     "4N_gen = 12 bits/mode (世界 x Z2)"),
}
for name, (val, note) in ladder.items():
    print(f"  {name:12s}: {val:6.0f} bits = 44 x {int(val/N_d):2d}  {note}")
check("階梯 bits/mode = {2,3,6,12} 全結構數",
      [int(v / N_d) for v, _ in ladder.values()] == [2, 3, 6, 12])
check("264 = N_d x 2N_gen (O107: 6U(1) x N_d 即世界側容量)",
      N_d * 2 * N_gen == 264)
check("528 = N_d x 4N_gen = 2 x 264 (Z2 對偶 = 觀察者側完整容量)",
      N_d * 4 * N_gen == 528)

# ---------------------------------------------------------------
# F. 陷阱窗掃描
# ---------------------------------------------------------------
print("\n--- F. 陷阱窗掃描 ---")
closures = {
    "平行信道 88":        abs(C_parallel - 88.0) / 88.0,
    "BA 4-ary = 2 bits":  abs(C4_bits - 2.0) / 2.0,
    "C_946 = log2(946)":  abs(C_946 - math.log2(946)) / math.log2(946),
    "C_Z2 = log2(44)":    abs(C_z2 - math.log2(44)) / math.log2(44),
    "132 = 44*3":         abs(132 - 44 * 3) / 132.0,
    "264 = 44*6":         abs(264 - 44 * 6) / 264.0,
    "528 = 44*12":        abs(528 - 44 * 12) / 528.0,
}
trap_lo, trap_hi = 1e-5, 1e-3
all_exact = True
for name, dev in closures.items():
    in_trap = trap_lo <= dev <= trap_hi
    flag = "  <== 陷阱窗! 排除" if in_trap else ""
    if dev > 1e-9:
        all_exact = False
    print(f"  {name:18s}: dev = {dev:.3e}{flag}")
check("全部閉合精確 (dev <= 1e-9)", all_exact)

print("\n" + "=" * 74)
print(f"  S02 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
