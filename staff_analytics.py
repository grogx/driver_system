import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB = "drivers.db"


class StaffAnalyticsWindow(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # =====================================================
        # HEADER
        # =====================================================
        ctk.CTkLabel(
            self,
            text="📊 АНАЛИТИКА НАГРУЗКИ ВОДИТЕЛЕЙ",
            font=("Arial", 24, "bold")
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self,
            text="Контроль нагрузки и соблюдение нормы 40 часов",
            font=("Arial", 13)
        ).pack()

        ctk.CTkButton(
            self,
            text="🔄 Обновить",
            command=self.load
        ).pack(pady=10)

        # =====================================================
        # CHART FRAME
        # =====================================================
        self.chart_wrap = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        self.chart_wrap.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.canvas = None
        self.fig = None

        # =====================================================
        # TABLE FRAME
        # =====================================================
        table_frame = ctk.CTkFrame(self)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        # =====================================================
        # TABLE STYLE
        # =====================================================
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            rowheight=34,
            fieldbackground="#2b2b2b",
            borderwidth=0,
            font=("Arial", 12)
        )

        style.configure(
            "Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            font=("Arial", 12, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#347083")]
        )

        # =====================================================
        # TABLE
        # =====================================================
        columns = ("name", "hours", "status")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # HEADERS
        self.table.heading("name", text="ВОДИТЕЛЬ")
        self.table.heading("hours", text="ЧАСЫ")
        self.table.heading("status", text="СТАТУС")

        # COLUMNS
        self.table.column("name", width=450, anchor="w")
        self.table.column("hours", width=120, anchor="center")
        self.table.column("status", width=250, anchor="center")

        # SCROLLBAR
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # =====================================================
        # ROW COLORS
        # =====================================================
        self.table.tag_configure(
            "red",
            background="#512222"
        )

        self.table.tag_configure(
            "yellow",
            background="#4d4320"
        )

        self.table.tag_configure(
            "green",
            background="#1d4027"
        )

        self.load()

    # =====================================================
    # GET DATA
    # =====================================================
    def get_data(self):

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        SELECT d.full_name,
               IFNULL(SUM(s.hours),0) as total
        FROM drivers d
        LEFT JOIN shifts s ON s.driver_id = d.id
        GROUP BY d.id
        ORDER BY total DESC
        """)

        rows = cur.fetchall()

        conn.close()

        return rows

    # =====================================================
    # LOAD ALL
    # =====================================================
    def load(self):

        rows = self.get_data()

        self.draw_chart(rows)

        self.load_table(rows)

    # =====================================================
    # DRAW CHART
    # =====================================================
    def draw_chart(self, rows):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        if self.fig:
            self.fig.clf()

        names = [r[0] for r in rows]
        hours = [r[1] for r in rows]

        if not names:
            return

        # COLORS
        colors = [
            "#ff4d4d" if h > 40 else
            "#ffb84d" if h >= 30 else
            "#2ecc71"
            for h in hours
        ]

        # FIXED CHART HEIGHT
        chart_height = min(max(4, len(names) * 0.45), 7)

        self.fig = Figure(
            figsize=(13, chart_height),
            dpi=100
        )

        ax = self.fig.add_subplot(111)

        # SPACE FOR LONG NAMES
        self.fig.subplots_adjust(left=0.35)

        self.fig.patch.set_facecolor("#202020")
        ax.set_facecolor("#202020")

        y_pos = range(len(names))

        bars = ax.barh(
            y_pos,
            hours,
            color=colors,
            height=0.55
        )

        ax.set_yticks(y_pos)

        ax.set_yticklabels(
            names,
            fontsize=9,
            color="white"
        )

        ax.invert_yaxis()

        max_val = max(hours + [40]) + 10

        ax.set_xlim(0, max_val)

        # VALUES
        for bar in bars:

            width = bar.get_width()

            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)} ч",
                va="center",
                color="white",
                fontsize=10
            )

        # LIMIT LINE
        ax.axvline(
            x=40,
            color="#ff3333",
            linestyle="--",
            linewidth=2
        )

        ax.text(
            40.5,
            -0.7,
            "Норма 40 ч",
            color="#ff6666",
            fontsize=10
        )

        # GRID
        ax.grid(
            axis="x",
            linestyle="--",
            alpha=0.2
        )

        # TITLE
        ax.set_title(
            "Фактическая загрузка сотрудников",
            color="white",
            fontsize=16,
            pad=15
        )

        # AXIS COLORS
        ax.tick_params(
            axis='x',
            colors='white'
        )

        # REMOVE BORDER
        for spine in ax.spines.values():
            spine.set_visible(False)

        # TKINTER CANVAS
        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.chart_wrap
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="x",
            padx=10,
            pady=10
        )

    # =====================================================
    # LOAD TABLE
    # =====================================================
    def load_table(self, rows):

        # CLEAR TABLE
        for item in self.table.get_children():
            self.table.delete(item)

        overloaded = False

        # INSERT DATA
        for name, hours in rows:

            if hours > 40:
                status = "ПЕРЕГРУЗКА"
                tag = "red"
                overloaded = True

            elif hours >= 30:
                status = "ВЫСОКАЯ НАГРУЗКА"
                tag = "yellow"

            else:
                status = "НОРМА"
                tag = "green"

            self.table.insert(
                "",
                "end",
                values=(
                    name,
                    f"{hours} ч",
                    status
                ),
                tags=(tag,)
            )

        # WARNING
        if overloaded:

            messagebox.showwarning(
                "Внимание",
                "Есть сотрудники с переработкой."
            )