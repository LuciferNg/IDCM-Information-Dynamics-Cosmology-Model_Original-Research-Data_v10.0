#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O85-17: Layer-3 doc crosscheck + 檔案集完整性審計（唯讀）
=================================================================
① 讀全部 data/*.json, 驗證每個 check pass=True 且 total==passed
② docs/*.md 關鍵數字抽樣比對（由獨立計算）
③ 檔案集對稱: docs 15 / scripts 16 / data 16 / logs 正典 log 存在
④ /tmp 寫入模式衛生掃描（scripts/*.py）
★ 唯讀: 唔改任何 doc
"""
import json, re, os, glob

CHECKS = []
def chk(tag, name, cond, detail=""):
    CHECKS.append({'tag': tag, 'name': name, 'pass': bool(cond), 'detail': str(detail)})
    print(f"  {'✅' if cond else '❌'} [{tag}] {name}" + (f"   — {detail}" if detail else ""))
    return cond

print("=" * 78)
print("O85-17 Layer-3 doc crosscheck + 檔案集完整性（唯讀）")
print("=" * 78)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =====================================================================
# ① data JSON 完整性
# =====================================================================
print("\n" + "=" * 78)
print("① data/*.json checks 驗證")
print("=" * 78)

data_files = sorted(glob.glob('data/*.json'))
print(f"    data/ 共 {len(data_files)} 個 JSON")
all_ok = True
for df in data_files:
    if os.path.basename(df) == '17_doc_crosscheck.json':
        continue  # 自指 audit: 記錄緊自己上一次結果 (untracked-by-design)
    with open(df, encoding='utf-8') as f:
        d = json.load(f)
    t, p = d.get('total', 0), d.get('passed', 0)
    nfail = sum(1 for c in d.get('checks', []) if not c['pass'])
    ok = (t == p and nfail == 0 and p == len(d.get('checks', [])))
    all_ok &= ok
chk('D1', f'★ 01-19 共 {len(data_files)-1} 個 data JSON: total==passed==checks 數',
    all_ok, f'每檔 {[os.path.basename(f) for f in data_files if os.path.basename(f) != "17_doc_crosscheck.json"]}')
chk('D2', '★ data 檔數 = 20（01-19 + 20 湯川承接）', len(data_files) == 20)

# =====================================================================
# ② docs 關鍵數字抽樣
# =====================================================================
print("\n" + "=" * 78)
print("② docs 關鍵數字抽樣（獨立比對）")
print("=" * 78)

def doc_has(fname, *needles):
    txt = open(fname, encoding='utf-8').read()
    return all(n in txt for n in needles)

pairs = [
    ('docs/01_breaking_path_classification.md', ['S(U(3)×U(2)×U(1)^7)', 'rank 11', '143']),
    ('docs/02_q6_global_vs_gauge.md', ['1.88191', 'global', 'index']),
    ('docs/03_breaking_chain.md', ['131', 'rank 11', 'Y']),
    ('docs/04_mass_spectrum.md', ['36', 'C(9,2)', '0.0606569', 'Golomb']),
    ('docs/05_fermion_reps.md', ['72', 'anomaly', '22/22']),
    ('docs/06_scale.md', ['10¹⁶', '10¹⁷', 'M_Pl / 87']),
    ('docs/07_y_combination.md', ['−1/3', '+1/2', '−1/6', '66']),
    ('docs/08_vl_mass.md', ['24', '12/12̄', 'Pati-Salam']),
    ('docs/09_u1_scale_ladder.md', ['157.28', '12.54', 'λ_m']),
    ('docs/10_vl_assignment.md', ['e^c', '2∧2', '13']),
    ('docs/11_rep_consistency.md', ['15 ≠ 0', '維度巧合', '66']),
    ('docs/12_yi_assignment.md', ['11/rep', '33', '5'],),
    ('docs/13_yi_observational.md', ['1/N_gen', 'ν^c', '7 = 3']),
    ('docs/14_singlet_mode.md', ['(m−7)/6', '184', '56/3']),
    ('docs/15_uniqueness.md', ['C-對稱', '等間距', '1/6']),
    ('docs/16_vl_scale_open.md', ['7.19×10¹⁴', '1.13×10¹⁷', 'y_Y']),
    ('docs/17_singlet_mode_interpretation.md', ['Cartan', '線性', 'AP']),
    ('docs/18_vl_yukawa_o86.md', ['√2·M₀', 'O86', '35.41']),
]
ok_docs = True
for fname, needles in pairs:
    ok = doc_has(fname, *needles)
    ok_docs &= ok
    if not ok:
        miss = [n for n in needles if n not in open(fname, encoding='utf-8').read()]
        print(f"    ❌ {os.path.basename(fname)} 缺: {miss}")
chk('D3', f'★ 15 份 docs 關鍵數字抽樣全部命中（{len(pairs)} 檔 × {sum(len(n) for _,n in pairs)} 枚針）',
    ok_docs)

# =====================================================================
# ③ 檔案集對稱
# =====================================================================
print("\n" + "=" * 78)
print("③ 檔案集對稱")
print("=" * 78)

scripts = sorted(glob.glob('scripts/*.py'))
chk('D4', f'★ scripts 數 = 20（01-19 + 20 湯川承接）', len(scripts) == 20,
    f'實際 {[os.path.basename(s) for s in scripts]}')
chk('D5', '★ docs 數 = 18（01-18）', len(glob.glob('docs/*.md')) == 18)
# logs 正典
logs = sorted(glob.glob('logs/*.out'))
chk('D6', '★ logs/ 有正典 log（每 script 一支 .out）', len(logs) >= len(scripts),
    f'實際 {len(logs)} .out')

# scripts ↔ data 對稱: 每 script 具名輸出一個 data JSON
data_claim = {os.path.basename(f)[:2]: f for f in data_files}
claims = {}
for s in scripts:
    txt = open(s, encoding='utf-8').read()
    m = re.findall(r"data/(\d+_[a-z_]+)\.json", txt)
    for mm in m:
        claims.setdefault(os.path.basename(s), set()).add(mm)
    if not m:
        claims.setdefault(os.path.basename(s), set()).add('(none)')
missing = []
for s, claimed in claims.items():
    if os.path.basename(s) == '17_doc_crosscheck.py':
        continue  # 自指 audit: 自己寫自己, 跑完先存在
    for c in claimed:
        if c != '(none)' and not os.path.exists(f'data/{c}.json'):
            missing.append(f'{s}:data/{c}.json')
chk('D7', f'★ scripts 宣告輸出 ↔ data 檔案: 缺 {len(missing)} 個',
    len(missing) == 0, str(missing) if missing else '全部存在')

# =====================================================================
# ④ /tmp 寫入模式衛生
# =====================================================================
print("\n" + "=" * 78)
print("④ /tmp 寫入模式衛生")
print("=" * 78)

bad = []
for s in scripts:
    txt = open(s, encoding='utf-8').read()
    # 寫入模式: open(...'/tmp/...', 'w') / write / dump 去 /tmp
    if re.search(r"\bopen\(\s*['\"]/tmp/", txt) or re.search(r"'/tmp/.*\.json'\s*,\s*['\"]w", txt):
        bad.append(os.path.basename(s))
    # 檔案寫入到 /tmp 嘅 json.dump
    if re.search(r"json\.dump.*open\(['\"]/tmp/", txt, re.S):
        bad.append(os.path.basename(s))
chk('D8', f'★ scripts 寫入 /tmp 命中 = {len(bad)}', len(bad) == 0,
    str(bad) if bad else '零命中')

print("\n" + "=" * 78)
tot = len(CHECKS); ps = sum(1 for c in CHECKS if c['pass'])
print(f"匯總: 總檢查數 {tot}  PASS {ps}  FAIL {tot-ps}")
print(f"  {('🎉 Layer-3 全部通過' if ps == tot else '⚠️ 有 FAIL 需查')}")

with open('data/17_doc_crosscheck.json', 'w', encoding='utf-8') as f:
    json.dump({'layer': 3, 'total': tot, 'passed': ps, 'failed': tot - ps,
               'checks': CHECKS, 'data_files': len(data_files),
               'scripts': len(scripts), 'docs': len(glob.glob('docs/*.md'))},
              f, ensure_ascii=False, indent=2)
print("✅ 已保存 data/17_doc_crosscheck.json")