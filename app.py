import pickle

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)
with open("encoders.pkl", "rb") as f:
    encoders = pickle.load(f)
with open("feature_list.pkl", "rb") as f:
    features = pickle.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    try:
        values = {
            "Gender": encoders["Gender"].transform([data["gender"]])[0],
            "Age": float(data["age"]),
            "Academic Pressure": float(data["academicPressure"]),
            "Study Satisfaction": float(data["studySatisfaction"]),
            "Sleep Duration": encoders["Sleep Duration"].transform([data["sleep"]])[0],
            "Dietary Habits": encoders["Dietary Habits"].transform([data["diet"]])[0],
            "Work/Study Hours": float(data["studyHours"]),
            "Financial Stress": float(data["financialStress"]),
            "Family History of Mental Illness": encoders[
                "Family History of Mental Illness"
            ].transform([data["familyHistory"]])[0],
            "CGPA": float(data["cgpa"]),
        }
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"ข้อมูลไม่ถูกต้อง: {e}"}), 400

    input_df = pd.DataFrame([values], columns=features)
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])  # ความน่าจะเป็นของ "เป็นซึมเศร้า"

    return jsonify({
        "prediction": prediction,
        "probability": round(probability * 100, 1),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)