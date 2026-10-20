# cmb_cold_spot 新 Session 啟動文件 — P4 CMB 大冷斑

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

## 所需 Skills（載入順序）

### 1. `idcm-cmb-analysis`（核心, 必須）
- real-data verification workflow (SMICA download/read/smooth/node sampling)
- anchor-control uniqueness tests (node 0 + 57 對徑)
- multi-scale hot-spot hierarchy (F₆ 1.0°, F₇ 0.5°)
- cross-map validation (SMICA × NILC × Commander; NESTED ordering pitfall)
- topological bits / frustration storage (ΔE=0 12 節點)

### 2. `userskills-idcm-v10.0-research-navigation`（輔助/需要時）
- project structure routing; main_problems vs open_problems_fresh conventions

### 3. `polyhedral-graph-analysis`（輔助/需要時）
- Rhombicosidodecahedron 面遍歷/阻挫飽和 (20Δ+30□+12⬠, χ=2)
- graph-rebuild double-verification (O3 88/88)

## 前置資料（session 內需知）

```
專案: /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/
scripts/  # 02-28 (28_double_verification.py = 全量雙重驗證, 26/26 PASS)
data/     # a5_nodes.txt (60 節點), anchored_coloring.txt, frustration_edges.txt (32),
          # smica_smoothed.txt (節點 -134.2μK), smica_permutation.txt (p=0.0186, z=-3.25)
docs/     # 03_first_results, 15_complete_record, 16-21 各階段, 22_complete_summary, 23_edge_closure_integration

SMICA map (Planck 2018 R3.00 full, 2.01GB): /home/wsl/.hermes/cache/scratch/planck_smica/smica.fits
  scripts hardcode /tmp/smica2.fits — 跑前 symlink/copy, WSL 重啟會清 /tmp
冷斑: (209°, -57°) ICRS (48.30°, -20.44°), R8=4.17°, FWHM 平滑
振幅: RMS=ε⁵/8=1.1007e-5, 冷斑=5ε⁵/8=5.5035e-5 (-150μK, SMICA -134.2μK)
常數: ε=φ⁻¹/4, φ=(1+√5)/2, FWHM→σ: σ=FWHM/(2√(2ln2)), 閾值 28°
統計: 排列 p=0.0186 (1.98σ), 隨機著色 z=-3.25σ, 邊長 z=-0.52σ, 錨點唯一 node0/57
```

## 啟動 Prompt（複製做第一條訊息）

```
開 cmb_cold_spot 專案: main_problems/p4_cmb_cold_spot

任務: P4 CMB 大冷斑 — 拓撲干涉節點本質嘅閉合維護 + 殘餘開放項推進

步驟:
1. 審計現有 scripts (02-28) 全量重跑 + data 對照 — data 同 stdout 不一致要修正
2. 推殘餘開放 O2/O3 級問題 — 見 01_problem_record 狀態表
3. 每發現 → 獨立 doc + register 更新

載入 skills: idcm-cmb-analysis, userskills-idcm-v10.0-research-navigation
方法: model-free 統計優先 (排列/隨機著色/錨點對照), RAM-heavy 跑 foreground (4GB cgroup)

誠實: 負結果都要記錄 (🟢/🟡/🔴), 唔好假裝閉合
最後: 雙重驗證 (28_double_verification.py) + 更新 01_problem_record + README
```

## 檔案結構

```
p4_cmb_cold_spot/
├── 01_problem_record.md   # 問題 + 狀態表 (root, 標準)
├── SESSION_START.md       # 本文檔
├── README.md              # 主索引
├── final_result.md        # RESULT_TEMPLATE 格式
├── scripts/               # 02-28 驗證腳本
├── docs/                  # 03, 15-23 各階段記錄
└── data/                  # 節點/著色/阻挫/SMICA 數據
```

## 常見坑 (預先提醒)

1. SMICA map 2.01GB — 下載確認 byte count (2013275520), scripts hardcode `/tmp/smica2.fits`, WSL 重啟清 /tmp → 需要重新 link
2. NESTED ordering — NILC/Commander 要 `nest=True` + `hp.reorder(n2r)`; SMICA 係 RING
3. 「冷/熱色」= BFS parity, 唔係溫度預測器 (node 57 冷色但 +8.21μK)
4. 對徑點 z 值相同 = A₅ 自同構圖論必然, 唔係 anomaly
5. 唔好強迫閉合 — O4 距離衰減已誠實負結果 (BIC constant-mean 贏 φ^-d)