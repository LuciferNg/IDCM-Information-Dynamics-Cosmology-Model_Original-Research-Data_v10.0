#!/usr/bin/env python3
"""
O208 scripts/02_three_source_consistency.py — 三源一致機制
============================================================
README / SESSION_START / 前置引用 三源狀態自動對齊工具。

三源定義 (O115 docs/02 §三 缺陷 3 + O208 docs/03):
  源 A = SESSION_START.md 嘅 `> **狀態**:` 行 (起點 snapshot, 之後唔改)
  源 B = master README.md 表格行 (living summary)
  源 C = 前置引用 (O 內 docs/scripts 引用其他 O 狀態, e.g. 「O56 🟢」)

機制:
  1. 讀 README 每行 O 狀態 → B
  2. 讀每目錄 SESSION_START 狀態 → A
  3. 掃描每目錄 docs/scripts 內「O<NNN> <emoji>」引用 → C
  4. 對比 A/B/C → 不一致清單 + 一致率報告
  5. 輸出三源一覽表 (data/03_three_source_report.json + 打印)

用法:
    /usr/bin/python3 scripts/02_three_source_consistency.py --root <open_problems_fresh>

注意:
  - A 係 snapshot (SESSION_START 之後唔改) — 唔一致係預期, 標記「snapshot 過時」
  - 真不一致 = B vs C 衝突 (README 話 🟢, 引用話 🔴)
"""
import os, re, sys, json, argparse, glob

STATUS_EMOJI = {'🟢', '🟡', '🔴', '✅', '🟠', '⚪'}
# 狀態分組: 🟢/✅ = 閉合完成, 🟡/🟠 = 部分/候選, 🔴 = 開放/未閉合
STATUS_GROUP = {'🟢': 'P', '✅': 'P', '🟡': 'S', '🟠': 'S', '🔴': 'N', '⚪': 'U'}
SKIP_DIRS = {'.git', '__pycache__', 'node_modules'}

def parse_status_line(text):
    """搵 SESSION_START 嘅狀態行. 返回 (status, raw) 或 None."""
    for line in text.splitlines():
        if '**狀態**' in line or '**狀態**:' in line:
            m = re.search(r'[🟢🟡🔴✅🟠⚪]', line)
            if m:
                return m.group(0), line.strip()
    return None, None

