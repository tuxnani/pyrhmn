import pandas as pd
import os
import sys
import argparse

def load_data(filepath: str) -> pd.DataFrame | None:
    """
    Loads data from a file into a pandas DataFrame based on its extension.
    """
    # Get the file extension, converting to lowercase
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    print(f"Attempting to load data from {filepath} (format: {ext})...")
    
    try:
        if ext == '.csv':
            return pd.read_csv(filepath)
        elif ext == '.json':
            # read_json can be tricky. 'records' orient is common,
            # but we'll try without it first to let pandas infer.
            try:
                return pd.read_json(filepath)
            except ValueError:
                print("Initial JSON read failed. Trying orient='records'...")
                return pd.read_json(filepath, orient='records')
        elif ext == '.xml':
            # pd.read_xml requires lxml to be installed
            return pd.read_xml(filepath)
        elif ext == '.parquet':
            # pd.read_parquet requires pyarrow or fastparquet
            return pd.read_parquet(filepath)
        else:
            print(f"Error: Unsupported input file format '{ext}'.", file=sys.stderr)
            return None
            
    except FileNotFoundError:
        print(f"Error: Input file not found at {filepath}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None

def save_data(df: pd.DataFrame, filepath: str, **kwargs) -> bool:
    """
    Saves a DataFrame to a file based on its extension.
    """
    # Get the file extension, converting to lowercase
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    print(f"Attempting to save data to {filepath} (format: {ext})...")
    
    try:
        if ext == '.csv':
            df.to_csv(filepath, index=False)
        elif ext == '.json':
            json_orient = kwargs.get('json_orient', 'records')
            df.to_json(filepath, orient=json_orient, indent=4)
        elif ext == '.xml':
            # pd.to_xml requires lxml
            root_name = kwargs.get('xml_root', 'data')
            row_name = kwargs.get('xml_row', 'row')
            df.to_xml(filepath, index=False, root_name=root_name, row_name=row_name)
        elif ext == '.parquet':
            # pd.to_parquet requires pyarrow or fastparquet
            df.to_parquet(filepath, index=False)
        else:
            print(f"Error: Unsupported output file format '{ext}'.", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error saving {filepath}: {e}", file=sys.stderr)
        return False
        
    return True

def main():
    """
    Main function to parse arguments and run the converter.
    """
    parser = argparse.ArgumentParser(
        description="Multi-format Data Converter (JSON, XML, CSV, Parquet)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("input_file", help="Path to the input file.")
    parser.add_argument("output_file", help="Path for the converted output file.")
    
    # Optional arguments for specific formats
    parser.add_argument(
        "--json_orient",
        default="records",
        help="Orientation for JSON output. E.g., 'records', 'split', 'columns'.\n(default: 'records')"
    )
    parser.add_argument(
        "--xml_root",
        default="data",
        help="The root element name for XML output.\n(default: 'data')"
    )
    parser.add_argument(
        "--xml_row",
        default="row",
        help="The row element name for XML output.\n(default: 'row')"
    )
    
    args = parser.parse_args()
    
    # 1. Load Data
    df = load_data(args.input_file)
    
    if df is None:
        print("Failed to load data. Exiting.")
        sys.exit(1)
        
    print(f"Successfully loaded {len(df)} rows.")
    
    # 2. Save Data
    # Pass optional args to the save function
    success = save_data(
        df,
        args.output_file,
        json_orient=args.json_orient,
        xml_root=args.xml_root,
        xml_row=args.xml_row
    )
    
    if success:
        print(f"\nSuccessfully converted data to {args.output_file}")
    else:
        print("\nFailed to save converted data.")
        sys.exit(1)

if __name__ == "__main__":
    main()
