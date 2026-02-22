import re
import json
import os
import pandas as pd

# MANUAL Divide preface and Epilogue if present - DONE
# the manually cleaned file is present in ./src/transient_data/manually_cleaned/albanian_dictionary_1980.txt

def clean_definition(text):
    """
    Cleans grammatical and other annotations from the definition text.
    """
    # Markers to remove from the content (grammatical, category, and historical details)
    markers = [
        r'm\.', r'f\.', r'mb\.', r'ndajf\.', r'kal\.', r'jokal\.', r'vety\.', r'vetv\.',
        r'pës\.', r'pasth\.', r'lidh\.', r'përem\.', r'num\.', r'pjesëz\.', r'bised\.',
        r'vjet\.', r'spec\.', r'hist\.', r'gjuh\.', r'anat\.', r'zool\.', r'bot\.', r'kim\.',
        r'fiz\.', r'mat\.', r'muz\.', r'let\.', r'arkit\.', r'usht\.', r'gjeogr\.', r'astr\.', r'mit\.',
        r'fer\.', r'krahin\.', r'euf\.', r'iron\.', r'shak\.', r'keq\.', r'mospërf\.', r'thjeshtligj\.', r'libr\.',
        r'sh\.', r'vet\.', r'nj\.', r'fig\.', r'fet\.', r'ek\.', r'filoz\.', r'gjeol\.', r'gjeod\.', r'art\.', r'logj\.',
        r'pës\.', r'përmb\.', r'det\.', r'usht\.', r'biol\.', r'veter\.', r'etnogr\.', r'Hdh\.', r'n\.'
    ]
    
    # Match markers that are either at the start or preceded by space/punctuation
    # and followed by space or punctuation
    marker_pattern = r'(?:^|[\s\.,;])(?:' + '|'.join(markers) + r')(?=[\s\.,;]|$)'
    
    # Remove Roman numerals like I., II. at the start of a definition block
    text = re.sub(r'^(?:[IVX]+\.)\s*', '', text)
    
    # Repeatedly remove markers and leading punctuation/whitespace
    iteration_text = text
    while True:
        # Remove markers
        iteration_text = re.sub(marker_pattern, ' ', iteration_text).strip()
        # Remove leading punctuation (—, -, ., ,) that usually precedes the text
        iteration_text = re.sub(r'^[\s\.,;—\-]+', '', iteration_text).strip()
        # Remove repeated numbers if they occur at the very start
        iteration_text = re.sub(r'^[1-9]\.\s*', '', iteration_text).strip()
        
        if iteration_text == text:
            break
        text = iteration_text
        
    return text

def run_pipeline():
    # Paths (Absolute paths based on environment context)
    base_dir = '/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning'
    input_path = os.path.join(base_dir, 'src/transient_data/manually_cleaned/albanian_dictionary_1980.txt')
    output_jsonl = os.path.join(base_dir, 'cleaned_data/albanian_dictionary_1980.jsonl')
    output_parquet = os.path.join(base_dir, 'src/parquet/albanian_dictionary_1980.parquet')
    
    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    
    # 1. Read file and combine into a long string
    print(f"Reading {input_path}...")
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        # Step: Remove new lines and combine into a long string
        text = " ".join(line.strip() for line in f if line.strip())
        text = re.sub(r'\s+', ' ', text)
    
    # 2. Parse the string for every uppercase word and divide into new entries
    # Heuristic: An entry starts with one or more uppercase words followed by a marker or a number.
    # Markers to look for as anchors
    markers_list = [
        'm.', 'f.', 'mb.', 'ndajf.', 'kal.', 'jokal.', 'vety.', 'vetv.',
        'pës.', 'pasth.', 'lidh.', 'përem.', 'num.', 'pjesëz.', 'bised.',
        'vjet.', 'spec.', 'hist.', 'gjuh.', 'anat.', 'zool.', 'bot.', 'kim.',
        'fiz.', 'mat.', 'muz.', 'let.', 'arkit.', 'usht.', 'gjeogr.', 'astr.', 'mit.',
        'fer.', 'krahin.', 'euf.', 'iron.', 'shak.', 'keq.', 'mospërf.', 'thjeshtligj.', 'libr.',
        'sh.', 'vet.', 'nj.', 'fig.', 'fet.', 'ek.', 'filoz.', 'gjeol.', 'gjeod.', 'art.', 'logj.',
        'pës.', 'përmb.', 'det.', 'usht.', 'biol.', 'veter.', 'etnogr.', 'Hdh.'
    ]
    marker_regex = r'|'.join(re.escape(m) for m in markers_list)
    
    # Regex: Look for Uppercase sequences that look like headwords.
    # EDGE CASE handle: derivations in uppercase are kept within the headword sequence.
    entry_start_regex = r'(?:^|\s)([A-ZÇË]{1,}(?:[,\.\-\s][A-ZÇË]+)*)(?=\s+(?:' + marker_regex + r'|I{1,3}\.|[1-9]\.))'
    
    matches = list(re.finditer(entry_start_regex, text))
    print(f"Found {len(matches)} potential dictionary entries.")
    
    entries = []
    for i in range(len(matches)):
        start_pos = matches[i].start()
        # The next entry starts where the next match begins
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
        
        raw_headword = matches[i].group(1).strip()
        raw_content = text[matches[i].end():end_pos].strip()
        
        # Extract main word (e.g., from "ABA,-JA" take "ABA")
        word = re.split(r'[,;\-\s\.]', raw_headword)[0].strip()
        
        if not word:
            continue
            
        # 3. Clean annotations and group definitions
        # Split content into definitions by numbers "1. ", "2. ", etc.
        # Capturing group in split includes the delimiter in the result list
        parts = re.split(r'\s+([1-9]\.)\s+', " " + raw_content)
        
        defs = []
        if len(parts) <= 1:
            # Single definition entry
            d = clean_definition(raw_content)
            if d: defs.append(d)
        else:
            # Multi-definition entry. parts = ["", "1.", "Def1", "2.", "Def2", ...]
            for j in range(2, len(parts), 2):
                d = clean_definition(parts[j])
                if d: defs.append(d)
        
        if word and defs:
            entries.append({
                "word": word,
                "definitions": defs
            })

    # 4. Convert to JSONL
    print(f"Saving to JSONL: {output_jsonl}")
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
    # 5. Add to instruction format and store as parquet file
    # Format: instruction (Q), input (empty), output (A)
    print(f"Converting to instruction format and saving Parquet: {output_parquet}")
    parquet_data = []
    for entry in entries:
        word = entry['word']
        all_defs = " ".join(entry['definitions'])
        
        parquet_data.append({
            "instruction": f"Çfarë do të thotë fjala shqipe '{word}'?",
            "input": "",
            "output": f"{word} do të thotë: {all_defs}"
        })
        
    if parquet_data:
        df = pd.DataFrame(parquet_data)
        df.to_parquet(output_parquet, index=False)
        print(f"Successfully processed {len(entries)} entries.")
    else:
        print("No entries were found to process.")

if __name__ == "__main__":
    # The script is ready for execution
    run_pipeline()
    pass