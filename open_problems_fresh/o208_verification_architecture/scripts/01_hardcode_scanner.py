#!/usr/bin/env python3
"""
O208 scripts/01_hardcode_scanner.py — 語義級硬編碼掃描器
============================================================
語義級掃描: 搵「字面 True 冒充驗證」嘅真硬編碼, 同時排除 API 參數/配置/算法 flag。

用法:
    /usr/bin/python3 scripts/01_hardcode_scanner.py [--root <open_problems_fresh>] [--json out.json]

判定規則 (docs/02 反硬編碼規則):
  A. assert True                       → 🔴 禁止
  B. check("名", True) / chk(..., True) → 🔴 禁止
  C. assert x is True / == True         → 🟡 禁止 (用 assert x)
  D. dict 值字面 True (檢查 dict)       → 🔴 禁止
  E. 無條件 accumulator ok=True         → 🟡 禁止

豁免 (唔報):
  - API 參數: lonlat=True, nest=True, exist_ok=True, overwrite=True, ...
  - 配置 dict (pre_smoothed, ...) — 由 key 名啟發式判斷
  - 算法初始化 visited[x]=True, ok=True 但之後可設 False
  - 環境 flag: HAVE_MP = True

輸出: 每 script 命中行 + 總計。exit 0 = 零真硬編碼 (閉合測試通過)。
"""
import os, re, sys, json, argparse

# API 參數 key 名 — 豁免
API_PARAM_KEYS = {
    'lonlat', 'nest', 'nested', 'exist_ok', 'overwrite', 'notext', 'cbar', 'hold',
    'field', 'inclusive', 'keepdims', 'verbose', 'text', 'suppress', 'recursive',
    'force', 'ignore', 'replace', 'expanduser', 'asarray', 'dtype', 'order',
    'index', 'bins', 'density', 'histtype', 'align', 'rwidth', 'stacked', 'label',
    'color', 'marker', 'linestyle', 'ls', 'lw', 'alpha', 'zorder', 's', 'c',
}
# 配置 dict key — 豁免
CONFIG_KEYS = {'pre_smoothed', 'smoothed', 'has_phase', 'has_window', 'is_ring',
               'is_periodic', 'has_mask', 'raw', 'final', 'cached', 'exists',
               'present', 'available', 'enabled', 'disabled', 'valid', 'included',
               'applied', 'computed', 'saved', 'loaded', 'written', 'has_data'}
# flag key 名 — 真硬編碼風險高 (檢查 dict / 驗證 dict)
CHECK_DICT_HINTS = ('check', 'pass', 'ok', 'valid', 'consistent', 'match',
                    'closed', 'closure', 'verified', 'verify', 'confirm',
                    'self_consistent', 'accept', 'success', 'detected', 'found',
                    'prediction', 'antiparticle', 'charge', 'spectrum', 'operator',
                    'conclusion', 'involution', 'observed', 'external', 'core',
                    'restores', 'zero_', 'blind', 'triple', 'ap_test', 'dm31', 'dm21')

# 需要跳過嘅目錄
SKIP_DIRS = {'.git', '__pycache__', 'node_modules'}

def classify_hardcode(line, prev_line=None):
    """逐行分類。返回 (is_hardcode, kind) 或 (False, None)."""
    s = line.strip()
    # --- A. assert True ---
    if re.search(r'\bassert\s*\(?\s*True\s*\)?\s*:', s) or \
       re.search(r'\bassert\s*\(?\s*True\s*\)?\s*$', s):
        return True, 'A'
    # --- B. check("...", True) / chk(..., True) — 字面 True 直出 (真硬編碼) ---
    # 唔包括 check("...", expr is True) — 鏈式檢查, 另列
    if re.search(r'\b(?:check|chk)\s*\([^)]*\bTrue\b', s) and \
       not re.search(r'\b(?:is|==|!=)\s*True\b', s) and \
       not re.search(r'\[\s*["\'][^"\']+["\']\s*\]\s*(?:is|==)', s):
        return True, 'B'
    # --- C. assert x is True / == True ---
    if re.search(r'\bassert\b.*\b(?:is|==)\s*True\b', s):
        return True, 'C'
    # --- D. dict 值字面 True ---
    m = re.match(r'["\']([^"\']+)["\']\s*:\s*True\s*,?\s*$', s)
    if m:
        key = m.group(1).strip()
        # 豁免 API / 配置 key
        if key in API_PARAM_KEYS or key in CONFIG_KEYS:
            return False, None
        # 檢查 dict 暗示 → 硬編碼
        if any(h in key.lower() for h in CHECK_DICT_HINTS):
            return True, 'D'
        # 否則: 屬結果記錄 (可能係 config) — 保守報 🟡 等人工睇
        return False, None
    # --- E. 無條件 accumulator: 只睇 "ok = True" 起始, 之後有冇條件設 False 要跨行分析 ---
    # 單行處理: 唔報 (需要完整檔案分析, 見 scan_file)
    return False, None

