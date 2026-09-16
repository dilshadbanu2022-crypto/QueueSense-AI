import sqlite3
from datetime import datetime
import os


# -----------------------------------------
# DATABASE LOCATION
# -----------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(BASE_DIR, "queue.db")


# -----------------------------------------
# CREATE DATABASE
# -----------------------------------------

def create_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Organizations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organization_type TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    # Locations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT NOT NULL,
            FOREIGN KEY (organization_id)
                REFERENCES organizations(id)
        )
    """)

    # Services table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            FOREIGN KEY (location_id)
                REFERENCES locations(id)
        )
    """)

    # Queue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            name TEXT,
            service_type TEXT,
            status TEXT,
            joined_at TEXT,
            organization_id INTEGER,
            location_id INTEGER,
            service_id INTEGER
        )
    """)

    # Migration for existing queue database
    try:
        cursor.execute(
            "ALTER TABLE queue ADD COLUMN organization_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE queue ADD COLUMN location_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE queue ADD COLUMN service_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    # Queue events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT,
            people_waiting INTEGER,
            people_arriving INTEGER,
            people_served INTEGER,
            active_counters INTEGER,
            average_service_time REAL,
            recorded_at TEXT
        )
    """)

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT,
            predicted_waiting_time REAL,
            predicted_crowd REAL,
            risk_level TEXT,
            created_at TEXT
        )
    """)

    # AI actions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            reason TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------------------
# ADD HYDERABAD ORGANIZATION
# -----------------------------------------

# -----------------------------------------
# ADD ORGANIZATION
# -----------------------------------------

def add_organization(
    name,
    organization_type
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if organization already exists
    cursor.execute("""
        SELECT id
        FROM organizations
        WHERE name = ?
        AND organization_type = ?
        AND city = 'Hyderabad'
    """, (
        name,
        organization_type
    ))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return existing[0]

    # Create new organization
    cursor.execute("""
        INSERT INTO organizations
        (name, organization_type, city)
        VALUES (?, ?, ?)
    """, (
        name,
        organization_type,
        "Hyderabad"
    ))

    organization_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return organization_id


# -----------------------------------------
# ADD LOCATION
# -----------------------------------------


def add_location(
    organization_id,
    name,
    address=""
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if location already exists
    cursor.execute("""
        SELECT id
        FROM locations
        WHERE organization_id = ?
        AND name = ?
        AND city = 'Hyderabad'
    """, (
        organization_id,
        name
    ))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return existing[0]

    # Create new location
    cursor.execute("""
        INSERT INTO locations
        (organization_id, name, address, city)
        VALUES (?, ?, ?, ?)
    """, (
        organization_id,
        name,
        address,
        "Hyderabad"
    ))

    location_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return location_id


# -----------------------------------------
# ADD SERVICE
# -----------------------------------------


def add_service(location_id, service_name):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if service already exists
    cursor.execute("""
        SELECT id
        FROM services
        WHERE location_id = ?
        AND service_name = ?
    """, (
        location_id,
        service_name
    ))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return existing[0]

    # Create new service
    cursor.execute("""
        INSERT INTO services
        (location_id, service_name)
        VALUES (?, ?)
    """, (
        location_id,
        service_name
    ))

    service_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return service_id

# -----------------------------------------
# GET ORGANIZATIONS
# -----------------------------------------

def get_organizations():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, organization_type, city
        FROM organizations
        WHERE city = 'Hyderabad'
        ORDER BY name
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -----------------------------------------
# GET LOCATIONS
# -----------------------------------------

def get_locations():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            locations.id,
            organizations.name,
            locations.name,
            locations.address,
            locations.city
        FROM locations

        JOIN organizations
        ON locations.organization_id = organizations.id

        WHERE locations.city = 'Hyderabad'

        ORDER BY locations.name
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -----------------------------------------
# TOKEN GENERATION
# -----------------------------------------

def generate_token(organization_id, location_id, service_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(token)
        FROM queue
        WHERE organization_id = ?
        AND location_id = ?
        AND service_id = ?
    """, (
        organization_id,
        location_id,
        service_id
    ))

    result = cursor.fetchone()[0]

    token = 1 if result is None else result + 1

    conn.close()

    return token


# -----------------------------------------
# ADD PERSON TO QUEUE
# -----------------------------------------

