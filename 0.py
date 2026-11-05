import tkinter as tk
from tkinter import ttk, messagebox
import database as db
import tickets_ui as tui

Vert , Bleu = '#009036', '#1565D8'
TITRE = ("Segoe UI", 18, "bold")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IncidentDesk")
        self.user = None
        self.show_login()
    def clear(self):
        for w in self.winfo_children():
            w.destroy() 
    #-------------------Ecran1: connexion------------------
    def show_login(self):
        self.clear()
        self.geometry("420x420")
        frame = ttk.Frame(self, padding=30)
        frame.pack(expand=True)
        ttk.Label(frame, text="Gestion des incidents",
                 font=("Segoe UI", 16,"bold")).pack(pady=10)
        ttk.Label(frame, text="Identifiant employe").pack(anchor="w")
        self.entry_id = ttk.Entry(frame, width=30)
        self.entry_id.pack(pady=5)
        ttk.Button(frame, text="Se connecter",
                    command=self.login).pack(fill="x",pady=10)
    def login(self):
        value = self.entry_id.get().strip()
        if not value.isdigit():
            messagebox.showwarning("Attention",
                                    "Identifiant invalide")
            return
        user = db.check_login(int(value))
        if user is None :
            messagebox.showerror("Erreur", "Employe introuvable.")
            return
        self.user = user
        self.show_dashboard()
    def logout(self):
        self.user = None
        self.show_login()
    #--------------Ecran2:tableau de bord-------------------
    def show_dashboard(self):
        self.clear()
        self.geometry("1000x600")
        side = tk.Frame(self, bg=Vert, width=210)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="IncidentDesk", bg=Vert, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=20)
        menu = [
            ("Tableau de bord", self.page_home),
            ("Mes tickets", lambda: tui.page_mine(self.content, self.user)),
            ("Tickets du departement", lambda: tui.page_dept(self.content, self.user)),
        ]
        for text, cmd in menu:
            tk.Button(side, text=text, command=cmd, bg=Vert, fg="white",
            relief="flat", anchor="w", padx=15,pady=8,
            activebackground=Bleu, activeforeground="white").pack(fill="x", padx=10, pady=2)
        tk.Button(side, text="+ Nouveau ticket", command=self.new_ticket,
                  bg=Bleu, fg="white", relief="flat", pady=8,
                  activebackground=Bleu, activeforeground="white").pack(fill="x", padx=10, pady=15)
        tk.Button(side, text="Deconnexion", command=self.logout,
                          bg=Bleu, fg="white", relief="flat",anchor="w", padx=15,
                          activebackground=Bleu).pack(side="bottom", fill="x", pady=15)
        self.content = ttk.Frame(self, padding=20)
        self.content.pack(side="right", fill="both", expand=True)
        self.page_home()    

    def new_ticket(self):
        tui.open_new_ticket(
            self,
            self.user,
            lambda: tui.page_mine(self.content, self.user),
        )

    def page_home(self):
        tui.clear(self.content)
        ttk.Label(
            self.content,
            text=f"Bonjour, {self.user['Name']}",
            font=TITRE,
        ).pack(anchor="w")
        counts = db.count_by_status(self.user["ID"])
        cards = ttk.Frame(self.content)
        cards.pack(fill="x", pady=15)
        for status in ("Open", "In treatment", "Done"):
            card = ttk.LabelFrame(
                cards,
                text=tui.LABELS[status],
                padding=15,
            )
            card.pack(side="left", expand=True, fill="x", padx=5)
            ttk.Label(
                card,
                text=str(counts.get(status, 0)),
                font=("Segoe UI", 22, "bold"),
            ).pack()
        ttk.Label(
            self.content,
            text="Mes derniers tickets",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tui.build_table(
            self.content,
            db.get_my_tickets(self.user["ID"])[:5],
        )
 












if __name__ == "__main__":
    App().mainloop()
