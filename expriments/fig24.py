import os
import matplotlib.pyplot as plt
from .common import run_acceptance_curve

def main():
    print("Generating Figure 24: Impact of HI-task ratio (P_HI)...")
    p_hi_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    iap_res, glob_res = [], []

    for p in p_hi_values:
        print(f"Testing P_HI={p}...")
        points, _ = run_acceptance_curve(
            m=4, n_tasks=10, util_points=[0.7], 
            trials_per_point=50, p_hi=p, r_hi=2.0, n_flags=4, 
            V=0.1, Tac=0.6, seed0=42
        )
        iap_res.append(points[0]["accept_iap"] * 100)
        glob_res.append(points[0]["accept_global"] * 100)

    plt.figure(figsize=(7, 5))
    plt.plot(p_hi_values, iap_res, 'o-', color='blue', label='FP-IAP')
    plt.plot(p_hi_values, glob_res, 's--', color='orange', label='Global Baseline')
    plt.xlabel("HI-task Ratio (P_HI)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig 24: Impact of P_HI (m=4, U=0.7)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fig24.png", dpi=200)
    print("Done! Saved to results/fig24.png")

if __name__ == "__main__":
    main()