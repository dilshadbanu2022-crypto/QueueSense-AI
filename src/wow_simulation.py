import time

from autonomous_simulation import AutonomousQueueSimulation
from ml_prediction_engine import MLPredictionEngine
from ai_decision_engine import AIDecisionEngine
from ai_intelligence import AIIntelligence
from scenario_engine import ScenarioEngine
from impact_measurement import ImpactMeasurement


class WOWSimulation:

    def __init__(self):

        print("\n" + "=" * 70)
        print("QUEUE SENSE AI")
        print("AUTONOMOUS WOW SIMULATION")
        print("=" * 70)

        self.simulation = AutonomousQueueSimulation(
            initial_queue=20,
            initial_counters=3,
            max_counters=5,
            average_service_time=5,
            seed=42
        )

        self.ml_engine = MLPredictionEngine()

        self.decision_engine = AIDecisionEngine(
            max_counters=5
        )

        self.intelligence = AIIntelligence(
            max_counters=5
        )

        self.scenario_engine = ScenarioEngine(
            seed=42
        )

        self.impact = ImpactMeasurement()

        self.simulation.start()

    # ---------------------------------------------------------
    # GET PREDICTION VALUE
    # ---------------------------------------------------------

    def get_prediction_value(
        self,
        prediction,
        possible_keys,
        default=0
    ):

        for key in possible_keys:

            if key in prediction:
                return prediction[key]

        return default

    # ---------------------------------------------------------
    # NORMALIZE ML PREDICTION
    # ---------------------------------------------------------

    def normalize_prediction(
        self,
        prediction,
        state
    ):

        waiting_time = self.get_prediction_value(
            prediction,
            [
                "predicted_waiting_time",
                "waiting_time",
                "predicted_wait",
                "waiting_prediction"
            ],
            state.get("waiting_time", 0)
        )

        future_crowd = self.get_prediction_value(
            prediction,
            [
                "predicted_future_crowd",
                "future_crowd",
                "predicted_crowd",
                "crowd_prediction",
                "predicted_crowd_level"
            ],
            state.get("current_crowd", 0)
        )

        risk = self.get_prediction_value(
            prediction,
            [
                "risk",
                "risk_level",
                "crowd_risk",
                "predicted_risk"
            ],
            state.get("crowd_level", "LOW")
        )

        return {
            "predicted_waiting_time": float(
                waiting_time
            ),

            "predicted_future_crowd": float(
                future_crowd
            ),

            "risk": str(risk)
        }

    # ---------------------------------------------------------
    # APPLY AI DECISION
    # ---------------------------------------------------------

    def apply_decision(
        self,
        decision
    ):

        action = decision.get(
            "action",
            "MONITOR"
        )

        priority = decision.get(
            "priority",
            "LOW"
        )

        reason = decision.get(
            "reason",
            "System is monitoring the queue."
        )

        new_counters = decision.get(
            "new_counters",
            self.simulation.active_counters
        )

        print("\n🤖 AI DECISION")
        print("-" * 70)

        print(
            f"Action       : {action}"
        )

        print(
            f"Priority     : {priority}"
        )

        print(
            f"Reason       : {reason}"
        )

        # -------------------------------------------------
        # OPEN COUNTER
        # -------------------------------------------------

        if action == "OPEN_COUNTER":

            current = (
                self.simulation.active_counters
            )

            if new_counters > current:

                print(
                    "\n🚀 AUTOMATIC INTERVENTION"
                )

                print(
                    f"Counter {new_counters} "
                    f"ACTIVATED"
                )

                self.simulation.set_counters(
                    new_counters
                )

                return "COUNTER_ACTIVATED"

            else:

                print(
                    "\n⚠ Counter limit reached."
                )

                return "MAX_CAPACITY"

        # -------------------------------------------------
        # MAX COUNTERS
        # -------------------------------------------------

        elif action == "MAX_COUNTERS":

            print(
                "\n⚠ MAXIMUM COUNTERS ACTIVE"
            )

            return "MAX_CAPACITY"

        # -------------------------------------------------
        # PREPARE COUNTER
        # -------------------------------------------------

        elif action == "PREPARE_COUNTER":

            print(
                "\n🟡 AI PREPARATION"
            )

            print(
                "Additional counter should be prepared."
            )

            return "PREPARE_COUNTER"

        # -------------------------------------------------
        # NO ACTION
        # -------------------------------------------------

        elif action == "NO_ACTION":

            print(
                "\n✓ NO ACTION REQUIRED"
            )

            return "NO_ACTION"

        # -------------------------------------------------
        # MONITOR
        # -------------------------------------------------

        else:

            print(
                "\n👁 AI MONITORING"
            )

            return "MONITOR"

    # ---------------------------------------------------------
    # SCENARIO ARRIVAL GENERATOR
    # ---------------------------------------------------------

    def generate_scenario_arrivals(
        self,
        base_arrivals,
        multiplier
    ):

        arrivals = int(
            base_arrivals * multiplier
        )

        return max(
            0,
            arrivals
        )

    # ---------------------------------------------------------
    # RUN ONE STEP
    # ---------------------------------------------------------

    def run_step(self):

        # ---------------------------------------------
        # BEFORE STATE
        # ---------------------------------------------

        before_state = (
            self.simulation.get_state()
        )

        before_queue = (
            before_state["queue_length"]
        )

        before_wait = (
            before_state["waiting_time"]
        )

        before_counters = (
            before_state["active_counters"]
        )

        # ---------------------------------------------
        # NORMAL SIMULATION STEP
        # ---------------------------------------------

        state = self.simulation.step(
    self.scenario_engine.get_arrival_multiplier()
)

        # ---------------------------------------------
        # ML PREDICTION
        # ---------------------------------------------

        prediction = (
            self.ml_engine.predict(state)
        )

        normalized = (
            self.normalize_prediction(
                prediction,
                state
            )
        )

        predicted_wait = (
            normalized[
                "predicted_waiting_time"
            ]
        )

        predicted_crowd = (
            normalized[
                "predicted_future_crowd"
            ]
        )

        risk = (
            normalized["risk"]
        )

        # ---------------------------------------------
        # SCENARIO UPDATE
        # ---------------------------------------------

        scenario_prediction = {

            "predicted_waiting_time":
                predicted_wait,

            "predicted_future_crowd":
                predicted_crowd,

            "risk":
                risk
        }

        self.scenario_engine.update_scenario(
            state,
            scenario_prediction
        )

        scenario = (
            self.scenario_engine.get_scenario()
        )

        multiplier = (
            self.scenario_engine
            .get_arrival_multiplier()
        )

        # ---------------------------------------------
        # AI DECISION
        # ---------------------------------------------

        decision = (
            self.decision_engine.decide(
                state,
                prediction
            )
        )

        # ---------------------------------------------
        # AI INTELLIGENCE
        # ---------------------------------------------

        intelligence = (
            self.intelligence.analyze(
                state,
                prediction
            )
        )

        # ---------------------------------------------
        # DISPLAY
        # ---------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            f"SIMULATION TIME : "
            f"{state['simulation_time']}"
        )

        print(
            f"SCENARIO        : "
            f"{scenario}"
        )

        print(
            f"MULTIPLIER      : "
            f"{multiplier:.1f}x"
        )

        print(
            "=" * 70
        )

        print(
            f"Arrivals        : "
            f"{state['people_arriving']}"
        )

        print(
            f"Served          : "
            f"{state['people_served']}"
        )

        print(
            f"Queue           : "
            f"{state['queue_length']}"
        )

        print(
            f"Current Crowd   : "
            f"{state['current_crowd']}"
        )

        print(
            f"Counters        : "
            f"{state['active_counters']}"
        )

        print(
            f"Waiting Time    : "
            f"{predicted_wait:.2f} min"
        )

        print(
            f"Future Crowd    : "
            f"{predicted_crowd:.2f}"
        )

        print(
            f"Risk            : "
            f"{risk}"
        )

        # ---------------------------------------------
        # APPLY AI ACTION
        # ---------------------------------------------

        intervention = (
            self.apply_decision(
                decision
            )
        )

        # ---------------------------------------------
        # AFTER STATE
        # ---------------------------------------------

        after_state = (
            self.simulation.get_state()
        )

        after_queue = (
            after_state["queue_length"]
        )

        after_wait = (
            after_state["waiting_time"]
        )

        after_counters = (
            after_state["active_counters"]
        )

        # ---------------------------------------------
        # IMPACT CALCULATION
        # ---------------------------------------------

        if before_queue > 0:

            queue_change = (
                (
                    after_queue -
                    before_queue
                )
                / before_queue
            ) * 100

        else:

            queue_change = 0

        if before_wait > 0:

            wait_change = (
                (
                    after_wait -
                    before_wait
                )
                / before_wait
            ) * 100

        else:

            wait_change = 0

        # ---------------------------------------------
        # IMPACT DISPLAY
        # ---------------------------------------------

        print(
            "\n📊 IMPACT MEASUREMENT"
        )

        print(
            "-" * 70
        )

        print(
            f"Queue Before    : "
            f"{before_queue}"
        )

        print(
            f"Queue After     : "
            f"{after_queue}"
        )

        print(
            f"Waiting Before  : "
            f"{before_wait:.2f} min"
        )

        print(
            f"Waiting After   : "
            f"{after_wait:.2f} min"
        )

        print(
            f"Counters        : "
            f"{before_counters} → "
            f"{after_counters}"
        )

        # ---------------------------------------------
        # SMART LABELS
        # ---------------------------------------------

        if queue_change > 0:

            print(
                f"Queue Increase  : "
                f"{queue_change:.2f}%"
            )

        elif queue_change < 0:

            print(
                f"Queue Reduction : "
                f"{abs(queue_change):.2f}%"
            )

        else:

            print(
                "Queue Change    : 0.00%"
            )

        if wait_change > 0:

            print(
                f"Waiting Increase: "
                f"{wait_change:.2f}%"
            )

        elif wait_change < 0:

            print(
                f"Waiting Reduction: "
                f"{abs(wait_change):.2f}%"
            )

        else:

            print(
                "Waiting Change  : 0.00%"
            )

        print(
            f"Intervention    : "
            f"{intervention}"
        )

        # ---------------------------------------------
        # RECORD IMPACT
        # ---------------------------------------------

        self.impact.record_state(
            after_state,
            prediction,
            decision
        )

        return {

            "state":
                after_state,

            "prediction":
                normalized,

            "decision":
                decision,

            "intelligence":
                intelligence,

            "scenario":
                scenario,

            "multiplier":
                multiplier,

            "intervention":
                intervention,

            "queue_change":
                queue_change,

            "wait_change":
                wait_change
        }

    # ---------------------------------------------------------
    # RUN AUTONOMOUS SIMULATION
    # ---------------------------------------------------------

    def run(
        self,
        steps=20,
        delay=1
    ):

        print(
            "\n🚀 AUTONOMOUS MODE STARTED"
        )

        print(
            "PREDICT → DECIDE → ACT → MEASURE → REPEAT"
        )

        for step in range(steps):

            print(
                f"\n\n######## STEP "
                f"{step + 1} ########"
            )

            self.run_step()

            time.sleep(delay)

        # ---------------------------------------------
        # FINAL SUMMARY
        # ---------------------------------------------

        print(
            "\n\n" + "=" * 70
        )

        print(
            "AUTONOMOUS WOW SIMULATION COMPLETED"
        )

        print(
            "=" * 70
        )

        self.impact.display_summary()


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    wow = WOWSimulation()

    wow.run(
        steps=20,
        delay=1
    )