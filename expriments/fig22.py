import os
import matplotlib.pyplot as plt
from .common import run_acceptance_curve

def main():
    print("Generating Figure 22: Impact of Task Count (n)...")
    n_values = [10, 20, 30, 40]
    iap_res, glob_res = [], []

    for n in n_values:
        print(f"Testing n={n}...")
        points, _ = run_acceptance_curve(
            m=4, n_tasks=n, util_points=[0.7], 
            trials_per_point=50, p_hi=0.5, r_hi=2.0, n_flags=4, 
            V=0.1, Tac=0.6, seed0=42
        )
        iap_res.append(points[0]["accept_iap"] * 100)
        glob_res.append(points[0]["accept_global"] * 100)

    plt.figure(figsize=(7, 5))
    plt.plot(n_values, iap_res, 'o-', color='blue', label='FP-IAP')
    plt.plot(n_values, glob_res, 's--', color='orange', label='Global Baseline')
    plt.xlabel("Number of Tasks (n)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig 22: Impact of n (m=4, U=0.7)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fig22.png", dpi=200)
    print("Done! Saved to results/fig22.png")

if __name__ == "__main__":
    main()