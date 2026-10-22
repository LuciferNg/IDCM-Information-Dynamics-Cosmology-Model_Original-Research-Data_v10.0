#!/usr/bin/env python3
"""
O51 第三階段探索: 無理拍頻 → 龐加萊復歸 + 真實年齡 (探索版)
================================================================
問題: 宇宙(44-tone 準週期系統)究竟經歷過多少次龐加萊復歸? 真實年齡幾多?
框架: v10.0 非膨脹宇宙, 946 個拍頻全部無理比 → 永不精確循環

呢個 script 只做數值探索 — 輸出所有候選結構, 唔下結論
Run: /usr/bin/python3 scripts/03_poincare_explore.py
"""
import math, sys
sys.path.insert(0, '../../src')
from kchain_wave_params import R_H, c, Nd, H0, compute_modes

phi = (1 + math.sqrt(5)) / 2
Mpc_to_km = 3.085677581e19
Gyr_s = 3.15576e16
c_MpcGyr = c * Gyr_s / Mpc_to_km

t_ring = R_H / c_MpcGyr          # 13.470 Gyr
T_sync = 2 * math.pi * t_ring    # 84.635 Gyr
t_render = t_ring * Nd / (Nd - 1)  # 13.7833 Gyr

modes = compute_modes()
w = [m.omega for m in modes]        # rad/s (n=1..44)
f = [m.frequency for m in modes]    # 1/Gyr

print("=" * 72)
print("O51-3 探索: 無理拍頻 → 龐加萊復歸 + 真實年齡")
print("=" * 72)
print(f"t_ring  = {t_ring:.6f} Gyr (光繞環)")
print(f"T_sync  = {T_sync:.6f} Gyr (週期恢復)")
print(f"t_render= {t_render:.6f} Gyr (渲染深度, 已驗證)")

# ── 1. 946 拍頻統計 ──
beats = []  # (i, j, dw_rad_s, T_Gyr)
for i in range(44):
    for j in range(i + 1, 44):
        dw = w[j] - w[i]
        T = 2 * math.pi / dw / Gyr_s
        beats.append((i + 1, j + 1, dw, T))

T_vals = sorted(b[3] for b in beats)
T_min, T_max = T_vals[0], T_vals[-1]
T_mean = sum(T_vals) / len(T_vals)
# 諧波平均
T_harm = len(T_vals) / sum(1 / t for t in T_vals)
# 幾何平均
T_geo = math.exp(sum(math.log(t) for t in T_vals) / len(T_vals))

print("\n[1] 946 個拍頻周期 T_ij = 2π/(ω_i−ω_j) (Gyr)")
print(f"    min = {T_min:.4f}  (i,j={beats[T_vals.index(T_min)][0:2]})")
print(f"    max = {T_max:.4f}  (i,j={beats[T_vals.index(T_max)][0:2]})")
print(f"    mean= {T_mean:.4f}    harmonic={T_harm:.4f}    geo={T_geo:.4f}")
print(f"    max/min = {T_max/T_min:.4f}")
print(f"    max/T_sync = {T_max/T_sync:.6f}    max/t_render = {T_max/t_render:.6f}")
print(f"    mean/T_sync = {T_mean/T_sync:.6f}  harm/T_sync = {T_harm/T_sync:.6f}")

# ── 2. 每個 T_sync 嘅拍頻週期完成數 N(T) = Σ T/T_ij ──
def N_recur(T):
    return sum(T / b[3] for b in beats)

N_sync = N_recur(T_sync)
N_render = N_recur(t_render)
print("\n[2] 拍頻週期完成總數 (每時間 T 內所有 946 拍頻繞圈總次數)")
print(f"    N(T_sync)   = {N_sync:.6f}")
print(f"    N(t_render) = {N_render:.6f}")
print(f"    N_sync/946  = {N_sync/946:.6f}    N_sync/88 = {N_sync/88:.6f}    N_sync/44 = {N_sync/44:.6f}")
print(f"    N_sync/178  = {N_sync/178:.6f}    N_sync/90 = {N_sync/90:.6f}")

# ── 3. 每次 T_sync 嘅相位漂移 δ_n = frac(ω_n T_sync / 2π) = frac(88 sin(πn/88)) ──
deltas = []
for n in range(1, 45):
    x = 88 * math.sin(math.pi * n / 88)
    d = x - math.floor(x)
    deltas.append((n, x, d))
