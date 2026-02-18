"""
Reproduce a 'Figure 20-like' acceptance vs utilization curve (IAP-FP vs Global baseline).
Run:
  python -m expriments.fig20
"""
import os
import matplotlib.pyplot as plt

from .common import run_acceptance_curve, save_rows, weighted_schedulability

def main():
    m = 4
    n_tasks = 10
    util_points = [0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    trials = 50

    points, raw = run_acceptance_curve(
        m=m, n_tasks=n_tasks,
        util_points=util_points,
        trials_per_point=trials,
        p_hi=0.5,
        r_hi=2.0,
        n_flags=4,
        V=0.1,
        Tac=0.6,
        seed0=42,
        util_tolerance=0.0,
        min_period=1,
        max_period=100
    )

    os.makedirs("results", exist_ok=True)
    save_rows("results/fig20_points.csv", points)
    save_rows("results/fig20_raw.csv", raw)

    aw_iap = weighted_schedulability(points, "accept_iap")
    aw_glob = weighted_schedulability(points, "accept_global")
    print(f"Weighted schedulability: IAP={aw_iap:.3f}  Global={aw_glob:.3f}")

    x = [p["u_norm"] for p in points]
    y1 = [p["accept_iap"]*100 for p in points]
    y2 = [p["accept_global"]*100 for p in points]

    plt.figure()
    plt.plot(x, y1, marker="o", label="IAP-FP (FP-IAP)")
    plt.plot(x, y2, marker="s", label="Global FP baseline")
    plt.xlabel("Normalized utilization (U)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig20-like: Schedulability vs Utilization (m=4)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/fig20.png", dpi=200)
    print("Saved: results/fig20.png")

if __name__ == "__main__":
    main()
