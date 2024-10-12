from flask import Flask, render_template
import json
import helpers.fetchers as fetchers

app = Flask(__name__)


@app.route("/")
def index():
    table = fetchers.fetch_table()
    table = fetchers.parse_table(table)
    if not table:
        return "Error fetching data", 500

    return render_template("index.html", headers=table[0], postal_codes=table[1:])


@app.route("/map_meta")
def meta():
    with open("static/assets/map_meta.json", "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    app.run(debug=True)
