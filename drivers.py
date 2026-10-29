import customtkinter as ctk
import sqlite3
from tkinter import messagebox, ttk
import re
from datetime import datetime

DB = "drivers.db"


class DriversWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # =========================
        # FORM
        # =========================
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        self.name = self.create_field(form, "ФИО")
        self.phone = self.create_field(form, "Телефон")
        self.exp = self.create_field(form, "Стаж")
        self.cat = self.create_field(form, "Категория")
        self.med = self.create_field(form, "Медкнижка № (MB-XXXX)")
        self.med_date = self.create_field(form, "Срок (ДД.ММ.ГГГГ)")

        # =========================
        # BUTTONS
        # =========================
        btns = ctk.CTkFrame(self)
        btns.grid(row=1, column=0, sticky="ew", padx=15, pady=10)

        ctk.CTkButton(btns, text="➕ Добавить", command=self.add, height=40, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="✏ Редактировать", command=self.update, height=40, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="🗑 Удалить", command=self.delete, height=40, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="🔄 Обновить", command=self.load, height=40, width=140).pack(side="left", padx=8)

        # =========================
        # TABLE
        # =========================
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=15)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "name", "phone", "exp", "cat", "med", "date")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1e1e1e",
            foreground="white",
            rowheight=42,
            font=("Arial", 13)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 14, "bold")
        )

        style.map("Treeview", background=[("selected", "#2b6cb0")])

        for col, text in zip(columns, ["ID", "ФИО", "Телефон", "Стаж", "Категория", "Медкнижка", "Срок"]):
            self.tree.heading(col, text=text)

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=260)
        self.tree.column("phone", width=180)
        self.tree.column("exp", width=90, anchor="center")
        self.tree.column("cat", width=120, anchor="center")
        self.tree.column("med", width=180)
        self.tree.column("date", width=140)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.select)

        # цвета статуса
        self.tree.tag_configure("ok", background="#1e1e1e")
        self.tree.tag_configure("warn", background="#2b2a1e")
        self.tree.tag_configure("bad", background="#3a1f1f")

        self.load()

    # =========================
    def create_field(self, parent, title):
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10)

        ctk.CTkLabel(frame, text=title, font=("Arial", 15, "bold")).pack(anchor="w")

        entry = ctk.CTkEntry(frame, width=180, height=38)
        entry.pack(pady=5)

        return entry

    # =========================
    # VALIDATION
    # =========================
    def validate(self):
        if not self.name.get().strip():
            return "ФИО не может быть пустым"

        if not self.exp.get().isdigit():
            return "Стаж должен быть числом"

        if not re.match(r"^\+?\d{10,15}$", self.phone.get()):
            return "Телефон должен содержать только цифры"

        if not re.match(r"^MB-\d{3,6}$", self.med.get()):
            return "Медкнижка должна быть вида MB-1234"

        try:
            datetime.strptime(self.med_date.get(), "%d.%m.%Y")
        except:
            return "Срок должен быть ДД.ММ.ГГГГ"

        return None

    # =========================
    def med_state(self, date_str):
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.today().date()

            if d < today:
                return "bad"
            elif (d - today).days <= 30:
                return "warn"
            return "ok"
        except:
            return "bad"

    # =========================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT id, full_name, phone, experience,
                   license_category, med_book_number, med_expiry_date
            FROM drivers
        """)

        rows = cur.fetchall()

        conn.close()

        for r in rows:

            tag = self.med_state(r[6])

            date_ru = ""

            try:
                if r[6]:
                    date_ru = datetime.strptime(
                        r[6],
                        "%Y-%m-%d"
                    ).strftime("%d.%m.%Y")
            except:
                date_ru = r[6]

            values = (
                r[0],
                r[1],
                r[2],
                r[3],
                r[4],
                r[5],
                date_ru
            )

            self.tree.insert(
                "",
                "end",
                values=values,
                tags=(tag,)
            )

    # =========================
    def select(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        data = self.tree.item(selected[0], "values")

        self.selected_id = data[0]

        self.name.delete(0, "end")
        self.name.insert(0, data[1])

        self.phone.delete(0, "end")
        self.phone.insert(0, data[2])

        self.exp.delete(0, "end")
        self.exp.insert(0, data[3])

        self.cat.delete(0, "end")
        self.cat.insert(0, data[4])

        self.med.delete(0, "end")
        self.med.insert(0, data[5])

        self.med_date.delete(0, "end")
        self.med_date.insert(0, data[6])

    # =========================
    def add(self):

        err = self.validate()

        if err:
            messagebox.showerror("Ошибка", err)
            return

        db_date = datetime.strptime(
            self.med_date.get(),
            "%d.%m.%Y"
        ).strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO drivers (
            full_name,
            phone,
            experience,
            license_category,
            med_book_number,
            med_expiry_date
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.name.get(),
            self.phone.get(),
            self.exp.get(),
            self.cat.get(),
            self.med.get(),
            db_date
        ))

        conn.commit()
        conn.close()

        self.load()

    # =========================
    def update(self):

        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите запись")
            return

        err = self.validate()

        if err:
            messagebox.showerror("Ошибка", err)
            return

        db_date = datetime.strptime(
            self.med_date.get(),
            "%d.%m.%Y"
        ).strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        UPDATE drivers
        SET full_name=?,
            phone=?,
            experience=?,
            license_category=?,
            med_book_number=?,
            med_expiry_date=?
        WHERE id=?
        """, (
            self.name.get(),
            self.phone.get(),
            self.exp.get(),
            self.cat.get(),
            self.med.get(),
            db_date,
            self.selected_id
        ))

        conn.commit()
        conn.close()

        self.load()

    # =========================
    def delete(self):

        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите водителя")
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM drivers WHERE id=?",
            (self.selected_id,)
        )

        conn.commit()
        conn.close()

        self.load()