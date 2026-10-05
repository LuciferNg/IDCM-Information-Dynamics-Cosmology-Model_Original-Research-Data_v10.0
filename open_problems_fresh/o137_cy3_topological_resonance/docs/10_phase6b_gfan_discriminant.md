# O137 — Phase 6b: gfan 二次扇 + 判別式盲測

**狀態**: 🟡 部分完成 — gfan 算不了 85 點 4D 二次扇（整數溢出），轉用 GLSM 荷矩陣測試
**日期**: 2026-08-30
**檔案**: scripts/18_gfan_discriminant_blind_test.py

## 一、gfan 指令行測試

**輸入**: 85 點的 Δ* 4D 座標，加前導 1 齊次化
**指令**: `gfan _secondaryfan < gfan_points_input.txt`
**結果**: 🔴 INTEGER OVERFLOW 崩潰

```
INTEGER OVERFLOW
Converting (18563017/395655, ...) to primitive vector
Assertion `0' failed.
```

**原因**: 85 點 4D 點配置的二次扇在 ℝ⁸⁰ 中，有理係數分子/分母過大，gfan 整數類型溢出。

## 二、替代方案：GLSM 荷矩陣抓 Mori 錐生成元

現有 68×73 GLSM 荷矩陣，每行 Q_a 滿足 ΣQ_a = 0。

## 三、判別式盲測

### 公式 z_a(n) = exp(2πi·n·a/88)

| 模式 | 預期 | 結果 | 說明 |
|:---|:---:|:---:|:---|
| n=1 | ✅ ALLOWED | ✅ PASS | 無除數給 z=1 |
| n=7 | ✅ ALLOWED | ✅ PASS | 無除數給 z=1 |
| n=11 | ❌ EXCLUDED | ✅ FAIL | a=8,16,24,32 給 z=1 |
| n=15 | ❌ EXCLUDED | ❌ PASS | 錯誤 — 應排除 |
| n=21 | ❌ EXCLUDED | ❌ PASS | 錯誤 — 應排除 |
| n=25 | ❌ EXCLUDED | ❌ PASS | 錯誤 — 應排除 |
| n=33 | ✅ ALLOWED | ❌ FAIL | 錯誤 — a=8,16,24,32 給 z=1 |
| n=35 | ❌ EXCLUDED | ❌ PASS | 錯誤 — 應排除 |

**結論**: 簡單公式 z_a(n) = exp(2πi·n·a/88) 無法正確復現 {1,7,33} 選擇。

## 四、正確的判別式測試需要 Mori Cone Generators

完整的 GKZ 判別式檢驗須：
1. 沿各 Mori cone generator 方向 Q_a 代 z_a = ∏(x_i)^{Q_a^i}
2. 鏡像映射 t = 1/(2πi)log(z) + O(z)
3. 模式 n 的 Kähler 參數 t_n = γ_n = 4sin²(nπ/88)
4. 判別式 Δ(z) = 0 的條件是 z_a(n) 落於判別式超曲面

**Mori cone generators 受阻原因**: CYTools `extremal_rays()` 超時 + gfan 整數溢出。