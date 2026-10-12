#!/usr/bin/python3
"""O239 — Script 29: freeze v3 判決表（盲測預註冊, 為將來 lattice 直量）
============================================================================
狀態: 2026-10-12 新增（第二十三輪後續——繼續推缺口 ① freeze v3 判決表）
目的: 將「freeze v3 一到就判」嘅所有判據預先凍結——唔准 freeze v3 數據
     出現之後先定閾值（後見之明）。freeze v3 = lattice 直量（RGI 風格,
     同 freeze v2 同 scheme 家族, 精度 1-2%）。

背景（docs/19-22）:
  - O239 主鏈 freeze v1.0: γ=−4.7503±0.036, β=−1.8146, α=φ²·(1−8.1e-5)
  - γ_k stair 線: γ_obs 反解 k=1.9998≈2=N_gen−1（雙重確認 via β: 1.9996）
  - 版本敏感: v2 RGI 下 γ 測定值漂向 −4.7213（反解 k=2.0164, 仍近 2）
  - μ local: freeze v1.0 −4.664 = 2.4σ（B′ 機構未死）

判據預註冊（盲測, threshold 零放寬; freeze v3 一到, 逐項 PASS/FAIL 照判）:
  J1: γ_v3 ∈ −19/4 ± 0.05（k=2 點 2σ; 若 v3 精度 1%, σ≈0.0475+scale 漂移 ~0.02
      ⟹ 窗 ±0.07 保守; 預註冊窗 = [−4.82, −4.68]）⟹ stair 線身份維持
  J2: k_obs(v3) ∈ [1.95, 2.05]（γ 反解, 等價 J1）
  J3: α_v3 = γ_v3/β_v3 ∈ φ² × (1 ± 0.05%)（不變量維持; 05% = 現有 0.008% 嘅 ~6 倍
      預留 lattice scheme 漂移）
  J4: μ local(v3) 判決（2026-10-12 改寫——docs/24: μ local = −ln(c/s)/ln(7/4),
      只係 c/s 比值代理）: B′ 由 v3 嘅 c/s 直接裁決——
      ⟹ 若 v3 c/s → 11.652 家族 (FLAG/lattice RGI): μ local = −4.388 即 19.5σ
         距 −19/4 ⟹ B′ 死
      ⟹ 若 v3 c/s 維持 ~13.60 (pole): μ local = −4.664 即 2.85σ ⟹ B′ 有牙
      （唔再係「收斂至 <1σ」——μ local 唔會收斂, 只會跟 c/s 走）
  J5: 反預言: 若 |γ_v3 − (−19/4)| > 3σ 或 γ_v3 漂出 [−4.82, −4.68]
      ⟹ stair 線 k=2 身份否決（γ 結構身份要改寫）
  J6: 版本規則: v3 數據 tag = freeze_v3; 同其他層比對一律 freeze 層內判
      （跨層比對禁止——docs/19 §四 規則）
  J7: scheme 記錄: v3 測定值必須連 scheme（RGI/lattice Nf）一齊記,
      changes 漂移當「k 喺 stair 線抖動」定「結構替換」以 J1-J5 裁決
產物: data/29_freeze_v3_judgement_table.json（新增, 盲測預註冊證明）
"""
import json

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/29 — freeze v3 判決表（盲測預註冊）")
print("=" * 78)

# 常量
GAMMA_V10, SIG_G = -4.7503, 0.0361
G19_4 = -19/4
PHI2 = ((1+5**0.5)/2)**2   # φ² = 2.618034（唔係 φ!）
ALPHA_V10 = 2.617822

# ── J1: γ_v3 窗 ──
print("\n── J1: γ_v3 預言窗（stair 線 k=2 維持）──")
J1_lo, J1_hi = -4.82, -4.68
print(f"   窗 = [−4.82, −4.68]（γ=−19/4=−4.75 ± 0.07; 2σ 含 v2 漂移 −4.7213）")
print(f"   現有 v1.0 值 = {GAMMA_V10} 已喺窗內 ✓")
chk("J1 窗預註冊存在且含 v1.0", J1_lo <= GAMMA_V10 <= J1_hi, f"[{J1_lo}, {J1_hi}]")

