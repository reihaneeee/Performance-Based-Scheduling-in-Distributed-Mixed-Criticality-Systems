from expriments.common import run_generation_expriment

def main():
    scenarios = [
        # Scenario 1: Standard case (Fig 20 in paper) - 4 Cores, 10 Tasks
        {
            'name': 'Scenario_Standard_4Cores',
            'n_cores': 4,
            'n_tasks': 10,
            'utilization_list': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'p_hi': 0.5,      
            'r_hi': 2.0,      
            'n_flags': 4,    
            'num_sets_per_utilization': 5  
        },
        # Scenario 2: More Tasks (Fig 23 in paper) - 4 Cores, 16 Tasks
        {
            'name': 'Scenario_Heavy_16Tasks',
            'n_cores': 4,
            'n_tasks': 16,
            'utilization_list': [0.5, 0.6, 0.7, 0.8],
            'p_hi': 0.5,      
            'r_hi': 2.0,      
            'n_flags': 4,    
            'num_sets_per_utilization': 5  
        },
        # Scenario 3: More Cores (Fig 24 in paper) - 8 Cores, 20 Tasks
        {
            'name': 'Scenario_ManyCores_8Cores',
            'n_cores': 8,
            'n_tasks': 20,
            'utilization_list': [0.5, 0.6, 0.7, 0.8],
            'p_hi': 0.5,      
            'r_hi': 2.0,      
            'n_flags': 8,    
            'num_sets_per_utilization': 5  
        }
    ]

    print("-|_|- Starting Phase 1: Data Generation for Multiple Scenarios...")
    
    for config in scenarios:
        print(f"\n>>> Running: {config['name']}")
        
        output_csv = run_generation_expriment(config, output_dir="results")
        
        print(f"    ✔ Done. Output: {output_csv}")

    print("\n------------------------------------------------")
    print(f"/*\ All Scenarios Complete!")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()