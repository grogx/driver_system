import sqlite3
from datetime import datetime, timedelta

DB = "drivers.db"


def auto_assign_shift(bus_id=None, route=None, date=None, start_time=None, end_time=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    fmt = "%H:%M"

    # =========================
    # DEFAULT VALUES
    # =========================
    if not route:
        route = f"R{datetime.now().minute % 99}"

    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    if not start_time:
        start_time = "08:00"

    if not end_time:
        end_time = "16:00"

    # =========================
    # BUS SELECT
    # =========================
    if not bus_id:
        cur.execute("SELECT id FROM buses ORDER BY RANDOM() LIMIT 1")
        bus = cur.fetchone()
        if not bus:
            conn.close()
            return None, "Нет автобусов"
        bus_id = bus[0]

    # =========================
    # SHIFT DURATION
    # =========================
    start = datetime.strptime(start_time, fmt)
    end = datetime.strptime(end_time, fmt)

    if end <= start:
        end += timedelta(days=1)

    hours = (end - start).seconds / 3600

    # =========================
    # GET DRIVERS
    # =========================
    cur.execute("""
        SELECT id, full_name, experience, med_expiry_date
        FROM drivers
        WHERE status='работает'
    """)

    drivers = cur.fetchall()

    best = None
    best_score = -10**9

    today = datetime.today().date()

    for driver_id, name, exp, med in drivers:

        # =========================
        # MED CHECK (SAFE)
        # =========================
        try:
            if not med:
                continue

            if datetime.strptime(med, "%Y-%m-%d").date() < today:
                continue
        except:
            continue

        # =========================
        # TOTAL HOURS
        # =========================
        cur.execute("""
            SELECT IFNULL(SUM(hours),0)
            FROM shifts
            WHERE driver_id=?
        """, (driver_id,))

        total = cur.fetchone()[0]

        if total + hours > 40:
            continue

        # =========================
        # CONFLICT CHECK (FIXED)
        # =========================
        cur.execute("""
            SELECT start_time, end_time
            FROM shifts
            WHERE driver_id=? AND shift_date=?
        """, (driver_id, date))

        shifts = cur.fetchall()

        conflict = False

        for s_start_str, s_end_str in shifts:
            s_start = datetime.strptime(s_start_str, fmt)
            s_end = datetime.strptime(s_end_str, fmt)

            if s_end <= s_start:
                s_end += timedelta(days=1)

            # overlap check
            if not (end <= s_start or start >= s_end):
                conflict = True
                break

        if conflict:
            continue

        # =========================
        # AI SCORE (CLEAN VERSION)
        # =========================
        score = 0

        # load balance
        score += (40 - total) * 3

        # experience bonus
        score += exp * 4

        # penalty for overload
        score -= total * 1.2

        if score > best_score:
            best_score = score
            best = (driver_id, name)

    # =========================
    # RESULT
    # =========================
    if not best:
        conn.close()
        return None, "Нет подходящих водителей"

    cur.execute("""
        INSERT INTO shifts (
            driver_id, bus_id, route,
            shift_date, start_time, end_time, hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        best[0],
        bus_id,
        route,
        date,
        start_time,
        end_time,
        hours
    ))

    conn.commit()
    conn.close()

    return best, f"AI назначил {best[1]} (score={best_score:.1f})"