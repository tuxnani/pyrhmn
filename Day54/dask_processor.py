import dask.dataframe as dd
from dask.distributed import Client, LocalCluster
import pandas as pd
import numpy as np
import time
import os

def generate_large_data(num_rows: int, num_partitions: int = 4) -> dd.DataFrame:
    """
    Generates a large synthetic Dask DataFrame for demonstration purposes.
    
    Args:
        num_rows: Total number of rows for the resulting dataset.
        num_partitions: The number of Dask partitions (workers) to use.
        
    Returns:
        A Dask DataFrame.
    """
    print(f"Generating synthetic data: {num_rows:,} rows, {num_partitions} partitions...")
    
    # Create a large pandas DataFrame first
    data = {
        'group_id': np.random.randint(0, 1000, num_rows),
        'value_1': np.random.rand(num_rows) * 100,
        'value_2': np.random.randint(1, 10, num_rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], num_rows)
    }
    pdf = pd.DataFrame(data)
    
    # Convert to Dask DataFrame
    ddf = dd.from_pandas(pdf, npartitions=num_partitions)
    print(f"Dask DataFrame created with {ddf.npartitions} partitions.")
    return ddf

def parallel_process_data(ddf: dd.DataFrame) -> pd.DataFrame:
    """
    Performs a complex, parallel aggregation operation using Dask.
    
    Args:
        ddf: The input Dask DataFrame.
        
    Returns:
        The resulting Pandas DataFrame after computation is triggered.
    """
    print("Starting parallel processing (Group-by and Aggregation)...")
    
    # 1. Group by two columns
    grouped = ddf.groupby(['group_id', 'category'])
    
    # 2. Define multiple complex aggregations
    aggregated_ddf = grouped.agg(
        total_value_1=('value_1', 'sum'),
        mean_value_2=('value_2', 'mean'),
        count=('group_id', 'size'),
        max_value_1=('value_1', 'max')
    )
    
    # 3. Rename columns for clarity (optional, but good practice)
    aggregated_ddf.columns = [
        'Total_Value', 'Average_Score', 'Record_Count', 'Max_Value'
    ]
    
    # 4. Sort the result in parallel
    sorted_ddf = aggregated_ddf.reset_index().set_index('Record_Count').sort_index(ascending=False)

    # 5. Trigger computation and return as a Pandas DataFrame
    print("Dask computation graph built. Triggering computation now...")
    start_time = time.time()
    result_pdf = sorted_ddf.compute()
    end_time = time.time()
    
    print(f"Computation finished in {end_time - start_time:.2f} seconds.")
    return result_pdf

if __name__ == "__main__":
    # --- Dask Setup ---
    # Using LocalCluster and Client is best practice for controlling resources
    # It initializes a local scheduler and workers based on your available cores
    # Set n_workers to the number of logical cores you want to use
    n_workers = os.cpu_count() or 4
    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=1, processes=True)
    client = Client(cluster)
    
    print(f"Dask Dashboard link: {client.dashboard_link}")
    print(f"Running on {n_workers} workers.")
    
    # --- Configuration ---
    TOTAL_ROWS = 10_000_000  # 10 million rows for a significant workload
    PARTITIONS = n_workers * 2 # Good heuristic: 2x to 4x the number of workers

    try:
        # 1. Generate Data
        data_ddf = generate_large_data(TOTAL_ROWS, PARTITIONS)
        
        # 2. Process Data
        processed_data_pdf = parallel_process_data(data_ddf)
        
        # 3. Output Results
        print("\n--- Final Results (First 5 Rows) ---")
        print(processed_data_pdf.head())
        print(f"\nResulting Pandas DataFrame shape: {processed_data_pdf.shape}")

    finally:
        # 4. Clean up Dask resources
        print("\nClosing Dask client and cluster.")
        client.close()
        cluster.close()
