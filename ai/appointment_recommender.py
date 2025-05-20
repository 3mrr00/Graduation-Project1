import joblib
import pandas as pd
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'appointment_model.pkl')
model = joblib.load(MODEL_PATH)

def recommend_appointment(features: dict):
    df = pd.DataFrame([features])
    prediction = model.predict(df)
    return prediction[0]