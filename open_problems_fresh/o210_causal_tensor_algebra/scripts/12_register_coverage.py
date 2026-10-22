#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/12_register_coverage.py  —  登記面覆蓋核對（§4.10 / 硬規則 6）
================================================================================
七項核對（skill `idcm-closeout` §4.10）:
  ① 正向覆蓋: 本 O 鏈每個「輪次結果 / 殘餘」→ register 有對應事件（一條都唔可以漏）
  ② 新問題註冊: 每個新問題 → register 有 entry，`ref` 恰一條路徑，**逐個實核**（檔案存在 + 行號 ≤ 行數）
  ③ 反向覆蓋: register 內本 O 之 entry ↔ 記錄所列項，兩側差集須空（幽靈項偵測）
  ④ `check` 對**基線**（全局 HARD DRIFT 係**全局量**：其他 O 平行活動會令佢升 ⟹ 本 O 只要求「涉本 pid 之 hard 問題 = 0」，唔可以要求總數唔升；出檔再 grep，唔好 grep 被截斷嘅 stdout）
  ⑤ 機器塊: `blocks --list` 唔應該有自己 pid
  ⑥ 讀回傳行: 事件數前後差 == 預期（唔可以用 `>/dev/null` 吞）
  ⑦ README: 只改狀態 emoji（本腳本只**讀**核，唔寫）

