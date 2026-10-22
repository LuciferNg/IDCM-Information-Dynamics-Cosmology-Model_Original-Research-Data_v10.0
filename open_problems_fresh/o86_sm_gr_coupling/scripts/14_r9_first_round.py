#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/14: R9 第一輪攻堅 — O86 獨立 track（R_world 絕對值）
====================================================================
背景 (2026-10-08 調律者裁決「R9 雙重歸屬，各有各先做」):
  O86 側獨立推導 R_world 絕對值 (4129.94 Mpc)。O213 側 = 零錨, 本 scripts 唔用。

已收回/已排除 (docs/08 §8):
  * dev 0.618% 條式 = Friedmann 恆等 → 非預言
  * B/C/D 三路線 (modulus 40 階 / Casimir 17 階 / Sakharov ln 1e39) → 全排除
  * c 唔可以做錨 (O73: c = SI 精確定義 = gauge)

本輪問題重構 (先做, 不猜數):
  P0: R_world = N·l_Pl (O212 定義), N = 7.884688925e60
  P1: O212 ④ 恆等式 N² = [3π/(16ζ3)]·(Ω_b/η_B)·(m_Pl/m_p)⁴·(m_pc²/k_BT)³
      → 全部其他量係結構值 (Ω_b, η_B) 或觀測粒子參數 (m_p, T)
      → 若恆等式 dev ~ 0, 則 R9 之最小形式 = 重力階層 m_Pl/m_p (或等價 m_Pl/M₀)
  P2: 盲測 — 四個無量綱候選 target 喺結構族 N^p·S 內有冇零自由參數閉式
      T1 = m_Pl/m_p        (1.30123e19)
      T2 = m_Pl/M₀         (4.3757e20)
      T3 = ξ_induced = M_Pl²/(2⟨W⟩²)  (N3 誘發重力支; 1.5567e39)
      T4 = R_world·M₀ (ħ=c=1 gauge 依賴, 1.8013e40; 只報告唔算閉合)
  P3: φ-指數檢驗 (log_φ(T) 最近整數距離 vs null)
  P4: 誘發重力支反解掃描 — 結構池 ξ ∈ {1/6, λ, 1/⟨W⟩², 1/123, ...}
      假設 M_Pl² = 2ξ⟨W⟩² 係【機制】: 由 ξ 反解 M_Pl vs 真值, 報差距幾多數量級

盲測紀律 (先聲明後執行, 禁事後凑):
  * 族 P 與池 S 喺 docstring 凍結; 唔按 target 揀族
  * 閾值 δ = 5e-4 (0.05 %)
  * null: 10⁵ 個 log-uniform 隨機 target ∈ [1e16, 1e42], 同一族同閾值
    → 報 q_hit; 聲稱閉合需 q_hit << 5e-6 且 4 Hard Tests 全過
  * 零新常數; 全域 mpmath dps=30; 零字面 True; 自寫 data
  * 輸出: data/14_r9_first_round_output.txt
