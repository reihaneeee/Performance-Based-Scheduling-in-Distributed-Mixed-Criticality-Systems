import csv
import os
import time
from src.generator import generate_taskset

def save_tasksets_to_csv (tasksets_data, filepath):
    if not tasksets_data:
        return
    
    # Extracting CSV headers
    headers = tasksets_data[0].keys()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(tasksets_data)
    print(f" (.^.) Data successfully saved to: {filepath}")


def run_generation_expriment (config, output_dir="results"):

    all_tasks_flat = []                                     # List to hold all tasks
    # Extract the parameters
    n_tasks=config['n_tasks']
    n_cores=config['n_cores']
    u_list=config['utilization_list']                       # List of utilization points (X-axis of paper graphs)
    p_hi_prob=config['p_hi']
    r_hi_factor=config['r_hi']
    n_flags=config['n_flags']
    num_sets=config['num_sets_per_utilization']             # Sample size per point (example: 100 sets)

    print(f"--- Running Experiment Runner ---")
    print(f"Settings: Cores={n_cores}, Tasks={n_tasks}, P_HI={p_hi_prob}, R_HI={r_hi_factor}")

    # to assign a uniqe index to each generated task_set
    set_id_counter = 0

    for u_norm in u_list:
        print(f"Generating {num_sets} sets for Target Utilization: {u_norm} ...")

        for _ in range(num_sets):
            tasks, metadata = generate_taskset(
                n_tasks=n_tasks,
                n_cores=n_cores,
                target_u_norm=u_norm,
                p_hi_prob=p_hi_prob,
                r_hi_factor=r_hi_factor,
                min_period=config.get('min_period', 10),
                max_period=config.get('max_period', 100),
                n_flags=n_flags
            )

            for task in tasks:
                row = task.to_dict()
                row['set_id'] = set_id_counter
                row['system_total_utilization'] = metadata['u_sum_absolute']
                row['system_target_u_norm'] = u_norm
                row['system_cores'] = n_cores
                
                all_tasks_flat.append(row)

            set_id_counter += 1

    filename = f"tasksets_n{config['n_tasks']}_m{config['n_cores']}_phigh{config['p_hi']}.csv"
    filepath = os.path.join(output_dir, filename)

    save_tasksets_to_csv(all_tasks_flat, filepath)
    return filepath