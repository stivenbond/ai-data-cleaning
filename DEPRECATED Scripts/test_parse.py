import re
import json

def parse_line(line):
    # Remove the leading line number and colon if present (from tool output, but let's be safe)
    # Actually the file itself might have it? Let's check the raw content again.
    # The view_file output showed "1: HA,...". 
    # Let's assume the input file has these numbers for now, or I'll handle both.
    
    line = re.sub(r'^\d+:\s*', '', line).strip()
    if not line:
        return []

    # Dictionary words are usually uppercase.
    # We look for uppercase words that are followed by punctuation or metadata-like markers.
    # Pattern: Uppercase word(s) optionally followed by (i, e) or similar, 
    # then maybe metadata, then definition.
    
    # This is a tough one. Let's try splitting by uppercase words that look like headers.
    # A header word is usually at the start of a "sentence-like" block.
    # It's often preceded by a space or start of line.
    
    # Let's try to find all occurrences of words in uppercase (all letters uppercase).
    # We filter out short ones or common abbreviations like "I", "II", "III", "IV".
    
    entries = []
    
    # Possible word patterns:
    # 1. Start of line: WORD
    # 2. After a period/semicolon/quote: WORD
    
    # Split the line into potential segments.
    # Actually, let's try to identify words by looking for uppercase sequences 
    # followed by dictionary-style punctuation like ,", or just ,
    
    # Find all potential word starts
    # We look for sequences of uppercase letters (A-Z, Ç, Ë).
    # We might have spaces in words or multiple words like "HAP PAS HAPI".
    
    # Let's try to split by a regex that matches the start of a new entry.
    # Usually: [SPACE] UPPERCASE_WORD metadata_marker
    
    # Metadata markers: m., f., mb., ndajf., kal., jokal., vety., vetv., pës., pasth., lidh., përem., num., pjesëz.
    markers = [
        r'm\.', r'f\.', r'mb\.', r'ndajf\.', r'kal\.', r'jokal\.', r'vety\.', r'vetv\.', 
        r'pës\.', r'pasth\.', r'lidh\.', r'përem\.', r'num\.', r'pjesëz\.', r'bised\.',
        r'vjet\.', r'spec\.', r'hist\.', r'gjuh\.', r'anat\.', r'zool\.', r'bot\.', r'kim\.',
        r'fiz\.', r'mat\.', r'muz\.', r'let\.', r'arkit\.', r'usht\.', r'gjeogr\.', r'astr\.', r'mit\.',
        r'fer\.', r'krahin\.', r'euf\.', r'iron\.', r'shak\.', r'keq\.', r'mospërf\.', r'thjeshtligj\.', r'libr\.'
    ]
    marker_pattern = '|'.join(markers)
    
    # Entry pattern: (Possible boundary) (UPPERCASE_WORD) (maybe suffix) (marker)
    # Suffixes like "(i, e)", " (i)", " (e)"
    word_pattern = r'(?:^|\s|\.|\"|;|,)\s*([A-ZÇË\s\-]+(?:\([ie,\s]+\))?)\s*(?:,",|,\s*|\s+)(?=' + marker_pattern + r'|\d+\.)'
    
    # This regex is experimental. Let's try a different approach.
    # Many entries start with WORD followed by ,", or just , then metadata.
    
    # Let's just find all matches of uppercase words that are at least 3 chars long or 2 chars known ones.
    # And look what follows them.
    
    matches = list(re.finditer(r'([A-ZÇË]{2,}(?:\s+[A-ZÇË]{2,})*)', line))
    
    results = []
    for i in range(len(matches)):
        start = matches[i].start()
        word = matches[i].group(1).strip()
        
        # Skip if it's a roman numeral like I, II, III
        if word in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']:
            continue
            
        # Get the text between this word and the next word
        end = matches[i+1].start() if i+1 < len(matches) else len(line)
        meaning = line[matches[i].end():end].strip()
        
        # Heuristic: a word is an entry if it's followed by a comma, quote, or specific metadata.
        # Or if it's the very first word in the line.
        is_entry = False
        if i == 0:
            is_entry = True
        else:
            # Check if there's a marker or specific punctuation right after the word
            context = line[matches[i].end() : matches[i].end() + 20]
            if any(re.search(r'\b' + m, context) for m in markers) or context.startswith((',"', ',', '.', ' -')):
                is_entry = True
        
        if is_entry:
            if results:
                # Update previous meaning to end here
                results[-1]['meaning'] = line[results[-1]['meaning_start']:start].strip()
            
            results.append({
                'word': word,
                'meaning_start': matches[i].end(),
                'meaning': meaning # placeholder
            })
            
    if results:
        results[-1]['meaning'] = line[results[-1]['meaning_start']:len(line)].strip()
        
    # Clean up results
    final_entries = []
    for r in results:
        meaning = r['meaning']
        # Clean up leading punctuation from meaning
        meaning = re.sub(r'^[,;\"\.\s\-]+', '', meaning).strip()
        if meaning:
            final_entries.append({"word": r['word'], "meaning": meaning})
            
    return final_entries

def test():
    peek_file = "/Users/stivenbond/Desktop/Engineering/Projects/SWEng/AI-ML/data cleaning/raw_data/Albanian_Dictionary.txt"
    with open(peek_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i in range(10): # test first 10 lines
        print(f"--- Line {i+1} ---")
        entries = parse_line(lines[i])
        for e in entries:
            print(f"WORD: {e['word']}")
            print(f"MEANING: {e['meaning'][:100]}...")
            print("-" * 10)

if __name__ == "__main__":
    test()
