""" Flask app """

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

from aramorph import analyser

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# not using a database
# not sure if I need this line:
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# views

@app.route('/')
def main():
    return render_template('yamli.html')

@app.route('/query_ajax', methods=['POST'])
def query():
    if request.json and 'words' in request.json:
        results = list()
        words = request.json['words'].split(",")
        for word in words:
            for analysis in analyser.ai.analyse_arabic(word):
                if analysis and analysis not in results:
                    results.append(analysis)
        if len(results) > 0:
            return jsonify(analyses=results), 201
        else:
            # Yamli gave us some words but we didn't find them in Buckwalter AMA
            # give some abbreviated information anyway
            results = analyser.ai.information(words)
            return jsonify(analyses=results), 201

# TODO: add route like /kitab etc
# fuzzy.herokuapp.com/kitab ---> page with "kitab" already filled in and all the possibilities displayed
#def word():
#    return render_template('yamli.html', {'word': word})

if __name__ == '__main__':
    app.run(debug=False)