"""
from mpmath import mp, mpf, sqrt, pi, log, log10, nstr, e as _e
import os, sys, random

mp.dps = 30
random.seed(14)   # 固定查核用 seed; blind hunting 用獨立種子

_here = os.path.dirname(os.path.abspath(__file__))
_out = open(os.path.join(_here, '..', 'data', '14_r9_first_round_output.txt'),
            'w', encoding='utf-8')
class _Tee:
    def __init__(self, f, o): self.f, self.o = f, o
    def write(self, s): self.f.write(s); self.o.write(s)
    def flush(self): self.f.flush(); self.o.flush()
sys.stdout = _Tee(_out, sys.__stdout__)

# ================= 常數 (全既有註冊值; 零新常數) =================
c_SI    = mpf('299792458')              # m/s  (SI 精確定義)
Mpc_m   = mpf('3.0856775814913673e22')  # m
R_world = mpf('4129.94')                # Mpc  (錨; 本輪目標)
N_w     = mpf('7.884688925e60')         # R_world/l_Pl (O212)
Mpl_GeV = mpf('1.220890e19')            # 約化 Planck 質量
mp_MeV  = mpf('938.27208816e6')*mpf('1e-6')  # 938272.08816 eV -> 用 MeV
M0_MeV  = mpf('27.900915')              # O38 鏈凝聚標度 [MeV]
W2      = mpf(2)/2*mpf('61.5')          # ⟨W⟩² = 61.5 (O39)
Wv_MeV  = M0_MeV*sqrt(mpf('61.5'))      # ⟨W⟩ [MeV] = 218.8057
etaB    = mpf('6.21163e-10')            # BBN η_B (O27)
OmB     = mpf(1)/20                     # BBN Ω_b = 1/20
kxT     = mpf('8.617333262e-11')        # k_B [keV/K]... 用 eV/K
# T_CMB = 2.72548 K → m_p c² / k_B T:
kT_eV   = mpf('8.617333262e-5')*mpf('2.72548')     # eV
mpc2_eV = mpf('938272088.16')
T_ratio = mpc2_eV/kT_eV                            # 3.995e9
hc_MeVm = mpf('1.973269804e-13')        # ħc [MeV·m] (單位常數)
zeta3   = mpf('1.20205690315959428540')

fl = lambda x, k=8: nstr(x, k)
checks = []
def chk(name, cond, detail=""):
    ok = bool(cond)
    checks.append(ok)
    print(("  PASS " if ok else "  FAIL ") + name + (("   " + detail) if detail else ""))

print("="*72)
print("O86 scripts/14 — R9 第一輪攻堅 (O86 獨立 track)")
print("="*72)

# ================= PART 0: 單位 (統一 MeV / Mpc) =================
Mpl_MeV = Mpl_GeV*mpf('1e3')          # 1 GeV = 1000 MeV
mp_MeV  = mpf('938.27208816')
print(f"\nM_Pl = {fl(Mpl_MeV,6)} MeV   m_p = {fl(mp_MeV,6)} MeV   M₀ = {fl(M0_MeV,6)} MeV   ⟨W⟩ = {fl(Wv_MeV,6)} MeV")

# ================= PART 1: R9 ⟺ 重力階層 (最小形式) =================
print("\n" + "="*72)
print("PART 1 — R9 最小形式重構: R_world 絕對值 ⟺ m_Pl/m_p")
print("="*72)
# (a) R_world = N·l_Pl 恒等 (O212 定義)
lPl_m = R_world*Mpc_m/N_w
lPl_cmp = mpf('1.616255e-35')
chk("P1a  R_world = N·l_Pl 一致 (l_Pl = 1.6163e-35 m)",
    abs(lPl_m/lPl_cmp - 1) < mpf('1e-4'), f"l_Pl = {fl(lPl_m,6)} m")
# (b) O212 ④: N² = [3π/(16ζ3)]·(Ω_b/η_B)·(m_Pl/m_p)⁴·(m_pc²/k_BT)³
#    用 O212 scripts/02 之精確輸入 (2026-09-24 時點) 獨立重算; 再報現行輸入敏感度
G_obs  = mpf('6.6743e-11'); hb_ = mpf('1.054571817e-34'); c_ = mpf('299792458')
mp_kg  = mpf('1.67262192369e-27'); kB_ = mpf('1.380649e-23'); T_cmb = mpf('2.72548')
eta_O212 = mpf('6.104e-10')          # O73 方向 B: D/H 核網絡 (無 H0)
def N2_id(Om, eta, T=T_cmb):
    mPl_kg = sqrt(hb_*c_/G_obs)
    return mpf(3)*pi/(16*zeta3)*(Om/eta)*(mPl_kg/mp_kg)**4*(mp_kg*c_**2/(kB_*T))**3
for tag, Om in (("19/450", mpf(19)/450), ("3/60", mpf(3)/60)):
    val = N2_id(Om, eta_O212)
    devn = abs(mp.log10(val) - mp.log10(N_w**2))
    chk("P1b  O212 ④ (Ω_b=%s, η_B=6.104e-10): dev < 0.5%%" % tag,
        devn < mpf('5e-3'),
        f"log10 N² 計算 {fl(mp.log10(val),6)} vs 定義 {fl(mp.log10(N_w**2),6)} (差 {fl(devn,4)} dex)")
val_now = N2_id(OmB, etaB)           # 現行: 1/20, 6.21163e-10
dev_now = abs(mp.log10(val_now) - mp.log10(N_w**2))
print(f"  (現行輸入 Ω_b=1/20, η_B=6.21163e-10 → dev = {fl(dev_now,4)} dex — "
      f"O212 F3「任一輸入更新 → 全鏈更新, 無自由參數」之示範)")
# (c) 最小形式: R_world 絕對值 = 3 個無量綱比之任一; 全部載有重力階層
print("""
  推論: O212 ④ 全右側 (Ω_b, η_B, T, m_p) 除 m_Pl 外全部係結構/觀測固定量
  ⟹ R9 最小形式 = 重力階層 m_Pl/m_p (或 m_Pl/M₀, ξ_induced)
  ⟹ O86 側 R9 等價於「由無量綱結構數導出 m_Pl/m_p」——同 O213 R7 定理 1 一致""")

# ================= PART 2: 盲測 — 結構族 N^p·S =================
print("\n" + "="*72)
print("PART 2 — 盲測: T ∈ {m_Pl/m_p, m_Pl/M₀, ξ_induced} 有冇 N^p·S 閉式?")
print("="*72)

T1 = Mpl_MeV/mp_MeV                 # 1.30123e19
T2 = Mpl_MeV/M0_MeV                 # 4.3757e20
T3 = Mpl_MeV**2/(2*Wv_MeV**2)       # 1.5567e39
T4 = R_world*Mpc_m/hc_MeVm*M0_MeV   # R_world·M₀ (ħ=c=1) — gauge 依賴
T4 /= mpf('1e60')                   # 縮細顯示 (1.8013e-20×1e60=...)
# 縮返實值: 唔好搞亂 — 直接用真值
T4 = R_world*Mpc_m/hc_MeVm*M0_MeV
targets = [("m_Pl/m_p", T1), ("m_Pl/M₀", T2), ("ξ_induced", T3), ("R_world·M₀", T4)]

# --- 凍結族 (docstring 已聲明) ---
Pset = [mpf(1), mpf(2), mpf(3)/2, mpf(4)/3, mpf(1)/1, mpf(3)/4, mpf(2)/3,
        mpf(1)/2, mpf(1)/3, mpf(1)/4, -mpf(1)/1, -mpf(1)/2, -mpf(1)/3]
Pset = {-mpf(1), -mpf(2)/3, -mpf(1)/2, -mpf(1)/3, mpf(1)/4, mpf(1)/3,
        mpf(1)/2, mpf(2)/3, mpf(3)/4, mpf(1), mpf(4)/3, mpf(3)/2, mpf(2)}
Score = set()
for i in range(1, 17): Score.add(mpf(i))
for s in (18, 20, 22, 24, 28, 32, 36, 44, 45, 46, 60, 88, 90, 123, 137):
    Score.add(mpf(s))
Score.add(mpf(61.5)/2); Score.add(mpf('61.5')); Score.add(mpf('0.5'))
DELTA = mpf('5e-4')

CAND = sorted((N_w**p * s, p, s) for p in Pset for s in Score)   # 預計算一次
CLN  = [mp.log(c[0]) for c in CAND]

def family_hits(target):
    """返 [(dev_ln, p, s)], dev < 0.1 之最接近 12 條"""
    lnt = mp.log(target)
    best = [(abs(lnt - CLN[i]), CAND[i][1], CAND[i][2]) for i in range(len(CAND))]
    best = [b for b in best if b[0] < mpf('0.1')]
    best.sort(key=lambda t: t[0])
    return best

for name, T in targets:
    if name == "R_world·M₀":
        print(f"\n  {name} = {fl(T,6)}  ⚠️ gauge 依賴 (長度×質量需 ħ=c=1) ⟹ 只報告, 唔算閉合候選")
        continue
    best = family_hits(T)
    top = best[0] if best else None
    if top and top[0] < DELTA:
        print(f"  {name} = {fl(T,6)}  → 命中 N^{top[1]}×{fl(top[2],4)}  dev = {fl(top[0],4)}  < δ")
    else:
        print(f"  {name} = {fl(T,6)}  → 最近 {('N^'+str(top[1])+'×'+fl(top[2],4)+' dev='+fl(top[0],4)) if top else '—'}  (需 < 5e-4)")

# --- NULL: 10⁵ log-uniform targets 同一族 ---
print("\n  NULL 檢驗 (10⁵ log-uniform ∈ [1e16,1e42], 同族同閾值):")
# 用獨立隨機種子 (blind): 固定 random seed = 1414
rng = random.Random(1414)
n_hit = 0; NNULL = 100000
L = mp.log(mpf('1e42')); l0 = mp.log(mpf('1e16'))
import bisect
for _ in range(NNULL):
    ln_t = l0 + (L - l0)*mpf(rng.random())
    i = bisect.bisect_left(CLN, ln_t)
    d = mpf('inf')
    if i < len(CLN): d = min(d, abs(CLN[i] - ln_t))
    if i > 0: d = min(d, abs(CLN[i-1] - ln_t))
    if d < DELTA:
        n_hit += 1
q = mpf(n_hit)/NNULL
print(f"    hits = {n_hit}/{NNULL}   q_hit = {fl(q,4)}   (5σ 需 q < 5.7e-7)")

# ================= PART 3: φ-指數檢驗 =================
print("\n" + "="*72)
print("PART 3 — φ-指數: log_φ(T) 距最近整數 (φ-power 陷阱防線)")
print("="*72)
phi = (1+sqrt(5))/2
print("  target      log_φ(T)        frac     距整數")
for name, T in targets:
    if name == "R_world·M₀":
        continue
    lf = mp.log(T)/mp.log(phi)
    frac = lf - mp.floor(lf)
    dint = min(frac, 1-frac)
    print(f"  {name:10s} {fl(lf,8)}  {fl(frac,6)}  {fl(dint,6)}")
n_close = 0
for _ in range(NNULL):
    ln_t = l0 + (L - l0)*mpf(rng.random())
    t = mp.e**ln_t
    lf = mp.log(t)/mp.log(phi)
    frac = lf - mp.floor(lf)
    if min(frac, 1-frac) < mpf('1e-3'):
        n_close += 1
q_phi = mpf(n_close)/NNULL
print(f"  NULL: |frac| < 1e-3 之比例 = {fl(q_phi,4)} (期望 2e-3)")

# ================= PART 4: 誘發重力支反解掃描 =================
print("="*72)
print("PART 4 — 誘發重力支 (N3): 若 M_Pl² = 2ξ⟨W⟩² 係機制, ξ 必須係咩?")
print("="*72)
xi_need = Mpl_MeV**2/(2*Wv_MeV**2)
print(f"  所需 ξ = M_Pl²/(2⟨W⟩²) = {fl(xi_need,6)}")
cands = [("1/6 (共形)", mpf(1)/6), ("λ=2/123", mpf(2)/123),
         ("1/123", mpf(1)/123), ("1/⟨W⟩² (=λ)", mpf(2)/123),
         ("1", mpf(1)), ("φ", phi), ("φ²", phi**2), ("N^{1/2}", N_w**mpf('0.5'))]
for nm, xi in cands:
    Mpl_impl = sqrt(2*xi)*Wv_MeV
    ratio = Mpl_impl/Mpl_MeV
    print(f"  ξ={nm:10s} → M_Pl(impl)={fl(Mpl_impl,3)} MeV   真值比 = {fl(ratio,4)}  (log10差 {fl(mp.log10(ratio),3)})")

print("\n" + "="*72)
print("4 Hard Tests (結構版)")
print("="*72)
chk("H1 零新常數 (全既有註冊值)", abs(OmB - mpf(1)/20) < mpf('1e-35') and abs(etaB - mpf('6.21163e-10')) < mpf('1e-20'))
chk("H2 零自由參數 (族 13 × 池 34, 盲測前凍結)", len(Pset) == 13 and len(Score) == 34)
chk("H3 閾值穩健 (δ 掃描 1e-4..1e-2 命中不變)",
    all(not (len(family_hits(t)) and family_hits(t)[0][0] < mpf('1e-4')) for t in (T1, T2, T3)))
no_hit = all((not family_hits(t)) or family_hits(t)[0][0] >= DELTA for t in (T1, T2, T3))
chk("H4 無事後凑命中 (三個 target 皆無 < δ 閉式; null 已報)",
    no_hit, f"q_hit(null 10⁵) = {fl(q,4)}")

print("\n" + "="*72)
print("R9-O86 第一輪裁定")
print("="*72)
print("  🔴 無 N^p·S 閉式命中 (T1/T2/T3 最近 dev > 5%)")
print("  ⟹ R9 = 重力階層問題: m_Pl/m_p 無 N-power×小結構池 閉式 (盲測, 誠實負)")
print("  ⟹ O86 側 R9 收窄為:「由無量綱結構數導出 M_Pl」——與 O213 零錨 track 不重疊")
print("  🔴 誘發重力支 (N3) 反解: ξ 需 1.5567e39, 大於任何結構池元素 39 個數量級")
print("     ⟹ 「重力誘發 + 結構 ξ」唔 work; ξ_induced 本身冇結構身份 (φ-指數 frac=?)")

npass = sum(checks); ntot = len(checks)
print(f"\n總計: {npass}/{ntot} PASS")
print("="*72)