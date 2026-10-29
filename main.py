import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

from database import init_db

from drivers import DriversWindow
from buses import BusesWindow
from shifts import ShiftsWindow
from shifts_table import ShiftsTable
from reports import ReportsWindow
from dispatcher_dashboard import DispatcherDashboard
from staff_analytics import StaffAnalyticsWindow
from calendar_view import CalendarView
from sync_1c import export_to_1c, import_from_1c


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

DB = "drivers.db"


# =========================
# LOGIN
# =========================
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ERP Автопарк — вход")
        self.geometry("420x360")
        self.resizable(False, False)

        self.main_app = None

        ctk.CTkLabel(self, text="ERP СИСТЕМА",
                     font=("Arial", 24, "bold")).pack(pady=25)

        self.username = ctk.CTkEntry(self, placeholder_text="Логин", width=250, height=40)
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Пароль", show="*", width=250, height=40)
        self.password.pack(pady=10)

        ctk.CTkButton(self, text="Войти",
                      width=200, height=40,
                      command=self.login).pack(pady=25)

    def login(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (self.username.get(), self.password.get())
        )

        row = cur.fetchone()
        conn.close()

        if row:
            self.withdraw()
            self.main_app = MainApp(self, row[0])
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


# =========================
# MAIN APP
# =========================
class MainApp(ctk.CTkToplevel):
    def __init__(self, login_window, role):
        super().__init__()

        self.login_window = login_window
        self.role = role
        self.current_frame = None
        self.alive = True

        today = datetime.now().strftime("%d.%m.%Y")
        self.title(f"ERP Автопарк | {role.upper()} | {today}")

        try:
            self.state("zoomed")
        except:
            self.attributes("-fullscreen", True)

        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        # =========================
        # GRID
        # =========================
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # =========================
        # NAVBAR
        # =========================
        self.navbar = ctk.CTkFrame(self, height=60)
        self.navbar.grid(row=0, column=0, sticky="ew")
        self.navbar.grid_propagate(False)
        self.navbar.grid_columnconfigure(0, weight=1)

        self.menu_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.menu_frame.pack(side="left", padx=10)

        self.right_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.right_frame.pack(side="right", padx=10)

        # =========================
        # MAIN AREA
        # =========================
        self.main_area = ctk.CTkFrame(self)
        self.main_area.grid(row=2, column=0, sticky="nsew")

        self.create_menu()
        self.show_page(DispatcherDashboard)

    # =========================
    # PAGE SWITCH
    # =========================
    def show_page(self, page):
        if not self.alive:
            return

        try:
            if self.current_frame is not None:
                self.current_frame.destroy()

            self.current_frame = page(self.main_area)
            self.current_frame.pack(fill="both", expand=True)

        except Exception as e:
            print("PAGE ERROR:", e)

    # =========================
    # MENU
    # =========================
    def create_menu(self):

        menu = [
            ("Панель", DispatcherDashboard),
            ("Водители", DriversWindow),
            ("Автобусы", BusesWindow),
            ("Смены", ShiftsWindow),
            ("Таблица", ShiftsTable),
            ("Календарь", CalendarView),
            ("Аналитика", StaffAnalyticsWindow),
            ("Отчёты", ReportsWindow),
        ]

        for text, page in menu:
            ctk.CTkButton(
                self.menu_frame,
                text=text,
                width=110,
                command=lambda p=page: self.show_page(p)
            ).pack(side="left", padx=5, pady=10)

        # =========================
        # 1C BUTTONS (FIXED LAYOUT)
        # =========================

        self.sync_status = ctk.CTkLabel(
            self.right_frame,
            text="",
            width=120,
            anchor="w",
            text_color="#aaaaaa"
        )
        self.sync_status.pack(side="left", padx=8)

        ctk.CTkButton(
            self.right_frame,
            text="📥 Импорт",
            width=90,
            fg_color="#1f4e79",
            hover_color="#2a6aa3",
            command=self.import_1c
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.right_frame,
            text="📤 Экспорт",
            width=90,
            fg_color="#2e8b57",
            hover_color="#3cb371",
            command=self.export_1c
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.right_frame,
            text="Выход",
            width=90,
            fg_color="red",
            hover_color="#aa0000",
            command=self.exit_app
        ).pack(side="left", padx=5)

    # =========================
    def export_1c(self):
        result = export_to_1c()
        self.sync_status.configure(text="✔ экспорт")
        messagebox.showinfo("1C", result)

    def import_1c(self):
        result = import_from_1c()
        self.sync_status.configure(text="✔ импорт")
        messagebox.showinfo("1C", result)

    # =========================
    def exit_app(self):
        self.alive = False

        try:
            if self.current_frame:
                self.current_frame.destroy()
        except:
            pass

        try:
            self.destroy()
        except:
            pass

        try:
            self.login_window.destroy()
        except:
            pass


# =========================
# RUN
# =========================
if __name__ == "__main__":
    init_db()
    app = LoginApp()
    app.mainloop()