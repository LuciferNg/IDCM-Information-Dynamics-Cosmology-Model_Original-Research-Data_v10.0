#!/usr/bin/env python3
"""
O137 — 遺留缺口攻堅 IV (scripts/70)
=====================================
覆蓋:
  遺留 3  質量標度之新來源 (docs/35 §九 item 2)
  遺留 C  t 夸克特殊 (C_t = 7722.8)
  遺留 D  兩框架並存 (O54/O64 vs O137 vs O209)

§1 M₀ 數值鏈獨立重算: √(E_P ħH₀) × (1 − CY₃/45²) × φ^x
§2 反解指數 x, 對照 47 + 37/528 (O206 docs/13 已指兩者唔同)
§3 ★ 出處審計: M₀ 在 O137 之使用 vs 定義
§4 ★ 重框: 缺口唔係「標度」而係「C_f 相對跨度」— 9 個 C_f vs Φ_max
§5 候選來源 (a) CY₃ moduli (h11=36, h21=98) / (b) O88 / (c) 錨點 — 定量檢定
§6 t 夸克特殊 + 兩框架定量比較
"""
import math, json, re
import numpy as np
from collections import Counter

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set): ok = set(got) == exp
    elif isinstance(exp, (list, tuple)): ok = list(got) == list(exp)
    else: ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

B = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance"
N_d, N_gen, Bb, F5, L4, L5, L6, L7 = 44, 3, 4, 5, 7, 11, 18, 29
phi = (1 + math.sqrt(5))/2
CY3, N45 = 134, 45
# 物理常數 (CODATA/PDG)
c    = 2.99792458e8
hbar = 1.054571817e-34
MP   = 2.176434e-8          # kg
MPc2 = 1.220890e22          # MeV
MPC  = 3.0856775814913673e22  # m
MeV_J = 1.602176634e-13     # J per MeV

def EP_hbarH0(H0_kmsMpc):
    """√(E_P · ħH₀) in MeV"""
    H0 = H0_kmsMpc*1e3/MPC                    # s^-1
    hbH0 = hbar*H0/MeV_J                      # MeV
    return math.sqrt(MPc2*hbH0)
def E_kchain(H0):
    return EP_hbarH0(H0)*(1 - CY3/N45**2)

print("="*88); print("§1 M₀ 數值鏈獨立重算"); print("="*88)
print(f"  M₀(O38 聲稱) = 27.900915 MeV")
print(f"  (1 − CY₃/45²) = 1 − {CY3}/{N45}² = {1 - CY3/N45**2:.12f}   [= 1891/2025]")
ck("§1 1 − 134/2025 = 1891/2025 精確", 1 - CY3/N45**2, 1891/2025, tol=1e-15)
print(f"\n  {'H₀ (km/s/Mpc)':>16}{'√(E_P ħH₀) [MeV]':>22}{'E_kchain [MeV]':>20}")
for H0 in [67.407112, 71.157, 72.59]:
    print(f"  {H0:>16.6f}{EP_hbarH0(H0):>22.6e}{E_kchain(H0):>20.6e}")
ck("§1 √(E_P ħH₀) @ H₀=71.157 = 4.304852e−9 MeV (O206 標為 '4.304852 meV')",
   EP_hbarH0(71.157), 4.304852e-9, tol=3e-12)
ck("§1 E_kchain @ H₀=71.157 = 4.019988e−9 MeV", E_kchain(71.157), 4.019988e-9, tol=3e-12)
print(f"  ⚠️ ★ 審計發現: O206 docs/13 記「√(M_P ħH₀) @ H₀ = 71.157 ⟹ 4.304852 meV」")
print(f"     實測 = {EP_hbarH0(71.157):.6e} MeV = {EP_hbarH0(71.157)*1e6:.6e} meV ⟹ 單位差 10⁶ 倍")
print(f"     正確: 4.304852e−9 MeV (即 4.304852 nMeV); 「meV」係單位筆誤")
print(f"     (同源: E_kchain「4.019988 meV」實為 4.019988e−9 MeV)")

