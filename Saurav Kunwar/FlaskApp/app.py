import numpy as np
from flask import Flask, render_template, jsonify, request
import pickle
app = Flask(__name__)
filename = 'trained_model.ml'
model = pickle.load(open(filename, 'rb'))
status = ""


@app.route('/')
def welcome():
    return render_template("index.html")


@app.route('/1')
def swelcome():
    return "Abe saale"


@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    features = [float(x) for x in request.form.values()]
    final_features = np.array([features])
    # final_features = [np.array(int_features)]
    # prediction = model.predict(final_features)
    prediction = model.predict(final_features)
    result = request.form
    global status
    if prediction[0] == 0:
        status = "Malicious"
    else:
        status = "Not Malicious"

    return render_template('prediction.html', prediction_text='The File is {}'.format(status), result=result)


@app.route('/api', methods=['GET', 'POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)