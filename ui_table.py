import tkinter as tk
from tkinter import ttk


class Table(ttk.Treeview):
    def __init__(self, parent, columns):
        super().__init__(parent, columns=columns, show="headings")

        self.columns_list = columns

        for col in columns:
            self.heading(col, text=col)
            self.column(col, width=120, anchor="center")

        self.pack(fill="both", expand=True)

    def clear(self):
        for item in self.get_children():
            self.delete(item)

    def load_data(self, rows):
        self.clear()
        for row in rows:
            self.insert("", "end", values=row)