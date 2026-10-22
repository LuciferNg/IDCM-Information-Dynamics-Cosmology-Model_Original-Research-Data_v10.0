# PROVENANCE -- script chain files in scripts/ that did NOT originate here

Two groups.  **(A) MIRRORED**: created during rounds 2-5 OUTSIDE this O directory (Hermes agent
scratch dir, pruned after 24 h idle), copied in byte-identically on 2026-10-01, then MOVED from
`scratch/probes/` into `scripts/` so the whole script chain -- judgment scripts, probes,
launchers, close-out tools -- lives in one folder.  The sha256 column is re-verified by
`scripts/chain_audit.py` section 4 and by `scripts/07_audit.py` A16.
**(B) NATIVE**: written directly inside this O directory; listed so the folder has one provenance
table.  NOTE: editing any listed tool invalidates its row -- regenerate this table, refresh the
same row in `data/16_r5_manifest.sha256`, then re-run the audits.

## A. Mirrored files (origin = Hermes agent scratch dir)

| file in scripts/ | sha256 | bytes | mtime | purpose (first line) | == origin |
|:--|:--|--:|:--|:--|:--|
| `probe_quant.py` | `fb5de5c376799458ea50ce02daf6af7fdbce8a87128006b5b8067f75214e36cc` | 2819 | 2026-09-30 23:09 | scratch probe: where does the 1/15 (mod-8) quantisation of the frozen correlation come from?""" | yes |
| `probe_a4b.py` | `3e9b073f09833b184423481655b2bb4454d1a1c884b4d0ea1d6407d5da6aa812` | 2027 | 2026-09-30 23:43 | scratch: debug the A4b inner-automorphism transport failure at h = 5.""" | yes |
| `probe_axisfamily.py` | `c7405574349191083bde2caedce7379c2dfead04c203be6e158a39d0fab948a4` | 3445 | 2026-09-30 23:39 | scratch: which condition makes the 60-class sum divisible by 4 (numerator divisible by 8)? | yes |
| `probe_e4mask.py` | `8f260015b65cf892a1b454e62ce23f7fdde5720b0c6cdba38d41e8730646f796` | 2768 | 2026-10-01 00:31 | scratch probe: masked maxima of /E4/ under window constraints (round-3 planning).""" | yes |
| `probe_relax.py` | `1d7d3d7eda307d35cf6c49e5dcaa435b768440c911d9d3ae2692eebb79b48c75` | 3406 | 2026-10-01 00:39 | scratch probe: is the (c,c')-separated relaxation of the n=4 Mermin maximum tight? | yes |
| `probe_r7a_fix.py` | `20ffde1ff244dd804daa295364372dc554bb7d7a40f07028f592f7644bf48951` | 3320 | 2026-10-01 00:55 | scratch smoke test: verify the fixed brute_val against the explicit F/G split, and the | yes |
| `probe_v8_debug.py` | `a6d1ae289f29e1e9a0f589f6372df27087bf026bb6c5c0170c79fe44c4be9e13` | 2157 | 2026-09-30 23:39 | scratch: why does my V8 parity check disagree with probe_quant.py's control? | yes |
| `probe_anti_dbg.py` | `970026d5c3df1c887f9a336a86719105ff7edbfe6e31e923a811428bcd8a24ea` | 3212 | 2026-10-01 03:10 | scratch debug: why do the three antipodal-realisation counts differ (392 / 880 / 1734 / 1794 / | yes |
| `probe_r4.py` | `684c311a30232d4de5295cafd1b43a53684c65e27e553b24e81f27e2670149b2` | 8471 | 2026-10-01 01:50 | Round-4 probe (scratch): (1) time the vectorised (d,d') separable inner solve; (2) check the | yes |
| `probe_r5.py` | `8a8604185bb97c4ef778d3e8003485db868afd4533860bdb81cc3038deffefce` | 2263 | 2026-10-01 03:27 | import sys, time, numpy as np | yes |
| `bench_r5.py` | `54acfd59a113a3d662f94dc843e4a02f4a276f29d278ba5283a15142e32356c6` | 2409 | 2026-10-01 03:27 | import sys, time, numpy as np | yes |
| `prof_r5.py` | `77bd932fe3e97bf25db3354b1322632585b3d21c28ea099ab162329c930d3a2e` | 2368 | 2026-10-01 03:36 | import sys, time, numpy as np, importlib.util | yes |
| `probe_gpu.py` | `a408f7201fda2e6e5a38f21ee0e802723d65dc9c10aaf16d4962bbd1a66f49e9` | 1422 | 2026-10-01 03:33 | import sys, time, numpy as np, importlib.util, os | yes |
| `probe_gpu2.py` | `98b353619235f09e4c7b7426ec027dd29e9fe9da9d62a985cd8f26c0d63101e7` | 1468 | 2026-10-01 03:38 | import sys, time, numpy as np, importlib.util | yes |
| `run_r4_shards.sh` | `3f4788e582138f53884e67615dcafec712c64c1c96bc0d8d059997c826f208af` | 481 | 2026-10-01 01:58 | round-4 sharded runner: 12 shards over the party-1 ordered pair index | yes |
| `run_r4_closeout.sh` | `dde378dc4356b1bb2a08a3751aa7018d78aa5da80a5ceb8ebda7249f91148989` | 770 | 2026-10-01 02:30 | round-4 close-out chain: determinism (D1-D3) -> re-aggregate -> addendum -> audit | yes |

## B. Native files (created inside this O directory, then moved into scripts/)

| file in scripts/ | sha256 | bytes | mtime | purpose (first line) |
|:--|:--|--:|:--|:--|
| `run_chain.sh` | `d8525fb6859d646a04c00d2e28a4b19d57b52c1dd28e37db1a16a951d36c4eca` | 4594 | 2026-10-01 15:59 | ============================================================================================ |
| `run_r5_ranges.sh` | `2a86a162dc5b8a349f6205600d5c18aa967626547fd094bd0449baa4ded453c8` | 1580 | 2026-10-01 04:05 | O224 round-5 launcher: exact global extremes of all five Bell windows of n=4 Mermin over the whole |
| `measure_engines.py` | `fe77ee677a6dbe67de389a9170ef38f1d1e92473e7b04de8ab0fe10abd6d0e57` | 5234 | 2026-10-01 11:24 | O224 scratch/measure_engines.py -- LOGGED measurement of the three round-5 engines on this box, |
| `chain_audit.py` | `eec5f5d57b9b4a78df2d94ce5a851a758a21627a93754ffbf471b37fa39e03cb` | 11896 | 2026-10-01 15:59 | O224 scratch/chain_audit.py -- CHAIN COMPLETENESS AUDIT for the O224 derivation. |
| `chain_audit_v1.py` | `261fa02596139983e4dbc2127d167dbcf5c8c2a9932f57818287c22f6ad1f363` | 7119 | 2026-10-01 15:51 | O224 scratch/chain_audit.py -- mechanical audit of the SCRIPT CHAIN: which script produces which |

## Verification
```bash
/usr/bin/python3 scripts/chain_audit.py    # section 4 re-hashes every row
/usr/bin/python3 scripts/07_audit.py      # A16 re-hashes every row
```
