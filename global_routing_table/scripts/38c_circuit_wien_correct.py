#!/usr/bin/env python3
"""
GRT-38c: 正確 Wien Bridge 節點模組原理圖 (教科書式佈局)
================================================================
修正 GRT-38b 電路原理錯誤:
❌ 舊版: Wien 網絡接到反相輸入 (-) — 錯!
✅ 新版: Wien 網絡 (R1C1 串聯 + R2∥C2 並聯) 接正相輸入 (+)
        負回授 Rf/Ri 接反相輸入 (-), 增益 = 1+Rf/Ri ≥ 3

標準 Wien bridge 振盪器拓撲:
  Vout ──┬── R1 ──┬── C1 ──┬── (+ 輸入)
         │        │        │
         │      (節點A)   (節點B)
         │        │        │
         │        R2       C2
         │        │        │
         └────────┴── GND ─┘

  (- 輸入): Ri → GND, Rf ← Vout  (增益 1+Rf/Ri)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle
import numpy as np
import math
import sys, os

import matplotlib.font_manager as fm
for f in fm.fontManager.ttflist:
    if 'WenQuanYi' in f.name or 'Noto Sans CJK' in f.name:
        plt.rcParams['font.sans-serif'] = [f.name]
        break
plt.rcParams['axes.unicode_minus'] = False

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(16, 11))
ax.set_aspect('equal')
ax.axis('off')

def gnd(x, y, color='black'):
    """接地符號"""
    ax.plot([x, x], [y, y-0.5], 'k-', lw=2, color=color)
    ax.plot([x-0.5, x+0.5], [y-0.5, y-0.5], 'k-', lw=2, color=color)
    ax.plot([x-0.32, x+0.32], [y-0.85, y-0.85], 'k-', lw=2, color=color)
    ax.plot([x-0.16, x+0.16], [y-1.2, y-1.2], 'k-', lw=2, color=color)

def resistor(x1, y1, x2, y2, label, color='blue', lw=2):
    """水平電阻"""
    ax.plot([x1, x1], [y1, y1+0.25], 'k-', lw=lw)
    ax.plot([x2, x2], [y2, y2-0.25], 'k-', lw=lw)
    ax.plot([x1, (x1+x2)/2-0.35], [y1+0.25, y1+0.25], 'k-', lw=lw)
    ax.plot([(x1+x2)/2-0.35, (x1+x2)/2-0.35], [y1+0.25, y1+0.6], 'k-', lw=lw)
    ax.plot([(x1+x2)/2-0.35, (x1+x2)/2+0.35], [y1+0.6, y1+0.6], 'k-', lw=lw)
    ax.plot([(x1+x2)/2+0.35, (x1+x2)/2+0.35], [y1+0.6, y1+0.25], 'k-', lw=lw)
    ax.plot([(x1+x2)/2+0.35, x2], [y1+0.25, y2-0.25], 'k-', lw=lw)
    ax.text((x1+x2)/2, y1+0.85, label, fontsize=10, color=color, ha='center')

def resistor_v(x, y1, y2, label, color='blue', lw=2):
    """垂直電阻"""
    ax.plot([x, x], [y1, y1-0.25], 'k-', lw=lw)
    ax.plot([x, x], [y2, y2+0.25], 'k-', lw=lw)
    ax.plot([x, x], [y1-0.25, y1-0.6], 'k-', lw=lw)
    ax.plot([x-0.35, x+0.35], [y1-0.6, y1-0.6], 'k-', lw=lw)
    ax.plot([x-0.35, x+0.35], [y1-1.1, y1-1.1], 'k-', lw=lw)
    ax.plot([x, x], [y1-1.1, y1-1.45], 'k-', lw=lw)
    ax.plot([x, x], [y1-1.45, y2+0.25], 'k-', lw=lw)
    ax.text(x+0.45, (y1+y2)/2, label, fontsize=10, color=color, va='center')

def capacitor_v(x, y1, y2, label, color='red', lw=2):
    """垂直電容 (兩條平行線)"""
    ax.plot([x, x], [y1, y1-0.3], 'k-', lw=lw)
    ax.plot([x, x], [y2, y2+0.3], 'k-', lw=lw)
    ym = (y1+y2)/2
    ax.plot([x-0.4, x+0.4], [ym+0.15, ym+0.15], 'k-', lw=lw)
    ax.plot([x-0.4, x+0.4], [ym-0.15, ym-0.15], 'k-', lw=lw)
    ax.plot([x, x], [ym-0.15, y2+0.3], 'k-', lw=lw)
    ax.text(x+0.45, ym, label, fontsize=10, color=color, va='center')

# ============================================================
# 主佈局
# ============================================================
# TL074 位置: 中央偏右
OPX, OPY = 9.5, 5.5

# ---- 運算放大器 ----
opamp = mpatches.Polygon([
    (OPX, OPY+1.6), (OPX, OPY-1.6), (OPX+2.6, OPY)
], closed=True, fc='#ccffcc', ec='black', lw=2.5)
ax.add_patch(opamp)
ax.text(OPX+0.85, OPY+0.55, '+', fontsize=18, ha='center', va='center')
ax.text(OPX+0.85, OPY-0.65, '-', fontsize=18, ha='center', va='center')
ax.text(OPX+2.8, OPY+0.6, 'TL074 (¼)', fontsize=11, color='green')
ax.text(OPX+2.8, OPY-0.6, '運算放大器', fontsize=9, color='green')

# ---- 電源 ----
# +Vcc (頂)
ax.plot([OPX+0.5, OPX+0.5], [OPY+1.6, OPY+3.2], 'k-', lw=2.5, color='purple')
ax.plot([OPX+0.5, OPX-1.8], [OPY+3.2, OPY+3.2], 'k-', lw=2.5, color='purple')
ax.plot([OPX-1.8, OPX-1.8], [OPY+3.2, OPY+4.0], 'k-', lw=2.5, color='purple')
ax.text(OPX-2.2, OPY+4.0, '+Vcc (9V)', fontsize=11, color='purple', ha='right')
# -Vcc (底)
ax.plot([OPX+0.5, OPX+0.5], [OPY-1.6, OPY-3.2], 'k-', lw=2.5, color='purple')
ax.plot([OPX+0.5, OPX-1.8], [OPY-3.2, OPY-3.2], 'k-', lw=2.5, color='purple')
ax.plot([OPX-1.8, OPX-1.8], [OPY-3.2, OPY-4.0], 'k-', lw=2.5, color='purple')
ax.text(OPX-2.2, OPY-4.0, '-Vcc (-9V)', fontsize=11, color='purple', ha='right')

# ---- 輸出 (右) ----
ax.plot([OPX+2.6, OPX+4.6], [OPY, OPY], 'k-', lw=3)
ax.text(OPX+4.8, OPY+0.2, 'Vout', fontsize=13, fontweight='bold')
# 輸出節點
circ = Circle((OPX+4.6, OPY), 0.14, fc='black')
ax.add_patch(circ)

# ============================================================
# Wien 網絡 (正回授): 接 + 輸入
# ============================================================
# + 輸入位置: (OPX, OPY+0.55) — 引線向左
ax.plot([OPX, OPX-1.0], [OPY+0.55, OPY+0.55], 'k-', lw=2.5)
# 節點 B (+ 輸入連接點)
circ = Circle((OPX-1.0, OPY+0.55), 0.14, fc='black')
ax.add_patch(circ)
ax.text(OPX-1.4, OPY+0.95, '節點 B', fontsize=9, ha='center', color='#666666')

# C1: 節點 B → 節點 A (水平串聯臂上段)
ax.plot([OPX-1.0, OPX-3.2], [OPY+0.55, OPY+0.55], 'k-', lw=2.5)
# C1 符號 (垂直電容, 在 x=OPX-3.2 附近)
ax.plot([OPX-3.2, OPX-3.2], [OPY+0.55, OPY+1.3], 'k-', lw=2)
ax.plot([OPX-3.6, OPX-2.8], [OPY+1.3, OPY+1.3], 'k-', lw=2)
ax.plot([OPX-3.6, OPX-2.8], [OPY+1.0, OPY+1.0], 'k-', lw=2)
ax.plot([OPX-3.2, OPX-3.2], [OPY+1.0, OPY+0.3], 'k-', lw=2)
ax.text(OPX-3.2, OPY+1.7, 'C1\n10nF', fontsize=9, color='red', ha='center')

# R1: 節點 A → Vout (串聯臂上段水平)
# 節點 A 位置: (OPX-3.2, OPY+0.55) 向上轉 再向右
ax.plot([OPX-3.2, OPX-3.2], [OPY+0.55, OPY+2.5], 'k-', lw=2.5)
circ = Circle((OPX-3.2, OPY+0.55), 0.14, fc='black')
ax.add_patch(circ)
ax.text(OPX-3.6, OPY+0.35, '節點 A', fontsize=9, ha='center', color='#666666')
# R1 水平 (x: OPX-3.2 → OPX+0.5, y: OPY+2.5)
ax.plot([OPX-3.2, OPX-1.0], [OPY+2.5, OPY+2.5], 'k-', lw=2)
ax.plot([OPX-1.0, OPX-1.0], [OPY+2.5, OPY+2.0], 'k-', lw=2)
ax.plot([OPX-1.0, OPX+0.5], [OPY+2.0, OPY+2.0], 'k-', lw=2)
ax.plot([OPX+0.5, OPX+0.5], [OPY+2.0, OPY+2.5], 'k-', lw=2)
ax.plot([OPX+0.5, OPX+2.0], [OPY+2.5, OPY+2.5], 'k-', lw=2)
ax.plot([OPX+2.0, OPX+2.0], [OPY+2.5, OPY+0.6], 'k-', lw=2)
# 接回 Vout 線
ax.plot([OPX+2.0, OPX+4.6], [OPY+0.6, OPY+0.6], 'k-', lw=2)
circ = Circle((OPX+4.6, OPY+0.6), 0.14, fc='black')
ax.add_patch(circ)
ax.text(OPX-1.6, OPY+2.85, 'R1  10kΩ', fontsize=11, color='blue', ha='center')

# R2∥C2 並聯臂: 節點 B → GND (垂直向下)
ax.plot([OPX-1.0, OPX-1.0], [OPY+0.55, OPY-1.0], 'k-', lw=2.5)
# R2 (垂直)
ax.plot([OPX-1.0, OPX-1.0], [OPY-1.0, OPY-2.6], 'k-', lw=2)
ax.plot([OPX-1.4, OPX-0.6], [OPY-2.6, OPY-2.6], 'k-', lw=2)
ax.plot([OPX-1.4, OPX-0.6], [OPY-3.2, OPY-3.2], 'k-', lw=2)
ax.plot([OPX-1.0, OPX-1.0], [OPY-3.2, OPY-4.2], 'k-', lw=2)
ax.text(OPX-0.5, OPY-2.5, 'R2\n10kΩ', fontsize=9, color='blue', ha='left')
# C2 (垂直, 並聯 R2)
ax.plot([OPX-2.3, OPX-2.3], [OPY+0.55, OPY-0.4], 'k-', lw=2)
ax.plot([OPX-2.7, OPX-1.9], [OPY-0.4, OPY-0.4], 'k-', lw=2)
ax.plot([OPX-2.7, OPX-1.9], [OPY-0.7, OPY-0.7], 'k-', lw=2)
ax.plot([OPX-2.3, OPX-2.3], [OPY-0.7, OPY-2.6], 'k-', lw=2)
ax.plot([OPX-2.3, OPX-2.3], [OPY-2.6, OPY-4.2], 'k-', lw=2)
ax.text(OPX-3.1, OPY-2.5, 'C2\n10nF', fontsize=9, color='red', ha='right')
# 並聯臂接地
ax.plot([OPX-1.0, OPX-1.0], [OPY-4.2, OPY-4.7], 'k-', lw=2)
ax.plot([OPX-2.3, OPX-2.3], [OPY-4.2, OPY-4.7], 'k-', lw=2)
ax.plot([OPX-2.3, OPX-1.0], [OPY-4.7, OPY-4.7], 'k-', lw=2)
gnd(OPX-1.65, OPY-4.7)
ax.text(OPX-1.65, OPY-6.3, 'GND (信號地)', fontsize=9, ha='center', color='#666666')

# ============================================================
# 負回授: Rf/Ri (接 - 輸入)
# ============================================================
# - 輸入位置: (OPX, OPY-0.65) — 引線向左
ax.plot([OPX, OPX-1.5], [OPY-0.65, OPY-0.65], 'k-', lw=2.5)
circ = Circle((OPX-1.5, OPY-0.65), 0.14, fc='black')
ax.add_patch(circ)

# Ri: - 輸入 → GND (垂直)
ax.plot([OPX-1.5, OPX-1.5], [OPY-0.65, OPY-2.0], 'k-', lw=2)
ax.plot([OPX-1.5, OPX-1.5], [OPY-2.0, OPY-3.4], 'k-', lw=2)
ax.plot([OPX-1.9, OPX-1.1], [OPY-3.4, OPY-3.4], 'k-', lw=2)
ax.plot([OPX-1.9, OPX-1.1], [OPY-4.0, OPY-4.0], 'k-', lw=2)
ax.plot([OPX-1.5, OPX-1.5], [OPY-4.0, OPY-4.7], 'k-', lw=2)
gnd(OPX-1.5, OPY-4.7)
ax.text(OPX-0.95, OPY-3.6, 'Ri  10kΩ', fontsize=10, color='blue', ha='left')

# Rf: - 輸入 → Vout (水平, 上方繞)
ax.plot([OPX-1.5, OPX-1.5], [OPY-0.65, OPY-3.0], 'k-', lw=2)
ax.plot([OPX-1.5, OPX+1.0], [OPY-3.0, OPY-3.0], 'k-', lw=2)
ax.plot([OPX+1.0, OPX+1.0], [OPY-3.0, OPY-3.6], 'k-', lw=2)
ax.plot([OPX+1.0, OPX+3.2], [OPY-3.6, OPY-3.6], 'k-', lw=2)
ax.plot([OPX+3.2, OPX+3.2], [OPY-3.6, OPY-0.4], 'k-', lw=2)
ax.plot([OPX+3.2, OPX+4.6], [OPY-0.4, OPY-0.4], 'k-', lw=2)
circ = Circle((OPX+4.6, OPY-0.4), 0.14, fc='black')
ax.add_patch(circ)
ax.text(OPX+0.7, OPY-4.1, 'Rf  33kΩ (回授)', fontsize=10, color='blue', ha='center')

# 增益標註
ax.text(OPX-0.4, OPY-5.5, '增益 = 1 + Rf/Ri = 1 + 33k/10k = 4.3 (> 3 確保振盪)',
        fontsize=10, color='#cc0000', ha='center')

# ============================================================
# 輸出耦合 + LED 指示
# ============================================================
# Rout → 鄰近節點 (右上)
ax.plot([OPX+4.6, OPX+4.6], [OPY, OPY+1.8], 'k-', lw=2.5)
ax.plot([OPX+4.6, OPX+6.6], [OPY+1.8, OPY+1.8], 'k-', lw=2)
ax.plot([OPX+6.6, OPX+6.6], [OPY+1.8, OPY+1.3], 'k-', lw=2)
ax.plot([OPX+6.6, OPX+8.2], [OPY+1.3, OPY+1.3], 'k-', lw=2)
ax.plot([OPX+8.2, OPX+8.2], [OPY+1.3, OPY+1.8], 'k-', lw=2)
ax.plot([OPX+8.2, OPX+10.5], [OPY+1.8, OPY+1.8], 'k-', lw=2)
ax.text(OPX+7.4, OPY+1.05, 'Rout\n10kΩ', fontsize=9, color='blue', ha='center')
ax.text(OPX+11.2, OPY+1.8, '→ 鄰近節點', fontsize=11, ha='left', va='center')
circ = Circle((OPX+10.5, OPY+1.8), 0.16, fc='black')
ax.add_patch(circ)

# R_LED + 反並聯 LED (右下)
ax.plot([OPX+4.6, OPX+4.6], [OPY, OPY-5.8], 'k-', lw=2.5)
# R_LED
ax.plot([OPX+4.6, OPX+4.6], [OPY-5.8, OPY-6.6], 'k-', lw=2)
ax.plot([OPX+4.2, OPX+5.0], [OPY-6.6, OPY-6.6], 'k-', lw=2)
ax.plot([OPX+4.2, OPX+5.0], [OPY-7.2, OPY-7.2], 'k-', lw=2)
ax.plot([OPX+4.6, OPX+4.6], [OPY-7.2, OPY-8.0], 'k-', lw=2)
ax.text(OPX+5.2, OPY-6.8, 'R_LED\n1kΩ', fontsize=9, color='blue', ha='left')
# LED1 (紅, 向上)
ax.plot([OPX+4.6, OPX+4.2], [OPY-8.0, OPY-8.6], 'k-', lw=2)
tri1 = mpatches.Polygon([(OPX+3.95, OPY-8.6), (OPX+4.45, OPY-8.6), (OPX+4.2, OPY-8.25)], closed=True, fc='#ff6666', ec='red', lw=1.5)
ax.add_patch(tri1)
ax.plot([OPX+4.2, OPX+4.2], [OPY-8.25, OPY-8.0], 'k-', lw=2)
# LED2 (綠, 向下)
ax.plot([OPX+4.6, OPX+5.0], [OPY-8.0, OPY-8.6], 'k-', lw=2)
tri2 = mpatches.Polygon([(OPX+4.75, OPY-8.25), (OPX+5.25, OPY-8.25), (OPX+5.0, OPY-8.6)], closed=True, fc='#66ff66', ec='green', lw=1.5)
ax.add_patch(tri2)
ax.plot([OPX+5.0, OPX+5.0], [OPY-8.25, OPY-8.0], 'k-', lw=2)
# LED 下連接地
ax.plot([OPX+4.2, OPX+5.0], [OPY-8.6, OPY-8.6], 'k-', lw=2)
ax.plot([OPX+4.6, OPX+4.6], [OPY-8.6, OPY-9.2], 'k-', lw=2)
gnd(OPX+4.6, OPY-9.2)
ax.text(OPX+5.6, OPY-8.4, 'LED1(紅)+LED2(綠)\n反並聯: 正交 = 兩顆都熄滅!', fontsize=10, color='#cc0000', ha='left')

# ============================================================
# Wien 網絡說明框
# ============================================================
ax.text(2.0, 8.2, '''
Wien 網絡 (正回授, 接 + 輸入):
  Vout → R1 → 節點A → C1 → 節點B → (+ 輸入)
  節點B → R2 → GND   (並聯臂)
  節點B → C2 → GND   (並聯臂)
  選頻: f = 1/(2π·R·C) = 1.59 kHz

負回授 (接 - 輸入):
  Ri: (- 輸入) → GND
  Rf: Vout → (- 輸入)
  增益 = 1 + Rf/Ri = 4.3 (> 3 振盪條件)

相位指示:
  LED 反並聯跨接節點輸出: 同相=閃亮, 正交=熄滅
''', fontsize=10, va='top', ha='left',
    bbox=dict(boxstyle='round', fc='#f5f5f5', ec='gray', pad=0.8))

ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.set_title('圖 2c: 正確 Wien Bridge 單節點模組 (教科書式) - TL074\nWien 網絡 (R1C1+R2∥C2) 接 +輸入正回授 | Ri/Rf 負回授增益 4.3 | LED 反並聯相位指示',
             fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_node_module_correct.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 圖 2c: 正確 Wien Bridge 節點模組 → circuit_node_module_correct.png")

# ============================================================
# Netlist 接線表 (照住砌)
# ============================================================
netlist = """GRT-38 模擬電路 Netlist — 單節點模組 (Wien Bridge, TL074)
=====================================================================
每 1 個節點需要以下接線 (60 節點 = 重複 60 次):

