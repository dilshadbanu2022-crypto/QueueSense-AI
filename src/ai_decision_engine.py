class AIDecisionEngine:

    def __init__(self, max_counters=5):
        self.max_counters = max_counters

    def decide(self, state, prediction):

        queue = state.get("queue_length", 0)
        counters = state.get("active_counters", 1)

        waiting = prediction.get(
            "predicted_waiting_time",
            prediction.get("waiting_time", 0)
        )

        risk = prediction.get(
            "risk",
            prediction.get("risk_level", "LOW")
        )

        # ==================================================
        # HIGH / CRITICAL RISK
        # ==================================================

        if risk in ["HIGH", "CRITICAL"]:

            if waiting > 40 or queue >= 30:

                if counters < self.max_counters:

                    return {
                        "action": "OPEN_COUNTER",
                        "priority": "CRITICAL",
                        "reason": "High congestion and long waiting time",
                        "new_counters": counters + 1
                    }

                return {
                    "action": "MAX_COUNTERS",
                    "priority": "CRITICAL",
                    "reason": "Maximum counters already active",
                    "new_counters": counters
                }

            if waiting > 25 or queue >= 20:

                if counters < self.max_counters:

                    return {
                        "action": "OPEN_COUNTER",
                        "priority": "HIGH",
                        "reason": "High congestion requires additional counter",
                        "new_counters": counters + 1
                    }

                return {
                    "action": "MAX_COUNTERS",
                    "priority": "HIGH",
                    "reason": "Maximum counters already active",
                    "new_counters": counters
                }

        # ==================================================
        # MEDIUM RISK
        # ==================================================

        if risk == "MEDIUM":

            # Serious medium congestion
            # Automatically open a counter
            if waiting > 28 or queue >= 25:

                if counters < self.max_counters:

                    return {
                        "action": "OPEN_COUNTER",
                        "priority": "HIGH",
                        "reason": "Medium congestion is becoming critical",
                        "new_counters": counters + 1
                    }

                return {
                    "action": "MAX_COUNTERS",
                    "priority": "HIGH",
                    "reason": "Maximum counters already active",
                    "new_counters": counters
                }

            # Moderate congestion
            if waiting > 15:

                return {
                    "action": "PREPARE_COUNTER",
                    "priority": "MEDIUM",
                    "reason": "Medium congestion with increasing waiting time",
                    "new_counters": counters
                }

            return {
                "action": "MONITOR",
                "priority": "MEDIUM",
                "reason": "Moderate congestion detected",
                "new_counters": counters
            }

        # ==================================================
        # LOW RISK
        # ==================================================

        if risk == "LOW":

            if waiting < 10 and queue < 10:

                return {
                    "action": "NO_ACTION",
                    "priority": "LOW",
                    "reason": "Conditions are stable",
                    "new_counters": counters
                }

            return {
                "action": "MONITOR",
                "priority": "LOW",
                "reason": "Continue monitoring queue conditions",
                "new_counters": counters
            }

        # ==================================================
        # DEFAULT
        # ==================================================

        return {
            "action": "MONITOR",
            "priority": "LOW",
            "reason": "No immediate intervention required",
            "new_counters": counters
        }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    engine = AIDecisionEngine(max_counters=5)

    test_state = {
        "queue_length": 20,
        "active_counters": 3
    }

    test_prediction = {
        "predicted_waiting_time": 31.82,
        "risk": "MEDIUM"
    }

    decision = engine.decide(
        test_state,
        test_prediction
    )

    print("\nQueueSense AI")
    print("AI Decision Engine Test")
    print("=" * 50)

    print("\nAI DECISION")
    print("=" * 50)

    print(
        f"Action       : {decision['action']}"
    )

    print(
        f"Priority     : {decision['priority']}"
    )

    print(
        f"Reason       : {decision['reason']}"
    )

    print(
        f"New Counters : {decision['new_counters']}"
    )