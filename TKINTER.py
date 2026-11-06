import tkinter as tk
from tkinter import messagebox, ttk
import ORM

MANAGER_ID = "R150193"  


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("320x180")

        ORM.init_db()
        try:
            ORM.seed_initial_data()
        except:
            pass

        frame = ttk.Frame(root, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Employee ID:").pack(anchor="w", pady=5)
        self.id_entry = ttk.Entry(frame, width=25)
        self.id_entry.pack(pady=5, fill="x")
        self.id_entry.focus()

        ttk.Button(frame, text="Login", command=self.handle_login).pack(pady=10, fill="x")

    def handle_login(self):
        emp_id = self.id_entry.get().strip()
        user = ORM.authentifier(emp_id)
        if user:
            self.root.destroy()
            main_root = tk.Tk()
            Dashboard(main_root, user)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid ID!")


class Dashboard:
    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user 
        self.is_manager = (current_user[0] == MANAGER_ID)

        self.root.title(f"Dashboard - {current_user[1]}")
        self.root.geometry("800x500")

        top_bar = ttk.Frame(root, padding=5)
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text=f"User: {current_user[1]} ({current_user[3]})").pack(side="left")
        ttk.Button(top_bar, text="Logout", command=self.logout).pack(side="right")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        
        self.tab_tickets = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tickets, text="Tickets")
        self.setup_tickets_tab()

        
        if not self.is_manager:
            self.tab_create = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_create, text="New Ticket")
            self.setup_create_tab()

    def setup_tickets_tab(self):
        frame = ttk.Frame(self.tab_tickets, padding=5)
        frame.pack(fill="both", expand=True)

        columns = ("ID", "Description", "Creator", "Department", "Status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        self.tree.pack(fill="both", expand=True, pady=5)

        
        self.tree.bind("<Double-1>", self.open_ticket_details)

        
        if self.is_manager:
            act_frame = ttk.Frame(frame, padding=5)
            act_frame.pack(fill="x")

            ttk.Label(act_frame, text="Set Status:").pack(side="left")
            self.status_var = tk.StringVar(value="Open")
            ttk.Combobox(act_frame, textvariable=self.status_var, values=["Open", "In treatment", "Done", "Canceled"],
                         state="readonly", width=15).pack(side="left", padx=5)
            ttk.Button(act_frame, text="Update", command=self.update_status).pack(side="left")

        self.load_tickets()

    def load_tickets(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in ORM.get_all_tickets():
            self.tree.insert("", "end", values=t)

    def open_ticket_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        ticket_data = self.tree.item(selected[0], "values")
        ticket_id, description, creator, department, status = ticket_data

        
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Ticket #{ticket_id} Details")
        detail_win.geometry("450x320")
        detail_win.minsize(400, 300)

        padding_frame = ttk.Frame(detail_win, padding=15)
        padding_frame.pack(fill="both", expand=True)

        
        info_frame = ttk.Frame(padding_frame)
        info_frame.pack(fill="x", pady=5)

        ttk.Label(info_frame, text=f"Ticket ID: #{ticket_id}", font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=f"Creator: {creator} | Department: {department}", font=("Arial", 9),
                  foreground="#555555").pack(anchor="w", pady=2)
        ttk.Label(info_frame, text=f"Status: {status}", font=("Arial", 9, "bold"), foreground="#0052CC").pack(
            anchor="w", pady=2)

        ttk.Separator(padding_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(padding_frame, text="Description:", font=("Arial", 10, "bold")).pack(anchor="w", pady=2)

        desc_text = tk.Text(padding_frame, wrap="word", height=8, font=("Arial", 10))
        desc_text.pack(fill="both", expand=True, pady=5)
        desc_text.insert("1.0", description)
        desc_text.config(state="disabled")  

        ttk.Button(padding_frame, text="Close", command=detail_win.destroy).pack(pady=5)

    def update_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a ticket.")
            return
        ticket_id = self.tree.item(selected[0], "values")[0]
        ORM.update_ticket_status(ticket_id, self.status_var.get())
        self.load_tickets()

    def setup_create_tab(self):
        frame = ttk.Frame(self.tab_create, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Description:").pack(anchor="w")
        self.desc_box = tk.Text(frame, height=4, width=40)
        self.desc_box.pack(pady=5)

        ttk.Label(frame, text=f"Target Department: {self.current_user[3]} (Locked)").pack(anchor="w", pady=5)
        ttk.Button(frame, text="Submit", command=self.submit_ticket).pack(pady=10)

    def submit_ticket(self):
        desc = self.desc_box.get("1.0", "end-1c").strip()
        if not desc:
            messagebox.showerror("Error", "Description required.")
            return

        ORM.create_ticket(desc, self.current_user[0], self.current_user[2])
        messagebox.showinfo("Success", "Ticket created.")
        self.desc_box.delete("1.0", "end")
        self.load_tickets()

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
