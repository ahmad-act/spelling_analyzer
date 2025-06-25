import argparse
import json
import sys
from .analyzer import analyze_project

def main():
    parser = argparse.ArgumentParser(description="Analyze the project codebase.")
    parser.add_argument("path", help="Path to the project directory")
    parser.add_argument("-o", "--output", help="Output file (JSON)", default=None)
    parser.add_argument(
        "--fail-on",
        help="Comma-separated sources to consider failure (default: code). Options: code, comment",
        default="code"
    )

    args = parser.parse_args()

    # Parse fail-on sources into a set for easy checking
    fail_sources = set(s.strip().lower() for s in args.fail_on.split(','))

    try:
        report = analyze_project(args.path)

        if report is None:
            print("Error: Analysis failed, no report generated.", file=sys.stderr)
            sys.exit(1)

        # Check if any spelling issue has source in fail_sources
        for file_issues in report.values():
            issues = file_issues.get("pyspellchecker", [])
            for issue in issues:
                if issue.get("source", "").lower() in fail_sources:
                    print(f"Error: Spelling errors found in source '{issue.get('source')}'.", file=sys.stderr)
                    if args.output:
                        with open(args.output, 'w') as f:
                            json.dump(report, f, indent=4)
                        print(f"Report saved to {args.output}")
                    else:
                        print(json.dumps(report, indent=4))
                    sys.exit(1)  # failure exit code

        # No failing issues found
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=4)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=4))

        sys.exit(0)

    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()



# Usage examples:

# Fail only on "code" source errors (default):
#     spelling-analyzer "D:\My Project" --output report.json

# Fail on both "code" and "comment" source errors:
#     spelling-analyzer "D:\My Project" --output report.json --fail-on code,comment