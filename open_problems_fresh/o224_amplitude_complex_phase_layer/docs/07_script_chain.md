# O224 劇本鏈完整性審計（script chain audit）

> **2026-10-01 合併更新**：全部劇本（判定鏈＋driver＋探針＋工具）現時**都喺 `scripts/` 內**；
> 此前一輪曾鏡射到 `scratch/probes/`（位置不對），已搬正並刪除該目錄，A16 加 `SCRIPT CONSOLIDATION` 斷言。

**問題**：整個 O224 推導過程，是否完整留下 python 劇本檔案鏈？
**答案**：**現時係「是」**。原本有**一處真缺口**（R2–R5 探針、啟動器、round manifests 只存在於 Hermes agent
scratch，該目錄 24 小時閒置即被清）；已全部**鏡射入本目錄**並以 sha256 釘住。機械證據：
`logs/19_chain_audit.out`（**VERDICT: CHAIN COMPLETE, 0 failed checks**）＋ `scripts/07_audit.py` **A16 PASS**。

---

## 1. 主鏈（judgment chain，R1–R5）：每件 artefact 恰好一支生產腳本

| # | 劇本 | 產物 | log | 輪 |
|:--|:--|:--|:--|:--|
| 00 | `scripts/00_contract.py` | `data/00_contract.json`（合約＋預註冊）| `logs/00_contract.out` | R1 |
| 01 | `scripts/01_relock.py` | `data/01_relock.json`（凍結機器重鎖）| `logs/01_relock.out` | R1 |
| 02 | `scripts/02_phase.py` | `data/02_phase.json`（判項 a）| `logs/02_phase.out` | R1 |
| 03 | `scripts/03_tensor.py` | `data/03_tensor.json`（判項 b）| `logs/03_tensor.out` | R1 |
| 04 | `scripts/04_multiparty.py` | `data/04_multiparty.json`（判項 c, B6 界）| `logs/04_multiparty.out` | R1 |
| 04b | `scripts/04b_window.py` | `data/04b_window.json`（c 之修正：三體序貫 E3）| `logs/04b_window.out` | R1 |
| 05 | `scripts/05_valueset.py` | `data/05_valueset.json`（判項 d）| `logs/05_valueset.out` | R1 |
| 06 | `scripts/06_escape.py` | `data/06_escape.json`（判項 e, F1/F2）| `logs/06_escape.out` | R1 |
| 07 | `scripts/07_audit.py` | `data/07_audit.json`（A1–A16 審計＋ledger）| `logs/07_audit.out` | 每輪 |
| 08 | `scripts/08_residuals.py` | `data/08_residuals.json`（四殘留）| `logs/08_residuals.out` | R2 |
| 09 | `scripts/09_global_n.py` | `data/09_global_n.json`（E4 全層、n=4 窗）| `logs/09_global_n.out` | R3 |
| 10 | `scripts/10_e5.py` | `data/10_e5.json`（E5 全 62⁵）| `logs/10_e5.out` | R3 |
| 11 | `scripts/11_determinism.py` | `data/11_determinism.json`（D1–D3）| `logs/11_determinism.out` | R3/R4 |
| 12 | `scripts/12_n4_global.py` | `data/12_n4_global.json`（＋12 分片 `data/12_shard_KKof12.json`）| `logs/12_n4_global.out` / `logs/12_shard_KK.out` | R4 |
| 13 | `scripts/13_party_window.py` | `data/13_party_window.json`（合法窗）| `logs/13_party_window.out` | R4 |
| 14 | `scripts/14_census_exact.py` | `data/14_census_exact.json`（存在計數）| `logs/14_census_exact.out` | R4 |
| 15 | `scripts/15_anti_convention.py` | `data/15_anti_convention.json`（慣例判別）| `logs/15_anti_convention.out` | R4 |
| 16 | `scripts/16_windows_global.py` | `data/16_windows_global.json`（＋12 分片 `data/16_shard_KKof12.json`）| `logs/16_aggregate.out` | R5 |
| 17 | `scripts/17_windows_global_gpu.py` | `data/16_shard_KKof12.json`（CuPy 引擎，同 schema；G1 跨引擎核對）| `logs/17_check_g1.out` | R5 |
| 18 | `scripts/18_windows_global_jit.py` | `data/16_shard_KKof12.json`（Numba JIT 生產引擎；`--run-range` checkpoint、`--merge`）| `logs/18_*.out` | R5 |
| — | `scripts/lib2i.py` | （庫：精確 Q(√5) 機器、Report 寫入器）| — | R1–R5 |

