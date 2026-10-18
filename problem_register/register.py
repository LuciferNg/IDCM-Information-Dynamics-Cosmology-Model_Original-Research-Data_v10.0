#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""problem_register - append-only lifecycle register for IDCM open problems.

Records ONLY lifecycle metadata:
    registration / ownership / closure / negative result / post-hoc / progress
NEVER results.  NEVER derivation content.  Pointers (ref) only.

Key = pid:  'O213'      O-series problem
            'bbn/he3'   problem inside a theme folder (no O number)

Storage:
    register.jsonl   system of record - append-only text, git-mergeable
    register.sqlite  generated query index - gitignored, fully rebuildable
    clues.sqlite     derived clue index over the docs - regenerable
    REGISTER.md      generated human mirror - read-only

Run from anywhere; paths are resolved relative to this file.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OPF = os.path.join(REPO, "open_problems_fresh")
JSONL = os.path.join(HERE, "register.jsonl")
SQLITE = os.path.join(HERE, "register.sqlite")
MIRROR = os.path.join(HERE, "REGISTER.md")
CLUES = os.path.join(HERE, "clues.sqlite")
SCHEMA = os.path.join(HERE, "schema.sql")

STATES = ("registered", "open", "partial", "closed", "merged", "retracted", "tombstone")
VERDICTS = ("closed", "negative", "partial", "falsified")
EMOJI = {"\U0001F7E2": "closed", "\U0001F7E1": "partial", "\U0001F534": "open",
         "\U0001F7E0": "partial", "\U0001F4C4": "registered", "\U0001F500": "merged"}
THEME_DIRS = ("bbn", "cmb_cl", "cmb_cold_spot", "h0_tension", "kchain_number_field",
              "ktree_structure", "little_red_dots", "neutrino_p6_mode", "p7_reionization",
              "ckm_reconstruction", "crystal_stress", "data_gated_unlock",
              "uhecrs", "beat_periodic_table", "global_routing_table",
              "early_derivations",
              # 2026-10-14: cross-version register (v1.0–v9.0, v11.0) + v11 problem m1
              "m1", "v1.0", "v2.0", "v3.0", "v4.0", "v5.0", "v6.0", "v7.0", "v8.0", "v9.0", "v11.0")

# 2026-10-05: non-O problem folders moved from open_problems_fresh/ to main_problems/
# with p-index prefixes (P1-P5 numbers reused from the retired P universe; P6/P7 kept).
# pid keeps the legacy theme name (bbn/he3 etc); the FOLDER is resolved via theme_dir().
MAIN = os.path.join(REPO, "main_problems")
THEME_MOVE = {
    "bbn": "p1_bbn", "ckm_reconstruction": "p2_ckm_reconstruction",
    "cmb_cl": "p3_cmb_cl", "cmb_cold_spot": "p4_cmb_cold_spot",
    "crystal_stress": "p5_crystal_stress", "neutrino_p6_mode": "p6_neutrino",
    "p7_reionization": "p7_reionization", "h0_tension": "p8_h0_tension",
    "kchain_number_field": "p9_kchain_number_field", "ktree_structure": "p10_ktree_structure",
    "little_red_dots": "p11_little_red_dots", "uhecrs": "p12_uhecrs",
    "beat_periodic_table": "p13_beat_periodic_table", "global_routing_table": "p14_global_routing_table",
    "early_derivations": "p15_early_derivations",
    # 2026-10-14: cross-version register —— 版本 repo 喺 v10 repo 外面, 用絕對路徑 (join 唔識返上一層)
    "m1": "/home/wsl/Projects/IDCM-Original/IDCM-v11.0--Reality-Architecture/main_problems/m1_mass_file_schema",
    "v1.0": "/home/wsl/Projects/IDCM-Original/IDM-v1.0--Information-Dynamics-Cosmology",
    "v2.0": "/home/wsl/Projects/IDCM-Original/IDM-v2.0--Consistency-Importance-Weight",
    "v3.0": "/home/wsl/Projects/IDCM-Original/IDM-v3.0--Domain-Framework",
    "v4.0": "/home/wsl/Projects/IDCM-Original/IDM-v4.0--Consistency-Field-Applied-Science",
    "v5.0": "/home/wsl/Projects/IDCM-Original/IDM-v5.0--Recursive-Structural-Cosmology",
    "v6.0": "/home/wsl/Projects/IDCM-Original/IDCM-v6.0--Information-Dynamics-Cosmology-Model",
    "v7.0": "/home/wsl/Projects/IDCM-Original/IDCM-v7.0--Information-Dynamics-Cosmology-Model",
    "v8.0": "/home/wsl/Projects/IDCM-Original/IDCM-v8.0--Compiled-Cosmology",
    "v9.0": "/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice",
    "v11.0": "/home/wsl/Projects/IDCM-Original/IDCM-v11.0--Reality-Architecture",
}
MOVED_SRC = {os.path.join(OPF, k): os.path.join(MAIN, v) for k, v in THEME_MOVE.items()}

# 2026-10-08 O144 收據 note 之 ref 筆誤: 目錄 slug 寫成 o243_triple_vacuum_phase_transition，
# 實際係 o243_phase_transition_no_go。JSONL 唔改（append-only），喺翻譯層補回。
O243_SLUG_FIX = os.path.join(OPF, "o243_triple_vacuum_phase_transition")
O243_SLUG_FIX_TO = os.path.join(OPF, "o243_phase_transition_no_go")

# 2026-10-08 O144/P3 預註冊事件 ref 之檔名筆誤: 猜名 docs/10_link_energy_flux_tube.md，
# 實際 docs/10_su3_connection_functional_sigma.md。同樣翻譯層補回。
P3_PRE_REG_REF = os.path.join(OPF, "o144_boson_identity/docs/10_link_energy_flux_tube.md")
P3_PRE_REG_REF_TO = os.path.join(OPF, "o144_boson_identity/docs/10_su3_connection_functional_sigma.md")

# 2026-10-06 修正第 ② 類 REF-MISSING（O85 rename）:
# O85 於 2026-10-05「由零重建」（用戶裁定全刪舊 docs 由零推導），舊檔名已不存在；
# register 舊 event 的 ref 仍指向舊名。JSONL 歷史 event 唔改（append-only），
# 呢度提供舊名 → 新名翻譯層，令 check 可以 materialise 到現存的檔。
# 逐檔核對內容對應：每個舊檔按 register note 主題 map 到新 O85 docs 中最相關一份
# （唔係 1:1 rename，係內容重排後嘅最貼近檔）。
O85_RENAME = {
    # 舊 O85 docs（2026-10-05 已刪）→ 新 O85 docs（內容最相關）
    os.path.join(OPF, "o85_su12_breaking/docs/04_inbound_handoff_processing.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/01_breaking_path_classification.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/05_chain_reconstruction.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/03_breaking_chain.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/06_chain_contamination_ledger.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/04_mass_spectrum.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/08_remaining_gaps.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/02_q6_global_vs_gauge.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/09_eigenvalue_assignment.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/09_u1_scale_ladder.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/10_nine_modes_origin.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/09_u1_scale_ladder.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/12_ring_label_equivariance.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/17_singlet_mode_interpretation.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/13_residuals_sweep.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/06_scale.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/03_sm_feynman_rules.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/05_fermion_reps.md"),
    os.path.join(OPF, "o85_su12_breaking/docs/17_o88_framework_audit.md"):
        os.path.join(OPF, "o85_su12_breaking/docs/05_fermion_reps.md"),
}

# 2026-10-07 修正第 ③ 類 REF-MISSING（O206 round10-15 遷移 O233）:
# O206 第十至十五輪 (docs/33-43, scripts/29-39) 於 2026-10-06 經調律者裁決 git mv 轉移去
# O233 (o233_c_f_identity)，docs 編號重排 (33→01, 36→04, ..., 43→11)。
# register 舊 event 的 ref 仍指向 o206 舊路徑；JSONL 歷史事件唔改（append-only），
# 呢度提供舊路徑 → O233 現存路徑翻譯層。逐檔按 round 主題 1:1 對應。
O206_TO_O233 = {
    os.path.join(OPF, "o206_per_mode_frequency/docs/33_round10_conflict_adjudication.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/01_round10_conflict_adjudication.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/36_round11_unified_generator.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/04_round11_unified_generator.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/37_round11b_cf_sawtooth.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/05_round11b_cf_sawtooth.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/38_round11c_sawtooth_z2.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/06_round11c_sawtooth_z2.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/39_round11d_z2_three_tests.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/07_round11d_z2_three_tests.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/40_round12_joint_power_parity.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/08_round12_joint_power_parity.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/41_round13_flow_identity.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/09_round13_flow_identity.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/42_round14_lepton_slot.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/10_round14_lepton_slot.md"),
    os.path.join(OPF, "o206_per_mode_frequency/docs/43_round15_charge_residue_corrected.md"):
        os.path.join(OPF, "o233_c_f_identity/docs/11_round15_charge_residue_corrected.md"),
}