TL074 (¼ 運放) 接腳:
  Pin 2 (反相輸入 -) : 接 Rf 一端 + Ri 一端
  Pin 3 (正相輸入 +) : 接 C1 一端 (節點B) + R2 一端 + C2 一端
  Pin 6 (輸出)       : 接 Rf 另一端 + Rout 一端 + R_LED 一端
  Pin 4 (-Vcc)       : -9V
  Pin 8 (+Vcc)       : +9V

Wien 網絡 (正回授):
  R1 (10k): 一端接 Vout (Pin6 輸出線), 另一端接 節點A
  節點A: R1 + C1 連接點
  C1 (10n): 一端接 節點A, 另一端接 節點B
  節點B: C1 + R2 + C2 + Pin3 (+輸入) 連接點
  R2 (10k): 一端接 節點B, 另一端接 GND
  C2 (10n): 一端接 節點B, 另一端接 GND

負回授:
  Ri (10k): 一端接 Pin2 (-輸入), 另一端接 GND
  Rf (33k): 一端接 Pin2 (-輸入), 另一端接 Vout (Pin6)

輸出:
  Rout (10k): 一端接 Vout, 另一端接 鄰近節點
  R_LED (1k): 一端接 Vout, 另一端接 LED 對
  LED1 (紅)  + LED2 (綠) 反並聯: 兩端分別接 R_LED 和 GND

阻挫邊 (32 條): 唔用 Rout 直連, 改用 TL074 反相放大器:
  第 2 顆 TL074 嘅 ¼ 接成反相器 (R=10k): Vout_edge = -Vin_edge
  輸入接 節點A 輸出, 輸出接 節點B 輸入 (π 相移)

電源: ±9V (兩顆 9V 電池), 全部 TL074 共用
頻率: f = 1/(2π·10k·10n) = 1.59 kHz
"""
with open(f'{OUT}/circuit_netlist.txt', 'w', encoding='utf-8') as f:
    f.write(netlist)
print("✅ Netlist 接線表 → circuit_netlist.txt")
