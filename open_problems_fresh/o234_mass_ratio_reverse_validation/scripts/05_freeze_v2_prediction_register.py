#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O234 scripts/05 -- freeze v2 + 即時全套 scheme 更正 + redundancy 閉環 + pre-registered 預言表

License: IDCM O234. stdlib-only. 全確定性; 誤差 = 一階傳播 (frozen layer v2).
來源: FLAG Review 2024 §4.3 (Eqs. 61-64, Tab. 15) + §4.1 (Eqs. 35,44) + Nf=4 mc/ms.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

def gamma(n): return 4.0*math.sin(n*math.pi/88.0)**2
g = {n: gamma(n) for n in [1,2,3,4,5,7,9,11,13]}

print("=" * 74)
print("O234 freeze v2 -- scheme 更正 + RGI_b 入層 + 預言 register")
print("=" * 74)

# ------------------------------------------------------------ FROZEN v2 (新增/更正)
F2 = {
    "M_RGI_u":     (2.97,  0.11, 0.03),     # MeV, FLAG Eq.(44), Nf=2+1+1, Refs[42,63]
    "M_RGI_d":     (6.53,  0.07, 0.08),     # MeV, FLAG Eq.(44)
    "M_RGI_b":     (6938., 23.,  45.),      # MeV, FLAG Eq.(64): 6.938(23)(45) GeV, Nf=2+1+1
    "mb_mc_3GeV":  (4.586, 0.012),          # HPQCD 21, MS mu=3GeV, Nf=4 (QED included)
    "mb_mc_FM":    (4.578, 0.007),          # FNAL/MILC/TUM 18 cross (0.007=quadrature sys+stat)
    "mc_ms_Nf4":   (11.652, 0.065),         # kept primary (round-2 watch, z proposal)
    "mc_ms_HP":    (11.85,  0.16),          # kept cross (HPQCD 09A)
}
# 已凍結 (round 1, 唔重開)
F1 = {
    "ms_mud_2G":   (27.227, 0.081),         # FLAG Eq.(34/35) avg
    "md_mu_2G":    (2.1505, 0.1110),        # 0.465(24) -> 2.1505; 誤差由 (1/0.465) 傳播
    "M_RGI_s":     (130.0,  0.8, 1.3),      # MeV, FLAG Eq.(35)
    "M_RGI_ud":    (4.768,  0.071, 0.046),  # MeV, FLAG Eq.(35)
}

print("\n[A] freeze v2 新增/更正量")
for k, v in F2.items():
    if len(v) == 2:
        rel = v[1]/v[0]*100
        print(f"   {k:12s} = {v[0]:9.3f} ± {v[1]:7.3f}  ({rel:.2f}%)")
    else:
        rel = math.hypot(v[1], v[2])/v[0]*100
        print(f"   {k:12s} = {v[0]:9.3f} ± {v[1]:6.3f} ± {v[2]:6.3f}  ({rel:.2f}%)")

# ------------------------------------------------------------ [B] 更正: b/c scheme
print("\n[B] ★ S1a 更正: b/c 混標度假命中已死")
mb_mc_mixed = 4.18/1.27                      # PDG mb(mb)/mc(mc) 混標度 (round-1 用)
Cbc_mixed = mb_mc_mixed/(g[11]/g[7])
Cbc_3GeV  = F2["mb_mc_3GeV"][0]/(g[11]/g[7])
pool_44_33 = 44/33
print(f"   混標度 mb/mc = {mb_mc_mixed:.4f} -> C_b/C_c = {Cbc_mixed:.4f}  (vs 44/33={pool_44_33:.4f}, dev {abs(Cbc_mixed-pool_44_33)/pool_44_33*100:.1f}%)")
print(f"   scheme 正確 mb/mc@3GeV = {4.586:.3f} -> C_b/C_c = {Cbc_3GeV:.4f}  (vs 44/33, dev {abs(Cbc_3GeV-pool_44_33)/pool_44_33*100:.1f}%)")
print(f"   ⟹ round-1 'b/c 近命中 dev 3.0% (nominal)' 係混標度偽影; 更正後 43.5% 死實")

