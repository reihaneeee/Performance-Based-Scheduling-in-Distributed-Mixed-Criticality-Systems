import random
import math
from .task import Task

def uunifast (n, u_total):
    sum_u = u_total
    utilizations = []

    for i in range(1, n):
        next_sum_u = sum_u * (random.random() ** (1.0 / (n - i)))
        utilizations.append(sum_u - next_sum_u)
        sum_u = next_sum_u

    utilizations.append(sum_u)
    return utilizations

def generate_taskset (
        n_tasks,            # Number of tasks (n)
        n_cores,            # Number of cores (m)
        target_u_norm,      # Normilized utilization 
        p_hi_prob,          # Probability of a task being high criticality  
        r_hi_factor,        # Factor to calculate C_HI (C_HI = C_LOW * R_HI)
        min_period=10,      
        max_period=1000,     
        n_flags=4           # number of memory banks/interference domains (*/assiges randomly\*-_-)
):
    # Calculate Total Utilization for UUnifast
    u_sum_absolute = target_u_norm * n_cores

    # generate utilizatios for LOW mode
    utilizations = uunifast(n_tasks, u_sum_absolute)
    tasks = []

    for i, u_low in enumerate (utilizations):
        task_id = i + 1

        # Determin the Criticality
        if random.random() < p_hi_prob:
            criticality = 'HIGH'
            # Caus R_HI varies or is a max parameter (based on the paper)
            # we use it as the multiplier
            current_r_hi = r_hi_factor
        else:
            criticality = 'LOW'
            current_r_hi = 1.0

        # generating period: based on the paper we use "Uniform Distribution" for perios
        period = random.randint(min_period, max_period)

        # U_LOW = C_LOW / T => C_LOW + U_LOW * T
        c_low = u_low * period
        c_high = c_low * current_r_hi

        # Making sure C_LOW and C_HIGH dont exceed period
        if c_high > period:
            c_high = period
            c_low  = c_high / current_r_hi

        # assigning random flags
        flag = random.randint(1, n_flags)

        new_task = Task (
            task_id=task_id, 
            criticality=criticality,
            c_low=c_low, 
            c_high=c_high,
            period=period,
            flag=flag
        )
        tasks.append(new_task)

    # returning metadata for runner to save it
    metadata = {
        "m_cores": n_cores,
        "n_tasks": n_tasks,
        "target_u_norm": target_u_norm,
        "u_sum_absolute": u_sum_absolute,
        "p_high": p_hi_prob
    }
    
    return tasks, metadata