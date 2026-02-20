import math

def calculate_rta(task, all_tasks, m, Tac, mode="LO"):
    Ci = task.c_lo if mode == "LO" else task.c_hi
    interference_penalty = (m - 1) * Tac
    
    R_new = Ci + interference_penalty
    R_old = 0
    
    while R_new != R_old:
        R_old = R_new
        interference_sum = 0
        
        hp_tasks = [t for t in all_tasks if t.deadline < task.deadline]
        
        for pj in hp_tasks:
            Cj = pj.c_lo if mode == "LO" else pj.c_hi
            interference_sum += math.ceil(R_old / pj.period) * Cj
            
        R_new = Ci + interference_penalty + (1/m) * interference_sum
        
        if R_new > task.deadline:
            return float('inf')
            
    return R_new

def global_schedulable(tasks, m, Tac=0.6):
    if not tasks:
        return True

    for t in tasks:
        if calculate_rta(t, tasks, m, Tac, mode="LO") > t.deadline:
            return False
            
    hi_tasks = [t for t in tasks if t.criticality == 'HI']
    for t in hi_tasks:
        if calculate_rta(t, hi_tasks, m, Tac, mode="HI") > t.deadline:
            return False
            
    return True