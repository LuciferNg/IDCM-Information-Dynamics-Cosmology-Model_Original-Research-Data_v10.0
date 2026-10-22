# MANIFEST — O229（R1 ＋ R2 ＋ R3 ＋ R4 ＋ R5）

> **日期**: 2026-10-04 ｜ **檔案數**: 141 件（唔含本 MANIFEST 自身）
> **凍結合約 R1** `docs/00_contract.md` sha256 `e3f18caac665984bbdb7ffd0a71a5e00131396ee771b75f7094633928743b449`
> **凍結合約 R2** `docs/08_r2_contract.md` sha256 `cd2e8af286d3bceae947cb8355cbc1828d8e29e790617c37c3f3ed0cd1ccbd96`
> **凍結合約 R3** `docs/14_r3_contract.md` sha256 `a1ee4af87565432627539912983bb21982c475806835aec252823f589d04e3d3`
> **凍結合約 R4** `docs/20_r4_contract.md` sha256 `58aa031d84ef81742a0b58fc9e580c8662eb090e6b1ce03c7eb5962cea045953`
> **凍結合約 R5** `docs/26_r5_contract.md` sha256 `ab53e38fc7fce72050a8fade3e90372096375c7fa929efd2460f54e6506a4a10`
> **規則版本**: o229-r1+r2+r3+r4+r5 contract v1 + closeout-2026-10-04

## 一、閘門
**R1** = 233/234（8 引擎）
**R2** = 42/44（3 引擎） ＋ 獨立核對 `12_r2_independent_audit` 21/21
**R3** = 59/65（4 引擎） ＋ 獨立核對 `17_r3_independent_audit` 18/18
**R4** = 33/35（3 引擎） ＋ 獨立核對 `21_r4_independent_audit` 18/18
**R5** = 24/29（3 引擎） ＋ 獨立核對 `25_r5_independent_audit` 23/23

**2026-10-04 全鏈 closeout 重跑閘（尾部更新，`logs/closeout_*`；正典 logs = R1–R5 era 記錄）**：`05_gap3_completeness` 29/29 ＋ `08_independent_audit` 45/45 ＋ `12_r2_independent_audit` 21/21 ＋ `17_r3_independent_audit` 18/18 ＋ `21_r4_independent_audit` 18/18 ＋ `25_r5_independent_audit` 23/23 ⟹ 合計 154/154

```
01_atom_identity                   RESULT: 74/74 PASS
02_roles_graph                     RESULT: 34/34 PASS
03_gap1_degeneracy                 RESULT: 14/14 PASS
04_gap2_mu2_identity               RESULT: 20/20 PASS
05_gap3_completeness               RESULT: 25/25 PASS
06_gap4_rigidity                   RESULT: 9/9 PASS
07_gap5_density                    RESULT: 12/13 PASS
08_independent_audit               RESULT: 45/45 PASS
09_r2_index_identity_and_routes    RESULT: 14/15 PASS
10_r2_vmin_and_qed_sum             RESULT: 13/13 PASS
11_r2_two_param_rigidity           RESULT: 15/16 PASS
12_r2_independent_audit            RESULT: 21/21 PASS
13_r3_y_uniqueness                 RESULT: 14/16 PASS
14_r3_spectrum_family              RESULT: 19/22 PASS
15_r3_polysemy_classification      RESULT: 15/16 PASS
16_r3_density_atom_pool            RESULT: 11/11 PASS
17_r3_independent_audit            RESULT: 18/18 PASS
18_r4_chain_family                 RESULT: 13/13 PASS
19_r4_mu2_support                  RESULT: 12/12 PASS
20_r4_hardtest_reaudit             RESULT: 8/10 PASS
21_r4_independent_audit            RESULT: 18/18 PASS
22_r5_endpoint_anatomy             RESULT: 13/13 PASS
23_r5_form_class                   RESULT: 8/8 PASS
24_r5_discrimination               RESULT: 3/8 PASS
25_r5_independent_audit            RESULT: 23/23 PASS
```

