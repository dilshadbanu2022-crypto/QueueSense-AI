class ImpactMeasurement:

    def __init__(self):

        self.records = []

        self.total_ai_actions = 0

        self.positive_actions = 0

        self.peak_queue = 0

        self.peak_waiting_time = 0

    # ==================================================
    # RECORD STATE
    # ==================================================

    def record_state(
        self,
        state,
        prediction,
        decision
    ):

        queue = state["queue_length"]

        waiting_time = prediction[
            "predicted_waiting_time"
        ]

        counters = state[
            "active_counters"
        ]

        risk = prediction["risk"]

        action = decision["action"]

        # Update peaks
        self.peak_queue = max(
            self.peak_queue,
            queue
        )

        self.peak_waiting_time = max(
            self.peak_waiting_time,
            waiting_time
        )

        record = {

            "step":
                len(self.records) + 1,

            "queue":
                queue,

            "waiting_time":
                round(
                    waiting_time,
                    2
                ),

            "counters":
                counters,

            "risk":
                risk,

            "action":
                action
        }

        self.records.append(record)

        # Count meaningful AI interventions
        if action in [
            "OPEN_COUNTER",
            "PREPARE_COUNTER",
            "MAX_COUNTERS"
        ]:

            self.total_ai_actions += 1

    # ==================================================
    # CALCULATE IMPACT
    # ==================================================

    def calculate_impact(
        self,
        before_queue,
        after_queue,
        before_wait,
        after_wait
    ):

        # ----------------------------------------------
        # Queue improvement
        # ----------------------------------------------

        if before_queue > 0:

            queue_improvement = (
                (
                    before_queue
                    - after_queue
                )
                / before_queue
            ) * 100

        else:

            queue_improvement = 0

        # ----------------------------------------------
        # Waiting-time improvement
        # ----------------------------------------------

        if before_wait > 0:

            waiting_improvement = (
                (
                    before_wait
                    - after_wait
                )
                / before_wait
            ) * 100

        else:

            waiting_improvement = 0

        # ----------------------------------------------
        # Determine whether outcome improved
        # ----------------------------------------------

        positive = (
            queue_improvement > 0
            or waiting_improvement > 0
        )

        if positive:

            self.positive_actions += 1

        return {

            "queue_improvement":
                round(
                    queue_improvement,
                    2
                ),

            "waiting_improvement":
                round(
                    waiting_improvement,
                    2
                ),

            "positive":
                positive
        }

    # ==================================================
    # CALCULATE NEXT-STEP IMPACT
    # ==================================================

    def calculate_next_step_impact(
        self,
        before_state,
        after_state,
        before_prediction,
        after_prediction
    ):

        before_queue = before_state[
            "queue_length"
        ]

        after_queue = after_state[
            "queue_length"
        ]

        before_wait = before_prediction[
            "predicted_waiting_time"
        ]

        after_wait = after_prediction[
            "predicted_waiting_time"
        ]

        return self.calculate_impact(
            before_queue,
            after_queue,
            before_wait,
            after_wait
        )

    # ==================================================
    # GENERATE SUMMARY
    # ==================================================

    def get_summary(self):

        if not self.records:

            return {

                "total_steps": 0,

                "peak_queue": 0,

                "peak_waiting_time": 0,

                "total_ai_actions": 0,

                "positive_actions": 0
            }

        return {

            "total_steps":
                len(self.records),

            "peak_queue":
                self.peak_queue,

            "peak_waiting_time":
                round(
                    self.peak_waiting_time,
                    2
                ),

            "total_ai_actions":
                self.total_ai_actions,

            "positive_actions":
                self.positive_actions
        }

    # ==================================================
    # DISPLAY SUMMARY
    # ==================================================

    def display_summary(self):

        summary = self.get_summary()

        print("\n")
        print("=" * 60)
        print("AI IMPACT MEASUREMENT")
        print("=" * 60)

        print(
            f"Total Steps       : "
            f"{summary['total_steps']}"
        )

        print(
            f"Peak Queue        : "
            f"{summary['peak_queue']}"
        )

        print(
            f"Peak Waiting Time : "
            f"{summary['peak_waiting_time']} minutes"
        )

        print(
            f"AI Actions        : "
            f"{summary['total_ai_actions']}"
        )

        print(
            f"Positive Actions  : "
            f"{summary['positive_actions']}"
        )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print("\nQueueSense AI")
    print("Impact Measurement Test")
    print("=" * 60)

    impact = ImpactMeasurement()

    # ----------------------------------------------
    # BEFORE AI ACTION
    # ----------------------------------------------

    before_queue = 100
    before_wait = 60

    # ----------------------------------------------
    # AFTER AI ACTION
    # ----------------------------------------------

    after_queue = 70
    after_wait = 40

    result = impact.calculate_impact(
        before_queue,
        after_queue,
        before_wait,
        after_wait
    )

    print("\nIMPACT RESULT")
    print("=" * 60)

    print(
        f"Queue Improvement   : "
        f"{result['queue_improvement']}%"
    )

    print(
        f"Waiting Improvement : "
        f"{result['waiting_improvement']}%"
    )

    print(
        f"Positive Outcome    : "
        f"{result['positive']}"
    )

    # ----------------------------------------------
    # RECORD TEST STATE
    # ----------------------------------------------

    test_state = {

        "queue_length": 70,

        "active_counters": 4
    }

    test_prediction = {

        "predicted_waiting_time": 40,

        "risk": "MEDIUM"
    }

    test_decision = {

        "action": "OPEN_COUNTER"
    }

    impact.record_state(
        test_state,
        test_prediction,
        test_decision
    )

    # ----------------------------------------------
    # DISPLAY SUMMARY
    # ----------------------------------------------

    impact.display_summary()