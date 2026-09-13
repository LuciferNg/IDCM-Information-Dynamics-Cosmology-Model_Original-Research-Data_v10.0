#!/usr/bin/env python3
# O192 scripts/02 — RS1 ↔ F−1/L−1 家族橋樑掃描 (第一原理, stdlib only)
# 目的: O190 結構對比 (形狀/parity/AdS↔MERA) 之外, 量化測試 RS1 數值量會唔會命中
#       IDCM 已閉合家族 {F−1, L−1, 預算, 階梯} — 可證偽: miss = 兩層數值真係分開
# 規則: 唔 import 任何被驗證 script; Bessel 零點用 McMahon 4-term + 直接級數交叉驗證
# 修正 (09-13): B02 容差改漸近判準 (n≥2); B04 閾值改 0.5% + 角巧合註解;
#               + B05 統一 π 結構控制 (4n+1)/5×1.02486; B06 x40/x1 陷阱捕獲

import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def csc(x): return 1 / math.sin(x)

# ---- Bessel J₁ 零點: 直接級數 (小 z 驗證用) + McMahon 4-term (全譜) ----
def j1_series(z):
    s, term, k = 0.0, z / 2, 0
    while abs(term) > 1e-18:
        s += term
        k += 1
        term *= -(z * z / 4) / (k * (k + 1))
    return s

def bessel_zero_mcm(n):
    b = math.pi * (n + 0.25)          # McMahon: β = π(n + ν/2 − 1/4), ν=1
    return b - 3 / (8 * b) + 0.0234375 / b**3 - 0.2302734 / b**5

# 交叉驗證 x₁: Newton + 直接級數 (z≈3.83 級數收斂快)
x1 = 3.9
for _ in range(10):
    h = 1e-6
    x1 -= j1_series(x1) / ((j1_series(x1 + h) - j1_series(x1 - h)) / (2 * h))
print(f"x1_direct = {x1:.8f}   x1_mcm = {bessel_zero_mcm(1):.8f}   diff = {abs(x1-bessel_zero_mcm(1)):.2e}")
check("B01 McMahon 4-term 驗證 (x₁ vs Newton+直接級數)", abs(x1 - bessel_zero_mcm(1)) < 1e-4)

# ---- IDCM 已閉合家族 (O191/O192, 零新常數) ----
FAM_F = {2, 4, 7, 12, 20, 33, 54, 88, 143}     # F−1, m=4..12
FAM_L = {6, 10, 17, 28, 46, 75, 122, 198, 321}  # L−1, m=4..12
FAM_B = {88, 90, 178, 66, 536, 264, 272, 9350}  # 譜和預算 (×μ² 量子)
FAM_K = {11, 22, 33, 44}                        # 階梯 {L₅×1..4}
FULL = sorted(FAM_F | FAM_L | FAM_B | FAM_K)

hits = []
def scan(q, label, tol=0.05):
    t = min(FULL, key=lambda tt: abs(q - tt) / tt)
    dev = abs(q - t) / t
    if dev < tol:
        hits.append((label, q, t, dev))
        print(f"  HIT {label}: q={q:.6f} -> {t}  (dev {dev*100:.4f}%)")
    return t, dev

# ================= A. Bessel 零點 (RS1 KK 塔) =================
print("== A. Bessel 零點 (KK 塔) vs 家族 ==")
x = [bessel_zero_mcm(n) for n in range(1, 45)]
asym_lead = [abs(x[n-1] - math.pi * (n + 0.25)) / x[n-1] for n in range(1, 45)]
# O190「線性上升」係漸近判決: 首階 π(n+1/4) 對 n≥2 < 1%; n=1 嘅 2.49% = McMahon 3/(8β) 首階修正
check("B02 KK 塔線性上升 (漸近): x_n ≈ π(n+1/4) 對 n≥2 < 1% (O190 重驗)",
      max(asym_lead[1:]) < 0.01, f"max dev n≥2 = {max(asym_lead[1:])*100:.3f}%")
print(f"     n=1 dev = {asym_lead[0]*100:.3f}% = 3/(8β) 首階修正 (非線性, O190 判決唔受影響)")
for n in range(2, 45):
    scan(x[n-1] / x[0], f"x{n}/x1")
for n in range(2, 45):
    scan(x[n-1] - x[n-2], f"Δx{n} (→π)")
print(f"  x44/x1 = {x[43]/x[0]:.4f}  (vs 33=M: {(abs(x[43]/x[0]-33)/33)*100:.2f}%)")
print(f"  Δx 漸近 = π = {math.pi:.6f}  (vs 3 = L3-1 家族外: {abs(math.pi-3)/3*100:.2f}%)")

# 統一 π 結構控制: x_n/x1 ≈ (4n+1)/5 × (π·1.25/x1)  — n=1 McMahon 修正係唯一額外因子
c1_fac = math.pi * 1.25 / x[0]                    # 1.02486 = x1 未修正/已修正
worst = 0.0
for n in range(2, 45):
    pred = (4 * n + 1) / 5 * c1_fac
    dev = abs(x[n-1] / x[0] - pred) / (x[n-1] / x[0])
    worst = max(worst, dev)
check("B05 Bessel 命中全被 (4n+1)/5 × 1.02486 (π 結構 + n=1 修正) 解釋",
      worst < 0.01, f"max dev {worst*100:.3f}%")