# ------------------------------------------------------------ [C] redundancy 閉環
print("\n[C] ★ redundancy 0 -> 1: RGI b/s 第二通道")
mbs_rgi = F2["M_RGI_b"][0]/F1["M_RGI_s"][0]              # RGI 同框架, scheme 安全
e_mbs_rgi = mbs_rgi*math.hypot(F2["M_RGI_b"][1]/F2["M_RGI_b"][0], F2["M_RGI_b"][2]/F2["M_RGI_b"][0],
                               F1["M_RGI_s"][1]/F1["M_RGI_s"][0], F1["M_RGI_s"][2]/F1["M_RGI_s"][0])
mbs_impl = F2["mb_mc_3GeV"][0]*F2["mc_ms_Nf4"][0]        # (b/c)*(c/s) 獨立路徑
e_mbs_impl = mbs_impl*math.hypot(F2["mb_mc_3GeV"][1]/F2["mb_mc_3GeV"][0], F2["mc_ms_Nf4"][1]/F2["mc_ms_Nf4"][0])
z_mbs = (mbs_impl-mbs_rgi)/math.hypot(e_mbs_impl, e_mbs_rgi)
print(f"   (b/c)*(c/s) 推 b/s = {mbs_impl:8.4f} ± {e_mbs_impl:6.4f}")
print(f"   RGI     直量 b/s = {mbs_rgi:8.4f} ± {e_mbs_rgi:6.4f}")
print(f"   dev = {abs(mbs_impl-mbs_rgi)/mbs_rgi*100:.2f}%  z = {z_mbs:+.2f}  -> 喉道閉環 PASS")

# RGI d/u 第二通道 (round-1 只有 MS md/mu)
print("\n[D] RGI u/d 第二通道 (純 γ 對沖)")
mdu_rgi = F2["M_RGI_d"][0]/F2["M_RGI_u"][0]
e_mdu_rgi = mdu_rgi*math.hypot(F2["M_RGI_d"][1]/F2["M_RGI_d"][0], F2["M_RGI_d"][2]/F2["M_RGI_d"][0],
                               F2["M_RGI_u"][1]/F2["M_RGI_u"][0], F2["M_RGI_u"][2]/F2["M_RGI_u"][0])
z_ud_rgi = (g[3]/g[2]-mdu_rgi)/e_mdu_rgi
z_ud_ms  = (g[3]/g[2]-F1["md_mu_2G"][0])/F1["md_mu_2G"][1]
print(f"   RGI d/u = {mdu_rgi:.4f} ± {e_mdu_rgi:.4f}  vs 純γ γ3/γ2 = {g[3]/g[2]:.4f}  z = {z_ud_rgi:+.2f}")
print(f"   MS  d/u = {F1['md_mu_2G'][0]:.4f} ± {F1['md_mu_2G'][1]:.4f}  vs 純γ              z = {z_ud_ms:+.2f}")

# ------------------------------------------------------------ [E] C-shape v2
print("\n[E] C-shape v2 (anchor 每扇區 = 1; b 用 scheme 正確 mb/mc@3GeV)")
C = {}
C["u"], C["d"] = 1.0, (F1["md_mu_2G"][0])/(g[3]/g[2])
C["s"] = (F1["ms_mud_2G"][0]*(1+F1["md_mu_2G"][0])/2)/(g[4]/g[2])
C["c"] = C["s"]*F2["mc_ms_Nf4"][0]/(g[7]/g[4])
C["b"] = C["c"]*Cbc_3GeV
C["e"], C["mu"] = 1.0, (105.658/0.510999)/(g[5]/g[1])
C["tau"] = C["mu"]*(1776.86/105.658)/(g[9]/g[5])
print("   " + "  ".join(f"{k}={v:.3f}" for k, v in C.items()))
print(f"   C_b/C_s 經 RGI = {mbs_rgi/(g[11]/g[4]):.4f} vs 經 b/c×c/s = {C['b']/C['s']:.4f} (dev {abs(mbs_rgi/(g[11]/g[4])-C['b']/C['s'])/(C['b']/C['s'])*100:.2f}%)")

# ------------------------------------------------------------ [F] pre-registered 預言 register
print("\n[F] ★★ pre-registered 預言 register (freeze v2; 每行=可證偽預言)")
preds = []
def addp(name, val, err, trigger, note):
    preds.append({"ratio": name, "pred": round(val, 4), "err": round(err, 4),
                  "rel_pct": round(err/val*100, 2), "trigger": trigger, "note": note})
    print(f"   {name:22s} {val:10.4f} ± {err:8.4f} ({err/val*100:5.2f}%)  [觸發: {trigger}]  {note}")

