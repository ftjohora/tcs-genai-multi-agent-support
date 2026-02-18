import sqlite3
from pathlib import Path
from utils.local_llm import generate

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "customers.db"

def ask_customer(question: str) -> str:
    q = question.lower()

    # simple name detection for demo
    target = None
    for name in ["ema", "ema ali", "john", "sara"]:
        if name in q:
            target = name
            break

    if not target:
        return "Please specify a customer name (e.g., 'Ema Ali')."

    want_profile = any(x in q for x in ["profile", "details", "overview", "info"])
    want_tickets = any(x in q for x in ["ticket", "tickets", "support", "issue", "history"])
    want_latest = any(x in q for x in ["latest", "most recent", "last ticket", "recent ticket"])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, email, phone, city, created_at FROM customers WHERE lower(name) LIKE ? LIMIT 1",
        (f"%{target}%",),
    )
    customer = cur.fetchone()
    if not customer:
        conn.close()
        return f"No customer found matching '{target}'."

    cid, name, email, phone, city, created_at = customer

    # Decide what to pull from DB
    tickets = []
    if want_tickets or want_latest or (not want_profile and not want_tickets):
        if want_latest:
            cur.execute(
                "SELECT subject, status, created_at, description FROM tickets WHERE customer_id=? ORDER BY created_at DESC LIMIT 1",
                (cid,),
            )
        else:
            cur.execute(
                "SELECT subject, status, created_at, description FROM tickets WHERE customer_id=? ORDER BY created_at DESC",
                (cid,),
            )
        tickets = cur.fetchall()

    conn.close()

    # Build raw info for local LLM summary
    raw_parts = []
    if want_profile or (not want_profile and not want_tickets):
        raw_parts.append(
            f"""Customer:
- Name: {name}
- Email: {email}
- Phone: {phone}
- City: {city}
- Created At: {created_at}
"""
        )

    if tickets:
        raw_parts.append(
            "Tickets:\n" + "\n".join(
                [f"- {sub} | {status} | {tdate} | {desc}" for sub, status, tdate, desc in tickets]
            )
        )

    raw = "\n".join(raw_parts).strip()

    prompt = f"""
You are a helpful customer support assistant.
Summarize the information below in a short, structured format.
Use bullet points. Keep it under 10 lines.

{raw}
"""
    return generate(prompt, max_new_tokens=256)
