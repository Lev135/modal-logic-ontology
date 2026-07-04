import os
import sys
import re
import csv

# Regex to match refinement type usage in Soufflé source files: $type("value")
SUGAR_DL_REGEX = re.compile(r'\$([a-zA-Z_]\w*)\s*\(\s*"([^"]+)"\s*\)')

# Regex to find $type markers within CSV header columns (e.g., "id: $logic")
HEADER_MARKER_REGEX = re.compile(r'\$([a-zA-Z_]\w*)')

# Regex to extract the raw value 'vvv' from lines like '$type(vvv)' in registry files
REGISTRY_LINE_REGEX = re.compile(r'^\$?([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*\(\s*(.*?)\s*\)\s*$')

def load_declared_invariants(declared_dir, stats):
    """
    Loads master registries from DECLARED_DIR.
    Counts the total number of declared unique valid constants.
    """
    registry = {}
    if not os.path.exists(declared_dir):
        print(f"Error: DECLARED_DIR '{declared_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    for file in os.listdir(declared_dir):
        if file.endswith('.csv'):
            # Strip extension and remove potential leading '$' to get the clean type name
            type_name = os.path.splitext(file)[0].lstrip('$')
            registry[type_name] = set()
            path = os.path.join(declared_dir, file)

            with open(path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    match = REGISTRY_LINE_REGEX.match(clean_line)
                    if match:
                        value = match.group(2).strip()  # group(2) captures the raw value inside the brackets
                        registry[type_name].add(value)
                        stats['declarations'] += 1
                    else:
                        print(f"Warning ({file}:{line_num}): "
                              f"Line '{clean_line}' does not match expected format '$type(value)'. Skipped.",
                              file=sys.stderr)
    return registry


def check_dl_file_invariants(path, rel_path, registry, stats):
    """Parses a single .dl file and flags undeclared refinement type constants."""
    stats['dl_files'] += 1

    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            for match in SUGAR_DL_REGEX.finditer(line):
                type_name, value = match.group(1), match.group(2)
                stats['literals'] += 1

                if type_name not in registry:
                    print(f"{rel_path}:{line_num}: Unknown refinement type '${type_name}' used.", file=sys.stderr)
                    stats['errors'] += 1
                elif value not in registry[type_name]:
                    print(f"{rel_path}:{line_num}: Undefined constant '{value}' for type '${type_name}'.", file=sys.stderr)
                    stats['errors'] += 1


def check_csv_file_invariants(path, rel_path, registry, stats):
    """Parses a single data .csv file and ensures column contents match type constraints."""
    stats['csv_files'] += 1

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return  # Skip empty files silently

        tracked_columns = {}
        for idx, col in enumerate(header):
            h_match = HEADER_MARKER_REGEX.search(col)
            if h_match:
                t_name = h_match.group(1)
                if t_name in registry:
                    tracked_columns[idx] = t_name
                else:
                    print(f"{rel_path}:1 Header column '{col}' references unknown type '${t_name}'.", file=sys.stderr)
                    stats['errors'] += 1

        if not tracked_columns:
            return  # No refinement columns found, skip content validation

        for line_num, row in enumerate(reader, 2):
            if not row:
                continue

            for idx, type_name in tracked_columns.items():
                if idx >= len(row):
                    continue

                value = row[idx].strip()
                stats['literals'] += 1

                if value not in registry[type_name]:
                    print(f"{rel_path}:{line_num}: Data violation in column '{header[idx]}'. Value '{value}' is not registered as a valid '{type_name}'.", file=sys.stderr)
                    stats['errors'] += 1


def run_invariant_checker(source_dir, declared_dir):
    """Performs a single-pass directory traversal and collects verification statistics."""
    # Global metrics dictionary
    stats = {
        'declarations': 0,
        'dl_files': 0,
        'csv_files': 0,
        'literals': 0,
        'errors': 0
    }

    registry = load_declared_invariants(declared_dir, stats)
    abs_declared_dir = os.path.abspath(declared_dir)

    for root, _, files in os.walk(source_dir):
        if os.path.abspath(root) == abs_declared_dir:
            continue

        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, source_dir)

            if file.endswith('.dl'):
                check_dl_file_invariants(path, rel_path, registry, stats)
            elif file.endswith('.csv'):
                check_csv_file_invariants(path, rel_path, registry, stats)

    # Output concise statistics line with total errors and declarations count
    print(f"Checking completed. Found {stats['errors']} errors. "
          f"Verified {stats['literals']} literals against {stats['declarations']} master declarations "
          f"across {stats['dl_files']} .dl and {stats['csv_files']} .csv files.")

    if stats['errors'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    SOURCE_DIR = "src"
    DECLARED_DIR = "out/declared"

    run_invariant_checker(SOURCE_DIR, DECLARED_DIR)
