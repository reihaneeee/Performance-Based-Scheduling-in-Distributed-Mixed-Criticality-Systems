import os
import matplotlib.pyplot as plt
from .common import run_acceptance_curve

def main():
    print("Generating Figure 23: Impact of R_HI factor...")
    r_values = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    iap_res, glob_res = [], []

    for r in r_values:
        print(f"Testing r_hi={r}...")
        points, _ = run_acceptance_curve(
            m=4, n_tasks=10, util_points=[0.7], 
            trials_per_point=50, p_hi=0.5, r_hi=r, n_flags=4, 
            V=0.1, Tac=0.6, seed0=42
        )
        iap_res.append(points[0]["accept_iap"] * 100)
        glob_res.append(points[0]["accept_global"] * 100)

    plt.figure(figsize=(7, 5))
    plt.plot(r_values, iap_res, 'o-', color='blue', label='FP-IAP')
    plt.plot(r_values, glob_res, 's--', color='orange', label='Global Baseline')
    plt.xlabel("R_HI (C_HI / C_LO)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig 23: Impact of R_HI (m=4, U=0.7)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fig23.png", dpi=200)
    print("Done! Saved to results/fig23.png")

if __name__ == "__main__":
    main()