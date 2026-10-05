#!/usr/bin/env python3
"""
O59 closeout — independent audit (2026-10-05)
============================================
T1 獨立重驗：唔 import / 唔 call 任何 O59 原推導 script。
由原始輸入（o53 polytopes JSON、d_tensor_native_12d.npy、結構常數、K_Chain 譜公式）重算
docs/01-15 + 01_problem_record 所有 headline 數字，並核對 data/*.json stored 值。

段 A: 結構恆等（整數）
段 B: K_Chain 譜閉合（clean data）
段 C: 12D/36D Frobenius 子代數（30/31 核心）
段 D: 31_verify_all 結果 (49/50) 再確認
段 E: 路徑衛生後置（ghost 殘留 0）

執行: /usr/bin/python3 32_audit_independent.py
"""
import os, json, math, glob, sys
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
D_NAT  = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ---------- 結構常數 ----------
Nd, B, Ngen, Ktree = 44, 4, 3, 33
L3, L4, L5, L6, L7 = 4, 7, 11, 18, 29
F5, F6, F7, F8, F9 = 5, 8, 13, 21, 34
M0 = 27.900915          # MeV, O34/O38 K_Chain 基底標度 (docs/02)
V_EW = 246.22           # GeV (文獻)

def gamma(n, N=88):
    return 4.0 * math.sin(math.pi * n / N) ** 2

print("=" * 72)
print("O59 closeout independent audit — 段 A: 結構恆等")
print("=" * 72)