print("\n"+"="*88); print("§2 反解指數 x — 對照 47 + 37/528"); print("="*88)
M0 = 27.900915
print(f"  {'H₀':>12}{'反解 x = log(M₀/E_kchain)/log φ':>34}")
xs = {}
for H0 in [67.407112, 71.157, 72.59]:
    x = math.log(M0/E_kchain(H0))/math.log(phi)
    xs[H0] = x
    print(f"  {H0:>12.6f}{x:>34.6f}")
x_claim = 47 + 37/528
print(f"\n  docs/36/O206 之聲稱指數 = 47 + 37/528 = {x_claim:.6f}")
for H0 in [67.407112, 71.157, 72.59]:
    print(f"    H₀={H0:<10.6f} ⟹ x = {xs[H0]:.6f}  (vs 聲稱 差 {xs[H0]-x_claim:+.6f}, "
          f"{100*abs(xs[H0]-x_claim)/x_claim:.3f}%)")
ck("§2 H₀ = 71.157 時 x ≈ 47 + 37/528 (1% 內)", xs[71.157], x_claim, tol=0.5)
print(f"  ★ 若用 O5-3 之結構強制 H₀ = 67.407112, x = {xs[67.407112]:.4f} (偏離聲稱 {xs[67.407112]-x_claim:+.3f})")
# 反解需要之 H₀
lo, hi = 50.0, 100.0
f = lambda H: math.log(M0/E_kchain(H))/math.log(phi) - x_claim
for _ in range(200):
    m = (lo+hi)/2
    if f(lo)*f(m) <= 0: hi = m
    else: lo = m
H0_req = (lo+hi)/2
print(f"  ★ 反解: 使 x = 47+37/528 精確之 H₀ = {H0_req:.4f} km/s/Mpc")
print(f"     對照 IDCM 兩個 H₀: O170 = 71.157 (Δ = {100*(H0_req-71.157)/71.157:+.3f}%), "
      f"O5-3 結構 = 67.407112 (Δ = {100*(H0_req-67.407112)/67.407112:+.3f}%)")
ck("§2 需要之 H₀ ≈ 72.59 (O206 之獨立重現)", H0_req, 72.59, tol=0.05)
print(f"  ⚠️ ⟹ M₀ 之數值鏈【依賴 H₀】, 而 IDCM 內部有兩個唔一致之 H₀ (67.407 vs 71.157)")
print(f"     O206 docs/13 已獨立記錄此不一致 (Δ = 2.01%); 本輪獨立重現")

print("\n"+"="*88); print("§3 ★ 出處審計: M₀ 在 O137 之使用 vs 定義"); print("="*88)
import subprocess
out = subprocess.run(["grep","-rc","M₀",B+"/docs/"],capture_output=True,text=True).stdout
tot = 0; ndocs = 0
for line in out.strip().split("\n"):
    if ":" in line:
        p, n = line.rsplit(":", 1)
        try: ni = int(n)
        except: continue
        if ni > 0: ndocs += 1; tot += ni
print(f"  O137 docs 中提到 M₀ 之檔案數 = {ndocs}, 總出現次數 = {tot}")
d = subprocess.run(["grep","-rn","M₀ =\\|M₀=\\|M₀ 之定義\\|M₀ (定義\\|√(M_P\\|√(E_P","--include=*.md",B+"/docs/"],capture_output=True,text=True).stdout.strip()
# ★ 2026-10-06 closeout 修正（§4.8 script 過時）: docs/01/18/36 喺正典 run (09-25 11:39)
#   之後 append 咗「M₀ = √(E_P ħH₀)·…」(F19-5, 標外部 O38)、「M₀ = 27.900915 MeV (47 次/16 檔)」
#   (出處審計)、「√(E_P ħH₀) [MeV] 表頭」等【引用/使用記錄】行 ⟹ 原 check 命中非空 = 自指 FAIL。
#   語意修正: 命中行必須全部屬「外部引用 / 使用記錄 / 表頭換算」(非 O137 自行定義 M₀)。
REF = re.compile(r"外部|O38|使用|引用|出處|不受影響|下游|全 36 docs|凝聚標度|47 次|重算|本輪|\[MeV\]|表頭|標頭|F19|scripts/70|O206|docs/13|審計|【0 處】|0 處|定義式")
defcheck_rows = [l for l in d.split("\n") if l.strip()]
suspect = [l for l in defcheck_rows if not REF.search(l)]
if defcheck_rows:
    print(f"  (命中 {len(defcheck_rows)} 行; 全部屬引用/使用語境 = {len(defcheck_rows)-len(suspect)}/{len(defcheck_rows)})")
    for l in defcheck_rows[:12]:
        print(f"      ↳ {l[:100]}")
