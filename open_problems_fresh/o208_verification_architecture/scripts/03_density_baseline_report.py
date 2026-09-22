#!/usr/bin/env python3
"""
O208 scripts/03_density_baseline_report.py — 密度基準報告模板生成器
====================================================================
任何數值匹配閉合聲稱必須附密度基準 (docs/01)。

用法:
    /usr/bin/python3 scripts/03_density_baseline_report.py \\
        --name "O208 示範" --obs 0.146 --obs_unit "%" \\
        --med 0.176 --search 2.4e5 --mc 1e6 --seed 42

或匯入:
    from density_baseline import DensityBaseline
    db = DensityBaseline(N_search=2.4e5, d_med=0.176, d_obs=0.146, N_mc=1e6, seed=42)
    print(db.report())
"""
import argparse, json, sys

class DensityBaseline:
    """密度基準 — 標準報告格式生成器."""

    def __init__(self, N_search, d_med, d_obs, N_mc=1_000_000, seed=None,
                 q_obs=None, name="", unit="%"):
        self.N_search = N_search
        self.d_med = d_med
        self.d_obs = d_obs
        self.N_mc = N_mc
        self.seed = seed
        self.q_obs = q_obs
        self.name = name
        self.unit = unit

    def verdict(self):
        if self.q_obs is None:
            return "🟡 未報告分位數 — 未閉合"
        if self.q_obs <= 1:
            return "🟢 統計顯著"
        if self.q_obs <= 5:
            return "🟡 候選 (需加強證據)"
        return "🔴 唔顯著 (密度效應)"

    def report(self):
        lines = [
            "## 密度基準",
            f"- 名稱: {self.name}",
            f"- N_search = {self.N_search:g}" + (f" (唯一候選)" if self.N_search == 1 else ""),
            f"- N_mc = {self.N_mc:g}, seed = {self.seed}",
            f"- d_obs = {self.d_obs}{self.unit} (觀測偏差)",
            f"- d_med = {self.d_med}{self.unit} (隨機中位偏差)",
            f"- q_obs = {self.q_obs}% → {self.verdict()}",
        ]
        return "\n".join(lines)

    def to_dict(self):
        return {
            "name": self.name, "N_search": self.N_search, "N_mc": self.N_mc,
            "seed": self.seed, "d_obs": self.d_obs, "d_med": self.d_med,
            "q_obs": self.q_obs, "unit": self.unit, "verdict": self.verdict(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='')
    ap.add_argument('--obs', type=float, required=True)
    ap.add_argument('--med', type=float, required=True)
    ap.add_argument('--search', type=float, required=True)
    ap.add_argument('--mc', type=float, default=1e6)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--q', type=float, default=None, help='觀測偏差分位數 (%)')
    ap.add_argument('--unit', default='%')
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    db = DensityBaseline(args.search, args.med, args.obs, args.mc, args.seed,
                         args.q, args.name, args.unit)
    print(db.report())
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(db.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nJSON -> {args.json}")

    # exit code: 有分位數先算閉合
    if args.q is None:
        print("\n⚠️ 冇分位數 = 未閉合 (docs/01 規則)")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
