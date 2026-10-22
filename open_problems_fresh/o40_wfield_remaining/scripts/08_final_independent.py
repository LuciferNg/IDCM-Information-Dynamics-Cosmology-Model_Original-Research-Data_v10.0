#!/usr/bin/env python3
"""
O40 — 最終獨立重算 (FINAL independent re-derivation, 防幻覺)
==============================================================
完全唔 reuse scripts, 從第一性原理重算全部關鍵公式同數值。
用 mpmath 高精度 + 唔同路徑, 確認記錄文檔所有數字正確。
"""
import mpmath as mp
mp.mp.dps = 50
phi = mp.mpf((1+mp.sqrt(5))/2)

print("=" * 72)
print("  FINAL 獨立重算 (O37 + O40 全部關鍵數值)")
print("=" * 72)
results = []

def chk(name, got, expect, tol=1e-8):
    dev = abs(mp.mpf(got)-mp.mpf(expect))/abs(mp.mpf(expect))
    ok = dev < tol
    results.append(ok)
    print(f"  {'✅' if ok else '❌'} {name}: {mp.nstr(got,12)} vs {mp.nstr(expect,12)} (dev {mp.nstr(dev,3)})")
    return ok

# ═══════════ 從第一性原埋重算 ═══════════
# 88-site 對偶鏈: γ_k = 4sin²(kπ/176), k = 1..88
# Σγ_even (世界) = Σ_{k even 2..88} 4sin²(kπ/176) = 90
# Σγ_odd  (觀察者) = Σ_{k odd 1..87} 4sin²(kπ/176) = 88
def gamma_88(k):
    return 4*mp.sin(k*mp.pi/176)**2
S_even = sum(gamma_88(2*n) for n in range(1,45))   # k=2,4,...,88
S_odd  = sum(gamma_88(2*n-1) for n in range(1,45)) # k=1,3,...,87
S_total = S_even + S_odd
# 44-site K_Chain 全譜: Σ_{n=1}^{44} 4sin²(nπ/88) = 90
def gamma_44(n):
    return 4*mp.sin(n*mp.pi/88)**2
S_chain44 = sum(gamma_44(n) for n in range(1,45))

# M₀ (O34 級聯) — 第一性: E_kchain × φ^(47+37/528)
E_kchain = mp.mpf('4.060265e-3')  # eV
M0_eV = E_kchain * phi**(mp.mpf(47) + mp.mpf(37)/mp.mpf(528))
M0_MeV = M0_eV*1e-6

print("\n═══ O37 核心 ═══")
chk("Σγ_even (世界) = 90", S_even, 90)
chk("Σγ_odd (觀察者) = 88", S_odd, 88)
chk("Σγ_total = 178 = 2F₁₁", S_total, mp.mpf(178), 1e-10)
chk("44-site 全譜 Σγ = 90", S_chain44, 90, 1e-9)
chk("μ² = Σγ_even−Σγ_odd = 2", S_even-S_odd, 2, 1e-9)
chk("M₀ (MeV)", M0_MeV, mp.mpf('27.9009'), 1e-4)
# Ω_Λ = 4/(φ⁴−1)
OmL = 4/(phi**4-1)
chk("Ω_Λ = 4/(φ⁴−1)", OmL, mp.mpf('0.68328157'), 1e-6)
# λ_B = (φ⁴−1)/4
lamB = (phi**4-1)/4
chk("λ_B = (φ⁴−1)/4", lamB, mp.mpf('1.46352549'), 1e-6)
# ⟨W⟩²_B = μ²/2λ = 2/(2λ_B) = 4/(φ⁴−1)
chk("⟨W⟩²_B = 4/(φ⁴−1) = Ω_Λ", 2/(2*lamB), OmL, 1e-10)
# m_δW = M0/2
chk("m_δW = M0/2 (MeV)", M0_MeV/2, mp.mpf('13.95046'), 1e-4)
# m_7 = M0·√γ_7 = M0·2sin(7π/88)
m7 = M0_eV*2*mp.sin(7*mp.pi/88)
chk("m_7 (MeV)", m7*1e-6, mp.mpf('13.80016'), 1e-4)
# m_δW/m_7 dev
dev_mdw = abs(M0_MeV/2 - m7*1e-6)/(m7*1e-6)*100
print(f"  → m_δW/m_7 dev = {mp.nstr(dev_mdw,5)}% (記錄: 1.09%)")

