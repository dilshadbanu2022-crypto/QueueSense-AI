
import os
import numpy as np
import pandas as pd


# -------------------------------------------------
# 1. Basic settings
# -------------------------------------------------

NUM_RECORDS = 50000

np.random.seed(42)


# -------------------------------------------------
# 2. Create timestamps
# -------------------------------------------------

timestamps = pd.date_range(
    start="2025-01-01",
    periods=NUM_RECORDS,
    freq="10min"
)


# -------------------------------------------------
# 3. Basic time information
# -------------------------------------------------

df = pd.DataFrame({
    "timestamp": timestamps
})

df["day_of_week"] = df["timestamp"].dt.day_name()
df["hour"] = df["timestamp"].dt.hour


# -------------------------------------------------
# 4. Service types
# -------------------------------------------------

service_types = [
    "Registration",
    "OPD",
    "Laboratory",
    "Pharmacy"
]

df["service_type"] = np.random.choice(
    service_types,
    size=NUM_RECORDS,
    p=[0.20, 0.40, 0.20, 0.20]
)


# -------------------------------------------------
# 5. Holiday
# -------------------------------------------------

df["holiday"] = np.random.choice(
    [0, 1],
    size=NUM_RECORDS,
    p=[0.95, 0.05]
)


# -------------------------------------------------
# 6. Number of active counters
# -------------------------------------------------

df["active_counters"] = np.random.randint(
    1, 6, size=NUM_RECORDS
)


# -------------------------------------------------
# 7. Staff available
# -------------------------------------------------

df["staff_available"] = (
    df["active_counters"]
    + np.random.randint(0, 3, size=NUM_RECORDS)
)


# -------------------------------------------------
# 8. Average service time
# -------------------------------------------------

service_time_map = {
    "Registration": 5,
    "OPD": 12,
    "Laboratory": 10,
    "Pharmacy": 7
}

df["average_service_time"] = (
    df["service_type"]
    .map(service_time_map)
    + np.random.normal(0, 1.5, NUM_RECORDS)
)

df["average_service_time"] = (
    df["average_service_time"].clip(lower=3)
)


# -------------------------------------------------
# 9. Arrival pattern
# -------------------------------------------------

# Base arrival rate
base_arrivals = np.random.poisson(
    5,
    NUM_RECORDS
)


# Peak-hour multiplier
peak_multiplier = np.where(
    df["hour"].isin([9, 10, 11, 12, 14, 15, 16, 17]),
    1.8,
    0.8
)


# Weekend multiplier
weekend_multiplier = np.where(
    df["day_of_week"].isin(["Saturday", "Sunday"]),
    0.6,
    1.0
)


# Holiday multiplier
holiday_multiplier = np.where(
    df["holiday"] == 1,
    0.5,
    1.0
)


df["people_arriving"] = (
    base_arrivals
    * peak_multiplier
    * weekend_multiplier
    * holiday_multiplier
).astype(int)


# -------------------------------------------------
# 10. Service capacity
# -------------------------------------------------

# Each counter can serve approximately:
# 10 minutes / average service time

df["capacity"] = (
    df["active_counters"] * 10
    / df["average_service_time"]
).round().astype(int)

df["capacity"] = df["capacity"].clip(lower=1)


# -------------------------------------------------
# 11. People served
# -------------------------------------------------

service_probability = np.random.uniform(
    0.75,
    1.0,
    NUM_RECORDS
)

df["people_served"] = (
    df["capacity"] * service_probability
).astype(int)

df["people_served"] = (
    df["people_served"].clip(lower=0)
)


# -------------------------------------------------
# 12. Queue length
# -------------------------------------------------

queue = 0
queue_lengths = []

for i, (arrivals, served) in enumerate(
    zip(
        df["people_arriving"],
        df["people_served"]
    )
):

    # Reset queue at the beginning of each new day
    if i > 0:
        current_day = str(df.loc[i, "timestamp"])[:10]
        previous_day = str(df.loc[i - 1, "timestamp"])[:10]

        if current_day != previous_day:
            queue = 0

    queue = max(
        0,
        queue + arrivals - served
    )

    queue_lengths.append(queue)

df["queue_length"] = queue_lengths


# -------------------------------------------------
# 13. Current crowd
# -------------------------------------------------

df["current_crowd"] = (
    df["queue_length"]
    + df["people_arriving"]
).astype(int)


# -------------------------------------------------
# 14. Waiting time
# -------------------------------------------------

df["waiting_time"] = (
    df["queue_length"]
    * df["average_service_time"]
    / df["active_counters"]
)

# Add small realistic variation
df["waiting_time"] += np.random.normal(
    0,
    2,
    NUM_RECORDS
)

df["waiting_time"] = (
    df["waiting_time"]
    .clip(lower=0)
    .round(2)
)


# -------------------------------------------------
# 15. Future crowd
# -------------------------------------------------

future_change = (
    df["people_arriving"]
    - df["people_served"]
)

df["future_crowd"] = (
    df["current_crowd"]
    + future_change
    + np.random.randint(-3, 4, NUM_RECORDS)
)

df["future_crowd"] = (
    df["future_crowd"]
    .clip(lower=0)
    .astype(int)
)


# -------------------------------------------------
# 16. Crowd level
# -------------------------------------------------

df["crowd_level"] = pd.cut(
    df["future_crowd"],
    bins=[-1, 15, 35, np.inf],
    labels=["Low", "Medium", "High"]
)


# -------------------------------------------------
# 17. Arrange columns
# -------------------------------------------------

df = df[
    [
        "timestamp",
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
        "waiting_time",
        "future_crowd",
        "crowd_level"
    ]
]


# -------------------------------------------------
# 18. Create output folder
# -------------------------------------------------

output_folder = "data/raw"

os.makedirs(
    output_folder,
    exist_ok=True
)


# -------------------------------------------------
# 19. Save dataset
# -------------------------------------------------

output_file = os.path.join(
    output_folder,
    "queue_data.csv"
)

df.to_csv(
    output_file,
    index=False
)


# -------------------------------------------------
# 20. Show results
# -------------------------------------------------

print("====================================")
print("QueueSense AI Dataset Generated!")
print("====================================")

print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_file}")

print("\nFirst 5 records:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())