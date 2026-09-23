# subjectsBuilder

This repository contains two small Python converters for turning subject data into nested JSON trees.

## What each file does

| File | Purpose |
| --- | --- |
| `csvltojson.py` | Reads `SN-T_v2.csv` and builds a nested JSON tree from the `Level N` / `Level N ID` columns. Only rows with `Discipline = TRUE` are included. |
| `responsetojson.py` | Reads `response.json` and rebuilds it into a parent/child tree using `parentIds`. The output is trimmed to 5 levels deep. |
| `test_csvltojson.py` | Unit tests for `csvltojson.py` using `version-small.csv` as a fixture. |
| `SN-T_v2.csv` | Main CSV input expected by `csvltojson.py`. |
| `version-small.csv` | Smaller sample CSV used by the tests. |
| `response.json` | Example API-style JSON input for `responsetojson.py`. |
| `output.json` | Generated output from `csvltojson.py`. |
| `response-output.json` | Generated output from `responsetojson.py`. |
| `subjects-example.json` | Example subject payload in the source format. |

## How `csvltojson.py` works

The script:

1. Loads `SN-T_v2.csv` with `cp1252` encoding.
2. Checks the `Discipline` column and keeps only rows where it is `TRUE`.
3. Walks through `Level 1` to `Level 15` and their matching `Level N ID` columns.
4. Builds a nested structure like:

```json
{
  "data": [
    {
      "name": "Physical Sciences",
      "id": "2867",
      "description": "...",
      "sublevels": []
    }
  ]
}
```

If a child row is included but its parent row has `Discipline = FALSE`, the script still keeps the child and prints a warning.

## How `responsetojson.py` works

The script:

1. Loads `response.json`.
2. Creates a node for each item in `data`.
3. Uses `parentIds` to attach each node to its parent.
4. Puts items without parents at the root.
5. Trims the final tree to 5 levels.
6. Writes the result to `response-output.json`.

## Requirements

- Python 3
- `pandas`

Install the dependency with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas
```

## How to use it

### Convert the CSV input

Make sure your source file is named `SN-T_v2.csv` and is in the repository root, then run:

```bash
python3 csvltojson.py
```

This creates `output.json`.

### Convert the JSON response input

Make sure `response.json` is in the repository root, then run:

```bash
python3 responsetojson.py
```

This creates `response-output.json`.

## Running the tests

The tests expect a virtual environment at `venv/` with `pandas` installed.

```bash
source venv/bin/activate
python3 -m unittest test_csvltojson.py
```