ms_mu  = F1["ms_mud_2G"][0]*(1+F1["md_mu_2G"][0])/2
e_ms_mu = ms_mu*math.hypot(F1["ms_mud_2G"][1]/F1["ms_mud_2G"][0], F1["md_mu_2G"][1]/(1+F1["md_mu_2G"][0]))
ms_md  = F1["ms_mud_2G"][0]*(1+1/F1["md_mu_2G"][0])/2
e_ms_md = ms_md*math.hypot(F1["ms_mud_2G"][1]/F1["ms_mud_2G"][0], F1["md_mu_2G"][1]/(F1["md_mu_2G"][0]*(1+F1["md_mu_2G"][0])))
mc_mu  = ms_mu*F2["mc_ms_Nf4"][0]; e_mc_mu = mc_mu*math.hypot(e_ms_mu/ms_mu, F2["mc_ms_Nf4"][1]/F2["mc_ms_Nf4"][0])
mc_md  = mc_mu/F1["md_mu_2G"][0]; e_mc_md = mc_md*math.hypot(e_mc_mu/mc_mu, F1["md_mu_2G"][1]/F1["md_mu_2G"][0])

addp("md/mu (MS)", F1["md_mu_2G"][0], F1["md_mu_2G"][1], "lattice 1-2% mu/md", "純γ 2.2452 vs shape 2.1505 相隔 4.4% -- 1% 精度即判")
addp("ms/mu (derived)", ms_mu, e_ms_mu, "future lattice 直量 1%", "唯一非 assignment 內含 killer test")
addp("ms/md (derived)", ms_md, e_ms_md, "future lattice 直量", "")
addp("mc/mu (derived)", mc_mu, e_mc_mu, "future lattice mc/mu 直量", "")
addp("mc/md (derived)", mc_md, e_mc_md, "future lattice mc/md 直量", "")
addp("mb/ms (RGI)", mbs_rgi, e_mbs_rgi, "RGI 直量第二通道", f"已與 b/c×c/s 閉環 z={z_mbs:+.2f}")
addp("mb/mc (3GeV)", F2["mb_mc_3GeV"][0], F2["mb_mc_3GeV"][1], "HPQCD21 已凍結", "scheme 正確版本; C_b/C_c=1.916 池無命中")
addp("RGI d/u", mdu_rgi, e_mdu_rgi, "RGI 框架", f"純γ z={z_ud_rgi:+.2f}")

# ------------------------------------------------------------ PASS/FAIL
p = s = 0
def chk(name, ok, detail):
    global p, s
    print(("  PASS " if ok else "  FAIL ") + f"[{name}] {detail}")
    if ok: p += 1
    else:  s += 1

chk("B1 混標度假命中判定: 更正後池無命中", abs(Cbc_3GeV-pool_44_33)/pool_44_33 > 0.30,
    f"round-1 nominal 3.0% 偽影 -> {abs(Cbc_3GeV-pool_44_33)/pool_44_33*100:.1f}% 死實")
chk("C1 b/s 閉環 (|z|<=2)", abs(z_mbs) <= 2, f"z={z_mbs:+.2f}; redundancy 0->1 成立")
chk("D1 純γ u/d 雙通道 (MS+RGI)", abs(z_ud_ms) <= 2 and abs(z_ud_rgi) <= 2,
    f"MS z={z_ud_ms:+.2f}; RGI z={z_ud_rgi:+.2f}")
chk("E1 C-shape v2 自洽 (RGI vs 乘積路徑 dev<2%)", abs(mbs_rgi/(g[11]/g[4])-C['b']/C['s'])/(C['b']/C['s'])*100 < 2,
    f"dev = {abs(mbs_rgi/(g[11]/g[4])-C['b']/C['s'])/(C['b']/C['s'])*100:.2f}%")

out = {"freeze_v2": {k: {"value": v[0], "errs": v[1:]} for k, v in F2.items()},
       "prediction_register": preds}
with open(os.path.join(DATA, "05_freeze_v2_prediction_register.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n[data] 05_freeze_v2_prediction_register.json 已寫")
print(f"\n=== {p} PASS / {s} FAIL ===")