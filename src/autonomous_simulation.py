import random
from datetime import datetime, timedelta


class AutonomousQueueSimulation:

    def __init__(
        self,
        initial_queue=20,
        initial_counters=3,
        max_counters=5,
        average_service_time=5,
        seed=None
    ):

        self.random = random.Random(seed)

        # ==================================================
        # INITIAL SYSTEM STATE
        # ==================================================

        self.initial_queue = initial_queue
        self.initial_counters = initial_counters
        self.initial_staff = initial_counters + 1

        self.queue_length = initial_queue
        self.active_counters = initial_counters
        self.max_counters = max_counters

        self.average_service_time = average_service_time
        self.staff_available = self.initial_staff

        self.people_arriving = 0
        self.people_served = 0
        self.current_crowd = initial_queue

        self.total_arrivals = 0
        self.total_served = 0

        # ==================================================
        # DYNAMIC ENVIRONMENT
        # ==================================================

        # Controlled by Scenario Engine
        self.arrival_multiplier = 1.0

        # Simulation-only environment parameter.
        # This controls service capacity in the demo.
        self.service_rate_factor = 1.0

        # Remembers increasing/decreasing demand.
        self.demand_pressure = 0.0

        # ==================================================
        # VIRTUAL CLOCK
        # ==================================================

        self.initial_time = datetime(
            2026,
            1,
            1,
            9,
            0
        )

        self.simulation_time = self.initial_time

        # ==================================================
        # STATUS
        # ==================================================

        self.running = False
        self.speed = 1

        # ==================================================
        # EVENT LOG
        # ==================================================

        self.events = []

    # ======================================================
    # CONTROLS
    # ======================================================

    def start(self):

        self.running = True

        self.add_event(
            "Simulation started"
        )

    def pause(self):

        self.running = False

        self.add_event(
            "Simulation paused"
        )

    def reset(self):

        self.__init__(
            self.initial_queue,
            self.initial_counters,
            self.max_counters,
            self.average_service_time
        )

        self.add_event(
            "Simulation reset"
        )

    # ======================================================
    # ARRIVAL MULTIPLIER
    # ======================================================

    def set_arrival_multiplier(self, multiplier):

        self.arrival_multiplier = max(
            0.5,
            float(multiplier)
        )

    # ======================================================
    # DYNAMIC ARRIVAL GENERATION
    # ======================================================

    def generate_arrivals(self):

        hour = self.simulation_time.hour

        # --------------------------------------------------
        # Base demand
        # --------------------------------------------------

        base_arrivals = self.random.randint(
            6,
            11
        )

        # --------------------------------------------------
        # Natural peak-hour demand
        # --------------------------------------------------

        if 9 <= hour < 12:

            base_arrivals += self.random.randint(
                3,
                7
            )

        elif 14 <= hour < 17:

            base_arrivals += self.random.randint(
                3,
                7
            )

        # --------------------------------------------------
        # Dynamic queue pressure
        # --------------------------------------------------

        if self.queue_length >= 30:

            self.demand_pressure += 1.5

        elif self.queue_length >= 20:

            self.demand_pressure += 0.8

        elif self.queue_length >= 10:

            self.demand_pressure += 0.2

        else:

            self.demand_pressure -= 0.5

        self.demand_pressure = max(
            0,
            min(
                self.demand_pressure,
                15
            )
        )

        # --------------------------------------------------
        # Additional demand caused by pressure
        # --------------------------------------------------

        pressure_arrivals = int(
            self.demand_pressure
        )

        # --------------------------------------------------
        # Natural variation
        # --------------------------------------------------

        variation = self.random.randint(
            -2,
            4
        )

        arrivals = (
            base_arrivals
            + pressure_arrivals
            + variation
        )

        # --------------------------------------------------
        # Scenario multiplier
        # --------------------------------------------------

        arrivals = int(
            round(
                arrivals
                * self.arrival_multiplier
            )
        )

        return max(
            0,
            arrivals
        )

        # ======================================================
    # SERVICE PROCESSING
    # ======================================================

    def process_service(self):

        if self.queue_length <= 0:
            return 0

        # Normal service capacity
        capacity_per_counter = 4

        # Natural variation
        variation = self.random.randint(-1, 1)

        service_capacity = (
            self.active_counters
            * capacity_per_counter
            + variation
        )

        # --------------------------------------------------
        # Adaptive service efficiency
        # --------------------------------------------------
        # When congestion becomes severe and all available
        # counters are active, the system operates at higher
        # efficiency to help recover the queue.

        if (
            self.queue_length >= 70
            and self.active_counters >= self.max_counters
        ):

            self.service_rate_factor = 1.25

        elif (
            self.queue_length >= 40
            and self.active_counters >= self.max_counters
        ):

            self.service_rate_factor = 1.15

        else:

            self.service_rate_factor = 1.0

        service_capacity = int(
            service_capacity
            * self.service_rate_factor
        )

        service_capacity = max(
            0,
            service_capacity
        )

        return min(
            self.queue_length,
            service_capacity
        )
    # ======================================================
    # UPDATE QUEUE
    # ======================================================

    def update_queue(self):

        # Generate new arrivals
        arrivals = self.generate_arrivals()

        # Process people currently in queue
        served = self.process_service()

        self.people_arriving = arrivals
        self.people_served = served

        # --------------------------------------------------
        # Queue equation
        #
        # New Queue =
        # Old Queue + Arrivals - Served
        # --------------------------------------------------

        self.queue_length = max(
            0,
            self.queue_length
            + arrivals
            - served
        )

        # Current crowd equals people currently waiting
        self.current_crowd = self.queue_length

        # Update totals
        self.total_arrivals += arrivals
        self.total_served += served

        # --------------------------------------------------
        # Advance virtual time
        # --------------------------------------------------

        self.simulation_time += timedelta(
            minutes=5
        )

        return {
            "arrivals": arrivals,
            "served": served,
            "queue": self.queue_length
        }

    # ======================================================
    # WAITING TIME
    # ======================================================

    def calculate_waiting_time(self):

        if self.active_counters <= 0:

            return 0

        waiting_time = (
            self.queue_length
            * self.average_service_time
            / self.active_counters
        )

        return round(
            max(
                0,
                waiting_time
            ),
            2
        )

    # ======================================================
    # CROWD LEVEL
    # ======================================================

    def get_crowd_level(self):

        crowd = self.current_crowd

        if crowd < 30:

            return "LOW"

        elif crowd < 70:

            return "MEDIUM"

        elif crowd < 120:

            return "HIGH"

        return "CRITICAL"

    # ======================================================
    # COUNTER CONTROL
    # ======================================================

    def set_counters(
        self,
        number_of_counters
    ):

        number_of_counters = max(
            1,
            min(
                number_of_counters,
                self.max_counters
            )
        )

        old_counters = (
            self.active_counters
        )

        self.active_counters = (
            number_of_counters
        )

        # Make sure enough staff exists
        self.staff_available = max(
            self.staff_available,
            self.active_counters
        )

        # --------------------------------------------------
        # Event logging
        # --------------------------------------------------

        if self.active_counters > old_counters:

            self.add_event(
                f"Counter increased from "
                f"{old_counters} to "
                f"{self.active_counters}"
            )

        elif self.active_counters < old_counters:

            self.add_event(
                f"Counter decreased from "
                f"{old_counters} to "
                f"{self.active_counters}"
            )

    # ======================================================
    # SIMULATION STEP
    # ======================================================

    def step(
        self,
        arrival_multiplier=None
    ):

        # --------------------------------------------------
        # Apply scenario multiplier if supplied
        # --------------------------------------------------

        if arrival_multiplier is not None:

            self.set_arrival_multiplier(
                arrival_multiplier
            )

        # --------------------------------------------------
        # Do nothing if simulation is paused
        # --------------------------------------------------

        if not self.running:

            return self.get_state()

        # --------------------------------------------------
        # Update environment
        # --------------------------------------------------

        result = self.update_queue()

        crowd_level = (
            self.get_crowd_level()
        )

        # --------------------------------------------------
        # Detect arrival surge
        # --------------------------------------------------

        if result["arrivals"] > 20:

            self.add_event(
                "Arrival surge detected"
            )

        # --------------------------------------------------
        # Detect critical congestion
        # --------------------------------------------------

        if crowd_level == "CRITICAL":

            self.add_event(
                "Critical congestion detected"
            )

        # --------------------------------------------------
        # Detect recovery
        # --------------------------------------------------

        if (
            result["served"]
            > result["arrivals"]
            and self.queue_length > 0
        ):

            self.add_event(
                "Queue recovery detected"
            )

        return self.get_state()

    # ======================================================
    # EVENT LOG
    # ======================================================

    def add_event(self, message):

        timestamp = (
            self.simulation_time
            .strftime("%H:%M:%S")
        )

        self.events.append(
            f"{timestamp} - {message}"
        )

        # Keep latest 50 events
        self.events = (
            self.events[-50:]
        )

    # ======================================================
    # CURRENT STATE
    # ======================================================

    def get_state(self):

        return {

            "simulation_time":
                self.simulation_time.strftime(
                    "%H:%M:%S"
                ),

            "queue_length":
                self.queue_length,

            "people_arriving":
                self.people_arriving,

            "people_served":
                self.people_served,

            "current_crowd":
                self.current_crowd,

            "active_counters":
                self.active_counters,

            "staff_available":
                self.staff_available,

            "average_service_time":
                self.average_service_time,

            "waiting_time":
                self.calculate_waiting_time(),

            "crowd_level":
                self.get_crowd_level(),

            "total_arrivals":
                self.total_arrivals,

            "total_served":
                self.total_served,

            "arrival_multiplier":
                self.arrival_multiplier,

            "demand_pressure":
                round(
                    self.demand_pressure,
                    2
                ),

            "running":
                self.running,

            "events":
                self.events,
        }


