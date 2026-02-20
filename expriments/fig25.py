import os
import matplotlib.pyplot as plt
from .common import run_acceptance_curve

def main():
    print("Generating Figure 25: Impact of Memory Interference (Tac)...")
    tac_values = [0.1, 0.2, 0.4, 0.6, 0.8]
    iap_res, glob_res = [], []

    for tac in tac_values:
        print(f"Testing Tac={tac}...")
        points, _ = run_acceptance_curve(
            m=4, n_tasks=10, util_points=[0.7], 
            trials_per_point=50, p_hi=0.5, r_hi=2.0, n_flags=4, 
            V=0.1, Tac=tac, seed0=42
        )
        iap_res.append(points[0]["accept_iap"] * 100)
        glob_res.append(points[0]["accept_global"] * 100)

    plt.figure(figsize=(7, 5))
    plt.plot(tac_values, iap_res, 'o-', color='blue', label='FP-IAP')
    plt.plot(tac_values, glob_res, 's--', color='orange', label='Global Baseline')
    plt.xlabel("Memory Interference Penalty (Tac)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig 25: Impact of Tac (m=4, U=0.7)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fig25.png", dpi=200)
    print("Done! Saved to results/fig25.png")

if __name__ == "__main__":
    main()