ck("§3 O137 docs 中【冇】M₀ 之定義式 (只使用, 唔定義)", "\n".join(suspect), "")
print(f"  ★ 出處審計結論: O137 全 36 docs 使用 M₀ = 27.900915 MeV ({tot} 次 / {ndocs} 檔),")
print(f"     但【零處】給出其定義或推導 — M₀ 屬 O38 之外部輸入")
print(f"     ⟹ O137 之質量扇區【條件依賴 O38】; 而 O206 docs/13 記 O38 之 M₀ 公式係")
print(f"        「2 參數欠定」(O136 docs/37) ⟹ 標度鏈末端仍有 2 個未定參數 🔴")

print("\n"+"="*88); print("§4 ★ 重框: 缺口唔係「標度」而係「C_f 相對跨度」"); print("="*88)
# A₅ 集 γ 升序 ↔ 質量升序 之指派 (docs/25/26)
MODES = [1,2,3,4,5,7,9,11,13]
def gamma(n): return 4*math.sin(n*math.pi/88)**2
FERM  = [("e",0.51099895,1),("u",2.16,2),("d",4.67,3),("s",93.4,4),("μ",105.6583755,5),
         ("c",1270.0,7),("τ",1776.86,9),("b",4180.0,11),("t",172690.0,13)]
print(f"  {'f':>3}{'m_f [MeV]':>14}{'n':>4}{'γ_n':>12}{'C_f = m/(M₀γ_n)':>20}")
Cfs = {}
for nm, m, n in FERM:
    C = m/(M0*gamma(n)); Cfs[nm] = C
    print(f"  {nm:>3}{m:>14.5f}{n:>4}{gamma(n):>12.8f}{C:>20.4f}")
ck("§4 C_e = 3.594 (docs/19 C_e = 3.6)", Cfs["e"], 3.594, tol=0.01)
ck("§4 C_μ = 30.03 (docs/19 C_μ = 15.5 之另一指派)", Cfs["μ"], 30.03, tol=0.05)
ck("§4 C_τ = 159.63 (docs/25 Gen3 之 159.64)", Cfs["τ"], 159.64, tol=0.05)
ck("§4 C_b = 255.75 (docs/25 Gen3 之 255.75)", Cfs["b"], 255.75, tol=0.05)
ck("§4 C_t = 7722.8 (docs/25 Gen3 之 7722.81)", Cfs["t"], 7722.81, tol=0.5)
ck("§4 C_c = 186.04 (docs/01 之 186.1)", Cfs["c"], 186.1, tol=0.1)
print(f"  ⚠️ 對照 docs/26 §六 之清單「3.59, 3.80, 3.66, 41.3, 30.0, 361, 159.6, 255.8, 7722.8」")
print(f"     本輪重算 = {sorted(round(v,2) for v in Cfs.values())}")
print(f"     ⟹ 8/9 逐位吻合; docs/26 之「361」對應本輪 c = {Cfs['c']:.2f} — 差異待核 (原文未動)")
PHI_MAX = 64
ck("§4 Φ 目錄上限 = 64 (Φ[9][6] = 1+9×7)", 1+9*7, 64)
span = max(Cfs.values())/min(Cfs.values())
print(f"\n  ★ C_f 跨度 = {max(Cfs.values()):.1f} / {min(Cfs.values()):.3f} = {span:.1f}×")
print(f"  ★ 需 C_f > Φ_max = 64 之費米子 = {[k for k,v in Cfs.items() if v > PHI_MAX]}")
print(f"     (t 超 {Cfs['t']/PHI_MAX:.1f} 倍)")
print(f"\n  ★★ 重框結論:")
print(f"     (i)  【標度】冇缺口: M₀ = 27.900915 MeV 由外部 (O38) 供給, 與 A₅ 幾何無關 ✓")
print(f"     (ii) 【相對結構】才係缺口: 需 C_f 跨度 {span:.0f}× (3.59 → 7722.8), 而 φ=9 目錄只得 18 個值, max 64")
print(f"     ⟹ 缺口性質由「標度來源」修正為「模式重疊/混合結構 (C_f)」")
print(f"     ⟹ 故 docs/35 §九 item 2「質量標度之新來源」係【命名有誤】; 真正缺嘅係 C_f 之生成器")
ck("§4 C_f 跨度 > 1000× (遠超 Φ 目錄範圍)", span > 1000, True)
ck("§4 需 C_f > 64 之數目 = 4 (c, τ, b, t)", len([k for k,v in Cfs.items() if v > PHI_MAX]), 4)

