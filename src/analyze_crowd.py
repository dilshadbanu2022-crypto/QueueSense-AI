import pandas as pd

# Load processed dataset
df = pd.read_csv("data/processed/processed_queue_data.csv")

print("\n========== CROWD STATISTICS ==========")

print("Average Current Crowd:", round(df["current_crowd"].mean(), 2))
print("Maximum Current Crowd:", df["current_crowd"].max())
print("Minimum Current Crowd:", df["current_crowd"].min())

print("\n========== CROWD BY HOUR ==========")

crowd_by_hour = df.groupby("hour")["current_crowd"].mean()
print(crowd_by_hour.round(2))

busiest_crowd_hour = crowd_by_hour.idxmax()

print("\nBusiest Crowd Hour:", busiest_crowd_hour)
print("Average Crowd:", round(crowd_by_hour.max(), 2))

print("\n========== CROWD LEVEL DISTRIBUTION ==========")

crowd_distribution = df["crowd_level"].value_counts().sort_index()

print(crowd_distribution)

print("\n========== CROWD BY SERVICE TYPE ==========")

crowd_by_service = df.groupby("service_type")["current_crowd"].mean()

print(crowd_by_service.round(2))