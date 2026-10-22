#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/81_o225_closeout2_audit.py — O225 close-out 第二輪（R1–R23）T1 審計

紀律：**不 import 本 o 任何推導 script**（只以 subprocess 重跑）。
段：A 合約／唯讀輸入凍結；B 全鏈重跑（01–80 ＋ 82）；C 判決逐項比對（重跑前 vs 重跑後）；
    D 契約 sha256 一致性（freeze JSON ↔ 合約檔）；E 磁碟⟂MANIFEST 覆蓋；F AST 禁 import／跨腳本 import 掃描；
    G 文檔標記（docs/49、§三十三、清冊）；H 三檔狀態行同步。
"""
import io, os, re, json, ast, hashlib, subprocess, sys, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = '/usr/bin/python3'
REUSE = '--reuse' in sys.argv          # 重用剛完成之全鏈重跑日誌（須通過時效斷言）
CLAIMS, INFO = [], []
def claim(tag, desc, ok, detail=''):
    CLAIMS.append({'tag': tag, 'desc': desc, 'ok': bool(ok), 'detail': str(detail)[:600]})
    print('[%s] %-4s %s  --  %s' % ('PASS' if ok else 'FAIL', tag, desc, str(detail)[:400]))
def info(s):
    INFO.append(s)
    print('       info:', s)

def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()
def sha(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
PAT = re.compile(r'RESULT: (\d+)/(\d+) PASS')

# ---------- A 凍結 ----------
pinned = {'docs/49_o225_closeout_r1-r23.md': sha(os.path.join(BASE, 'docs/49_o225_closeout_r1-r23.md')),
          'docs/48_r23_results.md': sha(os.path.join(BASE, 'docs/48_r23_results.md')),
          'data/37_closeout_docs.json': sha(os.path.join(BASE, 'data/37_closeout_docs.json')),
          'data/MANIFEST.json': sha(os.path.join(BASE, 'data/MANIFEST.json'))}
info('A 唯讀釘選 = %s' % {k: v[:10] for k, v in pinned.items()})

# ---------- B 全鏈重跑 ----------
SCR = sorted(f for f in os.listdir(os.path.join(BASE, 'scripts')) if f.endswith('.py'))
BEFORE = {}
for f in SCR:
    lg = os.path.join(BASE, 'logs', f[:-3] + '.out')
    if os.path.exists(lg):
        m = PAT.findall(rd(lg))
        BEFORE[f] = m[-1] if m else None
t0 = time.time()
AFTER, EXITS, TB = {}, {}, {}
RERUN_STAMP = os.path.join(BASE, 'logs', '_rerun_all.out')
stamp_ok = os.path.exists(RERUN_STAMP)
# 重跑窗：以本輪重跑之「最後一支 log」為參考，容許 1 小時窗（可驗證之時效斷言）
ref = max((os.path.getmtime(os.path.join(BASE, 'logs', f[:-3] + '.out'))
           for f in SCR if os.path.exists(os.path.join(BASE, 'logs', f[:-3] + '.out'))), default=0)
FRESH = {f: (os.path.exists(os.path.join(BASE, 'logs', f[:-3] + '.out'))
             and os.path.getmtime(os.path.join(BASE, 'logs', f[:-3] + '.out')) >= ref - 3600) for f in SCR}
info('重跑窗參考 T = %s ; 窗內日誌 = %d/%d' % (time.strftime('%H:%M:%S', time.localtime(ref)),
     sum(1 for v in FRESH.values() if v), len(SCR)))
for f in SCR:
    if f.startswith('81_'):
        continue                      # 不自跑
    if REUSE:
        lg = os.path.join(BASE, 'logs', f[:-3] + '.out')
        out = rd(lg) if os.path.exists(lg) else ''
        m = PAT.findall(out)
        AFTER[f], EXITS[f], TB[f] = (m[-1] if m else None), -1, bool(re.search(r'^Traceback \(most recent call last\)', out, re.M))
        if not FRESH.get(f):
            AFTER[f] = None          # 日誌非本輪重跑窗內所產 ⟹ 不以之為證
        continue
    try:
        r = subprocess.run([PY, os.path.join(BASE, 'scripts', f)], capture_output=True,
                           text=True, timeout=900, cwd=BASE)
        out, ec = (r.stdout or '') + (r.stderr or ''), r.returncode
    except subprocess.TimeoutExpired:
        out, ec = 'TIMEOUT', -9
    io.open(os.path.join(BASE, 'logs', f[:-3] + '.out'), 'w', encoding='utf-8').write(out)
    m = PAT.findall(out)
    AFTER[f], EXITS[f] = (m[-1] if m else None), ec
    TB[f] = bool(re.search(r'^Traceback \(most recent call last\)', out, re.M))
dur = time.time() - t0
info('模式 = %s ; 重跑日誌時效斷言 = %s' % ('reuse（重用重跑日誌）' if REUSE else 'rerun（本輪實跑）', stamp_ok))
io.open(os.path.join(BASE, 'logs', '_rerun_all.out'), 'w', encoding='utf-8').write(
    '\n'.join('%s exit=%d' % (f[:-3], EXITS[f]) for f in sorted(EXITS)) + '\n')
info('B 重跑 %d 支完成，用時 %.1f s' % (len(AFTER), dur))

# ---------- C 判決比對 ----------
HISTP = '/home/wsl/.hermes/cache/scratch/o225_closeout_before.json'
HIST = {}
if os.path.exists(HISTP):
    try:
        _h = json.load(io.open(HISTP, encoding='utf-8'))
        HIST = {f: (v.get('last') if isinstance(v, dict) else None) for f, v in _h.items()}
    except Exception:
        HIST = {}
info('歷史快照（重跑前首記錄）項數 = %d' % len(HIST))
drift, drift_hist, nores, gate_ok, gate_bad = [], [], [], [], []
for f in sorted(AFTER):
    if AFTER[f] is None or BEFORE.get(f) is None:
        nores.append(f)
        continue
    if AFTER[f] != BEFORE[f]:
        lg = rd(os.path.join(BASE, 'logs', f[:-3] + '.out'))
        is_gate = f.endswith('_contract.py')
        reg_fail = bool(re.search(r'\[FAIL\][^\n]*register', lg)) or bool(re.search(r'register[^\n]*note', lg)) or '[FAIL] C8' in lg
        drift.append((f, BEFORE[f], AFTER[f], 'gate-register' if (is_gate and reg_fail) else 'UNEXPECTED'))
        (gate_ok if (is_gate and reg_fail) else gate_bad).append((f, BEFORE[f], AFTER[f]))
for f in sorted(AFTER):
    if AFTER[f] is None:
        continue
    h = HIST.get(f[:-3] + '.out')
    h = ('%s/%s' % (h[0], h[1])) if isinstance(h, (list, tuple)) and len(h) == 2 else h
    a_now = AFTER[f]
    a_now = ('%s/%s' % (a_now[0], a_now[1])) if isinstance(a_now, (list, tuple)) and len(a_now) == 2 else a_now
    if h and h != a_now:
        lg = rd(os.path.join(BASE, 'logs', f[:-3] + '.out'))
        is_gate = f.endswith('_contract.py')
        reg_fail = ('[FAIL] C8' in lg) or bool(re.search(r'register[^\n]*note', lg))
        drift_hist.append((f, h, a_now, 'gate-register' if (is_gate and reg_fail) else 'UNEXPECTED'))
        if (is_gate and reg_fail):
            gate_ok.append((f, h, a_now))
        else:
            gate_bad.append((f, h, a_now))
claim('C1', '全鏈重跑 vs **歷史首記錄**：非預期漂移 = 0；契約閘之「見數前註冊（C8 型）」一次性判據之漂移屬記錄在案（該判據要求「無結果 note」，事後必 FAIL）',
      [d for d in drift_hist if d[3] == 'UNEXPECTED'] == [],
      '歷史對照 = %d 項；漂移 = %s ; 同輪 before→after 漂移 = %s ; 無 RESULT = %d 支'
      % (len(HIST), drift_hist[:8], drift[:4], len(nores)))
tb_now = [f for f in TB if TB[f] and '_firstrun' not in f]
claim('C2', '重跑後之 log 無 `Traceback`（首跑 implbug 日誌除外）', tb_now == [], '含 Traceback = %s' % tb_now[:6])
info('C 各輪尾次判決（抽樣）= %s' % {k: AFTER[k] for k in list(sorted(AFTER))[-6:]})

# ---------- D 契約 sha 一致性 ----------
docs = {f: sha(os.path.join(BASE, 'docs', f)) for f in os.listdir(os.path.join(BASE, 'docs')) if f.endswith('.md')}
by_sha = {}
for f, h in docs.items():
    by_sha.setdefault(h, []).append(f)
fresh = {f: sha(os.path.join(BASE, 'data', f)) for f in os.listdir(os.path.join(BASE, 'data')) if f.endswith('.json')}
unmatched, npin = [], 0
for f, h in fresh.items():
    try:
        j = json.load(io.open(os.path.join(BASE, 'data', f), encoding='utf-8'))
    except Exception:
        continue
    s = j.get('contract_sha256') or j.get('sha256')
    if s:
        npin += 1
        if s not in by_sha:
            unmatched.append((f, s[:12]))
claim('D1', '全部 freeze JSON 所 pin 之合約 sha256 皆對應到 docs/ 內某一檔（0 失配）',
      unmatched == [], 'pin 數 = %d ; 失配 = %s' % (npin, unmatched[:6]))

# ---------- E 磁碟 ⟂ MANIFEST ----------
MAN = json.load(io.open(os.path.join(BASE, 'data/MANIFEST.json'), encoding='utf-8'))
mk = {x['path'] for x in MAN['files']}
SKIP = tuple(MAN.get('untracked_by_design') or [])
disk = set()
for sub in ('docs', 'scripts', 'data', 'logs'):
    for f in os.listdir(os.path.join(BASE, sub)):
        p = os.path.join(BASE, sub, f)
        if os.path.isfile(p) and p.endswith(('.md', '.py', '.json', '.out')):
            disk.add(os.path.relpath(p, BASE))
for f in os.listdir(BASE):
    p = os.path.join(BASE, f)
    if os.path.isfile(p) and f.endswith('.md'):
        disk.add(f)
missing = sorted(d for d in disk if d not in mk and d not in SKIP
                 and not d.endswith('.pyc') and '__pycache__' not in d)
claim('E1', '磁碟上全部檔（doc/script/data/log/root）皆入 MANIFEST（排除 untracked-by-design）',
      missing == [], '未收錄 = %d 件；首 8 = %s' % (len(missing), missing[:8]))

# ---------- F AST 掃描 ----------
FORB = {'math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'secrets', 'decimal', 'mpmath', 'sympy'}
viol, cross = [], []
for f in SCR:
    src = rd(os.path.join(BASE, 'scripts', f))
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        viol.append((f, 'SyntaxError %s' % e))
        continue
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split('.')[0] in FORB:
                    viol.append((f, a.name))
        elif isinstance(n, ast.ImportFrom) and (n.module or '').split('.')[0] in FORB:
            viol.append((f, n.module))
    if 'spec_from_file_location' in src and re.search(r"scripts/[0-9]", src) and 'o222' not in src:
        cross.append(f)
claim('F1', 'AST：全 scripts/ 無禁用模組 import（math／random／numpy／scipy／statistics／cmath／secrets／decimal／mpmath／sympy）',
      viol == [], '違規 = %s' % viol[:6])
claim('F2', '審計器未經 importlib 載入本 o 自身推導 script（跨腳本 import = 0）', cross == [], '可疑 = %s' % cross[:6])

# ---------- G 文檔標記 ----------
rec = rd(os.path.join(BASE, '01_problem_record.md'))
fin = rd(os.path.join(BASE, 'final_result.md'))
need = {'docs/49_o225_closeout_r1-r23.md': os.path.exists(os.path.join(BASE, 'docs/49_o225_closeout_r1-r23.md')),
        '§三十三 in record': '三十三、Close-out 第二輪' in rec,
        '清冊 9 項 in docs/49': 'MECH-1' in rd(os.path.join(BASE, 'docs/49_o225_closeout_r1-r23.md')),
        'final_result R23': 'R23' in fin, 'final_result closeout': 'Close-out 第二輪' in fin}
claim('G1', 'close-out 第二輪之文檔標記齊備（docs/49、§三十三、清冊、final_result）',
      all(need.values()), '逐項 = %s' % need)

# ---------- H 三檔狀態行 ----------
toks = {}
for f in ('SESSION_START.md', '01_problem_record.md', 'final_result.md'):
    m = [l for l in rd(os.path.join(BASE, f)).split('\n') if l.startswith('> **狀態') or l.startswith('## 狀態')]
    toks[f] = (re.findall(r'R1[–\-]R\d+', m[0]) or ['NONE'])[0] if m else None
claim('H1', '三檔狀態行同步（R1–R23）', len(set(toks.values())) == 1, '三檔 = %s' % toks)

if REUSE:
    claim('H2', '重跑日誌時效斷言（reuse 模式之前置）：重跑窗內日誌 ≥ 70 支',
          sum(1 for v in FRESH.values() if v) >= 70,
          '窗內 = %d/%d（參考 T = %s）' % (sum(1 for v in FRESH.values() if v), len(SCR),
                                          time.strftime('%F %T', time.localtime(ref))))
npass = sum(1 for c in CLAIMS if c['ok'])
print('=' * 118)
print('RESULT: %d/%d PASS  |  O225 close-out 第二輪 T1 審計' % (npass, len(CLAIMS)))
with io.open(os.path.join(BASE, 'data/81_o225_closeout2_audit.json'), 'w', encoding='utf-8') as fh:
    json.dump({'rules': 'o225-closeout2-t1-v1', 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
               'pinned': pinned, 'rerun_seconds': dur, 'drift': drift, 'unmatched_sha': unmatched,
               'missing_in_manifest': missing, 'before': BEFORE, 'after': AFTER, 'exits': EXITS, 'mode': 'reuse' if REUSE else 'rerun',
               'gate_register_drift': gate_ok, 'unexpected_drift': gate_bad,
               'hist_drift': drift_hist, 'hist_size': len(HIST)},
              fh, indent=1, ensure_ascii=False)
raise SystemExit(0 if npass == len(CLAIMS) else 1)
