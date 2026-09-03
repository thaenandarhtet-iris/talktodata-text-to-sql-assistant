import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCHEMA_DESCRIPTION = """
Database: talktodata (MySQL)

carriers(carrier_cd CHAR(2) PRIMARY KEY, carrier_name VARCHAR(60))
airports(airport_cd CHAR(3) PRIMARY KEY, airport_name VARCHAR(100), city VARCHAR(60), country VARCHAR(60))
aircraft(aircraft_id INT PRIMARY KEY, model VARCHAR(60), capacity INT, carrier_cd CHAR(2) references carriers)
flights(flight_id INT PRIMARY KEY, flight_num VARCHAR(10), carrier_cd CHAR(2) references carriers, origin_cd CHAR(3) references airports, dest_cd CHAR(3) references airports, aircraft_id INT references aircraft, sched_dep_dt DATETIME, sched_arr_dt DATETIME, delay_min INT, status_cd CHAR(2))
passengers(pax_id INT PRIMARY KEY, full_name VARCHAR(100), email VARCHAR(120), loyalty_tier CHAR(3))
bookings(booking_id INT PRIMARY KEY, pax_id INT references passengers, flight_id INT references flights, booking_dt DATE, fare_class CHAR(1), fare_amt DECIMAL(7,2), status_cd CHAR(2))

Coded columns, interpret these exactly as shown, do not spell them out in the SQL:
flights.status_cd: OT = on time, DL = delayed, CN = cancelled, DV = diverted
bookings.fare_class: Y = economy, W = premium economy, J = business, F = first
bookings.status_cd: CF = confirmed, CX = cancelled, WL = waitlisted
passengers.loyalty_tier: BAS = basic, SLV = silver, GLD = gold
""".strip()

SYSTEM_PROMPT = """You are a MySQL expert. Given a question in plain English and a database schema, write a single MySQL SELECT query that answers it.

Rules:
- Only ever write SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, ALTER, or anything that changes data.
- Return only the raw SQL query. No explanation, no markdown code fences, no semicolon-separated multiple statements.
- Use the coded column values exactly as they appear in the schema, for example status_cd = 'DL', do not spell them out.
- If the question is ambiguous, make the most reasonable assumption and answer it, don't ask a clarifying question back.
"""

def generate_sql(question: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Schema:\n{SCHEMA_DESCRIPTION}\n\nQuestion: {question}"}
        ],
    )
    sql = message.content[0].text.strip()
    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.startswith("sql"):
            sql = sql[3:]
    return sql.strip()

if __name__ == "__main__":
    test_questions = [
        "How many flights were delayed?",
        "Which carrier has the most cancelled flights?",
        "What is the total revenue from confirmed bookings?",
        "List the top 5 passengers by total spend",
    ]
    for q in test_questions:
        print(f"Q: {q}")
        print(f"SQL: {generate_sql(q)}")
        print()