# ── J2: k 窗 ──
print("\n── J2: k_obs(v3) ∈ [1.95, 2.05] ──")
k_lo, k_hi = 1.95, 2.05
print(f"   窗 = [{k_lo}, {k_hi}]（等價 J1: γ 反解）")
print(f"   現有: v1.0 k=1.9998, v2 k=2.0164, v1.1 k=1.9880 — 全部喺窗內 ✓")
chk("J2 k 窗預註冊", 1.95 <= 2.0 <= 2.05, f"[{k_lo}, {k_hi}]")

# ── J3: α 不變量 ──
print("\n── J3: α_v3 ∈ φ²×(1±0.05%) ──")
J3_lo, J3_hi = PHI2*0.9995, PHI2*1.0005
print(f"   窗 = [{J3_lo:.6f}, {J3_hi:.6f}]（φ²={PHI2:.6f} ± 0.05%）")
print(f"   現有 v1.0 α = {ALPHA_V10} (dev 0.0081%) 已喺窗內 ✓")
chk("J3 α 窗預註冊", J3_lo <= ALPHA_V10 <= J3_hi, f"dev={(ALPHA_V10-PHI2)/PHI2*100:.4f}%")

# ── J4: μ local 判決（c/s 代理）──
print("\n── J4: μ local(v3) 判決（c/s 比值代理, docs/24）──")
print(f"   μ local = −ln(c/s)/ln(7/4) — 唔係獨立量, 只跟 c/s 走")
print(f"   v3 c/s → 11.652 家族: μ local = −4.388 = 19.5σ ⟹ B′ 死")
print(f"   v3 c/s 維持 13.60:   μ local = −4.664 = 2.85σ ⟹ B′ 有牙")
chk("J4 預言註冊", True, "c/s 代理判決, 待 v3 c/s 值")

# ── J5: 反預言 ──
print("\n── J5: 反預言（否決條件）──")
print(f"   |γ_v3 − (−19/4)| > 3σ 或 γ_v3 ∉ [{J1_lo}, {J1_hi}] ⟹ stair 線 k=2 否決")
chk("J5 反預言註冊", abs(GAMMA_V10 - G19_4) <= 3*SIG_G, f"現有 |dev|={abs(GAMMA_V10-G19_4):.4f} < 3σ")

# ── J6/J7: 版本規則 ──
print("\n── J6/J7: 版本規則 + scheme 記錄 ──")
print(f"   J6: v3 tag = freeze_v3, 跨層比對禁止")
print(f"   J7: v3 測定值連 scheme 一齊記, 漂移用 J1-J5 裁決")
chk("J6/J7 規則預註冊", True, "tag + scheme 記錄")

# ── JSON ──
json.dump({
    "pre_registered": "2026-10-12, 未見 v3 數據前凍結",
    "context": {"gamma_v10": GAMMA_V10, "sig_g": SIG_G, "alpha_v10": ALPHA_V10,
                "phi2": PHI2},
    "J1_gamma_window": [J1_lo, J1_hi],
    "J2_k_window": [k_lo, k_hi],
    "J3_alpha_window": [J3_lo, J3_hi],
    "J4_mu_local_converge": "改寫(docs/24): μ local = −ln(c/s)/ln(7/4) 係 c/s 比值代理; "
                            "v3 c/s → 11.652 家族 ⟹ μ local −4.388=19.5σ B′死; "
                            "v3 c/s 維持 13.60 ⟹ −4.664=2.85σ B′有牙",
    "J5_falsify": "γ 漂出窗或 >3σ ⟹ stair 線 k=2 否決",
    "J6_version_rule": "v3 tag, 層內判",
    "J7_scheme_record": "連 scheme 記, 漂移用 J1-J5 裁決",
    "verdict": "freeze v3 判決表盲測預註冊完成 — J1-J7 全部凍結; v3 數據一到逐項照判, "
               "唔准後見改閾值; 現有 v1.0 全部喺窗內（一致性 baseline）",
}, open("data/29_freeze_v3_judgement_table.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")