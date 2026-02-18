# Mixed-Criticality Scheduling Project (FP-IAP / IAP-FP vs Global)

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
```

## Run
### Generate a Figure-20-like curve
```bash
python -m expriments.fig20
```

Outputs:
- `results/fig20.png`
- `results/fig20_points.csv`
- `results/fig20_raw.csv`

## Notes
- Generator uses UUniFast; total utilization = U_norm * m
- HI tasks: C_HI = C_LO * RHI
- LO tasks: C_HI = 0 (dropped in HI mode)
- FP-IAP pipeline: DCDU-WF allocation + swapping/balancing (Algorithms 1-7) + per-core FP schedulability (Audsley + RTA + AMC-style mode-change bound).
- Global baseline is a discrete-time simulation of Global Fixed Priority (DCDU) in LO and HI modes.
