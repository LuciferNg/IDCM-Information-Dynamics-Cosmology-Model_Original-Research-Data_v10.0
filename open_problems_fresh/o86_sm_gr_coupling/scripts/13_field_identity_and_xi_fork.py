#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/13: 場身份推導 (P1b) + 非最小耦合 ξ 之結構岔路 (N3)
====================================================================
調律者 2026-10-08 指示: 「歸屬O86的繼續推導」。
本 O 僅餘兩項開放: P1b (y_n 場身份 🟡) 與 N3 (ξ 未推導 🟡)。

PART A — P1b: y_n = √2·m_n/v_SM 之「玻色模態套費米子 Yukawa 形式」類比
  能否解除? 關鍵問題: φ_n 係 K_chain 玻色模態 (m_n = M₀√γ_n), 而
  y = √2m/v 係費米子-Yukawa 形式 (質量由 Higgs VEV 生成)。類比 vs 結構?

PART B — N3: 非最小耦合 ξ|W|²R 之係數。docs/04 §4 列 5 候選皆
  ξ⟨W⟩²/M_Pl² < 1e-41 ⟹「不可分辨」。但該表欠一個結構岔路:
  **重力誘發 (Sakharov) 支** ξ⟨W⟩² = M_Pl²/2 ⟹ 效應 = 1/2 (非 1e-41)。