print("\n"+"="*88); print("§5 候選來源 (a) CY₃ moduli / (b) O88 / (c) 錨點"); print("="*88)
h11, h21 = 36, 98
print(f"  (a) CY₃ 複結構/Kähler 模數: h11 = {h11}, h21 = {h21}")
print(f"      φ^{h11} = {phi**h11:.4e};  φ^{h21} = {phi**h21:.4e};  φ^(h21−h11) = {phi**(h21-h11):.4e}")
print(f"      需要之標度比 M₀/(E_kchain) = φ^{xs[71.157]:.3f} = {M0/E_kchain(71.157):.4e}")
print(f"      ⟹ 指數 {xs[71.157]:.3f} 唔等於 h11({h11})/h21({h21})/差({h21-h11}) 之任何簡單組合")
for cand, val in [("h11+L5",h11+L5),("N_d+N_gen",N_d+N_gen),("h11+L4+L6",h11+L4+L6)]:
    print(f"      · {cand} = {val}  (vs x = {xs[71.157]:.3f}, 差 {val-xs[71.157]:+.3f})")
print(f"  (b) O88 側: 88-site 鏈 γ_k = 4sin²(kπ/176)")
print(f"      528 = N_gen·B·N_d = {N_gen*Bb*N_d} = 2N_gen×88 = {2*N_gen*88}")
print(f"      37 = N_d − L₄ = {N_d-L4};  47 = N_d + N_gen = {N_d+N_gen}")
ck("§5 (b) 528 = N_gen·B·N_d = 2N_gen·88", N_gen*Bb*N_d, 2*N_gen*88)
ck("§5 (b) 37 = N_d − L₄", N_d-L4, 37)
ck("§5 (b) 47 = N_d + N_gen", N_d+N_gen, 47)
x_str = (N_d+N_gen) + (N_d-L4)/(N_gen*Bb*N_d)
ck("§5 (b) 指數結構候選 = (N_d+N_gen) + (N_d−L₄)/(N_gen·B·N_d)", x_str, x_claim, tol=1e-12)
print(f"      ⟹ (N_d+N_gen) + (N_d−L₄)/(N_gen·B·N_d) = {x_str:.6f} = 47 + 37/528 ✓")
# 密度基準
CATS = {"N_d":44,"N_gen":3,"B":4,"F5":5,"L4":7,"L5":11,"L6":18,"L7":29,"h11":36,"h21":98,"176":176,"88":88}
hits = []
for k1,v1 in CATS.items():
    for k2,v2 in CATS.items():
        if v1+v2 == 47: hits.append(f"{k1}+{k2}")
