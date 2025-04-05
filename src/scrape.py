import os
from typing import Any, Dict, List

from utils import scrape_json, save_json, load_json

RHRA_PUBLIC_REGISTER_URL = (
    "https://www.rhra.ca/wp-admin/admin-ajax.php?action=public_register&language=en"
)
RHRA_PUBLIC_REGISTER_FILE = "data/rhra_register.json"


class Registery:
    def __init__(self, filename: str, url: str):
        self.residences = {}
        if os.path.exists(filename):
            self.residences = load_json(filename)
        else:
            self.load_url(url)
            self.save_json(filename)

    def load_url(self, url: str):
        response_json: Dict[str, Any] = scrape_json(url)
        status = response_json.get("result", {}).get("status")
        entries = response_json.get("result", {}).get("entries")
        if not status or status != "OK" or not entries:
            raise RuntimeError("Unable to download RHRA registry", url)
        for entry in entries:
            r_id = entry.get("id")
            residence = {
                key: value for key, value in entry.items() if value is not None
            }
            self.residences.update({r_id: residence})
    
    def keep_only(self, status: List[str] = ["Issued"]):
        if status:
            for key, residence in self.residences.copy().items():
                if "lic_status" not in residence or residence["lic_status"] not in status:
                    del(self.residences[key])

    def save_json(self, filename: str):
        if self.residences:
            save_json(self.residences, filename, indent=4)


def main():
    registry = Registery(
        filename=RHRA_PUBLIC_REGISTER_FILE, url=RHRA_PUBLIC_REGISTER_URL
    )
    registry.keep_only(["Issued"])
    print(len(registry.residences))


if __name__ == "__main__":
    main()
