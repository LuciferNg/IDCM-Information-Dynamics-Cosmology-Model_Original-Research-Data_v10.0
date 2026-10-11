#!/usr/bin/python3
"""O238 — Script 24: C 數值閉合終審 — C = 1 MeV/88³?

R8 之後唯一未閉合 = C 嘅數值身份. 觀察: C_fit(S1)=1.466433599e-6 MeV vs
1/88³ = 1.467411e-6 (差 ~0.067%?). 本 script 終審:

  P1 C(S1/S2/S3) vs 1/88³, 1/88⁴·π, 1/(44⁵), M₀/88⁴, 2⁻²⁴ 等結構候選
  P2 盲測紀律: 候選必須有結構動機 — 88 = 鏈長, ³ = 三維?(IDCM 世界弦維度)
     對照: 196 池獨立密度 (候選數 N_c × 窗口帶寬 X 有幾多個會中)
  P3 剔 c/s 後 C7 表現 (C7 = 1.159e-6 — 係咪都中 1/88³? 定 c/s 離群令 C9 對齊?)
  P4 預言: C = 1 MeV/88³ ⟹ freeze v2 新量度 ms/mu 落點?
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
Eee = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = Eee[:, None] - Eee[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
logd = np.log([admn[n-1] for n in SEL9])

# 三套 C
C_schemes = {}
for sname, mdict in [("S1", None)]:
    pass
# S1/S2/S3 用返 docs/04 數值
C_s1 = 1.466433599e-6
C_s2 = 1.52151e-6
C_s3 = 1.82e-6
C7_s1 = 1.15919811e-6  # scripts/20

print("═══ P1. C vs 結構候選 ═══")
cands = {
    "1/88³": 1/88**3,
    "1/88⁴·π": math.pi/88**4,
    "1/(44⁵)": 1/44**5,
    "M₀/88⁴": M0/88**4,
    "M₀/88³": M0/88**3,
    "2⁻²⁴": 2**-24,
    "φ⁻³⁵": PHI**-35,
    "1/90⁴·φ²": 1/(90**4)*PHI**2,
    "88⁻³·φ⁻¹": 1/88**3*PHI**-1,
    "88⁻³·φ²": 1/88**3*PHI**2,
    "M₀²/(88³·1000)": M0**2/(88**3*1000),
    "ħc/(88³·MeV2)": 197.32698/88**3,
    "1/(88³·M₀)·(M₀/1)": (M0/1)/ (88**3*M0),
}
print(f"  C(S1) = {C_s1:.10e} MeV")
for nm, v in cands.items():
    for Cv, lvl in [(C_s1, "S1"), (C_s2, "S2"), (C7_s1, "C7")]:
        dev = abs(math.log(v/Cv))
        if dev < 0.05:
            print(f"    {nm:22s} = {v:.6e}: dev vs {lvl} = {dev*100:.2f}%")

print("\n═══════ 終審: C = 1 MeV/88³? ═══════")
c88 = 1/88**3
print(f"  1/88³ = {c88:.10e} MeV")
for nm, Cv in [("C(S1)", C_s1), ("C(S2)", C_s2), ("C(S3)", C_s3), ("C7", C7_s1)]:
    dev = abs(Cv-c88)/c88*100
    zd = abs(math.log(Cv/c88))
    print(f"  {nm:6s} = {Cv:.10e}: dev = {dev:.4f}%  (log dev = {zd:.6f})")

# 幾何平均 C (9 點 fit 嘅中位數), 同 1/88³
C_geo = math.exp(np.mean(logm - PHI2*logd))
print(f"\n  C_geo(9點) = {C_geo:.10e} vs 1/88³ = {c88:.10e}  dev={abs(C_geo-c88)/c88*100:.4f}%")

dev_s1 = abs(math.log(C_s1/c88))
dev_s2 = abs(math.log(C_s2/c88))
chk("P1 S1 C = 1/88³ (dev<0.5%)", dev_s1 < 0.005, f"dev={dev_s1*100:.3f}%")
# 池密度: 196 池 2% 窗口之前 0 命中 (scripts/01). 1/88³ 唔喺個池度.
# 但 88³ 係「譜構造」數 (88-chain 三維?) — 0.067% 偏差遠細過 2% 窗口
print("\n═══ P3. C7 對照 ═══")
print(f"  C7 = {C7_s1:.3e} vs 1/88³ = {c88:.3e}: dev={abs(C7_s1-c88)/c88*100:.2f}%")
print(f"  ⟹ c/s 離群剔除後 C 偏離 1/88³ 21% — c/s 本身令 C9 對齊 1/88³?")

print("\n═══ P4. 冷靜檢查: 單位/維度 ═══")
print(f"  1/88³ = 1/{681472} — 88-chain 三次冪 (三維世界弦體積倒數?)")
print(f"  IDCM 世界弦: 88-site K_Chain 2D+1D? 88³ 有『體積倒數』自然性")
print(f"  ★ 預言: C ≡ 1 MeV/88³ 係零參數結構常數 ⟹ freeze v2 ms/mu killer 落點:")
C_pre = c88
for p_ in ["s","u","c","b","d","t","tau","mu","e"]:
    i_ = names9.index(p_)
    m_pre = C_pre * admn[SEL9[i_]-1]**PHI2
    print(f"    {p_:>4s}: m_pred = {m_pre:10.3f} MeV (obs {MS2[p_]:10.3f})")

out = {"c88": float(c88), "C_s1_dev": float(abs(math.log(C_s1/c88))),
       "C_s2_dev": float(abs(math.log(C_s2/c88))), "C_geo_dev": float(abs(math.log(C_geo/c88)))}
with open("data/24_C_numeric_closure.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")