def add_person(
    name,
    service_type,
    organization_id,
    location_id,
    service_id
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    token = generate_token(
        organization_id,
        location_id,
        service_id
    )

    cursor.execute("""
        INSERT INTO queue
        (
            token,
            name,
            service_type,
            status,
            joined_at,
            organization_id,
            location_id,
            service_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        token,
        name,
        service_type,
        "Waiting",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        organization_id,
        location_id,
        service_id
    ))

    conn.commit()
    conn.close()

    return token

# -----------------------------------------
# GET CURRENT QUEUE
# -----------------------------------------

def get_queue():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            token,
            name,
            service_type,
            status,
            joined_at

        FROM queue

        WHERE status = 'Waiting'

        ORDER BY token
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -----------------------------------------
# PEOPLE AHEAD
# -----------------------------------------

def get_people_ahead(
    token,
    organization_id,
    location_id,
    service_id
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM queue
        WHERE token < ?
        AND organization_id = ?
        AND location_id = ?
        AND service_id = ?
        AND status = 'Waiting'
    """, (
        token,
        organization_id,
        location_id,
        service_id
    ))

    count = cursor.fetchone()[0]

    conn.close()

    return count


# -----------------------------------------
# SERVE TOKEN
# -----------------------------------------

def serve_token(
    token,
    organization_id,
    location_id,
    service_id
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE queue
        SET status = 'Served'
        WHERE token = ?
        AND organization_id = ?
        AND location_id = ?
        AND service_id = ?
    """, (
        token,
        organization_id,
        location_id,
        service_id
    ))

    conn.commit()
    conn.close()


# -----------------------------------------
# SAVE QUEUE EVENT
# -----------------------------------------

def record_queue_event(
    service_type,
    people_waiting,
    people_arriving,
    people_served,
    active_counters,
    average_service_time
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO queue_events
        (
            service_type,
            people_waiting,
            people_arriving,
            people_served,
            active_counters,
            average_service_time,
            recorded_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        service_type,
        people_waiting,
        people_arriving,
        people_served,
        active_counters,
        average_service_time,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


# -----------------------------------------
# SAVE ML PREDICTION
# -----------------------------------------

def save_prediction(
    service_type,
    predicted_waiting_time,
    predicted_crowd,
    risk_level
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions
        (
            service_type,
            predicted_waiting_time,
            predicted_crowd,
            risk_level,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        service_type,
        predicted_waiting_time,
        predicted_crowd,
        risk_level,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


# -----------------------------------------
# SAVE AI ACTION
# -----------------------------------------

def save_ai_action(action, reason):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ai_actions
        (
            action,
            reason,
            created_at
        )

        VALUES (?, ?, ?)
    """, (
        action,
        reason,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


# -----------------------------------------
# TEST
# -----------------------------------------

if __name__ == "__main__":

    create_database()

    print("=" * 60)
    print("QUEUE SENSE AI")
    print("HYDERABAD DATABASE")
    print("=" * 60)

    # ========================================================
    # DEMO HOSPITAL
    # ========================================================

    hospital_id = add_organization(
        "Demo Hospital",
        "Hospital"
    )

    hospital_location_id = add_location(
        hospital_id,
        "Demo Hospital Hyderabad",
        "Hyderabad"
    )

    add_service(
        hospital_location_id,
        "Registration"
    )

    add_service(
        hospital_location_id,
        "OPD"
    )

    add_service(
        hospital_location_id,
        "Laboratory"
    )

    add_service(
        hospital_location_id,
        "Pharmacy"
    )

    # ========================================================
    # DEMO BANK
    # ========================================================

    bank_id = add_organization(
        "Demo Bank",
        "Bank"
    )

    bank_location_id = add_location(
        bank_id,
        "Demo Bank Hyderabad",
        "Hyderabad"
    )

    add_service(
        bank_location_id,
        "Account Services"
    )

    add_service(
        bank_location_id,
        "Cash Counter"
    )

    add_service(
        bank_location_id,
        "Customer Support"
    )

    # ========================================================
    # DEMO E-SEVA CENTER
    # ========================================================

    eseva_id = add_organization(
        "Demo e-Seva Center",
        "Government Service"
    )

    eseva_location_id = add_location(
        eseva_id,
        "Demo e-Seva Hyderabad",
        "Hyderabad"
    )

    add_service(
        eseva_location_id,
        "Certificates"
    )

    add_service(
        eseva_location_id,
        "Bill Payment"
    )

    add_service(
        eseva_location_id,
        "Government Services"
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\nDatabase created successfully!")

    print("\nHyderabad Organizations:")

    for organization in get_organizations():
        print(organization)

    print("\nHyderabad Locations:")

    for location in get_locations():
        print(location)

    print("\nDatabase test completed successfully!")
