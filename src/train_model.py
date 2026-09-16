import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("====================================")
print("QUEUE SENSE AI - WAITING TIME MODEL")
print("====================================")

# Load training and testing data
X_train = pd.read_csv("data/processed/X_train.csv")
X_test = pd.read_csv("data/processed/X_test.csv")

y_train = pd.read_csv("data/processed/y_train.csv").squeeze()
y_test = pd.read_csv("data/processed/y_test.csv").squeeze()

print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)


# Create Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# Train model
print("\nTraining model...")
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n========== MODEL RESULTS ==========")
print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("R2  :", round(r2, 4))

# Save model
joblib.dump(model, "models/waiting_time_model.pkl")

print("\nModel saved successfully!")
print("models/waiting_time_model.pkl")

# Sample predictions
print("\n========== SAMPLE PREDICTIONS ==========")

for i in range(5):
    print(
        "Actual:", round(y_test.iloc[i], 2),
        "| Predicted:", round(y_pred[i], 2)
    )

print("\nDAY 3 COMPLETED!")