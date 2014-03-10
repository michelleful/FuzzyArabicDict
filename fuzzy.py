""" Flask app """

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

from aramorph import aramorph

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

@app.route('/query', methods=['POST'])
def query():
    if request.json and 'words' in request.json:
        results = list()
        for word in request.json['words'].split(","):
            for analysis in aramorph.analyse_arabic(word):
                if analysis:
                    results.append(analysis)
        return jsonify(analyses=results), 201

if __name__ == '__main__':
    app.run(debug=True)
