#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 散射 channel: kernel 對稱性數學驗證 (2026-10-17)
============================================================
理論問題 (record 19/20 拒證後): 觀測 Hα 唔對稱 (3/3)，但 Rusakov 電子散射
模型 fit 良好。散射 kernel 會唔會本身破壞對稱？定係保對稱？

定理候選:
  若 input 光譜 I(ν) 對稱 (繞 ν₀), kernel K 對稱 (繞 0), 則 output
  (I*K)(ν) 都對稱 — 純散射唔會破壞對稱。
  ⟹ 觀測嘅唔對稱必須來自非散射 channel (吸收/P-Cygni/bulk 流/幾何)。

驗證:
  A. 對稱 kernel (Thomson exp): 模態對雙峰 × exp kernel → 峰距/峰高比保持
  B. 非對稱 kernel (吸收): I × e^{-τ(λ)} → 峰高比偏離 1 (對稱破壞定量)
  C. f(τ) 定量: 峰高比 R = e^{-Δτ}, Δτ 由效率譜求
  D. 效率譜 (IDCM 已有結構): 線吸收只喺凝聚層 (hop) 有效 —
     藍峰 (blueshifted 發射) 通過更多凝聚層 → 更強吸收 → R < 1
     預言: 對稱破壞方向 = 藍峰弱 (紅峰強) — 同 A/C/G 觀測中點偏移方向比較!
"""
import numpy as np

C_KM = 2.99792458e5
print("="*76)
print("A. 定理: 對稱 kernel 卷積保對稱")
print("="*76)

# 模態對雙峰: ±418 km/s 對稱 (IDCM ℓ=3 n=5 半距), FWHM 100 km/s
def double_peak(v, vsep, vwid, ratio=1.0):
    """ratio = 峰2/峰1 高度比 (1 = 對稱)"""
    return (np.exp(-0.5*((v-vsep/2)/vwid)**2) + ratio*np.exp(-0.5*((v+vsep/2)/vwid)**2))

def thomson_kernel(v, ve):
    """電子散射 exp kernel: K ∝ exp(-|v|/ve) (Rusakov: exp tail)"""
    return np.exp(-np.abs(v)/ve)

v_grid = np.linspace(-3000, 3000, 60001)
dv = v_grid[1]-v_grid[0]
vp = 836.1  # IDCM ℓ=3 n=5 峰距 km/s
vw = 60.0   # 峰寬

I0 = double_peak(v_grid, vp, vw, ratio=1.0)
K_th = thomson_kernel(v_grid, v_e := 1000.0)
K_th /= K_th.sum()*dv   # normalize

# 卷積 (FFT)
I_conv = np.convolve(I0, K_th, mode='same')*dv

def measure(v_grid, I):
    """量峰距 + 峰高比 + 中點偏移 — 解析: 喺 ±vp/2 附近 ±100 km/s 窗內揾 local max"""
    vp = 836.1
    def peak_near(vc):
        m = (v_grid >= vc-80) & (v_grid <= vc+80)
        i = np.argmax(I[m])
        return v_grid[m][i], I[m][i]
    v1, f1 = peak_near(-vp/2)
    v2, f2 = peak_near(+vp/2)
    sep_meas = abs(v2-v1)
    ratio = min(f1, f2)/max(f1, f2)
    mid = (v1+v2)/2
    return sep_meas, ratio, mid

m0 = measure(v_grid, I0)
m1 = measure(v_grid, I_conv)
print(f"輸入模態對: 峰距={m0[0]:.1f} km/s, 峰高比={m0[1]:.4f}, 中點={m0[2]:+.1f}")
print(f"×Thomson kernel: 峰距={m1[0]:.1f} km/s, 峰高比={m1[1]:.4f}, 中點={m1[2]:+.1f}")
print(f"⟹ 峰距變化 {abs(m1[0]-m0[0])/m0[0]*100:.2f}% (寬 kernel 塗污, 兩線相同波長無關 → T1 ratio 穩健), 峰高比偏差 {abs(m1[1]-m0[1])*100:.4f}%")
chkA = abs(m1[1]-m0[1]) < 1e-3
print(f"[{'PASS' if chkA else 'FAIL'}] 對稱 kernel 保對稱 (峰高比不變; 峰距收縮係外觀效應)")
print("[INFO] Part A 峰距 836→757 收縮 9.4%: 對兩線同等 (Thomson 波長無關) ⟹ Δv(Hβ)/Δv(Hα) 比值判別唔受影響")

print("\n" + "="*76)
print("B. 非對稱 channel (吸收): 峰高比偏離 + 中點偏移")
print("="*76)
# 吸收因子: 藍峰更強衰減 (通過更多凝聚層) — exp(-τ·f(v))
def abs_factor(v, tau, asym=1.0):
    """藍側 (v<0) 吸收更強: τ_blue = tau·(1+asym), τ_red = tau·(1-asym)"""
    t = np.where(v < 0, tau*(1+asym), tau*(1-asym))
    return np.exp(-t)

for tau, asym in [(0.1, 1.0), (0.3, 1.0), (0.5, 1.0), (1.0, 1.0)]:
    I_abs = I0 * abs_factor(v_grid, tau, asym)
    m = measure(v_grid, I_abs)
    print(f"τ={tau:.1f}: 峰高比={m[1]:.4f} (偏差 {(1-m[1])*100:.1f}%), 中點偏移={m[2]:+.1f} km/s")

print("\n" + "="*76)
print("C. 對稱破壞方向 — IDCM 凝聚層 hop 結構預言")
print("="*76)
print("hop 階梯 [4,8,11,12,11,8,4,1] (record 11, sum=59):")
hop = np.array([4,8,11,12,11,8,4,1])
print(f"  Σhop = {hop.sum()}, B=4 hop 數 = {len(hop)}")
# 藍峰 = 發射體正面運動 → 喺介質內行徑更長 (向觀測者射來穿過凝聚層)
# 預言: Δτ_blue > Δτ_red ⟹ 藍峰弱 ⟹ 峰高比 R < 1 且中點向藍偏
# (紅峰 = 遠離側, 穿層少)
print("  預言: 藍峰更弱 (R<1), 強峰紅移 — 方向: 中點偏移 < 0 偏藍?")
print("  觀測 (record 19): A 中點偏移 -132/+198, C +92, G +521, G395H C_H -241")
print("  混合方向: 冇一致性 — 吸收唔係唯一 channel (要 bulk 流/幾何)")

print("\n" + "="*76)
print("D. 定量效率譜: hop 數 vs 峰高比")
print("="*76)
# 每 hop = 一層凝聚 — 對稱模態對兩峰通過層數差 ∝ hop 重心差
# 簡單模型: Δτ ∝ Σhop · (v_blue-v_red)/(2·v_scale)
v_scale = 3000.0
dtau_kms = 836.1/v_scale * 0.5  # 每 836 km/s 偏移光深差 0.5×τ_c
for tau_c in [0.3, 1.0, 2.0]:
    dtau = tau_c * dtau_kms
    R = np.exp(-dtau)
    print(f"τ_c={tau_c}: Δτ(836 km/s)={dtau:.3f} → 峰高比 R_e^{{-Δτ}} = {R:.3f} (藍弱)")

print("\n[INFO] 結論: 純 Thomson 散射保對稱; 觀測唔對稱 ⟹ 需要非散射 channel")
print("[INFO] 吸收模型預言藍弱 (方向固定); 觀測中點偏移無一致性 ⟹")
print("[INFO]   A/C/G 嘅唔對稱可能係 bulk outflow / 幾何遮蔽, 唔係純吸收")