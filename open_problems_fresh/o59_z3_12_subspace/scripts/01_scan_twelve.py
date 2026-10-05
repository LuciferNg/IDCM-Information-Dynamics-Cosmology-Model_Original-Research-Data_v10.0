#!/usr/bin/env python3
"""
O59 Phase 1: 全面搜集 IDCM 中所有「12」嘅出現位置
================================================
掃描 docs + 所有 open_problems_fresh docs, 分類每個 12 嘅上下文。
"""
import os, re, json, glob

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
roots = [
    os.path.join(BASE, "docs"),
    os.path.join(BASE, "open_problems_fresh"),
]
# 收集所有 .md 檔案
files = []
for r in roots:
    for root, dirs, fs in os.walk(r):
        if "data" in root or "scripts" in root or "__pycache__" in root:
            continue
        for f in fs:
            if f.endswith(".md"):
                files.append(os.path.join(root, f))

print(f"掃描 {len(files)} 個 .md 檔案")

# 12 出現模式 (正則)
patterns = {
    "12 維/12D/12-dim": r"12\s*(維|D|d|-dim|維空間|維機制)",
    "= 12": r"=\s*12(?:\s|$|[,.)])",
    "12 =": r"(?<![0-9])12\s*=",
    "×12/*12": r"[×x*]\s*12(?:\s|$|[,.)])",
    "/12": r"/\s*12(?:\s|$|[,.)])",
    "12 個": r"12\s*個",
    "12 元素": r"12\s*元素",
    "C(12,2)": r"C\(12,\s*2\)",
    "su(12)": r"su\(12\)",
    "SU(12)": r"SU\(12\)",
    "12 組": r"12\s*組",
    "12 個 Kähler": r"12\s*個\s*Kähler",
    "1+2+3+4+2": r"1\s*\+\s*2\s*\+\s*3\s*\+\s*4\s*\+\s*2",
    "3×12": r"3\s*[×x]\s*12",
    "12=3×4": r"12\s*=\s*3\s*[×x]\s*4",
    "Nd/4+1": r"44/\s*4\s*\+\s*1",
    "L5+1": r"L[₅5]\s*\+\s*1",
    "13−1": r"13\s*[−-]\s*1",
    "12 = 36/3": r"12\s*=\s*36\s*/\s*3",
}

results = {k: [] for k in patterns}
for f in files:
    try:
        content = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for name, pat in patterns.items():
        for m in re.finditer(pat, content):
            line_start = content.rfind("\n", 0, m.start()) + 1
            line_end = content.find("\n", m.end())
            line = content[line_start:line_end if line_end != -1 else len(content)].strip()
            results[name].append((f.replace(BASE, ""), line[:160]))

print("\n" + "=" * 80)
for name, hits in results.items():
    print(f"\n### {name} ({len(hits)} hits)")
    seen = set()
    for f, line in hits[:12]:
        key = (f, line[:80])
        if key in seen:
            continue
        seen.add(key)
        print(f"  {f}: {line[:130]}")
    if len(hits) > 12:
        print(f"  ... (+{len(hits)-12} more)")