★ 各輪 closeout 時**整體重跑**，逐項 RESULT 與本表一致。
★ 預註冊 FAIL 原樣保留 ＋ `-c` 校正（承 §F「無效才是正確」）：R1 1 條、R2 2 條、R3 6 條、R4 2 條、R5 5 條。
★ 規模: (root) 3｜data 33｜docs 32｜logs 41｜scripts 25｜verify 7

## 二、檔案清單（sha256 / bytes）

| 檔 | bytes | sha256 |
|:--|--:|:--|
| `01_problem_record.md` | 29063 | `d8d02946b5a73882…` |
| `SESSION_START.md` | 14967 | `73bfb8898af106c8…` |
| `data/01_atom_identity.json` | 377 | `b15f3951e4671071…` |
| `data/02_roles_graph.json` | 4524 | `07342eb50098f749…` |
| `data/03_gap1_degeneracy.json` | 762 | `e6244deaaf51daeb…` |
| `data/04_gap2_mu2_identity.json` | 908 | `051305f1ca7cedff…` |
| `data/05_gap3_completeness.json` | 4432 | `d01a2fac5f6de48e…` |
| `data/06_gap4_rigidity.json` | 2618 | `e23560786c4a4a00…` |
| `data/07_gap5_density.json` | 2380 | `a875623bf7c456bf…` |
| `data/08_independent_audit.json` | 949 | `37e01ad7dcb603e2…` |
| `data/09_r2_index_identity_and_routes.json` | 1404 | `9050776723908888…` |
| `data/10_r2_vmin_and_qed_sum.json` | 977 | `92ca5f343e54a019…` |
| `data/11_r2_two_param_rigidity.json` | 1761 | `4169dce6be226942…` |
| `data/12_r2_independent_audit.json` | 1413 | `ddf3954a007cd467…` |
| `data/13_r3_y_uniqueness.json` | 1228 | `c2a9be3ba92be23b…` |
| `data/14_r3_spectrum_family.json` | 1330 | `2b561d6bbb9475dd…` |
| `data/15_r3_polysemy_classification.json` | 3192 | `c7b5a3303d51c5ca…` |
| `data/16_r3_density_atom_pool.json` | 747 | `08c0188288c26968…` |
| `data/17_r3_independent_audit.json` | 1434 | `8f022fabe1c84100…` |
| `data/18_r4_chain_family.json` | 1577 | `8fc7bb1d999bfe68…` |
| `data/19_r4_mu2_support.json` | 1777 | `91509f0311888c17…` |
| `data/20_r4_hardtest_reaudit.json` | 1410 | `afb26134fc666e79…` |
| `data/21_r4_independent_audit.json` | 1445 | `24988ae140624e1e…` |
| `data/22_r5_endpoint_anatomy.json` | 1770 | `2b818f5169a2ac19…` |
| `data/23_r5_form_class.json` | 2064 | `3b323e3935191b5c…` |
| `data/23_r5_form_class.pre_correction.json` | 1731 | `de6ca77132c574cb…` |
| `data/24_r5_discrimination.json` | 7621 | `d6c099b2371f42db…` |
| `data/24_r5_discrimination.pre_rerun.json` | 7621 | `d6c099b2371f42db…` |
| `data/25_r5_independent_audit.json` | 3059 | `57ea2fc10987d823…` |
| `data/closeout_05_gap3_completeness.json` | 4218 | `d921b42db5358709…` |
| `data/closeout_08_independent_audit.json` | 758 | `f324dd616c94b555…` |
| `data/closeout_12_r2_independent_audit.json` | 1222 | `a9908ce154b7fce2…` |
| `data/closeout_17_r3_independent_audit.json` | 1243 | `a044e859a32b7d57…` |
| `data/closeout_21_r4_independent_audit.json` | 1254 | `1b3ae2d3904e903d…` |
| `data/closeout_25_r5_independent_audit.json` | 2868 | `1a4d7261cd5fae32…` |
| `docs/00_contract.md` | 7468 | `e3f18caac665984b…` |
| `docs/01_accounting_table.md` | 8294 | `2bbb0b3ff5b8aceb…` |
| `docs/02_gap1_degeneracy.md` | 4112 | `22f145cfcae0879e…` |
| `docs/03_gap2_mu2_identity.md` | 4966 | `d62578e2264f884f…` |
| `docs/04_gap4_rigidity.md` | 3522 | `1807507cfd14d9eb…` |
| `docs/05_gap5_density.md` | 4079 | `83b31a73a02253ae…` |
| `docs/06_r1_verdicts.md` | 4859 | `ec3701941bbf4c82…` |
| `docs/07_independent_audit.md` | 3874 | `21790e02d0a540b2…` |
| `docs/08_r2_contract.md` | 3718 | `cd2e8af286d3bcea…` |
| `docs/09_r2_gap2b_index_identity.md` | 4575 | `96237d850bafa09f…` |
| `docs/10_r2_vmin_closed_form.md` | 4231 | `f776e1e8648b1389…` |
| `docs/11_r2_two_param_rigidity.md` | 3654 | `1596e41692a18a76…` |
| `docs/12_r2_verdicts.md` | 2937 | `175f9fd6235a41df…` |
| `docs/13_r2_independent_audit.md` | 3602 | `f960823150910d97…` |
| `docs/14_r3_contract.md` | 5810 | `a1ee4af875654326…` |
| `docs/15_r3_y_uniqueness.md` | 3726 | `d423b6b98f882a66…` |
| `docs/16_r3_spectrum_family.md` | 3558 | `76020ecbe8bba73e…` |
| `docs/17_r3_polysemy_classification.md` | 3519 | `f9968bbf5dd122aa…` |
| `docs/18_r3_density_atom_pool.md` | 2276 | `e296500c5b8156ac…` |
| `docs/19_r3_verdicts.md` | 3506 | `8bc6e9dfb4f41723…` |
| `docs/20_r4_contract.md` | 5436 | `58aa031d84ef8174…` |
| `docs/21_r4_chain_family.md` | 3026 | `382c55f49b672451…` |
| `docs/22_r4_mu2_support.md` | 3072 | `747ef29afb2a2368…` |
| `docs/23_r4_hardtest_reaudit.md` | 3787 | `0f07c07259cc7463…` |
| `docs/24_r4_verdicts.md` | 2782 | `2943c5d55f84ef18…` |
| `docs/25_r4_residuals.md` | 2438 | `c730018a842ce2c8…` |
| `docs/26_r5_contract.md` | 5016 | `ab53e38fc7fce720…` |
| `docs/27_r5_endpoint_anatomy.md` | 2434 | `b0817fa833474dcb…` |
| `docs/28_r5_form_class.md` | 3574 | `2bc992cb3414a359…` |
| `docs/29_r5_discrimination.md` | 3026 | `41f2f167620540e2…` |
| `docs/30_r5_verdicts.md` | 4224 | `bca378d3c691cbdb…` |
| `docs/31_r5_residuals.md` | 15779 | `f66b307c936075d2…` |
| `final_result.md` | 15239 | `b84ad5ede833fedf…` |
| `logs/01_atom_identity.out` | 3975 | `2c2fc03d1cdedb62…` |
| `logs/02_roles_graph.out` | 4868 | `e7f1b0ce9a985210…` |
| `logs/03_gap1_degeneracy.out` | 2613 | `6fb8ca447b6219d9…` |
| `logs/04_gap2_mu2_identity.out` | 3571 | `8ea1a0fe1979da95…` |
| `logs/05_gap3_completeness.out` | 5301 | `f358bffaa0e5d9ae…` |
| `logs/06_gap4_rigidity.out` | 7627 | `1bf01016c46c8616…` |
| `logs/07_gap5_density.out` | 3708 | `2b8ae02b5febc18d…` |
| `logs/08_independent_audit.out` | 5961 | `e43c00e506a8cfe9…` |
| `logs/09_r2_index_identity_and_routes.out` | 4522 | `ae634027bb3aefc4…` |
| `logs/10_r2_vmin_and_qed_sum.out` | 2825 | `e3932a1702aeb9eb…` |
| `logs/11_r2_two_param_rigidity.out` | 3322 | `dc74aecd37acd422…` |
| `logs/12_r2_independent_audit.out` | 2064 | `8146421fa47963dc…` |
| `logs/13_r3_y_uniqueness.out` | 4790 | `ffc5f497f8f10228…` |
| `logs/14_r3_spectrum_family.out` | 4991 | `6000411268254db7…` |
| `logs/15_r3_polysemy_classification.out` | 3712 | `127204d3c4d2d74f…` |
| `logs/16_r3_density_atom_pool.out` | 3086 | `ace810c665bee8a7…` |
| `logs/17_r3_independent_audit.out` | 2603 | `78344cc5617cebe0…` |
| `logs/18_r4_chain_family.out` | 4030 | `1c9092cff26d6d07…` |
| `logs/19_r4_mu2_support.out` | 4048 | `50a73ec5fc6b9c88…` |
| `logs/20_r4_hardtest_reaudit.out` | 3540 | `5b54a9e59219f2cb…` |
| `logs/21_r4_independent_audit.out` | 2970 | `bde76695e59daf78…` |
| `logs/22_r5_endpoint_anatomy.out` | 2928 | `521e084cb385778d…` |
| `logs/23_r5_form_class.out` | 3101 | `ca33ea1e30ba04cf…` |
| `logs/23_r5_form_class.pre_correction.out` | 1915 | `ed60ea70f21e8565…` |
| `logs/24_r5_discrimination.out` | 3362 | `32e2aac0a352beb3…` |
| `logs/24_r5_discrimination.pre_rerun.json` | 7621 | `d6c099b2371f42db…` |
| `logs/24_r5_discrimination.pre_rerun.out` | 3362 | `32e2aac0a352beb3…` |
| `logs/25_r5_independent_audit.out` | 3396 | `5cad993d4d4955ef…` |
| `logs/chain_01_path_hygiene.out` | 698 | `2188e94bae36e713…` |
| `logs/chain_02_numeric_producer.out` | 1181 | `b0f7ed2fc63c053a…` |
| `logs/chain_03_trail_integrity.out` | 724 | `b5ab6b6a0a5a413a…` |
| `logs/chain_04_session_provenance.out` | 9114 | `4637afbd9182f409…` |
| `logs/chain_05_full_rerun.out` | 1776 | `bc15cc4455bc1556…` |
| `logs/closeout_05_gap3_completeness.out` | 5153 | `5080dfd93defc728…` |
| `logs/closeout_08_independent_audit.out` | 9720 | `9da294d015cfd97b…` |
| `logs/closeout_12_r2_independent_audit.out` | 3724 | `39575df455e41de8…` |
| `logs/closeout_17_r3_independent_audit.out` | 3508 | `05530defed85299c…` |
| `logs/closeout_21_r4_independent_audit.out` | 2307 | `839e65fca50724c7…` |
| `logs/closeout_25_r5_independent_audit.out` | 3148 | `5fff405aa9578a40…` |
| `logs/legacy_24_pre_c2_aborted.out` | 2144 | `fcac1c90bdcfd33c…` |
| `logs/legacy_diag24_c6_signature.out` | 4353 | `f7518b7350339572…` |
| `scripts/01_atom_identity.py` | 9343 | `bbe8563cd6f3dca6…` |
| `scripts/02_roles_graph.py` | 9930 | `0da2cf78f5080a0e…` |
| `scripts/03_gap1_degeneracy.py` | 5147 | `3f105db40f5f14ce…` |
| `scripts/04_gap2_mu2_identity.py` | 7346 | `791f18994674c1b5…` |
| `scripts/05_gap3_completeness.py` | 13122 | `021d6317e62ef77c…` |
| `scripts/06_gap4_rigidity.py` | 8672 | `317d33f61797559e…` |
| `scripts/07_gap5_density.py` | 8550 | `2d8e42eddf9e564c…` |
| `scripts/08_independent_audit.py` | 11889 | `e1982de20184178e…` |
| `scripts/09_r2_index_identity_and_routes.py` | 8849 | `5b47d107d2de9a18…` |
| `scripts/10_r2_vmin_and_qed_sum.py` | 6229 | `53ef6648d7c3f4c4…` |
| `scripts/11_r2_two_param_rigidity.py` | 9928 | `31c13bc80048db86…` |
| `scripts/12_r2_independent_audit.py` | 10988 | `584718a6c5ba8d0e…` |
| `scripts/13_r3_y_uniqueness.py` | 9672 | `fef3aac715758a0e…` |
| `scripts/14_r3_spectrum_family.py` | 8527 | `ad1ccc1e0b879dc2…` |
| `scripts/15_r3_polysemy_classification.py` | 9045 | `4bee5ab57de585a6…` |
| `scripts/16_r3_density_atom_pool.py` | 4529 | `7a9fe63fadf5ede7…` |
| `scripts/17_r3_independent_audit.py` | 9901 | `2d64185a5605a03a…` |
| `scripts/18_r4_chain_family.py` | 4893 | `1d58a29a148e7206…` |
| `scripts/19_r4_mu2_support.py` | 6383 | `e665ef88fea7509d…` |
| `scripts/20_r4_hardtest_reaudit.py` | 7621 | `1ab0e0317121038f…` |
| `scripts/21_r4_independent_audit.py` | 9601 | `eb45b1c71f7149a5…` |
| `scripts/22_r5_endpoint_anatomy.py` | 5230 | `0dea6f5f8f101f02…` |
| `scripts/23_r5_form_class.py` | 7146 | `e814c3643c4aa2e3…` |
| `scripts/24_r5_discrimination.py` | 9283 | `dff305b252ec4ed2…` |
| `scripts/25_r5_independent_audit.py` | 16187 | `83b3327ddb4009f4…` |
| `verify/build_manifest.py` | 7461 | `a4ee909b17e6b474…` |
| `verify/chain_session_provenance.py` | 3635 | `96010167c8353418…` |
| `verify/diag24_c6_signature.py` | 2461 | `84dfbc35b14e8b2d…` |
| `verify/run_full_chain.sh` | 2294 | `3fc9ef7610b2f736…` |
| `verify/third_route_arbiter.json` | 1159 | `bd0a681808c7ae21…` |
| `verify/third_route_arbiter.out` | 1442 | `87433e2451732668…` |
| `verify/third_route_arbiter.py` | 4416 | `5086ffb9935a36ed…` |

