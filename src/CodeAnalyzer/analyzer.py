# src/CodeAnalyzer/analyzer.py

import os
from src.CodeReview.pyspellchecker_runner import run_pyspellchecker
import logging

from src.logger_config import setup_logging
setup_logging()

SUPPORTED_EXTENSIONS = ('.py', '.cs', '.vb', '.js', '.ts')

def analyze_file(file_path):
    """Run all tools on one file and return results."""
    results = {}
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Add individual tool-level error handling
        try:
            results['pyspellchecker'] = run_pyspellchecker(file_path)
        except Exception as e:
            logging.error(f"pyspellchecker failed for {file_path}: {e}")
            results['pyspellchecker'] = {'error': f'pyspellchecker failed: {str(e)}'}

    except Exception as e:
        logging.error(f"Failed to analyze file {file_path}: {e}")
        results['error'] = str(e)

    return results

def analyze_project(path):
    """
    Analyze all supported source files in `path`.

    Args:
        path (str): Root folder of the project.

    Returns:
        dict: Report with per-file results.
    """
    report = {}
    if not os.path.isdir(path):
        return {'error': f"Provided path is not a directory: {path}"}

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(SUPPORTED_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                try:
                    report[rel_path] = analyze_file(full_path)
                except Exception as e:
                    logging.error(f"Unexpected error analyzing {rel_path}: {e}")
                    report[rel_path] = {'error': str(e)}
    return report
