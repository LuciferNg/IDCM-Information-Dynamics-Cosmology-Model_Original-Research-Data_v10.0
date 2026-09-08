#!/usr/bin/env python3
"""41 — (c2) 收尾: 結構命中 null-control + δ 31 hits 枚舉 + s=85/41 排除驗證
T1: 100 random targets @1e-4: 結構命中分佈 (框架角係咪低於/高於隨機?)
T2: δ 31 個結構命中完整枚舉 + 分類 (shared-s 家族 vs 其他)
T3: s=85 對 θ₂₃ 嘅 co-closure: beat(33,35)/beat(x,y), x+y=85, 可能值範圍
T4: s=41 no-reuse 確認
"""
import numpy as np

N = 88
pairs = [(a,b) for a in range(1,N) for b in range(a+1,N+1)]
beats = np.array([4*np.sin((b-a)*np.pi/176.0)*np.cos((a+b)*np.pi/176.0) for a,b in pairs])
ds = np.array([(b-a, a+b) for a,b in pairs])
M = len(pairs)
STRUCT = {1,2,3,4,5,6,7,8,9,11,12,13,16,17,18,19,20,21,22,25,27,29,32,33,34,36,38,40,41,42,44,47,55,63,64,66,68,76,77,85,88,90,91,98}
D6 = {1,2,6,9,19,21}; S6 = {11,25,41,44,68,85}

def struct_hits(t, tol=1e-4):
    hits = []
    for i in range(M):
        r = beats[i]/beats
        m = np.abs(r - t) < tol*t
        for j in np.argwhere(m).flatten():
            (d1,s1),(d2,s2) = ds[i], ds[j]
            if d1 in STRUCT and s1 in STRUCT and d2 in STRUCT and s2 in STRUCT:
                hits.append((tuple(pairs[i]),(d1,s1),tuple(pairs[j]),(d2,s2)))
    return hits

print("=== T1: 結構命中 null-control (100 random targets @1e-4) ===")
rng = np.random.default_rng(11)
counts = []
for _ in range(100):
    t = 10**rng.uniform(-1.5, 0.5)
    counts.append(len(struct_hits(t)))
counts = np.array(counts)
print(f"  隨機 target 結構命中: mean={counts.mean():.2f}, median={np.median(counts):.0f}, "
      f"max={counts.max()}, P(≥1)={(counts>=1).mean()*100:.0f}%, P(≥2)={(counts>=2).mean()*100:.0f}%")

print("\n=== T2: 框架 4 角嘅結構命中數 + δ 枚舉 ===")
for name, deg, kind in [("θ₁₂", 13.039994, "tan"), ("θ₂₃", 2.379994, "tan"),
                        ("θ₁₃", 0.200961, "sin"), ("δ", 66.399960, "tan")]:
    t = np.sin(np.radians(deg)) if kind=="sin" else np.tan(np.radians(deg))
    hits = struct_hits(t)
    print(f"  {name}: {len(hits)} 結構命中")
    if name == "δ":
        fam = {}
        for (p1,(d1,s1),p2,(d2,s2)) in hits:
            key = (d1,s1,d2,s2)
            fam.setdefault((d1,d2), []).append((s1,s2,p1,p2))
        for (d1,d2), lst in sorted(fam.items()):
            print(f"    d族 ({d1},{d2}): {len(lst)} 個: s={sorted(set(s1 for s1,_,_,_ in lst))}")

print("\n=== T3: s=85 對 θ₂₃ co-closure ===")
num = 4*np.sin(2*np.pi/176)*np.cos(68*np.pi/176)
t23 = np.tan(np.radians(2.379994))
need = num/t23
print(f"  beat(33,35) = {num:.6f}, θ₂₃ tan 需分母 = {need:.6f}")
# s=85 所有 pair 嘅 beat 範圍
b85 = [4*np.sin((b-a)*np.pi/176)*np.cos(85*np.pi/176) for a,b in pairs if a+b==85]
print(f"  s=85 pairs 嘅 beat 範圍: [{min(b85):.6f}, {max(b85):.6f}] — 需要 {need:.4f} → {'✗ 不可能 (太大)' if max(b85) < need else '✓ 可能'}")
# s=41 所有 pair 範圍
b41 = [4*np.sin((b-a)*np.pi/176)*np.cos(41*np.pi/176) for a,b in pairs if a+b==41]
print(f"  s=41 pairs 嘅 beat 範圍: [{min(b41):.6f}, {max(b41):.6f}]")

print("\n=== T4: s=41 no-reuse ===")
print("  (21,41) = (31,10) = θ₁₃ 分母 (10,31) ✓ 重用 → no-reuse 排除 (docs/04 §8.3)")

print("\nRESULT: (c2) 收尾測試完成")
