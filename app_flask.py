
from flask import Flask, request, render_template
import joblib
import pandas as pd
from features import extract_features

app = Flask(__name__)

# Load the saved dict
bundle = joblib.load("model/phishdetector_v1.pkl")
pipeline = bundle["pipeline"]

# Home page
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Prediction route
@app.route("/predict", methods=["POST"])
def predict():
    url = request.form['url']

    # Extract features from the input URL
    features = extract_features(url)
    df = pd.DataFrame([features])

    # Predict using pipeline
    prediction = pipeline.predict(df)[0]

    # (Optional) probability score if available
    proba = pipeline.predict_proba(df)[0][1] if hasattr(pipeline, "predict_proba") else None

    return render_template(
        "index.html",
        prediction=prediction,
        probability=proba,
        url=url
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
