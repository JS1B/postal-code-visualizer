def get_duplicates(data):
    seen = set()
    duplicates = []
    for row in data:
        considered = tuple(row[2:8])
        if considered in seen:
            duplicates.append(row)
        else:
            seen.add(considered)

    return duplicates


def group_by_place(data):
    places = {}
    for row in data[1:]:
        place = (row[1], row[4], row[5], row[6])
        if place not in places:
            places[place] = 0

        places[place] += 1

    return places


if __name__ == "__main__":

    def get_raw_data(data):
        return [row[2:] for row in data]

    import sqlite3 as sq3

    cache_file_name = "cache/solution.db"

    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM postal_codes")
        data = c.fetchall()

    with sq3.connect("cache/data.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM postal_codes")
        data2 = c.fetchall()

    missing = set(get_raw_data(data)) - set(get_raw_data(data2))
    print(f"Found {len(missing)} missing rows")
    print(missing)

    print(get_duplicates(data))
