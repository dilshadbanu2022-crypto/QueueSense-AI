from ml_prediction_engine import MLPredictionEngine


class WhatIfSimulator:

    def __init__(self, max_counters=5):

        self.max_counters = max_counters

        self.ml_engine = MLPredictionEngine()

    # ==================================================
    # RUN WHAT-IF SCENARIO
    # ==================================================

    def simulate(
        self,
        state,
        additional_counters
    ):

        current_counters = state["active_counters"]

        new_counters = min(
            current_counters + additional_counters,
            self.max_counters
        )

        # Copy current state
        scenario = state.copy()

        # Change counters
        scenario["active_counters"] = new_counters

        # Adjust staff for additional counters
        scenario["staff_available"] = max(
            state["staff_available"],
            new_counters
        )

        # Predict new result
        prediction = self.ml_engine.predict(
            scenario
        )

        return {
            "current_counters":
                current_counters,

            "new_counters":
                new_counters,

            "predicted_waiting_time":
                prediction["predicted_waiting_time"],

            "predicted_crowd":
                prediction["predicted_crowd"],

            "risk":
                prediction["risk"]
        }

    # ==================================================
    # COMPARE CURRENT VS WHAT-IF
    # ==================================================

    def compare(
        self,
        current_prediction,
        what_if_result
    ):

        current_wait = (
            current_prediction[
                "predicted_waiting_time"
            ]
        )

        new_wait = (
            what_if_result[
                "predicted_waiting_time"
            ]
        )

        if current_wait > 0:

            improvement = (
                (
                    current_wait - new_wait
                )
                / current_wait
            ) * 100

        else:

            improvement = 0

        return {
            "current_wait":
                round(current_wait, 2),

            "new_wait":
                round(new_wait, 2),

            "improvement":
                round(improvement, 2),

            "risk":
                what_if_result["risk"]
        }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    print("\nQueueSense AI")
    print("What-If Simulator Test")
    print("=" * 60)

    simulator = WhatIfSimulator(
        max_counters=5
    )

    # Example simulation state
    state = {
    "queue_length": 80,
    "people_arriving": 20,
    "people_served": 8,
    "active_counters": 3,
    "staff_available": 4,
    "average_service_time": 5,
    "hour": 10,
    "day_of_week": 1,
    "service_type": 1,
    "holiday": 0,
    "current_crowd": 100,
    "simulation_time": "10:00:00"
}

    # Current prediction
    current_prediction = (
        simulator.ml_engine.predict(
            state
        )
    )

    print("\nCURRENT SITUATION")
    print("=" * 60)

    print(
        f"Counters : "
        f"{state['active_counters']}"
    )

    print(
        f"Waiting  : "
        f"{current_prediction['predicted_waiting_time']:.2f} minutes"
    )

    print(
        f"Crowd    : "
        f"{current_prediction['predicted_crowd']:.2f}"
    )

    print(
        f"Risk     : "
        f"{current_prediction['risk']}"
    )

    # Add 2 counters
    result = simulator.simulate(
        state,
        additional_counters=2
    )

    comparison = simulator.compare(
        current_prediction,
        result
    )

    print("\nWHAT-IF: ADD 2 COUNTERS")
    print("=" * 60)

    print(
        f"New Counters : "
        f"{result['new_counters']}"
    )

    print(
        f"New Waiting  : "
        f"{result['predicted_waiting_time']:.2f} minutes"
    )

    print(
        f"New Crowd    : "
        f"{result['predicted_crowd']:.2f}"
    )

    print(
        f"New Risk     : "
        f"{result['risk']}"
    )

    print(
        f"Improvement  : "
        f"{comparison['improvement']}%"
    )