# 2026-10-07 修正 O237 簡寫 ref（Session 20261007 用咗 "o237/docs/..." 短路徑）:
# register 舊 event 的 ref 仍指向簡寫；JSONL 歷史事件唔改（append-only），
# 呢度提供簡寫 → 現存路徑翻譯層（prefix map；"o237/docs/02-04" 係 range 注，指 01_problem_record）。
O237_SHORTHAND_PREFIX = os.path.join(REPO, "o237")
O237_SHORTHAND_DIR = os.path.join(OPF, "o237_mass_roadmap_kchain_to_perception")
O237_SHORTHAND_RANGE = os.path.join(REPO, "o237/docs/02-04")

# 2026-10-09 修正第 ④ 類 REF-MISSING（P1 BBN session 重驗時發現，8 個）:
# ① O225/R2 三個 handed_off 事件 ref 寫漏 `open_problems_fresh/` 前綴
#    （"o222_qm_evaluation_semantics/..." 喺 repo-root 相對解析下報 MISSING，
#    檔案真實存在於 OPF/o222_qm_evaluation_semantics/）；
# ② O229 兩個 progress 事件 ref 寫成目錄名（"o229_mu2_b4_particle_accounting"
#    冇檔名）— 指向目錄嘅 01_problem_record.md；
# ③ crystal_stress / little_red_dots / uhecrs 三個 registered 事件 ref 指
#    main_problems/pNN/01_problem_record.md，但 migration 後指名檔移入
#    docs/（p5）、records/（p11），p12 用 records/03_uhecrs_record.md。
# JSONL 歷史事件唔改（append-only），呢度提供舊 ref → 現存路徑翻譯層。
# 逐條核對真實存在先加入；同 O85_RENAME/O206_TO_O233 先例一致。
REF_PATH_FIX = {
    os.path.join(REPO, "o222_qm_evaluation_semantics/docs/40_r26_g1g8.md"):
        os.path.join(OPF, "o222_qm_evaluation_semantics/docs/40_r26_g1g8.md"),
    os.path.join(REPO, "o222_qm_evaluation_semantics/scripts/70_r27d_nogo.py"):
        os.path.join(OPF, "o222_qm_evaluation_semantics/scripts/70_r27d_nogo.py"),
    os.path.join(REPO, "o229_mu2_b4_particle_accounting"):
        os.path.join(OPF, "o229_mu2_b4_particle_accounting/01_problem_record.md"),
    os.path.join(MAIN, "p5_crystal_stress/docs/01_problem_record.md"):
        os.path.join(MAIN, "p5_crystal_stress/01_problem_record.md"),
    os.path.join(MAIN, "p11_little_red_dots/01_problem_record.md"):
        os.path.join(MAIN, "p11_little_red_dots/records/01_problem_record.md"),
    os.path.join(MAIN, "p12_uhecrs/01_problem_record.md"):
        os.path.join(MAIN, "p12_uhecrs/records/03_uhecrs_record.md"),
}


# 2026-10-12 修正 O247 類⑦ REF-MISSING: registered 事件 ref 嘅目錄 slug 寫漏
# `o247_` 前綴（"open_problems_fresh/natural_contamination_ladder/..." vs 實際
# o247_natural_contamination_ladder）。JSONL 歷史事件唔改（append-only），
# 翻譯層補回——同 O144 O243_SLUG_FIX 先例一致；只影響 O247 自己嘅 ref 解析。
O247_SLUG_FIX = {
    os.path.join(OPF, "natural_contamination_ladder/01_problem_record.md"):
        os.path.join(OPF, "o247_natural_contamination_ladder/01_problem_record.md"),
}


# 2026-10-18 修正 P10 REF-MISSING: registered 事件 ref 指
# main_problems/p10_ktree_structure/01_ktree_definition.py，但 P10 於 2026-10-18
# 結構重組（跟 O-series 慣例：root 只留 README/final_result/01_problem_record/
# SESSION_START；*.md→docs/、*.py→scripts/）後該檔已移入 scripts/。
# JSONL 歷史事件唔改（append-only），翻譯層補回——同 REF_PATH_FIX 先例一致。
P10_REF_FIX = {
    os.path.join(MAIN, "p10_ktree_structure/01_ktree_definition.py"):
        os.path.join(MAIN, "p10_ktree_structure/scripts/01_ktree_definition.py"),
}

# 2026-10-18 P12 結構重整 (records→docs, root 建齊四檔): 註冊時嘅 note event ref
# 指 records/03_uhecrs_record.md，該檔已移入 docs/。JSONL 歷史事件唔改
# （append-only），翻譯層補回——同 P10_REF_FIX 先例一致；只影響 uhecrs 自己 ref 解析。
P12_REF_FIX = {
    os.path.join(MAIN, "p12_uhecrs/records/03_uhecrs_record.md"):
        os.path.join(MAIN, "p12_uhecrs/docs/03_uhecrs_record.md"),
    os.path.join(MAIN, "p12_uhecrs/records/05_psz1_vacuum_result.md"):
        os.path.join(MAIN, "p12_uhecrs/docs/05_psz1_vacuum_result.md"),
}

# 2026-10-18 O168 越界產物撤回 (調律者裁決「register 發還 O38 重做」): 09:50 handoff
# 事件嘅 ref 指 docs/29_m0_scale_blueprint.md，該藍圖已隨 `git revert f306a18` + `git rm`
# 撤回刪除 ⟹ 永久 REF-MISSING。JSONL 歷史事件唔改（append-only），翻譯層指向代表檔
# docs/28_phase_closeout.md（載有 10-16 裁決註記）；同 REF_PATH_FIX/O247_SLUG_FIX 先例一致。
O168_RETRACT_FIX = {
    os.path.join(OPF, "o168_g_last_input/docs/29_m0_scale_blueprint.md"):
        os.path.join(OPF, "o168_g_last_input/docs/28_phase_closeout.md"),
}


def theme_dir(name):
    """Resolve a theme folder by its legacy pid first-segment (name).
    Returns the post-migration main_problems/ path when moved, else open_problems_fresh/."""
    if name in THEME_MOVE:
        p = os.path.join(MAIN, THEME_MOVE[name])
        if os.path.isdir(p):
            return p
    return os.path.join(OPF, name)


def resolve_ref(fp):
    """Follow the 2026-10-05 theme migration for ref checks: a ref that pointed at
    open_problems_fresh/<theme>/... is translated to main_problems/pNN_<theme>/...
    Also translate O85 pre-rebuild doc names (O85_RENAME, 2026-10-06) and
    O206 round10-15 docs migrated to O233 (O206_TO_O233, 2026-10-07).
    Historical jsonl events are never rewritten (append-only); this translation is
    applied only when materialising the check target."""
    if os.path.exists(fp):
        return fp
    new = O85_RENAME.get(fp)
    if new and os.path.exists(new):
        return new
    new = O206_TO_O233.get(fp)
    if new and os.path.exists(new):
        return new
    if O237_SHORTHAND_RANGE and fp == O237_SHORTHAND_RANGE:
        return os.path.join(O237_SHORTHAND_DIR, "01_problem_record.md")
    if O237_SHORTHAND_PREFIX and fp.startswith(O237_SHORTHAND_PREFIX + os.sep):
        cand = O237_SHORTHAND_DIR + fp[len(O237_SHORTHAND_PREFIX):]
        if os.path.exists(cand):
            return cand
    if fp.startswith(O243_SLUG_FIX + os.sep):
        cand = O243_SLUG_FIX_TO + fp[len(O243_SLUG_FIX):]
        if os.path.exists(cand):
            return cand
    if fp == P3_PRE_REG_REF and os.path.exists(P3_PRE_REG_REF_TO):
        return P3_PRE_REG_REF_TO
    new = REF_PATH_FIX.get(fp)
    if new and os.path.exists(new):
        return new
    # 2026-10-12 O247 類⑦: registered 事件 ref slug 寫漏 oNNN_ 前綴 →
    # 翻譯層（上方 O247_SLUG_FIX）；only-for-O247，唔做全庫猜測。
    new = O247_SLUG_FIX.get(fp)
    if new and os.path.exists(new):
        return new
    # 2026-10-18 P10 結構重組 (md→docs, py→scripts) 翻譯層
    new = P10_REF_FIX.get(fp)
    if new and os.path.exists(new):
        return new
    # 2026-10-18 P12 結構重整 (records→docs) 翻譯層
    new = P12_REF_FIX.get(fp)
    if new and os.path.exists(new):
        return new
    # 2026-10-18 O168 越界藍圖撤回 (docs/29 已刪) 翻譯層
    new = O168_RETRACT_FIX.get(fp)
    if new and os.path.exists(new):
        return new
    for src, dst in MOVED_SRC.items():
        if fp.startswith(src + os.sep):
            cand = dst + fp[len(src):]
            if os.path.exists(cand):
                return cand
    return fp


