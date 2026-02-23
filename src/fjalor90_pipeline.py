import json
import re
import os

def extract_entries(input_file):
    """
    Generator that parses the dictionary file and yields entries as dictionaries.
    A new entry is identified by a line starting with a fully uppercase word.
    """
    # Regex to identify a headword at the start of a line.
    # It matches one or more uppercase Albanian letters (A-Z, Ç, Ë).
    # We use a word boundary or specific punctuation to ensure it's a word.
    headword_regex = re.compile(r'^([A-ZÇË]+)')
    
    current_word = None
    current_content = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            
            # Skip empty lines at the very beginning
            if not stripped and current_word is None:
                continue
            
            # Check if this line starts a new entry
            is_new_entry = False
            word_found = None
            
            match = headword_regex.match(stripped)
            if match:
                word_found = match.group(1)
                remainder = stripped[len(word_found):]
                
                # Heuristic to distinguish headwords from sentence starts:
                # 1. Headwords are usually followed by space, punctuation (,~./), or end of line.
                # 2. We exclude cases where the next char is lowercase (which would mean the word is CamelCase).
                #    But our regex [A-ZÇË]+ already only matches uppercase part.
                #    So if stripped is "Abaci", match is "A", remainder is "baci".
                #    In this case, remainder[0] is 'b' (lowercase), so it's not a headword entry.
                if not remainder:
                    is_new_entry = True
                elif remainder[0] in ' ,.~/()[]-I123456789:;':
                    # If it's a single letter 'A' followed by space, it's a headword "A".
                    # If it's "ABA," it's "ABA".
                    # We also allow Roman numerals (I, II...) or digits if they follow the headword.
                    is_new_entry = True
                else:
                    # e.g. "Abëcë" -> match is "A", remainder is "bëcë". remainder[0] is 'b'.
                    # This is not a new headword entry in our format.
                    is_new_entry = False

            if is_new_entry:
                # Yield the previous entry if it exists
                if current_word:
                    yield {
                        'word': current_word,
                        'content': "".join(current_content).strip()
                    }
                current_word = word_found
                current_content = [line]
            else:
                # Continue previous entry
                if current_word:
                    current_content.append(line)
                else:
                    # Handle lines before the first headword (e.g. intro text)
                    pass
                    
    # Yield the last entry
    if current_word:
        yield {
            'word': current_word,
            'content': "".join(current_content).strip()
        }

def process_file(input_path, output_path):
    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")
    
    entry_count = 0
    try:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for entry in extract_entries(input_path):
                out_f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                entry_count += 1
                if entry_count % 5000 == 0:
                    print(f"Processed {entry_count} entries...")
        
        print(f"Success! Total entries processed: {entry_count}")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    # Define paths
    input_file = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/src/transient_data/manually_cleaned/fjalor90.txt"
    output_file = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/src/transient_data/script_managed/fjalor90.jsonl"
    
    process_file(input_file, output_file)
