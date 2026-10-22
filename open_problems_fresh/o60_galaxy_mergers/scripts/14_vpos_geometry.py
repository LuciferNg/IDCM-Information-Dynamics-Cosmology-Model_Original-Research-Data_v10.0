#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60b 衛星系平面 (VPOS) — K_Chain 投影幾何 (Gemini 方案 B)
===========================================================
Gemini 建議: 本星系群 = 雙相空間節點, 檢查 K_Chain 相位投影
會唔會自然導出垂直於雙星連線嘅極小能量張量平面?

背景:
- MW 衛星 11/11 喺同一極化平面 (VPOS, Pawlowski+2012)
  VPOS 法向量: (l, b) = (188.5°, -13.5°) 銀河座標
- M31 衛星都有平面 (GPOA, Ibata+2013)
- ΛCDM 張力: 平面太薄 (RMS 厚度 ~20 kpc vs 半徑 ~200 kpc)
- IDCM: K_Chain 1D 環 → 3D 投影, 有冇自然平面?

關鍵想法:
1. K_Chain 44-site 環 → 3D 投影 (O57 cy3_projection_gen)
2. A₅ 冷斑節點 (60 節點) 已經有 3D 幾何
3. 本星系群 = MW+M31 雙核 → 連線定義一個軸
4. 衛星系分佈會唔會垂直於呢個軸?

數據: McConnachie 2012 本星系群衛星目錄
"""
import numpy as np

# VPOS 數據 (Pawlowski+2012)
# 法向量: l=188.5°, b=-13.5° → 極化平面嘅法線
# 平面本身: 大圓垂直於法向量
l_vpos = np.radians(188.5)
b_vpos = np.radians(-13.5)

# M31 方向 (銀河座標)
l_m31 = np.radians(121.17)
b_m31 = np.radians(-21.57)

# M31-MW 連線方向 (單位向量)
def gal_to_vec(l, b):
    return np.array([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)])

v_m31 = gal_to_vec(l_m31, b_m31)
v_vpos = gal_to_vec(l_vpos, b_vpos)

print("=" * 72)
print("O60b: VPOS vs M31-MW 連線幾何")
print("=" * 72)

# 1. VPOS 平面 vs M31 方向
angle = np.degrees(np.arccos(np.clip(np.dot(v_m31, v_vpos), -1, 1)))
print(f"[1] VPOS 法向量 vs M31-MW 連線:")
print(f"    VPOS 法向量 (l=188.5°, b=-13.5°)")
print(f"    M31 方向 (l=121.17°, b=-21.57°)")
print(f"    夾角 = {angle:.1f}°")
print(f"    → 如果 VPOS 垂直於 M31 連線: 夾角應 90°")
print(f"    → 實際 {angle:.1f}° — 偏差 {abs(angle-90):.1f}°")

# 2. VPOS 平面包含 M31 方向?
# 如果 M31 喺 VPOS 平面內: 法向量 ⊥ M31 → 夾角 90°
print(f"\n[2] M31 喺 VPOS 平面內?")
print(f"    夾角 = {angle:.1f}° vs 90° → 偏差 {abs(angle-90):.1f}°")
print(f"    → M31 唔喺 VPOS 平面內 (偏差 25°)")

# 3. VPOS vs 銀河盤
l_disk = np.radians(0)
b_disk = np.radians(0)
v_disk = gal_to_vec(l_disk, b_disk)  # 銀河盤法向量 (b=90°)
v_disk = np.array([0, 0, 1])  # 銀河盤法向量 = b=90°
angle_disk = np.degrees(np.arccos(np.clip(np.dot(v_vpos, v_disk), -1, 1)))
print(f"\n[3] VPOS 法向量 vs 銀河盤法向量:")
print(f"    夾角 = {angle_disk:.1f}°")
print(f"    → VPOS 同銀河盤夾角 {90-angle_disk:.1f}° (平面同盤傾角)")

# 4. K_Chain 投影假說
print(f"""
[4] K_Chain 投影假說:
    K_Chain 44-site 1D 環 → 3D 投影 (O57)
    投影數學: 1D 環嘅調和函數 e^(inθ) → 3D 球諧 Y_lm?
    如果投影用特定 l,m: 
      l=1 (偶極): 產生一個方向 → 對稱軸
      l=2 (四極): 產生一個平面 → 極化面!
    44-site 環嘅 44 個模式 → 44 個諧波
    n=2 模式 (SYNC): 最強 → l=2 四極 → 平面?
    
    具體: 如果衛星系分佈 = K_Chain n=2 模式投影
    → 平面法向量 = 投影軸
    → 本星系群: MW+M31 雙核 → 連線軸?
    → VPOS 法向量 vs M31 方向: {angle:.0f}° (唔垂直)
    → 但 VPOS 可能垂直於「本星系群角動量軸」而唔係 M31 連線?
    
    ⚠️ 需要 O57 投影數學先可以推導 — 目前係假說
""")

# 5. 定量: VPOS 厚度
print(f"[5] VPOS 觀測特性 (Pawlowski+2012):")
print(f"    RMS 高度 (垂直平面): ~20 kpc")
print(f"    衛星半徑: ~100-250 kpc")
print(f"    厚度/半徑比: 20/200 = 0.10 (薄面!)")
print(f"    ΛCDM 預測: 衛星各向同性 → 厚度 ~ 半徑 (比 1.0)")
print(f"    → IDCM 如果預測平面 → 需要厚度比 < 0.1")
print(f"    → 44-site 環投影嘅「量子化」厚度?")
print(f"    → 20 kpc / 200 kpc = 0.1 = 1/10")
print(f"    → 44/4.4 = 10? 冇直接結構")

# 6. 關鍵測試: 衛星角動量 vs VPOS
print(f"""
[6] 關鍵測試 (未來):
    Gaia DR3 proper motions → 衛星軌道角動量
    如果全部衛星共面同向旋轉 → 強 VPOS
    IDCM 預測: 平面 = K_Chain n=2 投影 → 法向量 = 固定軸
    ΛCDM 預測: 各向同性 + 偶爾瞬時平面
    判別: 平面嘅「持續性」(KPP) vs 瞬時對齊
    → TNG50 話 KPP 早期形成 (arXiv:2605.05972)
    → 如果 KPP 係「宇宙網拉格朗日體積變形」→ ΛCDM 有解釋
    → IDCM: K_Chain 投影天然產生固定平面? 需要推導
""")

print(f"\n結論: VPOS 係開放問題, 需要 O57 投影數學")
print(f"初步: VPOS 法向量 vs M31 方向夾角 {angle:.0f}° (唔垂直)")
print(f"→ 唔支持「垂直於 M31 連線」假說")
print(f"→ 但可能係本星系群角動量軸或其他投影軸")
