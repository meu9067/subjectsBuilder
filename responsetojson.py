import json


with open("response.json", encoding="utf-8") as response_file:
    response = json.load(response_file)

nodes_by_id = {
    subject["id"]: {
        "name": subject["name"],
        "id": str(subject["id"]),
        "description": subject.get("description") or "",
        "sublevels": [],
    }
    for subject in response["data"]
}
roots = []

for subject in response["data"]:
    node = nodes_by_id[subject["id"]]
    parent_ids = subject.get("parentIds", [])

    if not parent_ids:
        roots.append(node)
        continue

    parent_id = parent_ids[-1]
    parent = nodes_by_id.get(parent_id)
    if parent is None:
        print(
            f"Warning: parent {parent_id} for '{subject['name']}' was not found; "
            "adding it at the top level."
        )
        roots.append(node)
    else:
        parent["sublevels"].append(node)


def trim_to_five_levels(nodes, level=1):
    if level == 5:
        for node in nodes:
            node["sublevels"] = []
        return

    for node in nodes:
        trim_to_five_levels(node["sublevels"], level + 1)


trim_to_five_levels(roots)

with open("response-output.json", "w", encoding="utf-8") as output_file:
    json.dump({"data": roots}, output_file, indent=4, ensure_ascii=False)

print("Nested JSON file has been created successfully.")
