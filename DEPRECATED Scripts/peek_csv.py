import csv
import os
import sys

# Increase the limit for large fields
csv.field_size_limit(sys.maxsize)

files = [
    "raw_data/Fjalor i shqipes se sotme.csv",
    "raw_data/Fjalori sinonimik i gjuhes shqipe.csv",
    "raw_data/albanian_dictionary_dataset1980.csv",
    "raw_data/fjalori-i-drejtshkrimit.csv",
    "raw_data/kushtetuta.csv"
]

for file_path in files:
    print(f"\n--- Analyzing: {file_path} ---")
    if not os.path.exists(file_path):
        print("File not found")
        continue
        
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            print(f"Headers: {reader.fieldnames}")
            for i, row in enumerate(reader):
                if i >= 1: # Just one row is enough to see the structure
                    break
                print(f"\nRow {i+1}:")
                for key, value in row.items():
                    val_str = str(value).replace('\n', ' ')[:500]
                    print(f"  {key}: {val_str}...")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
