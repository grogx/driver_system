import json
import sqlite3
import os

DB = "drivers.db"
FILE = r"C:\ERP_SYNC\exchange.json"


def ensure_folder():
    folder = os.path.dirname(FILE)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)


def safe(v):
    return "" if v is None else v


# =========================
# IMPORT FROM 1C
# =========================
def import_from_1c():
    try:
        ensure_folder()

        if not os.path.exists(FILE):
            return "ERROR: exchange.json not found"

        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        # ================= DRIVERS =================
        for d in data.get("drivers", []):

            cur.execute("""
                INSERT INTO drivers (
                    id, full_name, phone,
                    experience, license_category,
                    status, med_book_number,
                    med_expiry_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    full_name=excluded.full_name,
                    phone=excluded.phone,
                    experience=excluded.experience,
                    license_category=excluded.license_category,
                    status=excluded.status,
                    med_book_number=excluded.med_book_number,
                    med_expiry_date=excluded.med_expiry_date
            """, (
                safe(d.get("id")),
                safe(d.get("name")),
                safe(d.get("phone")),
                safe(d.get("experience")),
                safe(d.get("license_category")),
                safe(d.get("status")),
                safe(d.get("med_book_number")),
                safe(d.get("med_expiry_date")),
            ))

        # ================= BUSES =================
        for b in data.get("buses", []):

            cur.execute("""
                INSERT INTO buses (
                    id, number, model, capacity
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    number=excluded.number,
                    model=excluded.model,
                    capacity=excluded.capacity
            """, (
                safe(b.get("id")),
                safe(b.get("number")),
                safe(b.get("model")),
                safe(b.get("capacity")),
            ))

        conn.commit()
        conn.close()

        return "✔ IMPORT OK"

    except Exception as e:
        return f"IMPORT ERROR: {str(e)}"


# =========================
# EXPORT TO 1C
# =========================
def export_to_1c():
    try:
        ensure_folder()

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        data = {"drivers": [], "buses": []}

        cur.execute("""
            SELECT id, full_name, phone,
                   experience, license_category,
                   status, med_book_number,
                   med_expiry_date
            FROM drivers
        """)

        for r in cur.fetchall():
            data["drivers"].append({
                "id": r[0],
                "name": r[1],
                "phone": r[2],
                "experience": r[3],
                "license_category": r[4],
                "status": r[5],
                "med_book_number": r[6],
                "med_expiry_date": r[7],
            })

        cur.execute("SELECT id, number, model, capacity FROM buses")

        for r in cur.fetchall():
            data["buses"].append({
                "id": r[0],
                "number": r[1],
                "model": r[2],
                "capacity": r[3],
            })

        conn.close()

        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return "✔ EXPORT OK"

    except Exception as e:
        return f"EXPORT ERROR: {str(e)}"