# src/baseline_global.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from .task import Task

@dataclass
class Job:
    task: Task
    deadline: int
    remaining: float

def _priority_key(task: Task) -> Tuple[int, float]:
    # Priority based on DCDU (Decreasing Criticality, then Utilization)
    crit_rank = 0 if task.criticality == "HI" else 1
    util = task.u_hi if task.criticality == "HI" else task.u_lo
    return (crit_rank, -util)

def simulate_global_fp(tasks: List[Task], m: int, horizon: int, mode: str = "LO", Tac: float = 0.6) -> bool:
    # In HI-mode, ONLY HI-criticality tasks are executed (Article Section III)
    if mode == "HI":
        active_tasks = [t for t in tasks if t.criticality == "HI"]
    else:
        active_tasks = tasks
    
    if not active_tasks: return True

    exec_times = {t.task_id: (t.c_lo if mode == "LO" else t.c_hi) for t in active_tasks}
    active_jobs: List[Job] = []
    
    for t in range(horizon):
        for task in active_tasks:
            if t % task.period == 0:
                if any(j.task.task_id == task.task_id for j in active_jobs):
                    return False 
                active_jobs.append(Job(task, t + task.deadline, float(exec_times[task.task_id])))

        for j in active_jobs:
            if t >= j.deadline and j.remaining > 0:
                return False

        active_jobs.sort(key=lambda j: (_priority_key(j.task), j.deadline))
        running_jobs = active_jobs[:m]
        
        # Memory interference penalty (Algorithm 8 logic)
        num_running = len(running_jobs)
        progress = 1.0 / (1.0 + (num_running - 1) * Tac) if num_running > 1 else 1.0

        for j in running_jobs:
            j.remaining -= progress

        active_jobs = [j for j in active_jobs if j.remaining > 0.001]
    return True

def global_schedulable(tasks: List[Task], m: int, Tac: float = 0.6) -> bool:
    max_p = max(t.period for t in tasks) if tasks else 0
    horizon = max(1, 5 * max_p) # Reduced horizon for faster exact calculation
    return simulate_global_fp(tasks, m, horizon, "LO", Tac) and \
           simulate_global_fp(tasks, m, horizon, "HI", Tac)