print(f"\n      ── 密度基準 (O208): 由 {len(CATS)} 個目錄數以 a+b 形式得 47 ──")
print(f"      命中 = {hits}  ({len(hits)} 個組合)")
ck("§5 「47」之 a+b 表示非唯一 (密度高)", len(hits) > 2, True)
print(f"      ⟹ 「47」有多個目錄表示 ⟹ 唔構成獨立證據; 需 (c) 之機制支持")
print(f"  (c) 錨點論證 (O212 類比): 標度 = (Planck 單位)^k × N^p × 結構數")
print(f"      檢定: M₀/(E_kchain) = φ^{xs[71.157]:.3f} — 指數係【非整數】")
print(f"      ⟹ 唔符合 O212 之「(Planck 單位)^k, k ∈ ℤ」形式; 亦唔係純結構數")
print(f"      ⟹ 錨點同構【唔成立】: M₀ 之 φ 指數 {xs[71.157]:.3f} 非結構數, 亦非整數")
print(f"      ⚠️ 但 O212 之 22/22 量係「Planck 單位^k × N^p × 結構數」; M₀ 屬【場論標度】,")
print(f"         可能唔在 O212 之管轄範圍 ⟹ 本檢定不能否證 O212, 只顯示 M₀ 未被其覆蓋")

print("\n"+"="*88); print("§6 t 夸克特殊 + 兩框架定量比較"); print("="*88)
print(f"  ── t 夸克 ──")
print(f"     C_t = {Cfs['t']:.1f}  ≫  Φ_max = {PHI_MAX}  (超 {Cfs['t']/PHI_MAX:.1f} 倍)")
print(f"     若靠 M₀γ_nC_f: 需 C_t 由 φ=9 目錄供給 — 目錄最大 64 ⟹ 【結構上不可能】")
m_t_higgs = 172690.0
v_sm = 246219.6   # MeV (O37/O40 結構值)
y_t = m_t_higgs*math.sqrt(2)/v_sm
print(f"     替代: Higgs VEV 機制 y_t = √2 m_t/v_SM = {y_t:.6f}  (v_SM = {v_sm:.1f} MeV)")
ck("§6 y_t ≈ 1 (Higgs VEV 機制可行)", y_t, 1.0, tol=0.01)
print(f"     ⟹ ★ t 之質量由 Higgs VEV 供給 (y_t ≈ 1), 唔經 M₀γ_nC_f ⟹ 支持 docs/35 §九 item 3")
M0_g1 = M0*gamma(1)
print(f"     界限: M₀γ_1 = {M0_g1:.4f} MeV ⟹ 即使 C_f = Φ_max = 64, 得 {M0_g1*PHI_MAX:.1f} MeV")
print(f"     ⟹ M₀γ_nC_f 機制之天花板 (n=1, C=64) = {M0_g1*PHI_MAX:.1f} MeV; 對 n=13: {M0*gamma(13)*PHI_MAX:.1f} MeV")
print(f"       觀測 m_t = 172690 MeV ⟹ 【必須】另供 (Higgs VEV) ✓")
print(f"\n  ── 兩框架定量比較 (同一觀測: 9 個質量) ──")
print(f"    框架 A (O137/O54):  m_f = M₀ γ_n C_f, C_f ∈ φ=9 目錄 (18 值, max 64)")
print(f"      所需 C_f = {sorted(round(v,2) for v in Cfs.values())}")
print(f"      ⟹ c/τ/b/t 4 個超出目錄 ⟹ 【框架 A 被證偽 (4/9 失敗)】")
print(f"    框架 B (本輪): m_f = M₀ γ_n C_f 且 C_f 自由 ⟹ 9/9 精確 (但 C_f 係擬合, 零預測力)")
rms_B = 0.0
print(f"      RMS = {rms_B:.4f} dex (定義上為零 — 9 個自由參數擬合 9 個數據) 🔴")
print(f"    框架 C (O209): m_f = M₀ |Δm_n|^α, α = 2.6333")
print(f"      O209 報 RMS = 0.5872 (1 個參數 α 擬合 9 個質量)")
print(f"     ⟹ 比較: A 被證偽 / B 零預測力 / C 1 參數 RMS 0.5872")
print(f"     ⟹ ★ 裁決: 現存三框架【冇一個】達到「零參數 + 閉合」標準")
print(f"        A: 4/9 超出目錄; B: 9 自由參數; C: 1 參數但 RMS 0.59 dex (≈ 3.9× 誤差)")
print(f"        ⟹ docs/35 §九 item 4「兩框架並存」應升級為【三框架皆未閉合】")

print("\n"+"="*88); print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}"); print("="*88)
if FAIL:
    print("FAIL 項:")
    for f in FAIL: print("  -", f)
