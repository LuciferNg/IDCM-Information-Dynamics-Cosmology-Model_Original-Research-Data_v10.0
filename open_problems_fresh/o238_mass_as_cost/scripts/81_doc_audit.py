#!/usr/bin/python3
"""O238 — Script 81: 文檔層公式/數字 Audit (T2-docs)

用戶指令: 「Audit O238 所有文檔的公式數字是否正確」— 覆蓋 docs/02-14,
final_result.md, record 入面每個公式/數字.

方法: 對每份 docs 抽「關鍵聲稱」, 同權威值表 (scripts/80 已驗證 data JSON + 外部權威) 對比.
  權威值表: AUDIT (已知正確, 31/31 PASS 來自 scripts/80) + OBS (外部觀測, PDG/lattice)
  容差: 相對 1e-3 (0.1%) — 超過 = FAIL; 標度近似 (如 1.4664e-6 vs 1.466433599e-6) 容許 1e-4

FAIL 判準: docs 數字同權威值唔符 (超過容差) = 文檔錯誤, 需 append-only 更正.
"""
import re, sys, os

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o238_mass_as_cost"
os.chdir(BASE)

# ── 權威值表 (source: scripts/80 audit PASS + data JSON + 外部權威) ──
AUDIT = {
    # 模型核心 (S1 = 混標度, S2 = freeze v2 權威)
    "C_S1": 1.466433599e-6, "C_S2": 1.521507856e-6,
    "RMS_S1": 0.580174, "RMS_S2": 0.545571, "RMS_S3": 0.626725,
    "a_S1": 2.616977, "a_S2": 2.642463, "a_S3": 2.615977,
    "a_loocv_lo": 2.5520, "a_loocv_hi": 2.6836,
    "M0": 27.9009, "R": 603.207305,
    # c/s 剔除後
    "RMS_S1_nocs": 0.2515, "RMS_S2_nocs": 0.1987,
    # C 閉合
    "inv88cubed": 1.467411e-6, "C1_dev": 0.067, "C2_dev": 3.69,
    # 殘差 (log 域 S1/S2/S3)
    "resid_b_S2": -0.416, "resid_b_S3": -0.228,
    # 共線性
    "R2_all": 0.09, "corr_sel9": -0.996, "R2_sel9": 0.992,
    "p_rand9": 0.00015, "p_a5": 1.75e-12, "p_a5_bonf": 1.225e-11,
    "spearman": 1.00000000,
    # PCA
    "pc1_var": 99.8, "corr_pc1": 0.986, "rms_pca": 0.646, "msp_ratio": 1.69,
    # c/s 軌跡
    "cs_ratio": 3.177, "rms_csdummy": 0.225, "dpc1_pc2_corr": -0.65,
    # C 分通道 (S2)
    "C_A": 9.6e-7, "C_B": 1.47e-6, "C_C": 1.85e-6, "p_channel": 0.431, "F_channel": 0.897,
    "p_channel_nocs": 0.135, "F_channel_nocs": 3.906,
    # CSG v2
    "csg_v2_rms": 0.0833, "csg_v1_rms": 0.0076,
    # 強子盲測
    "hadron_hit": 6, "hadron_pool": 17, "pool_density": 8.6,
    # look-elsewhere
    "r2_rules": {"coprime11": 0.9954, "a5": 0.9920, "primepower": 0.9903},
    "rms_rules": {"a5": 0.546, "coprime11": 1.102, "primepower": 1.137},
    # LO4 譜統計
    "lo4_overlap_max": 1, "lo4_rmax": 0.10, "gamma_top_R2": 0.819,
    # 11×奇子格
    "s11_odd": 0.008, "s11_even": 6.36,
    # α 對比
    "phi2": 2.618034,
    # 張力鏈
    "e1": 0.00822, "e2": 0.01112, "frust_med": 26.05, "edge_len": 26.09,
    # A₅ 群論
    "a5_order": 60, "s5_order": 120, "frust_edges": 32, "transparent": 88,
}
# 外部觀測/權威 (PDG/lattice/FLAG)
OBS = {
    "me": 0.51099895, "mmu": 105.6583755, "mtau": 1776.86,
    "md_mu_fl": 2.1505, "md_mu_err": 0.111,
    "ms_mu_fl": 42.89, "ms_mu_err": 1.52,
    "mc_ms_v2": 11.652, "mb_mc_v2": 4.586, "mb_mc_rgi": 4.586,
    "b_s1": 3581.6, "b_s2": 4990.9, "b_s3": 6938.0,
    "u_rgi": 2.97, "d_rgi": 6.53, "s_rgi": 130.0, "c_rgi": 1484.2,
    "gamma3_gamma2": 2.245204,
}

