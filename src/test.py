import csv
import json

with open("data/rhra_register.json", "r") as f:
    json_data = json.load(f)

status_types = {v.get("lic_status") for v in json_data.values()}
print(status_types)

# addr_to_id = {v.get("streetaddress"): k for k,v in json_data.items()}
# corrections = {}

# with open("data/ontario-retirement-homes.csv", "r") as f:
#     csv_data = csv.DictReader(f)
#     for row in csv_data:
#         sa = row.get("streetaddress")
#         i = addr_to_id[sa]
#         corrections[i] = row

# with open("data/corrections.json", "w") as f:
#     json.dump(corrections, f, indent=4)