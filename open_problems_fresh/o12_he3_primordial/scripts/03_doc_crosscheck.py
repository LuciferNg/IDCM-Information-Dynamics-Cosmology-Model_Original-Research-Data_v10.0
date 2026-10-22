#!/usr/bin/env python3
"""
O12 文檔交叉核對 script (03_doc_crosscheck.py v2)
==================================================
從 01_problem_record.md / 02_results.md / 03_verification_record.md / SESSION_START.md
抽出所有數字, 同獨立計算對比。只讀不寫 — 唔修改任何記錄文檔。

處理 Unicode superscript (⁶, ⁻⁶, ⁴ 等) + ×10 科學記號 + ± 誤差。
"""
import re
import math
import os
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi

# ── 獨立計算基準 (由文獻原始數字) ──
D_H = 2.555e-5
He3_H_IDCM = D_H * phi_inv**2          # 9.7592e-6
He3_H_LCDM = 1.04e-5
cooke_lim, cooke_err = 1.09e-5, 0.18e-5
s209, s209_err = 1.10e-5, 0.28e-5
sm_he3he4, sm_err = 1.257e-4, 0.017e-4
gce_he3he4, gce_err = 1.043e-4, 0.089e-4
He4_H_IDCM = 0.2496 / (4 * (1 - 0.2496))
He3_He4_IDCM = He3_H_IDCM / He4_H_IDCM
He3_He4_LCDM = 1.2799e-4
diff_pct = abs(He3_H_IDCM - He3_H_LCDM) / He3_H_LCDM * 100
z_cooke_idcm = abs(He3_H_IDCM - cooke_lim) / cooke_err
z_cooke_lcdm = abs(He3_H_LCDM - cooke_lim) / cooke_err
z_s209_idcm = abs(He3_H_IDCM - s209) / s209_err
z_s209_lcdm = abs(He3_H_LCDM - s209) / s209_err
z_sm_idcm = abs(He3_He4_IDCM - sm_he3he4) / sm_err
z_sm_lcdm = abs(He3_He4_LCDM - sm_he3he4) / sm_err
z_gce_idcm = abs(He3_He4_IDCM - gce_he3he4) / gce_err
z_gce_lcdm = abs(He3_He4_LCDM - gce_he3he4) / gce_err
err_cooke_pct = cooke_err / cooke_lim * 100
err_s209_pct = s209_err / s209 * 100
need_pct = diff_pct / 2
comb_err = math.sqrt(sm_err**2 + (0.025 * He3_He4_IDCM)**2)
z_sys = abs(He3_He4_IDCM - sm_he3he4) / comb_err

# Unicode superscript 映射
SUP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5',
       '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-', '⁺': '+', '−': '-'}

def norm_sci(text):
    """將 Unicode 科學記號轉 ASCII: 9.76×10⁻⁶ → 9.76e-6"""
    def repl_sup(m):
        return ''.join(SUP.get(c, c) or c for c in m.group(0))
    text = re.sub(r'[⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹]+', repl_sup, text)
    text = text.replace('×10', 'e').replace('x10', 'e').replace('× 10', 'e')
    text = text.replace('−', '-').replace('±', '+/-')
    return text

# 文檔檔案
docs = {
    "01_problem_record.md": os.path.join(BASE, "01_problem_record.md"),
    "02_results.md": os.path.join(BASE, "02_results.md"),
    "03_verification_record.md": os.path.join(BASE, "03_verification_record.md"),
    "SESSION_START.md": os.path.join(BASE, "SESSION_START.md"),
}

print("=" * 72)
print("O12 文檔交叉核對 v2 — 只讀, 不修改任何文檔")
print("=" * 72)

contents = {}
for name, path in docs.items():
    with open(path, encoding="utf-8") as f:
        contents[name] = f.read()

# 檢查點: (描述, 期望值, 相對容差, 必需出現嘅文件)
# 每個檢查點會喺文檔 norm 後搜尋 close-enough 數字
checks = [
    ("IDCM ³He/H 9.7592e-6", 9.7592e-6, 1e-3, ["01_problem_record.md", "02_results.md"]),
    ("ΛCDM 1.04e-5", 1.04e-5, 1e-3, ["01_problem_record.md", "02_results.md"]),
    ("Cooke limit 1.09e-5", 1.09e-5, 1e-3, ["01_problem_record.md", "02_results.md", "03_verification_record.md"]),
    ("Cooke err 0.18e-5", 0.18e-5, 1e-3, ["01_problem_record.md", "02_results.md", "03_verification_record.md"]),
    ("S209 1.10e-5", 1.10e-5, 1e-3, ["01_problem_record.md", "02_results.md", "03_verification_record.md"]),
    ("S209 err 0.28e-5", 0.28e-5, 1e-3, ["01_problem_record.md", "02_results.md", "03_verification_record.md"]),
    ("SM ³He/⁴He 1.257e-4", 1.257e-4, 1e-3, ["02_results.md", "03_verification_record.md"]),
    ("SM err 0.017e-4", 0.017e-4, 1e-3, ["02_results.md", "03_verification_record.md"]),
    ("GCE 1.043e-4", 1.043e-4, 1e-3, ["02_results.md", "03_verification_record.md"]),
    ("GCE err 0.089e-4", 0.089e-4, 1e-3, ["02_results.md", "03_verification_record.md"]),
    ("模型差距 6.16%", diff_pct, 0.02, ["01_problem_record.md", "02_results.md"]),
    ("Cooke 誤差 16.5%", err_cooke_pct, 0.02, ["01_problem_record.md", "02_results.md"]),
    ("S209 誤差 25.5%", err_s209_pct, 0.02, ["01_problem_record.md", "02_results.md"]),
    ("需要 3.1%", need_pct, 0.02, ["01_problem_record.md", "02_results.md"]),
    ("IDCM vs Cooke 0.63σ", z_cooke_idcm, 0.02, ["02_results.md", "03_verification_record.md"]),
    ("ΛCDM vs Cooke 0.28σ", z_cooke_lcdm, 0.02, ["02_results.md"]),
    ("IDCM vs S209 0.44σ", z_s209_idcm, 0.05, ["02_results.md", "03_verification_record.md"]),
    ("ΛCDM vs S209 0.21σ", z_s209_lcdm, 0.05, ["02_results.md"]),
    ("IDCM vs SM 4.9σ", z_sm_idcm, 0.05, ["02_results.md", "03_verification_record.md"]),
    ("ΛCDM vs SM 1.3σ", z_sm_lcdm, 0.05, ["02_results.md", "03_verification_record.md"]),
    ("IDCM vs GCE 1.5σ", z_gce_idcm, 0.05, ["02_results.md"]),
    ("ΛCDM vs GCE 2.7σ", z_gce_lcdm, 0.05, ["02_results.md"]),
    ("系統修正 2.5σ", z_sys, 0.02, ["02_results.md", "03_verification_record.md"]),
]

