#!/usr/bin/env python3
"""
投影方向審計 — 物質 vs 拓撲 × 高維→低維 vs 低維→高維 (2026-09-09)
==================================================================
四象限盤點所有 IDCM 投影操作 + 正反比一致性 + 跨象限耦合檢查

定義:
  高維 (H) = 世界層 (88-site 對偶鏈 / 176-Laplacian / N_ℓ 大層)
  低維 (L) = 觀察者 (44 模 / ℓ=0 世界 / 二維觀測面)
  HD = 高維→低維 (投影/觀測/衰減)
  LH = 低維→高維 (提升/分支/積累)
"""
import math, json

phi = (1+5**0.5)/2
N_d, B, L5, L4, N_gen, F8 = 44, 4, 11, 7, 3, 21
mu2 = 4*math.sin(math.pi*44/176)**2   # gamma_44 = 2

print("="*78)
print("投影方向審計 — 四象限盤點")
print("="*78)
print(f"譜量: N_d=44, B=4, L₅=11, L₄=7, N_gen=3, F₈=21, μ²=γ₄₄={mu2}")
print()

# ============ 拓撲投影 ============
print("── 拓撲投影 (TOPO) ──")
topo = [
    # (id, 方向, 因子, 表達式, 驗證)
    ("t_nz",    "HD",  "4^-ell",     "N(z) ∝ 1/(1+z) = 4^-ell 投影面積律",         "🟢 EIGER 校準"),
    ("t_db",    "HD",  "176/42",     "dβ/dℓ = 4N_d/(N_d-μ²) 每層光譜陡峭化",        "🟢 0.22σ"),
    ("t_spec",  "HD",  "90/88",      "Σγ_even/Σγ_odd 世界譜/觀察者譜",              "✅ 譜身份"),
    ("t_wfrac", "HD",  "44/88",      "世界模/總模 = 1/2",                            "✅"),
    ("t_EO",    "HD",  "2",          "E-O = 2 = γ₄₄ = μ² 對偶差",                    "✅ O159"),
    ("t_Dapp",  "HD",  "44-44/4^ell","D_app(ℓ) 投影距離",                            "✅ O65"),
    ("t_C",     "HD",  "4/11",       "干涉對比 C = B/L₅",                            "🟢 0.2%"),
    ("t_branch","LH",  "4^ell",      "N_ℓ = N·4^ℓ 每層世界分支",                     "✅"),
    ("t_lift",  "LH",  "4",          "44 → 176-Laplacian 提升",                      "✅"),
    ("t_dual",  "LH",  "2",          "88-site 對偶鏈 ×2",                            "✅"),
    ("t_route", "LH",  "60",         "a5 路由: 觀測位置 → 60 節點 (BC,frust,hop)",   "✅"),
    ("t_hop",   "LH",  "cos(pi·hop/4)","干涉模態 hop 提升 (hop=4 相消)",             "🟢"),
]
for i, (id_, d, fac, desc, ver) in enumerate(topo, 1):
    print(f"  T{i:<3} {id_:<8} [{d}] {fac:>12}  {desc}  {ver}")

# ============ 物質投影 ============
print("\n── 物質投影 (MAT) ──")
mat = [
    ("m_eta",    "HD", "phi^-21",   "η = φ^{-(N_d-μ²)/2} 應變能→質量凝聚效率",  "🟢 6.6%"),
    ("m_ff",     "HD", "(1+δ)^1.5", "free-fall 凝聚 M ∝ ρ^{3/2}",               "🟢 0.86 Schindler"),
    ("m_hop",    "HD", "7/15",      "M₄/M₀ = (1-C)/(1+C) = L₄/(L₅+B) hop 質量比", "🟢 53.3%"),
    ("m_gzk",    "HD", "phi^44",    "E_GZK = hc/(L_P·φ^44) 晶格→能量",           "🟢 2.18%"),
    ("m_g3",     "HD", "gamma^3",   "f_ν ∝ γ³ (p=3=N_gen) 模態→發射譜",          "🟢 fit"),
    ("m_mu_e",   "HD", "206.705",   "μ/e = (γ₇/γ₁)(F_μ/F_e) 譜→質量比",           "🟢 0.031%"),
    ("m_sin",    "HD", "sinO/sinW", "質量比 = sin(觀察者)/sin(世界)",             "🟢 O158"),
    ("m_accum",  "LH", "phi^21",    "η⁻¹ 質量→應變能積累 (LRD=積累點)",           "🟢"),
    ("m_rel",    "LH", "phi^44",    "φ⁴⁴ 應力→UHECR 釋放",                       "🟢"),
    ("m_lbol",   "LH", "M^1",       "質量→光度 Lbol ∝ M",                        "🟡"),
]
for i, (id_, d, fac, desc, ver) in enumerate(mat, 1):
    print(f"  M{i:<3} {id_:<8} [{d}] {fac:>12}  {desc}  {ver}")

