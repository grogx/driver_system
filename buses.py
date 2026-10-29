import customtkinter as ctk
import sqlite3
from tkinter import messagebox, ttk

DB = "drivers.db"


# =========================
# TABLE STYLE (BIGGER FIX)
# =========================
def setup_table_style():
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#1e1e1e",
        foreground="white",
        rowheight=44,  # 🔥 ещё крупнее строки
        fieldbackground="#1e1e1e",
        font=("Arial", 14)  # 🔥 увеличен шрифт
    )

    style.configure(
        "Treeview.Heading",
        background="#1f1f1f",
        foreground="white",
        font=("Arial", 15, "bold")  # 🔥 заголовки крупнее
    )

    style.map(
        "Treeview",
        background=[("selected", "#2b6cb0")]
    )


class BusesWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        setup_table_style()

        self.selected_id = None

        # =========================
        # GRID FIX
        # =========================
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # =========================
        # FORM
        # =========================
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.number = self.create_field(form, "Госномер")
        self.model = self.create_field(form, "Модель")
        self.capacity = self.create_field(form, "Вместимость")

        # =========================
        # BUTTONS
        # =========================
        btns = ctk.CTkFrame(self)
        btns.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkButton(btns, text="➕ Добавить", command=self.add, height=40).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="✏ Редактировать", command=self.update, height=40).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🗑 Удалить", command=self.delete, height=40).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🔄 Обновить", command=self.load, height=40).pack(side="left", padx=5)

        # =========================
        # TABLE
        # =========================
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "number", "model", "capacity"),
            show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("number", text="Госномер")
        self.tree.heading("model", text="Модель")
        self.tree.heading("capacity", text="Вместимость")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("number", width=200)
        self.tree.column("model", width=260)
        self.tree.column("capacity", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.select)

        self.load()

    # =========================
    # FIELD (BIGGER INPUTS)
    # =========================
    def create_field(self, parent, title):
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 15, "bold")  # 🔥 крупнее
        ).pack(anchor="w")

        entry = ctk.CTkEntry(
            frame,
            width=200,
            height=38,
            font=("Arial", 14)  # 🔥 крупный ввод
        )
        entry.pack(pady=5)

        return entry

    # =========================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT * FROM buses")

        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    # =========================
    def select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        data = self.tree.item(selected[0], "values")

        self.selected_id = data[0]

        self.number.delete(0, "end")
        self.number.insert(0, data[1])

        self.model.delete(0, "end")
        self.model.insert(0, data[2])

        self.capacity.delete(0, "end")
        self.capacity.insert(0, data[3])

    # =========================
    def add(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO buses(number, model, capacity)
        VALUES (?, ?, ?)
        """, (
            self.number.get(),
            self.model.get(),
            self.capacity.get()
        ))

        conn.commit()
        conn.close()
        self.load()

    # =========================
    def update(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите автобус")
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        UPDATE buses
        SET number=?, model=?, capacity=?
        WHERE id=?
        """, (
            self.number.get(),
            self.model.get(),
            self.capacity.get(),
            self.selected_id
        ))

        conn.commit()
        conn.close()
        self.load()

    # =========================
    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите автобус")
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("DELETE FROM buses WHERE id=?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load()