## 三、重建指令

```bash
cd open_problems_fresh/o229_mu2_b4_particle_accounting
for i in $(seq -w 1 25); do /usr/bin/python3 scripts/${i}_*.py; done
# 逐腳本 RESULT 應與本檔 §一 一致；08/12/17/21/25 為獨立核對器（唔 import 受核腳本）
/usr/bin/python3 verify/third_route_arbiter.py   # 第三路線仲裁（唔計入 scripts 名單）
```

## 四、核心數字
- R1 `e3f18caac665984b…` ／ R2 `cd2e8af286d3bcea…` ／ R3 `a1ee4af875654326…` ／ R4 `58aa031d84ef8174…` ／ R5 `ab53e38fc7fce720…`
- R1 **233/234**（8 引擎）
- R2 **42/44**（3 引擎）＋核對 21/21
- R3 **59/65**（4 引擎）＋核對 18/18
- R4 **33/35**（3 引擎）＋核對 18/18
- R5 **24/29**（3 引擎）＋核對 23/23
- R5 核心: 端點鎖三項解剖 `137 = C(B²,2)+B²+1 = 120+16+1` ⟹ 「半結構」（120 之群階讀法僅在 16 態不可分下被排除）｜
  函數正則類 112 項 / 234,136 形式 ⟹ 命中 270、含 B 228 條**全部**以 `B = 4` 為唯一正整數解（過定）｜
  值層零判別力: `express(137) = 270` 排 34/34、同量級池 `p = 0.6238`、`max lock = 737 @ 16`｜
  `-c6`: 25 初版 `2^B` 項漏乘 `den`（誤報 227/729）⟹ 更正後 25 = 23/23，第三路線 0 差異
- R4 核心: 鏈長族 ℳ = {8,16,44,88,176,352,704} = {2^a·11^b} ⟹ 整數譜值集恰 {0, μ², B}；μ² 支撐秩 1、外部 0
- R3 核心: 異常泛函恆等零 ⟹ 解集維數 2；譜整數性 ⟺ 階 ∈ {1,2,3,4,6}；端點鎖 4/34 = 11.76%
- MC null（R1）: N = 10⁷, seed 229, 命中 13 ⟹ 1.30e-06（R4 精確校正 8/4885673）

