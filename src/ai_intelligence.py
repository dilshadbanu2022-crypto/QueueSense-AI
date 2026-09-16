class AIIntelligence:

    def __init__(self, max_counters=5):
        self.max_counters = max_counters

    # ==================================================
    # AI INTELLIGENCE ANALYSIS
    # ==================================================

    def analyze(self, state, prediction, decision=None):

        queue = state.get("queue_length", 0)
        arrivals = state.get("people_arriving", 0)
        served = state.get("people_served", 0)

        waiting = prediction.get(
            "predicted_waiting_time",
            prediction.get("waiting_time", 0)
        )

        future_crowd = prediction.get(
            "predicted_crowd",
            prediction.get("predicted_future_crowd", 0)
        )

        risk = prediction.get(
            "risk",
            prediction.get("risk_level", "LOW")
        )

        # Demand pressure
        demand_pressure = arrivals - served

        # ==================================================
        # USE THE AUTHORITATIVE AI DECISION
        # ==================================================

        if decision is not None:

            action = decision.get("action", "MONITOR")
            priority = decision.get("priority", "LOW")
            reason = decision.get(
                "reason",
                "Continue monitoring queue conditions"
            )
            new_counters = decision.get(
                "new_counters",
                state.get("active_counters", 1)
            )

        else:

            # Fallback if no decision is supplied
            action = "MONITOR"
            priority = risk
            reason = "Continue monitoring queue conditions"
            new_counters = state.get("active_counters", 1)

        # ==================================================
        # INTELLIGENCE EXPLANATION
        # ==================================================

        if action == "OPEN_COUNTER":

            explanation = (
                f"AI detected {risk.lower()} congestion with "
                f"predicted waiting time of {waiting:.2f} minutes. "
                f"Additional service capacity is recommended."
            )

        elif action == "MAX_COUNTERS":

            explanation = (
                "Congestion is high, but the maximum number "
                "of available counters is already active."
            )

        elif action == "PREPARE_COUNTER":

            explanation = (
                f"Demand pressure detected: {demand_pressure:+d} "
                "people. AI recommends preparing additional capacity."
            )

        elif action == "MONITOR":

            explanation = (
                f"Current conditions are being monitored. "
                f"Predicted future crowd: {future_crowd:.2f}."
            )

        elif action == "NO_ACTION":

            explanation = (
                "Queue conditions are stable and no intervention "
                "is currently required."
            )

        else:

            explanation = "AI is continuously monitoring queue conditions."

        # ==================================================
        # RETURN INTELLIGENCE RESULT
        # ==================================================

        return {
            "decision": action,
            "priority": priority,
            "reason": explanation,
            "action": action,
            "new_counters": new_counters,
            "risk": risk,
            "predicted_waiting_time": waiting,
            "predicted_future_crowd": future_crowd,
            "demand_pressure": demand_pressure
        }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print("\nQueueSense AI")
    print("AI Intelligence Engine Test")
    print("=" * 60)

    ai = AIIntelligence(max_counters=5)

    state = {
        "queue_length": 80,
        "active_counters": 3,
        "people_arriving": 20,
        "people_served": 8
    }

    prediction = {
        "predicted_waiting_time": 45,
        "predicted_crowd": 95,
        "risk": "HIGH"
    }

    decision = {
        "action": "OPEN_COUNTER",
        "priority": "CRITICAL",
        "reason": "High congestion and long waiting time",
        "new_counters": 4
    }

    result = ai.analyze(
        state,
        prediction,
        decision
    )

    print("\nAI INTELLIGENCE ANALYSIS")
    print("=" * 60)

    print("Decision       :", result["decision"])
    print("Priority       :", result["priority"])
    print("Reason         :", result["reason"])
    print("Action         :", result["action"])
    print("New Counters   :", result["new_counters"])

    print("\nFuture Crowd   :", result["predicted_future_crowd"])
    print("Waiting Time   :", result["predicted_waiting_time"])
    print("Risk           :", result["risk"])
    print("Demand Pressure:", result["demand_pressure"])