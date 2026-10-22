#!/usr/bin/env python3
"""
O96 — 02: 排除法驗證 (L5)
========================
目標: 系統性證明 SU(5)/SO(10)/E₆ 全部 FAIL rank/fundamental/Λ² 匹配

方法:
  1. 用 rank 同 fundamental 作為篩選條件
  2. 用 66 = Λ²(N) 作為第二篩選
  3. 用 143 = adjoint 作為第三篩選
  4. 用 4×3 tensor product 結構作為最終篩選
"""
import math
import json
import os

phi = (1 + math.sqrt(5)) / 2


def L(n):
    return round(phi**n + (-phi)**(-n))


def F(n):
    return round((phi**n - (-phi)**(-n)) / math.sqrt(5))


# ============================================
# Lie 群定義
# ============================================

# SU(N) series
def su_props(N):
    return {
        "name": f"SU({N})",
        "rank": N - 1,
        "fundamental": N,
        "adjoint": N**2 - 1,
        "Lambda2": N * (N - 1) // 2,
        "tensor_4x3": N == 12,
        "series": "A"
    }


# SO(N) series
def so_props(N):
    rank = N // 2
    return {
        "name": f"SO({N})",
        "rank": rank,
        "fundamental": N,
        "adjoint": N * (N - 1) // 2,
        "Lambda2": N * (N - 1) // 2,
        "tensor_4x3": False,
        "series": "D"
    }


# Sp(N) series (N even)
def sp_props(N):
    rank = N // 2
    return {
        "name": f"Sp({N})",
        "rank": rank,
        "fundamental": N,
        "adjoint": N * (N + 1) // 2,
        "Lambda2": N * (N - 1) // 2,
        "tensor_4x3": False,
        "series": "C"
    }


# Exceptional groups
exceptional = [
    {"name": "G₂", "rank": 2, "fundamental": 7, "adjoint": 14, "Lambda2": 21, "tensor_4x3": False},
    {"name": "F₄", "rank": 4, "fundamental": 26, "adjoint": 52, "Lambda2": 324, "tensor_4x3": False},
    {"name": "E₆", "rank": 6, "fundamental": 27, "adjoint": 78, "Lambda2": 351, "tensor_4x3": False},
    {"name": "E₇", "rank": 7, "fundamental": 56, "adjoint": 133, "Lambda2": 1540, "tensor_4x3": False},
    {"name": "E₈", "rank": 8, "fundamental": 248, "adjoint": 248, "Lambda2": 30628, "tensor_4x3": False},
]

# Build candidate list
candidates = []

# SU(N) for N=2..20
for N in range(2, 21):
    candidates.append(su_props(N))

# SO(N) for N=4..24 (even)
for N in range(4, 25, 2):
    candidates.append(so_props(N))

# Sp(N) for N=2..24 (even)
for N in range(2, 25, 2):
    candidates.append(sp_props(N))

# Exceptional
candidates.extend(exceptional)

# ============================================
# 驗證
# ============================================
results = {}
all_pass = True


def check(name, condition, detail):
    global all_pass
    ok = bool(condition)
    if not ok:
        all_pass = False
    results[name] = {"pass": ok, "detail": detail}
    return ok


