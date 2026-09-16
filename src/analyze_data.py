import pandas as pd

# Load processed dataset
df = pd.read_csv("data/processed/processed_queue_data.csv")

print("\n========== DATASET OVERVIEW ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Queue statistics
print("\n========== QUEUE STATISTICS ==========")
print("Average Queue Length:", round(df["queue_length"].mean(), 2))
print("Maximum Queue Length:", df["queue_length"].max())
print("Minimum Queue Length:", df["queue_length"].min())

# Queue by hour
print("\n========== QUEUE BY HOUR ==========")
queue_by_hour = df.groupby("hour")["queue_length"].mean()
print(queue_by_hour.round(2))

# Busiest hour
busiest_hour = queue_by_hour.idxmax()
print("\nBusiest Hour:", busiest_hour)
print("Average Queue:", round(queue_by_hour.max(), 2))

# Queue by service type
print("\n========== QUEUE BY SERVICE TYPE ==========")
queue_by_service = df.groupby("service_type")["queue_length"].mean()
print(queue_by_service.round(2))

# Highest queue service
highest_service = queue_by_service.idxmax()
print("\nService with Highest Average Queue:", highest_service)