import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, classification_report

print("====================================")
print("QUEUE SENSE AI - CROWD MODELS")
print("====================================")

df = pd.read_csv("data/processed/processed_queue_data.csv")

features = [
    "day_of_week",
    "hour",
    "service_type",
    "queue_length",
    "people_arriving",
    "people_served",
    "active_counters",
    "staff_available",
    "average_service_time",
    "capacity",
    "holiday",
    "current_crowd",
    "year",
    "month",
    "day"
]

X = df[features]

# ==============================
# CROWD PREDICTION
# ==============================

y_crowd = df["future_crowd"]

print("\nTraining crowd prediction model...")

crowd_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_crowd,
    test_size=0.20,
    random_state=42
)

crowd_model.fit(X_train, y_train)

predictions = crowd_model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\n========== CROWD PREDICTION ==========")
print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("R2  :", round(r2, 4))

joblib.dump(crowd_model, "models/crowd_prediction_model.pkl")

print("Crowd model saved!")

# ==============================
# CROWD RISK CLASSIFIER
# ==============================

y_risk = df["crowd_level"]

print("\nTraining crowd risk classifier...")

risk_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_risk,
    test_size=0.20,
    random_state=42,
    stratify=y_risk
)

risk_model.fit(X_train, y_train)

risk_predictions = risk_model.predict(X_test)

accuracy = accuracy_score(y_test, risk_predictions)

print("\n========== CROWD RISK ==========")
print("Accuracy:", round(accuracy, 4))

print("\nClassification Report:")
print(classification_report(y_test, risk_predictions))

joblib.dump(risk_model, "models/crowd_risk_model.pkl")

print("Risk model saved!")

print("\n====================================")
print("DAY 4 COMPLETED!")
print("====================================")