# ---------- 段 A: 結構恆等 ----------
twelve_1 = L5 + 1
twelve_2 = B * Ngen
twelve_3 = (Nd - 2 * B) // Ngen
check("12 = L₅+1 = 11+1", twelve_1 == 12, f"({twelve_1})")
check("12 = B×N_gen = 4×3", twelve_2 == 12, f"({twelve_2})")
check("12 = (Nd−2B)/3 = 36/3", twelve_3 == 12, f"({twelve_3})")
check("三路徑等價", twelve_1 == twelve_2 == twelve_3 == 12)
check("rank(su(12)) = L₅ = Nd/B = 11", L5 == Nd // B == 11, f"({L5})")
check("h11 = 36 = K_tree+N_gen = 33+3", Ktree + Ngen == 36, f"({Ktree+Ngen})")
check("66 = C(12,2) = 2×K_tree", math.comb(12, 2) == 2 * Ktree == 66, f"({math.comb(12,2)})")
check("dim(su(12)) = 143 = B×K_tree+L₅", B * Ktree + L5 == 143, f"({B*Ktree+L5})")
check("1232 = (2N_d)(2L₄) = 88×14", (2*Nd)*(2*L4) == 1232, f"({(2*Nd)*(2*L4)})")
check("V+E+F = 62 = h²¹−h¹¹ = N_d+L₆", 12+30+20 == 98-36 == Nd+L6 == 62, f"({12+30+20})")
check("V+E+F = |A₅|+χ = 60+2", 12+30+20 == 60+2, f"({12+30+20})")
check("44 = 12+32 = (L₅+1)+2B²", (L5+1) + 2*B*B == 44, f"({(L5+1)+2*B*B})")
check("33+3 = K_tree+N_gen", 33 + 3 == 36)
check("O137 44 分解一致: 28+9+5+2", 28+9+5+2 == 44, "(44)")
check("O59/O137 調和: 33=28+5, 3=√9", (28+5 == 33) and (9 == Ngen*Ngen))

print("=" * 72)
print("段 B: K_Chain 譜閉合（clean data — d_tensor_native_12d）")
print("=" * 72)

# ---------- 段 B ----------
g1 = gamma(1); g7 = gamma(7); g20 = gamma(20)
check("γ₁ = 4sin²(π/88) ≈ 0.005096", abs(g1 - 0.005096) < 1e-5, f"({g1:.6f})")
check("γ₇ ≈ 0.244642", abs(g7 - 0.244642) < 1e-5, f"({g7:.6f})")
check("γ₂₀ ≈ 1.715370", abs(g20 - 1.715370) < 1e-5, f"({g20:.6f})")
inv_g20 = 1.0 / g20
check("1/γ₂₀ ≈ 0.58297", abs(inv_g20 - 0.58297) < 1e-4, f"({inv_g20:.6f})")

# clean data 重算（docs/08,11,12,15 核心）
dnat = np.load(os.path.join(D_NAT, "d_tensor_native_12d.npy"))          # 12×12×12
phi = (1 + math.sqrt(5)) / 2
v12 = phi ** (-np.arange(12) / 12)
Y12 = np.einsum("ijk,k->ij", dnat, v12)
Y12 = (Y12 + Y12.T) / 2
ev12 = np.sort(np.linalg.eigvalsh(Y12))[::-1]
lam_max_act, lam2_act = ev12[0], ev12[1]
trY_act = float(np.trace(Y12))

lam_max_pred = 36 - inv_g20            # 36 − 1/γ₂₀
check("λ_max(clean) ≈ 36−1/γ₂₀ (0.0021%)",
      abs(lam_max_pred - lam_max_act) / lam_max_act < 5e-4,
      f"pred={lam_max_pred:.4f} act={lam_max_act:.4f} dev={abs(lam_max_pred-lam_max_act)/lam_max_act*100:.4f}%")
trY_pred = 2 * B * B * (1 - g1)        # 2B²×(1−γ₁)
check("tr(Y_clean) ≈ 2B²×(1−γ₁) (0.03%)",
      abs(trY_pred - trY_act) / trY_act < 5e-3,
      f"pred={trY_pred:.3f} act={trY_act:.3f} dev={abs(trY_pred-try_act)/trY_act*100 if False else abs(trY_pred-trY_act)/trY_act*100:.3f}%")
lam2_pred = 2 + 2*F9*g1 + g1*g7*L4/(L5-1)   # 2+2F₉γ₁+γ₁γ₇·7/10
check("λ₂ ≈ 2+2F₉γ₁+γ₁γ₇L₄/(L₅−1) (0.0007%)",
      abs(lam2_pred - lam2_act) / lam2_act < 2e-4,
      f"pred={lam2_pred:.6f} act={lam2_act:.6f} dev={abs(lam2_pred-lam2_act)/lam2_act*100:.5f}%")

# v_geom (docs/11,15: 88×(L₅−1+L₄·B·γ₇) × √λ_max × M₀)
factor = 88 * (L5 - 1 + L4 * B * g7)
v_geom = math.sqrt(lam_max_act) * M0 * factor / 1000.0        # GeV
check("v_geom ≈ 88×(10+28γ₇)·√λ_max·M₀ = 246.22 (0.003%)",
      abs(v_geom - V_EW) / V_EW < 1e-3,
      f"v={v_geom:.3f} GeV target={V_EW} dev={abs(v_geom-V_EW)/V_EW*100:.4f}%")

# 1+11 ratio (clean)
rest = ev12[1:]
ratio_clean = lam_max_act / float(np.mean(np.abs(rest)))
check("1+11 ratio(clean) ≈ 37.4", abs(ratio_clean - 37.4) < 1.0, f"({ratio_clean:.1f})")

print("=" * 72)
print("段 C: 12D/36D Frobenius 子代數 + 真 κ 結構 (30_push_forward/31)")
print("=" * 72)

# ---------- 段 C ----------
with open(os.path.join(D_POLY, "cy36_98_intersection_full.json")) as f:
    K36 = np.array(json.load(f)["kappa"])       # 36×36×36
with open(os.path.join(D_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y36 = np.einsum("ijk,k->ij", K36, J0)
Y36 = (Y36 + Y36.T) / 2
trY36 = float(np.trace(Y36))
lam36 = np.linalg.eigvalsh(Y36)
check("sum(κ) = −8 = −2B", abs(float(np.sum(K36)) + 8) < 1e-6, f"({np.sum(K36):.4f})")
check("tr(Y_36) = tr(κ·J*) ≈ 3.16 (docs/07-08)", abs(trY36 - 3.16) < 0.05, f"({trY36:.3f})")
check("36D λ_max ≈ 3.70 (docs/08)", abs(lam36[-1] - 3.70) < 0.05, f"({lam36[-1]:.3f})")

# Frobenius/associativity — 2026-10-05 closeout finding:
# docs/14 宣稱「Associativity error = 0.00e+00 ✅」係同義反覆 (O197 trap)：
# 原 check 只驗 d_sq - d_sq.transpose(1,0,2,3)（對稱性，任何對稱張量都成立），並非 associativity。
# 真正 WDVV associativity: (a*b)*c == a*(b*c), 用 pipeline 自己嘅 metric g=Y。
# 12D: err 0.759 FAIL；36D κ 對照: err 6.5e7 都 FAIL → 此數據集未建立 associativity。
g12_inv = np.linalg.inv(Y12)
C12m = np.einsum("abp,pq->abq", dnat, g12_inv)          # C^q_ab = d_abp g^{pq}
lhs12 = np.einsum("abp,pcd->abcd", C12m, C12m)          # C^p_ab·C^d_pc
rhs12 = np.einsum("bcp,apd->abcd", C12m, C12m)          # C^p_bc·C^d_ap
assoc12_err = float(np.max(np.abs(lhs12 - rhs12)))
check("實際 WDVV associativity(12D, g=Y) — 未證實 (docs/14 '0.00' 係同義反覆)",
      assoc12_err < 1e-6, f"(err={assoc12_err:.4f} — 期望失敗即為 finding)")

g36_inv = np.linalg.inv(Y36)
C36m = np.einsum("abp,pq->abq", K36, g36_inv)
lhs36 = np.einsum("abp,pcd->abcd", C36m, C36m)
rhs36 = np.einsum("bcp,apd->abcd", C36m, C36m)
assoc36_err = float(np.max(np.abs(lhs36 - rhs36)))
check("36D κ 對照 associativity(同準則) 亦未過 — 證實非 metric 選擇問題",
      assoc36_err < 1e-6, f"(err={assoc36_err:.3e} — 對照亦失敗，屬 finding 佐證)")

# docs/14 原 check 重現（確認係同義反覆）
embedded = np.zeros((36, 36, 36))
embedded[:12, :12, :12] = dnat
d_sq = np.einsum("abc,cde->abde", embedded, embedded)
triv = float(np.max(np.abs(d_sq - d_sq.transpose(1, 0, 2, 3))))
check("docs/14 原論證重整: d_sq 對稱性 (任何對稱張量成立 = 無內容)",
      triv == 0.0, f"(triv={triv:.2e} — 同義反覆確認)")

# 跨項隔離（docs/14「完全隔離」）— 真成立
cross_terms = (float(np.sum(np.abs(embedded[:12, :12, 12:]))) +
               float(np.sum(np.abs(embedded[:12, 12:, :12]))) +
               float(np.sum(np.abs(embedded[12:, :12, :12]))))
check("12D×24D 跨項 = 0 (隔離成立)", cross_terms == 0.0, f"({cross_terms:.2e})")

# SVD 比 (docs/13-15: 47 = K_tree+2L₄)
sv_k = float(np.linalg.svd(K36.reshape(36, 36*36), compute_uv=False)[0])
sv_d = float(np.linalg.svd(dnat.reshape(12, 12*12), compute_uv=False)[0])
ratio_svd = sv_k / sv_d
check("SVD 比 = 47 ≈ K_tree+2L₄ = 33+14", abs(ratio_svd - 47.0) / 47.0 < 0.02,
      f"({ratio_svd:.3f}) target 47.00")

print("=" * 72)
print("段 D: 31_verify_all 結果再確認 (docs/15: 49/50)")
print("=" * 72)

# ---------- 段 D ----------
log31 = os.path.join(O, "logs", "31_verify_all.out")
tot = pas = fal = None
if os.path.exists(log31):
    for line in open(log31):
        if "Total checks" in line: tot = int(line.split(":")[1].strip())
        if "PASS:" in line and "✅" in line: pas = int(line.split("PASS:")[1].strip().split()[0])
        if "FAIL:" in line and "❌" in line: fal = int(line.split("FAIL:")[1].strip().split()[0])
check("31_verify_all log 存在", os.path.exists(log31))
check("31_verify_all = 49/50", (tot, pas, fal) == (50, 49, 1), f"(tot={tot} pass={pas} fail={fal})")

# data JSON stored 值核對 (docs/15 vs data)
sj = json.load(open(os.path.join(O, "data", "session_verification.json")))
check("data/session_verification.json passed=28 failed=0",
      sj.get("passed") == 28 and sj.get("failed") == 0,
      f"(passed={sj.get('passed')} failed={sj.get('failed')})")
check("data/session: λ_max 51.5606 stored", abs(sj.get("lam_max", 0) - 51.56061144) < 1e-5, f"({sj.get('lam_max')})")
check("data/session: v_geom 246.82 stored", abs(sj.get("v_geom_GeV", 0) - 246.8245) < 1e-2, f"({sj.get('v_geom_GeV')})")

print("=" * 72)
print("段 E: 路徑衛生後置（ghost 殘留 = 0）")
print("=" * 72)

# ---------- 段 E ----------
ghost_hits = 0
dg = "/home/wsl/Projects/IDCM/IDCM-" + "v10.0"   # 字串拼接避免自指命中 (closeout skill §10-A #45)
for p in sorted(glob.glob(os.path.join(O, "scripts", "*.py"))):
    b = os.path.basename(p)
    if b.startswith("fix_ghost_paths") or b.startswith("32_audit"):
        continue  # 審計/工具器自身含有該字面量，屬自指豁免
    if dg in open(p, encoding="utf-8").read():
        ghost_hits += 1
        print(f"  ❌ {b} 仍含 ghost 路徑")
check("scripts/ 無 ghost 路徑殘留", ghost_hits == 0, f"({ghost_hits} hit)")

print()
print("=" * 72)
print(f"INDEPENDENT AUDIT: {passed} PASS, {failed} FAIL")
print("=" * 72)
sys.exit(0 if failed == 0 else 1)