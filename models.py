from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Load model and vectorizer
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
with open('vectorizer.pkl', 'rb') as vec_file:
    vectorizer = pickle.load(vec_file)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['text']
    transformed_text = vectorizer.transform([text])
    prediction = model.predict(transformed_text)
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)
