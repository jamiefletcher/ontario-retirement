import os
import json
import random
from typing import Any, Dict, List

from utils import scrape, scrape_html, save_json, load_json

REGISTER_FILE = "data/rhra_register.json"
REGISTER_EXTRA_FILE = "data/rhra_register_extra.json"

class Registery:
    registry_url = (
        "https://www.rhra.ca/wp-admin/admin-ajax.php?action=public_register&language=en"
    )

    def __init__(self, filename: str = ""):
        self.residences: Dict[str, Residence] = {}
        if filename and os.path.exists(filename):
            self.load_json(filename)
        else:
            self.load_url(Registery.registry_url)

    def load_json(self, filename: str):
        self.residences = {
            r_id: Residence(r) for r_id, r in load_json(filename).items()
        }

    def load_url(self, url: str):
        response_json: Dict[str, Any] = json.loads(scrape(url))
        status = response_json.get("result", {}).get("status")
        entries = response_json.get("result", {}).get("entries")

        if not status or status != "OK" or not entries:
            raise RuntimeError("Unable to download registry", url)

        for entry in entries:
            r_id = entry.get("id")
            r = {key: value for key, value in entry.items() if value is not None}
            self.residences.update({r_id: Residence(r)})

    def keep_only(self, status: List[str] = ["Issued"]):
        if status:
            for r_id, r in self.residences.copy().items():
                if (
                    "lic_status" not in r.attributes
                    or r.attributes["lic_status"] not in status
                ):
                    del self.residences[r_id]

    def scrape_extra_data(self):
        residences = list(self.residences.values())
        random.shuffle(residences)
        for r in residences[:3]:
            r.scrape()

    def save_json(self, filename: str):
        if self.residences:
            residences = {r_id: r.json for r_id, r in self.residences.items()}
            save_json(residences, filename, indent=4)


class Residence:
    base_url = "https://www.rhra.ca/en/register/homeid"

    def __init__(self, attributes: Dict[str, Any]):
        self.attributes = attributes
        self.id = self.attributes.get("id")

    def scrape(self):
        parse_tree = scrape_html(f"{Residence.base_url}/{self.id}", ["body"])
        print(self.id)
        for node in parse_tree.find_all(*["div", "row my-4"]):
            contents = [c for c in node.contents if not c.text.strip() == ""]
            print(contents)

    @property
    def json(self) -> Dict[str, Any]:
        return self.attributes


def main():
    registry = Registery(REGISTER_FILE)
    registry.save_json(REGISTER_FILE)
    registry.keep_only(["Issued"])
    registry.scrape_extra_data()
    print(len(registry.residences))


if __name__ == "__main__":
    main()
