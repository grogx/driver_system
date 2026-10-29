import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "drivers.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # =========================
    # USERS
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # =========================
    # DRIVERS
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT,
        experience INTEGER,
        license_category TEXT,
        status TEXT DEFAULT 'работает',
        med_book_number TEXT,
        med_expiry_date TEXT
    )
    """)

    # =========================
    # BUSES
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS buses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE,
        model TEXT,
        capacity INTEGER,
        status TEXT DEFAULT 'свободен'
    )
    """)

    # =========================
    # SHIFTS
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL,
        bus_id INTEGER,
        route TEXT,
        shift_date TEXT,
        start_time TEXT,
        end_time TEXT,
        hours REAL,
        status TEXT DEFAULT 'назначена',
        FOREIGN KEY(driver_id) REFERENCES drivers(id) ON DELETE CASCADE,
        FOREIGN KEY(bus_id) REFERENCES buses(id) ON DELETE SET NULL
    )
    """)

    # =========================
    # USERS INIT
    # =========================
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, [
            ("admin", "admin", "admin"),
            ("dispatcher", "1234", "dispatcher"),
            ("director", "1234", "director")
        ])

    # =========================
    # ФИО (Фамилия + Имя + Отчество)
    # =========================
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов"]
    first_names = ["Иван", "Алексей", "Дмитрий", "Сергей", "Андрей"]
    patronymics = ["Иванович", "Петрович", "Сергеевич", "Алексеевич", "Дмитриевич"]

    def gen_phone():
        return f"+7 9{random.randint(10,99)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"

    def gen_med_date():
        r = random.random()
        if r < 0.2:  # просрочено
            return (datetime.today() - timedelta(days=random.randint(10, 500))).strftime("%Y-%m-%d")
        elif r < 0.4:  # скоро истекает
            return (datetime.today() + timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d")
        else:  # норм
            return (datetime.today() + timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d")

    # =========================
    # DRIVERS INIT
    # =========================
    cur.execute("SELECT COUNT(*) FROM drivers")
    if cur.fetchone()[0] == 0:

        drivers = []

        for i in range(1, 35):

            full_name = f"{random.choice(last_names)} {random.choice(first_names)} {random.choice(patronymics)}"

            drivers.append((
                full_name,
                gen_phone(),
                random.randint(1, 40),
                "D",
                "работает",
                f"MB-{1000 + i}",
                gen_med_date()
            ))

        cur.executemany("""
        INSERT INTO drivers (
            full_name, phone, experience,
            license_category, status,
            med_book_number, med_expiry_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, drivers)

    # =========================
    # BUSES
    # =========================
    cur.execute("SELECT COUNT(*) FROM buses")
    if cur.fetchone()[0] == 0:

        models = ["Volvo", "Mercedes", "MAN", "Scania"]
        buses = []

        for i in range(1, 20):
            buses.append((
                f"A{i:03d}AA",
                random.choice(models),
                random.choice([40, 50, 60, 80, 100]),
            ))

        cur.executemany("""
        INSERT INTO buses (number, model, capacity)
        VALUES (?, ?, ?)
        """, buses)

    # =========================
    # SHIFTS
    # =========================
    cur.execute("SELECT COUNT(*) FROM shifts")
    if cur.fetchone()[0] == 0:

        shifts = []

        for i in range(70):

            driver_id = random.randint(1, 30)
            bus_id = random.randint(1, 19)

            start = random.randint(6, 18)

            # перегрузки
            if random.random() < 0.3:
                end = start + random.randint(10, 16)
            else:
                end = start + random.randint(4, 8)

            shifts.append((
                driver_id,
                bus_id,
                f"{random.randint(1, 120)}",
                (datetime.today() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                f"{start:02d}:00",
                f"{end:02d}:00",
                end - start
            ))

        cur.executemany("""
        INSERT INTO shifts (
            driver_id, bus_id, route,
            shift_date, start_time, end_time,
            hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, shifts)

    conn.commit()
    conn.close()

    print("✅ БАЗА ПЕРЕСОЗДАНА: ФИО + ОТЧЕСТВА + МЕДКНИЖКИ + РЕАЛЬНЫЕ СРОКИ")