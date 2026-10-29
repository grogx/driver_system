# =========================
# auto_schedule.py (SAFE ERP VERSION)
# =========================

import sqlite3
from datetime import datetime, timedelta

from smart_assign import get_best_driver

DB = "drivers.db"


def generate_week_schedule():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=7)

        # =========================
        # ОЧИСТКА ТОЛЬКО ТЕКУЩЕЙ НЕДЕЛИ
        # =========================
        cur.execute("""
            DELETE FROM shifts
            WHERE route = 'AUTO'
            AND shift_date BETWEEN ? AND ?
        """, (start_date.strftime("%Y-%m-%d"),
              end_date.strftime("%Y-%m-%d")))

        # =========================
        # ПОЛУЧАЕМ АВТОБУС
        # =========================
        cur.execute("SELECT id FROM buses LIMIT 1")
        bus_row = cur.fetchone()

        if not bus_row:
            return "❌ Нет автобусов в системе"

        bus_id = bus_row[0]

        created = 0

        # =========================
        # ГЕНЕРАЦИЯ
        # =========================
        for i in range(7):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

            driver_data = get_best_driver()

            if not driver_data:
                continue

            driver_id = driver_data[0]

            # =========================
            # ПРОВЕРКА: уже есть смена?
            # =========================
            cur.execute("""
                SELECT COUNT(*)
                FROM shifts
                WHERE driver_id=? AND shift_date=?
            """, (driver_id, date))

            if cur.fetchone()[0] > 0:
                continue

            # =========================
            # ЧАСЫ В НЕДЕЛЕ
            # =========================
            cur.execute("""
                SELECT IFNULL(SUM(hours),0)
                FROM shifts
                WHERE driver_id=?
                AND shift_date BETWEEN ? AND ?
            """, (
                driver_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            ))

            total = cur.fetchone()[0]

            if total >= 40:
                continue

            # =========================
            # СОЗДАНИЕ СМЕНЫ
            # =========================
            cur.execute("""
                INSERT INTO shifts
                (driver_id, bus_id, route, shift_date, start_time, end_time, hours)
                VALUES (?, ?, 'AUTO', ?, '08:00', '16:00', 8)
            """, (driver_id, bus_id, date))

            created += 1

        conn.commit()

        return f"✔ Сгенерировано смен: {created}"

    except Exception as e:
        return f"❌ Ошибка автогенерации: {str(e)}"

    finally:
        conn.close()