# O186: TRGB/Miras 校準差異機制

## 狀態: 🟢 已閉合 (19/19 PASS)

TRGB (69.79) 同 Miras (73.29) 嘅校準差異機制已從第一原理推導：

- **TRGB 負偏移 (−κφ⁻¹):** 核心 He 閃 (收縮, 能量向內) → 單層同步事件 → 全耦合
- **Miras 正偏移 (+κφ⁻¹/4):** 表面脈動 (膨脹, 能量向外) → 4 分支樹振盪 → B 稀釋
- **RR Lyrae (+κφ⁻¹/6):** L₄−1 = 2×3 雙模態 × 三世代（🟡 0.5σ，待 JWST/Gaia DR5）

**核心:** 4 = φ³−φ⁻³ = MERA 分支因子 B；6 = L₄−1 = 7−1 = 2×3

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 問題記錄 + 推導結果 + 推導時序索引 | 🟢 |
| `docs/02_mechanism_derivation.md` | 完整結構推導 (6 步) | 🟢 |
| `docs/03_rr_lyrae_operator.md` | RR Lyrae n=6 算符同構 | 🟢 |
| `docs/04_calibration_family_map.md` | 全天體標尺修補總地圖 | 🟢 |
| `docs/05_zero_point_and_layer_unification.md` | Q1-Q5 開放問題閉合 | 🟢 |
| `docs/06_verification_record.md` | 最終核對 + 獨立審計 (2026-09-11) | ✅ 19/19 |
| `final_result.md` | 結論摘要 (RESULT_TEMPLATE) | 🟢 |
| `scripts/01_mechanism_verify.py` | TRGB/Miras 驗證 | ✅ 5/5 |
| `scripts/02_rr_lyrae_verify.py` | n=6 同構驗證 | ✅ 6/6 |
| `scripts/03_layer_unification_verify.py` | 層級統一驗證 | ✅ 8/8 |
| `scripts/04_m_family_verify.py` | M-家族統一驗證 (攻堅 2026-10-10 新增) | ✅ 6/6 |
| `docs/07_attack_session_20261010.md` | 攻堅記錄 (2026-10-10, 三輪) | 🟢 |
| `SESSION_START.md` | Session 啟動文件 | — |

## 預測

RR Lyrae H₀ ≈ 73.06 km/s/Mpc (正修正, +κφ⁻¹/6) — 等待 JWST/Gaia DR5 誤差 < 0.5
