from autonomous_simulation import AutonomousQueueSimulation
from ml_prediction_engine import MLPredictionEngine
from ai_decision_engine import AIDecisionEngine
from ai_intelligence import AIIntelligence
from impact_measurement import ImpactMeasurement
from scenario_engine import ScenarioEngine

class SimulationEngine:

    def __init__(self):

        # ==================================================
        # AUTONOMOUS SIMULATION
        # ==================================================

        self.simulation = AutonomousQueueSimulation(
            initial_queue=20,
            initial_counters=3,
            max_counters=5,
            average_service_time=5,
            seed=42
        )

        # ==================================================
        # ML PREDICTION ENGINE
        # ==================================================

        self.ml_engine = MLPredictionEngine()

        # ==================================================
        # AI DECISION ENGINE
        # ==================================================

        self.decision_engine = AIDecisionEngine(
            max_counters=5
        )

        # ==================================================
        # AI INTELLIGENCE
        # ==================================================

        self.intelligence = AIIntelligence()

        # ==================================================
        # IMPACT MEASUREMENT
        # ==================================================

        self.impact = ImpactMeasurement()

        # ==================================================
        # SCENARIO ENGINE
        # ==================================================

        self.scenario_engine = ScenarioEngine(
            seed=42,
            max_counters=5
        )

        # ==================================================
        # PERFORMANCE
        # ==================================================

        self.total_steps = 0


    # ======================================================
    # RUN AUTONOMOUS SIMULATION
    # ======================================================

    def run(self, max_steps=300):

        print("\n")
        print("=" * 60)
        print("              QUEUESENSE AI")
        print("        AUTONOMOUS SIMULATION")
        print("=" * 60)

        # Start autonomous simulation

        self.simulation.start()

        # Previous state is empty at the beginning.
        # This avoids an unnecessary extra simulation step.

        previous_state = None
        previous_prediction = None


        # ==================================================
        # MAIN AUTONOMOUS LOOP
        # ==================================================

        for step in range(1, max_steps + 1):

            self.total_steps = step

            print("\n")
            print("=" * 60)
            print(f"SIMULATION STEP {step}")
            print("=" * 60)


            # ==================================================
            # GET CURRENT ARRIVAL MULTIPLIER
            # ==================================================

            multiplier = (
                self.scenario_engine.get_arrival_multiplier()
            )


            # ==================================================
            # AUTONOMOUS SIMULATION STEP
            # ==================================================

            state = self.simulation.step(
                arrival_multiplier=multiplier
            )


            # ==================================================
            # ML PREDICTION
            # ==================================================

            prediction = self.ml_engine.predict(
                state
            )


            # ==================================================
            # AI DECISION
            # ==================================================

            decision = self.decision_engine.decide(
                state,
                prediction
            )


            # ==================================================
            # GET AI ACTION
            # ==================================================

            action = decision.get(
                "action",
                "NO_ACTION"
            )

            new_counters = decision.get(
                "new_counters",
                state.get(
                    "active_counters",
                    1
                )
            )


            # ==================================================
            # APPLY AI COUNTER DECISION
            # ==================================================

            if action in [
                "OPEN_COUNTER",
                "INCREASE_COUNTERS",
                "PREPARE_COUNTER",
                "MAX_COUNTERS"
            ]:

                self.simulation.set_counters(
                    new_counters
                )


            # ==================================================
            # AI INTELLIGENCE
            # ==================================================

            intelligence = self.intelligence.analyze(
                state,
                prediction,
                decision
            )


            # ==================================================
            # IMPACT MEASUREMENT
            # ==================================================

            if (
                previous_state is not None
                and previous_prediction is not None
            ):

                impact_result = (
                    self.impact.calculate_next_step_impact(
                        previous_state,
                        state,
                        previous_prediction,
                        prediction
                    )
                )

            else:

                impact_result = {
                    "queue_improvement": 0,
                    "waiting_improvement": 0,
                    "positive": False
                }


            # ==================================================
            # RECORD CURRENT STATE
            # ==================================================

            self.impact.record_state(
                state,
                prediction,
                decision
            )


            # ==================================================
            # UPDATE PREVIOUS STATE
            # ==================================================

            previous_state = state
            previous_prediction = prediction


            # ==================================================
            # PRINT SIMULATION STATE
            # ==================================================

            print("\nSIMULATION STATE")
            print("-" * 60)

            print(
                f"Simulation Time   : "
                f"{state.get('simulation_time')}"
            )

            print(
                f"Scenario          : "
                f"{self.scenario_engine.get_scenario()}"
            )

            print(
                f"Arrival Multiplier : "
                f"{self.scenario_engine.get_arrival_multiplier():.1f}x"
            )

            print(
                f"Queue Length      : "
                f"{state.get('queue_length')}"
            )

            print(
                f"People Arriving   : "
                f"{state.get('people_arriving')}"
            )

            print(
                f"People Served     : "
                f"{state.get('people_served')}"
            )

            print(
                f"Current Crowd     : "
                f"{state.get('current_crowd')}"
            )

            print(
                f"Active Counters   : "
                f"{state.get('active_counters')}"
            )

            print(
                f"Staff Available   : "
                f"{state.get('staff_available')}"
            )


            # ==================================================
            # PRINT ML PREDICTION
            # ==================================================

            print("\nML PREDICTION")
            print("-" * 60)

            print(
                f"Predicted Waiting : "
                f"{prediction.get('predicted_waiting_time', 0):.2f} minutes"
            )

            print(
                f"Predicted Crowd   : "
                f"{prediction.get('predicted_crowd', 0):.2f}"
            )

            print(
                f"Risk Level        : "
                f"{prediction.get('risk', 'LOW')}"
            )


            # ==================================================
            # PRINT AI DECISION ENGINE
            # ==================================================

            print("\nAI DECISION ENGINE")
            print("-" * 60)

            print(
                f"Action            : "
                f"{action}"
            )

            print(
                f"Priority          : "
                f"{decision.get('priority', 'NORMAL')}"
            )

            print(
                f"Reason            : "
                f"{decision.get('reason', '')}"
            )

            print(
                f"New Counters      : "
                f"{new_counters}"
            )


            # ==================================================
            # PRINT AI INTELLIGENCE
            # ==================================================

            print("\nAI INTELLIGENCE")
            print("-" * 60)

            print(
                f"Decision          : "
                f"{intelligence.get('decision', action)}"
            )

            print(
                f"Priority          : "
                f"{intelligence.get('priority', 'NORMAL')}"
            )

            print(
                f"Reason            : "
                f"{intelligence.get('reason', '')}"
            )


            # ==================================================
            # PRINT AI ACTION
            # ==================================================

            print("\nAI ACTION")
            print("-" * 60)

            print(
                f"Action       : "
                f"{action}"
            )

            print(
                f"Priority     : "
                f"{decision.get('priority', 'NORMAL')}"
            )

            print(
                f"Reason       : "
                f"{decision.get('reason', '')}"
            )


            if action == "MAX_COUNTERS":

                print(
                    "Maximum counters already active."
                )

            elif action in [
                "OPEN_COUNTER",
                "INCREASE_COUNTERS"
            ]:

                print(
                    f"Counter level changed to "
                    f"{new_counters}."
                )

            elif action == "PREPARE_COUNTER":

                print(
                    "AI recommends preparing "
                    "an additional counter."
                )

            else:

                print(
                    "No intervention required."
                )


            # ==================================================
            # PRINT IMPACT
            # ==================================================

            print("\nAI IMPACT MEASUREMENT")
            print("-" * 60)

            print(
                f"Queue Improvement   : "
                f"{impact_result['queue_improvement']:.2f}%"
            )

            print(
                f"Waiting Improvement : "
                f"{impact_result['waiting_improvement']:.2f}%"
            )

            print(
                f"Positive Outcome    : "
                f"{impact_result['positive']}"
            )


            # ==================================================
            # SCENARIO UPDATE
            # ==================================================

            old_scenario = (
                self.scenario_engine.get_scenario()
            )

            new_scenario = (
                self.scenario_engine.update_scenario(
                    state,
                    prediction
                )
            )


            # ==================================================
            # SCENARIO TRANSITION
            # ==================================================

            if new_scenario != old_scenario:

                print("\nSCENARIO TRANSITION")
                print("-" * 60)

                print(
                    f"{old_scenario} -> "
                    f"{new_scenario}"
                )

                print(
                    f"Next Arrival Multiplier : "
                    f"{self.scenario_engine.get_arrival_multiplier():.1f}x"
                )


            # ==================================================
            # AUTONOMOUS STABILIZATION
            # ==================================================

            current_queue = state.get(
                "queue_length",
                0
            )

            current_waiting = prediction.get(
                "predicted_waiting_time",
                0
            )


            # --------------------------------------------------
            # Stop when ScenarioEngine itself reaches
            # STABILIZATION.
            #
            # This is state-based, not time-based.
            # --------------------------------------------------

            if new_scenario == "STABILIZATION":

                print("\n")
                print("=" * 60)
                print("      AUTONOMOUS SYSTEM STABILIZED")
                print("=" * 60)

                print(
                    f"Final Queue       : "
                    f"{current_queue}"
                )

                print(
                    f"Final Waiting     : "
                    f"{current_waiting:.2f} minutes"
                )

                print(
                    f"Final Risk        : "
                    f"{prediction.get('risk', 'LOW')}"
                )

                break


        else:

            print("\n")
            print("=" * 60)
            print("MAXIMUM SIMULATION STEPS REACHED")
            print("=" * 60)


        # ======================================================
        # FINAL PERFORMANCE SUMMARY
        # ======================================================

        self.print_final_summary()


    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    def print_final_summary(self):

        summary = self.impact.get_summary()

        print("\n")
        print("=" * 60)
        print("       FINAL AI PERFORMANCE SUMMARY")
        print("=" * 60)

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
        # POSITIVE OUTCOME RATE
        # ==================================================

        if summary["total_steps"] > 0:

            positive_rate = (
                summary["positive_actions"]
                / summary["total_steps"]
            ) * 100

        else:

            positive_rate = 0


        print(
            f"Positive Outcome Rate : "
            f"{positive_rate:.2f}%"
        )


        # ==================================================
        # FINAL SCENARIO STATUS
        # ==================================================

        print("\n")
        print("=" * 60)
        print("FINAL SCENARIO STATUS")
        print("=" * 60)

        print(
            f"Scenario            : "
            f"{self.scenario_engine.get_scenario()}"
        )

        print(
            f"Arrival Multiplier  : "
            f"{self.scenario_engine.get_arrival_multiplier():.1f}x"
        )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    engine = SimulationEngine()

    engine.run(
        max_steps=300
    )