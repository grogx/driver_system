import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from datetime import datetime

DB = "drivers.db"


class ShiftsTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_id = None
        self.hover_item = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # =========================
        # FILTER PANEL (BIGGER UI)
        # =========================
        top = ctk.CTkFrame(self, corner_radius=10)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.driver_filter = ctk.CTkEntry(
            top,
            placeholder_text="ФИО водителя",
            width=200,
            height=38
        )
        self.driver_filter.pack(side="left", padx=5)

        self.bus_filter = ctk.CTkEntry(
            top,
            placeholder_text="Автобус",
            width=160,
            height=38
        )
        self.bus_filter.pack(side="left", padx=5)

        self.date_filter = ctk.CTkEntry(
            top,
            placeholder_text="Дата (ДД.ММ.ГГГГ)",
            width=180,
            height=38
        )
        self.date_filter.pack(side="left", padx=5)

        ctk.CTkButton(
            top,
            text="🔍 Фильтр",
            command=self.load,
            width=130,
            height=38
        ).pack(side="left", padx=5)

        # =========================
        # TABLE
        # =========================
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "id",
            "driver",
            "bus",
            "route",
            "date",
            "start",
            "end",
            "hours"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # =========================
        # STYLE
        # =========================
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1e1e1e",
            foreground="white",
            rowheight=42,
            fieldbackground="#1e1e1e",
            font=("Arial", 14)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 15, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#2b6cb0")]
        )

        # HEADERS
        self.tree.heading("id", text="ID")
        self.tree.heading("driver", text="Водитель")
        self.tree.heading("bus", text="Автобус")
        self.tree.heading("route", text="Маршрут")
        self.tree.heading("date", text="Дата")
        self.tree.heading("start", text="Начало")
        self.tree.heading("end", text="Конец")
        self.tree.heading("hours", text="Часы")

        # WIDTH
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("driver", width=220)
        self.tree.column("bus", width=140)
        self.tree.column("route", width=140)
        self.tree.column("date", width=140)
        self.tree.column("start", width=120, anchor="center")
        self.tree.column("end", width=120, anchor="center")
        self.tree.column("hours", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_row
        )

        # =========================
        # EDIT PANEL
        # =========================
        bottom = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        bottom.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=10
        )

        self.route = ctk.CTkEntry(
            bottom,
            placeholder_text="Маршрут (например 25)",
            width=180,
            height=38
        )
        self.route.pack(side="left", padx=5)

        self.date = ctk.CTkEntry(
            bottom,
            placeholder_text="ДД.ММ.ГГГГ",
            width=160,
            height=38
        )
        self.date.pack(side="left", padx=5)

        self.start = ctk.CTkEntry(
            bottom,
            placeholder_text="08:00",
            width=120,
            height=38
        )
        self.start.pack(side="left", padx=5)

        self.end = ctk.CTkEntry(
            bottom,
            placeholder_text="16:00",
            width=120,
            height=38
        )
        self.end.pack(side="left", padx=5)

        ctk.CTkButton(
            bottom,
            text="✏ Редактировать",
            command=self.update,
            width=130,
            height=38
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            bottom,
            text="🗑 Удалить",
            command=self.delete,
            width=130,
            height=38
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            bottom,
            text="🔄 Обновить",
            command=self.load,
            width=130,
            height=38
        ).pack(side="left", padx=5)

        self.load()

    # =========================
    def load(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        query = """
        SELECT shifts.id,
               drivers.full_name,
               buses.number,
               shifts.route,
               shifts.shift_date,
               shifts.start_time,
               shifts.end_time,
               shifts.hours
        FROM shifts
        JOIN drivers ON shifts.driver_id = drivers.id
        JOIN buses ON shifts.bus_id = buses.id
        WHERE 1=1
        """

        params = []

        if self.driver_filter.get():
            query += " AND drivers.full_name LIKE ?"
            params.append(f"%{self.driver_filter.get()}%")

        if self.bus_filter.get():
            query += " AND buses.number LIKE ?"
            params.append(f"%{self.bus_filter.get()}%")

        if self.date_filter.get():

            try:
                db_date = datetime.strptime(
                    self.date_filter.get(),
                    "%d.%m.%Y"
                ).strftime("%Y-%m-%d")

                query += " AND shifts.shift_date = ?"
                params.append(db_date)

            except:
                pass

        cur.execute(query, params)

        rows = cur.fetchall()

        conn.close()

        for i, row in enumerate(rows):

            ru_date = datetime.strptime(
                row[4],
                "%Y-%m-%d"
            ).strftime("%d.%m.%Y")

            tag = "even" if i % 2 == 0 else "odd"

            self.tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    ru_date,
                    row[5],
                    row[6],
                    row[7]
                ),
                tags=(tag,)
            )

        self.tree.tag_configure(
            "even",
            background="#1e1e1e"
        )

        self.tree.tag_configure(
            "odd",
            background="#262626"
        )

    # =========================
    def select_row(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.selected_id = values[0]

        self.route.delete(0, "end")
        self.route.insert(0, values[3])

        self.date.delete(0, "end")
        self.date.insert(0, values[4])

        self.start.delete(0, "end")
        self.start.insert(0, values[5])

        self.end.delete(0, "end")
        self.end.insert(0, values[6])

    # =========================
    def update(self):

        if not self.selected_id:
            messagebox.showerror(
                "Ошибка",
                "Выберите запись"
            )
            return

        try:
            db_date = datetime.strptime(
                self.date.get(),
                "%d.%m.%Y"
            ).strftime("%Y-%m-%d")

        except:
            messagebox.showerror(
                "Ошибка",
                "Дата должна быть ДД.ММ.ГГГГ"
            )
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        UPDATE shifts
        SET route=?,
            shift_date=?,
            start_time=?,
            end_time=?
        WHERE id=?
        """, (
            self.route.get(),
            db_date,
            self.start.get(),
            self.end.get(),
            self.selected_id
        ))

        conn.commit()
        conn.close()

        self.load()

    # =========================
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