import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest

def smart_cleaner(df: pd.DataFrame, 
                  cleaning_level: str = 'normal', 
                  outlier_level: str = 'none', 
                  outlier_method: str = 'remove') -> pd.DataFrame:
    """
    Applies a tiered data cleaning and outlier detection pipeline.

    Args:
        df: The input pandas DataFrame.
        cleaning_level: 'shallow', 'normal', or 'deep'.
            - 'shallow': Removes duplicate rows and all-NaN rows. Strips whitespace.
            - 'normal': All 'shallow' steps + imputes NaNs (median/mode) & standardizes case.
            - 'deep': All 'shallow' steps + advanced KNN imputation, scaling (numeric),
                      and one-hot encoding (categorical).
        outlier_level: 'none', 'normal', or 'intense'.
            - 'none': No outlier detection.
            - 'normal': Uses the IQR (Interquartile Range) method.
            - 'intense': Uses the Isolation Forest algorithm.
        outlier_method: 'remove' or 'flag'.
            - 'remove': Drops rows identified as outliers.
            - 'flag': Adds a boolean column 'is_outlier'.
            
    Returns:
        A cleaned pandas DataFrame.
    """
    
    print(f"--- Starting Smart Cleaner ---")
    print(f"Original shape: {df.shape}")
    print(f"Settings: Cleaning={cleaning_level}, Outlier={outlier_level} ({outlier_method})")

    data = df.copy()

    # --- 1. Identify Column Types ---
    numeric_cols = data.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    print(f"Found {len(numeric_cols)} numeric cols, {len(categorical_cols)} categorical cols.")

    # --- 2. Cleaning Levels (Mutually Exclusive Logic) ---
    
    # All levels start with these basic steps
    if cleaning_level in ['shallow', 'normal', 'deep']:
        # Remove rows where *all* columns are NaN
        data.dropna(how='all', inplace=True)
        # Remove exact duplicate rows
        data.drop_duplicates(inplace=True)
        
        # Strip whitespace from object columns
        for col in categorical_cols:
            if pd.api.types.is_string_dtype(data[col]):
                data[col] = data[col].str.strip()

    if cleaning_level == 'shallow':
        print("Applying SHALLOW cleaning.")
        # Shallow cleaning is already complete from the steps above.
        pass

    elif cleaning_level == 'normal':
        print("Applying NORMAL cleaning.")
        # Standardize case
        for col in categorical_cols:
            if pd.api.types.is_string_dtype(data[col]):
                data[col] = data[col].str.lower()
        
        # Simple Imputation (Median for numeric, Mode for categorical)
        for col in numeric_cols:
            median_val = data[col].median()
            data[col].fillna(median_val, inplace=True)
            
        for col in categorical_cols:
            if not data[col].empty:
                mode_val = data[col].mode()[0]
                data[col].fillna(mode_val, inplace=True)

    elif cleaning_level == 'deep':
        print("Applying DEEP cleaning.")
        # Standardize case
        for col in categorical_cols:
            if pd.api.types.is_string_dtype(data[col]):
                data[col] = data[col].str.lower()
                
        # Advanced Imputation
        # Mode for categorical (KNN doesn't work on strings)
        for col in categorical_cols:
            if not data[col].empty:
                mode_val = data[col].mode()[0]
                data[col].fillna(mode_val, inplace=True)
        
        # KNNImputer for numeric
        if numeric_cols and data[numeric_cols].isnull().any().any():
            print("Applying KNNImputer for numeric NaNs...")
            imputer = KNNImputer(n_neighbors=5)
            data[numeric_cols] = imputer.fit_transform(data[numeric_cols])
        else:
            # Fallback for empty data or no NaNs
            for col in numeric_cols:
                median_val = data[col].median()
                data[col].fillna(median_val, inplace=True)

    # --- 3. Outlier Detection (Applied AFTER imputation) ---
    outlier_indices = pd.Index([])

    if outlier_level == 'normal' and numeric_cols:
        print("Applying NORMAL outlier detection (IQR)...")
        for col in numeric_cols:
            # Skip columns with no variance
            if data[col].nunique() < 2:
                continue
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            col_outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)].index
            outlier_indices = outlier_indices.union(col_outliers)

    elif outlier_level == 'intense' and numeric_cols:
        print("Applying INTENSE outlier detection (Isolation Forest)...")
        # Ensure we only use numeric data for the model
        numeric_data = data[numeric_cols]
        if not numeric_data.empty:
            # Model works better if there are no NaNs (which we handled)
            model = IsolationForest(contamination='auto', random_state=42)
            predictions = model.fit_predict(numeric_data)
            # -1 indicates an outlier
            outlier_indices = data.index[predictions == -1]

    # --- 4. Apply Outlier Handling ---
    if not outlier_indices.empty:
        print(f"Detected {len(outlier_indices)} outlier rows.")
        if outlier_method == 'remove':
            print("Removing outlier rows.")
            data = data.drop(outlier_indices)
        elif outlier_method == 'flag':
            print("Flagging outlier rows with 'is_outlier' column.")
            data['is_outlier'] = 0
            data.loc[outlier_indices, 'is_outlier'] = 1
    else:
        print("No outliers detected or level set to 'none'.")

    # --- 5. Deep Cleaning Transformations (Applied AFTER outlier removal) ---
    if cleaning_level == 'deep':
        print("Applying DEEP transformations (Scaling/Encoding)...")
        
        # Re-identify columns as they might have changed (e.g., 'is_outlier' added)
        current_numeric_cols = data.select_dtypes(include=np.number).columns.tolist()
        if 'is_outlier' in current_numeric_cols:
            # We don't want to scale the outlier flag
            current_numeric_cols.remove('is_outlier')
            
        current_categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()

        # Apply StandardScaler to numeric features
        if current_numeric_cols:
            scaler = StandardScaler()
            data[current_numeric_cols] = scaler.fit_transform(data[current_numeric_cols])
            
        # Apply OneHotEncoder to categorical features
        if current_categorical_cols:
            encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop='first')
            encoded_cols = encoder.fit_transform(data[current_categorical_cols])
            # Create new DataFrame with encoded column names
            encoded_df = pd.DataFrame(encoded_cols, 
                                      columns=encoder.get_feature_names_out(current_categorical_cols), 
                                      index=data.index)
            # Drop original categorical columns and join new encoded ones
            data = data.drop(columns=current_categorical_cols)
            data = pd.concat([data, encoded_df], axis=1)

    print(f"--- Cleaning Complete ---")
    print(f"Final shape: {data.shape}\n")
    return data