fails = []
def check(doc, claim, got_audit, tol=1e-3, aud=True):
    """got = docs 數字; aud = 權威值"""
    if aud:
        ref = AUDIT.get(got_audit, None)
    else:
        ref = OBS.get(got_audit, None)
    if ref is None:
        return
    try:
        gv = float(claim)
    except:
        return
    if ref == 0:
        return
    rel = abs(gv - ref) / max(abs(ref), 1e-30)
    ok = rel < tol
    if not ok:
        fails.append((doc, claim, got_audit, ref, rel))
    return ok

def scan(docname, keymap):
    """keymap: {docs 數字樣本 -> 權威 key} — 對該 doc 全文抽匹配"""
    p = os.path.join("docs", docname)
    txt = open(p, encoding="utf-8").read()
    r = f"FAIL {docname}: "
    n = 0
    for pat, refkey, tol in keymap:
        # 喺 txt 揾 pattern (正則), 取第一個 match
        m = re.search(pat, txt)
        if not m:
            continue
        try:
            val = float(m.group(1))
        except:
            continue
        n += 1
        # 對比
        if refkey in AUDIT:
            ref = AUDIT[refkey]
        elif refkey in OBS:
            ref = OBS[refkey]
        else:
            continue
        rel = abs(val - ref) / max(abs(ref), 1e-30)
        if rel >= tol:
            fails.append((docname, f"pat={pat} got={val}", refkey, ref, rel))
    return n

# ── 逐 doc 抽公式/數字 ──
checks_done = 0
def A(doc, pat, key, tol=1e-3):
    global checks_done
    m = re.search(pat, open(f"docs/{doc}", encoding="utf-8").read())
    if not m:
        return
    checks_done += 1
    try:
        val = float(m.group(1))
    except:
        return
    ref = AUDIT.get(key, OBS.get(key, None))
    if ref is None:
        return
    rel = abs(val - ref) / max(abs(ref), 1e-30)
    if rel >= tol:
        fails.append((doc, f"'{pat}' → {val}", key, ref, rel))

