import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import concurrent.futures


def fetch_list(force_web_fetch=False):
    cache_file_name = "cache/data.json"
    if not force_web_fetch:
        places = fetch_valid_cached_table(cache_file_name)
        if places:
            return places

    places = retrieve_internet_list()
    if not places:
        return None

    for i, place in enumerate(places[1:]):
        place[0] = i + 1

    # Save the places to cache
    import os

    os.makedirs("cache", exist_ok=True)
    with open(cache_file_name, "w") as f:
        now = datetime.now().isoformat()
        json.dump({"time": now, "data": places}, f)

    return places


def fetch_internet_table(code):
    url = "https://www.geonames.org/postalcode-search.html?country=PL&q="

    print(f"    fetching code {code}", end="")
    try:
        response = requests.get(url + code)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f" - failed ({e})")
        return None

    soup = BeautifulSoup(response.content, "lxml")
    restable = soup.find("table", class_="restable")

    if not restable:
        print(" - empty")
    else:
        print(" - success")
    return restable


def retrieve_internet_list():
    def handle_one_code(code):
        data = parse_table(fetch_internet_table(code))
        if not data:
            return []
        return data

    post_codes = get_possible_postal_codes()
    data = [parse_table_header(fetch_internet_table("42-069"))]

    print("Fetching data from the internet")
    with concurrent.futures.ThreadPoolExecutor(50) as executor:
        results = executor.map(handle_one_code, post_codes[:200])

    for result in results:
        data.extend(result)

    return data


def get_possible_postal_codes():
    L = [f"{i:02}" for i in range(100)]
    R = [f"{i:03}" for i in range(1, 1000)]
    codes = [f"{l}-{r}" for l in L for r in R]

    return codes


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
            return json_data.get("data")
    except json.JSONDecodeError as e:
        print(f"Error getting the file: {e}")
        return None
    except FileNotFoundError:
        print("No cache found")
        return None


def parse_table_header(restable):
    if not restable:
        return None

    rows = restable.find_all("tr")

    header_row = [cell.text for cell in rows[0].find_all("th", recursive=False)]
    header_row[0] = "#"
    header_row.append("Coordinates")
    return header_row


def parse_table(restable):
    if not restable:
        return None

    postal_codes = []
    rows = restable.find_all("tr")

    for i in range(1, len(rows) - 1, 2):
        cells = rows[i].find_all("td", recursive=False)

        code_data = [cell.get_text(strip=True) for cell in cells]
        code_data.append(rows[i + 1].get_text(strip=True))
        postal_codes.append(code_data)
    return postal_codes
