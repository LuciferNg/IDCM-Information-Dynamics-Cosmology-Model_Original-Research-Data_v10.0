#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_numerology_null_230.py — δ_PMNS = 230° (= 5×46) 嘅 numerology 判證
=====================================================================
背景: ckm_reconstruction/docs/09 §14.4 + Master Theorem T9 提 δ_PMNS = (K_tree+F₇)(L₅−2N_gen)
      = 46×5 = 230.00° EXACT, 並宣稱「雙重選擇規則 (mod-5 ∧ J_CP) 唯一鎖定」。

本 script 對該聲稱跑 4 Hard Tests:
  H1 dof 成本 (0 參數?)
  H2 Monte-Carlo / 窮舉 null: 結構常數池 + 表達式預算 ≤3 → 覆蓋 [0,360) 程度
  H3 可證偽/盲測: J_CP 判別是否循環 (用 δ match δ) + 對現行擬合
  H4 剛性: ±1 擾動存活率
判準: coverage ~100% ⟹ p(hit) ≈ 1 ⟹ 零信息量 ⟹ numerology
"""
import itertools, math

# ── IDCM 結構常數池 (公理 A1-A4 + O-series 身份, 35 個) ────────────────────
C = {'B':4,'N_gen':3,'L5':11,'F7':13,'K_tree':33,'N_d':44,'mu2':2,'SgE':90,'SgO':88,
     'F5':5,'L4':7,'L6':18,'F6':8,'L7':29,'F8':21,'F10':55,'Ndm':42,'Ndp':46,
     'F4':3,'F3':2,'L3':4,'F9':34,'L10':123,'Sg_all':178,'N_d_minus_B':40,'L5p':12,
     'N_gen2':9,'B2':16,'B3':64,'KpF7':46,'gamma44':2,'N_obs':88,'N_world':90,
     'pi_deg':180,'E_min_num':123}
vals = list(C.items())

def deg(x):
    if isinstance(x, complex): return None
    if abs(x - round(x)) > 1e-9: return None
    return int(round(x)) % 360

reached, wit = set(), {}
def add(n, e):
    if n is None: return
    reached.add(n); wit.setdefault(n, e)

for k, v in vals: add(deg(v), k)
for (ka,a),(kb,b) in itertools.combinations_with_replacement(vals, 2):
    add(deg(a*b), f"{ka}*{kb}"); add(deg(a+b), f"{ka}+{kb}"); add(deg(a-b), f"{ka}-{kb}")
    if b and abs(a/b-round(a/b)) < 1e-9: add(deg(a/b), f"{ka}/{kb}")
for (ka,a),(kb,b),(kc,c) in itertools.combinations_with_replacement(vals, 3):
    add(deg(a*b+c), f"{ka}*{kb}+{kc}"); add(deg(a*b-c), f"{ka}*{kb}-{kc}")
    add(deg(a*(b+c)), f"{ka}*({kb}+{kc})"); add(deg(a*(b-c)), f"{ka}*({kb}-{kc})")
    add(deg((a+b)*c), f"({ka}+{kb})*{kc}"); add(deg((a-b)*c), f"({ka}-{kb})*{kc}")
    add(deg(a+b+c), f"{ka}+{kb}+{kc}"); add(deg(a+b-c), f"{ka}+{kb}-{kc}")

print("="*76)
print("  230° = 5×46 numerology 判證 (4 Hard Tests)")
print("="*76)
print(f"\n  H1. dof 成本: 形式 0 參數 ✓ (但下面 3 關決定信息量)")
cov = len(reached)/360
print(f"\n  H2. 窮舉 null (常數池 {len(vals)} 個, 表達式預算 ≤3 常數):")
print(f"      [0,360) 可達整數角 = {len(reached)}/360 = {cov*100:.1f}%")
print(f"      ⇒ p(隨機目標被某式命中) ≈ {cov:.2f}  (≡ 1 ⇒ 零信息量)")
print(f"      230 可達? {230 in reached}   witness: {wit.get(230)}")

w = set()
for (ka,a),(kb,b),(kc,c) in itertools.combinations_with_replacement(vals, 3):
    for e,v in [(f"{ka}*{kb}+{kc}",a*b+c),(f"{ka}*{kb}-{kc}",a*b-c),(f"{ka}*({kb}+{kc})",a*(b+c)),
                (f"{ka}*({kb}-{kc})",a*(b-c)),(f"({ka}+{kb})*{kc}",(a+b)*c),(f"({ka}-{kb})*{kc}",(a-b)*c),
                (f"{ka}+{kb}+{kc}",a+b+c),(f"{ka}+{kb}-{kc}",a+b-c)]:
        if deg(v) == 230: w.add(e)
for (ka,a),(kb,b) in itertools.combinations_with_replacement(vals, 2):
    for e,v in [(f"{ka}*{kb}",a*b),(f"{ka}+{kb}",a+b),(f"{ka}-{kb}",a-b)]:
        if deg(v) == 230: w.add(e)
print(f"      命中 230 嘅 distinct 結構式 = {len(w)} 條 (「唯一」係假象)")
for e in sorted(w)[:6]: print(f"        · {e}")

print(f"\n  H3. 可證偽/盲測:")
print(f"      原聲稱判準 2「J_CP 0.4% vs NuFIT」— 用 δ=232° (同一擬合) 導出 ⇒ 循環")
def Jmax(s2_12,s2_23,s2_13):
    s12,s23,s13=math.sqrt(s2_12),math.sqrt(s2_23),math.sqrt(s2_13)
    c12,c23,c13=math.sqrt(1-s2_12),math.sqrt(1-s2_23),math.sqrt(1-s2_13)
    return s12*c12*s23*c23*s13*c13**2
Jm=Jmax(0.30815,0.57512,0.02259)
for nm,d in [("NuFIT6.0 NO",177),("NuFIT6.1 NO",212),("PDG2025",217.8),("IDCM 230",230)]:
    print(f"      δ={nm:<12s}{d:6.1f}° → J_CP = {Jm*abs(math.sin(math.radians(d))):.5f}")
print(f"      ⇒ J(230)=0.0255 但現行 J(212)≈0.0177 → 44% off; 冇 CP-獨立預言")

print(f"\n  H4. 剛性 (±1 擾動 N_gen, L₅, F₇):")
surv=tot=0
for Ng in (2,3,4):
    for L5 in (10,11,12):
        for F7 in (12,13,14):
            v=((Ng*L5)+F7)*(L5-2*Ng); tot+=1
            if abs(v-230)<1e-12: surv+=1
print(f"      (N_gen·L₅+F₇)(L₅−2N_gen)=230 存活 {surv}/{tot} (僅 nominal)")
print(f"      ⇒ 配合 H2 嘅 {len(w)} witness, 剛性無意義 (精確整數巧合)")

print("\n" + "="*76)
print("  裁決")
print("="*76)
print(f"      H1 ✔ 0 參數 | H2 ✘ coverage {cov*100:.0f}% | H3 ✘ 循環+無獨立預言 | H4 ✘ 剛性空虛")
print(f"      ⇒ δ_PMNS = 230° = numerology 級 (🟡→🔴), 唔可以宣稱閉合")
print(f"      ⇒ 但 46 = Σγ(k≡0 mod 4) = 46.000000 係真身份 🟢 (死嘅係 ×5 同「唯一」)")
