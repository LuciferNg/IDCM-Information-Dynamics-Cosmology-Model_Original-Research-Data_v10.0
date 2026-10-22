#!/usr/bin/env python3
"""
O32-12: BTFR 深層分析 — IDCM 截距偏差來源
============================================
發現: IDCM 零參數 BTFR 預測截距 = 1.827, 數據 fit (斜率 4) = 1.675
偏差 -0.152 dex → IDCM 預測質量高 42%

分析:
1. Υ 假設敏感度: 官方 BTFR 用 Υ = 0.5 固定
2. 距離系統誤差
3. 樣本選擇
4. IDCM a₀ 修正候選: a₀_eff 需要幾大先 fit 到截距?
"""
import numpy as np
import json

c = 299792.458
R_H = 4129.94
H0_idcm = c / R_H
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
H0_s = H0_idcm / Mpc_to_km
G = 6.674e-11
Msun = 1.989e30

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10
A0_MOND = 1.2e-10
phi = (1 + np.sqrt(5)) / 2

# ============ 載入官方 BTFR ============
btfr = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            logMb = float(parts[4])
            elogMb = float(parts[5])
            logVf = float(parts[6])
            elogVf = float(parts[7])
            Fg = float(parts[8])
            btfr.append((name, logMb, elogMb, logVf, elogVf, Fg))
        except ValueError:
            continue

btfr = np.array(btfr, dtype=object)
logMb = btfr[:, 1].astype(float)
logVf = btfr[:, 3].astype(float)
Fg = btfr[:, 5].astype(float)
print(f"BTFR: {len(btfr)} 星系")
print(f"Gas fraction 範圍: {Fg.min():.2f} - {Fg.max():.2f} (median {np.median(Fg):.2f})")

# ============ 1. IDCM 預測截距 vs 數據 ============
print("\n=== 1. IDCM 零參數 BTFR ===")
intercept_idcm = 4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)
intercept_mond = 4*np.log10(1e3) - np.log10(G*A0_MOND) - np.log10(Msun)

# 數據 fit (斜率 4 固定)
logMb_fit4 = logMb - 4*logVf
intercept_data = np.mean(logMb_fit4)
print(f"數據截距 (斜率4): {intercept_data:.3f}")
print(f"IDCM 截距: {intercept_idcm:.3f} (偏差 {intercept_data-intercept_idcm:+.3f} dex)")
print(f"MOND 截距: {intercept_mond:.3f} (偏差 {intercept_data-intercept_mond:+.3f} dex)")

# IDCM 需要嘅 a₀
a0_need = 10**((4*np.log10(1e3) - np.log10(Msun) - intercept_data)/1) / G
print(f"要 fit 截距需要 a₀ = {a0_need:.4e}")
print(f"a₀_need/a₀_idcm = {a0_need/A0_IDCM:.4f}")

# ============ 2. Υ 敏感度 ============
print("\n=== 2. Υ 敏感度分析 ===")
# 官方 BTFR logMb 假設 Υ = 0.5
# 如果實際 Υ = 0.44 (我 fit 嘅 median): logMb 要 -log10(0.44/0.5) = -0.056
# 呢個只改 -0.056 dex, 唔夠 -0.152
ups_med = 0.44
delta_logMb_ups = np.log10(ups_med / 0.5)
print(f"Υ median {ups_med} vs 官方 0.5: ΔlogMb = {delta_logMb_ups:+.3f} dex")
print(f"→ 修正後數據截距: {intercept_data + delta_logMb_ups:.3f}")
print(f"→ IDCM 偏差: {intercept_data + delta_logMb_ups - intercept_idcm:+.3f} dex")

# ============ 3. 樣本: 按 gas fraction 分區 ============
print("\n=== 3. Gas fraction 分區分析 ===")
for label, mask in [("gas-rich (Fg>0.5)", Fg > 0.5),
                     ("gas-poor (Fg<0.2)", Fg < 0.2),
                     ("intermediate", (Fg >= 0.2) & (Fg <= 0.5))]:
    if mask.sum() == 0:
        continue
    lm = logMb[mask] - 4*logVf[mask]
    print(f"{label:<24}: N={mask.sum():>3}, 截距 = {np.mean(lm):.3f} ± {np.std(lm)/np.sqrt(mask.sum()):.3f}")

# ============ 4. IDCM 結構修正候選 ============
print("\n=== 4. IDCM a₀ 修正候選 ===")
print(f"a₀_idcm = {A0_IDCM:.4e}")
print(f"需要 a₀ = {a0_need:.4e} (fit BTFR 截距)")
ratio = a0_need / A0_IDCM
print(f"比例 = {ratio:.4f}")

# 候選: 1/(1-ε), 1/(1+ε), φ⁻¹, 2/π...
candidates = {
    "1/(1-ε)": 1/(1-1/phi/4),
    "1/(1+ε)": 1/(1+1/phi/4),
    "1/(1-2ε)": 1/(1-2/phi/4),
    "φ⁻¹·φ⁻¹·4": (1/phi)**2*4,
    "2/π": 2/np.pi,
    "√φ": np.sqrt(phi),
}
print(f"\n比例 = {ratio:.4f}")
for name, val in candidates.items():
    print(f"  {name:<14} = {val:.4f} (差 {(val-ratio)/ratio*100:+.1f}%)")

# ============ 5. 用 fit 嘅 Υ 重新算 BTFR (SPARC mass models) ============
print("\n=== 5. SPARC 樣本 BTFR (用我 fit 嘅 Υ) ===")
# 從之前 fit 載入
try:
    with open('data/global_joint_fit.json') as f:
        jf = json.load(f)
    ups_idcm = jf['ups_idcm']

    sample = {}
    with open('data/SPARC_Lelli2016c.mrt') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 17:
                continue
            name = parts[0]
            if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
                continue
            try:
                L36 = float(parts[7])
                MHI = float(parts[13])
                Vflat = float(parts[15])
            except (ValueError, IndexError):
                continue
            sample[name] = {'L36': L36, 'MHI': MHI, 'Vflat': Vflat}

    pts = []
    for name in sample:
        if name not in ups_idcm:
            continue
        Mb = ups_idcm[name] * sample[name]['L36'] + 1.33 * sample[name]['MHI']
        Vf = sample[name]['Vflat']
        if Vf > 10 and Mb > 0:
            pts.append((np.log10(Mb), np.log10(Vf)))
    pts = np.array(pts)
    print(f"SPARC BTFR 樣本: {len(pts)}")
    lm = pts[:, 0] - 4*pts[:, 1]
    print(f"截距 (斜率4): {np.mean(lm):.3f} ± {np.std(lm)/np.sqrt(len(pts)):.3f}")
    print(f"IDCM 截距: {intercept_idcm:.3f}")
    print(f"偏差: {np.mean(lm) - intercept_idcm:+.3f} dex")
except FileNotFoundError:
    print("(global_joint_fit.json 未找到, 跳過)")

# ============ 保存 ============
with open('data/btfr_deep.json', 'w') as f:
    json.dump({
        'intercept_data_slope4': float(intercept_data),
        'intercept_idcm': float(intercept_idcm),
        'intercept_mond': float(intercept_mond),
        'delta_idcm': float(intercept_data - intercept_idcm),
        'delta_mond': float(intercept_data - intercept_mond),
        'a0_needed': float(a0_need),
        'a0_idcm': float(A0_IDCM),
        'ups_correction': float(delta_logMb_ups)
    }, f, indent=2)
print("\n結果已存: data/btfr_deep.json")
