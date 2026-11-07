import tkinter as tk
from tkinter import messagebox, ttk

import database as db


LABELS = {
    "Open": "Ouvert",
    "In treatment": "En traitement",
    "Done": "Terminé",
    "Canceled": "Annulé",
}

LINE = "#C8D4E3"
ROW = 30
FOND = "#F5F8FC"
MARINE = "#0F2A5C"
B = "#1451A5"
BORDURE = "#C9D6EA"


def clear(parent):
    for widget in parent.winfo_children():
        widget.destroy()


def _ticket_values(ticket, show_creator=True):
    values = [
        ticket[0],
        ticket[1],
        ticket[3] or "",
        LABELS.get(ticket[4], ticket[4]),
    ]
    if show_creator:
        values.append(ticket[2] or "")
    return values


class TicketTable(ttk.Frame):
    def __init__(self, parent, tickets, show_creator=True, rows=8):
        super().__init__(parent)
        ttk.Style().configure("Treeview", rowheight=ROW)
        self.columns = ["ID", "Description", "Département", "Statut"]
        if show_creator:
            self.columns.append("Créateur")

        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            height=max(len(tickets), rows),
        )
        self.tree.pack(fill="both", expand=True)

        for column in self.columns:
            wide = column == "Description"
            self.tree.heading(column, text=column)
            self.tree.column(
                column,
                width=300 if wide else 120,
                minwidth=150 if wide else 70,
                stretch=wide,
            )

        for ticket in tickets:
            self.tree.insert(
                "",
                "end",
                iid=str(ticket[0]),
                values=_ticket_values(ticket, show_creator),
            )

        for event in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.tree.bind(event, lambda event: "break")
        self.tree.bind("<Configure>", lambda event: self.tree.after(10, self.draw_lines))

    def draw_lines(self):
        for widget in self.tree.winfo_children():
            widget.destroy()

        x = 0
        for column in self.columns[:-1]:
            x += self.tree.column(column, "width")
            tk.Frame(self.tree, bg=LINE, width=1).place(x=x, y=0, relheight=1)

        items = self.tree.get_children()
        box = self.tree.bbox(items[0]) if items else None
        y = box[1] if box else ROW
        while y < self.tree.winfo_height():
            tk.Frame(self.tree, bg=LINE, height=1).place(
                x=0, y=y, relwidth=1
            )
            y += ROW

    def selected_id(self):
        selection = self.tree.selection()
        return int(selection[0]) if selection else None


def build_table(parent, tickets):
    table = TicketTable(parent, tickets)
    table.pack(fill="both", expand=True, pady=10)
    return table


