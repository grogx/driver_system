import customtkinter as ctk
import sqlite3
from datetime import datetime

DB = "drivers.db"


class DispatcherDashboard(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # =====================================================
        # MAIN STYLE
        # =====================================================
        self.configure(fg_color="#0f0f0f")

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # =====================================================
        # HEADER
        # =====================================================
        header = ctk.CTkFrame(
            self,
            fg_color="#161616",
            corner_radius=18,
            height=90
        )

        header.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=20,
            pady=(20, 10)
        )

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        # TITLE
        ctk.CTkLabel(
            header,
            text="🚦 ERP ДИСПЕТЧЕРСКИЙ ЦЕНТР",
            font=("Arial", 30, "bold"),
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=(15, 0)
        )

        # TIME
        self.time_label = ctk.CTkLabel(
            header,
            text="",
            font=("Arial", 15),
            text_color="#bdbdbd"
        )

        self.time_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=28,
            pady=(0, 15)
        )

        # REFRESH BUTTON
        ctk.CTkButton(
            header,
            text="🔄 ОБНОВИТЬ",
            width=180,
            height=42,
            font=("Arial", 15, "bold"),
            fg_color="#1f4e79",
            hover_color="#2d6aa1",
            command=self.load
        ).grid(
            row=0,
            column=1,
            rowspan=2,
            padx=25
        )

        # =====================================================
        # KPI CARDS
        # =====================================================
        self.card_drivers = self.create_card(
            "👨‍✈️ ВОДИТЕЛИ",
            "#17351f",
            1,
            0
        )

        self.card_buses = self.create_card(
            "🚌 АВТОБУСЫ",
            "#142b40",
            1,
            1
        )

        self.card_shifts = self.create_card(
            "📅 СМЕНЫ",
            "#3a2c12",
            1,
            2
        )

        self.card_hours = self.create_card(
            "⏱ ЧАСЫ",
            "#3a1616",
            1,
            3
        )

        # =====================================================
        # MAIN ANALYTICS PANEL
        # =====================================================
        self.analytics = ctk.CTkFrame(
            self,
            fg_color="#161616",
            corner_radius=20
        )

        self.analytics.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=20,
            pady=15
        )

        self.analytics.grid_columnconfigure((0, 1), weight=1)

        # =====================================================
        # STATUS BLOCK
        # =====================================================
        self.status_block = ctk.CTkFrame(
            self.analytics,
            fg_color="#1e7f3f",
            corner_radius=18,
            height=180
        )

        self.status_block.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=15,
            pady=15
        )

        self.status_title = ctk.CTkLabel(
            self.status_block,
            text="СТАТУС АВТОПАРКА",
            font=("Arial", 18, "bold"),
            text_color="white"
        )

        self.status_title.pack(pady=(25, 10))

        self.status_label = ctk.CTkLabel(
            self.status_block,
            text="",
            font=("Arial", 28, "bold"),
            text_color="white"
        )

        self.status_label.pack(pady=10)

        # =====================================================
        # INFO BLOCK
        # =====================================================
        self.info_block = ctk.CTkFrame(
            self.analytics,
            fg_color="#1b1b1b",
            corner_radius=18
        )

        self.info_block.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=15,
            pady=15
        )

        self.info_title = ctk.CTkLabel(
            self.info_block,
            text="📈 ERP АНАЛИТИКА",
            font=("Arial", 20, "bold"),
            text_color="white"
        )

        self.info_title.pack(pady=(20, 15))

        self.info_text = ctk.CTkTextbox(
            self.info_block,
            font=("Consolas", 15),
            height=220,
            fg_color="#121212",
            text_color="#eaeaea",
            border_width=0
        )

        self.info_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.load()

    # =====================================================
    # CREATE KPI CARD
    # =====================================================
    def create_card(self, title, color, row, col):

        frame = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=20,
            height=150
        )

        frame.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=15,
            pady=10
        )

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 17, "bold"),
            text_color="#d9d9d9"
        )

        title_label.pack(pady=(22, 8))

        value_label = ctk.CTkLabel(
            frame,
            text="0",
            font=("Arial", 42, "bold"),
            text_color="white"
        )

        value_label.pack()

        frame.value_label = value_label

        return frame

    # =====================================================
    # LOAD DATA
    # =====================================================
    def load(self):

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        # =====================================================
        # KPI
        # =====================================================
        cur.execute("SELECT COUNT(*) FROM drivers")
        drivers = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM buses")
        buses = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM shifts")
        shifts = cur.fetchone()[0]

        cur.execute("SELECT IFNULL(SUM(hours),0) FROM shifts")
        hours = cur.fetchone()[0]

        # =====================================================
        # MEDICAL WARNING
        # =====================================================
        expired = 0

        try:
            cur.execute("""
                SELECT med_expiry_date
                FROM drivers
            """)

            for row in cur.fetchall():

                if row[0]:

                    med_date = datetime.strptime(
                        row[0],
                        "%Y-%m-%d"
                    ).date()

                    if med_date < datetime.today().date():
                        expired += 1

        except:
            pass

        conn.close()

        # =====================================================
        # UPDATE KPI
        # =====================================================
        self.card_drivers.value_label.configure(text=str(drivers))
        self.card_buses.value_label.configure(text=str(buses))
        self.card_shifts.value_label.configure(text=str(shifts))
        self.card_hours.value_label.configure(text=str(hours))

        # =====================================================
        # STATUS LOGIC
        # =====================================================
        if hours > 200:

            self.status_block.configure(
                fg_color="#8B0000"
            )

            self.status_label.configure(
                text="⚠ ПЕРЕГРУЗКА"
            )

        elif hours > 120:

            self.status_block.configure(
                fg_color="#b8860b"
            )

            self.status_label.configure(
                text="⚠ ВЫСОКАЯ НАГРУЗКА"
            )

        else:

            self.status_block.configure(
                fg_color="#1e7f3f"
            )

            self.status_label.configure(
                text="✔ НОРМА"
            )

        # =====================================================
        # TIME
        # =====================================================
        self.time_label.configure(
            text=f"Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

        # =====================================================
        # ERP INFO
        # =====================================================
        self.info_text.delete("0.0", "end")

        self.info_text.insert(
            "end",
            "ERP СТАТИСТИКА АВТОПАРКА\n"
        )

        self.info_text.insert(
            "end",
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        self.info_text.insert(
            "end",
            f"👨‍✈️ Водителей в системе: {drivers}\n\n"
        )

        self.info_text.insert(
            "end",
            f"🚌 Автобусов в системе: {buses}\n\n"
        )

        self.info_text.insert(
            "end",
            f"📅 Всего смен: {shifts}\n\n"
        )

        self.info_text.insert(
            "end",
            f"⏱ Общая нагрузка: {hours} ч.\n\n"
        )

        self.info_text.insert(
            "end",
            f"🩺 Просроченных медкнижек: {expired}\n\n"
        )

        # =====================================================
        # ПОКАЗ ДАТ В РУССКОМ ФОРМАТЕ
        # =====================================================
        try:

            conn = sqlite3.connect(DB)
            cur = conn.cursor()

            cur.execute("""
                SELECT full_name, med_expiry_date
                FROM drivers
                WHERE med_expiry_date IS NOT NULL
                ORDER BY med_expiry_date
                LIMIT 5
            """)

            rows = cur.fetchall()

            conn.close()

            if rows:

                self.info_text.insert(
                    "end",
                    "📋 БЛИЖАЙШИЕ МЕДОСМОТРЫ:\n\n"
                )

                for row in rows:

                    date_ru = datetime.strptime(
                        row[1],
                        "%Y-%m-%d"
                    ).strftime("%d.%m.%Y")

                    self.info_text.insert(
                        "end",
                        f"• {row[0]} — {date_ru}\n"
                    )

                self.info_text.insert(
                    "end",
                    "\n"
                )

        except:
            pass

        if expired > 0:

            self.info_text.insert(
                "end",
                "⚠ Требуется обновление документов персонала\n"
            )

        else:

            self.info_text.insert(
                "end",
                "✔ Все медкнижки актуальны\n"
            )