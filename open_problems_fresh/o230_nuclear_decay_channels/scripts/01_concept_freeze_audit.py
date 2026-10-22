#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# O230 R1 — 概念凍結 (Concept Freeze) + 前提審計 (Premise Audit)
#             + 帶電流 β 衰變算子身份 (Charged-Current Beta-Decay Operator Identity)
#
# 慣例聲明 (CONVENTION — 每個 check 標籤載明):
#   [44-mode]   fermion/node 模: gam_n = 4 sin^2(pi n / 88), n = 1..44   (sum gam = 90)
#   [88-link]   gauge/link 模:  lam_n = 4 sin^2(pi n / 88), n = 0..87   (lam_0 = 0 massless)
#   [88-L]      176-Laplacian 半集: gam_k = 4 sin^2(pi k / 176), k = 1..88
#   [scale]     M0 = 27.900915 MeV; dimensionless ratios scale-free
# ASCII-only 數學名 (f-string 內禁 Unicode 上下標)
import json, os
from fractions import Fraction as Fr
from mpmath import mp, mpf, pi, sin, exp, sqrt, nstr

mp.dps = 50
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

# ---- 結構常數 (全部由 {0,1} -> phi 推導; 此處作已知輸入引用) ----
ND, B, NG = 44, 4, 3          # N_d, B=phi^3-phi^-3=4, N_gen
L5, L4, F5, F6 = 11, 7, 5, 8  # L5=N_d/B, L4, F5, F6
M0 = mpf("27.900915")         # MeV (維度錨; dof=1, O212)

checks = []
def chk(name, ok, val=None, note=""):
    checks.append({"name": name, "pass": bool(ok), "value": val, "note": note})
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f"  = {val}" if val is not None else "") + (f"  ({note})" if note else ""))
    return ok

def claim(text):
    print(f"[CLAIM] {text}")
    claims.append(text)

claims = []

# ============================================================
# A. 概念凍結 (S0 corpus 0 命中 -> 定義自建 + 凍結)
# ============================================================
print("=== A. 概念凍結 (Concept Freeze) ===")
concept = {
    "version": "o230-r1-2026-10-08",
    "corpus_status": "v10.0 open_problems_fresh/ grep: 核衰變=0, beta decay=0, "
                     "nuclear decay=0, 中子衰變=0, alpha decay=0 (概念層從未形式化)",
    "def_channel": "核衰變通道 = 一個初核態 |i> 經算子 T_hat 躍遷到末核態 |f> + 放出粒子集合 S 之過程; "
                   "以量子數 ledgers (Q, T3L, T3R, B-L) 同模標籤 n 標定。",
    "def_decay_operator": "T_hat = (g2/sqrt2) * J^+_mu ⊗ l_mu  (帶電流), 其中 J^+_mu = psi_bar_u g^mu P_L psi_d "
                          "(idcm 費曼規則: 費米子-規範頂點 = -i g T^a g^mu P_L, O85 171/171)。",
    "def_rate_law": "Gamma = |<f|T_hat|i>|^2 * rho_ps  (離散費米黃金律: rho_ps = 鏈模密度, 非連續積分 d^3p)。",
    "def_selection": "通道選擇 = (i) 電荷守恆 Q = T3L + Y; (ii) 模守恆 sum n = 0 (mod 88)。",
    "frozen": True,
    "change_policy": "任何定義修改 = 新 doc + 明寫『移動球門』; 唔准一路做一路改定義。",
}
print("  [FROZEN] 5 個定義 (channel / decay_operator / rate_law / selection / change_policy)")
claim("本 O 之概念詞 (核衰變通道算子身份) 在 v10 corpus 0 命中 -> 定義自建並凍結於 data/01_concept_freeze.json")

# ============================================================
# B. 前提審計 (Premise Audit) — 逐項重算已閉合輸入
# ============================================================
print("\n=== B. 前提審計 ===")

# B1 [44-mode] gam_44 = B = 4 EXACT
g = [mpf(0)] + [4*sin(pi*n/88)**2 for n in range(1, 45)]   # g[1..44]
g44 = g[44]
chk("B1 [44-mode] gam_44 = 4 = B (EXACT)", abs(g44-4) < mpf("1e-45"), nstr(g44, 12), "mode chain endpoint")

# B2 [44-mode] sum gam_n = 90 = 2 N_d + mu^2
S44 = sum(g[1:45])
chk("B2 [44-mode] sum_{1..44} gam_n = 90", abs(S44-90) < mpf("1e-40"), nstr(S44, 12), "= 2 N_d + mu^2 = 88 + 2")

# B3 [44-mode] gam_n + gam_{N_d-n} = 4 = B (n=1..43) — 互補對 (n <-> N_d-n)
comp_ok = all(abs(4*sin(pi*n/88)**2 + 4*sin(pi*(ND-n)/88)**2 - 4) < mpf("1e-45") for n in range(1, ND))
chk("B3 [44-mode] gam_n + gam_{44-n} = 4 = B (all n=1..43)", comp_ok, "complementary pairing -> Dirac")