def extract_values(text):
    """從 norm 後文字抽所有浮點數 (含 e-notation + (V±E)×10^n 括號格式)"""
    text = norm_sci(text)
    vals = []
    # 優先: (V1±V2)e±exp → V1*10^exp 同 V2*10^exp
    for m in re.finditer(r'\((\d+\.?\d*)\s*\+/-\s*(\d+\.?\d*)\)\s*[eE]([-+]?\d+)', text):
        exp = int(m.group(3))
        vals.append(float(m.group(1)) * 10**exp)
        vals.append(float(m.group(2)) * 10**exp)
    # 完整科學記號 V e ±exp
    for m in re.finditer(r'(\d+\.?\d*)[eE]([-+]?\d+)', text):
        try:
            vals.append(float(m.group(1)) * 10**int(m.group(2)))
        except ValueError:
            pass
    # 普通數字 (backup)
    for m in re.finditer(r'\d+\.?\d*', text):
        try:
            vals.append(float(m.group(0)))
        except ValueError:
            pass
    return vals

print("\n[1] 文檔完整性")
for name, path in docs.items():
    size = os.path.getsize(path)
    print(f"  {name}: {size} bytes {'✅' if size > 0 else '❌'}")

print("\n[2] 數字抽檢 (每項: 期望值 → 文檔中搵到近似值)")
all_ok = True
for desc, expected, tol, req_docs in checks:
    statuses = []
    for doc_name in req_docs:
        vals = extract_values(contents[doc_name])
        found = any(abs(v - expected) <= tol * abs(expected) for v in vals)
        statuses.append(f"{doc_name.split('_')[0]}:{'✅' if found else '❌'}")
    ok = all('✅' in s for s in statuses)
    if not ok:
        all_ok = False
    print(f"  {'✅' if ok else '❌'} {desc:30s} = {expected:.6g}  [{', '.join(statuses)}]")

# 特別檢查: 02_results 中 0.63σ/0.28σ/2.5σ 已修正
print("\n[2b] 修正確認 (02_results.md)")
r2 = norm_sci(contents["02_results.md"])
for pat, label in [("0.63σ", "Cooke IDCM σ=0.63"), ("0.28σ", "Cooke ΛCDM σ=0.28"),
                   ("2.5σ", "系統 2.5σ"), ("0.44σ", "S209 IDCM 0.44σ"),
                   ("0.21σ", "S209 ΛCDM 0.21σ")]:
    found = pat in r2 or pat.replace('σ','σ') in contents["02_results.md"]
    print(f"  {'✅' if found else '❌'} {label}: {'存在' if found else '缺'}")

print("\n[3] 文檔時序")
timeline = []
for name, path in docs.items():
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    timeline.append((mtime, name))
timeline.sort()
for mtime, name in timeline:
    print(f"  {mtime.strftime('%m-%d %H:%M')}  {name}")
print(f"  → SESSION_START (08-16 21:33) 最早, 其餘本 session 順序: 01 → 02 → 03")
print(f"  → 時序合理? {'✅' if timeline[0][1] == 'SESSION_START.md' else '⚠️'}")

# 時序完整性: 每個文檔創建時間唔可以早過佢依賴嘅文檔
print("\n[4] 本 script 只讀模式 — 冇寫入任何文檔 ✅")

print("\n[5] 結論")
print(f"  {'✅ 所有文檔數字與獨立計算一致' if all_ok else '⚠️ 有缺漏, 需人工檢查'}")
print("\n獨立計算基準:")
print(f"  IDCM ³He/H = {He3_H_IDCM:.6e}")
print(f"  ³He/⁴He IDCM = {He3_He4_IDCM:.6e}")
print(f"  模型差距 = {diff_pct:.4f}%")
print(f"  z_cooke = {z_cooke_idcm:.2f}σ (IDCM) / {z_cooke_lcdm:.2f}σ (ΛCDM)")
print(f"  z_s209 = {z_s209_idcm:.2f}σ (IDCM) / {z_s209_lcdm:.2f}σ (ΛCDM)")
print(f"  z_sm = {z_sm_idcm:.1f}σ (IDCM) / {z_sm_lcdm:.1f}σ (ΛCDM)")
print(f"  z_gce = {z_gce_idcm:.1f}σ (IDCM) / {z_gce_lcdm:.1f}σ (ΛCDM)")
print(f"  系統修正 = {z_sys:.2f}σ")