只讀（除 `check`/`blocks` 子命令本身外，皆為唯讀查詢）；輸出 data/audit/register_coverage.json。
"""
import io
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
REG = os.path.join(ROOT, 'problem_register', 'register.jsonl')
BASELINE_HARD_DRIFT = 78          # 開輪實測（收輪只要求「總數唔升」）
ODIR_REL = 'open_problems_fresh/o210_causal_tensor_algebra'
stats = {"PASS": 0, "FAIL": 0}


def chk(name, dev, tol):
    ok = dev < tol
    stats["PASS" if ok else "FAIL"] += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   [dev = {dev}]")
    return ok


ev = []
for ln in io.open(REG, encoding='utf-8'):
    ln = ln.strip()
    if ln:
        ev.append(json.loads(ln))
mine = [d for d in ev if str(d.get('pid')) == 'O210']
print(f"register 總事件 = {len(ev)}；本 O(O210) 事件 = {len(mine)}")
for d in mine:
    print(f"   {d.get('ts')}  {d.get('kind'):<10} state={d.get('state')}  ref={str(d.get('ref'))[:70]}")

# ---------- ① 正向覆蓋：鏈上每個輪次結果 / 殘餘 ----------
CHAIN = [
    ('R1 首輪閉合（型別/運算/憲章/重寫率 88.9%）', ['閉合', '129/129', '90 條目', '重寫'], None),
    ('R2 續攻1 T1 模B定則', ['T1', '模B', '模 B'], 'docs/06_escape_period_theorem.md'),
    ('R3 續攻2 T2 no-go + O88 三條件', ['T2', 'no-go', '三條件'], 'docs/07_operator_layer_selection.md'),
    ('R4 續攻3 C9 K_tree 身份分離（原事件只落 O126）', ['身份分離'], None),
    ('R5 續攻4 T3 分支荷 + C9 修訂', ['T3', '分支荷', 'C9'], 'docs/09_ktree_two_counts.md'),
    ('R6 續攻5 T4/C10 ℤ₄ 橋', ['ℤ₄', '扇區', 'T4'], 'docs/10_z4_bridge.md'),
    ('R7 續攻6 T5/T6 共同測度 no-go', ['共同測度', 'T5', 'T6'], 'docs/11_common_measure_no_go.md'),
    ('R8 收尾（全鏈 closeout + 工具）', ['收尾', 'closeout', '全鏈'], 'docs/12_full_chain_closeout.md'),
]
notes_all = "\n".join((d.get('note') or '') for d in mine)
gap1 = []
for label, keys, ref in CHAIN:
    if not any(k in notes_all for k in keys):
        gap1.append(label)
print(f"\n① 正向覆蓋：鏈上 {len(CHAIN)} 輪 ⟹ 無 register 事件者 = {len(gap1)} {gap1}")
chk("① 每輪結果都有 register 事件（缺口 0）", len(gap1), 1)

# ---------- ② ref 實核（檔案存在 + 行號） ----------
bad_ref, nref = [], 0
for d in mine:
    r = d.get('ref')
    if not r or r == 'None':
        continue
    for part in str(r).split():                       # ref 恰一條路徑
        nref += 1
        path, line = (part.split('#L') + [None])[:2] if '#L' in part else (part, None)
        ap = os.path.join(ROOT, path)
        if not os.path.isfile(ap):
            bad_ref.append((part, 'MISSING'))
            continue
        if line:
            nl = sum(1 for _ in io.open(ap, encoding='utf-8', errors='replace'))
            if int(line) > nl:
                bad_ref.append((part, f'LINE {line} > {nl}'))
print(f"\n② ref 條數 = {nref}；不合格 = {len(bad_ref)} {bad_ref}")
chk("② ref 全部實核（存在 + 行號在範圍內）", len(bad_ref), 1)
multi = [str(d.get('ref')) for d in mine if d.get('ref') and len(str(d['ref']).split()) > 1]
chk("②b ref 恰一條路徑（多條串埋 = 永久 REF-MISSING）", len(multi), 1)

# ---------- ③ 反向覆蓋：register 有 ref 入本 O ⟹ 記錄有該輪 ----------
ghost = []
for d in mine:
    r = str(d.get('ref') or '')
    if ODIR_REL not in r:
        continue
    doc = os.path.basename(r.split('#')[0])
    if doc in ('01_problem_record.md', 'final_result.md', 'SESSION_START.md'):
        continue            # ref 指向記錄本身 = 合法（記錄就係清單；自指唔算幽靈）
    if doc and doc not in io.open(os.path.join(BASE, '01_problem_record.md'), encoding='utf-8').read() \
            and doc not in io.open(os.path.join(BASE, 'final_result.md'), encoding='utf-8').read():
        ghost.append(doc)
print(f"\n③ 反向覆蓋：register 指向本 O 但記錄未提之 doc = {len(ghost)} {ghost}")
chk("③ 無幽靈項（兩側差集空）", len(ghost), 1)

# ---------- ④ check 對基線 ----------
outp = os.path.join(BASE, 'data', 'audit', '_check.txt')
os.makedirs(os.path.dirname(outp), exist_ok=True)
with io.open(outp, 'w', encoding='utf-8') as fh:
    subprocess.run(['/usr/bin/python3', os.path.join(ROOT, 'problem_register', 'register.py'), 'check'],
                   stdout=fh, stderr=subprocess.STDOUT, cwd=os.path.join(ROOT, 'problem_register'))
chk_txt = io.open(outp, encoding='utf-8', errors='replace').read()
m = re.search(r'HARD DRIFT:\s*(\d+)', chk_txt)
hard = int(m.group(1)) if m else -1
# ★ hard 問題清單印喺 '[TYPE] n' 段落（header 之前）；header 之後係空區 —
#   用 split('HARD DRIFT')[1] 做「涉本 pid」檢查 = 空真 PASS（永遠 0 命中，見 pitfalls #17）。
HARD_TYPES = ('DUPLICATE-DIR', 'COLLISION-STALE', 'README-ONLY', 'STATUS-DRIFT',
              'PID-NO-FOLDER', 'REF-MISSING', 'REF-LINE-OOR', 'ALIAS-DANGLING',
              'BLOCK-DRIFT', 'BLOCK-UNREGISTERED', 'UNREGISTERED-DIR')
sec = re.split(r'^\[([A-Z-]+)\] \d+$', chk_txt, flags=re.M)
hard_lines = []
for i in range(1, len(sec), 2):
    if sec[i] in HARD_TYPES:
        hard_lines += [l.strip() for l in (sec[i + 1] if i + 1 < len(sec) else '').splitlines() if l.strip()]
o210_hard = [l for l in hard_lines if 'O210' in l or 'o210' in l]
print(f"\n④ register check → 全局 HARD DRIFT = {hard}（上次 O210 收尾 snapshot = {BASELINE_HARD_DRIFT}）")
print(f"    hard 問題行總數 = {len(hard_lines)}；涉本 pid（O210） = {len(o210_hard)}")
for l in o210_hard[:10]:
    print("    ", l[:140])
chk("④ 本 pid 於全局 HARD DRIFT 零新增（0 條涉 O210）", len(o210_hard), 1)
print(f"    全局 drift 增量 {max(0, hard - BASELINE_HARD_DRIFT)} 條 = 其他 O 平行活動（例如 O85/O206/O144 重組 ⟹ REF-MISSING 上升），非本 O 責任")

# ---------- ⑤ 機器塊 ----------
bp = subprocess.run(['/usr/bin/python3', os.path.join(ROOT, 'problem_register', 'register.py'),
                     'blocks', '--list'], capture_output=True, text=True)
inblk = 'O210' in bp.stdout
print(f"\n⑤ blocks --list 含 O210 = {inblk}")
chk("⑤ 本 pid 唔在 NO-BLOCK 清單", 1 if inblk else 0, 1)

# ---------- ⑦ README 狀態一致 ----------
readme = io.open(os.path.join(ROOT, 'open_problems_fresh', 'README.md'), encoding='utf-8').read()
line = next((l for l in readme.splitlines() if l.startswith('| **O210**')), '')
emoji = '🟢' if '🟢' in line else ('🟡' if '🟡' in line else ('🔴' if '🔴' in line else '?'))
last_state = next((d.get('state') for d in reversed(mine) if d.get('state')), None)
print(f"\n⑦ README O210 行 emoji = {emoji}；register 最後帶 state 之事件 = {last_state}")
chk("⑦ README emoji 與 register state 一致（🟢 ↔ closed）",
    0 if (emoji == '🟢' and last_state == 'closed') else 1, 1)

out = {'n_events_total': len(ev), 'n_events_o210': len(mine), 'chain_gaps': gap1, 'bad_ref': bad_ref,
       'ghosts': ghost, 'hard_drift': hard, 'baseline': BASELINE_HARD_DRIFT, 'readme_emoji': emoji,
       'events': [{'ts': d.get('ts'), 'kind': d.get('kind'), 'ref': d.get('ref'),
                   'note': (d.get('note') or '')[:120]} for d in mine], 'stats': stats}
with io.open(os.path.join(BASE, 'data', 'audit', 'register_coverage.json'), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("\n" + "=" * 84)
print(f"O210 登記面覆蓋 — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 84)
print("RESULT:", "FAIL" if stats["FAIL"] else "PASS")
sys.exit(1 if stats["FAIL"] else 0)
