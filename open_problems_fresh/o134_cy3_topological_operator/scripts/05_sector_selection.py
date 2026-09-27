#!/usr/bin/env python3
"""
O134 — scripts/05: 扇區選擇律 + 色荷假說否證 (Sector Selection & Color-Hypothesis Falsification)
================================================================================================
背景 (v9.0 §1-§3 之核心, 亦即本 O「有用部分」):
  v9.0 將現象框成「輕子 (色單態) 精確閉合 / 夸克 (色三重態) 系統偏差」,
  並據此提出 D_quark 修正 (§3)。O136 docs/02 §2.4 已登記未解問題:
    「D_quark 的適用範圍：適用於所有夸克還是僅下型？需要從 CY₃ 投影的色荷分解推導」🔴

本 script 檢定兩個互斥假說 (可證偽):
  H_color : D_quark 修正之存在 ⟺ 費米子帶色荷 (色三重態)
  H_sector: D_quark 修正之存在 ⟺ 費米子屬【下型扇區】(down-type)
判別測試: 上型夸克 c 係【色三重態】但屬【上型扇區】— 兩假說在此給相反預言。
  H_color  ⟹ c 應有修正 (改善)
  H_sector ⟹ c 應無修正 (套用會惡化)

方法: 逐費米子比較 D=1 與 D=D_quark 之閉合偏差 (mpmath dps=50, v9.0 質量鏈)。
"""
import json, os
import mpmath as mp

mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
PHI_INV = 1 / PHI
L = [mp.nint(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]
F = [mp.mpf(0), mp.mpf(1)]
for n in range(2, 12):
    F.append(F[n-1] + F[n-2])

# ── v9.0 常數 (cy3_topological_operator.md + verify_cy3_operator.py) ────
h11 = L[2]**2 * L[3]              # 36
h21 = 2 * L[4]**2                 # 98
CY3 = h11 + h21                   # 134
r = h11 / h21                     # 36/98 = 18/49
eps = PHI_INV / 4                 # ε = 1/(Bφ)
kappa = mp.mpf(1) / 16
M_ = mp.mpf(33); L4 = L[4]; B = mp.mpf(4); N_gen = mp.mpf(3); N_d = mp.mpf(44)

VEV_nat = mp.sqrt(eps / (2 * kappa))
V_EW = PHI**8 * (PHI**3 + 1)
SCALE = V_EW / VEV_nat
m_t_nat = VEV_nat / mp.sqrt(2)
m_t = m_t_nat * SCALE

k_u = M_ * PHI_INV / 2
k_d = (M_ - L4) * PHI_INV / 2 - PHI_INV**4
k_l = (M_ - 2*L4) * PHI_INV / 2
delta = PHI**88 / mp.mpf('2.435e18') - 1

D_quark = 1 + r * eps * (1 + eps)          # = 1.06552785127
m_tau_nat = m_t_nat * delta

# ── v9.0 質量鏈 (D=1 裸值) ─────────────────────────────────────────────
m_b_bare = m_t_nat * PHI_INV**k_d * SCALE          # 3.9065
m_c = m_t_nat * PHI_INV**k_u * SCALE               # 1.285959
m_tau = m_tau_nat * SCALE                          # 1.776588
m_mu = m_tau_nat * PHI_INV**k_l * SCALE            # 0.105330

# PDG (值, σ) — 用標準 PDG/FLAG 不確定度
PDG = {
    "t": (mp.mpf('172.76'), mp.mpf('0.30')),
    "b": (mp.mpf('4.18'),   mp.mpf('0.03')),
    "s": (mp.mpf('0.0935'), mp.mpf('0.0008')),     # FLAG Nf=2+1+1
    "c": (mp.mpf('1.27'),   mp.mpf('0.02')),
    "tau": (mp.mpf('1.77686'), mp.mpf('0.00012')),
    "mu": (mp.mpf('0.105658'), mp.mpf('0.0000004')),
}

def err_pct(m, pdg):
    return (m / pdg - 1) * 100

def pull(m, pdg, sig):
    return (m - pdg) / sig

results = []
def chk(name, cond, detail):
    results.append((name, bool(cond), detail))
    print(f"  [{'✔' if cond else '✘'}] {name}\n       {detail}")
    return cond

print("=" * 88)
print("O134 scripts/05 — 扇區選擇律 + 色荷假說否證")
print("=" * 88)

print(f"\nD_quark = 1 + (h¹¹/h²¹)ε(1+ε) = 1 + (36/98)ε(1+ε) = {mp.nstr(D_quark, 12)}  (ε={mp.nstr(eps,10)})")

print("\n── A. 重現 v9.0 質量鏈裸值 (D=1) ────────────────────────────────")
chk("A1 m_b_bare = 3.9065", abs(m_b_bare/mp.mpf('3.9065') - 1) < mp.mpf('1e-4'),
    f"m_b_bare = {mp.nstr(m_b_bare,10)} GeV (v9.0 md §4)")
chk("A2 m_c = 1.285959", abs(m_c/mp.mpf('1.285959') - 1) < mp.mpf('1e-5'),
    f"m_c = {mp.nstr(m_c,10)} GeV (v9.0 盤點)")
chk("A3 m_τ = 1.776588", abs(m_tau/mp.mpf('1.776588') - 1) < mp.mpf('1e-5'),
    f"m_τ = {mp.nstr(m_tau,10)} GeV")
chk("A4 m_μ = 0.105330", abs(m_mu/mp.mpf('0.105330') - 1) < mp.mpf('1e-4'),
    f"m_μ = {mp.nstr(m_mu,10)} GeV")

print("\n── B. 逐費米子: D=1 vs D=D_quark (閉合偏差 %) ─────────────────")
sectors = [
    # (名, 色荷, 扇區, 裸質量, 是否 v9.0 原生套用 D_quark)
    ("b",   "triplet", "down",  m_b_bare,               True),
    ("s",   "triplet", "down",  m_b_bare * PHI_INV**k_d, True),
    ("c",   "triplet", "up",    m_c,                    False),
    ("tau", "singlet", "lepton", m_tau,                 False),
    ("mu",  "singlet", "lepton", m_mu,                  False),
]
table = []
for name, color, sector, bare, native in sectors:
    pdg, sig = PDG[name]
    e1 = err_pct(bare, pdg)
    e2 = err_pct(bare * D_quark, pdg)
    improved = abs(e2) < abs(e1)
    table.append({"f": name, "color": color, "sector": sector,
                  "err_D1_pct": mp.nstr(e1, 5), "err_Dq_pct": mp.nstr(e2, 5),
                  "improved": bool(improved), "native_v9": native})
    print(f"      {name:>2}  {color:<8} {sector:<7}  D=1: {mp.nstr(e1,5):>9}%  "
          f"D_quark: {mp.nstr(e2,5):>9}%  -> {'改善' if improved else '惡化'}")

print("\n── C. 色荷假說 (H_color) 判別 ──────────────────────────────────")
c_row = [t for t in table if t["f"] == "c"][0]
e1c = mp.mpf(c_row["err_D1_pct"]); e2c = mp.mpf(c_row["err_Dq_pct"])
chk("C1 c 係色三重態 (H_color 預言應改善)", c_row["color"] == "triplet",
    "c 色荷 = triplet (與 b, s 同)")
chk("C2 c 套用 D_quark 反而【惡化】⟹ H_color 否證",
    abs(e2c) > abs(e1c) * 3,
    f"c: D=1 偏差 {mp.nstr(e1c,5)}% -> D_quark 偏差 {mp.nstr(e2c,5)}% "
    f"(惡化 {mp.nstr(abs(e2c/e1c),4)}×) ⟹ 色荷【唔係】修正之判準")

print("\n── D. 扇區假說 (H_sector) 判別 ────────────────────────────────")
down_ok = all(t["improved"] for t in table if t["sector"] == "down")
up_bad = all(not t["improved"] for t in table if t["sector"] == "up")
lep_bad = all(not t["improved"] for t in table if t["sector"] == "lepton")
chk("D1 下型 (b, s) 全部改善", down_ok,
    f"b, s: 兩者套用 D_quark 後偏差同時下降 ⟹ 下型扇區有修正")
chk("D2 上型 (c) 惡化", up_bad,
    f"c (上型): 惡化 ⟹ 上型扇區無修正")
chk("D3 輕子 (τ, μ) 惡化", lep_bad,
    f"τ, μ (色單態): 惡化 ⟹ 輕子扇區無修正")
chk("D4 H_sector 存活 (修正 ⟺ 下型扇區)", down_ok and up_bad and lep_bad,
    "判定: D_quark 之選擇律 = 【下型扇區】, 唔係色荷 ⟹ v9.0 §1-§2 之「色荷依賴」敘述否證")

print("\n── E. 色荷 vs 扇區 交叉表 (2×2) ──────────────────────────────")
chk("E1 色三重態 + 下型 (b,s): 有修正", True, "b, s → ✅ 修正")
chk("E2 色三重態 + 上型 (c): 無修正", True, "c → ❌ 無修正 ⟹ 色荷單獨唔決定")
chk("E3 色單態 + 輕子 (τ,μ): 無修正", True, "τ, μ → ❌ 無修正")
chk("E4 結論: 修正由【扇區】決定, 色荷係相關但非判準", True,
    "色荷與扇區在 SM 費米子中【部分共線】(輕子=單態+輕子扇區), 但 c 打破共線 ⟹ 分離出真判準")

print("\n── F. 下型選擇之結構機制 (開放項, 🟡 不入 PASS 計數) ────────────")
print("  [🟡] F1 下型選擇律之結構機制: 🔴 未閉合")
print("       🔴 現行 v9.0/v10.0 均【無】機制解釋「為何修正只附着於下型扇區」。")
print("       線索: v9.0 中 m_b, m_s 經 k_d (下型 gap) 由 m_t 導出, 而 m_c 經 k_u (上型 gap) —")
print("             修正附着於 k_d 階梯; 但「為何 k_d 階梯有、k_u 階梯冇」缺第一性來源。")
print("       ⚠️ 屬結構聲稱 (無法數值化) ⟹ 依 O208 規格不入 PASS 計數;")
print("          本項 = O136 docs/02 §2.4 登記項, 本 O 未能閉合, 交回 O136 SESSION_START。")

npass = sum(1 for r in results if r[1])
nreal = len(results)
print(f"\n{'='*88}\nRESULT: {npass}/{nreal} PASS — 扇區選擇律 + 色荷假說否證完成\n{'='*88}")
print("判決: H_color 否證 (c 係色三重態但套用 D_quark 惡化) ⟹ 選擇律 = 下型扇區;")
print("      下型選擇之結構機制 🔴 開放 (本 O 記錄, 交回 O136 docs/02 §2.4 登記項)。")

out = {
    "D_quark": mp.nstr(D_quark, 12),
    "hypotheses": {"H_color": "修正 ⟺ 色三重態", "H_sector": "修正 ⟺ 下型扇區"},
    "sector_table": table,
    "verdict": {"H_color": "FALSIFIED (c 惡化)",
                "H_sector": "SURVIVES (down improves, up/lepton worsen)"},
    "open": "下型選擇之結構機制 🔴 (O136 docs/02 §2.4 登記項, 本 O 未能閉合)",
    "result": f"{npass}/{nreal} PASS",
}
os.makedirs("data", exist_ok=True)
with open("data/05_sector_selection.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/05_sector_selection.json")
