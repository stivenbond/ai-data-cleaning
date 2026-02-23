# this script will clean the fjalor90.jsonl file and save it to fjalor90_cleaned.jsonl
# from the original jsonl the following should be cleaned:
#   - Remove '\n' from the definition strings
#   - Fully uppercase words should be changed to Capitalized words (e.g. ABA -> Aba)
#   - for each definitions different 'nonsensical' snippets found throughout the definition should be removed, 
# the 'words' usually contain a tilde or a dash before them and are usually found int he begining of the definition string
# or are less than 3 characters long and end in a punctuation mark
import json
import re
import os

def capitalize_albanian(word):
    """Capitalizes the first letter of a word, handling Albanian characters."""
    if not word:
        return word
    # .capitalize() in Python 3 handles Unicode characters correctly.
    return word.capitalize()

def clean_definition(text):
    """
    Cleans the definition string according to the following rules:
    - Replace newlines with spaces.
    - Change fully uppercase words (2+ chars) to Capitalized.
    - Remove 'nonsensical' snippets starting with ~ or -.
    - Remove words < 3 characters long that end in punctuation (e.g., 'm.', 'f.', '1.').
    """
    # 1. Remove \n and replace with space
    text = text.replace('\n', ' ')
    
    # 2. Change fully uppercase words to Capitalized
    # Using regex to find all-caps words (A-Z, Ç, Ë) that are 2 or more characters long.
    text = re.sub(r'\b[A-ZÇË]{2,}\b', lambda m: m.group(0).capitalize(), text)
    
    # 3. Remove 'nonsensical' snippets starting with ~ or -
    # These often represent inflectional endings or OCR artifacts.
    text = re.sub(r'[~-][^\s,.;:!?]*', '', text)
    
    # Cleanup extra spaces created by removals
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Remove words less than 3 characters long ending in a punctuation mark
    words = text.split()
    final_words = []
    for w in words:
        if len(w) < 3 and len(w) > 0 and w[-1] in '.,;:!?':
            continue
        final_words.append(w)
    
    cleaned_text = " ".join(final_words)
    
    # Additional cleanup: fix spaces before commas and double punctuation
    cleaned_text = re.sub(r' ,', ',', cleaned_text)
    cleaned_text = re.sub(r',+', ',', cleaned_text)
    
    return cleaned_text

def process_cleaning(input_path, output_path):
    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")
    
    entry_count = 0
    try:
        with open(input_path, 'r', encoding='utf-8') as in_f, \
             open(output_path, 'w', encoding='utf-8') as out_f:
            for line in in_f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                
                # Capitalize the headword
                entry['word'] = capitalize_albanian(entry['word'])
                
                # Clean the definition/content string
                entry['content'] = clean_definition(entry['content'])
                
                # Save the cleaned entry
                out_f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                entry_count += 1
                if entry_count % 5000 == 0:
                    print(f"Processed {entry_count} entries...")
                    
        print(f"Success! Total entries cleaned: {entry_count}")
        
    except Exception as e:
        print(f"Error during cleaning: {e}")

if __name__ == "__main__":
    # Define paths
    base_dir = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/src/transient_data/script_managed"
    input_file = os.path.join(base_dir, "fjalor90.jsonl")
    output_file = os.path.join(base_dir, "fjalor90_cleaned.jsonl")
    
    if os.path.exists(input_file):
        process_cleaning(input_file, output_file)
    else:
        print(f"Input file not found at {input_file}")
