# 模擬電路原理圖 — 完整套件 (2026-08-17)

## 定位

調律者要求: 電路圖未生成 — 補齊可以照住砌嘅完整電路圖套件。

## 電路圖套件 (5 張圖 + 1 netlist)

| 檔案 | 內容 | 狀態 |
|:-----|:-----|:----:|
| `circuit_5node_loop.png` | 圖 1: 5 節點阻挫環 (4 電阻邊 + 1 反相器) | ✅ |
| `circuit_node_module.png` | 圖 2: 概念版節點模組 (TL074 + LED) | ✅ 概念 |
| `circuit_node_module_full.png` | 圖 2b: 實作版 (含 Wien 網絡) | ⚠️ 已取代 |
| `circuit_node_module_correct.png` | 圖 2c: **正確 Wien Bridge 教科書式** | ✅✅ 最終 |
| `circuit_a5_full.png` | 圖 3: 60 節點 A5 全網接線圖 | ✅ |
| `circuit_injection_write.png` | 圖 4: 注入鎖定寫入示意 | ✅ |
| `circuit_netlist.txt` | Netlist 接線表 (照住砌) | ✅ |

## 電路原理修正 (重要!)

**❌ 舊版 (38b) 錯**: Wien 網絡接到反相輸入 (-)
**✅ 新版 (38c) 正確**: 教科書式 Wien Bridge

```
Wien 網絡 (正回授) → + 輸入:
  Vout → R1 → 節點A → C1 → 節點B → (+ 輸入)
  節點B → R2 → GND  (並聯臂)
  節點B → C2 → GND  (並聯臂)

負回授 → - 輸入:
  Ri: (- 輸入) → GND
  Rf: Vout → (- 輸入)
  增益 = 1 + Rf/Ri = 4.3 (> 3 振盪條件)
```

## 正確電路參數

| 元件 | 值 | 作用 |
|:-----|:---|:-----|
| TL074 | ¼ 運放 | 振盪器 |
| R1 = R2 | 10 kΩ | Wien 選頻 |
| C1 = C2 | 10 nF | Wien 選頻 (f ≈ 1.59 kHz) |
| Ri | 10 kΩ | 增益設定 |
| Rf | 33 kΩ | 增益 = 4.3 (>3) |
| Rout | 10 kΩ | 節點耦合 |
| R_LED | 1 kΩ | LED 限流 |
| LED1/LED2 | 紅/綠 5mm | 反並聯相位指示 |
| 電源 | ±9V | 雙電源 |

## 阻挫邊實現

```
32 條阻挫邊: 唔用 Rout 直連, 用另一顆 TL074 ¼ 接成反相器:
  Vout_edge = -Vin_edge (π 相移)
  輸入接 節點A 輸出, 輸出接 節點B 輸入
```

## 驗證流程

1. **5 節點環**: 麵包板 + 5 運放 → 三用電表測相位鎖定
2. **60 節點 A5**: 15 顆 TL074 + 漆包線照鄰接矩陣
3. **量測**: AC 檔測 12 個 ΔE=0 節點電壓 < 其他 48 個 (LED 熄滅)
4. **寫入**: 訊號產生器注入反相信號 → 相位翻轉 π

## 誠實標記

- 圖 2b 曾接錯 (Wien 網絡去反相輸入) — vision 檢查發現, 已修正為 2c
- 圖 2c 經 vision 驗證: 電氣正確 ✅ (Wien→+, Rf/Ri→-, LED 限流, 電源齊全)
- Netlist 係文字版接線表, 同圖互補
- 60 節點焊接需要耐心 (120 邊) — 建議先 5 節點驗證再擴展

## 檔案

```
scripts/38_circuit_diagrams.py (圖1,2,3,4)
scripts/38b_circuit_node_full.py (圖2b, 已取代)
scripts/38c_circuit_wien_correct.py (圖2c + netlist) ✅
data/circuit_*.png ×5
data/circuit_netlist.txt
本文件: docs/15_circuit_diagrams.md
```

---

*文檔: 模擬電路原理圖套件*
*狀態: ✅ 5 圖 + netlist 完成, 圖 2c 電路正確經 vision 驗證*
*日期: 2026-08-17*