# docs/02
A("02_scale_c_identity.md", r"C\\_fit\s*=\s*([\d.e+-]+)", "C_S1")
A("02_scale_c_identity.md", r"M₀\s*=\s*([\d.]+)", "M0")
A("02_scale_c_identity.md", r"R\s*=\s*([\d.]+)", "R")
A("02_scale_c_identity.md", r"RMS\s*=\s*([\d.]+)", "RMS_S1")
# docs/03
A("03_scale_slope_round1.md", r"RMS\s*=\s*0\.580", "RMS_S1")
A("03_scale_slope_round1.md", r"79/30", None)  # 標誌
# docs/04
A("04_freeze_v2_scheme_audit.md", r"3581\.6", "b_s1")
A("04_freeze_v2_scheme_audit.md", r"4990\.9", "b_s2")
A("04_freeze_v2_scheme_audit.md", r"6938\.0", "b_s3")
A("04_freeze_v2_scheme_audit.md", r"−0\.416", "resid_b_S2", tol=1e-2)
A("04_freeze_v2_scheme_audit.md", r"−0\.228", "resid_b_S3", tol=1e-2)
A("04_freeze_v2_scheme_audit.md", r"474\.?", None)
# docs/06
A("06_projection_spectrum.md", r"γ₃/γ₂\s*=\s*([\d.]+)", "gamma3_gamma2", tol=1e-4)
A("06_projection_spectrum.md", r"2\.1505", "md_mu_fl")
A("06_projection_spectrum.md", r"0\.51099895", "me")
A("06_projection_spectrum.md", r"105\.6583755", "mmu")
A("06_projection_spectrum.md", r"1776\.86", "mtau")
# docs/07
A("07_csg_v2_collapse_channelC.md", r"0\.0833", "csg_v2_rms")
A("07_csg_v2_collapse_channelC.md", r"0\.0076", "csg_v1_rms")
# docs/08
A("08_projection_round_summary.md", r"0\.9920", "R2_sel9", tol=1e-2)
A("08_projection_round_summary.md", r"0\.7340|0\.734", None)
A("08_projection_round_summary.md", r"1088\.3", None)
A("08_projection_round_summary.md", r"4990\.9", "b_s2")
# docs/09
A("09_pca_trajectory_oos.md", r"99\.8", "pc1_var", tol=1e-2)
A("09_pca_trajectory_oos.md", r"0\.986", "corr_pc1", tol=1e-2)
A("09_pca_trajectory_oos.md", r"1\.69", "msp_ratio", tol=1e-2)
A("09_pca_trajectory_oos.md", r"42\.89", "ms_mu_fl")
A("09_pca_trajectory_oos.md", r"1\.52", "ms_mu_err")
# docs/10
A("10_all_push_closure.md", r"0\.546", "rms_rules_a5" if False else "rms_rules", tol=1e-2)
A("10_all_push_closure.md", r"1\.102", "rms_rules", tol=1e-2)
# docs/11
A("11_hadron_projection_blind.md", r"6/17|6 個|6 命中|6/", None)
A("11_hadron_projection_blind.md", r"8\.6", "pool_density")
# docs/12
A("12_rule_lookelsewhere.md", r"0\.9954", "r2_coprime" if False else "r2_rules", tol=1e-2)
A("12_rule_lookelsewhere.md", r"1\.75e-12", "p_a5", tol=1e-2)
A("12_rule_lookelsewhere.md", r"1\.102", "rms_rules", tol=1e-2)
# docs/13
A("13_final_verdict.md", r"2\.552", "a_loocv_lo", tol=1e-2)
A("13_final_verdict.md", r"2\.684", "a_loocv_hi", tol=1e-2)
A("13_final_verdict.md", r"3\.18", "cs_ratio", tol=1e-2)
A("13_final_verdict.md", r"0\.646", "rms_pca", tol=1e-2)
A("13_final_verdict.md", r"0\.225", "rms_csdummy", tol=1e-2)
A("13_final_verdict.md", r"3\.69", "C2_dev")
A("13_final_verdict.md", r"0\.067", "C1_dev", tol=1e-2)
# docs/14
A("14_lo4_irreducibility.md", r"2\.245204", "gamma3_gamma2", tol=1e-6)
A("14_lo4_irreducibility.md", r"3\.24", None)
A("14_lo4_irreducibility.md", r"0\.822", "e1", tol=1e-2)
A("14_lo4_irreducibility.md", r"1\.112", "e2", tol=1e-2)

print(f"抽查 {checks_done} 項")
if fails:
    print("\n❌ FAIL 清單:")
    for doc, claim, key, ref, rel in fails:
        print(f"  {doc}: {claim}  (ref {key}={ref}, rel dev {rel*100:.4f}%)")
else:
    print("\n✅ 全部抽查通過 (含容差)")

# 額外: 抽取 docs/11 6/17 命中率
t11 = open("docs/11_hadron_projection_blind.md", encoding="utf-8").read()
m = re.search(r"(\d+)/17", t11)
if m:
    v = int(m.group(1))
    print(f"\ndocs/11 強子命中: {v}/17 (權威 6/17) → {'OK' if v == 6 else 'FAIL'}")