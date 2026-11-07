import os
import tkinter as tk
from tkinter import ttk, messagebox
import database as db
import tickets_ui as tui

BB , Bleu = '#003290', '#1565D8'
TITRE = ("Viga regular", 18, "bold")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IncidentDesk")
        self.user = None
        db.init_db()
        db.seed_initial_data()
        self.show_login()
        
    def clear(self):
        for w in self.winfo_children():
            w.destroy() 
    #-------------------Ecran1: connexion------------------
    def show_login(self):
        self.clear()
        self.geometry("420x500")
        frame = ttk.Frame(self, padding=30)
        frame.pack(expand=True)
        chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_gestion.png")
        self.logo_img = tk.PhotoImage(file=chemin)
        tk.Label(frame, image=self.logo_img).pack(pady=(0, 15))
        ttk.Label(frame, text="Connexion",
                  font=("Viga regular", 22, "bold")).pack()
        ttk.Label(frame, text="Entrez votre ID",
                  font=("Viga regular", 10, "bold")).pack(pady=(10, 5))
        self.entry_id = ttk.Entry(frame, width=35)
        self.entry_id.pack(ipady=6)
        ttk.Button(frame, text="Se connecter",
                   command=self.login).pack(fill="x", pady=20)
    def login(self):
        value = self.entry_id.get().strip()
        if not value:
            messagebox.showwarning("Attention",
                                    "Identifiant invalide")
            return
        user_row = db.authentifier(value)
        if user_row is None:
            messagebox.showerror("Erreur", "Employe introuvable.")
            return
        self.user = {
            "ID": user_row[0],
            "Name": user_row[1],
            "DepartmentID": user_row[2],
            "DeptName": user_row[3],
        }
        self.show_dashboard()
        
    def logout(self):
        self.user = None
        self.show_login()
    #--------------Ecran2:tableau de bord-------------------
    def show_dashboard(self):
        self.clear()
        self.geometry("1000x600")
        side = tk.Frame(self, bg=BB, width=210)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="IncidentDesk", bg=BB, fg="white",
                 font=("Viga regular", 14, "bold")).pack(pady=20)
        menu = [
            ("Tableau de bord", self.page_home),
            ("Mes tickets", lambda: tui.page_mine(self.content, self.user)),
            ("Tickets du departement", lambda: tui.page_dept(self.content, self.user)),
        ]
        for text, cmd in menu:
            tk.Button(side, text=text, command=cmd, bg=BB, fg="white",
            relief="flat", anchor="w", padx=15,pady=8,
            activebackground=Bleu, activeforeground="white").pack(fill="x", padx=10, pady=2)
        tk.Button(side, text="+ Nouveau ticket", command=self.new_ticket,
                  bg=Bleu, fg="white", relief="flat", pady=8,
                  activebackground=Bleu, activeforeground="white").pack(fill="x", padx=10, pady=15)
        tk.Button(side, text="Deconnexion", command=self.logout,
                          bg=BB, fg="white", relief="flat",anchor="w", padx=15,
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
        ttk.Label(
            self.content,
            text=f"Département : {self.user['DeptName']}",
            font=("Viga regular", 11),
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
                font=("Viga regular", 22, "bold"),
            ).pack()
        ttk.Label(
            self.content,
            text="Mes derniers tickets",
            font=("Viga regular", 16, "bold"),
        ).pack(anchor="w")
        tui.build_table(
            self.content,
            db.get_my_tickets(self.user["ID"])[:5],
        )
if __name__ == "__main__":
    App().mainloop()
