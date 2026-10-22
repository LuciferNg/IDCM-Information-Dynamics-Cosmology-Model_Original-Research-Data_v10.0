# SESSION_START — O25 溫度尺度譜

> **開始**: 2026-08-17
> **來源**: O3 衍生問題 O3-5

## 任務

完整表徵節點溫度信號隨平滑尺度嘅變化 (0.5°-15°, 三地圖)。

## 交接點 (從 O3)

- 已有完整 cache: /tmp/cache_o3/ (SMICA/NILC/Commander × 10 尺度 = 30 檔案)
- 已知: 冷熱差 4.17°=-22.3, 10°=-12.5 μK; ΔE0 比例 0.35-0.51 @ 3°-7°
- 冷斑: 4.17°=-134.19, 10°=-68.8 μK
- 唔使重平滑! 直接用 cache

## 第一步

用全部 10 尺度 cache 提取冷熱差 + ΔE0 比例 + 極端行為 per 尺度


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **1 處 WRITE**（推導產物寫出 repo 外）。

### 一. 命中清單

#### 🔴 WRITE（違規）

| # | 檔案:行 | 寫去 |
|:--|:--|:--|
| 1 | `o25_scale_spectrum/scripts/rebuild_cache_o3.py:16` | `/tmp/cache_o3` |

### 二. 處置（別 O 執行；本節只記移交）

```
🔴 WRITE 命中：1 處把推導產物寫出 repo。
   ① 改寫入 <O>/data/（BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   ② 重跑該 script 生成產物，並更新所有引用該 /tmp 路徑嘅地方
   ③ 舊 /tmp 產物**搬入 data/**（唔係複製——避免兩份不一致）
   ④ 重跑 path_hygiene_scan --o-dir 確認 WRITE=0
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
