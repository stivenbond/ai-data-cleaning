import re
import json

def parse_line(line):
    # Remove the leading line number and colon if present
    line_content = re.sub(r'^\d+:\s*', '', line).strip()
    if not line_content:
        return []

    # Markers that usually follow a dictionary word entry
    # Added \b to ensure they are whole words and not parts of other words
    markers = [
        r'm\.', r'f\.', r'mb\.', r'ndajf\.', r'kal\.', r'jokal\.', r'vety\.', r'vetv\.', 
        r'pës\.', r'pasth\.', r'lidh\.', r'përem\.', r'num\.', r'pjesëz\.', r'bised\.',
        r'vjet\.', r'spec\.', r'hist\.', r'gjuh\.', r'anat\.', r'zool\.', r'bot\.', r'kim\.',
        r'fiz\.', r'mat\.', r'muz\.', r'let\.', r'arkit\.', r'usht\.', r'gjeogr\.', r'astr\.', r'mit\.',
        r'fer\.', r'krahin\.', r'euf\.', r'iron\.', r'shak\.', r'keq\.', r'mospërf\.', r'thjeshtligj\.', r'libr\.'
    ]
    marker_pattern = r'(?:' + '|'.join(markers) + r')'
    
    # Pattern for a dictionary entry:
    # 1. Start boundary: ^, space, period, etc.
    # 2. Uppercase word: Starts with A-ZÇË, contains A-ZÇË, spaces, hyphens.
    # 3. Optional suffix like (i, e)
    # 4. Optional punctuation
    # 5. Followed by a marker
    
    # Refined word pattern: Must start with a letter, no leading hyphen.
    word_pattern = r'([A-ZÇË][A-ZÇË\s\-\.\']*(?:\s*\([^)]+\))?)'
    
    # We use a non-greedy word match to avoid swallowing the whole line
    entry_start_regex = r'(?:^|\s|\.|\"|;)\s*' + word_pattern + r'\s*(?:,",|,\s*|\s+)?(?=' + marker_pattern + r')'
    
    matches = list(re.finditer(entry_start_regex, line_content))
    
    # If no matches found with marker, try to at least take the first word of the line if it's uppercase
    if not matches:
        first_word_match = re.match(r'^([A-ZÇË][A-ZÇË\s\-\.\']*(?:\s*\([^)]+\))?)', line_content)
        if first_word_match:
            word = first_word_match.group(1).strip()
            # Basic validation: not just a single letter (except maybe 'E', 'A' but let's say >=2), 
            # not a roman numeral, etc.
            if len(word) >= 2 and not re.match(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)$', word):
                # Mock a match object
                class MockMatch:
                    def __init__(self, w, s, e):
                        self._w = w
                        self._s = s
                        self._e = e
                    def group(self, i): return self._w
                    def start(self): return self._s
                    def end(self): return self._e
                matches = [MockMatch(word, first_word_match.start(), first_word_match.end())]

    entries = []
    for i, match in enumerate(matches):
        word = match.group(1).strip()
        # Clean up word
        word = re.sub(r'[,;\"\s\-]+$', '', word).strip()
        
        # Validation: avoid common metadata snippets that might look like words
        if word in ['ET', 'IT', 'TE', 'EDHE', 'ME', 'SË', 'NJË', 'OSE', 'KU', 'NË', 'NGA']:
            continue
            
        start = match.start()
        meaning_start = match.end()
        # The meaning for this word ends where the next word starts
        next_entry_start = matches[i+1].start() if i+1 < len(matches) else len(line_content)
        
        meaning = line_content[meaning_start:next_entry_start].strip()
        # Clean up leading punctuation from meaning
        meaning = re.sub(r'^[,;\"\.\s\-]+', '', meaning).strip()
        
        if word and meaning:
            entries.append({"word": word, "meaning": meaning})
            
    return entries

def process_dictionary(input_path, output_path):
    all_entries = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_entries = parse_line(line)
            all_entries.extend(line_entries)
            
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            # Final cleanup of meaning: sometimes it picks up the word itself at the end if the split was slightly off
            # But the current logic is mostly okay.
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return len(all_entries)

if __name__ == "__main__":
    input_file = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/raw_data/Albanian_Dictionary.txt"
    output_file = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/Albanian_Dictionary.jsonl"
    
    count = process_dictionary(input_file, output_file)
    print(f"Processed {count} entries.")
