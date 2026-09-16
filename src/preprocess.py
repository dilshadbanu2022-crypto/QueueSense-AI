import pandas as pd
import os

# -----------------------------------------
# 1. Load the dataset
# -----------------------------------------

input_file = "data/raw/queue_data.csv"

df = pd.read_csv(input_file)

print("Original dataset:")
print(df.head())

# -----------------------------------------
# 2. Convert timestamp
# -----------------------------------------

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Extract useful time features
df["year"] = df["timestamp"].dt.year
df["month"] = df["timestamp"].dt.month
df["day"] = df["timestamp"].dt.day

# -----------------------------------------
# 3. Convert text columns into numbers
# -----------------------------------------

df["day_of_week"] = df["day_of_week"].astype("category").cat.codes

df["service_type"] = df["service_type"].astype("category").cat.codes

df["crowd_level"] = (
    df["crowd_level"]
    .map({
        "Low": 0,
        "Medium": 1,
        "High": 2
    })
)

# -----------------------------------------
# 4. Remove timestamp
# -----------------------------------------

df = df.drop(columns=["timestamp"])

# -----------------------------------------
# 5. Save processed dataset
# -----------------------------------------

output_folder = "data/processed"

os.makedirs(output_folder, exist_ok=True)

output_file = os.path.join(
    output_folder,
    "processed_queue_data.csv"
)

df.to_csv(output_file, index=False)

# -----------------------------------------
# 6. Show results
# -----------------------------------------

print("\n====================================")
print("QueueSense AI Preprocessing Complete!")
print("====================================")

print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_file}")

print("\nProcessed dataset:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())