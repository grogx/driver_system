import customtkinter as ctk
import sqlite3
import calendar
from datetime import datetime

DB = "drivers.db"

MONTHS_RU = [
    "Январь", "Февраль", "Март", "Апрель",
    "Май", "Июнь", "Июль", "Август",
    "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]


class CalendarView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.year = datetime.today().year
        self.month = datetime.today().month

        # =========================
        # GRID
        # =========================
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # =========================
        # TOP BAR
        # =========================
        top = ctk.CTkFrame(
            self,
            height=60,
            fg_color="#1a1a1a",
            corner_radius=12
        )

        top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=10
        )

        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            top,
            text="◀",
            width=60,
            font=("Arial", 16, "bold"),
            command=self.prev_month
        ).grid(row=0, column=0, padx=10, pady=10)

        self.title_lbl = ctk.CTkLabel(
            top,
            text="",
            font=("Arial", 24, "bold"),
            text_color="#ffffff"
        )

        self.title_lbl.grid(row=0, column=1)

        ctk.CTkButton(
            top,
            text="▶",
            width=60,
            font=("Arial", 16, "bold"),
            command=self.next_month
        ).grid(row=0, column=2, padx=10, pady=10)

        # =========================
        # CALENDAR GRID
        # =========================
        self.grid_frame = ctk.CTkFrame(
            self,
            fg_color="#111111",
            corner_radius=12
        )

        self.grid_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=10
        )

        for i in range(7):
            self.grid_frame.grid_columnconfigure(
                i,
                weight=1,
                uniform="col"
            )

        for i in range(7):
            self.grid_frame.grid_rowconfigure(
                i,
                weight=1,
                uniform="row"
            )

        # =========================
        # ERP INFO PANEL
        # =========================
        self.info = ctk.CTkTextbox(
            self,
            height=230,
            fg_color="#111111",
            border_width=2,
            border_color="#2b2b2b",
            corner_radius=12,
            font=("Consolas", 15),
            text_color="#ffffff"
        )

        self.info.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 10)
        )

        # =========================
        # TAGS
        # =========================
        self.configure_tags()

        # =========================
        # START
        # =========================
        self.render()

    # =========================
    # TAGS
    # =========================
    def configure_tags(self):

        self.info.tag_config(
            "title",
            foreground="#4da3ff"
        )

        self.info.tag_config(
            "header",
            foreground="#00d0ff"
        )

        self.info.tag_config(
            "line",
            foreground="#555555"
        )

        self.info.tag_config(
            "row1",
            foreground="#ffffff",
            background="#1b1b1b"
        )

        self.info.tag_config(
            "row2",
            foreground="#ffffff",
            background="#262626"
        )

        self.info.tag_config(
            "empty",
            foreground="#ff5555"
        )

    # =========================
    # FETCH COUNTS
    # =========================
    def fetch_counts(self):

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT shift_date, COUNT(*)
            FROM shifts
            GROUP BY shift_date
        """)

        data = {d: c for d, c in cur.fetchall()}

        conn.close()

        return data

    # =========================
    # FETCH DAY
    # =========================
    def fetch_day(self, date_str):

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                drivers.full_name,
                buses.number,
                shifts.route,
                shifts.start_time,
                shifts.end_time,
                shifts.hours
            FROM shifts
            JOIN drivers ON drivers.id = shifts.driver_id
            JOIN buses ON buses.id = shifts.bus_id
            WHERE shift_date=?
            ORDER BY start_time
        """, (date_str,))

        rows = cur.fetchall()

        conn.close()

        return rows

    # =========================
    # ERP TABLE
    # =========================
    def show_day(self, date_str):

        self.info.delete("0.0", "end")

        rows = self.fetch_day(date_str)

        # =========================
        # TITLE
        # =========================
        date_ru = datetime.strptime(
            date_str,
            "%Y-%m-%d"
        ).strftime("%d.%m.%Y")

        self.info.insert(
            "end",
            f"📅 СМЕНЫ НА {date_ru}\n\n",
            "title"
        )

        if not rows:

            self.info.insert(
                "end",
                "Нет смен",
                "empty"
            )

            return

        # =========================
        # HEADER
        # =========================
        header = (
            f"{'ВОДИТЕЛЬ':<30}"
            f"{'АВТО':<12}"
            f"{'МАРШРУТ':<12}"
            f"{'ВРЕМЯ':<22}"
            f"{'ЧАСЫ':<10}\n"
        )

        self.info.insert(
            "end",
            header,
            "header"
        )

        self.info.insert(
            "end",
            "─" * 95 + "\n",
            "line"
        )

        # =========================
        # ROWS
        # =========================
        for i, r in enumerate(rows):

            driver = str(r[0])[:28]
            bus = str(r[1])
            route = str(r[2])

            time = f"{r[3]} - {r[4]}"
            hours = str(r[5])

            line = (
                f"{driver:<30}"
                f"{bus:<12}"
                f"{route:<12}"
                f"{time:<22}"
                f"{hours:<10}\n"
            )

            tag = "row1" if i % 2 == 0 else "row2"

            self.info.insert(
                "end",
                line,
                tag
            )

    # =========================
    # RENDER
    # =========================
    def render(self):

        for w in self.grid_frame.winfo_children():
            w.destroy()

        month_name = MONTHS_RU[self.month - 1]

        self.title_lbl.configure(
            text=f"{month_name} {self.year}"
        )

        counts = self.fetch_counts()

        headers = [
            "Пн", "Вт", "Ср",
            "Чт", "Пт", "Сб", "Вс"
        ]

        for i, h in enumerate(headers):

            ctk.CTkLabel(
                self.grid_frame,
                text=h,
                font=("Arial", 15, "bold"),
                text_color="#4da3ff"
            ).grid(
                row=0,
                column=i,
                pady=5
            )

        cal = calendar.Calendar(firstweekday=0)

        weeks = cal.monthdayscalendar(
            self.year,
            self.month
        )

        while len(weeks) < 6:
            weeks.append([0] * 7)

        for r in range(6):

            for c in range(7):

                day = weeks[r][c]

                frame = ctk.CTkFrame(
                    self.grid_frame,
                    fg_color="#1a1a1a",
                    corner_radius=8
                )

                frame.grid(
                    row=r + 1,
                    column=c,
                    sticky="nsew",
                    padx=3,
                    pady=3
                )

                if day == 0:
                    continue

                ds = f"{self.year}-{self.month:02d}-{day:02d}"

                cnt = counts.get(ds, 0)

                text = f"{day}\n🚍 {cnt}" if cnt else str(day)

                ctk.CTkButton(
                    frame,
                    text=text,
                    font=("Arial", 16, "bold"),
                    fg_color="#2b2b2b",
                    hover_color="#3a3a3a",
                    text_color="white",
                    command=lambda d=ds: self.show_day(d)
                ).pack(
                    expand=True,
                    fill="both",
                    padx=2,
                    pady=2
                )

    # =========================
    # PREV
    # =========================
    def prev_month(self):

        self.month -= 1

        if self.month == 0:
            self.month = 12
            self.year -= 1

        self.render()

    # =========================
    # NEXT
    # =========================
    def next_month(self):

        self.month += 1

        if self.month == 13:
            self.month = 1
            self.year += 1

        self.render()