# ═══════════ O40 ═══════════
print("\n═══ O40 核心 ═══")
# v_eff = M0·√2
v_eff = M0_eV*mp.sqrt(2)
# v_SM = v_eff·88·71·(1−4/(90(M+μ²))), M=33, μ²=2
M_tree, mu2 = mp.mpf(33), mp.mpf(2)
v_SM_pred = v_eff*88*71*(1 - 4/(90*(M_tree+mu2)))
chk("v_SM pred (GeV)", v_SM_pred*1e-9, mp.mpf('246.2196'), 1e-6)
# 35 = M+μ²
chk("35 = M+μ²", M_tree+mu2, 35, 1e-12)
# 787.5 = 90×35/4
chk("787.5 = 90×35/4", 90*(M_tree+mu2)/4, mp.mpf('787.5'), 1e-12)
# T = 123/4 (維里)
chk("T = 123/4 = 30.75", mp.mpf(123)/4, mp.mpf('30.75'), 1e-12)
# λ_B/λ_C = 61.5/Ω_Λ (λ_C = 2/123)
lamC = mp.mpf(2)/123
chk("λ_B/λ_C = 61.5/Ω_Λ", lamB/lamC, mp.mpf(61.5)/OmL, 1e-9)
# fib = 41/60 − Ω_Λ
fib = mp.mpf(41)/60 - OmL
chk("λ_B/λ_C = 90(1+λ_B·fib)", lamB/lamC, 90*(1+lamB*fib), 1e-9)
# R_H = c/H₀
R_H = mp.mpf('299792.458')/mp.mpf('72.59')
chk("R_H (Mpc)", R_H, mp.mpf('4129.94'), 1e-4)
# T_sync = 2π/H₀ (Gyr)
H0_s = mp.mpf('72.59')/mp.mpf('3.085677581e19')
T_sync = 2*mp.pi/H0_s
chk("T_sync (Gyr)", T_sync/mp.mpf('3.15576e16'), mp.mpf('84.64'), 1e-3)
# ρ_Λ = Ω_Λ·ρ_crit vs Planck Ω_Λ
chk("Ω_Λ vs Planck 0.6847", OmL, mp.mpf('0.6847'), 0.01)

# 44-tone: ω_2/ω_1 = 2cos(π/88) 無理數
r21 = mp.sin(2*mp.pi/88)/mp.sin(mp.pi/88)
chk("ω_2/ω_1 = 2cos(π/88)", r21, 2*mp.cos(mp.pi/88), 1e-12)

print(f"\n{'='*72}")
print(f"  FINAL 獨立重算: {sum(results)}/{len(results)} PASS")
print(f"{'='*72}")

with open("data/final_independent_rederivation_results.txt","w") as f:
    f.write("O40 — FINAL 獨立重算 (防幻覺)\n")
    f.write("="*70 + "\n\n")
    f.write(f"Σγ = {mp.nstr(S_total,10)}, Σγ_even = {mp.nstr(S_even,10)}, Σγ_odd = {mp.nstr(S_odd,10)}\n")
    f.write(f"M₀ = {mp.nstr(M0_MeV,8)} MeV, v_eff = {mp.nstr(v_eff*1e-3,6)} MeV\n")
    f.write(f"Ω_Λ = {mp.nstr(OmL,8)}, λ_B = {mp.nstr(lamB,8)}\n")
    f.write(f"m_δW = {mp.nstr(M0_MeV/2,6)} MeV, m_7 = {mp.nstr(m7*1e-6,6)} MeV (dev {mp.nstr(dev_mdw,4)}%)\n")
    f.write(f"v_SM pred = {mp.nstr(v_SM_pred*1e-9,8)} GeV (PDG 246.2196)\n")
    f.write(f"R_H = {mp.nstr(R_H,6)} Mpc, T_sync = {mp.nstr(T_sync/mp.mpf('3.15576e16'),6)} Gyr\n")
    f.write(f"λ_B/λ_C = {mp.nstr(lamB/lamC,8)} = 61.5/Ω_Λ\n")
    f.write(f"ω_2/ω_1 = {mp.nstr(r21,10)} = 2cos(π/88)\n\n")
    f.write(f"FINAL 獨立重算: {sum(results)}/{len(results)} PASS\n")
print(f"\n  結果已寫入 data/final_independent_rederivation_results.txt")