# B4 [88-link] N_d = 44 = B * L5 = 4*11
chk("B4 N_d = B * L5 = 44", ND == B*L5, f"{B*L5}")

# B5 mu^2 = 2 = sum gam_even - sum gam_odd  [44-mode parity split]
Sodd = sum(g[n] for n in range(1, 45, 2))     # n=1,3,..,43
Seven = sum(g[n] for n in range(2, 45, 2))    # n=2,4,..,44
mu2 = Seven - Sodd
chk("B5 [44-mode] mu^2 = 2 = SumEven - SumOdd", abs(mu2-2) < mpf("1e-40"),
    f"even={nstr(Seven,10)} odd={nstr(Sodd,10)} mu2={nstr(mu2,10)}")

# B6 e = g2 sin(theta_W)  (g2^2 = 4 pi / 30)
g2 = sqrt(4*pi/(ND - 2*L4))          # = sqrt(4 pi / 30)
sin2W = mpf("0.2207757330")
e_idcm = g2 * sqrt(sin2W)
chk("B6 g2 = sqrt(4pi/30) ; e = g2 sin(theta_W)", abs(g2**2 - 4*pi/30) < mpf("1e-45"),
    f"g2={nstr(g2,12)} e={nstr(e_idcm,12)}")

# B7 alpha^-1 = 3 N_d + F5 = 137 EXACT
achk = 3*ND + F5
chk("B7 alpha^-1 = 3 N_d + F5 = 137 (EXACT)", achk == 137, achk)

# B8 模守恆核: sum_{m=0}^{87} exp(2pi i K m /88) = 88 * delta_{K,0 mod 88}
def kern(K):
    return sum(exp(2j*mp.pi*K*m/88) for m in range(88))
k0 = kern(0); k1 = kern(1); k44 = kern(44); k88 = kern(88)
ok_kern = (abs(k0-88) < mpf("1e-40") and abs(k1) < mpf("1e-40")
           and abs(k44) < mpf("1e-40") and abs(k88-88) < mpf("1e-40"))
chk("B8 [88-link] Sum_m exp(2pi i K m/88) = 88 delta_{K,0 mod 88}", ok_kern,
    f"K=0:{nstr(abs(k0),8)} K=1:{nstr(abs(k1),8)} K=44:{nstr(abs(k44),8)} K=88:{nstr(abs(k88),8)}",
    "模守恆『導出』非『外加』")

# B9 費米子-規範頂點之唯一結構形 (引用 O85): -i g T^a g^mu P_L  (零新參數)
claim("費米子-規範頂點 = -i g T^a g^mu P_L (O85 171/171); beta 衰變 = 此頂點之帶電分支 T^+ = (s1+i s2)/2, "
      "零新參數, 零新結構")

# ============================================================
# C. 帶電流 β 衰變算子身份 + 通道量子數 ledger (EXACT Fractions)
# ============================================================
print("\n=== C. 帶電流算子身份 + 通道 ledger ===")
# 量子數 (左旋 Weyl): Q = T3L + Y ; Y = T3R + (B-L)/2
QN = {
    #        T3L        T3R        B          L          Y
    "u_L": (Fr(1,2),  Fr(0),    Fr(1,3),  Fr(0),  Fr(1,6)),
    "d_L": (Fr(-1,2), Fr(0),    Fr(1,3),  Fr(0),  Fr(1,6)),
    "e_L": (Fr(-1,2), Fr(0),    Fr(0),    Fr(1),  Fr(-1,2)),
    "nu_L":(Fr(1,2),  Fr(0),    Fr(0),    Fr(1),  Fr(-1,2)),
    "u_R": (Fr(0),    Fr(1,2),  Fr(1,3),  Fr(0),  Fr(2,3)),
    "d_R": (Fr(0),    Fr(-1,2), Fr(1,3),  Fr(0),  Fr(-1,3)),
    "e_R": (Fr(0),    Fr(-1,2), Fr(0),    Fr(1),  Fr(-1)),
}
def Q(name):
    t3l, t3r, b, l, y = QN[name]
    return t3l + y, y
# 自洽: Y = T3R + (B-L)/2 及 Q = T3L + Y
y_ok = all(QN[k][4] == QN[k][1] + (QN[k][2]-QN[k][3])/2 for k in QN)
q_ok = all(QN[k][0] + QN[k][4] == Q(k)[0] for k in QN)
chk("C1 Y = T3R + (B-L)/2 及 Q = T3L + Y (all Weyl states)", y_ok and q_ok, "8 anomaly basis")
chk("C2 Q(u)=+2/3, Q(d)=-1/3, Q(e-)=-1, Q(nu)=0",
    (Q("u_L")[0], Q("d_L")[0], Q("e_L")[0], Q("nu_L")[0]) == (Fr(2,3), Fr(-1,3), Fr(-1), Fr(0)),
    str([str(Q(x)[0]) for x in ("u_L","d_L","e_L","nu_L")]))

# 通道電荷 + B-L ledger (含放出粒子; 反粒子 = 共軛: T3->-T3, B,L->-neg, Y->-Y)
def antip(name):
    t3l,t3r,b,l,y = QN[name]
    return (-t3l,-t3r,-b,-l,-y)