# ==========================================================
# BASIC TEST
# ==========================================================

if __name__ == "__main__":

    simulation = AutonomousQueueSimulation(
        initial_queue=20,
        initial_counters=3,
        max_counters=5,
        average_service_time=5,
        seed=42
    )

    simulation.start()

    print(
        "\nQUEUE SENSE AI\n"
        "AUTONOMOUS SIMULATION\n"
        + "=" * 60
    )

    for step_number in range(20):

        state = simulation.step()

        print(
            f"\nStep: {step_number + 1}"
        )

        print(
            f"Time: "
            f"{state['simulation_time']}"
        )

        print(
            f"Arrivals: "
            f"{state['people_arriving']}"
        )

        print(
            f"Served: "
            f"{state['people_served']}"
        )

        print(
            f"Queue: "
            f"{state['queue_length']}"
        )

        print(
            f"Counters: "
            f"{state['active_counters']}"
        )

        print(
            f"Waiting Time: "
            f"{state['waiting_time']} min"
        )

        print(
            f"Crowd Level: "
            f"{state['crowd_level']}"
        )

        print(
            f"Demand Pressure: "
            f"{state['demand_pressure']}"
        )

        print(
            f"Arrival Multiplier: "
            f"{state['arrival_multiplier']}x"
        )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL SIMULATION STATE"
    )

    print(
        "=" * 60
    )

    print(
        f"Queue: "
        f"{state['queue_length']}"
    )

    print(
        f"Total Arrivals: "
        f"{state['total_arrivals']}"
    )

    print(
        f"Total Served: "
        f"{state['total_served']}"
    )

    print(
        f"Waiting Time: "
        f"{state['waiting_time']} min"
    )

    print(
        f"Crowd Level: "
        f"{state['crowd_level']}"
    )

    print(
        "\nEVENT LOG"
    )

    print(
        "=" * 60
    )

    for event in state["events"]:

        print(event)