## 2. 驅動（driver of record）：`scripts/run_chain.sh`

原本缺口：**調用命令列**冇被保存（腳本、產物、log 都在，但「邊條命令、咩次序」只存在於對話 ✗）。
而家 `scripts/run_chain.sh` 由腳本自身 docstring 之用法欄（例：`python3 scripts/12_n4_global.py --shard K N`）
＋ 磁碟上真實 log 檔名**機械重建**全鏈 **49 條調用**（31 個 `run` 語句），**預設 dry-run**，
要 `--execute` 才會真跑（避免誤覆寫）。驗證：`bash -n` ✓、每條命令之腳本存在 ✓、所用 flag 逐個出現在該腳本
源碼中 ✓（A16 檢查）。

## 3. 外部產物之鏡射（byte-identical）

| 目錄 | 內容 | 數量 |
|:--|:--|--:|
| `scripts/`（曾為 `scratch/probes/`） | R2–R5 探針與 R4/R5 啟動器（`probe_quant/a4b/axisfamily/e4mask/relax/r7a_fix/v8_debug/anti_dbg/r4/r5`、`bench_r5`、`prof_r5`、`probe_gpu`、`probe_gpu2`、`run_r4_shards.sh`、`run_r4_closeout.sh`）| 16 |
| `scratch/manifests/` | round manifests（`o224_r2/r3/r4/r4_addenda/r5_prereg/r5.sha256`）＋中間產物（smoke、revA 分片、`shard11_pre_rerun`）＋ `r5_premerge_revA/` | 11 + 12 |

每檔附 `PROVENANCE.md`：**完整 sha256、bytes、mtime、用途、鏡射時是否與來源一致**（27/27 一致 ✓）。

## 4. 唯一外部依賴

`data/frozen/*`（`04_b2_settings.json`、`08_a2_h_table.json`、`09_a2_correlation.json`、`o222_snapshot.sha256`、
`MANIFEST.json`）—— 即 **O222 凍結機器快照**，R1 複製入來後唯讀。除此之外，**全鏈自足** ✓。

## 5. 如何自行驗證（3 條命令）

```bash
bash scripts/run_chain.sh                    # dry-run: 印出全鏈 49 條調用（零副作用）
/usr/bin/python3 scripts/chain_audit.py      # 產物歸屬 + driver + 鏡射雜湊 → VERDICT
/usr/bin/python3 scripts/07_audit.py         # A15（R5 產物）＋ A16（鏈條完整性）
```

## 6. 已知限制（如實列出）

1. **R1–R3 調用非逐字記錄**：該等輪次係互動式執行，`run_chain.sh` 之重建依據為腳本 docstring 用法欄＋log 檔名
   （**語意正確、非逐字回溯**）。R4/R5 有原啟動器 `run_r4_shards.sh`／`scratch/run_r5_ranges.sh` ✓。
2. **兩支無法歸屬之 Hermes scratch 檔**（`diag59.py`、`diag59b.py`：多項式/gcd 題材，**無** `o224` 引用、
   **無** `lib2i` 引用）⟹ **未鏡射**、亦不屬本 O 鏈條（如實列出，不強行歸戶）。
3. **docs 係 live 文件**（drift-by-design）⟹ 不入雜湊 manifest；`data/16_r5_manifest.sha256` 只收不可變產物。
   `07_audit.py` 自身入 manifest（tripwire），故**改完 07 後須刷新 manifest 該行再跑審計**。
4. `data/smoke/16_shard_01of3844.json` 係**歸檔**（早前 smoke 產物，移位保留，非鏈條步驟）。
5. 引擎成本量測另有專檔：`scripts/measure_engines.py` → `logs/18_engine_measure.out`（見 docs/06 §7.9）。

## 變更史

- 2026-10-01：初版（鏡射至 `scratch/probes/`）。
- 2026-10-01（同日稍後）：**合併入 `scripts/`**（16 腳本）；新增 `scripts/README.md`、
  `scripts/MIRROR_PROVENANCE.md`（逐檔 sha256，A 組 16/16 與來源一致）；`run_chain.sh` 路徑更新；
  `scratch/probes/` 移除；A16 加 consolidation 斷言；審計 19/21（A1／A11 環境儀器）。
