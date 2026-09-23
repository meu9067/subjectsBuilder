import json

import pandas as pd


df = pd.read_csv("SN-T_v2.csv", encoding="cp1252")
json_structure = {"data": []}
included_by_id = {
    str(int(row["ID"])): str(row.iloc[59]).upper() == "TRUE"
    for _, row in df.iterrows()
}

for _, row in df.iterrows():
    if str(row.iloc[59]).upper() != "TRUE":
        continue

    levels = [
        (row[f"Level {level}"], row[f"Level {level} ID"])
        for level in range(1, 16)
        if f"Level {level}" in df.columns and f"Level {level} ID" in df.columns
        and not pd.isna(row[f"Level {level}"])
        and not pd.isna(row[f"Level {level} ID"])
    ]
    if len(levels) > 1:
        parent_name, parent_id = levels[-2]
        if included_by_id.get(str(int(parent_id))) is False:
            child_name, _ = levels[-1]
            print(
                f"Warning: including child '{child_name}' because BH is TRUE, "
                f"but parent '{parent_name}' has BH set to FALSE."
            )

    current_level = json_structure["data"]

    for level in range(1, 16):
        name_column = f"Level {level}"
        id_column = f"Level {level} ID"

        if name_column not in df.columns or id_column not in df.columns:
            break

        name = row[name_column]
        identifier = row[id_column]

        if pd.isna(name) or pd.isna(identifier):
            break

        id_ = str(int(identifier))
        node = next(
            (
                item
                for item in current_level
                if item["name"] == name and item["id"] == id_
            ),
            None,
        )

        if node is None:
            node = {
                "name": name,
                "id": id_,
                "description": "" if pd.isna(row["Description"]) else row["Description"],
                "sublevels": [],
            }
            current_level.append(node)

        current_level = node["sublevels"]

with open("output.json", "w", encoding="utf-8") as json_file:
    json.dump(json_structure, json_file, indent=4, ensure_ascii=False)

print("JSON file has been created successfully.")