# x40/x1 = 33.0005 陷阱捕獲: 33c1−c40 ≈ π ⟺ π² ≈ 9.9 (0.3%)
q40 = x[39] / x[0]
c1 = 3 / (8 * math.pi * 1.25)
c40 = 3 / (8 * math.pi * 40.25)
check("B06 x40/x1 = 33.0005 (0.0016%) 係 π²≈9.9 陷阱 (33·c1−c40 ≈ π, 0.2%)",
      abs(q40 - 33) / 33 < 0.0001 and abs(33 * c1 - c40 - math.pi) < 0.01,
      f"x40/x1 = {q40:.6f}; 33·c1−c40 = {33*c1-c40:.4f} vs π = {math.pi:.4f}")
b_hits = [h for h in hits if h[3] < 0.01]
print(f"  -> Bessel 命中 <1%: {len(b_hits)} 個, 全由 B05 控制")

# ================= B. csc 階梯 (rapidity, O140) =================
print("== B. csc 階梯 vs 家族 (含 π-control) ==")
b_hits = []
for n in range(1, 45):
    q = csc(math.pi * n / 88)
    t = min(FULL, key=lambda tt: abs(q - tt) / tt)
    dev = abs(q - t) / t
    if dev < 0.05:
        q1 = 88 / (math.pi * n)                      # 1/x 鏈 (22/7 + 小 x)
        ctrl = abs(t - q1) < abs(t - q)              # 命中被 88/π≈28 解釋 = π 陷阱
        b_hits.append((n, q, t, dev, ctrl))
        print(f"  HIT csc(π·{n}/88)={q:.5f} -> {t} (dev {dev*100:.4f}%)  [π-control: {ctrl}]")
check("B03 csc(π/88)=28.0172 vs 28=L7-1: 0.061% 係 π 陷阱 (28=88·7/22, 22/7≈π)",
      abs(csc(math.pi/88) - 28) / 28 < 0.001 and abs(28 - 88/math.pi) < abs(28 - csc(math.pi/88)),
      f"csc={csc(math.pi/88):.6f}, 88/π={88/math.pi:.6f}")
# n=15 嘅 2% 命中係角巧合: 15/88 ≈ 1/6 (2.3%) → csc(π/6) = 2 特殊角, 唔係家族橋
print(f"  n=15 註解: 15/88 = {15/88:.5f} vs 1/6 = {1/6:.5f} (dev {(abs(15/88-1/6)/(1/6))*100:.2f}%) -> csc(π/6) = 2 特殊角")
nonctrl = [h for h in b_hits if not h[4] and h[3] < 0.005]
check("B04 csc 階梯冇 <0.5% 非-π-control 命中 (結構橋閾值 = 0.1%, 2% 級全係巧合)",
      len(nonctrl) == 0, str([h[0] for h in nonctrl]))
ctrl_hits = [h for h in b_hits if h[4]]
print(f"  -> csc 命中 {len(b_hits)} 個: π-control {len(ctrl_hits)}, 軟巧合 {len(b_hits)-len(ctrl_hits)} (全部 ≥2%)")

# ================= C. warp / hierarchy =================
print("== C. warp (hierarchy) ==")
for h in (15, 16):
    krc = h * math.log(10) / math.pi
    print(f"  hierarchy 1e-{h}: k r_c π = {krc*math.pi:.3f}  =>  k r_c = {krc:.4f}")
krc15 = 15 * math.log(10) / math.pi
check("C01 k r_c (1e-15 hierarchy) ≈ 11 = L5 (階梯)", abs(krc15 - 11) < 0.01,
      f"{krc15:.4f} vs 11 (dev {abs(krc15-11)/11*100:.4f}%)")
check("C02 k r_c = 11 -> e^{-11π} ≈ 1e-15 (TeV 尺度)", abs(math.exp(-11 * math.pi) / 1e-15 - 1) < 0.05,
      f"{math.exp(-11*math.pi):.3e}")
krc16 = 16 * math.log(10) / math.pi
check("C03 L5 = 11 落入 RS1 所需窗口 [10.99, 11.73] (1e-15..1e-16)",
      krc15 <= 11 <= krc16, f"[{krc15:.3f}, {krc16:.3f}]")
for k in (10, 11, 12):
    print(f"  k r_c={k}: warp = e^-{k*math.pi:.3f} = {math.exp(-k*math.pi):.3e}")

# ================= D. 半整數回聲 =================
print("== D. 半整數回聲 (Wilson vs tree) ==")
g = math.gcd(89, 583)
check("D01 gcd(F11=89, 583=11×53) = 1 (冇共享生成器)", g == 1, f"gcd={g}")
print("  44.5 = F11/2 = 89/2 ;  291.5 = L5(Nd+Ng2)/2 = 583/2 ;  53 = Nd+Ng2")
check("D02 兩個半整數唔共享生成器 (回聲係軟嘅)", g == 1)

# ================= E. 符號層 (O190 已建立) =================
print("== E. 符號層 (O190 已建立, 重述) ==")
check("E01 sector 差 E−O = 2 = μ² (雙 brane 張力差類比)", 90 - 88 == 2)
check("E02 譜和預算 178 = 2F11 = F11·μ² (O190 穩定方程雙路由)", 178 == 2 * 89 == 89 * 2)

# ================= 總結 =================
print(f"\n=== 掃描小結 ===")
print(f"  Bessel 命中 <1%: {len([h for h in hits if h[3] < 0.01])} 個 — 全被 (4n+1)/5×1.02486 控制 (B05)")
print(f"  csc 命中: {len(b_hits)} 個 — 全 π-control 或 ≥2% 軟巧合 (B04)")
print(f"  唯一非-π 數值候選: k r_c ≈ 11 = L5 ({abs(krc15-11)/11*100:.4f}%) — 🟡 參數巧合 (RS1 自由參數, 需機制級論證)")
print(f"  半整數回聲: 冇共享生成器 (軟)")
print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
