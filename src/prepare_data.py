import pandas as pd
from sklearn.model_selection import train_test_split

# Load processed dataset
df = pd.read_csv("data/processed/processed_queue_data.csv")

print("Original dataset shape:", df.shape)

# Features for Machine Learning
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
    "future_crowd",
    "year",
    "month",
    "day"
]

# Target for Day 3: waiting time
X = df[features]
y = df["waiting_time"]

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\n====================================")
print("Training & Testing Data Prepared!")
print("====================================")

print("Training features:", X_train.shape)
print("Testing features:", X_test.shape)
print("Training target:", y_train.shape)
print("Testing target:", y_test.shape)

# Save the prepared datasets
X_train.to_csv("data/processed/X_train.csv", index=False)
X_test.to_csv("data/processed/X_test.csv", index=False)
y_train.to_csv("data/processed/y_train.csv", index=False)
y_test.to_csv("data/processed/y_test.csv", index=False)

print("\nFiles saved successfully!")
print("X_train.csv")
print("X_test.csv")
print("y_train.csv")
print("y_test.csv")