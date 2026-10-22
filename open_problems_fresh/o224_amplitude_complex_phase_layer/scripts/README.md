# O224 `scripts/` — the complete script chain

Four groups, all inside this folder (nothing needed from outside except `data/` and `logs/`):

| group | files | role |
|:--|:--|:--|
| **judgment chain** (rounds 1–5) | `00_contract` … `11_determinism`, `12_n4_global`, `13_party_window`, `14_census_exact`, `15_anti_convention`, `16_windows_global`, `17_windows_global_gpu`, `18_windows_global_jit`, `07_audit` (A1–A16), `lib2i` | produce every artefact in `data/`; `07_audit.py` is the standing audit |
| **driver of record** | `run_chain.sh` (dry-run by default), `run_r4_shards.sh`, `run_r4_closeout.sh`, `run_r5_ranges.sh` | reproduce any round / the whole chain |
| **round 2–5 probes** | `probe_quant`, `probe_a4b`, `probe_axisfamily`, `probe_e4mask`, `probe_relax`, `probe_r7a_fix`, `probe_v8_debug`, `probe_anti_dbg`, `probe_r4`, `probe_r5`, `bench_r5`, `prof_r5`, `probe_gpu`, `probe_gpu2` | exploratory / diagnostic steps taken between rounds |
| **close-out tools** | `measure_engines.py`, `chain_audit.py` (+ archived `chain_audit_v1.py`) | engine-cost measurement, chain-completeness audit |

* `MIRROR_PROVENANCE.md` — sha256 provenance for the mirrored probe/launcher files.
* Full chain map, round table and known limits: `../docs/07_script_chain.md`.
* Probes are CWD-dependent (they `sys.path.insert(0,'scripts')`): run them from the O224 root,
  e.g. `/usr/bin/python3 scripts/probe_r4.py`.
