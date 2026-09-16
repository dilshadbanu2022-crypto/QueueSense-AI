import os
import joblib
import pandas as pd


class MLPredictionEngine:

    def __init__(self):

        # =====================================================
        # FIND PROJECT DIRECTORY
        # =====================================================

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        models_dir = os.path.join(
            base_dir,
            "models"
        )

        # =====================================================
        # MODEL PATHS
        # =====================================================

        waiting_model_path = os.path.join(
            models_dir,
            "waiting_time_model.pkl"
        )

        crowd_model_path = os.path.join(
            models_dir,
            "crowd_prediction_model.pkl"
        )

        risk_model_path = os.path.join(
            models_dir,
            "crowd_risk_model.pkl"
        )

        # =====================================================
        # LOAD ML MODELS
        # =====================================================

        self.waiting_model = joblib.load(
            waiting_model_path
        )

        self.crowd_model = joblib.load(
            crowd_model_path
        )

        self.risk_model = joblib.load(
            risk_model_path
        )

        print("✓ Waiting-Time model loaded")
        print("✓ Crowd Prediction model loaded")
        print("✓ Crowd Risk model loaded")

    # =========================================================
    # CREATE FEATURES
    # =========================================================

    def create_features(self, state):

        # -----------------------------------------------------
        # Convert simulation time into pandas datetime
        # -----------------------------------------------------

        simulation_time = pd.Timestamp(
            "2026-01-01 "
            + state["simulation_time"]
        )

        # -----------------------------------------------------
        # Time features
        # -----------------------------------------------------

        hour = simulation_time.hour

        day_of_week = simulation_time.dayofweek

        year = simulation_time.year

        month = simulation_time.month

        day = simulation_time.day

        # -----------------------------------------------------
        # Service type
        #
        # OPD = 1
        # -----------------------------------------------------

        service_type = 1

        # -----------------------------------------------------
        # Average service time
        # -----------------------------------------------------

        average_service_time = state.get(
            "average_service_time",
            5
        )

        if average_service_time <= 0:

            average_service_time = 5

        # -----------------------------------------------------
        # Capacity
        #
        # Same logic used during model training
        # -----------------------------------------------------

        capacity = (
            state["active_counters"]
            * 10
            / average_service_time
        )

        # -----------------------------------------------------
        # Future crowd estimate
        # -----------------------------------------------------

        future_crowd_estimate = max(
            0,
            state["current_crowd"]
            + state["people_arriving"]
            - state["people_served"]
        )

        # =====================================================
        # CREATE FEATURE DICTIONARY
        # =====================================================

        features = {

            "day_of_week":
                day_of_week,

            "hour":
                hour,

            "service_type":
                service_type,

            "queue_length":
                state["queue_length"],

            "people_arriving":
                state["people_arriving"],

            "people_served":
                state["people_served"],

            "active_counters":
                state["active_counters"],

            "staff_available":
                state["staff_available"],

            "average_service_time":
                average_service_time,

            "capacity":
                capacity,

            "holiday":
                0,

            "current_crowd":
                state["current_crowd"],

            "future_crowd":
                future_crowd_estimate,

            "year":
                year,

            "month":
                month,

            "day":
                day
        }

        return pd.DataFrame(
            [features]
        )

    # =========================================================
    # PREDICT WAITING TIME, CROWD AND RISK
    # =========================================================

    def predict(self, state):

        # -----------------------------------------------------
        # Create ML features
        # -----------------------------------------------------

        features = self.create_features(
            state
        )

        # =====================================================
        # WAITING TIME PREDICTION
        # =====================================================

        predicted_waiting = (
            self.waiting_model.predict(
                features
            )[0]
        )

        # =====================================================
        # CROWD PREDICTION
        # =====================================================

        # future_crowd is the target for the crowd model,
        # therefore it must NOT be provided as an input.

        crowd_features = features.drop(
            columns=[
                "future_crowd"
            ]
        )

        predicted_crowd = (
            self.crowd_model.predict(
                crowd_features
            )[0]
        )

        # =====================================================
        # CROWD RISK PREDICTION
        # =====================================================

        predicted_risk = (
            self.risk_model.predict(
                crowd_features
            )[0]
        )

        # =====================================================
        # CONVERT RISK CODE TO TEXT
        # =====================================================

        risk_names = {

            0: "LOW",

            1: "MEDIUM",

            2: "HIGH"
        }

        risk_level = risk_names.get(
            int(predicted_risk),
            "UNKNOWN"
        )

        # =====================================================
        # RETURN PREDICTIONS
        # =====================================================

        return {

            "predicted_waiting_time":
                round(
                    max(
                        0,
                        float(
                            predicted_waiting
                        )
                    ),
                    2
                ),

            "predicted_crowd":
                round(
                    max(
                        0,
                        float(
                            predicted_crowd
                        )
                    ),
                    2
                ),

            "risk":
                risk_level,

            "risk_code":
                int(
                    predicted_risk
                )
        }


# ============================================================
# TEST ML PREDICTION ENGINE
# ============================================================

if __name__ == "__main__":

    print("\nQueueSense AI")
    print("ML Prediction Engine Test")
    print("=" * 50)

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    engine = MLPredictionEngine()

    # --------------------------------------------------------
    # Create test simulation state
    # --------------------------------------------------------

    test_state = {

        "simulation_time":
            "10:00:00",

        "queue_length":
            50,

        "people_arriving":
            15,

        "people_served":
            10,

        "current_crowd":
            55,

        "active_counters":
            3,

        "staff_available":
            4,

        "average_service_time":
            5
    }

    # --------------------------------------------------------
    # Run prediction
    # --------------------------------------------------------

    result = engine.predict(
        test_state
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\nML PREDICTION")
    print("=" * 50)

    print(
        "Predicted Waiting Time:",
        result["predicted_waiting_time"],
        "minutes"
    )

    print(
        "Predicted Future Crowd:",
        result["predicted_crowd"]
    )

    print(
        "Risk:",
        result["risk"]
    )

    print(
        "Risk Code:",
        result["risk_code"]
    )