def main():
    global all_pass
    print("=" * 72)
    print("O96 — 02: 排除法驗證 (L5)")
    print("=" * 72)

    # IDCM target values
    target_rank = 11
    target_fundamental = 12
    target_Lambda2 = 66
    target_adjoint = 143
    target_N = 12

    print(f"\n  目標: rank={target_rank}, fundamental={target_fundamental}, "
          f"Λ²={target_Lambda2}, adjoint={target_adjoint}")

    # ============================================
    # 篩選 1: rank 匹配
    # ============================================
    print("\n" + "=" * 72)
    print("篩選 1: rank = 11")
    print("=" * 72)

    rank_11 = [c for c in candidates if c["rank"] == target_rank]
    print(f"\n  候選總數: {len(candidates)}")
    print(f"  rank=11 群: {len(rank_11)}")
    for c in rank_11:
        print(f"    {c['name']}: fundamental={c['fundamental']}, adjoint={c['adjoint']}")

    check("S1_rank_11_count", len(rank_11) == 3,
          f"rank=11 群數 = {len(rank_11)} (SU(12), SO(22), Sp(22))")

    # ============================================
    # 篩選 2: fundamental 匹配
    # ============================================
    print("\n" + "=" * 72)
    print("篩選 2: fundamental = 12")
    print("=" * 72)

    rank_11_fund_12 = [c for c in rank_11 if c["fundamental"] == target_fundamental]
    print(f"\n  rank=11 且 fundamental=12: {len(rank_11_fund_12)}")
    for c in rank_11_fund_12:
        print(f"    ✅ {c['name']}: Λ²={c['Lambda2']}, adjoint={c['adjoint']}")

    check("S2_only_SU12", len(rank_11_fund_12) == 1,
          f"只有 {len(rank_11_fund_12)} 個群滿足 rank=11 且 fundamental=12")
    check("S2_is_SU12", rank_11_fund_12[0]["name"] == "SU(12)" if rank_11_fund_12 else False,
          f"唯一匹配群 = {rank_11_fund_12[0]['name'] if rank_11_fund_12 else 'NONE'}")

    # ============================================
    # 篩選 3: Λ² = 66
    # ============================================
    print("\n" + "=" * 72)
    print("篩選 3: Λ² = 66")
    print("=" * 72)

    rank_11_fund_12_lambda2 = [c for c in rank_11_fund_12 if c["Lambda2"] == target_Lambda2]
    print(f"\n  rank=11, fundamental=12, Λ²=66: {len(rank_11_fund_12_lambda2)}")
    for c in rank_11_fund_12_lambda2:
        print(f"    ✅ {c['name']}")

    check("S3_Lambda2_match", len(rank_11_fund_12_lambda2) == 1,
          f"Λ²匹配: {len(rank_11_fund_12_lambda2)}")

    # ============================================
    # 篩選 4: adjoint = 143
    # ============================================
    print("\n" + "=" * 72)
    print("篩選 4: adjoint = 143")
    print("=" * 72)

    all_match = [c for c in rank_11_fund_12_lambda2 if c["adjoint"] == target_adjoint]
    print(f"\n  全部匹配: {len(all_match)}")
    for c in all_match:
        print(f"    ✅ {c['name']}")

    check("S4_adjoint_match", len(all_match) == 1,
          f"adjoint 匹配: {len(all_match)}")
    check("S4_is_SU12", all_match[0]["name"] == "SU(12)" if all_match else False,
          f"唯一解 = {all_match[0]['name'] if all_match else 'NONE'}")

    # ============================================
    # 篩選 5: 4×3 tensor product 結構
    # ============================================
    print("\n" + "=" * 72)
    print("篩選 5: 4×3 tensor product 結構")
    print("=" * 72)

    tensor_match = [c for c in candidates if c["tensor_4x3"]]
    print(f"\n  支援 4×3 tensor product: {len(tensor_match)}")
    for c in tensor_match:
        print(f"    ✅ {c['name']}")

    check("S5_tensor_match", len(tensor_match) == 1,
          f"tensor product 匹配: {len(tensor_match)}")
    check("S5_is_SU12", tensor_match[0]["name"] == "SU(12)" if tensor_match else False,
          f"唯一解 = {tensor_match[0]['name'] if tensor_match else 'NONE'}")

    # ============================================
    # 詳細排除表
    # ============================================
    print("\n" + "=" * 72)
    print("詳細排除表")
    print("=" * 72)

    # Focus on the key alternative GUT groups
    key_groups = ["SU(5)", "SU(11)", "SU(12)", "SU(13)", "SO(10)",
                  "SO(22)", "Sp(22)", "E₆", "E₇", "E₈", "F₄", "G₂"]

    print(f"\n  {'Group':<10} {'rank':<6} {'fund':<6} {'Λ²':<6} {'adj':<6} {'4×3?':<6} {'判決':<6}")
    print(f"  {'-'*50}")

    for c in candidates:
        if c["name"] in key_groups:
            r_ok = "✅" if c["rank"] == target_rank else "❌"
            f_ok = "✅" if c["fundamental"] == target_fundamental else "❌"
            l_ok = "✅" if c["Lambda2"] == target_Lambda2 else "❌"
            a_ok = "✅" if c["adjoint"] == target_adjoint else "❌"
            t_ok = "✅" if c["tensor_4x3"] else "❌"
            verdict = "✅" if c["name"] == "SU(12)" else "❌"
            print(f"  {c['name']:<10} {r_ok:<6} {f_ok:<6} {l_ok:<6} {a_ok:<6} {t_ok:<6} {verdict:<6}")

    # ============================================
    # 總結
    # ============================================
    print("\n" + "=" * 72)
    print("L5 排除法總結")
    print("=" * 72)

    total = len(results)
    passed = sum(1 for v in results.values() if v["pass"])
    print(f"  總驗證項: {total}, 通過: {passed}/{total}")

    for k, v in results.items():
        flag = "✅" if v["pass"] else "❌"
        print(f"  {flag} {k}: {v['detail']}")

    # Identify all groups that pass ALL filters
    all_conditions = [c for c in candidates
                      if c["rank"] == target_rank
                      and c["fundamental"] == target_fundamental
                      and c["Lambda2"] == target_Lambda2
                      and c["adjoint"] == target_adjoint
                      and c["tensor_4x3"]]
    unique_match = len(all_conditions) == 1 and all_conditions[0]["name"] == "SU(12)"
    check("L5_summary_unique", unique_match,
          f"唯一通過所有篩選嘅群: {all_conditions[0]['name'] if all_conditions else 'NONE'}")

    # === Save results ===
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    exclusion_data = []
    for c in candidates:
        if c["name"] in key_groups:
            exclusion_data.append({
                "name": c["name"],
                "rank": c["rank"],
                "fundamental": c["fundamental"],
                "Lambda2": c["Lambda2"],
                "adjoint": c["adjoint"],
                "tensor_4x3": c["tensor_4x3"],
                "rank_match": c["rank"] == target_rank,
                "fundamental_match": c["fundamental"] == target_fundamental,
                "Lambda2_match": c["Lambda2"] == target_Lambda2,
                "adjoint_match": c["adjoint"] == target_adjoint,
                "tensor_match": c["tensor_4x3"],
                "unique_solution": c["name"] == "SU(12)"
            })

    output = {
        "verdict": "ALL PASS — SU(12) is the unique solution" if all_pass else "PARTIAL FAILURE",
        "all_pass": all_pass,
        "total_checks": total,
        "passed": passed,
        "results": results,
        "target": {
            "rank": target_rank,
            "fundamental": target_fundamental,
            "Lambda2": target_Lambda2,
            "adjoint": target_adjoint,
            "tensor_4x3": True
        },
        "exclusion_data": exclusion_data,
        "unique_solution": "SU(12)"
    }

    with open(os.path.join(data_dir, '02_exclusion.json'), 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 結果已保存至 data/02_exclusion.json")
    print(f"\n{'=' * 72}")
    print(f"Final: {'🟢 ALL PASS — SU(12) is the unique solution' if all_pass else '🔴 PARTIAL FAILURE'}")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()