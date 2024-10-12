import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

url = "https://www.geonames.org/postalcode-search.html?country=PL&q="


def fetch_table(force_web_fetch=False):
    cache_file_name = "cache/data.json"
    if not force_web_fetch:
        table = fetch_valid_cached_table(cache_file_name)
        if table:
            return table

    table = fetch_internet_table()
    if not table:
        return None

    # Save the table to cache
    import os

    os.makedirs("cache", exist_ok=True)
    with open(cache_file_name, "w") as f:
        now = datetime.now().isoformat()
        json.dump({"time": now, "data": str(table)}, f)
    return table


def fetch_internet_table():
    print("Fetching data from the internet")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

    soup = BeautifulSoup(response.content, "lxml")
    restable = soup.find("table", class_="restable")

    if not restable:
        print("No data found")
        return None

    return restable


def fetch_valid_cached_table(file_name):
    print("Fetching cached data")
    try:
        # Check if the data is cached
        with open(file_name, "r") as f:
            json_data = json.load(f)
            json_data_time = json_data.get("time")
            if not json_data_time:
                print("No time found in cache")
                return None

            json_data_time = datetime.fromisoformat(json_data_time)
            if (datetime.now() - json_data_time).days > 1:
                print("Data is too old")
                return None

            print("Data is valid")
            if data := json_data.get("data"):
                print("Converting to tag")
                data = BeautifulSoup(data, "lxml")
            return data
    except json.JSONDecodeError as e:
        print(f"Error getting the file: {e}")
        return None
    except FileNotFoundError:
        print("No cache found")
        return None


def parse_table(restable):
    postal_codes = []
    rows = restable.find_all("tr")

    header_row = [cell.text for cell in rows[0].find_all("th", recursive=False)]
    header_row[0] = "#"
    header_row.append("Coordinates")
    postal_codes.append(header_row)

    for i in range(1, len(rows) - 1, 2):
        cells = rows[i].find_all("td", recursive=False)

        code_data = [cell.get_text(strip=True) for cell in cells]
        code_data.append(rows[i + 1].get_text(strip=True))
        postal_codes.append(code_data)
    return postal_codes
