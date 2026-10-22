# O121 — 腳本鏈表 (scripts chain, 完整檔名)

> **用途**: §4.9① / §10-A#57 —— 記錄必須**逐個列出完整檔名**。只寫範圍／代號
> （如「scripts/13」）會令一閉合就「看似冇腳本」。本表為機器可查之正典清單。
> **建立**: 2026-10-02 (closeout)

## 主鏈 (chain scripts) — 19 支

| # | 完整檔名 | 產物 | RESULT (最後一跑) |
|:-:|:---------|:-----|:------------------|
| 01 | `scripts/01_tpipe_dag_spectrum.py` | `data/01_tpipe_dag_spectrum.json` | 14 PASS / 0 FAIL |
| 02 | `scripts/02_bh_formation.py` | `data/02_bh_formation.json` | 8 PASS / 0 FAIL |
| 03 | `scripts/03_microstate_count.py` | `data/03_microstate_count.json` | 6 PASS / 0 FAIL |
| 04 | `scripts/04_hawking_radiation.py` | `data/04_hawking_radiation.json` | 8 PASS / 0 FAIL |
| 05 | `scripts/05_information_paradox.py` | `data/05_information_paradox.json` | 8 PASS / 0 FAIL |
| 06 | `scripts/06_cosmic_horizon.py` | `data/06_cosmic_horizon.json` | 9 PASS / 0 FAIL |
| 07 | `scripts/07_transceiver_mechanism.py` | `data/07_transceiver_mechanism.json` | 11 PASS / 0 FAIL |
| 08 | `scripts/08_gravity_metric.py` | `data/08_gravity_metric.json` | 4 PASS / 0 FAIL |
| 09 | `scripts/09_schwarzschild.py` | `data/09_schwarzschild.json` | 10 PASS / 0 FAIL |
| 10 | `scripts/10_singularity_resolution.py` | `data/10_singularity_resolution.json` | 10 PASS / 0 FAIL |
| — | `scripts/audit_independent.py` | （唯讀審計，無 JSON） | 0 deviations |
| 11 | `scripts/11_g8_handover_verify.py` | `data/11_g8_handover_verify.json` | 18 PASS / 0 FAIL |
| 12 | `scripts/12_tau_rec_derivation.py` | `data/12_tau_rec_derivation.json` | 19 PASS / 0 FAIL |
| 13 | `scripts/13_g8_three_items.py` | `data/13_g8_three_items.json` | 22 PASS / 0 FAIL |
| 14 | `scripts/14_g8_deepening.py` | `data/14_g8_deepening.json` | 16 PASS / 0 FAIL |
| 15 | `scripts/15_prediction_register.py` | `data/15_prediction_register.json` | 8 PASS / 0 FAIL |
| 16 | `scripts/16_tau_ref_volume_audit.py` | `data/16_tau_ref_volume_audit.json` | 9 PASS / 0 FAIL |
| 17 | `scripts/17_reeval_corrected.py` | `data/17_reeval_corrected.json` | 6 PASS / 0 FAIL |
| 18 | `scripts/18_three_final.py` | `data/18_three_final.json` | 9 PASS / 0 FAIL |
| 19 | `scripts/19_closeout_audit.py` | `data/19_closeout_audit.json` | close-out 審計器 (A–K)：**67 PASS / 0 FAIL** |
| — | `scripts/run_chain.sh` | （driver of record, §4.9⑥） | dry-run 預設 + `--execute`；20 支全鏈 `exit=0` |

**鏈腳本 PASS 加總**：01–10 = **88**；11–18 = **107**；合計 **195**（`audit_independent` 另計 0 偏差）。

## 正典日誌 (canonical logs)

```
logs/01_tpipe_dag_spectrum.out        logs/11_g8_handover_verify.out
logs/02_bh_formation.out              logs/12_tau_rec_derivation.out
logs/03_microstate_count.out          logs/13_g8_three_items.out
logs/04_hawking_radiation.out         logs/14_g8_deepening.out
logs/05_information_paradox.out       logs/15_prediction_register.out
logs/06_cosmic_horizon.out            logs/16_tau_ref_volume_audit.out
logs/07_transceiver_mechanism.out     logs/17_reeval_corrected.out
logs/08_gravity_metric.out            logs/18_three_final.out
logs/09_schwarzschild.out             logs/19_closeout_audit.out
logs/10_singularity_resolution.out
logs/audit_independent.out
```

**每支皆帶 `^RESULT:` 行**（§4.9）。

## 文件鏈 (docs chain)

| 檔名 | 主題 |
|:-----|:-----|
| `docs/02_ontology.md` | 本體論定位 |
| `docs/03_entropy_structure.md` | 熵結構 |
| `docs/04_hawking_information.md` | Hawking 資訊 |
| `docs/05_string_comparison.md` | 弦論比較 |
| `docs/06_verification.md` | 驗證記錄 |
| `docs/07_transceiver_mechanism.md` | 收發機制 |
| `docs/08_gravity_metric.md` | 引力度規 |
| `docs/09_schwarzschild_derivation.md` | Schwarzschild 推導 |
| `docs/10_singularity_resolution.md` | 奇點消解 |
| `docs/11_audit_record.md` | 審計記錄 |
| `docs/12_return_rate_handover.md` | G8 交接 |
| `docs/13_tau_rec_derivation.md` | G8 主推導 |
| `docs/14_g8_three_items.md` | G8 三項攻堅 |
| `docs/15_g8_deepening.md` | G8 深化 |
| `docs/16_prediction_register.md` | 預言登記 + Gemini 核帳 |
| `docs/17_tau_ref_volume_audit.md` | **τ_ref 體積審計 (root cause)** |
| `docs/18_three_final.md` | G8 三項收尾 |
| `docs/19_closeout_record.md` | **close-out 記錄 (本輪)** |

---

*本檔為 O121 scripts-chain 正典清單 (§4.9①) ｜ 2026-10-02*