d_vals = [d for _, _, d in deltas]
print("\n[3] 每次 T_sync 嘅相位漂移 δ_n = frac(88·sin(πn/88))")
print(f"    n=44: δ={deltas[43][2]:.6f} (sin=1 → 88 整數週期 → 0 漂移)")
print(f"    max δ = {max(d_vals):.6f} (n={deltas[d_vals.index(max(d_vals))][0]})")
print(f"    min δ = {min(d_vals):.6f} (n={deltas[d_vals.index(min(d_vals))][0]})")
print(f"    mean δ = {sum(d_vals)/44:.6f}    Σδ = {sum(d_vals):.6f}")
print(f"    非零漂移模式數 = {sum(1 for d in d_vals if d > 1e-9)}")

# ── 4. 結構數 S = Σ(2n−45)sin(πn/88) (N_sync = 88·S 候選) ──
S = sum((2 * n - 45) * math.sin(math.pi * n / 88) for n in range(1, 45))
print("\n[4] S = Σ(2n−45)sin(πn/88)  → N_sync = 88·S ?")
print(f"    S = {S:.10f}")
print(f"    88·S = {88*S:.6f}  (vs N_sync = {N_sync:.6f})")

# ── 5. 相位漂移總和每次 T_sync 嘅「錯位量」──
# 總錯位 = Σ_ij δ_ij, δ_ij = frac(88(sin_i − sin_j)) (以 2π 計)
misalign = []
for i, j, dw, T in beats:
    x = 88 * (math.sin(math.pi * j / 88) - math.sin(math.pi * i / 88))
    d = x - math.floor(x)
    misalign.append(d)
print("\n[5] 每次 T_sync 嘅拍頻錯位 δ_ij = frac(88(sin_j − sin_i))")
print(f"    mean δ_ij = {sum(misalign)/len(misalign):.6f}    Σδ_ij = {sum(misalign):.6f}")
print(f"    Σδ_ij/946 = {sum(misalign)/946:.6f}")

# ── 6. 候選「真實年齡」──
print("\n[6] 候選真實年齡 (Gyr)")
cands = {
    "T_decohere = 2π/ω_min (所有拍頻完成首週期)": T_max,
    "T_sync (週期恢復)": T_sync,
    "t_render × 946 (拍頻數)": t_render * 946,
    "T_sync × 946": T_sync * 946,
    "T_sync × 88": T_sync * 88,
    "T_sync × 44": T_sync * 44,
    "T_sync × 43": T_sync * 43,
    "T_sync × 178": T_sync * 178,
    "T_sync / (88(1−cos(π/88))) [=T_decohere]": T_sync / (88 * (1 - math.cos(math.pi / 88))),
}
for name, val in cands.items():
    print(f"    {name:55s} = {val:14.4f}  (N_recur={N_recur(val):12.4f})")

# ── 7. 檢查「N_recur = 整數」嘅時間候選 ──
print("\n[7] 搵 N_recur(T) = 整數嘅 T (喺合理範圍)")
for target in [946, 88, 178, 44 * 44, 44 * 43, 946 * 2, 88 * 43, 43 * 44 * 2]:
    T_t = target / (sum(1 / b[3] for b in beats))
    print(f"    N_recur = {target:6d} → T = {T_t:14.4f} Gyr = {T_t/T_sync:8.4f}×T_sync = {T_t/t_render:8.4f}×t_render")

# ── 8. φ 結構檢查 ──
print("\n[8] φ 結構檢查")
print(f"    φ⁴+φ⁻⁴ = {phi**4 + phi**-4:.6f} (L4=7)   φ⁵+φ⁻⁵ = {phi**5 + phi**-5:.6f} (L5=11)")
print(f"    T_max/T_sync = {T_max/T_sync:.6f}    88(1−cos(π/88)) = {88*(1-math.cos(math.pi/88)):.10f}")
print(f"    φ⁻⁵ = {phi**-5:.6f}    1/(88(1−cos(π/88))) = {1/(88*(1-math.cos(math.pi/88))):.6f}")
print(f"    946/178 = {946/178:.6f}    946/90 = {946/90:.6f}    946/88 = {946/88:.6f}    946/44 = {946/44:.6f}")
print(f"    88·sin(π/88) = {88*math.sin(math.pi/88):.10f}  (≈π? {88*math.sin(math.pi/88)/math.pi:.8f})")
print(f"    t_render·44/43 = {t_render*44/43:.6f}  (=t_ring·(44/43)²)")
print(f"    t_render·43/44 = {t_render*43/44:.6f}  (=t_ring)")
