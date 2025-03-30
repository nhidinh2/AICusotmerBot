import os
import pandas as pd
import csv

def clean_quotes(value):
    """Clean and properly format string fields."""
    if isinstance(value, str):
        # Remove extra quotes and strip leading/trailing spaces
        value = value.strip().replace('""', '"').replace('"', '')
        # Ensure proper quoting for fields with commas or quotes
        if ',' in value or '"' in value:
            value = f'"{value}"'
    return value

def convert_parquet_to_csv(parquet_dir, csv_dir):
    """Convert all Parquet files in the specified directory to CSV format."""
    # Convert all Parquet files to CSV
    for file_name in os.listdir(parquet_dir):
        if file_name.endswith('.parquet'):
            parquet_file = os.path.join(parquet_dir, file_name)
            csv_file = os.path.join(csv_dir, file_name.replace('.parquet', '.csv'))
            
            # Load the Parquet file
            df = pd.read_parquet(parquet_file)
            
            # Clean quotes in string fields
            for column in df.select_dtypes(include=['object']).columns:
                df[column] = df[column].apply(clean_quotes)
            
            # Save to CSV
            df.to_csv(csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
            print(f"Converted {parquet_file} to {csv_file} successfully.")

    print("All Parquet files have been converted to CSV.")

def main():
    # Define the directory containing Parquet files
    parquet_dir = '/Users/dinhuyennhi/untitled folder/output/20240805-112918/artifacts'
    csv_dir = '/Users/dinhuyennhi/untitled folder/neo4j-community-5.21.2/import'
    convert_parquet_to_csv(parquet_dir, csv_dir)

if __name__ == '__main__':
    main()


