import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "customers.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        city TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        subject TEXT,
        description TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    # Clear old demo data (optional)
    cur.execute("DELETE FROM tickets")
    cur.execute("DELETE FROM customers")

    now = datetime.utcnow()

    customers = [
        ("Ema Ali", "ema@example.com", "+1-555-0101", "Toronto", (now - timedelta(days=120)).isoformat()),
        ("John Smith", "john.smith@example.com", "+1-555-0102", "Vancouver", (now - timedelta(days=90)).isoformat()),
        ("Sara Khan", "sara.khan@example.com", "+1-555-0103", "Calgary", (now - timedelta(days=60)).isoformat()),
    ]
    cur.executemany(
        "INSERT INTO customers (name, email, phone, city, created_at) VALUES (?, ?, ?, ?, ?)",
        customers
    )

    # Map names -> ids
    cur.execute("SELECT id, name FROM customers")
    id_map = {name: cid for cid, name in cur.fetchall()}

    tickets = [
        (id_map["Ema Ali"], "Refund request", "Customer asked about refund eligibility and timelines.", "Closed",
         (now - timedelta(days=15)).isoformat()),
        (id_map["Ema Ali"], "Delivery issue", "Package delayed; requested shipping estimate update.", "Open",
         (now - timedelta(days=3)).isoformat()),
        (id_map["John Smith"], "Warranty claim", "Reported manufacturing defect and asked about warranty coverage.", "Open",
         (now - timedelta(days=7)).isoformat()),
        (id_map["Sara Khan"], "Account access", "Cannot login; password reset not working.", "Closed",
         (now - timedelta(days=20)).isoformat()),
    ]
    cur.executemany(
        "INSERT INTO tickets (customer_id, subject, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
        tickets
    )

    conn.commit()
    conn.close()
    print(f"✅ Seeded DB at: {DB_PATH}")

if __name__ == "__main__":
    main()
