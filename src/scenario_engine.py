import random


class ScenarioEngine:

    def __init__(self, seed=42, max_counters=5):
        self.random = random.Random(seed)

        self.max_counters = max_counters

        self.scenario = "NORMAL"
        self.arrival_multiplier = 1.0

        self.stress_steps = 0
        self.recovery_steps = 0
        self.stable_steps = 0

        # Tracks the previous queue to detect real improvement
        self.previous_queue = 0

    def update_scenario(self, state, prediction):

        queue = state.get("queue_length", 0)
        arrivals = state.get("people_arriving", 0)
        served = state.get("people_served", 0)
        counters = state.get("active_counters", 1)

        waiting = prediction.get(
            "predicted_waiting_time",
            prediction.get("waiting_time", 0)
        )

        risk = prediction.get(
            "risk",
            prediction.get("risk_level", "LOW")
        )

        demand_pressure = arrivals - served

        # ==========================================================
        # NORMAL
        # ==========================================================

        if self.scenario == "NORMAL":

            pressure_detected = (
                demand_pressure > 0
                and (
                    queue >= 18
                    or waiting >= 25
                    or risk in ["HIGH", "CRITICAL"]
                )
            )

            if pressure_detected:
                self.stress_steps += 1
            else:
                self.stress_steps = max(
                    0,
                    self.stress_steps - 1
                )

            # Persistent pressure -> SURGE
            if self.stress_steps >= 2:

                self.scenario = "SURGE"
                self.arrival_multiplier = 1.8

                self.stress_steps = 0
                self.recovery_steps = 0
                self.stable_steps = 0
                self.previous_queue = queue

                return self.scenario

            self.arrival_multiplier = 1.0

        # ==========================================================
        # SURGE
        # ==========================================================

        elif self.scenario == "SURGE":

            # If maximum counters are active,
            # automatically reduce demand.

            if counters >= self.max_counters:

                if queue >= 120 or waiting >= 120:

                    self.arrival_multiplier = max(
                        0.6,
                        self.arrival_multiplier - 0.25
                    )

                elif queue >= 80 or waiting >= 80:

                    self.arrival_multiplier = max(
                        0.7,
                        self.arrival_multiplier - 0.20
                    )

                elif queue >= 50 or waiting >= 50:

                    self.arrival_multiplier = max(
                        0.8,
                        self.arrival_multiplier - 0.15
                    )

                else:

                    self.arrival_multiplier = max(
                        1.0,
                        self.arrival_multiplier - 0.10
                    )

            else:

                # Keep demand high while additional
                # service capacity is still available.

                self.arrival_multiplier = min(
                    1.8,
                    self.arrival_multiplier + 0.05
                )

            # ------------------------------------------------------
            # Detect recovery
            # ------------------------------------------------------

            recovery_detected = (
                served >= arrivals
                and queue > 0
                and waiting < 100
            )

            if recovery_detected:
                self.recovery_steps += 1
            else:
                self.recovery_steps = 0

            # Move to RECOVERY after sustained improvement
            if (
                counters >= self.max_counters
                and self.recovery_steps >= 2
            ):

                self.scenario = "RECOVERY"
                self.arrival_multiplier = 0.7

                self.recovery_steps = 0
                self.stable_steps = 0
                self.stress_steps = 0

                self.previous_queue = queue

                return self.scenario

        # ==========================================================
        # RECOVERY
        # ==========================================================

        elif self.scenario == "RECOVERY":

            # Keep arrivals below normal so the queue
            # has an opportunity to decrease.

            if queue > 80:

                self.arrival_multiplier = 0.6

            elif queue > 40:

                self.arrival_multiplier = 0.7

            elif queue > 20:

                self.arrival_multiplier = 0.8

            else:

                self.arrival_multiplier = 0.9

            # ------------------------------------------------------
            # Detect genuine improvement
            # ------------------------------------------------------

            improving = (
                queue < self.previous_queue
                and served >= arrivals
            )

            if improving:
                self.stable_steps += 1
            else:
                self.stable_steps = 0

            # Save current queue for the next step
            self.previous_queue = queue

            # ------------------------------------------------------
            # RECOVERY -> STABILIZATION
            # ------------------------------------------------------

            if self.stable_steps >= 3:

                self.scenario = "STABILIZATION"
                self.arrival_multiplier = 1.0

                self.stable_steps = 0
                self.recovery_steps = 0
                self.stress_steps = 0

                return self.scenario

            # ------------------------------------------------------
            # Detect serious deterioration
            # ------------------------------------------------------

            congestion_returning = (
                queue >= 100
                and demand_pressure > 5
            )

            if congestion_returning:
                self.stress_steps += 1
            else:
                self.stress_steps = 0

            # Serious congestion -> SURGE
            if self.stress_steps >= 2:

                self.scenario = "SURGE"
                self.arrival_multiplier = 1.8

                self.stress_steps = 0
                self.recovery_steps = 0
                self.stable_steps = 0

                self.previous_queue = queue

                return self.scenario

        # ==========================================================
        # STABILIZATION
        # ==========================================================

        elif self.scenario == "STABILIZATION":

            # Normal operating demand
            self.arrival_multiplier = 1.0

            # Only consider genuine congestion,
            # not ML risk by itself.

            congestion_returning = (
                demand_pressure > 5
                and (
                    queue >= 50
                    or waiting >= 60
                )
            )

            if congestion_returning:
                self.stress_steps += 1
            else:
                self.stress_steps = 0

            # Congestion returns -> new SURGE
            if self.stress_steps >= 2:

                self.scenario = "SURGE"
                self.arrival_multiplier = 1.8

                self.stress_steps = 0
                self.recovery_steps = 0
                self.stable_steps = 0

                self.previous_queue = queue

                return self.scenario

        return self.scenario

    # ==============================================================
    # ARRIVAL GENERATOR
    # ==============================================================

    def generate_arrivals(self, base_arrivals):

        arrivals = int(
            base_arrivals * self.arrival_multiplier
        )

        variation = self.random.randint(-2, 3)

        return max(
            0,
            arrivals + variation
        )

    # ==============================================================
    # GETTERS
    # ==============================================================

    def get_scenario(self):

        return self.scenario

    def get_arrival_multiplier(self):

        return self.arrival_multiplier

    # ==============================================================
    # RESET
    # ==============================================================

    def reset(self):

        self.scenario = "NORMAL"
        self.arrival_multiplier = 1.0

        self.stress_steps = 0
        self.recovery_steps = 0
        self.stable_steps = 0

        self.previous_queue = 0