def _complete_num_ref(base_dir, seg):
    """2026-10-08 類⑥延伸: ref 寫成 'docs/NN' 或 'scripts/NN'（數字無後綴）——
    若 base_dir 下該目錄存在**唯一** 'NN_*' 檔則補齊；0 或 >1 命中 → None（唔猜）。
    e.g. O144 note ref 'o144_boson_identity/docs/23' → docs/23_su12_breaking_mechanism.md"""
    parts = seg.replace(os.sep, "/").split("/")
    if len(parts) < 2 or parts[-2] not in ("docs", "scripts", "data"):
        return None
    if not re.fullmatch(r"\d{1,3}", parts[-1]):
        return None
    sub = os.path.join(base_dir, *parts[:-1])
    n = int(parts[-1])
    cands = [p for p in glob.glob(os.path.join(sub, "*"))
             if os.path.isfile(p) and os.path.basename(p).startswith(f"{n:02d}_")]
    return cands[0] if len(cands) == 1 else None


def check_ref_path(pid, seg, ddirs):
    """Resolve one ref segment to a real path, or None if genuinely missing.
    Order: absolute/REPO-join -> resolve_ref (theme migration / O85 rename) ->
    2026-10-07 類① fallback (bare O-dir-relative ref written without its oNNN
    prefix): try this pid's own O dir + seg, then a repo-wide unique */seg hit.
    2026-10-08 類⑥ fallback: 'docs/NN' 數字無後綴 → 該目錄唯一 NN_* 檔補齊。
    A repo-wide match is accepted ONLY when unique (otherwise the intent is
    ambiguous and the ref stays MISSING - never guess)."""
    fp = seg if os.path.isabs(seg) else os.path.join(REPO, seg)
    fp = resolve_ref(fp)
    if os.path.exists(fp):
        return fp
    fp2 = _complete_num_ref(REPO, seg)
    if fp2:
        return fp2
    n0 = num_of(pid)
    if n0 is None and pid and "/" in pid:
        # sub-item (e.g. O216/delta-n-color): resolve against the parent O dir
        head = pid.split("/")[0]
        if re.fullmatch(r"O\d+", head):
            n0 = num_of(head)
    if n0 is not None:
        for d in ddirs.get(n0, []):
            cand = os.path.join(d, seg)
            if os.path.exists(cand):
                return cand
            # 2026-10-08 類① 延伸: ref 帶 oNNN 目錄前綴但缺 open_problems_fresh/（
            # e.g. "o216_delta_n_color/docs/02…"）→ 剝走本 pid 自己 O dir slug 前綴再試。
            # 只接受本 pid 自己目錄（唔做全庫猜測）；同類 O144/O225 等留待其 owner 處理。
            slug = os.path.basename(d.rstrip(os.sep))
            if seg.startswith(slug + os.sep):
                stripped = seg[len(slug) + 1:]
                cand2 = os.path.join(d, stripped)
                if os.path.exists(cand2):
                    return cand2
                cand3 = _complete_num_ref(d, stripped)   # 2026-10-08 類⑥ (O144 docs/23)
                if cand3:
                    return cand3
            # 2026-10-09 類① 延伸 (O148): ref 帶 oNNN 短前綴（'o148/docs/17'）而唔係完整
            # slug（'o148_dual_scale_vacuum_budget/docs/17'）—— 剝走 'oNNN' 再對本 pid
            # 目錄試，同類 c/oN 短名寫法（'O148/...'）一併處理。只做本 pid 自己（唔猜）。
            short = f"o{n0}"
            if seg.startswith(short + os.sep):
                stripped = seg[len(short) + 1:]
                cand2 = os.path.join(d, stripped)
                if os.path.exists(cand2):
                    return cand2
                cand3 = _complete_num_ref(d, stripped)
                if cand3:
                    return cand3
            cand4 = _complete_num_ref(d, seg)            # 2026-10-08 類⑥ (無 slug 前綴)
            if cand4:
                return cand4
    hits = glob.glob(os.path.join(OPF, "*", seg)) + glob.glob(os.path.join(MAIN, "*", seg))
    if len(hits) == 1:
        return hits[0]
    # 2026-10-10: ref already carries the O-dir slug but not the open_problems_fresh/
    # prefix (e.g. "o221_low_energy_continuum/docs/31_.." from a note on another pid):
    # the slug-relative path is OPF/<seg> verbatim (additive; unique by construction).
    cand_op = os.path.join(OPF, seg)
    if os.path.exists(cand_op):
        return cand_op
    return None