def read_README_statuses(root):
    """讀 README.md 表格: O編號 -> (status, full_cell)."""
    out = {}
    readme = os.path.join(root, 'README.md')
    if not os.path.exists(readme):
        return out
    with open(readme, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.search(r'\|\s*\*\*O(\d+)\*\*\s*\|', line)
            if m:
                num = int(m.group(1))
                em = re.findall(r'[🟢🟡🔴✅🟠⚪]', line)
                out[num] = (em[0] if em else '?', line.strip()[:150])
    return out

def scan_cross_refs(o_dir, o_num):
    """掃描 O 目錄內 docs/scripts 對其他 O 嘅狀態引用. 返回 [(target_num, status, file, line, is_script)].
    is_script=True 表示 scripts/*.py (當下層面, C 源); False = docs (歷史 snapshot, 豁免)."""
    refs = []
    pat = re.compile(r'O(\d{2,3})[^\d]')
    for sub in ('docs', 'scripts'):
        d = os.path.join(o_dir, sub)
        if not os.path.isdir(d):
            continue
        is_script = sub == 'scripts'
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if not (fn.endswith('.md') or fn.endswith('.py')):
                continue
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except Exception:
                continue
            for i, line in enumerate(lines[:2000], 1):  # 限制每檔案行數
                for m in pat.finditer(line):
                    tgt = int(m.group(1))
                    if tgt == o_num:
                        continue
                    em = re.findall(r'[🟢🟡🔴✅🟠⚪]', line)
                    if em and tgt >= 1:
                        refs.append((tgt, em[0], os.path.join(sub, fn), i, is_script))
    return refs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--json', default=None)
    args = ap.parse_args()
    root = args.root

    readme_st = read_README_statuses(root)

    # 每 O 目錄: SESSION_START 狀態 + 前置引用
    o_dirs = {}
    for d in sorted(os.listdir(root)):
        m = re.match(r'o(\d+)_', d)
        if not m or not os.path.isdir(os.path.join(root, d)):
            continue
        num = int(m.group(1))
        ss_path = os.path.join(root, d, 'SESSION_START.md')
        a_status = None
        if os.path.exists(ss_path):
            with open(ss_path, encoding='utf-8', errors='replace') as f:
                a_status, _ = parse_status_line(f.read())
        refs = scan_cross_refs(os.path.join(root, d), num)
        o_dirs[num] = {'dir': d, 'A_session_start': a_status, 'refs': refs}

    # 對比 + 報告
    inconsistencies = []
    summary_rows = []
    for num in sorted(o_dirs):
        info = o_dirs[num]
        a = info['A_session_start']
        b = readme_st.get(num, (None, None))[0]
        row = {'O': num, 'dir': info['dir'], 'A_SESSION_START': a, 'B_README': b}
        # A vs B: snapshot 過時係預期 (唔算真不一致, 但記錄)
        if a and b and a != b:
            row['A_vs_B'] = 'DIFF (snapshot 過時 — 正常, 以 B 為準)'
        elif a and not b:
            row['A_vs_B'] = 'README 缺行'
        # 前置引用 vs B (真不一致 = 跨組對立: P↔N 或 S↔N; 只計 scripts 當下引用, docs 係歷史 snapshot 豁免)
        c_conflicts = []
        c_hist = []
        for tgt, st, f, ln, is_script in info['refs']:
            b_tgt = readme_st.get(tgt, (None, None))[0]
            if not b_tgt:
                continue
            g_ref = STATUS_GROUP.get(st, 'U')
            g_b = STATUS_GROUP.get(b_tgt, 'U')
            # 真衝突 = 引用同 README 狀態組對立: P↔N 或 S↔N (S vs P 唔算 — 候選/閉合相容)
            if (g_ref, g_b) not in {('P', 'N'), ('N', 'P'), ('S', 'N'), ('N', 'S')}:
                continue
            item = {'target': tgt, 'ref_status': st, 'ref_group': g_ref,
                    'README_status': b_tgt, 'README_group': g_b, 'file': f, 'line': ln}
            if is_script:
                c_conflicts.append(item)
            else:
                c_hist.append(item)
        row['C_refs_count'] = len(info['refs'])
        if c_conflicts:
            row['C_conflicts'] = c_conflicts
            inconsistencies.append({'O': num, 'dir': info['dir'], 'conflicts': c_conflicts})
        summary_rows.append(row)

    # 一致率: 有 scripts 引用嘅 O 中, 0 個當下衝突嘅比例
    with_refs = [r for r in summary_rows if r['C_refs_count'] > 0]
    clean = [r for r in with_refs if 'C_conflicts' not in r]
    rate = (len(clean) / len(with_refs) * 100) if with_refs else 100.0
    n_hist = sum(len(r['refs']) - sum(1 for ref in r['refs'] if ref[4]) for r in o_dirs.values())

    print(f"Three-source consistency scan root: {root}")
    print(f"O directories: {len(o_dirs)}")
    print(f"README rows: {len(readme_st)}")
    print(f"O dirs with cross-refs: {len(with_refs)}")
    print(f"Cross-ref conflicts (C vs B, scripts 當下): {len(inconsistencies)}")
    print(f"Docs 歷史引用 (豁免, 回溯污染唔改): {n_hist}")
    print(f"Consistency rate (scripts 層): {rate:.1f}%")
    print()
    if inconsistencies:
        print("CONFLICTS:")
        for inc in inconsistencies[:30]:
            print(f"  O{inc['O']} ({inc['dir']}):")
            for c in inc['conflicts'][:5]:
                print(f"    -> O{c['target']} 引用 {c['ref_status']} 但 README {c['README_status']} ({c['file']}:{c['line']})")
        if len(inconsistencies) > 30:
            print(f"  ... +{len(inconsistencies)-30} more")
    else:
        print("No cross-ref conflicts — 前置引用與 README 一致 ✅")

    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'root': root, 'dirs': len(o_dirs), 'readme_rows': len(readme_st),
                       'with_refs': len(with_refs), 'conflicts': len(inconsistencies),
                       'rate': rate, 'rows': summary_rows,
                       'conflict_details': inconsistencies}, f, indent=2, ensure_ascii=False)
        print(f"\nJSON -> {args.json}")

if __name__ == '__main__':
    main()
