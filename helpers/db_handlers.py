import sqlite3 as sq3

cache_file_name = "cache/data.db"


def restart_db():
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS postal_codes")
        c.execute(
            """
            CREATE TABLE postal_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                site_id INTEGER,
                place TEXT,
                code TEXT,
                country TEXT,
                admin1 TEXT,
                admin2 TEXT,
                admin3 TEXT,
                coordinates TEXT
            )
            """
        )
        conn.commit()


def get_db_headers():
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM postal_codes LIMIT 1")

        h = [x[0] for x in c.description]
        h.pop(1)
    return h


# Does it exist and have one row?
def is_db_valid() -> bool:
    try:
        with sq3.connect(cache_file_name) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM postal_codes")
            d = c.fetchone()
            if d is None:
                return False
            return d[0] > 0
    except sq3.OperationalError:
        return False


def add_to_db(places):
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.executemany(
            "INSERT INTO postal_codes (site_id, place, code, country, admin1, admin2, admin3, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            places,
        )
        conn.commit()


def fetch_last_updated():
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT code FROM postal_codes WHERE id = (SELECT MAX(id) FROM postal_codes)"
        )
        d = c.fetchone()
        if d is None:
            return "00-000"
        return d[0]


def fetch_all(include_header=True):
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, place, code, country, admin1, admin2, admin3, coordinates FROM postal_codes"
        )
        data = c.fetchall()

    if include_header:
        header = get_db_headers()
        data.insert(0, header)
    return data


def delete_entry_by_simplified_code(code):
    code = str(code)

    print(f"Deleting entries with simplified code {code}")
    with sq3.connect(cache_file_name) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM postal_codes WHERE code LIKE ?", ("%" + code,))
        conn.commit()
