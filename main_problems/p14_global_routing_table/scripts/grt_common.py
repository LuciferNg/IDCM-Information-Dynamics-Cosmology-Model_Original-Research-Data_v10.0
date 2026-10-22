#!/usr/bin/env python3
"""GRT 共用模組: 節點載入 + 建圖 (histogram-gap threshold)."""
import math
from collections import defaultdict

import numpy as np

PHI = (1 + 5**0.5) / 2
PHI_INV = 1 / PHI
EPS = PHI_INV / 4
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

NODES_PATH = "../../p4_cmb_cold_spot/data/a5_nodes.txt"
FRUST_PATH = "../../p4_cmb_cold_spot/data/frustration_edges.txt"
COLOR_PATH = "../../p4_cmb_cold_spot/data/anchored_coloring.txt"


def load_nodes(path=NODES_PATH):
    """載入 60 節點 (RA, Dec) -> (vec, idx)."""
    nodes = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ra, dec = map(float, line.split())
            nodes.append((ra, dec))
    vecs = []
    for ra, dec in nodes:
        r, d = math.radians(ra), math.radians(dec)
        vecs.append(np.array([math.cos(d) * math.cos(r),
                              math.cos(d) * math.sin(r),
                              math.sin(d)]))
    return nodes, np.array(vecs)


def ang_deg(v1, v2):
    dot = float(np.clip(np.dot(v1, v2), -1.0, 1.0))
    return math.degrees(math.acos(dot))


def edge_threshold_from_histogram(vecs):
    """技能 §1: 排序距離, 搵第 1 個 cluster (120 條邊) 同第 2 個 cluster 之間嘅 gap mid.
    Rhombicosidodecahedron: 邊長 ~26.09° (×120), 第二層 ~31.68° (×30) → threshold ~28°.
    """
    N = len(vecs)
    dists = []
    for i in range(N):
        for j in range(i + 1, N):
            dists.append(ang_deg(vecs[i], vecs[j]))
    dists = np.array(dists)
    dists.sort()
    # 搵第 120 條邊同第 121 條之間嘅 gap (E=120)
    thresh = (dists[119] + dists[120]) / 2
    return thresh, dists


def build_graph(vecs, thresh):
    """無向圖: adj[i] = set of neighbours."""
    N = len(vecs)
    adj = defaultdict(set)
    for i in range(N):
        for j in range(i + 1, N):
            if ang_deg(vecs[i], vecs[j]) < thresh:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def load_frustration_edges(path=FRUST_PATH):
    """阻挫邊 (1-indexed 檔案 -> 0-indexed pairs)."""
    edges = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            u, v = int(parts[0]) - 1, int(parts[1]) - 1
            edges.append((u, v))
    return set(frozenset(e) for e in edges)


def load_colors(path=COLOR_PATH):
    """從 anchored_coloring.txt 載入 BFS 著色 (1=冷, 0=熱)."""
    colors = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            idx, color = int(parts[0]), int(parts[3])
            colors[idx] = color
    return colors


def compute_frustration_edges(adj, colors):
    """從圖鄰接表 + BFS 著色計算真正阻挫邊 (同色相鄰)."""
    frust = set()
    for u in adj:
        for v in adj[u]:
            if v > u and colors[u] == colors[v]:
                frust.add((u, v))
    return frust
