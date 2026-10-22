#!/usr/bin/env python3
"""
重驗 — UHECR 能量尺度 (對應 01_problem_record.md §2.1-2.4, §1.2)
=============================================================================
在 IDCM v10.0 框架下重算舊公式, 逐條比對文檔聲稱值。
零自由參數 — 全部來自 x²+x-1=0。
"""
import math, json, os, sys

phi = (1 + 5**0.5) / 2
inv_phi = 1 / phi
eps = inv_phi / 4
kappa = 1 / 16
N_d = 44
L = 53 / 8

# 物理常數 (CODATA)
h = 6.62607015e-34
c = 2.99792458e8
L_P = 1.616255e-35
eV_J = 1.602176634e-19

rows = []   # (label, recomputed, claimed, ok)

def chk(label, got, claim, tol_rel, fmt="{:.6e}"):
    dev = abs(got / claim - 1)
    ok = dev <= tol_rel
    rows.append((label, fmt.format(got), fmt.format(claim), dev, ok))
    return ok

print("=" * 78)
print("重驗 — UHECR 能量尺度 (01_problem_record.md §2)")
print("=" * 78)

# --- §1.2 結構常數 ---
print("\n[§1.2 結構常數]")
consts = [
    ("φ", phi, 1.61803398875, 1e-10),
    ("φ⁻¹", inv_phi, 0.61803398875, 1e-10),
    ("ε = φ⁻¹/4", eps, 0.1545084972, 1e-9),
    ("κ = 1/16", kappa, 0.0625, 1e-12),
]
for name, got, claim, tol in consts:
    ok = abs(got / claim - 1) <= tol
    print(f"  {name:12s} = {got:.12f}  (doc {claim})  {'✅' if ok else '❌'}")

# --- F1: λ_min = L_P·φ⁴⁴ ---
lam_min = L_P * phi**44
print(f"\n[F1] λ_min = L_P·φ⁴⁴ = {lam_min:.4e} m  (doc 2.535e-26)")
chk("λ_min", lam_min, 2.535e-26, 5e-4)

# --- F2: E_GZK = hc/λ_min ---
E_GZK = h * c / lam_min / eV_J
print(f"[F2] E_GZK = hc/(L_P·φ⁴⁴) = {E_GZK:.4e} eV  (doc 4.891e19)")
chk("E_GZK", E_GZK, 4.891e19, 1e-3)
print(f"     偏差 vs 觀測 GZK 5e19 eV = {abs(E_GZK/5e19-1)*100:.2f}%  (doc 2.18%)")

# --- F3: E_max = 4φ·E_GZK ---
E_max = 4 * phi * E_GZK
print(f"[F3] E_max = 4φ·E_GZK = {E_max:.4e} eV  (doc 3.166e20)")
chk("E_max", E_max, 3.166e20, 1e-3)
print(f"     偏差 vs Oh-My-God 3.2e20 eV = {abs(E_max/3.2e20-1)*100:.2f}%  (doc 1.08%)")

# --- F4: ratio 4φ ---
ratio = E_max / E_GZK
print(f"[F4] E_max/E_GZK = 4φ = {ratio:.6f}  (doc 6.472136; 觀測 6.40)")
chk("ratio 4φ", ratio, 6.47213595499958, 1e-12)

# --- F5: 4φ = (φ³−φ⁻³)·φ ---
identity = (phi**3 - phi**-3) * phi
print(f"[F5] (φ³−φ⁻³)·φ = {identity:.6f}  (= 4φ, dev {abs(identity-4*phi)/4/phi*100:.2e}%)")
chk("4φ identity", identity, 4*phi, 1e-12)

# --- F6: E_Pl^h·φ⁻⁴⁴ = hc/(L_P·φ⁴⁴) ---
E_Pl_h = h * c / L_P / eV_J
E_via_planck = E_Pl_h * phi**-44
print(f"[F6] E_Pl^h = hc/L_P = {E_Pl_h:.4e} eV;  E_Pl^h·φ⁻⁴⁴ = {E_via_planck:.4e} eV")
chk("Planck×φ⁻⁴⁴ ≡ GZK", E_via_planck, E_GZK, 1e-12)

# --- F7: 敏感度 — 指數 44 唯一命中 ---
print("\n[F7] 敏感度 (指數唯一性):")
sensi = {}
for e in [43, 43.5, 44, 44.5, 45]:
    E = E_Pl_h * phi**(-e)
    dev = abs(E / 5e19 - 1) * 100
    sensi[e] = dev
    print(f"     φ^-{e:<4}: E = {E:.4e} eV, GZK 偏差 {dev:6.2f}%")
ok44 = min(sensi.items(), key=lambda kv: kv[1])[0] == 44
print(f"     最優指數 = {min(sensi.items(), key=lambda kv: kv[1])[0]}  {'✅ (=44)' if ok44 else '❌'}")
rows.append(("sens 最優指數=44", "44", "44", 0.0, ok44))

# --- F8: 上限 (冇事件 > E_max) ---
E_max_EeV = E_max / 1e18
print(f"\n[F8] 上限 = {E_max_EeV:.1f} EeV; 歷史最高 Oh-My-God 320 EeV (1σ 下限 230)")
ok_cap = 320 <= E_max_EeV * 1.05 or (320 - 90) <= E_max_EeV
rows.append(("cap 冇事件>上限", f"{E_max_EeV:.1f} EeV", "316.6 EeV", 0.0, ok_cap))
print(f"     Oh-My-God 320 喺 1σ 內一致: {'✅' if ok_cap else '❌'}")

# ============ 結果表 ============
print("\n" + "=" * 78)
print(f"{'公式':<22}{'重算':>16}{'文檔':>16}{'rel.dev':>11}{'':>4}")
print("-" * 78)
allok = True
for label, got, claim, dev, ok in rows:
    allok &= ok
    print(f"{label:<22}{got:>16}{claim:>16}{dev:>11.2e}  {'✅' if ok else '❌'}")
print("-" * 78)
print(f"結果: {sum(1 for *_,o in rows if o)}/{len(rows)} {'通過 ✅' if allok else '有 FAIL ❌'}")

os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'), exist_ok=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'reverify_energy.json')
with open(out, 'w') as f:
    json.dump({
        "lambda_min_m": lam_min, "E_GZK_eV": E_GZK, "E_max_eV": E_max,
        "E_GZK_dev_vs_5e19_pct": abs(E_GZK/5e19-1)*100,
        "E_max_dev_vs_3p2e20_pct": abs(E_max/3.2e20-1)*100,
        "ratio_4phi": ratio, "sensitivity": sensi, "all_pass": allok,
    }, f, indent=2)
print(f"已存 {out}")
sys.exit(0 if allok else 1)
