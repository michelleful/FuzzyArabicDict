""" Flask app """

from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    abort,
    render_template,
    flash,
    jsonify,
)
from aramorph.aramorpher import Aramorpher

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# not using a database
# not sure if I need this line:
app.config.from_envvar("FLASKR_SETTINGS", silent=True)

analyser = Aramorpher()

# views


@app.route("/")
def main():
    return render_template("yamli.html")


@app.route("/query_ajax", methods=["POST"])
def query():
    if request.json and "words" in request.json:
        results = request.json["words"]
        if results is not None:
            results = list()
            words = request.json["words"].split(",")
            for word in words:
                for analysis in analyser.analyse_arabic(word):
                    if analysis and analysis not in results:
                        results.append(analysis)
            if len(results) == 0:
                # Yamli gave us some words but we didn't
                # find them in Buckwalter AMA,
                # give some abbreviated information anyway
                results = analyser.information(words)
        return jsonify(analyses=results), 201


if __name__ == "__main__":
    app.run(debug=False)
