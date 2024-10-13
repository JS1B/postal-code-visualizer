from flask import Flask, render_template
import json
import helpers.fetchers as fetchers
import helpers.analyzers as analyzers

app = Flask(__name__)


@app.route("/")
def index():
    places = fetchers.fetch_list(force_web_fetch=False)

    # gr = analyzers.group_by_place(places)
    # gr = sorted(gr.items(), key=lambda x: x[1], reverse=True)
    # gr = gr[:5]
    # print(gr)

    if not places:
        return "Error fetching data", 500

    return render_template("index.html", headers=places[0], postal_codes=places[1:])


@app.route("/map_meta")
def meta():
    with open("static/assets/map_meta.json", "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    app.run(debug=True)
