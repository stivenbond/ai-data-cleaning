import csv
import sys

csv.field_size_limit(sys.maxsize)

files_to_inspect = {
    "raw_data/Fjalori sinonimik i gjuhes shqipe.csv": 5,
    "raw_data/fjalori-i-drejtshkrimit.csv": 0
}

for file_path, row_idx in files_to_inspect.items():
    print(f"\n--- {file_path} (Row {row_idx}) ---")
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i == row_idx:
                text = row['cleaned_text']
                print(text[5000:7000]) # Peek into the middle of the text
                break
