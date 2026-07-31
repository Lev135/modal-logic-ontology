import sys
import re
import csv
from pathlib import Path
from collections import defaultdict

source_path = Path("src")
declared_path = Path("out/declared")

def load_declared(stats):
  registry = defaultdict(set)
  for csv_path in declared_path.rglob("*.csv"):
    with csv_path.open() as file:
      reader = csv.reader(file)
      type_name = csv_path.stem
      for decl, in reader:
        registry[type_name].add(decl)
        stats['declarations'] += 1
  return dict(registry)

def check_csvs(registry, stats):
  for csv_path in source_path.rglob("*.csv"):
    stats['csv_files'] += 1
    with csv_path.open() as file:
      reader = csv.DictReader(file)

      if not reader.fieldnames:
        continue

      columns_to_check = {}

      for header in reader.fieldnames:
        parts = header.split(':')
        if len(parts) != 2:
          print(f"Err {csv_path}:1. Incorrect header '{header}'. Must be 'something:type'")
          stats['errors'] += 1
          continue
        type_name = parts[1].strip()
        if not type_name:
          continue
        if type_name not in registry:
          print(f"Err {csv_path}:1. Type '{type_name}' has no corresponding .csv in {declared_path}")
          stats['errors'] += 1
          continue
        columns_to_check[header] = type_name

      if not columns_to_check:
        continue

      for row_idx, row in enumerate(reader, start=2):
        for header, type_name in columns_to_check.items():
          value = row[header]
          if value not in registry[type_name]:
            print(f"Err {csv_path}:{row_idx}. '{value}' is not a valid '{type_name}'")
            stats['errors'] += 1
          stats['literals'] += 1

def check_dls(registry, stats):
  pattern = re.compile(r'@([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\"([^\"]*)\"\s*\)')

  for dl_path in source_path.rglob("*.dl"):
    stats['dl_files'] += 1
    with dl_path.open() as file:
      for row_idx, line in enumerate(file, start=1):
        line = line.strip()
        if line.startswith('//'):
          continue
        for match in pattern.finditer(line):
          identifier = match.group(1)
          string_literal = match.group(2)

          if identifier not in registry:
            continue

          if string_literal not in registry[identifier]:
            print(f"Err {dl_path}:{row_idx}. '{string_literal}' is not a valid '{identifier}'")
            stats['errors'] += 1

          stats['literals'] += 1

if __name__ == "__main__":
    stats = {
        'declarations': 0,
        'dl_files': 0,
        'csv_files': 0,
        'literals': 0,
        'errors': 0
    }

    registry = load_declared(stats)

    check_csvs(registry, stats)
    check_dls(registry, stats)

    print(f"Checking completed. Found {stats['errors']} errors. "
          f"Verified {stats['literals']} literals against {stats['declarations']} master declarations "
          f"across {stats['dl_files']} .dl and {stats['csv_files']} .csv files.")

    if stats['errors'] > 0:
        sys.exit(1)