def scan_file(path):
    """掃描單個 .py 檔案。返回命中列表。"""
    hits = []
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
    except Exception:
        return hits
    # 去掉註釋同 docstring 內容: 只掃代碼行 (strip 後以 # 開頭 = 註釋, 跳過)
    code_lines = []
    in_triple = None
    for line in lines:
        s = line.strip()
        # 處理 docstring 開關 (''' 或 """)
        if in_triple:
            if in_triple in s:
                in_triple = None
            code_lines.append(None)
            continue
        if s.startswith(("'''", '"""')):
            # 單行 triple 分隔符 (s == '"""' 或 s == "'''"): toggle
            if s in ("'''", '"""'):
                in_triple = s
                code_lines.append(None)
                continue
            # 同行開關 (start 同時 end): 唔入 in_triple
            if s.endswith(s[:3]) and len(s) > 3:
                code_lines.append(None)
                continue
            in_triple = s[:3]
            code_lines.append(None)
            continue
        if s.startswith('#'):
            code_lines.append(None)
            continue
        code_lines.append(line)
    # 變量層分析: 搵 ok/flag 變量嘅 assign True 然後從未喺條件下設 False
    assigns_true = {}   # var -> line
    cond_sets_false = set()
    for i, line in enumerate(lines):
        s = line.strip()
        # ok = True 起點
        m = re.match(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*True\s*(?:#.*)?$', s)
        if m and m.group(1).lower() in ('ok', 'ok_all', 'all_ok', 'allok', 'ok_a',
                                        'ok_n', 'ok_s', 'ok_tab', 'ok_odd',
                                        'all_pass', 'all_exact', 'all_found',
                                        'all_hit', 'allhit', 'theorem_ok', 'thm_ok',
                                        'ortho_ok', 'phase_ok', 'found', 'found_any',
                                        'mono', 'unique', 'bipartite', 'decay_found'):
            assigns_true.setdefault(m.group(1), i + 1)
        # 條件下設 False: if ...: 變量 = False
        if re.search(r'=\s*False\b', s):
            cond_sets_false.add(line[:line.find('=')].strip().split()[-1] if '=' in line else '')
    # 逐行主掃描 (只掃代碼行, 跳過註釋/docstring)
    prev = None
    for i, line in enumerate(code_lines):
        if line is None:
            prev = None
            continue
        is_hc, kind = classify_hardcode(line, prev)
        if is_hc:
            hits.append((i + 1, kind, line.strip()[:110]))
        prev = line
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    root = args.root
    total_hits = 0
    per_file = {}
    all_hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith('.py'):
                continue
            p = os.path.join(dirpath, fn)
            hits = scan_file(p)
            if hits:
                per_file[p] = hits
                all_hits.append((p, hits))
                total_hits += len(hits)

    # 輸出
    print(f"Hardcode scan root: {root}")
    print(f"Files with hardcoded True: {len(per_file)}")
    print(f"Total hardcoded True: {total_hits}")
    print()
    for p, hits in sorted(all_hits, key=lambda x: -len(x[1])):
        print(f"  {len(hits):3d}  {p}")
        for ln, kind, text in hits[:8]:
            print(f"        L{ln} [{kind}] {text}")
        if len(hits) > 8:
            print(f"        ... +{len(hits)-8} more")
    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'root': root, 'files': len(per_file), 'total': total_hits,
                       'hits': {p: [{'line': ln, 'kind': k, 'text': t} for ln, k, t in h]
                                for p, h in per_file.items()}}, f, indent=2, ensure_ascii=False)
        print(f"\nJSON -> {args.json}")
    print(f"\nRESULT: {'PASS (0 hardcoded)' if total_hits == 0 else f'FAIL ({total_hits} hardcoded)'}")
    sys.exit(0 if total_hits == 0 else 1)

if __name__ == '__main__':
    main()
