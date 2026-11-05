from tkinter import ttk

LABELS = {"Open": "Ouvert", "In treatment": "En traitement",
          "Done": "Termine", "Canceled": "Annule"}
def clear(parent):
    for w in parent.winfo_children():
        w.destroy()
def build_table(parent, tickets):
    ttk.Label(parent, text=str(tickets)).pack()
def page_mine(parent, user):
    clear(parent)
    ttk.Label(parent, text="Mes tickets (a venir)").pack()
def page_dept(parent, user):
    clear(parent)
    ttk.Label(parent, text="Tickets du departement (a venir)").pack()
def open_new_ticket(root, user, on_done):
    print("Nouveau ticket (a venir)")