def lep_Q(part):
    # part: ('e-',...) etc; return (charge, B-L, T3L)
    if part == "e-":  return (Q("e_L")[0], QN["e_L"][2]-QN["e_L"][3], QN["e_L"][0])
    if part == "e+":  a=antip("e_L"); return (a[0]+a[4], a[2]-a[3], a[0])
    if part == "nu":  return (Q("nu_L")[0], QN["nu_L"][2]-QN["nu_L"][3], QN["nu_L"][0])
    if part == "nub": a=antip("nu_L"); return (a[0]+a[4], a[2]-a[3], a[0])

def channel_ledger(name, init_had, init_leps, fin_had, fin_leps):
    Q0 = Q(init_had)[0] + sum(lep_Q(p)[0] for p in init_leps)
    Qf = Q(fin_had)[0] + sum(lep_Q(p)[0] for p in fin_leps)
    BL = lambda nm: QN[nm][2]-QN[nm][3]
    BL0 = BL(init_had) + sum(lep_Q(p)[1] for p in init_leps)
    BLf = BL(fin_had) + sum(lep_Q(p)[1] for p in fin_leps)
    dT3L = QN[fin_had][0] - QN[init_had][0]
    ok = (Qf == Q0) and (BLf == BL0)
    return ok, {"init": name, "Q_in": str(Q0), "Q_out": str(Qf),
                "BL_in": str(BL0), "BL_out": str(BLf), "dT3L_had": str(dT3L)}

chans = {
    "beta_minus":       ("d_L", [],         "u_L", ["e-", "nub"]),   # d -> u + e- + nu_bar
    "beta_plus":        ("u_L", [],         "d_L", ["e+", "nu"]),    # u -> d + e+ + nu
    "electron_capture": ("u_L", ["e-"],     "d_L", ["nu"]),          # u + e- -> d + nu (e- 被吸收)
}
res = {}
for nm, (i, il, f, fl) in chans.items():
    ok, led = channel_ledger(nm, i, il, f, fl)
    res[nm] = led
    chk(f"C3 {nm}: Q 守恆 & B-L 守恆", ok, f"Q {led['Q_in']}->{led['Q_out']} BL {led['BL_in']}->{led['BL_out']} dT3L_had={led['dT3L_had']}")

# C4 帶電流 ΔT3L: beta- hadronic +1, beta+ hadronic -1 (庫侖補償方向相反)
chk("C4 帶電流方向: beta- dT3L_had=+1 ; beta+/EC dT3L_had=-1",
    res["beta_minus"]["dT3L_had"] == "1" and res["beta_plus"]["dT3L_had"] == "-1"
    and res["electron_capture"]["dT3L_had"] == "-1",
    f"{res['beta_minus']['dT3L_had']}/{res['beta_plus']['dT3L_had']}/{res['electron_capture']['dT3L_had']}")

# ============================================================
# D. 誠實 ledger — 上游阻塞 + 未確立
# ============================================================
print("\n=== D. 誠實 ledger ===")
blocked = [
    ("RATE", "Gamma = |M|^2 rho_ps 之數值 — 需核子/強子束縛態波函數 <f|J^+|i>", "O124 §G / O144 §4.3 上游阻塞"),
    ("PHASE_SPACE", "離散相空間 rho_ps 之連續極限 (-> Sargent E^5 律) — 需 O221 連續極限", "O221"),
    ("ALPHA", "alpha 穿隧通道 — 完全空白 (corpus 0 命中)", "本 O, 未開始"),
    ("NUCLEAR_WF", "核束縛態本身未導出", "上游"),
]
for k, v, src in blocked:
    claim(f"[BLOCKED-{k}] {v}  <-- {src}")

# ============================================================
# 收尾
# ============================================================
npass = sum(1 for c in checks if c["pass"])
ntot = len(checks)
print(f"\nRESULT: {npass}/{ntot} PASS")
print(f"[CLAIM] 條數 = {len(claims)} (結構聲稱, 排除於 PASS 分母外)")

out = {
    "round": "R1", "date": "2026-10-08", "convention": "44-mode / 88-link / 88-L (labelled per check)",
    "concept_freeze": concept,
    "checks": checks, "pass": npass, "total": ntot,
    "claims": claims, "blocked": [{"item": k, "detail": v, "source": s} for k, v, s in blocked],
    "channel_ledgers": res,
    "inputs": {"N_d": ND, "B": B, "N_gen": NG, "L5": L5, "L4": L4, "F5": F5,
               "M0_MeV": str(M0), "sin2thetaW": str(sin2W), "e_idcm": nstr(e_idcm, 15),
               "alpha_inv": achk},
}
with open(os.path.join(DATA, "01_concept_freeze_audit.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
with open(os.path.join(DATA, "01_concept_freeze.json"), "w", encoding="utf-8") as fh:
    json.dump(concept, fh, ensure_ascii=False, indent=2)
print(f"data written: {os.path.join(DATA,'01_concept_freeze_audit.json')}")