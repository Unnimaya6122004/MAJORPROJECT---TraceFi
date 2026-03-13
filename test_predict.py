import requests
import joblib
import pandas as pd

# Load model features (same as Flask)
selected_features = joblib.load("model/tracefi_selected_features.pkl")

# Create a dummy test flow (example values)
sample = {feature: 0 for feature in selected_features}

response = requests.post(
    "http://127.0.0.1:5000/predict",
    json=sample
)

print(response.json())
