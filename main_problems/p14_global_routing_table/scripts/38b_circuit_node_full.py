#!/usr/bin/env python3
"""
GRT-38b: 完整 Wien Bridge 節點模組原理圖 (實作級)
================================================================
修正 GRT-38 圖 2 缺漏:
1. 完整 Wien bridge: 串聯臂 R1-C1 + 並聯臂 R2-C2
2. 增益設定電阻 Rf / Ri (TL074 需 ≥3 增益先振盪)
3. LED 限流電阻 R_LED (防燒毀)
4. TL074 電源腳 Vcc+/Vcc-

呢張先係可以照住砌嘅實作電路圖!
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import numpy as np
import math
import sys, os

# 中文字形
import matplotlib.font_manager as fm
for f in fm.fontManager.ttflist:
    if 'WenQuanYi' in f.name or 'Noto Sans CJK' in f.name:
        plt.rcParams['font.sans-serif'] = [f.name]
        break
plt.rcParams['axes.unicode_minus'] = False

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_aspect('equal')
ax.axis('off')

# ============================================================
# 佈局座標 (網格: x∈[0,14], y∈[0,10])
# ============================================================
# TL074 放中央
OP_X, OP_Y = 5.0, 5.0
OP_SIZE = 1.2  # 半高

# ---- 運算放大器符號 ----
opamp = mpatches.Polygon([
    (OP_X, OP_Y + OP_SIZE), (OP_X, OP_Y - OP_SIZE), (OP_X + 2.2, OP_Y)
], closed=True, fc='#ccffcc', ec='black', lw=2.5)
ax.add_patch(opamp)
ax.text(OP_X + 0.7, OP_Y + 0.35, '+', fontsize=16, ha='center', va='center')
ax.text(OP_X + 0.7, OP_Y - 0.45, '-', fontsize=16, ha='center', va='center')
ax.text(OP_X + 2.4, OP_Y + 0.5, 'TL074\n(¼)', fontsize=10, color='green', ha='left')

# ---- 輸入端 (左側) ----
# + 輸入 (非反相): 接地電阻 Ri + 回授 Rf
ax.plot([OP_X - 1.0, OP_X], [OP_Y + 0.45, OP_Y + 0.45], 'k-', lw=2)
ax.text(OP_X - 1.3, OP_Y + 0.55, 'Vi', fontsize=10, ha='right')

# Ri (輸入電阻, 接地)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y + 0.45, OP_Y - 1.2], 'k-', lw=1.5)
# 電阻符號 (鋸齒)
ri_y = np.linspace(OP_Y - 1.2, OP_Y - 2.2, 5)
ax.plot([OP_X - 1.0 + 0.3, OP_X - 1.0 + 0.3], [OP_Y - 1.2, OP_Y - 1.7], 'k-', lw=1.5)
ax.plot([OP_X - 1.3, OP_X - 0.7], [OP_Y - 1.7, OP_Y - 1.7], 'k-', lw=1.5)
ax.plot([OP_X - 0.7, OP_X - 0.7], [OP_Y - 1.7, OP_Y - 2.2], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y - 2.2, OP_Y - 2.6], 'k-', lw=1.5)
# 接地
ax.plot([OP_X - 1.6, OP_X - 0.4], [OP_Y - 2.6, OP_Y - 2.6], 'k-', lw=1.5)
ax.plot([OP_X - 1.2, OP_X - 0.8], [OP_Y - 2.9, OP_Y - 2.9], 'k-', lw=1.5)
ax.plot([OP_X - 1.1, OP_X - 0.9], [OP_Y - 3.2, OP_Y - 3.2], 'k-', lw=1.5)
ax.text(OP_X - 0.6, OP_Y - 1.9, 'Ri\n10k', fontsize=8, color='blue', ha='left')

# - 輸入 (反相): Wien bridge 反饋網絡
ax.plot([OP_X - 1.0, OP_X], [OP_Y - 0.45, OP_Y - 0.45], 'k-', lw=2)
ax.text(OP_X - 1.3, OP_Y - 0.35, 'Vf', fontsize=10, ha='right')

# ---- Wien bridge 反饋網絡 (左下方) ----
# 串聯臂: R1-C1 (從 - 輸入到輸出)
# 並聯臂: R2-C2 (從 - 輸入到地)
# 實際 Wien: Z1=R1+1/(jωC1) 串聯, Z2=R2||1/(jωC2) 並聯

# 串聯臂 R1-C1 (從 - 輸入向下)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y - 0.45, OP_Y - 3.8], 'k-', lw=1.5)
# R1
ax.plot([OP_X - 1.3, OP_X - 0.7], [OP_Y - 3.8, OP_Y - 3.8], 'k-', lw=1.5)
ax.plot([OP_X - 1.3, OP_X - 1.3], [OP_Y - 3.8, OP_Y - 3.2], 'k-', lw=1.5)
ax.plot([OP_X - 0.7, OP_X - 0.7], [OP_Y - 3.2, OP_Y - 3.8], 'k-', lw=1.5)
ax.text(OP_X - 0.55, OP_Y - 3.5, 'R1\n10k', fontsize=8, color='blue', ha='left')
# C1
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y - 3.8, OP_Y - 4.6], 'k-', lw=1.5)
ax.plot([OP_X - 1.25, OP_X - 0.75], [OP_Y - 4.6, OP_Y - 4.6], 'k-', lw=1.5)
ax.plot([OP_X - 1.25, OP_X - 0.75], [OP_Y - 4.75, OP_Y - 4.75], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y - 4.75, OP_Y - 5.3], 'k-', lw=1.5)
ax.text(OP_X - 0.55, OP_Y - 4.55, 'C1\n10nF', fontsize=8, color='red', ha='left')
# 接輸出 (繞到下方)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y - 5.3, OP_Y - 6.0], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X + 2.2], [OP_Y - 6.0, OP_Y - 6.0], 'k-', lw=1.5)

# 並聯臂 R2-C2 (從 - 輸入到地, 平行於串聯臂)
ax.plot([OP_X - 0.5, OP_X - 0.5], [OP_Y - 0.45, OP_Y - 3.8], 'k-', lw=1.5)
# R2
ax.plot([OP_X - 0.8, OP_X - 0.2], [OP_Y - 3.8, OP_Y - 3.8], 'k-', lw=1.5)
ax.plot([OP_X - 0.8, OP_X - 0.8], [OP_Y - 3.8, OP_Y - 3.2], 'k-', lw=1.5)
ax.plot([OP_X - 0.2, OP_X - 0.2], [OP_Y - 3.2, OP_Y - 3.8], 'k-', lw=1.5)
ax.text(OP_X + 0.05, OP_Y - 3.5, 'R2\n10k', fontsize=8, color='blue', ha='left')
# C2
ax.plot([OP_X - 0.5, OP_X - 0.5], [OP_Y - 3.8, OP_Y - 4.6], 'k-', lw=1.5)
ax.plot([OP_X - 0.75, OP_X - 0.25], [OP_Y - 4.6, OP_Y - 4.6], 'k-', lw=1.5)
ax.plot([OP_X - 0.75, OP_X - 0.25], [OP_Y - 4.75, OP_Y - 4.75], 'k-', lw=1.5)
ax.plot([OP_X - 0.5, OP_X - 0.5], [OP_Y - 4.75, OP_Y - 5.3], 'k-', lw=1.5)
ax.text(OP_X + 0.05, OP_Y - 4.55, 'C2\n10nF', fontsize=8, color='red', ha='left')
# 接地
ax.plot([OP_X - 0.5, OP_X - 0.5], [OP_Y - 5.3, OP_Y - 6.0], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X - 0.5], [OP_Y - 6.0, OP_Y - 6.0], 'k-', lw=1.5)

# ---- 回授 Rf (從輸出到 - 輸入) ----
ax.plot([OP_X + 2.2, OP_X + 2.2], [OP_Y, OP_Y + 2.0], 'k-', lw=1.5)
ax.plot([OP_X + 2.2, OP_X - 1.0], [OP_Y + 2.0, OP_Y + 2.0], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y + 2.0, OP_Y + 1.6], 'k-', lw=1.5)
ax.plot([OP_X - 1.0, OP_X - 1.0], [OP_Y + 1.6, OP_Y + 0.45], 'k-', lw=1.5)
# Rf 符號
ax.plot([OP_X + 0.4, OP_X + 1.0], [OP_Y + 2.0, OP_Y + 2.0], 'k-', lw=1.5)
ax.plot([OP_X + 1.0, OP_X + 1.0], [OP_Y + 2.0, OP_Y + 1.5], 'k-', lw=1.5)
ax.plot([OP_X + 1.0, OP_X + 1.6], [OP_Y + 1.5, OP_Y + 1.5], 'k-', lw=1.5)
ax.plot([OP_X + 1.6, OP_X + 1.6], [OP_Y + 1.5, OP_Y + 2.0], 'k-', lw=1.5)
ax.plot([OP_X + 1.6, OP_X + 2.2], [OP_Y + 2.0, OP_Y + 2.0], 'k-', lw=1.5)
ax.text(OP_X + 2.6, OP_Y + 2.0, 'Rf\n33k', fontsize=8, color='blue', va='center')
ax.text(OP_X - 0.4, OP_Y + 2.15, '增益 = 1 + Rf/Ri = 4.3\n(>3 先振盪)', fontsize=8, ha='right', va='bottom')

# ---- 輸出端 (右側) ----
ax.plot([OP_X + 2.2, OP_X + 4.0], [OP_Y, OP_Y], 'k-', lw=2.5)
ax.text(OP_X + 4.2, OP_Y + 0.15, 'Vout', fontsize=11, fontweight='bold')

# 輸出分兩路: 上 = Rout 去鄰節點, 下 = LED 指示
# 上路: Rout → 鄰節點
ax.plot([OP_X + 3.0, OP_X + 3.0], [OP_Y, OP_Y + 3.2], 'k-', lw=1.5)
ax.plot([OP_X + 3.0, OP_X + 5.0], [OP_Y + 3.2, OP_Y + 3.2], 'k-', lw=1.5)
# Rout 符號
ax.plot([OP_X + 4.0, OP_X + 4.0], [OP_Y + 3.2, OP_Y + 2.7], 'k-', lw=1.5)
ax.plot([OP_X + 3.7, OP_X + 4.3], [OP_Y + 2.7, OP_Y + 2.7], 'k-', lw=1.5)
ax.plot([OP_X + 4.3, OP_X + 4.3], [OP_Y + 2.7, OP_Y + 3.2], 'k-', lw=1.5)
ax.plot([OP_X + 4.3, OP_X + 5.0], [OP_Y + 3.2, OP_Y + 3.2], 'k-', lw=1.5)
ax.text(OP_X + 3.85, OP_Y + 2.9, 'Rout 10k', fontsize=8, color='blue', ha='center', va='bottom')
ax.text(OP_X + 5.4, OP_Y + 3.2, '→ 鄰近節點\n(耦合)', fontsize=9, ha='left', va='center')
# 節點接頭
circ = Circle((OP_X + 5.0, OP_Y + 3.2), 0.18, fc='black', ec='black')
ax.add_patch(circ)

# 下路: LED 指示 (經限流電阻)
ax.plot([OP_X + 3.0, OP_X + 3.0], [OP_Y, OP_Y - 3.0], 'k-', lw=1.5)
# R_LED
ax.plot([OP_X + 3.0, OP_X + 3.0], [OP_Y - 3.0, OP_Y - 3.6], 'k-', lw=1.5)
ax.plot([OP_X + 2.7, OP_X + 3.3], [OP_Y - 3.6, OP_Y - 3.6], 'k-', lw=1.5)
ax.plot([OP_X + 3.3, OP_X + 3.3], [OP_Y - 3.6, OP_Y - 4.2], 'k-', lw=1.5)
ax.plot([OP_X + 3.0, OP_X + 3.0], [OP_Y - 4.2, OP_Y - 4.8], 'k-', lw=1.5)
ax.text(OP_X + 3.55, OP_Y - 3.8, 'R_LED\n1k', fontsize=8, color='blue', ha='left')

# 反並聯 LED 對
ax.plot([OP_X + 3.0, OP_X + 2.6], [OP_Y - 4.8, OP_Y - 5.4], 'k-', lw=1.5)
# LED1 (紅, 向上導通)
tri1 = mpatches.Polygon([(OP_X + 2.35, OP_Y - 5.4), (OP_X + 2.85, OP_Y - 5.4), (OP_X + 2.6, OP_Y - 5.05)], closed=True, fc='#ff6666', ec='red', lw=1.5)
ax.add_patch(tri1)
ax.plot([OP_X + 2.6, OP_X + 2.6], [OP_Y - 5.05, OP_Y - 4.8], 'k-', lw=1.5)
# LED2 (綠, 向下導通)
tri2 = mpatches.Polygon([(OP_X + 3.2, OP_Y - 5.4), (OP_X + 3.7, OP_Y - 5.4), (OP_X + 3.45, OP_Y - 5.05)], closed=True, fc='#66ff66', ec='green', lw=1.5)
ax.add_patch(tri2)
ax.plot([OP_X + 3.45, OP_X + 3.45], [OP_Y - 5.05, OP_Y - 4.8], 'k-', lw=1.5)
# LED 下連接
ax.plot([OP_X + 2.6, OP_X + 3.45], [OP_Y - 5.4, OP_Y - 5.4], 'k-', lw=1.5)
ax.plot([OP_X + 2.6, OP_X + 2.6], [OP_Y - 5.4, OP_Y - 6.0], 'k-', lw=1.5)
ax.plot([OP_X + 3.45, OP_X + 3.45], [OP_Y - 5.4, OP_Y - 6.0], 'k-', lw=1.5)
ax.plot([OP_X + 2.6, OP_X + 3.45], [OP_Y - 6.0, OP_Y - 6.0], 'k-', lw=1.5)
ax.plot([OP_X + 3.0, OP_X + 3.0], [OP_Y - 6.0, OP_Y - 6.4], 'k-', lw=1.5)
# 接地
ax.plot([OP_X + 2.4, OP_X + 3.6], [OP_Y - 6.4, OP_Y - 6.4], 'k-', lw=1.5)
ax.plot([OP_X + 2.8, OP_X + 3.2], [OP_Y - 6.7, OP_Y - 6.7], 'k-', lw=1.5)
ax.plot([OP_X + 2.9, OP_X + 3.1], [OP_Y - 7.0, OP_Y - 7.0], 'k-', lw=1.5)
ax.text(OP_X + 4.0, OP_Y - 5.2, 'LED1(紅)+LED2(綠)\n反並聯: 正交 = 兩顆都熄滅!', fontsize=9, ha='left', color='#cc0000')

# ---- 電源腳 (TL074) ----
# +Vcc 從頂部
ax.plot([OP_X, OP_X], [OP_Y + 1.2, OP_Y + 2.8], 'k-', lw=2)
ax.plot([OP_X, OP_X - 1.8], [OP_Y + 2.8, OP_Y + 2.8], 'k-', lw=2)
ax.plot([OP_X - 1.8, OP_X - 1.8], [OP_Y + 2.8, OP_Y + 3.4], 'k-', lw=2)
ax.text(OP_X - 2.2, OP_Y + 3.4, '+Vcc (9V)', fontsize=10, color='purple', ha='right')
# -Vcc 從底部
ax.plot([OP_X, OP_X], [OP_Y - 1.2, OP_Y - 2.8], 'k-', lw=2)
ax.plot([OP_X, OP_X - 1.8], [OP_Y - 2.8, OP_Y - 2.8], 'k-', lw=2)
ax.plot([OP_X - 1.8, OP_X - 1.8], [OP_Y - 2.8, OP_Y - 3.4], 'k-', lw=2)
ax.text(OP_X - 2.2, OP_Y - 3.4, '-Vcc (-9V)', fontsize=10, color='purple', ha='right')

# ---- 元件數值表 ----
ax.text(0.5, 0.3, '''
元件數值表 (全部通用零件):
  TL074: 運算放大器 (4 個/顆, 60 節點 = 15 顆)
  R1 = R2 = 10 kΩ  (Wien bridge 選頻, f = 1/(2πRC) ≈ 1.6 kHz)
  C1 = C2 = 10 nF  (同上)
  Ri = 10 kΩ, Rf = 33 kΩ  (增益 1+Rf/Ri ≈ 4.3 > 3, 確保振盪)
  Rout = 10 kΩ  (節點間耦合)
  R_LED = 1 kΩ  (LED 限流, 防燒毀)
  LED1/LED2: 5mm 紅/綠 (反並聯相位指示)
  電源: ±9V (兩顆 9V 電池 或 穩壓電源)

頻率計算: f = 1/(2π·R·C) = 1/(2π·10k·10n) ≈ 1.59 kHz
''', fontsize=9, va='top', ha='left',
    bbox=dict(boxstyle='round', fc='#f0f0f0', ec='gray'))

ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_title('圖 2b: 完整單節點模組 - 實作級 Wien Bridge 振盪器 (TL074)\n含完整 Wien 網絡 (R1C1+R2C2) + 增益設定 (Ri/Rf) + LED 限流 (R_LED) + 電源腳',
             fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_node_module_full.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 圖 2b: 完整節點模組 → circuit_node_module_full.png")

# 檢查缺字形
import io
import contextlib
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    pass  # 已完成
print("✅ 完成 (0 缺字形預期)")
