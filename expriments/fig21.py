import os
import matplotlib.pyplot as plt
from .common import run_acceptance_curve

def main():
    print("Running Figure 21 (m impact) - Matching Fig 20 parameters...")
    # Parameters exactly from your friends' fig20.py
    m_values = [2, 4, 6, 8]
    trials = 50
    iap_res, glob_res = [], []

    for m in m_values:
        print(f"Testing m={m}...")
        points, _ = run_acceptance_curve(
            m=m, 
            n_tasks=10, # Keeping n_tasks same as fig20.py
            util_points=[0.7], 
            trials_per_point=trials,
            p_hi=0.5, r_hi=2.0, n_flags=4, V=0.1, Tac=0.6,
            seed0=42, util_tolerance=0.0, min_period=1, max_period=100
        )
        iap_res.append(points[0]["accept_iap"] * 100)
        glob_res.append(points[0]["accept_global"] * 100)

    plt.figure(figsize=(7, 5))
    plt.plot(m_values, iap_res, marker="o", label="IAP-FP")
    plt.plot(m_values, glob_res, marker="s", label="Global Baseline")
    plt.xlabel("Number of Cores (m)")
    plt.ylabel("Schedulability (%)")
    plt.title("Fig 21: Schedulability vs Core Count (U=0.7)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fig21.png", dpi=200)
    print("Finished! Check results/fig21.png")

if __name__ == "__main__":
    main()