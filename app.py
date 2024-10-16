from flask import Flask, render_template
import json
import helpers.fetchers as fetchers
import helpers.analyzers as analyzers
import helpers.db_handlers as db_handlers

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", headers=db_handlers.get_db_headers())


@app.route("/map_meta")
def meta():
    with open("static/assets/map_meta.json", "r") as f:
        data = json.load(f)
    return data


@app.route("/data")
def data():
    places = fetchers.fetch_list(force_web_refetch=False)
    if not places:
        return "Error fetching data", 500

    top2 = analyzers.get_n_most_common(places, 2)
    return app.response_class(
        response=json.dumps({"all": places, "top2": top2}),
        status=200,
        mimetype="application/json",
    )


if __name__ == "__main__":
    app.run(debug=False)
