import requests
from bs4 import BeautifulSoup
from datetime import datetime
from numpy import array_split
import concurrent.futures
import helpers.analyzers as analyzers
import helpers.db_handlers as db_handlers
import os


def fetch_list(force_web_refetch=False):
    # Prepare caching
    os.makedirs("cache", exist_ok=True)
    if not db_handlers.is_db_valid() or force_web_refetch:
        db_handlers.restart_db()

    simplified_code = 0
    if not force_web_refetch:
        last_code = db_handlers.fetch_last_updated()
        simplified_code = last_code.split("-")[1]
        try:
            simplified_code = int(simplified_code)
        except ValueError:
            print("Invalid simplified code, refetching")
            simplified_code = 0
        db_handlers.delete_entry_by_simplified_code(simplified_code)

    places = retrieve_internet_list(simplified_code_starting_from=simplified_code)
    if not places:
        return None

    table_len = len(places)
    places = analyzers.remove_duplicates_embedded_lists(places)
    print(f"There are {table_len - len(places)} duplicates in the db")

    return places


def fetch_internet_table(code):
    url = "https://www.geonames.org/postalcode-search.html?country=PL&q="

    print(f"    fetching code {code}", end="\n")
    try:
        response = requests.get(url + code)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f" - failed ({e})")
        return None

    soup = BeautifulSoup(response.content, "lxml")
    restable = soup.find("table", class_="restable")

    # Does not work well with thread pool
    # if not restable:
    #     print(" - empty")
    # else:
    # print(" - success")
    return restable


def retrieve_internet_list(simplified_code_starting_from):
    def handle_one_code(code):
        data = parse_table(fetch_internet_table(code))

        if not data:
            return []

        if len(data) < 200:
            return data

        print(
            "    code",
            code,
            "has 200 entries (saturated) - discarding and splitting requests",
        )
        # If reached max, throw out, redo with the full code XX-XXX
        with concurrent.futures.ThreadPoolExecutor(100) as sub_executor:
            data = sub_executor.map(handle_one_code, get_extended_postal_codes(code))

        sub_data = []
        for d in data:
            sub_data.extend(d)
        return sub_data

    post_codes = get_simplified_postal_codes(simplified_code_starting_from)

    print("Fetching data from the internet")
    time_start = datetime.now()

    # Split into n subsets, save each time
    subset_number = 20
    for i, post_codes in enumerate(array_split(post_codes, subset_number)):
        print(f"  Fetching subset {i + 1}/{subset_number}")
        data = []
        with concurrent.futures.ThreadPoolExecutor(60) as executor:
            results = executor.map(handle_one_code, post_codes)

        for result in results:
            data.extend(result)

        print(f"  Subset {i + 1}/{subset_number} fetched, saving")
        db_handlers.add_to_db(data)

    print(f"Fetching took {datetime.now() - time_start}")
    return db_handlers.fetch_all()


def get_simplified_postal_codes(starting_from=0):
    # L = [f"{i:02}" for i in range(100)]
    # R = [f"{i:03}" for i in range(1, 1000)]
    # codes = [f"{l}-{r}" for l in L for r in R]
    codes = [f"{i:03}" for i in range(starting_from, 1000)]

    return codes


def get_extended_postal_codes(code_R):
    L = [f"{i:02}" for i in range(0, 100)]
    codes = [
        f"{l}{code_R}" for l in L
    ]  # Do not add the dash here, it fucks up their db querying

    return codes


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
