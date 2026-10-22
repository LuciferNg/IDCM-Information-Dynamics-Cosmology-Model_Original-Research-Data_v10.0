# O20 新 Session 啟動文件 — E/B 極化峰

## 所需 Skills

1. `camb-cmb-verification` (核心)
2. `web-access-protocol` (輔助)

## 前置資料

```
T 峰公式: ℓ_m=44×(M−C(9−m,2))+((m−1)×9 mod 25)
T m=1-4: 220/537/810/1014 (0.00-0.49% ✅)
M=33, 44=2N_d
E 峰: 同 T 峰有相位偏移 (ΛCDM: E 領先 T ~π/2)
B lensing: ℓ≈1000
```

## 啟動 Prompt

```
開 O20 極化峰專案: /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o20_eb_polarization/

任務: 推導 E/B 極化峰位置結構公式

背景: T 峰公式已閉合 (m=1-4)。極化峰 (E, B) 未推導。
ΛCDM: E 峰同 T 峰有相位偏移 (聲波速度差)

步驟:
1. E 峰位: Planck PR4 E-mode 譜 → 峰位置
2. TE 相位: T-E 峰位 offset (=結構常數?)
3. B lensing: 透鏡 B 峰 (ℓ≈1000) vs 公式預測
4. 結構: 極化峰 = 溫度峰 + 偏移量 (偏移 = ?)

載入 skills: camb-cmb-verification, web-access-protocol
數據: Planck PR4 (pla.esac.esa.int) 或 CAMB E-mode 模擬
誠實: 如果 E 峰冇簡單結構公式 → 🟡
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. Planck PR4 極化數據未完全公開 — 可能要 CAMB 模擬
2. E 峰比 T 峰更闊 (damping tail) — 峰檢測更難
3. B lensing 好弱 — 峰位誤差大
4. 相位偏移 (TE offset) 可能係結構常數 — 但有冇 φ 公式?