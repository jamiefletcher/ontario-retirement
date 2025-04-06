import html
import json
import os
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

WINDOWS_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3"


def load_json(filename: str) -> Any:
    with open(filename, "r") as f:
        json_data = json.load(f)
    return json_data


def save_json(obj: Any, filename: str, indent = None):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent) 


def save_geojson(name: str, features: dict, output_filename: str):
    geojson = {
        "type": "FeatureCollection",
        "name": name,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }
    with open(output_filename, "w") as f:
        json.dump(geojson, f, indent=4, ensure_ascii=False)


def scrape(url: str, user_agent: str = WINDOWS_CHROME) -> Any:
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers)
    r.raise_for_status()
    return r.content


def scrape_html(url: str, root_tag: List[str], user_agent: str = WINDOWS_CHROME) -> BeautifulSoup:
    content = scrape(url, user_agent)
    return BeautifulSoup(content, features="html.parser").find(*root_tag)


# TODO: When the geocoder is confused, it returns multiple matches
def geocode(address: str, api_key_env: str = "GEOAPIFY_API_KEY") -> Tuple[str, Dict]:
    api_key = os.getenv(api_key_env)
    address = html.escape(address.strip())
    headers = {"Accept": "application/json"}
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
    r = requests.get(url, headers)
    r.raise_for_status()
    r_json = r.json()
    features = r_json.get("features")
    if features:
        f = features[0]
        props = f.get("properties", {})
        geo = f.get("geometry", {})
        formatted = props.get("formatted", "")
        return formatted, geo
    return "", {}

