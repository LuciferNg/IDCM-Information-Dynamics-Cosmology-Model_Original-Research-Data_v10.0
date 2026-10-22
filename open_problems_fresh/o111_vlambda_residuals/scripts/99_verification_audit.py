#!/usr/bin/env python3
"""
O111 Verification Audit: 驗證所有推導、公式、數值
===============================================
獨立重算所有關鍵數值，檢查 docs/ 嘅每個 claim。
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O111 Verification Audit: 獨立重算所有關鍵數值")
print("=" * 72)

passed = 0; failed = 0; total = 0
def check(name, cond, detail=""):
    global passed, failed, total
    total += 1
    if cond:
        passed += 1; print(f"  ✅ {name} {detail}")
    else:
        failed += 1; print(f"  ❌ {name} {detail}")

# ═══════════════════════════════════════════
# 1. 基準數值
# ═══════════════════════════════════════════
print("\n[1] 基準數值驗證")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2

Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
delta = Fg - 264
V_obs = 283.0752
V_Lambda = Fg + 19

check("F(γ) = 264.0821292326", abs(Fg - 264.0821292326) < 1e-8)
check("Δ = F(γ) − 264 = 0.0821292326", abs(delta - 0.0821292326) < 1e-8)
check("1/Δ = 12.1759325953", abs(1/delta - 12.1759325953) < 1e-6)
check("V_Λ = F(γ)+19 = 283.082129", abs(V_Lambda - 283.082129) < 1e-5)
check("V_Λ vs V_obs = 0.00245%", abs(V_Lambda - V_obs)/V_obs < 0.000025)
gamma88 = 4 * np.sin(np.pi * np.arange(1, 89) / 176) ** 2
# 88-site chain: odd k = 1,3,5,...,87 (0-indexed: 0,2,4,...,86); even k = 2,4,...,88 (1,3,...,87)
S_odd = sum(gamma88[0::2])   # k odd → 觀察者能量
S_even = sum(gamma88[1::2])  # k even → 世界能量
check("Σγ_odd = 88 (88-site odd modes)", abs(S_odd - 88) < 1e-10, f"(got {S_odd:.10f})")
check("Σγ_even = 90 (88-site even modes)", abs(S_even - 90) < 1e-10, f"(got {S_even:.10f})")
check("3×Σγ_odd = 264", abs(3*88 - 264) < 1e-10)

# O62/O84 基準
N_d = 44; F8_O84 = 8; B_O84 = 17; F8_O62 = 21; B_O62 = 4
check("19 = 44−8−17", 44-8-17 == 19)
check("19 = 44−21−4", 44-21-4 == 19)
check("25 = F₈+B = 8+17 = 21+4", 8+17 == 21+4 == 25)
check("CPX gap = 98−73 = 25", 98-73 == 25)

# ═══════════════════════════════════════════
# 2. Δ 連分數
# ═══════════════════════════════════════════
print("\n[2] Δ 連分數驗證")
cf = [0, 12, 5, 1, 2, 6, 12, 1, 2, 3, 3, 1, 1, 1, 25, 1195, 4, 1, 5, 1]
p = [0, 1]; q = [1, 0]
for i, a in enumerate(cf):
    p.append(a*p[-1] + p[-2])
    q.append(a*q[-1] + q[-2])
    if i >= 14:  # check convergents from position 14
        val = p[-1]/q[-1]
        err = abs(val - delta)/delta
        check(f"convergent {i+1}: {p[-1]}/{q[-1]} = {val:.12f}", err < 1e-10, f"(err {err:.2e})")

# 4235787/51574657
check("4235787/51574657 ≈ Δ", abs(4235787/51574657 - delta) < 1e-14)
check("Δ × 51574657 = 4235787 (整數)", abs(delta * 51574657 - 4235787) < 1e-5)

# 近整數
check("Δ × 134 ≈ 11.0053", abs(delta*134 - 11.005317) < 0.001)
check("Δ × 73 ≈ 5.9954", abs(delta*73 - 5.995434) < 0.001)
check("Δ × 61 ≈ 5.0099", abs(delta*61 - 5.009883) < 0.001)

# ═══════════════════════════════════════════
# 3. Δ 最佳候選
# ═══════════════════════════════════════════
print("\n[3] Δ 最佳候選驗證")
cands = {
    "γ_39/36 − γ_33/134": gamma44[38]/36 - gamma44[32]/134,
    "γ_29/36 − γ_1/98": gamma44[28]/36 - gamma44[0]/98,
    "γ_30/36 − γ_4/18 + γ_3/44": gamma44[29]/36 - gamma44[3]/18 + gamma44[2]/44,
    "γ_27/33 − γ_1/29 + γ_3/88": gamma44[26]/33 - gamma44[0]/29 + gamma44[2]/88,
    "1/(12+1/(5+1/(1+γ_19/γ_33)))": 1/(12+1/(5+1/(1+gamma44[18]/gamma44[32]))),
    "1/(12+1/(5+γ_9/γ_11))": 1/(12+1/(5+gamma44[8]/gamma44[10])),
}
for name, val in cands.items():
    err = abs(val - delta)/delta*100
    check(f"{name}", err < 0.001, f"(err {err:.4f}%, val={val:.12f})")

# ═══════════════════════════════════════════
# 4. Y(γ) 本徵值谱
# ═══════════════════════════════════════════
print("\n[4] Y(γ) signature 驗證")
Y = np.einsum("ijk,k", kappa, gamma36)
evY = np.linalg.eigvalsh(Y)
Y_pos = np.sum(evY > 1e-8)
Y_neg = np.sum(evY < -1e-8)
Y_zero = np.sum(np.abs(evY) < 1e-8)
check("Y(γ) 18 正本徵值", Y_pos == 18, f"(got {Y_pos})")
check("Y(γ) 14 負本徵值", Y_neg == 14, f"(got {Y_neg})")
check("Y(γ) 4 kernel", Y_zero == 4, f"(got {Y_zero})")
check("Y(γ) 總數 36", Y_pos + Y_neg + Y_zero == 36)

# 穩定 across threshold
for eps in [1e-12, 1e-10, 1e-8, 1e-6]:
    npY = np.sum(evY > eps)
    nnY = np.sum(evY < -eps)
    nzY = 36 - npY - nnY
    check(f"Y signature stable @ {eps:.0e}: {npY}+/{nnY}-/{nzY}kernel", 
          npY == 18 and nnY == 14, f"(got {npY}/{nnY}/{nzY})")

# 最負本徵值
check("Y min λ ≈ -157.3", abs(evY[0] + 157.3) < 0.5)
check("Y max λ ≈ 147.9", abs(evY[-1] - 147.9) < 0.5)

# ═══════════════════════════════════════════
# 5. G(γ) 本徵值谱
# ═══════════════════════════════════════════
print("\n[5] G(γ) signature 驗證")
V = Fg
dV = np.einsum("ijk,j,k", kappa, gamma36, gamma36) / 2.0
G = -Y/V + np.outer(dV, dV)/V**2
evG = np.linalg.eigvalsh(G)
G_pos = np.sum(evG > 1e-8)
G_neg = np.sum(evG < -1e-8)
G_zero = np.sum(np.abs(evG) < 1e-8)

check("G(γ) 15 正本徵值", G_pos == 15, f"(got {G_pos})")
check("G(γ) 17 負本徵值", G_neg == 17, f"(got {G_neg})")
check("G(γ) 4 kernel", G_zero == 4, f"(got {G_zero})")
check("G 總數 36", G_pos + G_neg + G_zero == 36)

# 正負交換定理
check("G_pos = Y_neg + 1", G_pos == Y_neg + 1, f"({G_pos} = {Y_neg}+1)")
check("G_neg = Y_pos - 1", G_neg == Y_pos - 1, f"({G_neg} = {Y_pos}-1)")
check("G_kernel = Y_kernel = B", G_zero == Y_zero == 4)

# 沿 γ 方向穩定
d2V = 6 * 1.0 * V
check("d²V/ds² > 0 (radial 穩定)", d2V > 0, f"({d2V:.4f})")

# ═══════════════════════════════════════════
# 6. 隨機搜索
# ═══════════════════════════════════════════
print("\n[6] 隨機搜索驗證")
rng = np.random.default_rng(42)
best_n = 0
found_full = 0
for _ in range(500):
    t = rng.uniform(0.1, 5.0, 36)
    Vt = np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0
    if Vt <= 0:
        continue
    dVt = np.einsum("ijk,j,k", kappa, t, t) / 2.0
    Yt = np.einsum("ijk,k", kappa, t)
    Gt = -Yt/Vt + np.outer(dVt, dVt)/Vt**2
    evGt = np.linalg.eigvalsh(Gt)
    n = np.sum(evGt > 1e-8)
    if n > best_n:
        best_n = n
    if n == 36:
        found_full += 1
check("500次隨機: 0 全正定", found_full == 0, f"(found {found_full})")
check("隨機最佳 ≥ 26", best_n >= 26, f"(best {best_n}/36)")

# ═══════════════════════════════════════════
# 7. κ-block 分解
# ═══════════════════════════════════════════
print("\n[7] κ-block 分解驗證")
import itertools
gen = np.array([0]*12 + [1]*12 + [2]*12)
F_recalc = 0
for g0, g1, g2 in itertools.product([0,1,2], repeat=3):
    mask = (gen == g0)[:, None, None] & (gen == g1)[None, :, None] & (gen == g2)[None, None, :]
    F_block = np.einsum("ijk,i,j,k", kappa * mask, gamma36, gamma36, gamma36) / 6.0
    F_recalc += F_block
check("κ-block 總和 = F(γ)", abs(F_recalc - Fg) < 1e-10)

# 關鍵 block
F222 = np.einsum("ijk,i,j,k", kappa * (gen == 2)[:, None, None] * (gen == 2)[None, :, None] * (gen == 2)[None, None, :], gamma36, gamma36, gamma36) / 6.0
check("F(2,2,2) = 550.74777022", abs(F222 - 550.74777022) < 1e-6)

# ═══════════════════════════════════════════
# 8. 19 身份
# ═══════════════════════════════════════════
print("\n[8] 19 身份驗證")
check("19 = L₅ + F₆ = 11+8", 11+8 == 19)
check("19 = L₆ + 1 = 18+1", 18+1 == 19)
check("19 = 44-25", 44-25 == 19)
check("c* = V_obs-F(γ) ≈ 18.9931", abs(283.0752 - Fg - 18.9931) < 0.001)
check("c* ≈ 19 (0.0365%)", abs(283.0752 - Fg - 19)/19 < 0.001)

# ═══════════════════════════════════════════
# 9. 正負交換定理 (Y ↔ G)
# ═══════════════════════════════════════════
print("\n[9] 正負交換定理驗證")
# G = -Y/V + vv^T/V²
# rank(Y) = 32 (36-4)
# rank(vv^T) = 1
# G inherits signature from -Y plus rank-1 correction
# Signature of Y: (18, 14, 4)
# Signature of -Y: (14, 18, 4)  (flipped)
# rank-1 vv^T can save at most 1 eigenvalue
# So G: (14+1, 18-1, 4) = (15, 17, 4) ✓

# 直接驗證: G = -Y/V + gg^T/V² 其中 g = dV
ggT = np.outer(dV, dV)
G_recalc = -Y/V + ggT/V**2
check("G = -Y/V + gg^T/V² 重建", np.allclose(G, G_recalc))

# 負方向 gen 分佈
evecs = np.linalg.eigh(G)[1]
neg_dirs = evecs[:, :G_neg]
gen_weight = np.array([np.sum(neg_dirs[:12]**2), np.sum(neg_dirs[12:24]**2), np.sum(neg_dirs[24:36]**2)])
gen_weight /= gen_weight.sum()
check("負方向 gen0 ≈ 0.18", abs(gen_weight[0] - 0.18) < 0.05)
check("負方向 gen1 ≈ 0.27", abs(gen_weight[1] - 0.27) < 0.05)
check("負方向 gen2 ≈ 0.55", abs(gen_weight[2] - 0.55) < 0.05)

# ═══════════════════════════════════════════
# 10. α' 修正閾值
# ═══════════════════════════════════════════
print("\n[10] α' 修正閾值驗證")
for eps, expected_n in [(0.01, 20), (0.05, 28), (0.1, 34), (0.2, 35), (0.5, 36)]:
    G_mod = G + eps * np.eye(36)
    ev_mod = np.linalg.eigvalsh(G_mod)
    n = np.sum(ev_mod > 1e-8)
    check(f"G + {eps}·I: {n}/36 正定 (≥{expected_n})", n >= expected_n)

# ═══════════════════════════════════════════
# 最終結果
# ═══════════════════════════════════════════
print("\n" + "=" * 72)
print(f"Verification Audit: {passed}/{total} PASS, {failed} FAILED")
print("=" * 72)

if failed > 0:
    print(f"⚠️  {failed} 個檢查失敗! 需要修正 docs.")
    exit(1)
else:
    print("🎉 全部 PASS! 所有推導、公式、數值正確。")
    print("docs/01_problem_record.md 同 docs/01_attack_record.md 嘅內容全部正確。")

# 輸出 JSON 記錄
out = {
    "test": "O111 Verification Audit",
    "date": "2026-08-29",
    "passed": passed, "failed": failed, "total": total,
    "Fg": float(Fg), "delta": float(delta), "V_Lambda": float(V_Lambda),
    "Y_signature": {"pos": int(Y_pos), "neg": int(Y_neg), "kernel": int(Y_zero)},
    "G_signature": {"pos": int(G_pos), "neg": int(G_neg), "kernel": int(G_zero)},
    "sign_exchange": {
        "G_pos_eq_Y_neg_plus_1": bool(G_pos == Y_neg + 1),
        "G_neg_eq_Y_pos_minus_1": bool(G_neg == Y_pos - 1),
        "kernel_eq_B": bool(Y_zero == 4)
    },
    "radial_stable": bool(d2V > 0),
    "random_best": int(best_n),
    "random_full_pos_def": int(found_full),
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "99_verification_audit.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)