def _department_tickets(department_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.ID, t.Description, e.Name, d.Name, t.Status
        FROM Ticket t
        LEFT JOIN Employee e ON t.CreatorID = e.ID
        LEFT JOIN Department d ON t.TargetDepartmentID = d.ID
        WHERE t.TargetDepartmentID = ?
        ORDER BY t.ID DESC
        """,
        (department_id,),
    )
    tickets = cursor.fetchall()
    conn.close()
    return tickets


def _ticket_page(parent, user, tickets, title, mode):
    clear(parent)
    page = TicketsPage(parent, user, tickets, title, mode)
    page.pack(fill="both", expand=True)
    return page


def page_mine(parent, user):
    return _ticket_page(
        parent,
        user,
        db.get_my_tickets(user["ID"]),
        "Mes tickets",
        "mine",
    )


def page_dept(parent, user):
    return _ticket_page(
        parent,
        user,
        _department_tickets(user["DepartmentID"]),
        "Tickets du département",
        "department",
    )


class TicketsPage(ttk.Frame):
    def __init__(self, parent, user, tickets, title, mode):
        super().__init__(parent)
        self.user = user
        self.tickets = tickets
        self.title = title
        self.mode = mode

        ttk.Label(self, text=title, font=("Segoe UI", 16, "bold")).pack(
            anchor="w"
        )
        self.buttons = ttk.Frame(self)
        self.buttons.pack(side="bottom", anchor="w", pady=10)
        self.table = TicketTable(self, tickets, show_creator=mode != "mine")
        self.table.pack(fill="both", expand=True, pady=10)

        if mode == "mine":
            self.add_button("Annuler le ticket", self.cancel)
        else:
            self.add_button(
                "Prendre en charge",
                lambda: self.change("In treatment"),
            )
            self.add_button("Terminer", lambda: self.change("Done"))

    def add_button(self, text, command):
        ttk.Button(self.buttons, text=text, command=command).pack(
            side="left", padx=4
        )

    def selected_id(self):
        ticket_id = self.table.selected_id()
        if ticket_id is None:
            messagebox.showwarning("Attention", "Sélectionnez un ticket.")
        return ticket_id

    def reload(self):
        if self.mode == "mine":
            page_mine(self.master, self.user)
        else:
            page_dept(self.master, self.user)

    def cancel(self):
        ticket_id = self.selected_id()
        if ticket_id is None:
            return
        ticket = next((ticket for ticket in self.tickets if ticket[0] == ticket_id), None)
        if ticket is None or ticket[4] != "Open":
            messagebox.showwarning(
                "Attention",
                "Seul un ticket ouvert peut être annulé.",
            )
            return
        if not messagebox.askyesno("Confirmation", "Annuler ce ticket ?"):
            return
        db.update_ticket_status(ticket_id, "Canceled")
        self.reload()

    def change(self, status):
        ticket_id = self.selected_id()
        if ticket_id is None:
            return
        ticket = next((ticket for ticket in self.tickets if ticket[0] == ticket_id), None)
        if ticket is None or ticket[4] in ("Done", "Canceled"):
            messagebox.showwarning("Attention", "Ce ticket est déjà fermé.")
            return
        db.update_ticket_status(ticket_id, status)
        self.reload()


class NewTicketWindow(tk.Toplevel):
    def __init__(self, root, user, on_done):
        super().__init__(root)
        self.user = user
        self.on_done = on_done
        self.title("Nouveau ticket")
        self.geometry("440x440")
        self.resizable(False, False)
        self.configure(bg=FOND)
        self.transient(root)
        self.grab_set()

        frame = tk.Frame(self, bg=FOND, padx=28, pady=24)
        frame.pack(fill="both", expand=True)
        tk.Label(
            frame,
            text="Nouveau ticket",
            bg=FOND,
            fg=MARINE,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 16))
        tk.Label(
            frame,
            text="Description de l'incident",
            bg=FOND,
            fg=MARINE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        box = tk.Frame(
            frame,
            bg="white",
            highlightbackground=BORDURE,
            highlightthickness=1,
        )
        box.pack(fill="x", pady=(6, 16))
        self.description = tk.Text(
            box,
            height=7,
            wrap="word",
            relief="flat",
            bd=0,
            bg="white",
            fg=MARINE,
            font=("Segoe UI", 11),
            insertbackground=MARINE,
            padx=10,
            pady=8,
        )
        self.description.pack(fill="x")

        tk.Label(
            frame,
            text="Département concerné",
            bg=FOND,
            fg=MARINE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        departments = db.get_all_departments()
        self.departments = {department[1]: department[0] for department in departments}
        self.combo = ttk.Combobox(
            frame,
            values=list(self.departments),
            state="readonly",
            font=("Segoe UI", 11),
        )
        if self.departments:
            self.combo.current(0)
        self.combo.pack(fill="x", pady=(6, 22))
        tk.Button(
            frame,
            text="Envoyer",
            command=self.submit,
            bg=B,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            pady=12,
            activebackground="#1D57A8",
            activeforeground="white",
        ).pack(fill="x")
        self.description.focus_set()

    def submit(self):
        text = self.description.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning(
                "Attention",
                "Écrivez une description.",
                parent=self,
            )
            return
        department = self.departments.get(self.combo.get())
        if department is None:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un département.",
                parent=self,
            )
            return
        db.create_ticket(text, self.user["ID"], department)
        self.destroy()
        self.on_done()


def open_new_ticket(root, user, on_done):
    return NewTicketWindow(root, user, on_done)
