import json
import os
import random
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from utils import ascii_only, clean_string, load_json, save_geojson, save_json, scrape

REGISTER_FILE = "data/rhra_register.json"
CORRECTIONS_FILE = "data/corrections.json"

class Registery:
    registry_url = (
        "https://www.rhra.ca/wp-admin/admin-ajax.php?action=public_register&language=en"
    )
    status_operating = ["Issued", "Application Received", "Issued with conditions"]

    def __init__(self, filename: str = ""):
        self.residences: Dict[str, Residence] = {}
        if filename and os.path.exists(filename):
            self.load_json(filename, update_only=False)
        else:
            self.load_url(Registery.registry_url)

    def load_json(self, filename: str, update_only = True):
        for r_id, r_attrib in load_json(filename).items():
            if r_id not in self.residences and not update_only:
                self.residences[r_id] = Residence(r_attrib)
            elif r_id in self.residences:
                self.residences[r_id].update(r_attrib)

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

    def filter_status(self, keep: List[str] = None):
        if keep:
            for r_id, r in self.residences.copy().items():
                if (
                    "lic_status" in r.attributes
                    and r.attributes["lic_status"] not in keep
                ):
                    del self.residences[r_id]

    def scrape_details(self):
        residences = list(self.residences.items())
        random.shuffle(residences)
        for r_id, r in residences:
            print(r_id)
            r_status = r.attributes.get("lic_status")
            if r_status in Registery.status_operating and "services" not in r.attributes:
                r.scrape()

    def save_json(self, filename: str):
        if self.residences:
            residences = {r_id: r.json for r_id, r in self.residences.items()}
            save_json(residences, filename, indent=4)
    
    def save_geojson(self, name:str, filename: str):
        if self.residences:
            features = [r.feature for r in self.residences.values()]
            save_geojson(name, features, filename)


class Residence:
    base_url = "https://www.rhra.ca/en/register/homeid"

    def __init__(self, attributes: Dict[str, Any]):
        self.attributes = attributes
        self.id = self.attributes.get("id")

    def scrape(self, target: Dict[str, str] = {"id": "accordionPR", "role": "tablist"}):
        html_content = scrape(f"{Residence.base_url}/{self.id}")
        parse_tree = BeautifulSoup(html_content, features="html.parser").find(**target)      
        children: List[BeautifulSoup] = [child for child in parse_tree if child.name is not None]

        extra_attributes = {}
        while children:
            section_title: str = children.pop(0).text.strip().lower()
            section_data = children.pop(0)
            new_attrs = Extractor(section_title).apply(section_data)
            extra_attributes.update(new_attrs)        
        self.attributes.update(extra_attributes)

    def update(self, attributes: Dict[str, Any]):
        self.attributes.update(attributes)

    @property
    def feature(self) -> Dict[str, Any]:
        geometry = None
        if "latlng" in self.attributes:
            lat, lon = self.attributes.get("latlng").split(",")
            lat, lon = float(lat), float(lon)
            geometry = { "type": "Point", "coordinates": [lon, lat]}
        return {
            "type": "Feature",
            "properties": self.attributes,
            "geometry": geometry,
        }

    @property
    def json(self) -> Dict[str, Any]:
        return self.attributes


class Extractor:
    _services_map = {
        "Assistance with bathing ": "Bathing",
        "Assistance with personal hygiene ": "Hygiene",
        "Assistance with ambulation ": "Walking",
        "Assistance with feeding ": "Feeding",
        "Provision of skin and wound care ": "Wounds",
        "Continence care ": "Continence",
        "Administration of drugs or another substance ": "Drugs",
        "Provision of a meal ": "Meals",
        "Dementia care program ": "Dementia",
        "Assistance with dressing ": "Dressing",
        "Any service that a member of the Ontario College of Pharmacists provides while engaging in the practice of pharmacy ": "Pharmacist",
        "Any service that a member of the College of Physicians and Surgeons of Ontario provides while engaging in the practice of medicine ": "Doctor",
        "Any service that a member of the College of Nurses of Ontario provides while engaging in the practice of nursing ": "Nurse",
    }
    
    def __init__(self, section: str = ""):
        self.methods = {
            "licence information": Extractor._summary,
            "care services": Extractor._services,
            "number of suites / fire sprinklers": Extractor._default,
            "inspection reports": Extractor._reports,
            "registrar enforcement orders": Extractor._orders,
            "external proceedings, orders and decisions": Extractor._proceedings,
            "conditions on the licence": Extractor._noop,
            "persons with controlling interest": Extractor._noop,
        }
        self.apply = self.methods.get(section, Extractor._noop)

    def _noop(root: BeautifulSoup) -> Dict[str, Any]:
        return {}

    def _default(root: BeautifulSoup, target = ["div", "row my-4"]) -> Dict[str, Any]:
        extra_attributes = {}
        for node in root.find_all(*target):
            contents = [c for c in node.contents if not c.text.strip() == ""]
            if len(contents) == 2:
                key, value = contents
                key = ascii_only(clean_string(key))
                extra_attributes[key] = clean_string(value)
        return extra_attributes
    
    def _summary(root: BeautifulSoup, target = ["div", "row my-4"]) -> Dict[str, Any]:
        extra_attributes = {}
        for node in root.find_all(*target):
            contents = [c for c in node.contents if not c.text.strip() == ""]
            if len(contents) == 2:
                key, value = contents
                key = ascii_only(clean_string(key))
                extra_attributes[key] = clean_string(value)
            elif len(contents) == 1:
                paragraphs: BeautifulSoup = contents[0].find("p")
                paragraphs = [] if paragraphs is None else paragraphs
                mandatory_inspection = False
                for p in paragraphs:
                    if "mandatory" in p.text.lower():
                        mandatory_inspection = True
                        break
                extra_attributes["mandatory_inspection"] = mandatory_inspection
        return extra_attributes
    
    def _services(root: BeautifulSoup, target = ["ul", "careservices_list"]) -> Dict[str, Any]:
        services = root.find(*target)
        services = [c for c in services.contents if not c.text.strip() == ""]
        services_list = {}
        for s in services:
            key, value = s.text.split("-")
            key = Extractor._services_map[key] if key in Extractor._services_map else key
            value = value.strip() == "\u2705"
            services_list[key] = value
        return {"services": services_list}
    
    def _reports(root: BeautifulSoup, target = ["div", "row my-4"], key="reports") -> Dict[str, Any]:
        base_url = "https://www.rhra.ca"
        reports = {}
        for node in root.find_all(*target):
            contents = [c for c in node.contents if not c.text.strip() == ""]
            if len(contents) == 2:
                date, link = contents
                link = link.find("a")
                if date and link:
                    date = date.text
                    url = f"{base_url}{link['href']}"
                    reports[date] = url
        return {key: reports}

    def _orders(root: BeautifulSoup) -> Dict[str, Any]:
        return Extractor._reports(root, key="orders")
    
    def _proceedings(root: BeautifulSoup) -> Dict[str, Any]:
        return Extractor._reports(root, key="proceedings")

def main():
    registry = Registery(REGISTER_FILE)
    registry.scrape_details()
    registry.save_json(REGISTER_FILE)
    registry.load_json(CORRECTIONS_FILE)
    registry.filter_status(keep=["Issued", "Application Received", "Issued with conditions"])
    registry.save_geojson("Ontario Retirement Homes", "data/homes.geojson")
    print(len(registry.residences))


if __name__ == "__main__":
    main()
