# O160 docs/01 — 工具註冊 (Tool Registry)

> 2026-09-08 | scripts/01 | 16/16 PASS + 全 integration PASS

## 1. 註冊咗啲乜

4 套譜幾何工具統一成一個 agent 可呼叫層:

| key | 項目 | 路徑 | 狀態 |
|:---:|:-----|:-----|:-----|
| csg | CSG SpectralSpace (K_Chain 版) | `/home/wsl/Projects/ChronologicalStringSpectralGeometry` | ✅ probe PASS + 2 integration PASS |
| ktsg | KTreeSpectralGeometry (K_Tree 版) | `/home/wsl/Projects/KTreeSpectralGeometry` | ✅ probe PASS + 5 integration PASS (51/51 平台 + 23/23 docking) |
| v2 | CSG-v2 v2core (T̂ 代數) | `/home/wsl/Projects/ChronologicalStringSpectralGeometry-v2` | ✅ probe PASS |
| fsr | O140 FSR (有限譜相對論) | `<IDCM>/open_problems_fresh/o140_finite_spectral_relativity` | ✅ probe PASS + 2 integration PASS (38/38 + generic-N) |

## 2. 兩層註冊

**Agent skill**: `idcm-spectral-scan-tools` (~/.hermes/skills/idcm/) — 程序知識: 4 套工具 API、掃描慣例、排除法管線、pitfalls。

**Agent tools**: `tools/registry.py` + `tools/cli.py` (O160):
- `registry.load(tool)` — spec_from_file_location 直接載入源檔 (避開 4 項目共用 `src/` 嘅 namespace 碰撞)
- `registry.probe(tool)` / `probe_all()` — smoke test
- `registry.integrate(tool)` — 喺項目 root 跑官方入口 (subprocess)
- `registry.get_spectra()` — 統一本徵值 (掃描器真源頭)
- `registry.invariants(a,b,c)` — 單格 13 族不變量 (mpmath 50dps)
- `cli.py`: `list` / `probe` / `spectra` / `invariants A B C`

## 3. 統一本徵值 (get_spectra 驗證)

| check | 值 | 結果 |
|:------|:---|:-----|
| Σγ (88) | 178.000000 = 2F₁₁ | ✅ |
| Σγ_even | 90.000000 (世界) | ✅ |
| Σγ_odd | 88.000000 (觀察者) | ✅ |
| Σλ | 66.000000 = 2K_tree | ✅ |
| FSR 恆等 γ_fsr = 2/ω | 全譜 | ✅ |
| E−O | 2 = μ² | ✅ |
| γ44 Σ | 90 | ✅ |

## 4. 踩過嘅坑

1. **跨項目 `src` namespace 碰撞**: CSG/KTSG 都有 regular `src/` package — `import src.xxx` 會撞。解法: spec_from_file_location + 獨特 module name (`o160_<tool>_<stem>`)。
2. **FSR script top-level 打印**: import 時執行全 script — load() redirect stdout 靜音。
3. **路徑**: o140 喺 `open_problems_fresh/` 下, 唔係 IDCM root 下 (OPF vs IDCM_ROOT)。
4. **mpmath 恆等檢查**: `==` 對 sin/cos 數值尾位假 FAIL — 一律用容差 (O158 同款坑)。

## 5. 驗證統計

- scripts/01: **16/16 PASS** (4 probe + 9 spectra + 3 invariants)
- Integration: csg 2/2, ktsg 5/5 (51/51 + 23/23 + 3 模組), fsr 2/2 (38 PASS + generic-N) — 全部 PASS
