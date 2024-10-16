def get_duplicates(data):
    seen = set()
    duplicates = []
    for row in data:
        considered = tuple(row[1:8])
        if considered in seen:
            duplicates.append(row)
        else:
            seen.add(considered)

    return duplicates


def group_by_place(data):
    places = {}
    for row in data[1:]:
        place = (row[1], row[4], row[5], row[6])
        if any(value is None or value == "" for value in place):
            print(f"Detected faulty {place}")

        if place not in places:
            places[place] = 0

        places[place] += 1

    return places


def get_n_most_common(data, n):
    gr = group_by_place(data)
    gr = sorted(gr.items(), key=lambda x: x[1], reverse=True)
    return gr[:n]


if __name__ == "__main__":

    import db_handlers as db_handlers

    cache_file_name = "cache/data.db"

    data = db_handlers.fetch_all()

    gr = group_by_place(data)

    gr = sorted(gr.items(), key=lambda x: x[1], reverse=True)
    count = sum([x[1] for x in gr])

    print(count)
    # This shows there is something wrong with the data
    # These counts as duplicates (there is more, too):
    # 40159  47       Krynica-Zdrój  33-338  Poland   Lesser Poland  Powiat nowosądecki  Krynica-Zdrój  49.4/20.953
    # 42777  23       Krynica-Zdrój  33-381  Poland   Lesser Poland  Powiat nowosądecki  Krynica-Zdrój  49.4/20.953
    # This has empty admin2 and admin3
    # 47972  30       Jeziora  88-420  Poland   Kujawsko-Pomorskie                  52.654/17.76

    print("Top 2 places:")
    print(get_n_most_common(data, 2))
