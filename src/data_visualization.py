import pandas as pd
import matplotlib.pyplot as plt

# Load processed dataset
df = pd.read_csv("data/processed/processed_queue_data.csv")


# ==========================================
# GRAPH 1 — Average Queue Length by Hour
# ==========================================

queue_by_hour = df.groupby("hour")["queue_length"].mean()

plt.figure(figsize=(10, 5))
plt.plot(queue_by_hour.index, queue_by_hour.values, marker="o")
plt.title("Average Queue Length by Hour")
plt.xlabel("Hour")
plt.ylabel("Average Queue Length")
plt.grid(True)
plt.xticks(range(24))
plt.tight_layout()
plt.savefig("data/queue_by_hour.png")
plt.show()


# ==========================================
# GRAPH 2 — Average Crowd by Hour
# ==========================================

crowd_by_hour = df.groupby("hour")["current_crowd"].mean()

plt.figure(figsize=(10, 5))
plt.plot(crowd_by_hour.index, crowd_by_hour.values, marker="o")
plt.title("Average Crowd by Hour")
plt.xlabel("Hour")
plt.ylabel("Average Crowd")
plt.grid(True)
plt.xticks(range(24))
plt.tight_layout()
plt.savefig("data/crowd_by_hour.png")
plt.show()


# ==========================================
# GRAPH 3 — Queue Length by Service Type
# ==========================================

queue_by_service = df.groupby("service_type")["queue_length"].mean()

plt.figure(figsize=(8, 5))
plt.bar(
    queue_by_service.index.astype(str),
    queue_by_service.values
)
plt.title("Average Queue Length by Service Type")
plt.xlabel("Service Type")
plt.ylabel("Average Queue Length")
plt.tight_layout()
plt.savefig("data/queue_by_service.png")
plt.show()


# ==========================================
# GRAPH 4 — Crowd Level Distribution
# ==========================================

crowd_levels = df["crowd_level"].value_counts().sort_index()

plt.figure(figsize=(8, 5))
plt.bar(
    crowd_levels.index.astype(str),
    crowd_levels.values
)
plt.title("Crowd Level Distribution")
plt.xlabel("Crowd Level")
plt.ylabel("Number of Records")
plt.tight_layout()
plt.savefig("data/crowd_level_distribution.png")
plt.show()


print("\n====================================")
print("Data Visualization Complete!")
print("====================================")
print("4 graphs created successfully.")