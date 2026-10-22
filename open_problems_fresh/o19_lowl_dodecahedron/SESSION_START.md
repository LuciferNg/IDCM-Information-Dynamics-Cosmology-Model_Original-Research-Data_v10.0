# O19 新 Session 啟動文件 — 低 ℓ 異常

## 所需 Skills

1. `polyhedral-graph-analysis` (核心)
2. `camb-cmb-verification` (輔助)

## 前置資料

```
Planck 低 ℓ 異常: 功率低, 四極/八極對齊, 60° 尺度
dodecahedron 5-5 軸角: 63.435°
A₅ 60 節點: 26.09° 邊長 (已閉合)
冷斑: ℓ≈44 (已閉合)
```

## 啟動 Prompt

```
開 O19 低ℓ異常專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o19_lowl_dodecahedron/

任務: 用 A₅ 節點網絡解釋 Planck 低 ℓ 異常

背景: Planck 低 ℓ (ℓ<10) 有異常: 功率低, 對齊, 60° 尺度
IDCM: 60 節點網絡 = 拓撲結構 → 可能解釋

步驟:
1. 60° 異常 vs dodecahedron 63.435° 幾何
2. 低 ℓ 譜預測: 節點網絡 → C_ℓ (ℓ<10)
3. 對齊檢驗: 四極/八極 vs A₅ 軸
4. 冷斑連結: 同源?

載入 skills: polyhedral-graph-analysis, camb-cmb-verification
方法: 60 節點點場 → 諧波分解 → C_ℓ 預測
誠實: 如果預測唔符觀測 → 🟡
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. 低 ℓ 樣本少 (2ℓ+1 個 mode) — 宇宙方差大
2. 60° 異常同 dodecahedron 63.435° 有 5% 差 — 要解釋
3. 點場 C_ℓ 同溫度場 C_ℓ 唔同 — 要清楚做邊個
4. 對齊異常有爭議 (look-elsewhere effect)
