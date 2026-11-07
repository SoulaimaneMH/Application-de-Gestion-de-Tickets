import tkinter as tk
from tkinter import ttk, messagebox
import database as db

TITRE = ("Viga regular", 18, "bold")

LABELS = {
    "Open": "Ouvert",
    "In treatment": "En traitement",
    "Done": "Terminé",
    "Canceled": "Annulé",
}
REVERSE = {v: k for k, v in LABELS.items()}

class TicketTable(ttk.Treeview):
    COLS = ("ID", "Description", "Créateur", "Département", "Statut")
    WIDTHS = (50, 380, 120, 130, 110)

    def __init__(self, parent):
        super().__init__(parent, columns=self.COLS, show="headings")
        for col, w in zip(self.COLS, self.WIDTHS):
            self.heading(col, text=col)
            self.column(col, width=w, anchor="w", stretch=(col == "Description"))

    def load(self, rows):
        self.delete(*self.get_children())
        for r in rows:
            self.insert("", "end", values=(r[0], r[1], r[2], r[3], LABELS.get(r[4], r[4])))
        self.configure(height=min(max(len(rows), 1), 12))


class DeptPage(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.is_manager = user["DeptName"] == "Management"
        titre = "Tous les tickets" if self.is_manager else f"Tickets du département {user['DeptName']}"
        ttk.Label(self, text=titre, font=TITRE).pack(anchor="w")
        self.table = TicketTable(self)
        self.table.pack(fill="x", pady=10)
        bar = ttk.Frame(self)
        bar.pack(anchor="w")
        self.status = ttk.Combobox(bar, values=list(LABELS.values()),
                                   state="readonly", width=18)
        self.status.current(1)
        self.status.pack(side="left")
        ttk.Button(bar, text="Changer le statut",
                   command=self.change).pack(side="left", padx=8)
        self.refresh()

    def refresh(self):
        rows = db.get_all_tickets()
        if not self.is_manager:
            rows = [r for r in rows if r[3] == self.user["DeptName"]]
        self.table.load(rows)

    def change(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionne un ticket.")
            return
        ticket_id = self.table.item(sel[0])["values"][0]
        db.update_ticket_status(ticket_id, REVERSE[self.status.get()])
        self.refresh()


class NewTicketWindow(tk.Toplevel):
    def __init__(self, master, user, on_done):
        super().__init__(master)
        self.title("Nouveau ticket")
        self.geometry("420x330")
        self.transient(master)
        self.grab_set()
        self.user = user
        self.on_done = on_done
        self.depts = {d[1]: d[0] for d in db.get_all_departments()}
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Description").pack(anchor="w")
        self.text = tk.Text(frame, height=7, width=45)
        self.text.pack(pady=5)
        ttk.Label(frame, text="Département cible").pack(anchor="w")
        self.combo = ttk.Combobox(frame, values=list(self.depts), state="readonly")
        self.combo.current(0)
        self.combo.pack(fill="x", pady=5)
        ttk.Button(frame, text="Créer le ticket", command=self.save).pack(fill="x", pady=10)

    def save(self):
        desc = self.text.get("1.0", "end").strip()
        if not desc:
            messagebox.showwarning("Attention", "La description est vide.", parent=self)
            return
        db.create_ticket(desc, self.user["ID"], self.depts[self.combo.get()])
        self.destroy()
        self.on_done()


def clear(frame):
    for w in frame.winfo_children():
        w.destroy()


def build_table(parent, rows):
    table = TicketTable(parent)
    table.load(rows)
    table.pack(fill="x", pady=10)
    return table


def page_mine(content, user):
    clear(content)
    ttk.Label(content, text="Mes tickets", font=TITRE).pack(anchor="w")
    build_table(content, db.get_my_tickets(user["ID"]))


def page_dept(content, user):
    clear(content)
    DeptPage(content, user).pack(fill="both", expand=True)


def open_new_ticket(master, user, on_done):
    NewTicketWindow(master, user, on_done)
