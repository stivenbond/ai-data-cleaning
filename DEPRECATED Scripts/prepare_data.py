import re
import json
import os
import csv
import sys

# Increase the limit for large fields
csv.field_size_limit(sys.maxsize)

def parse_txt_line(line):
    """Original parser for Albanian_Dictionary.txt"""
    match = re.match(r'^([^,"]+),"(.*)$', line)
    if not match:
        return None
    
    word = match.group(1).strip()
    content = match.group(2).strip()
    
    if content.endswith('"'):
        content = content[:-1]
        
    return {
        "word": word,
        "content": content
    }

def segment_text(text):
    """
    Heuristic to segment large OCR blocks into dictionary-like entries.
    Look for headwords at the start of lines or after double spaces.
    """
    # Pattern 1: Uppercase headwords (classic dictionary)
    # Pattern 2: Lowercase headwords at start of line (synonym dictionary)
    # We look for a word followed by a space and then some definition markers
    
    # Split by lines first to respect physical layout of dictionary
    lines = text.split('\n')
    entries = []
    current_word = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a potential headword
        # Headword candidate: First word(s) before a space, if followed by definition-like text
        # Or a word in ALL CAPS
        
        # Regex for headword: 
        # - Starts at beginning of line
        # - Consists of one or more words
        # - Followed by a comma, dash, space + abbreviation, or just a space and then lowercase
        match = re.match(r'^([A-ZÇËa-zçë-]{2,}(?:\s+[A-ZÇËa-zçë-]{2,})?)(?:,|\.|\s+-|\s+[a-z]{1,3}\.)\s*(.*)$', line)
        
        if match:
            # If we were already building an entry, save it
            if current_word and current_content:
                entries.append({"word": current_word, "content": " ".join(current_content)})
            
            current_word = match.group(1).strip()
            current_content = [match.group(2).strip()]
        else:
            if current_word:
                current_content.append(line)
            elif len(line) > 50:
                # If no word yet, but line is long, maybe it's orphan text
                entries.append({"word": "TEKST", "content": line})
                
    # Save last entry
    if current_word and current_content:
        entries.append({"word": current_word, "content": " ".join(current_content)})
        
    return entries

def process_file(file_path, output_dir):
    base_name = os.path.basename(file_path).replace(".csv", "").replace(".txt", "").replace(" ", "_").lower()
    cpt_output = os.path.join(output_dir, f"{base_name}_cpt.txt")
    sft_output = os.path.join(output_dir, f"{base_name}_sft.jsonl")
    
    print(f"Processing {file_path}...")
    
    entries = []
    
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = parse_txt_line(line.strip())
                if entry:
                    entries.append(entry)
    elif file_path.endswith(".csv"):
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get('cleaned_text', row.get('raw_text', ''))
                if not text:
                    continue
                
                # If it's the Constitution, we process differently
                if "kushtetuta" in file_path.lower():
                    # Split by Articles
                    articles = re.split(r'(Neni\s+\d+)', text)
                    for i in range(1, len(articles), 2):
                        title = articles[i].strip()
                        content = articles[i+1].strip() if i+1 < len(articles) else ""
                        if content:
                            entries.append({"word": title, "content": content})
                else:
                    # Dictionary-like segmentation
                    segmented = segment_text(text)
                    entries.extend(segmented)
                    
    if not entries:
        print(f"No entries found for {file_path}")
        return

    # Write CPT
    with open(cpt_output, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry['word']}: {entry['content']}\n")
            
    # Write SFT
    with open(sft_output, "w", encoding="utf-8") as f:
        for entry in entries:
            if len(entry['content']) < 10:
                continue
                
            if "kushtetuta" in file_path.lower():
                instruction = f"Çfarë thotë {entry['word']} i Kushtetutës së Shqipërisë?"
            else:
                instruction = f"Çfarë do të thotë fjala shqipe '{entry['word']}'?"
                
            response = f"{entry['word']} ka këtë kuptim: {entry['content']}"
            
            sft_item = {
                "instruction": instruction,
                "input": "",
                "output": response
            }
            f.write(json.dumps(sft_item, ensure_ascii=False) + "\n")
            
    print(f"  Generated {len(entries)} entries.")
    print(f"  CPT: {cpt_output}")
    print(f"  SFT: {sft_output}")

def main():
    raw_dir = "raw_data"
    output_dir = "cleaned_data"
    os.makedirs(output_dir, exist_ok=True)
    
    files = [
        "raw_data/Albanian_Dictionary.txt",
        "raw_data/Fjalor i shqipes se sotme.csv",
        "raw_data/Fjalori sinonimik i gjuhes shqipe.csv",
        "raw_data/albanian_dictionary_dataset1980.csv",
        "raw_data/fjalori-i-drejtshkrimit.csv",
        "raw_data/kushtetuta.csv"
    ]
    
    for f in files:
        if os.path.exists(f):
            process_file(f, output_dir)
        else:
            print(f"File not found: {f}")

if __name__ == "__main__":
    main()
