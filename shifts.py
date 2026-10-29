import customtkinter as ctk
import sqlite3
from tkinter import messagebox, ttk
import re
from datetime import datetime

DB = "drivers.db"


class ShiftsWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.driver_map = {}
        self.bus_map = {}
        self.selected_id = None

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ================= TITLE =================
        ctk.CTkLabel(
            self,
            text="Управление смен",
            font=("Arial", 26, "bold")
        ).grid(row=0, column=0, pady=10)

        # ================= FORM =================
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        form.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(form)
        left.grid(row=0, column=0, sticky="nsew", padx=10)

        right = ctk.CTkFrame(form)
        right.grid(row=0, column=1, sticky="nsew", padx=10)

        # ---------------- DRIVER ----------------
        ctk.CTkLabel(left, text="Водитель").pack(anchor="w")

        self.driver_box = ctk.CTkOptionMenu(
            left,
            values=["ФИО"],
            width=260
        )
        self.driver_box.set("ФИО")
        self.driver_box.pack(pady=5)

        # ---------------- BUS ----------------
        ctk.CTkLabel(left, text="Автобус").pack(anchor="w")

        self.bus_box = ctk.CTkOptionMenu(
            left,
            values=["Номер"],
            width=260
        )
        self.bus_box.set("Номер")
        self.bus_box.pack(pady=5)

        # ---------------- ROUTE ----------------
        ctk.CTkLabel(right, text="Маршрут").pack(anchor="w")
        self.route = ctk.CTkEntry(right, width=260)
        self.route.pack(pady=5)

        ctk.CTkLabel(right, text="Дата (ДД.ММ.ГГГГ)").pack(anchor="w")
        self.date = ctk.CTkEntry(right, width=260)
        self.date.pack(pady=5)

        ctk.CTkLabel(right, text="Начало (HH:MM)").pack(anchor="w")
        self.start = ctk.CTkEntry(right, width=260)
        self.start.pack(pady=5)

        ctk.CTkLabel(right, text="Конец (HH:MM)").pack(anchor="w")
        self.end = ctk.CTkEntry(right, width=260)
        self.end.pack(pady=5)

        # ================= BUTTONS =================
        btns = ctk.CTkFrame(self)
        btns.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkButton(btns, text="➕ Добавить", command=self.add_shift).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Авто", command=self.smart_auto_assign).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🗑 Удалить", command=self.delete).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🔄 Обновить", command=self.load).pack(side="left", padx=5)

        # ================= TABLE =================
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "driver", "bus", "route", "date", "time", "hours")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1e1e1e",
            foreground="white",
            rowheight=55,
            font=("Arial", 16)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 16, "bold")
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("driver", text="Водитель")
        self.tree.heading("bus", text="Автобус")
        self.tree.heading("route", text="Маршрут")
        self.tree.heading("date", text="Дата")
        self.tree.heading("time", text="Время")
        self.tree.heading("hours", text="Часы")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("driver", width=260)
        self.tree.column("bus", width=160)
        self.tree.column("route", width=160)
        self.tree.column("date", width=130)
        self.tree.column("time", width=180)
        self.tree.column("hours", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.select_row)

        self.load_selects()
        self.load()

    # ================= SELECT =================
    def select_row(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_id = self.tree.item(sel[0], "values")[0]

    # ================= VALIDATION =================
    def validate(self):
        if not self.route.get().strip():
            return "Маршрут не заполнен"

        if not re.match(r"\d{2}\.\d{2}\.\d{4}", self.date.get()):
            return "Дата должна быть ДД.ММ.ГГГГ"

        if not re.match(r"\d{2}:\d{2}", self.start.get()):
            return "Начало HH:MM"

        if not re.match(r"\d{2}:\d{2}", self.end.get()):
            return "Конец HH:MM"

        return None

    # ================= LOAD SELECTS =================
    def load_selects(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT id, full_name FROM drivers")
        drivers = cur.fetchall()

        cur.execute("SELECT id, number FROM buses")
        buses = cur.fetchall()

        conn.close()

        self.driver_map = {d[1]: d[0] for d in drivers}
        self.bus_map = {b[1]: b[0] for b in buses}

        driver_list = list(self.driver_map.keys())
        bus_list = list(self.bus_map.keys())

        if not driver_list:
            driver_list = ["... (нет водителей)"]

        if not bus_list:
            bus_list = ["... (нет автобусов)"]

        self.driver_box.configure(values=driver_list)
        self.bus_box.configure(values=bus_list)

        self.driver_box.set("ФИО")
        self.bus_box.set("Номер")

    # ================= AI =================
    def ai_select(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT d.id,
                   d.experience,
                   COALESCE(COUNT(s.id), 0)
            FROM drivers d
            LEFT JOIN shifts s
                ON s.driver_id = d.id
                AND date(s.shift_date) >= date('now','-7 days')
            GROUP BY d.id
        """)

        drivers = cur.fetchall()

        cur.execute("""
            SELECT b.id,
                   COALESCE(COUNT(s.id), 0)
            FROM buses b
            LEFT JOIN shifts s ON s.bus_id = b.id
            GROUP BY b.id
        """)

        buses = cur.fetchall()
        conn.close()

        best_driver = None
        best_bus = None
        best_score = -10**9

        for d_id, exp, d_load in drivers:

            driver_score = exp * 4 - d_load * 6

            for b_id, b_load in buses:

                score = driver_score - b_load * 3

                if score > best_score:
                    best_score = score
                    best_driver = d_id
                    best_bus = b_id

        return best_driver, best_bus

    # ================= AUTO =================
    def smart_auto_assign(self):

        err = self.validate()

        if err:
            messagebox.showerror("Ошибка", err)
            return

        driver_id, bus_id = self.ai_select()

        if not driver_id or not bus_id:
            messagebox.showerror("AI", "Нет доступных водителей или автобусов")
            return

        messagebox.showinfo(
            "Авто (AI)",
            f"Выбран водитель ID: {driver_id}\nАвтобус ID: {bus_id}"
        )

    # ================= ADD =================
    def add_shift(self):

        err = self.validate()

        if err:
            messagebox.showerror("Ошибка", err)
            return

        driver_id, bus_id = self.ai_select()

        db_date = datetime.strptime(
            self.date.get(),
            "%d.%m.%Y"
        ).strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO shifts(
                driver_id,
                bus_id,
                route,
                shift_date,
                start_time,
                end_time
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            driver_id,
            bus_id,
            self.route.get(),
            db_date,
            self.start.get(),
            self.end.get()
        ))

        conn.commit()
        conn.close()

        self.load()

    # ================= DELETE =================
    def delete(self):

        if not self.selected_id:
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM shifts WHERE id=?",
            (self.selected_id,)
        )

        conn.commit()
        conn.close()

        self.load()

    # ================= LOAD =================
    def load(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        SELECT shifts.id,
               drivers.full_name,
               buses.number,
               shifts.route,
               shifts.shift_date,
               shifts.start_time,
               shifts.end_time,
               shifts.hours
        FROM shifts
        JOIN drivers ON drivers.id = shifts.driver_id
        JOIN buses ON buses.id = shifts.bus_id
        ORDER BY shifts.id DESC
        """)

        for r in cur.fetchall():

            ru_date = datetime.strptime(
                r[4],
                "%Y-%m-%d"
            ).strftime("%d.%m.%Y")

            self.tree.insert("", "end", values=(
                r[0],
                r[1],
                r[2],
                r[3],
                ru_date,
                f"{r[5]} - {r[6]}",
                r[7]
            ))

        conn.close()