# ---------------------------------------------------------------- utilities
def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def session_id():
    return os.environ.get("HERMES_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or "-"


def num_of(pid):
    m = re.fullmatch(r"O(\d+)", pid or "")
    return int(m.group(1)) if m else None


def connect(create=True):
    if not create and not os.path.exists(SQLITE):
        sys.exit("no register.sqlite yet - run: register.py rebuild")
    con = sqlite3.connect(SQLITE)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout = 5000")
    if create:
        with open(SCHEMA, encoding="utf-8") as fh:
            con.executescript(fh.read())
    return con


def read_jsonl():
    if not os.path.exists(JSONL):
        return []
    out = []
    with open(JSONL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(rec):
    with open(JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def chain_hash(rec, prev):
    blob = json.dumps({k: v for k, v in rec.items() if k != "hash"},
                      ensure_ascii=False, sort_keys=True) + "|" + (prev or "")
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def clip(s, n):
    if s is None:
        return None
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def status_of_emoji(text):
    if not text:
        return None
    for e, k in EMOJI.items():
        if e in text:
            return k
    return None


def field(txt, label):
    if not txt:
        return None
    m = re.search(r"^>?\s*\*\*" + label + r"\*\*\s*[:：]\s*(.+)$", txt, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^" + label + r"\s*[:：]\s*(.+)$", txt, re.M)
    return m.group(1).strip() if m else None


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


TEMPLATES = os.path.join(OPF, "_templates")
BLOCK_RE = re.compile(r"<!--\s*registry\s*\n(.*?)\n\s*-->", re.S)


def parse_block(txt):
    """Parse the <!-- registry ... --> machine block. Returns dict or None."""
    if not txt:
        return None
    m = BLOCK_RE.search(txt)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        line = line.split("#")[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out or None


def iter_docs():
    """Yield (pid_guess, path, kind) for every problem_record / SESSION_START."""
    for d in sorted(glob.glob(os.path.join(OPF, "o*"))):
        if not os.path.isdir(d):
            continue
        for nm, kind in (("01_problem_record.md", "record"),
                         ("SESSION_START.md", "session"),
                         ("final_result.md", "result")):
            p = os.path.join(d, nm)
            if os.path.exists(p):
                yield os.path.basename(d), p, kind
    for t in sorted(listdir_theme_dirs()):
        td = theme_dir(t)
        if not os.path.isdir(td):
            continue
        for root, dirs, names in os.walk(td):
            dirs[:] = [x for x in dirs if x not in ("data", "docs", "__pycache__")]
            for nm in names:
                if nm in ("01_problem_record.md", "SESSION_START.md", "final_result.md"):
                    yield t, os.path.join(root, nm), "theme"


def listdir_theme_dirs():
    """All first-segment theme names: open_problems_fresh leftovers + moved main_problems."""
    out = []
    for t in sorted(os.listdir(OPF)):
        if os.path.isdir(os.path.join(OPF, t)) and t not in ("data", "_templates") \
                and not re.match(r"^o\d+_", t):
            out.append(t)
    for name in THEME_MOVE:
        if os.path.isdir(theme_dir(name)) and name not in out:
            out.append(name)
    return out


def dirs_by_num():
    out = {}
    for d in sorted(glob.glob(os.path.join(OPF, "o*"))):
        b = os.path.basename(d.rstrip("/"))
        m = re.match(r"o(\d+)_", b)
        if m and os.path.isdir(d):
            out.setdefault(int(m.group(1)), []).append(d.rstrip("/"))
    return out


def readme_nums():
    txt = read(os.path.join(OPF, "README.md")) or ""
    found = {}
    for line in txt.splitlines():
        if not line.startswith("| **O"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        m = re.match(r"\*\*O(\d+)\*\*", cells[1])
        if m:
            found[int(m.group(1))] = {"status": cells[3], "summary": cells[4]}
    return found


def _pid(a):
    """Resolve the target pid from CLI args (--pid wins, --num is shorthand)."""
    p = getattr(a, "pid", None)
    if p:
        return p
    n = getattr(a, "num", None)
    if n is not None:
        return "O%d" % n
    sys.exit("need --pid (e.g. O213 / bbn/he3) or --num N")


# ---------------------------------------------------------------- event write
EV_COLS = ("ts", "pid", "num", "kind", "verdict", "owner", "slug", "title", "keywords",
           "state", "state_source", "target_pid", "ref", "note", "session", "source",
           "prev_hash", "hash")


def insert_event(con, r):
    con.execute(
        "INSERT INTO event (" + ",".join(EV_COLS) + ") VALUES ("
        + ",".join(":" + c for c in EV_COLS) + ")",
        {c: r.get(c) for c in EV_COLS})


def record(con, kind, pid=None, **kw):
    rows = con.execute("SELECT hash FROM event ORDER BY id DESC LIMIT 1").fetchone()
    prev = rows["hash"] if rows else None
    rec = {
        "ts": now_iso(), "pid": pid, "num": kw.get("num", num_of(pid)), "kind": kind,
        "verdict": kw.get("verdict"), "owner": kw.get("owner"),
        "target_pid": kw.get("target_pid"), "ref": kw.get("ref"),
        "slug": kw.get("slug"), "title": clip(kw.get("title"), 120),
        "keywords": clip(kw.get("keywords"), 200), "state": kw.get("state"),
        "state_source": kw.get("state_source"),
        "note": clip(kw.get("note"), 200), "session": kw.get("session") or session_id(),
        "source": kw.get("source") or "cli", "prev_hash": prev,
    }
    rec["hash"] = chain_hash(rec, prev)
    append_jsonl(rec)
    insert_event(con, rec)
    con.commit()
    return rec


def replay(con, r):
    """Apply one event to the o_problem projection.

    The log is the only source of truth: sqlite is a pure function of it, so
    `rebuild` reproduces o_problem exactly.  Append-only, never destructive.
    """
    pid = r.get("pid")
    if r.get("kind") == "alias":
        con.execute("INSERT OR REPLACE INTO alias (scope,label,pid,note,ts) VALUES (?,?,?,?,?)",
                    (r.get("owner"), r.get("slug"), pid, r.get("note"), r.get("ts")))
        return
    if r.get("kind") == "collision":
        con.execute("INSERT OR REPLACE INTO collision (num,dirs,note,ts) VALUES (?,?,?,?)",
                    (r.get("num"), r.get("slug"), r.get("note"), r.get("ts")))
        return
    if pid is None:
        return
    if r.get("kind") == "tombstone":
        num = r.get("num")
        if num is not None:
            con.execute("INSERT OR IGNORE INTO reserved_num (num,reason,ts) VALUES (?,?,?)",
                        (num, r.get("note") or "tombstone", r.get("ts")))
    if r.get("kind") == "unreserve":
        # 調律者明示之墓碑編號重用（O-series management §編號碰撞: 用戶明示 = 特例）。
        # Append-only: 保留原本 tombstone 事件，只追加一次 unreserve 取消保留。
        num = r.get("num")
        if num is not None:
            con.execute("DELETE FROM reserved_num WHERE num=?", (num,))
    if r.get("kind") == "posthoc":
        cur = con.execute("SELECT flags FROM o_problem WHERE pid=?", (pid,)).fetchone()
        if cur is not None:
            have = {x for x in (cur["flags"] or "").split(",") if x}
            have.add("posthoc")
            con.execute("UPDATE o_problem SET flags=? WHERE pid=?",
                        (",".join(sorted(have)), pid))
        return
    if con.execute("SELECT 1 FROM o_problem WHERE pid=?", (pid,)).fetchone() is None:
        if not (r.get("slug") or r.get("title")):
            return
        con.execute(
            "INSERT INTO o_problem (pid,num,slug,title,keywords,owner,state,verdict,"
            "created_ts,backfilled,state_source) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (pid, r.get("num"), r.get("slug") or pid, r.get("title") or "(no title)",
             r.get("keywords"), r.get("owner"), r.get("state") or "registered",
             r.get("verdict"), r.get("ts"),
             1 if (r.get("source") or "").startswith("backfill") else 0,
             r.get("state_source")))
    sets, vals = [], []
    # handed_off: the event's `owner` names the RECEIVER (display only) -- it must NOT
    # overwrite the source problem's owner, otherwise O222 ends up labelled as owned by
    # the O it sent a correction note to.
    owner_transfer = r.get("kind") not in ("handed_off",)
    for k in ("state", "verdict", "owner", "slug", "title", "keywords", "state_source"):
        if k == "owner" and not owner_transfer:
            continue
        if r.get(k) is not None:
            sets.append(k + "=?")
            vals.append(r[k])
    if sets:
        vals.append(pid)
        con.execute("UPDATE o_problem SET " + ",".join(sets) + " WHERE pid=?", vals)


# ---------------------------------------------------------------- commands
def _need(con, pid):
    if not con.execute("SELECT 1 FROM o_problem WHERE pid=?", (pid,)).fetchone():
        sys.exit("%s not registered - run: register.py register --pid %s ..." % (pid, pid))


def _slugify(num, title):
    s = re.sub(r"[^a-z0-9]+", "_", (title or "").lower())
    s = re.sub(r"_{2,}", "_", s).strip("_")[:40].strip("_")
    return "o%d_%s" % (num, s or "tbd")


def cmd_scaffold(a):
    """Create a new problem folder from _templates/ (never hand-written)."""
    con = connect()
    if a.pid:
        pid = a.pid
        num = num_of(pid)
        slug = a.slug or pid.replace("/", "_")
        if num is None:
            # theme problem: NEVER write into the theme root - the theme already
            # owns 01_problem_record.md / SESSION_START.md.  Use a subfolder.
            theme, _, item = pid.partition("/")
            if not item:
                sys.exit("theme pid must be '<theme>/<item>', got '%s'" % pid)
            dest = os.path.join(theme_dir(theme), item)
        else:
            dest = os.path.join(OPF, slug)
    else:
        num = a.num if a.num is not None else _next_free(con)
        pid = "O%d" % num
        slug = a.slug or _slugify(num, a.title)
        dest = os.path.join(OPF, slug)
    if con.execute("SELECT 1 FROM o_problem WHERE pid=?", (pid,)).fetchone():
        sys.exit("%s already registered" % pid)
    if num is not None and con.execute("SELECT 1 FROM reserved_num WHERE num=?", (num,)).fetchone():
        sys.exit("O%d is a reserved/tombstone number - refusing" % num)
    if os.path.exists(dest):
        sys.exit("directory already exists: %s" % dest)

    today = datetime.date.today().isoformat()
    for tpl, out in (("01_problem_record.md", "01_problem_record.md"),
                     ("SESSION_START.md", "SESSION_START.md")):
        src = os.path.join(TEMPLATES, tpl)
        if not os.path.exists(src):
            sys.exit("template missing: %s (see _templates/FORMAT.md)" % src)
        txt = read(src)
        if txt is None:
            sys.exit("template unreadable: %s" % src)
        txt = (txt.replace("O{NNN}", pid if num is None else "O%d" % num)
                  .replace("{NNN}", str(num) if num is not None else pid)
                  .replace("{NN}", str(num) if num is not None else pid)
                  .replace("{folder}", os.path.relpath(dest, OPF))
                  .replace("{問題名，一行，≤120 字}", a.title)
                  .replace("{問題名}", a.title)
                  .replace("{YYYY-MM-DD}", today)
                  .replace("{由邊度註冊 — 例: O115 docs/02 §二 L7}",
                           a.source or "-")
                  .replace("{由邊度註冊}", a.source or "-"))
        os.makedirs(dest, exist_ok=True)
        target = os.path.join(dest, out)
        if os.path.exists(target):
            sys.exit("refusing to overwrite existing file: %s" % target)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(txt)
    for sub in ("docs", "scripts", "data"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)

    rec = record(con, "registered", pid, owner=a.owner or pid, slug=slug, title=a.title,
                 keywords=a.keywords, state=a.state or "registered",
                 state_source="manual", ref=os.path.relpath(
                     os.path.join(dest, "01_problem_record.md"), REPO))
    replay(con, rec)
    con.commit()
    print("scaffolded %s -> %s" % (pid, os.path.relpath(dest, REPO)))
    print("  from _templates/ (01_problem_record.md + SESSION_START.md + docs/ scripts/ data/)")
    print("  registered  ts=%s" % rec["ts"])
    print("\n  paste into open_problems_fresh/README.md (see _templates/README_row.md):")
    print("  | **%s** | **%s** | 📄 **已註冊 — 未開始** | **{摘要}** |" % (pid, a.title))


def cmd_blocks(a):
    """Machine-block coverage: how many docs carry the <!-- registry --> block."""
    import collections
    cov = collections.Counter()
    missing = []
    bad = []
    for guess, path, kind in iter_docs():
        b = parse_block(read(path))
        if not b:
            cov["no-block"] += 1
            missing.append(os.path.relpath(path, REPO))
            continue
        cov["ok"] += 1
        for req in ("pid", "title", "state", "owner", "created", "updated",
                    "prereq", "source", "verdict", "flags"):
            if req not in b:
                bad.append("%s: missing field '%s'" % (os.path.relpath(path, REPO), req))
        if b.get("state") not in STATES:
            bad.append("%s: bad state '%s'" % (os.path.relpath(path, REPO), b.get("state")))
    print("registry blocks: %d ok / %d missing  (%.1f%% coverage)"
          % (cov["ok"], cov["no-block"],
             100.0 * cov["ok"] / max(1, cov["ok"] + cov["no-block"])))
    if bad:
        print("\n[BAD-BLOCK] %d" % len(bad))
        for x in bad[:20]:
            print("   " + x)
    if a.list and missing:
        print("\n[NO-BLOCK] %d (first 20)" % len(missing))
        for x in missing[:20]:
            print("   " + x)
    print("\ntemplates: %s" % os.path.relpath(TEMPLATES, REPO))
    print("spec:      %s" % os.path.relpath(os.path.join(TEMPLATES, "FORMAT.md"), REPO))


def cmd_register(a):
    con = connect()
    if a.pid:
        pid = a.pid
    else:
        n = a.num if a.num is not None else _next_free(con)
        pid = "O%d" % n
    num = num_of(pid)
    if con.execute("SELECT 1 FROM o_problem WHERE pid=?", (pid,)).fetchone():
        sys.exit("%s already registered" % pid)
    if num is not None:
        if con.execute("SELECT 1 FROM reserved_num WHERE num=?", (num,)).fetchone():
            if not getattr(a, "reuse", False):
                sys.exit("O%d is a reserved/tombstone number - refusing "
                         "(creator-authorized reuse: pass --reuse --note '<authorization>')" % num)
            u = record(con, "unreserve", pid, num=num,
                       note=a.note or "creator-authorized reuse of tombstone number")
            replay(con, u)
            print("unreserved O%d (append-only event; original tombstone kept in log)" % num)
        for d in dirs_by_num().get(num, []):
            if getattr(a, "reuse", False):
                print("note: directory for O%d already exists (%s) - registering it in place"
                      % (num, d))
                break
            sys.exit("directory already exists: %s" % d)
        slug = a.slug or ("o%d_%s" % (num, _slugify(num, a.title).split("_", 1)[1]))
    else:
        head = pid.split("/")[0]
        if re.fullmatch(r"O\d+", head):
            # sub-item of an existing O, e.g. O222/Q1 -> num stays NULL (child problem,
            # not a new O-series row); the parent O must already be registered.
            if not con.execute("SELECT 1 FROM o_problem WHERE pid=?", (head,)).fetchone():
                sys.exit("parent %s is not registered - register the parent O first" % head)
            if not re.fullmatch(r"O\d+/[A-Za-z0-9_.-]+", pid):
                sys.exit("bad sub-id '%s' - use <O-number>/<item>, e.g. O222/Q1" % pid)
        elif head not in THEME_DIRS:
            sys.exit("theme '%s' is not a known theme dir - refusing (use --num for a new O)"
                     % head)
        slug = a.slug or pid
    rec = record(con, "registered", pid, owner=a.owner, ref=a.ref, note=a.note,
                 slug=slug, title=a.title, keywords=a.keywords,
                 state=a.state or "registered",
                 state_source=a.state_source or "manual")
    replay(con, rec)
    con.commit()
    print("registered %-12s slug=%-28s owner=%-8s ts=%s" % (
        pid, slug, a.owner or "-", rec["ts"]))
    print("  title: %s" % clip(a.title, 120))


def cmd_next_number(a):
    con = connect()
    print(_next_free(con))


def _next_free(con):
    used = {r["num"] for r in con.execute("SELECT num FROM o_problem WHERE num IS NOT NULL")}
    used |= {r["num"] for r in con.execute("SELECT num FROM reserved_num")}
    used |= set(dirs_by_num())
    n = max(used) + 1 if used else 1
    while n in used:
        n += 1
    return n


def cmd_assign(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    replay(con, record(con, "assigned", pid, owner=a.owner, ref=a.ref, note=a.note))
    con.commit()
    print("%s -> owner %s" % (pid, a.owner))


def cmd_progress(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    st = "partial" if a.verdict == "partial" else None
    replay(con, record(con, "progress", pid, verdict=a.verdict, ref=a.ref, note=a.note, state=st))
    con.commit()
    print("%s progress%s" % (pid, ("  verdict=" + a.verdict) if a.verdict else ""))


def cmd_close(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    v = a.verdict or "closed"
    st = {"closed": "closed", "negative": "closed", "falsified": "closed",
          "partial": "partial"}.get(v, "closed")
    replay(con, record(con, "closed", pid, verdict=v, ref=a.ref, note=a.note, state=st))
    con.commit()
    print("%s closed  verdict=%s  state=%s" % (pid, v, st))


def cmd_posthoc(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    replay(con, record(con, "posthoc", pid, ref=a.ref, note=a.note))
    con.commit()
    print("%s flagged post-hoc (verdict unchanged)" % pid)


def cmd_alias(a):
    """Record / list what a stale label means in a given scope."""
    con = connect()
    if a.list:
        rows = con.execute("SELECT * FROM alias ORDER BY scope,label").fetchall()
        print("%-16s %-10s %-10s %s" % ("scope", "label", "-> pid", "note"))
        for r in rows:
            print("%-16s %-10s %-10s %s" % (r["scope"], r["label"], r["pid"], r["note"] or ""))
        print("\n%d alias(es)" % len(rows))
        return
    if not (a.scope and a.label and a.pid):
        sys.exit("need --scope --label --pid (or --list)")
    if con.execute("SELECT 1 FROM o_problem WHERE pid=?", (a.pid,)).fetchone() is None:
        sys.exit("target pid %s is not registered - refusing (alias must point at a real problem)"
                 % a.pid)
    replay(con, record(con, "alias", a.pid, owner=a.scope, slug=a.label, note=a.note))
    con.commit()
    print("alias  %s:%s -> %s" % (a.scope, a.label, a.pid))


def cmd_collision(a):
    """Record / list number collisions (one number, several directories)."""
    con = connect()
    if a.list:
        rows = con.execute("SELECT * FROM collision ORDER BY num").fetchall()
        for r in rows:
            print("O%-5s %s\n        %s" % (r["num"], r["dirs"], r["note"] or ""))
        print("\n%d collision(s)" % len(rows))
        return
    if a.scan:
        n = 0
        for num, ds in sorted(dirs_by_num().items()):
            if len(ds) < 2:
                continue
            if con.execute("SELECT 1 FROM collision WHERE num=?", (num,)).fetchone():
                continue
            replay(con, record(con, "collision", None, num=num,
                               slug=json.dumps([os.path.basename(d) for d in ds]),
                               note="auto-detected: %d directories share O%d" % (len(ds), num)))
            n += 1
        con.commit()
        print("scanned: registered %d new collision(s)" % n)
        return
    sys.exit("use --scan or --list")


def cmd_resolve(a):
    """Resolve a label as written in a scope."""
    con = connect()
    r = con.execute("SELECT * FROM alias WHERE scope=? AND label=?",
                    (a.scope, a.label)).fetchone()
    if r:
        print("%s : %s  ->  %s   [%s]" % (a.scope, a.label, r["pid"], r["note"] or ""))
    else:
        print("%s : %s  ->  (no alias - means itself)" % (a.scope, a.label))


def cmd_note(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    replay(con, record(con, "note", pid, ref=a.ref, note=a.note))
    con.commit()
    print("%s noted (state unchanged)" % pid)


def cmd_reopen(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    replay(con, record(con, "reopened", pid, ref=a.ref, note=a.note, state="open"))
    con.commit()
    print("%s reopened" % pid)


def cmd_merge(a):
    con = connect()
    pid = _pid(a)
    tgt = _pid_target(a)
    _need(con, pid)
    _need(con, tgt)
    replay(con, record(con, "merged", pid, target_pid=tgt, ref=a.ref, note=a.note,
                       state="merged"))
    con.commit()
    print("%s merged into %s  (row kept as tombstone)" % (pid, tgt))


def cmd_handoff(a):
    con = connect()
    pid = _pid(a)
    tgt = _pid_target(a)
    _need(con, pid)
    _need(con, tgt)
    replay(con, record(con, "handed_off", pid, target_pid=tgt, ref=a.ref,
                       note=a.note, owner=tgt))
    con.commit()
    print("%s handed off to %s" % (pid, tgt))


def _pid_target(a):
    t = getattr(a, "target_pid", None)
    if t:
        return t
    n = getattr(a, "target", None)
    if n is not None:
        return "O%d" % n
    sys.exit("need --target-pid or --target N")


def cmd_retract(a):
    con = connect()
    pid = _pid(a)
    _need(con, pid)
    replay(con, record(con, "retracted", pid, ref=a.ref, note=a.note, state="retracted"))
    con.commit()
    print("%s retracted" % pid)


def cmd_tombstone(a):
    con = connect()
    pid = _pid(a)
    replay(con, record(con, "tombstone", pid, ref=a.ref, note=a.note, state="tombstone"))
    con.commit()
    print("%s marked tombstone (number reserved, never reusable)" % pid)


def _rows(con, pid=None):
    q = "SELECT * FROM o_problem"
    p = []
    if pid:
        # an O also owns its sub-items (O222/Q1 ...)
        q += " WHERE pid=? OR pid LIKE ?"
        p = [pid, pid + "/%"]
        q += " ORDER BY (num IS NULL), pid"
    else:
        q += " ORDER BY (num IS NULL), num, pid"
    return con.execute(q, p).fetchall()


def cmd_log(a):
    con = connect()
    want = None
    if getattr(a, "pid", None) or getattr(a, "num", None):
        want = _pid(a)
    q = "SELECT * FROM event"
    p = []
    if want:
        # own events + child items (O222/Q1) + INCOMING handoffs/merges (target_pid)
        q += " WHERE pid=? OR pid LIKE ? OR target_pid=?"
        p = [want, want + "/%", want]
    q += " ORDER BY id"
    for r in con.execute(q, p):
        inc = bool(want) and r["target_pid"] == want and r["pid"] != want
        kind = ("<< " + (r["kind"] or "")) if inc else (r["kind"] or "")
        print("%-24s %-14s %-10s %-9s %-8s %-34s %s" % (
            r["ts"], kind, r["pid"] or "-", r["verdict"] or "",
            r["owner"] or "", r["ref"] or "", r["note"] or ""))


def cmd_status(a):
    con = connect()
    pid = None
    if getattr(a, "pid", None) or getattr(a, "num", None):
        pid = _pid(a)
    rows = _rows(con, pid)
    if a.json:
        print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=1))
        return
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    print("%-10s %-9s %-10s %-8s %-8s %-10s %s" % (
        "pid", "state", "verdict", "flags", "owner", "created", "title"))
    for r in rows:
        print("%-10s %-9s %-10s %-8s %-8s %-10s %s" % (
            r["pid"], r["state"], r["verdict"] or "-", r["flags"] or "-",
            r["owner"] or "-", (r["created_ts"] or "")[:10], clip(r["title"], 56)))
    print("\ntotal=%d  %s" % (len(rows), "  ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    if pid:
        inc = con.execute(
            "SELECT * FROM event WHERE target_pid=? AND (pid IS NULL OR pid<>?)"
            " ORDER BY id", (pid, pid)).fetchall()
        print("\nincoming (%d addressed to %s):" % (len(inc), pid))
        for r in inc:
            print("  << %-24s %-11s from %-8s %s" % (
                r["ts"], r["kind"], r["pid"] or "-", clip(r["note"], 100) or ""))


def cmd_check(a):
    con = connect()
    allrows = con.execute("SELECT * FROM o_problem").fetchall()
    db = {r["pid"]: r for r in allrows}
    onum = {r["num"]: r for r in allrows if r["num"] is not None}
    ddirs = dirs_by_num()
    rdm = readme_nums()
    problems = []

    for n, v in {n: v for n, v in ddirs.items() if len(v) > 1}.items():
        problems.append(("DUPLICATE-DIR", "O%d has %d directories: %s" % (n, len(v), v)))

    # registered collisions must still be real; a resolved one should be retired
    reg = {r["num"]: r for r in con.execute("SELECT * FROM collision")}
    for n, r in sorted(reg.items()):
        if n not in ddirs or len(ddirs[n]) < 2:
            problems.append(("COLLISION-STALE", "O%d registered as collision but now has %d dir(s)"
                             % (n, len(ddirs.get(n, [])))))
    for n in sorted(set(ddirs) & set(reg)):
        pass  # known + still colliding = expected, not drift

    # alias targets must exist; a dangling alias silently misroutes a lookup
    for r in con.execute("SELECT * FROM alias"):
        if not con.execute("SELECT 1 FROM o_problem WHERE pid=?", (r["pid"],)).fetchone():
            problems.append(("ALIAS-DANGLING", "%s:%s -> %s (target not registered)"
                             % (r["scope"], r["label"], r["pid"])))

    for n in sorted(set(ddirs) - set(onum)):
        problems.append(("UNREGISTERED-DIR", "O%d dir exists, not in register (%s)" % (n, ddirs[n][0])))

    for n in sorted(set(onum) - set(ddirs)):
        problems.append(("INFO-DB-ONLY", "O%d registered, folder not created yet (%s)"
                         % (n, onum[n]["slug"])))

    for n in sorted(set(rdm) - set(onum)):
        problems.append(("README-ONLY", "O%d has README row but no register row" % n))

    for n, r in sorted(onum.items()):
        rs = status_of_emoji(rdm.get(n, {}).get("status"))
        if rs and r["state"] in ("closed", "merged", "retracted", "tombstone") and rs != r["state"]:
            if not (r["state"] in ("merged", "tombstone") and rs == "merged"):
                problems.append(("STATUS-DRIFT", "O%d register=%s README=%s" % (n, r["state"], rs)))

    # theme / sub-item problems: the pid's first segment must resolve to a real folder
    for pid, r in sorted(db.items()):
        if r["num"] is None:
            seg = pid.split("/")[0]
            if re.fullmatch(r"O\d+", seg):
                # sub-item of an existing O: parent registered + parent dir exists
                if seg not in db:
                    problems.append(("PID-ORPHAN", "%s -> parent %s not registered" % (pid, seg)))
                elif not ddirs.get(db[seg]["num"]):
                    problems.append(("PID-NO-FOLDER", "%s -> parent %s has no directory" % (pid, seg)))
            elif not os.path.isdir(theme_dir(seg)):
                problems.append(("PID-NO-FOLDER", "%s -> main_problems or open_problems_fresh/%s/ missing" % (pid, seg)))

    # refs are the ONLY content pointer: a broken ref means the register lost
    # its link to the original.  Check path (and #Lnn) against the filesystem.
    # 2026-10-07 修正第 ⑥ 類 REF-MISSING（O220/O221 雙路徑 ref）:
    #   some events chain several files in one ref ("a.md + b.md" or "a.md ; b.md").
    #   Split on ' + ' / ' ; ' and existence-check EVERY segment independently
    #   instead of treating the chained string as a single path (which can never
    #   exist).  Each segment still goes through resolve_ref (theme migration).
    #   O220: docs/13 + docs/14 (progress 2026-09-28).  O221: docs/19 ; docs/20.
    # 2026-10-07 修正第 ① 類 REF-MISSING（O 目錄相對 ref）:
    #   bare segments like "docs/14_..." written without the oNNN dir prefix are
    #   resolved via check_ref_path: pid's own O dir first, then repo-wide unique
    #   hit (never guess on ambiguous names).  Clears O220 residual + O225/O88.
    for pid, r in sorted(db.items()):
        for ref in con.execute("SELECT ref FROM event WHERE pid=? AND ref IS NOT NULL", (pid,)):
            rf = ref["ref"].split("#")[0].strip()
            # 2026-10-15 類⑥ 延伸 (O137 自引入): ref 可帶 section 標記
            # （'…/docs/36_gap_attack_round19.md §1.3'）。'§' 唔會喺 repo
            # 檔名出現（docs/scripts/data 檔名全 ASCII），故此後綴係註釋
            # 唔係路徑 — 剝走 '§' 及其後內容再檢查。
            rf = re.split(r"\s*§\s*", rf)[0].strip()
            if not rf or rf.startswith(("http", "-")):
                continue
            segs = [s.strip() for s in re.split(r"\s*[+;]\s+", rf)]
            # 2026-10-09 類⑥ 延伸 (O148 自引入): 該 event 把備註文字混入 ref
            # （'o148/docs/12 + S11 反事實'——'+' 之後係註釋唔係路徑）。repo 檔名全
            # ASCII（docs/scripts/data 層一級檔名無中文），含 CJK 字元嘅段唔可能係
            # 檔案路徑 → 當註釋跳過。ASCII 段維持原判（MISSING 照報，唔放寬）。
            segs = [s for s in segs if not re.search(r"[\u4e00-\u9fff]", s)]
            miss = [seg for seg in segs if seg and check_ref_path(pid, seg, ddirs) is None]
            if miss:
                problems.append(("REF-MISSING", "%s ref -> %s does not exist"
                                 % (pid, " | ".join(miss))))
                continue
            m = re.search(r"#L(\d+)", ref["ref"])
            if m:
                for seg in segs:
                    fp = check_ref_path(pid, seg, ddirs)
                    if fp and os.path.isfile(fp):
                        n = sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))
                        if int(m.group(1)) > n:
                            problems.append(("REF-LINE-OOR", "%s ref %s#L%s but file has %d lines"
                                             % (pid, seg, m.group(1), n)))
                        break

    # machine blocks: absence is informational (not migrated yet), but a block
    # that contradicts the register row is a hard drift - two sources of truth.
    for guess, path, kind in iter_docs():
        b = parse_block(read(path))
        rel = os.path.relpath(path, REPO)
        if not b:
            problems.append(("NO-BLOCK", rel))
            continue
        bp = b.get("pid")
        if not bp:
            problems.append(("BLOCK-DRIFT", "%s: block has no pid" % rel))
            continue
        row = db.get(bp)
        if row is None:
            problems.append(("BLOCK-UNREGISTERED", "%s: block pid %s not in register" % (rel, bp)))
            continue
        if b.get("state") and b["state"] != row["state"]:
            problems.append(("BLOCK-DRIFT", "%s: block=%s register=%s"
                             % (rel, b["state"], row["state"])))

    # informational: the legacy markdown sources disagree with each other.
    # README is authoritative, so this is not drift - it is a list of stale
    # problem_record / SESSION_START status lines worth fixing at leisure.
    for n in sorted(set(onum) & set(rdm)):
        d = ddirs.get(n, [])
        if not d:
            continue
        a_ = status_of_emoji(rdm[n]["status"])
        pr = read(os.path.join(d[0], "01_problem_record.md"))
        ss = read(os.path.join(d[0], "SESSION_START.md"))
        b_ = status_of_emoji(field(pr, "\u72c0\u614b") or field(ss, "\u72c0\u614b")
                             or field(ss, "\u6700\u7d42\u72c0\u614b"))
        if a_ and b_ and a_ != b_:
            problems.append(("SEED-DISAGREE", "O%d README=%s markdown=%s" % (n, a_, b_)))

    print("register rows=%d (O-series %d, theme %d)  dirs=%d  README rows=%d"
          % (len(db), len(onum), len(db) - len(onum), len(ddirs), len(rdm)))
    srcs = {}
    for r in db.values():
        srcs[r["state_source"] or "-"] = srcs.get(r["state_source"] or "-", 0) + 1
    print("seed state source: " + "  ".join("%s=%d" % kv for kv in sorted(srcs.items())))
    for kind in ("DUPLICATE-DIR", "COLLISION-STALE", "UNREGISTERED-DIR", "README-ONLY",
                 "STATUS-DRIFT", "PID-NO-FOLDER", "REF-MISSING", "REF-LINE-OOR",
                 "ALIAS-DANGLING", "BLOCK-DRIFT", "BLOCK-UNREGISTERED",
                 "NO-BLOCK", "SEED-DISAGREE", "INFO-DB-ONLY"):
        hits = [p for p in problems if p[0] == kind]
        print("\n[%s] %d" % (kind, len(hits)))
        for _, msg in hits[:15]:
            print("   " + msg)
        if len(hits) > 15:
            print("   ... +%d more" % (len(hits) - 15))
    hard = [p for p in problems if p[0] not in ("INFO-DB-ONLY", "SEED-DISAGREE", "NO-BLOCK")]
    print("\nHARD DRIFT: %d" % len(hard))
    return 0 if not hard else 1


def cmd_dump(a):
    con = connect()
    recs = [dict(r) for r in con.execute("SELECT * FROM event ORDER BY id")]
    with open(JSONL, "w", encoding="utf-8") as fh:
        for r in recs:
            r.pop("id", None)
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print("dumped %d events -> %s" % (len(recs), JSONL))


def cmd_import(a):
    src = a.path or JSONL
    con = connect()
    con.execute("DELETE FROM event")
    n = 0
    for r in (read_jsonl() if src == JSONL else
              [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]):
        insert_event(con, r)
        replay(con, r)
        n += 1
    con.commit()
    print("imported %d events from %s" % (n, src))


def cmd_rebuild(a):
    if os.path.exists(SQLITE):
        for suf in ("", "-wal", "-shm"):
            if os.path.exists(SQLITE + suf):
                os.remove(SQLITE + suf)
    con = connect()
    cmd_import(argparse.Namespace(path=JSONL))
    con.close()
    print("rebuild done - run: register.py status")


def cmd_mirror(a):
    con = connect()
    rows = _rows(con)
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    lines = [
        "# REGISTER - IDCM open-problem lifecycle (GENERATED, do not edit)",
        "",
        "Source of truth: `register.jsonl` (append-only). Regenerate: `python3 register.py mirror`",
        "Generated: %s" % now_iso(),
        "",
        "Events recorded: %d   Problems: %d" % (
            con.execute("SELECT COUNT(*) c FROM event").fetchone()["c"], len(rows)),
        "",
        "| pid | state | verdict | flags | owner | created | title |",
        "|:----|:------|:--------|:------|:------|:--------|:------|",
    ]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["pid"], r["state"], r["verdict"] or "-", r["flags"] or "-", r["owner"] or "-",
            (r["created_ts"] or "")[:10], (r["title"] or "").replace("|", "/")))
    lines += ["", "## Totals", ""]
    for k in sorted(counts):
        lines.append("- %s: %d" % (k, counts[k]))
    with open(MIRROR, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("mirror -> %s  (%d rows)" % (MIRROR, len(rows)))


# ---------------------------------------------------------------- backfill
def _git_first_seen():
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--reverse", "--name-only", "--format=%cI", "--",
             "open_problems_fresh"],
            cwd=REPO, capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return {}
    seen, cur = {}, None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d{4}-\d\d-\d\dT", line):
            cur = line
        elif cur and line not in seen:
            seen[line] = cur
    return seen


def cmd_backfill(a):
    con = connect()
    seen = _git_first_seen()
    rdm = readme_nums()
    added = 0
    for n, ds in sorted(dirs_by_num().items()):
        pid = "O%d" % n
        if con.execute("SELECT 1 FROM o_problem WHERE pid=?", (pid,)).fetchone():
            continue
        d = ds[0]
        pr = read(os.path.join(d, "01_problem_record.md"))
        ss = read(os.path.join(d, "SESSION_START.md"))
        title = None
        for txt in (pr, ss):
            if txt:
                m = re.search(r"^#\s*(.+)$", txt, re.M)
                if m:
                    title = m.group(1).strip()
                    break
        # state priority follows the project rule: README (authoritative) >
        # problem_record > SESSION_START.  SESSION_START alone must never decide
        # current state - it is a registration-time snapshot.
        st_rd = status_of_emoji(rdm.get(n, {}).get("status"))
        st_pr = status_of_emoji(field(pr, "\u72c0\u614b"))
        st_ss = status_of_emoji(field(ss, "\u72c0\u614b") or field(ss, "\u6700\u7d42\u72c0\u614b"))
        if st_rd:
            st, st_src = st_rd, "readme"
        elif st_pr:
            st, st_src = st_pr, "problem_record"
        elif st_ss:
            st, st_src = st_ss, "session_start"
        else:
            st, st_src = ("open" if (pr or ss) else "registered"), "inferred"
        src_txt = field(pr, "\u4f86\u6e90") or field(ss, "\u4f86\u6e90") or field(ss, "\u79fb\u4ea4")
        ts = None
        for k, v in seen.items():
            if k.startswith(d + "/") or k == d:
                if ts is None or v < ts:
                    ts = v
        if ts is None:
            try:
                p = os.path.join(d, "SESSION_START.md")
                ts = datetime.datetime.fromtimestamp(
                    os.path.getmtime(p if os.path.exists(p) else d)
                ).astimezone().isoformat(timespec="seconds")
            except OSError:
                ts = now_iso()
        ver = {"closed": "closed", "partial": "partial"}.get(st)
        rec = {"ts": ts, "pid": pid, "num": n, "kind": "registered", "verdict": ver,
               "owner": None, "target_pid": None, "ref": None,
               "slug": os.path.basename(d), "title": clip(title or "(no title)", 120),
               "keywords": clip(src_txt, 200), "state": st, "state_source": st_src,
               "note": clip(src_txt, 200), "session": "-",
               "source": "backfill:" + os.path.basename(d), "prev_hash": None}
        rows = con.execute("SELECT hash FROM event ORDER BY id DESC LIMIT 1").fetchone()
        rec["prev_hash"] = rows["hash"] if rows else None
        rec["hash"] = chain_hash(rec, rec["prev_hash"])
        append_jsonl(rec)
        insert_event(con, rec)
        replay(con, rec)
        added += 1
    # legacy tombstone numbers: README row with no directory, or number gap
    ns = sorted(dirs_by_num())
    gaps = [n for n in range(1, max(ns) + 1) if n not in dirs_by_num()] if ns else []
    for n in sorted(set(gaps) | {k for k in rdm if k not in dirs_by_num()}):
        replay(con, record(con, "tombstone", "O%d" % n,
                           note="legacy tombstone (no directory at backfill)"))
    con.commit()
    print("backfilled %d O-series problems; reserved %d tombstone numbers" % (added, len(set(gaps))))
    print("run: register.py mirror  &&  register.py check")


# ---------------------------------------------------------------- clue index
def cmd_clues(a):
    """Build the derived clue index: pid mentions + full-text, over the docs.

    Derived only.  Content stays in the markdown; this is a regenerable index
    that points back at it, so it never becomes a second system of record.

    2026-10-09: scope extended from OPF to OPF + MAIN (main_problems/ moved
    themes).  Mention pattern extended beyond O-numbers to main-theme pids
    (bbn, cmb_cl, ... pN-aliased themes) so p-series problems are findable.
    """
    # match O-numbers and any main-theme slug (case-insensitive, word-bounded)
    theme_pid_re = re.compile(
        r"(?<!\w)(%s)(?!\w)" % "|".join(sorted(THEME_MOVE, key=len, reverse=True)),
        re.IGNORECASE)
    o_re = re.compile(r"\bO(\d{1,3})\b")
    if os.path.exists(CLUES):
        os.remove(CLUES)
    con = sqlite3.connect(CLUES)
    con.execute("CREATE TABLE mention (pid TEXT, doc TEXT, line INTEGER, snippet TEXT)")
    con.execute("CREATE VIRTUAL TABLE doc_fts USING fts5(doc, text)")
    files = []
    for base, base_name in ((OPF, "open_problems_fresh"), (MAIN, "main_problems")):
        if not os.path.isdir(base):
            continue
        for root, dirs, names in os.walk(base):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "data", "_templates")]
            files += [os.path.join(root, nm) for nm in names if nm.endswith(".md")]
    nf = nm = 0
    for fp in sorted(files):
        rel = os.path.relpath(fp, REPO)
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        nf += 1
        con.execute("INSERT INTO doc_fts (doc,text) VALUES (?,?)", (rel, txt))
        for i, line in enumerate(txt.splitlines(), 1):
            for m in o_re.finditer(line):
                con.execute("INSERT INTO mention VALUES (?,?,?,?)",
                            ("O%d" % int(m.group(1)), rel, i, clip(line, 200)))
                nm += 1
            for m in theme_pid_re.finditer(line):
                pid = m.group(1).lower()
                if o_re.search(m.group(1)):
                    continue
                con.execute("INSERT INTO mention VALUES (?,?,?,?)",
                            (pid, rel, i, clip(line, 200)))
                nm += 1
    con.execute("CREATE INDEX idx_mention_pid ON mention(pid)")
    con.commit()
    con.close()
    print("clue index: %d docs, %d pid mentions (O + main themes) -> %s" % (nf, nm, os.path.basename(CLUES)))


def cmd_find(a):
    if not os.path.exists(CLUES):
        sys.exit("no clue index - run: register.py clues")
    con = sqlite3.connect(CLUES)
    pid = a.pid or ("O%d" % a.num if a.num else None)
    # resolve stale labels through the alias table before searching
    # (2026-10-09: also try global scope so pN_* theme aliases resolve
    # without requiring --scope; e.g. `find --pid p1_bbn` -> bbn)
    scope = getattr(a, "scope", None)
    if pid and (scope or True):
        lc = connect(create=False)
        r = lc.execute(
            "SELECT scope,pid,note FROM alias WHERE label=? AND (scope=? OR scope='global') "
            "ORDER BY (scope=?) DESC LIMIT 1",
            (pid, scope or "global", scope or "global")).fetchone()
        if r:
            print("resolved %s:%s -> %s   [%s]" % (r["scope"], pid, r["pid"], r["note"] or ""))
            pid = r["pid"]
        lc.close()
    if pid and num_of(pid) is not None:
        rows = con.execute("SELECT doc,line,snippet FROM mention WHERE pid=? ORDER BY doc,line",
                           (pid,)).fetchall()
        print("%d mentions of %s:" % (len(rows), pid))
        for d, l, s in rows[: a.limit]:
            print("  %s:%d  %s" % (d, l, " ".join(s.split())[:150]))
        if len(rows) > a.limit:
            print("  ... +%d more (raise --limit)" % (len(rows) - a.limit))
    elif pid:
        seg = pid.split("/")[0]
        tail = pid.split("/")[-1]
        # 2026-10-09: theme_dir() is migration-aware (open_problems_fresh or
        # main_problems/pNN_<theme>) — fallback must cover both.
        td = theme_dir(seg)
        tpat = os.path.relpath(td, REPO).replace("\\", "/")
        rows = con.execute(
            "SELECT doc, snippet(doc_fts,1,'[',']','...',10) FROM doc_fts"
            " WHERE doc_fts MATCH ? AND doc LIKE ? LIMIT ?",
            ('"%s"' % tail.replace('"', ""), tpat + "/%", a.limit)).fetchall()
        print("%s -> %d docs in %s/ matching %r:" % (pid, len(rows), tpat, tail))
        for d, s in rows:
            print("  %s  %s" % (d, " ".join((s or "").split())[:150]))
    elif a.term:
        try:
            rows = con.execute(
                "SELECT doc, snippet(doc_fts,1,'[',']','...',10) FROM doc_fts"
                " WHERE doc_fts MATCH ? LIMIT ?",
                ('"%s"' % a.term.replace('"', ""), a.limit)).fetchall()
        except sqlite3.OperationalError:
            rows = con.execute(
                "SELECT doc, substr(text,1,200) FROM doc_fts WHERE text LIKE ? LIMIT ?",
                ("%" + a.term + "%", a.limit)).fetchall()
        print("%d docs matching %r:" % (len(rows), a.term))
        for d, s in rows:
            print("  %s  %s" % (d, " ".join((s or "").split())[:160]))
    else:
        sys.exit("give --pid X, --num N or --term TEXT")
    con.close()


# ---------------------------------------------------------------- main
def build_parser():
    p = argparse.ArgumentParser(description="IDCM open-problem lifecycle register")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **kw):
        s = sub.add_parser(name, **kw)
        s.set_defaults(func=fn)
        return s

    def keyargs(s, required=False):
        s.add_argument("--pid", help="problem id, e.g. O213 or bbn/he3")
        s.add_argument("--num", type=int, help="shorthand for --pid O<num>")

    s = add("register", cmd_register)
    keyargs(s)
    s.add_argument("--slug")
    s.add_argument("--title", required=True)
    s.add_argument("--keywords")
    s.add_argument("--owner")
    s.add_argument("--state", choices=STATES)
    s.add_argument("--state-source", dest="state_source")
    s.add_argument("--ref")
    s.add_argument("--note")
    s.add_argument("--reuse", action="store_true",
                   help="creator-authorized reuse of a reserved/tombstone number: records an "
                        "append-only `unreserve` event instead of refusing")

    s = add("scaffold", cmd_scaffold)
    keyargs(s)
    s.add_argument("--slug")
    s.add_argument("--title", required=True)
    s.add_argument("--keywords")
    s.add_argument("--owner")
    s.add_argument("--state", choices=STATES)
    s.add_argument("--source", help="由邊度註冊 (寫入機器塊 source 欄)")

    s = add("blocks", cmd_blocks)
    s.add_argument("--list", action="store_true")

    add("next-number", cmd_next_number)

    s = add("assign", cmd_assign); keyargs(s)
    s.add_argument("--owner", required=True); s.add_argument("--ref"); s.add_argument("--note")

    s = add("progress", cmd_progress); keyargs(s)
    s.add_argument("--verdict", choices=VERDICTS); s.add_argument("--ref"); s.add_argument("--note")

    s = add("close", cmd_close); keyargs(s)
    s.add_argument("--verdict", choices=VERDICTS); s.add_argument("--ref"); s.add_argument("--note")

    s = add("posthoc", cmd_posthoc); keyargs(s)
    s.add_argument("--ref"); s.add_argument("--note")

    s = add("note", cmd_note); keyargs(s)
    s.add_argument("--ref", required=True); s.add_argument("--note")

    s = add("alias", cmd_alias)
    s.add_argument("--list", action="store_true")
    s.add_argument("--scope", help="'global' or a theme dir, e.g. cmb_cold_spot")
    s.add_argument("--label", help="label as WRITTEN in that scope, e.g. O3")
    s.add_argument("--pid", help="what it actually means today, e.g. O4")
    s.add_argument("--note")

    s = add("collision", cmd_collision)
    s.add_argument("--list", action="store_true")
    s.add_argument("--scan", action="store_true")

    s = add("resolve", cmd_resolve)
    s.add_argument("--scope", required=True)
    s.add_argument("--label", required=True)

    s = add("reopen", cmd_reopen); keyargs(s)
    s.add_argument("--ref"); s.add_argument("--note")

    for nm, fn in (("merge", cmd_merge), ("handoff", cmd_handoff)):
        s = add(nm, fn); keyargs(s)
        s.add_argument("--target-pid", dest="target_pid")
        s.add_argument("--target", type=int)
        s.add_argument("--ref"); s.add_argument("--note")

    s = add("retract", cmd_retract); keyargs(s)
    s.add_argument("--ref"); s.add_argument("--note")

    s = add("tombstone", cmd_tombstone); keyargs(s)
    s.add_argument("--ref"); s.add_argument("--note")

    s = add("log", cmd_log); keyargs(s)

    s = add("status", cmd_status); keyargs(s)
    s.add_argument("--json", action="store_true")

    add("check", cmd_check)
    add("dump", cmd_dump)
    s = add("import", cmd_import); s.add_argument("path", nargs="?")
    add("rebuild", cmd_rebuild)
    add("mirror", cmd_mirror)
    add("backfill", cmd_backfill)
    add("clues", cmd_clues)
    s = add("find", cmd_find); keyargs(s)
    s.add_argument("--scope", help="resolve a stale label in this scope first")
    s.add_argument("--term")
    s.add_argument("--limit", type=int, default=30)
    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(args.func(args) or 0)
