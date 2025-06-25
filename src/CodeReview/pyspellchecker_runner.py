from spellchecker import SpellChecker
import re
from typing import List, Dict
import logging

from src.logger_config import setup_logging
setup_logging()

def run_pyspellchecker(file_path: str) -> List[Dict]:
    spell = SpellChecker()
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logging.error(f"Failed to read file {file_path}: {e}")
        return [{"error": f"Could not read file: {e}"}]

    # --- Process comments line by line ---
    for line_num, line in enumerate(content.splitlines(), 1):
        try:
            comment_match = re.search(r'#(.*)', line)
            if comment_match:
                comment_text = comment_match.group(1)
                words = re.findall(r'\b[a-zA-Z]+\b', comment_text)
                misspelled = spell.unknown(words)
                for word in misspelled:
                    issues.append({
                        "file": file_path,
                        "line": line_num,
                        "word": word,
                        "suggestion": spell.correction(word),
                        "source": "comment"
                    })
        except Exception as e:
            logging.error(f"Error processing comment on line {line_num} in {file_path}: {e}")
            issues.append({
                "file": file_path,
                "line": line_num,
                "error": f"Failed to process comment: {e}"
            })

    # --- Process string literals globally (including multiline) ---
    try:
        # regex to capture all string literals, including triple quotes
        string_regex = r'(?:\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\'|\"(.*?)\"|\'(.*?)\')'
        string_matches = re.findall(string_regex, content, re.DOTALL)

        # For line number attribution, split file into lines to locate where strings appear
        lines = content.splitlines()

        for match_group in string_matches:
            string_text = " ".join(filter(None, match_group))
            words = re.findall(r'\b[a-zA-Z]+\b', string_text)
            misspelled = spell.unknown(words)

            # Find approximate line number of the string by searching string_text in content
            # Use content.find to get offset, then count '\n' to get line number
            offset = content.find(string_text)
            line_num = content[:offset].count('\n') + 1 if offset != -1 else 1

            for word in misspelled:
                issues.append({
                    "file": file_path,
                    "line": line_num,
                    "word": word,
                    "suggestion": spell.correction(word),
                    "source": "code"
                })
    except Exception as e:
        logging.error(f"Error processing string literals in {file_path}: {e}")
        issues.append({
            "file": file_path,
            "error": f"Failed to process string literals: {e}"
        })

    return issues