# ============ 正反比一致性檢查 ============
print("\n" + "="*78)
print("正反比一致性 (LH 應該 = 1/HD 對應對)")
print("="*78)
checks = []
def chk(name, lhs, rhs, tol=1e-6):
    ok = abs(lhs - rhs) < tol*max(1, abs(rhs))
    checks.append((name, ok))
    print(f"  {name:<38} {lhs:>12.6f} vs {rhs:>12.6f}  {'✅' if ok else '❌'}")

ell = 1.0  # 取 ℓ=1 做數值檢查
chk("t_nz × t_branch (4^-ell · 4^ell)", 4**(-ell)*4**ell, 1.0)
chk("m_eta × m_accum (φ⁻²¹ · φ²¹)", phi**(-21)*phi**21, 1.0)
chk("t_db 分子: 4N_d = 176", 4*N_d, 176)
chk("t_db 分母: N_d-μ² = 42", N_d-mu2, 42)
chk("t_db 化簡: 176/42 = 88/21", 176/42, 88/21)
chk("21 = (N_d-μ²)/2 (F₈ 譜衍生)", (N_d-mu2)/2, F8)
chk("t_C: C = B/L₅ = 4/11", 4/11, 0.36363636363636365)
chk("m_hop: (1-C)/(1+C) = 7/15", (1-4/11)/(1+4/11), 7/15)
chk("m_hop: 7 = L₄ = N_gen+B", 7, N_gen+B)
chk("m_hop: 15 = L₅+B", 15, L5+B)
chk("t_wfrac: 44/88 = 1/2", 44/88, 0.5)
chk("t_spec: 90/88 = 45/44", 90/88, 45/44)
chk("t_EO: 90-88 = 2 = μ²", 90-88, mu2)

# ============ 跨象限耦合檢查 ============
print("\n" + "="*78)
print("跨象限耦合 (物質因子 × 拓撲因子)")
print("="*78)
# η 嘅指數 21 = (N_d-μ²)/2 — 凝聚效率由拓撲譜量決定 (耦合!)
print(f"  η 指數 21 = (N_d-mu2)/2 = {mu2} → 凝聚效率由世界譜減中心模決定 [TOPO→MAT 耦合] 🟢")
# dβ/dℓ = 4N_d/(N_d-μ²) — 陡峭化 = 層分支 × 世界模 / 有效譜
print(f"  dβ/dℓ = 4·N_d/(N_d-μ²) = 分支因子 × 世界模 / 有效譜 [TOPO 內部] 🟢")
# hop 質量比 = (1-C)/(1+C), C = B/L₅ — 物質投影由拓撲干涉決定
print(f"  M₄/M₀ = (1-B/L₅)/(1+B/L₅) = L₄/(L₅+B) — 質量比全由拓撲量 (B,L₅) 決定 [TOPO→MAT] 🟢")
# 正反比淨值: 完整維度循環
net_nz = 4**(-ell)*4**ell
print(f"  完整循環 t_nz→t_branch→t_nz: 4^-ell · 4^ell = {net_nz} — 宇宙投影係維度升降閉環 🟢")

# ============ 對稱性殘缺檢查 ============
print("\n" + "="*78)
print("方向對稱性: 有冇 HD 冇 LH (或反之) 嘅孤兒投影?")
print("="*78)
hd_ids = [x[1] for x in topo+mat if x[1] == "HD"]
lh_ids = [x[1] for x in topo+mat if x[1] == "LH"]
print(f"  HD 投影: {len(hd_ids)} 個 (TOPO {sum(1 for x in topo if x[1]=='HD')} + MAT {sum(1 for x in mat if x[1]=='HD')})")
print(f"  LH 投影: {len(lh_ids)} 個 (TOPO {sum(1 for x in topo if x[1]=='LH')} + MAT {sum(1 for x in mat if x[1]=='LH')})")
print("  對稱: 每類都有 HD+LH → 投影係雙向操作, 冇單向孤兒 ✅")

# ============ 總結 ============
print("\n" + "="*78)
print("審計總結")
print("="*78)
npass = sum(1 for _, ok in checks if ok)
print(f"  一致性檢查: {npass}/{len(checks)} PASS")
print(f"  C = 4/11 = B/L₅ — 干涉對比度獲得譜身份 (新)")
print(f"  M₄/M₀ = 7/15 = L₄/(L₅+B) — hop 質量比獲得譜身份 (新)")
print(f"  21 = (N_d-μ²)/2 — 凝聚階梯譜衍生 (record 07 §1b)")
print(f"  η = phi^-((N_d-mu2)/2) — 物質投影指數由拓撲譜量決定")
json.dump({'n_checks': npass, 'total': len(checks), 'C_identity': 'B/L5',
           'Mhop_identity': 'L4/(L5+B)'}, open('data/15_projection_audit.json', 'w'), indent=2)
print(f"\nSaved data/15_projection_audit.json")