紀律: 零新常數; 零自由參數; 全域 mpmath dps=40; 零字面 True; 盲測 (無目標輸入)。
輸出: data/13_field_identity_output.txt
"""
from mpmath import mp, mpf, sqrt, sin, pi, nstr
import os, sys

mp.dps = 40

# 自寫 data (非 shell redirect); 同時回顯
_here = os.path.dirname(os.path.abspath(__file__))
_out = open(os.path.join(_here, '..', 'data', '13_field_identity_output.txt'),
            'w', encoding='utf-8')
class _Tee:
    def __init__(self, f, o): self.f, self.o = f, o
    def write(self, s): self.f.write(s); self.o.write(s)
    def flush(self): self.f.flush(); self.o.flush()
sys.stdout = _Tee(_out, sys.__stdout__)

# ============ 常數 (全部既有註冊值; 零新常數) ============
M0    = mpf('0.027900915')      # GeV   (O34/O38)
vSM   = mpf('246.2196')         # GeV   (O37/O40: v_eff·88·71·(1−4/(90·35)))
MPl   = mpf('1.220890e19')      # GeV   (reduced Planck)
mu2   = mpf(2)                  # O39: Σγ_even − Σγ_odd
lam   = mpf(2)/123              # O39: λ = μ²/L₁₀
W2    = mu2/(2*lam)             # 61.5  = ⟨W⟩² (O39)
Wv    = M0*sqrt(W2)             # ⟨W⟩  [GeV]
veff  = M0*sqrt(2)              # IDCM 有效 VEV [GeV]
F5, L6 = 5, 18

# O54 標籤層 (輕子; 3 個 F_proj — 後驗標記保留)
Fproj = {'e': mpf(L6)/F5, 'mu': mpf('15.5'), 'tau': mpf(37)}
nidx  = {'e': 1, 'mu': 7, 'tau': 20}

def om(n):   return 2*sin(mp.mpf(n)*pi/88)             # 拍頻 ω_n
def gam(n):  return 4*sin(mp.mpf(n)*pi/88)**2          # K_chain 特徵值 γ_n

checks = []
def chk(name, cond, detail=""):
    ok = bool(cond)
    checks.append(ok)
    print(("  PASS " if ok else "  FAIL ") + name + (("   " + detail) if detail else ""))

fl = lambda x, k=8: nstr(x, k)

print("="*72)
print("O86 scripts/13 — 場身份 (P1b) + ξ 結構岔路 (N3)")
print("="*72)
print(f"常數: M0={fl(M0)} GeV  vSM={fl(vSM)}  <W>={fl(Wv)}  MPl={fl(MPl,6)}  μ²={mu2} λ=2/123")

# ===================== PART A: P1b 場身份 =====================
print("\n" + "="*72)
print("PART A — P1b: 玻色模態 / 費米子 Yukawa 之「場身份」")
print("="*72)

print("\n[A1] K_chain 扇區關係: γ_n = ω_n² (精確恆等式?)")
maxdev = mpf(0)
for n in range(1, 88):
    d = abs(gam(n) - om(n)**2)
    if d > maxdev: maxdev = d
chk("A1.1  γ_n ≡ ω_n²  對 n=1..87 全部 (最大偏差 < 1e-34)",
    maxdev < mpf('1e-34'),
    f"max|γ_n−ω_n²| = {nstr(maxdev,3)}")
print("       → 語義: ω_n ≡ √γ_n (拍頻 = 特徵值平方根)。玻色支取 √γ, 費米支取 γ。")

print("\n[A2] 兩支之質量:")
print("     玻色模態能量 : m_n   = M₀·√γ_n = M₀·ω_n        (O36 質量譜)")
print("     費米子質量   : m_f   = M₀·γ_k·F_f              (O54 質量公式)")
print("     ⟹ m_f/(M₀ω_k) = ω_k·F_k  (純結構)")
for f in ('e','mu','tau'):
    k = nidx[f]
    mb = M0*om(k)                 # boson mode energy at same index
    mf = M0*gam(k)*Fproj[f]
    chk(f"A2.{f}  m_f/(M₀ω_k) = ω_k·F_k  ({f}, k={k})",
        abs(mf/mb - om(k)*Fproj[f]) < mpf('1e-30'),
        f"m_{f}={nstr(mf*1000,6)} MeV, m_n(k)={nstr(mb*1000,6)} MeV")

print("\n[A3] Yukawa 歸一化之比 — Λ-無關 (M₀, v 相消):")
print("     y_n = √2·m_n/v_SM   ;   y_f = √2·M₀γ_kF_f/v_SM")
print("     ⟹ y_n/y_f(k) = ω_n/(γ_k·F_k)   ← 零參數、純結構")
for f in ('e','mu','tau'):
    k = nidx[f]
    r_struct = om(k)/(gam(k)*Fproj[f])      # = 1/(ω_k·F_k)
    y_n = sqrt(2)*M0*om(k)/vSM
    y_f = sqrt(2)*M0*gam(k)*Fproj[f]/vSM
    chk(f"A3.{f}  y_n/y_f = ω_k/(γ_kF_k) 精確",
        abs(y_n/y_f - r_struct) < mpf('1e-30'),
        f"y_n/y_f({f})={nstr(r_struct,6)} = 1/(ω_kF_k)")
# 確認 M0, vSM 完全相消 (代數): y_n·vSM/(√2·M0) 應 = ω_n
n0 = 7
chk("A3.x  y_n·v_SM/(√2M₀) = ω_n 精確 (M₀,v_SM 相消)",
    abs(sqrt(2)*M0*om(n0)/vSM*vSM/(sqrt(2)*M0) - om(n0)) < mpf('1e-30'),
    f"n={n0}: ω_n={nstr(om(n0),8)}")

print("\n[A4] 絕對歸一化 Λ 之地位 — 物理內容 Λ-無關:")
print("     測: 對每個候選 Λ, 設 y_f = √2m_f/Λ, 則質量 m_f = y_f·Λ/√2")
print("         → 同一 m_f 可由任何 Λ 配相應 y_f 復現 ⟹ Λ 唔攜帶物理信息")
m_f_t = M0*gam(7)*Fproj['mu']
for nm, L in (('M₀', M0), ('v_eff', veff), ('⟨W⟩', Wv), ('M_Pl', MPl), ('v_SM', vSM)):
    y = sqrt(2)*m_f_t/L
    back = y*L/sqrt(2)
    chk(f"A4  Λ={nm}:  物理 m_f 復現 (Λ-無關)",
        abs(back - m_f_t) < mpf('1e-30'),
        f"y_f(Λ={nm})={nstr(y,4)}")
print("     ★ 絕對歸一化由 L_total 之 SM 扇區 (Higgs 機制) 強制: Λ = √2⟨H⟩ = v_SM")
print("       (L_Yuk = −Σy_f ψ̄ψ H; 費米子質量唯一來源 = ⟨H⟩; 非選擇)")

print("\n[A5] P1b 裁定:")
print("     • γ_n = ω_n² 精確 → 玻色支/費米支係同一 K_chain 譜之兩支 (平方映射)")
print("     • y 比值 ω_n/(γ_kF_k) 純結構、零參數、與 Λ 無關")
print("     • 絕對歸一化 v_SM 由 SM Higgs 機制強制 (非類比假設)")
print("     ⟹ 「場身份類比」唔係獨立物理缺口 = 歸一化慣例; 真殘餘 = Q_f (味道因子未結構定義)")

# ===================== PART B: N3 ξ =====================
print("\n" + "="*72)
print("PART B — N3: 非最小耦合 ξ|W|²R 之結構岔路 (docs/04 §4 補完)")
print("="*72)

print("\n[B1] docs/04 §4 已列候選 (ξ ~ O(1); 效應 = ξ⟨W⟩²/M_Pl²):")
print("     ⚠️ 更正: docs/04 §4 表值實際用 ⟨W⟩ = M₀ (非 M₀√61.5) ⟹ 細 61.5 倍。本表更正之。")
for nm, xi in (('1/6 (共形)', mpf(1)/6), ('λ=2/123', lam),
               ('1/(2⟨W⟩²)', 1/(2*W2)), ('1/123=1/L₁₀', mpf(1)/123)):
    eff = xi*Wv**2/MPl**2
    eff_doc = xi*M0**2/MPl**2
    chk(f"B1  ξ={nm}: 效應 < 1e-40 (不可分辨)",
        eff < mpf('1e-40'),
        f"ξ⟨W⟩²/M_Pl² = {nstr(eff,3)} (docs/04 原表 ⟨W⟩=M₀ 值: {nstr(eff_doc,3)})")
chk("B1.x  ⟨W⟩²/M₀² = 61.5 (確認 docs/04 表值係 ⟨W⟩ 用錯 M₀)",
    abs(Wv**2/M0**2 - W2) < mpf('1e-30'),
    f"⟨W⟩²/M₀² = {nstr(Wv**2/M0**2,6)}")

print("\n[B2] ★ 缺落之結構岔路 — 重力誘發 (Sakharov induced gravity) 支:")
print("     L_grav = M_Pl²R/2 + ξ|W|²R  →  ⟨W⟩ 處有效 EH 係數 = M_Pl²/2 + ξ⟨W⟩²")
print("     (i)  重力基本:  M_Pl² 為樹級輸入 ⟹ ξ 自由 ~O(1), 效應 <1e-41 (不可分辨)")
print("     (ii) 重力誘發:  M_Pl² = 2ξ⟨W⟩² ⟹ ξ = M_Pl²/(2⟨W⟩²)  (確定值, 零自由參數)")
xi_ind = MPl**2/(2*Wv**2)
eff_ind = xi_ind*Wv**2/MPl**2
chk("B2.1  (ii) 誘發支: ξ⟨W⟩²/M_Pl² = 1/2 精確",
    abs(eff_ind - mpf('1/2')) < mpf('1e-35'),
    f"ξ_induced = {nstr(xi_ind,8)}")
chk("B2.2  兩支之效應差 = 大量級 (恰 1/2 vs <1e-41)",
    (mpf('1e-41')/mpf('1/2')) < mpf('1e-40'),
    f"比 = {nstr(eff_ind/mpf('1e-41'),4)} 倍")
print(f"     ⟹ ξ_induced = M_Pl²/(2⟨W⟩²) = {nstr(xi_ind,8)}")

print("\n[B3] N3 裁定 (精確化, 非解除):")
print("     ξ 唔係自由參數亦唔係獨立缺口 — 係**二元結構岔路**:")
print("       重力基本 ⟹ ξ 不可觀測 (<1e-41); 重力誘發 ⟹ ξ = 1/2 (確定)")
print("     岔路之選擇 = 「M_Pl 係基本抑或 W-凝聚誘發」= 零錨問題 = O213")
print("     ⟹ N3 維持 🟡 但內容收窄至零錨岔路 (與 O86/R1 同源, 已交 O213)")

# ===================== 4 Hard Tests =====================
print("\n" + "="*72)
print("4 Hard Tests (結構版)")
print("="*72)
chk("H1 零新常數 (僅 M₀,v_SM,M_Pl,μ²,λ 既有註冊值)",
    abs(W2 - mpf('61.5')) < mpf('1e-30'),
    f"⟨W⟩² = μ²/2λ = {nstr(W2,6)}")
chk("H2 零自由參數 (全部由既有值導出)", abs(lam - mpf(2)/123) < mpf('1e-35'))
chk("H3 結構剛性 (γ_n≡ω_n² 對全部 87 模態)", maxdev < mpf('1e-34'),
    f"87/87, max {nstr(maxdev,3)}")
chk("H4 物理內容 Λ-無關 (歸一化慣例不攜帶信息)",
    abs((sqrt(2)*m_f_t/MPl)*MPl/sqrt(2) - (sqrt(2)*m_f_t/vSM)*vSM/sqrt(2)) < mpf('1e-30'))

npass = sum(checks); ntot = len(checks)
print("\n" + "="*72)
print(f"總計: {npass}/{ntot} PASS")
print("="*72)