# PROVENANCE -- round manifests and verification intermediates

These files were created during rounds 2-5 **outside** this directory (in the Hermes agent
scratch dir, which prunes entries idle for 24 h).  Mirrored here **byte-identically** on
2026-10-01 so the O224 script chain is self-contained.  The sha256 column is what
`scratch/chain_audit.py` section 4 and `scripts/07_audit.py` A16 re-verify.

| file | sha256 | bytes | mtime | purpose (first line) | matched origin at mirror time |
|:--|:--|--:|:--|:--|:--|
| `o224_r2.sha256` | `56a13722455781b22f444c625ade844e4c6a3ea42d14c4dd111a3808421c67ea` | 177 | 2026-10-01 00:05 | 05cf0a7419da4794361e62cf08c136521f359590448e28fd025c9d02743cc3a7 logs/08_residuals.out | yes |
| `o224_r3.sha256` | `e41c3bdacf441721dda72c4f0baa56f13ad546c3cb6b4045ebc2926433a9987d` | 688 | 2026-10-01 01:41 | f29942104f331b80c15648de34d304e3d0e7e7e344e81ee7585769545b4c4aba data/09_global_n.json | yes |
| `o224_r4.sha256` | `f42b92e2a49f00aa492a8a17d2e3931ae3dab0e02e2bf74dc381e6ce26dee9e4` | 2462 | 2026-10-01 03:14 | a92e3f211c9c2715da53dad7da18eb7730b2363b7cf7acc602cfb373fac28618 data/12_shard_00of12.json | yes |
| `o224_r4_addenda.sha256` | `eb7fd781bae4540b13f83e186788fa6f96ed788f4f3c69bd64a707cc286a0edd` | 255 | 2026-10-01 03:14 | 01712a6de38dee74d0cd4a543d3d98ba897319c6ef9d5437ca22e5f6bdaed27c data/07_audit.json | yes |
| `o224_r5.sha256` | `0883eaf85f35566524af6c56f4f8f3c526ea009bb78decd6d6f2b5ff533a144f` | 3948 | 2026-10-01 09:45 | O224 round-5 (all-window global closure) artefact hashes [revB] | yes |
| `o224_r5_prereg.sha256` | `3771b0040b67d95a91250e326f4c8c98795c367ddd66a412d388c6d1a4428b5b` | 579 | 2026-10-01 04:13 | 78c8964a1b4ab37cc4b1697304c2154a3d405c85f675de3585c6449b856741f2 scripts/16_windows_global.py | yes |
| `r5_shard00_premerge_revA.json` | `6e700a8e9a6a365f961154adfca69f6e9e7bfd27e05477de8943fdfaabdb6dd9` | 3206 | 2026-10-01 09:37 | {"absE4max": 120, "e4_build_s": 0.0, "engine": "numba-jit-parallel (18_windows_global_jit.py)", "groups_scanned": 1233924, "n_shards": 12, "outer_tupl | yes |
| `r5_shards_revA.sha256` | `c6fd66c9ca1cf28b53b82a7852cd089e9add3516b658555fac2447c076119830` | 1104 | 2026-10-01 09:38 | 6e700a8e9a6a365f961154adfca69f6e9e7bfd27e05477de8943fdfaabdb6dd9 data/16_shard_00of12.json | yes |
| `shard11_pre_rerun.json` | `29fb99cc9d072466528cad2100e69be538b8ee4d7de67cb2e60186ce24bab550` | 3204 | 2026-10-01 09:39 | {"absE4max": 120, "e4_build_s": 0.0, "engine": "numba-jit-parallel (18_windows_global_jit.py)", "groups_scanned": 1230080, "n_shards": 12, "outer_tupl | yes |
| `smoke_12_shard_00of3844.json` | `b0862b72695322c1767eefdb876df2658ae46635b3e2358d53e44f13f89699f1` | 504 | 2026-10-01 01:57 | { | yes |
| `smoke_12_shard_3843of3844.json` | `3e0109f91fc44e4095c5dfbbc4152c54de3dfe451b2548cdd30eda12160c8c39` | 516 | 2026-10-01 01:57 | { | yes |

Total: 11 files, 11 with a verified origin match.
