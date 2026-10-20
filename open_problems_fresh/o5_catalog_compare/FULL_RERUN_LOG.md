# O5 完整重跑記錄 (2026-08-17)

> 調律者指示: 所有曾因超時而優化過嘅測試重新跑一次完整版 — 唔用 cache (由 raw 重平滑), 唔設 timeout, 只監控有冇因 bug 停止。

## 執行摘要

| 項目 | 狀態 |
|:-----|:-----|
| 重平滑 | ✅ 由 raw SMICA (2GB) 重新生成 1.0°/3.0°/5.0° map |
| 02-05 | ✅ 完成 (background worker, 正常) |
| 06 | 🔴 OOM × 2 → ✅ foreground 跑成功 (int64 保持) |
| 07-11 | ✅ 完成 (node9 scripts 修正 CACHE_DIR) |
| 最終驗證 | ✅ **12/12 通過** |

## 遇到嘅 Bug (全部已修復)

### 1. 🐛 Background worker 4GB OOM (最關鍵)
- **症狀**: 06_cross_scale_match 兩次 exit=-9 (SIGKILL)
- **真相**: Hermes background worker 用 `systemd-run --user --scope` 建立獨立 cgroup, `MemoryMax=4GB` (process_registry.py `_WORKER_MEMORY_MAX_CAP_BYTES = 4GiB`)
- **證明**: `cat /proc/self/cgroup` → foreground 喺 `hermes-gateway.service` (memory.max = max), 而 worker scope 係 4GB
- **解決**: 用 **foreground terminal** 跑 (無 worker 限制) — 06 6 次 flood-fill (每次 3.22GB int64) 全部成功
- **記憶**: `TERMINAL_LOCAL_MEMORY_MAX_MB` env 只能收緊唔能放寬 (min(override, safe_bound))
- ⚠️ `.wslconfig` 已改 memory=56GB (調律者批准), 但**要等其他 session 完成先重啟生效**

### 2. 🐛 /tmp 磁碟滿 (tmpfs 16GB)
- **症狀**: 08 寫 cache 失敗 `Not enough space on disk: requested 402653184, available 0`
- **真相**: /tmp 係 tmpfs 16GB — 11 張 .prefull 舊 cache (4GB) + 新生成 cache + O3 嘅 5.5GB cache_o3 塞滿
- **解決**: 刪 .prefull + **調律者指示「不用 tmp」** → cache 改放專案 `data/smooth_cache/` (1.9GB)

### 3. 🐛 CACHE_DIR 未定義 (script 10)
- **症狀**: `NameError: name 'CACHE_DIR' is not defined`
- **真相**: 批量替換 script 只喺「import os」後插 CACHE_DIR, 但 10_node9_hop.py 原本冇 import os
- **解決**: 加 `import os` + CACHE_DIR 定義

### 4. ⚠️ 平滑 cache 檔名不一致 (02 寫 5.0 vs 05 讀 5)
- **真相**: 02 用 `CACHE5='/tmp/smica2_smooth5.fits'` 但其他用 `f'{fwhm}'`='5.0'
- **解決**: 02 改為 `smica2_smooth5.0.fits` 統一

## 結果一致性 (新舊對比)

| 量 | 舊 (cache) | 新 (raw 重平滑) | 一致? |
|:---|:-----------|:----------------|:-----:|
| node0 (冷斑) 5.0° | -124.6 μK | -124.6 μK | ✅ |
| node0 3.0° | -145.0 μK | -145.0 μK | ✅ |
| node9 3.0° | -110.6 μK | -110.6 μK | ✅ |
| node9 26° 環 p | 0.018 | 0.018 | ✅ |
| 1.0° cold top12 | 2/12 [0,9] | 2/12 [0,9] | ✅ |
| 3.0° cold top12 | 1/12 [0] | 1/12 [0] | ✅ |
| 5.0° cold top12 | 1/12 [0] | 1/12 [0] | ✅ |
| 三地圖 spread | 2.6% | 2.6% | ✅ |

**所有數字完全一致 — 之前嘅 cache 優化冇引入偏差。**

## 最終結果 (確認無誤)

1. **節點 0 (大冷斑)** 係唯一跨尺度一致命中 (1.0°/3.0°/5.0° 全中)
2. **節點 9 = 第二冷結構** (三地圖 2.6%, 26° 環 p=0.018, 10° 全網最冷)
3. 熱斑 F₆/F₇ 唔喺節點上 (距離 8-9°) — 隨機水平
4. 其他冷/熱斑命中率 = 隨機期望 (11.4% 覆蓋)

## 檔案

```
data/smooth_cache/          # 10 張平滑 map (0.5°-10.0°, 1.9GB) — 專案本地, 唔用 /tmp
data/backup_pre_full/       # 重跑前備份
data/full_rerun_*.log       # 重跑 log
scripts/master_full_rerun.sh   # master runner (02-11)
scripts/master_resume_rerun.sh # resume runner (06-11)
```
