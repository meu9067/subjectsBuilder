import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).parent
SCRIPT = PROJECT_DIR / "csvltojson.py"
DUMMY_CSV = PROJECT_DIR / "version-small.csv"
INPUT_CSV = "SN-T_v2.csv"


def all_nodes(nodes):
    for node in nodes:
        yield node
        yield from all_nodes(node["sublevels"])


class CsvToJsonTests(unittest.TestCase):
    def run_converter(self, modify_csv=None):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        work_dir = Path(temp_dir.name)
        shutil.copy(SCRIPT, work_dir / SCRIPT.name)

        csv_path = work_dir / INPUT_CSV
        if modify_csv is None:
            shutil.copy(DUMMY_CSV, csv_path)
        else:
            df = pd.read_csv(DUMMY_CSV, encoding="cp1252")
            modify_csv(df)
            df.to_csv(csv_path, index=False, encoding="cp1252")

        result = subprocess.run(
            [str(PROJECT_DIR / "venv/bin/python"), SCRIPT.name],
            cwd=work_dir,
            text=True,
            capture_output=True,
            check=True,
        )
        output = json.loads((work_dir / "output.json").read_text(encoding="utf-8"))
        return result, output

    def test_converts_dummy_csv_to_valid_nested_json(self):
        result, output = self.run_converter()

        self.assertIn("JSON file has been created successfully.", result.stdout)
        self.assertEqual(len(output["data"]), 5)
        self.assertTrue(all("name" in node and "id" in node for node in all_nodes(output["data"])))

    def test_excludes_rows_with_bh_not_true(self):
        _, output = self.run_converter()

        ids = {node["id"] for node in all_nodes(output["data"])}
        self.assertNotIn("2928", ids)
        self.assertIn("2869", ids)

    def test_warns_for_true_child_of_false_parent(self):
        def set_parent_to_false(df):
            df.loc[df["ID"] == 2869, "Discipline"] = False

        result, output = self.run_converter(set_parent_to_false)

        self.assertIn(
            "Warning: including child 'Physical Chemistry' because BH is TRUE, "
            "but parent 'Chemistry' has BH set to FALSE.",
            result.stdout,
        )
        ids = {node["id"] for node in all_nodes(output["data"])}
        self.assertIn("2869", ids)
        self.assertIn("2894", ids)


if __name__ == "__main__":
    unittest.main()
