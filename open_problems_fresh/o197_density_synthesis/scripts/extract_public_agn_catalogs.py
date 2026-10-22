#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O197 — 抽取公開高 z AGN 黑洞質量目錄 (w 份額 data-gate 攻堅)

來源 (全部公開, arXiv HTML 直連):
  1. Taylor+2025 (ApJ 986,165; arXiv:2409.06772) Table 1 — 62 Hα BLAGN, 3.5<z<6.8 (CEERS+RUBIES)
     同 Table 3 — 完整度修正 BHMF (5 mass bins, Φ/N/completeness)
  2. Juodžbalis+2026 (MNRAS 546; arXiv:2504.03551) Table 2 — 34 Type-1 broad-line AGN, 1.5<z<9 (JADES)

輸出: JSON 目錄檔 (供 scripts/15 計算 w)
"""
import re, json, html as H
from pathlib import Path

SRC = Path("/tmp/o197_data")
OUT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/"
           "open_problems_fresh/o197_density_synthesis/data")
OUT.mkdir(parents=True, exist_ok=True)


def cells(row):
    """抽 cell 純文字 — ⚠️ 必須先刪 <annotation> (x-tex alttext) 否則值會重複
    (e.g. '258−113+125' + annotation '258^{+125}_{-113}' → 誤讀 125258)"""
    out = []
    for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S):
        c = re.sub(r'<annotation[^>]*>.*?</annotation>', '', c, flags=re.S)
        t = H.unescape(re.sub(r'<[^>]+>', '', c))
        out.append(re.sub(r'\s+', ' ', t).strip())
    return out


def table_rows(fn, idx):
    r = open(SRC / fn, encoding='utf-8', errors='replace').read()
    tabs = list(re.finditer(r'<table(.*?)</table>', r, re.S))
    seg = tabs[idx].group(1)
    return [cells(x) for x in re.findall(r'<tr[^>]*>(.*?)</tr>', seg, re.S)]


def first_num(s):
    """由 '7.66−0.07+0.087.66_{-0.07}' 之類抽首個數 (去 MathML 重複)"""
    m = re.match(r'^[−-]?[0-9]*\.?[0-9]+', s.replace('−', '-'))
    return float(m.group(0)) if m else None


def num_err(s):
    """抽 值+上下誤差: '7.66−0.07+0.08...' → (7.66, -0.07, +0.08)"""
    s = s.replace('−', '-')
    m = re.match(r'^(-?[0-9]*\.?[0-9]+)(?:-([0-9]*\.?[0-9]+))?(?:\+([0-9]*\.?[0-9]+))?', s)
    if not m:
        return None, None, None
    v = float(m.group(1))
    lo = float(m.group(2)) if m.group(2) else None
    hi = float(m.group(3)) if m.group(3) else None
    return v, lo, hi


# ---------------- 1. Taylor+2025 Table 1 ----------------
rows = table_rows('taylor25.html', 0)
tay = []
for r in rows[2:]:
    if len(r) < 9 or not r[0] or 'RUBIES' not in r[0] and 'CEERS' not in r[0]:
        continue
    name = r[0].replace('†', '').replace('‡', '').strip()
    z = first_num(r[3])
    # r[4] F_Hα (total), r[5] F_Hα,narrow, r[6] F_Hα,broad — 單位 1e-18 erg/s/cm²
    f_tot, _, _ = num_err(r[4])
    f_nar, _, _ = num_err(r[5])
    f_bro, f_bro_lo, f_bro_hi = num_err(r[6])
    fwhm, _, _ = num_err(r[7])
    logM, lo, hi = num_err(r[8])
    tay.append(dict(name=name, z=z, logM=logM, logM_lo=lo, logM_hi=hi,
                    f_halpha=f_tot, f_halpha_narrow=f_nar,
                    f_halpha_broad=f_bro, f_halpha_broad_lo=f_bro_lo,
                    f_halpha_broad_hi=f_bro_hi,
                    fwhm_broad=fwhm, survey='Taylor+2025', instrument='NIRSpec G395M'))

# 去重: 論文 §3 明示 CEERS-2782 同 RUBIES-EGS-50052 係**同一源** (兩次觀測),
# 佢哋採用 RUBIES 觀測 ⟹ 剔除 CEERS-2782, 最終 62 個唯一源。
DUP_DROP = {'CEERS-2782'}
seen, tay_u = {}, []
for d in tay:
    if d['name'] in seen or d['name'] in DUP_DROP:
        continue
    seen[d['name']] = 1
    tay_u.append(d)

# ---------------- 2. Taylor+2025 Table 3 (BHMF) ----------------
bhmf_rows = table_rows('taylor25.html', 4)
bhmf = []
for r in bhmf_rows[2:]:
    if not r or first_num(r[0]) is None:
        continue
    m = first_num(r[0])
    phi, plo, phi_hi = num_err(r[1])
    ncorr = first_num(r[2])
    comp = [first_num(x) for x in r[3:6]]
    bhmf.append(dict(logM_center=m, Phi=phi, Phi_lo=plo, Phi_hi=phi_hi,
                     N_corr=ncorr, comp_total=comp[0], comp_obs=comp[1], comp_det=comp[2]))

# ---------------- 3. JADES 34 (Juodžbalis+2026) ----------------
jrows = table_rows('jades34.html', 7)
jades, cat = [], None
for r in jrows[1:]:
    if len(r) == 1:
        cat = r[0]
        continue
    if len(r) < 8 or not r[0] or r[0] == 'Object ID':
        continue
    logM, lo, hi = num_err(r[4])
    lam, _, _ = num_err(r[6])
    jades.append(dict(name=r[0], z=first_num(r[3]), logM=logM, logM_lo=lo, logM_hi=hi,
                      lam_Edd=lam, class_=cat, survey='JADES (Juodzbalis+2026)',
                      instrument='NIRSpec R1000/R2700'))

payload = dict(
    source_notes={
        'Taylor+2025': 'ApJ 986,165 (arXiv:2409.06772) Table 1+3; Hα BLAGN, CEERS+RUBIES, 3.5<z<6.8',
        'JADES34': 'MNRAS 546,3 (arXiv:2504.03551) Table 2; Type-1 broad-line AGN, 1.5<z<9',
        'urls': ['https://arxiv.org/html/2409.06772v2', 'https://arxiv.org/html/2504.03551'],
    },
    taylor25_blagn=tay_u, taylor25_bhmf=bhmf, jades34_agn=jades)

p = OUT / "highz_agn_bh_mass_catalogs.json"
p.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding='utf-8')

print(f"寫入 {p}")
print(f"  Taylor+2025 Table 1: {len(tay)} 行 → 去重後 {len(tay_u)} 個源")
print(f"  Taylor+2025 Table 3 (BHMF): {len(bhmf)} bins")
print(f"  JADES 34: {len(jades)} 個源  (Robust {sum(1 for d in jades if d['class_']=='Robust')}, "
      f"Tentative {sum(1 for d in jades if d['class_']=='Tentative')}, "
      f"Tentative Hβ {sum(1 for d in jades if d['class_'] and 'H' in d['class_'] and d['class_']!='Robust')})")
print()
print("Taylor+2025 logM 範圍:", f"{min(d['logM'] for d in tay_u):.2f} – {max(d['logM'] for d in tay_u):.2f}")
print("JADES logM 範圍     :", f"{min(d['logM'] for d in jades):.2f} – {max(d['logM'] for d in jades):.2f}")
print("Taylor z 範圍       :", f"{min(d['z'] for d in tay_u):.2f} – {max(d['z'] for d in tay_u):.2f}")
print("JADES z 範圍        :", f"{min(d['z'] for d in jades):.2f} – {max(d['z'] for d in jades):.2f}")
print()
print("Taylor F_Hα,broad 範圍 [1e-18 erg/s/cm²]:",
      f"{min(d['f_halpha_broad'] for d in tay_u if d['f_halpha_broad']):.2f} – "
      f"{max(d['f_halpha_broad'] for d in tay_u if d['f_halpha_broad']):.2f}",
      f"({sum(1 for d in tay_u if d['f_halpha_broad'])}/{len(tay_u)} 有值)")
print()
print("BHMF bins:")
for b in bhmf:
    print(f"  logM {b['logM_center']:.2f}  Φ={b['Phi']:8.2f} (+{b['Phi_hi']}/-{b['Phi_lo']})  "
          f"N_corr={b['N_corr']:6.2f}  comp(T/O/D)={b['comp_total']}/{b['comp_obs']}/{b['comp_det']}")
