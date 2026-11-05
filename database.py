import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("gestion.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Department (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL UNIQUE,
            Description TEXT
        );

        CREATE TABLE IF NOT EXISTS Employee (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            DepartmentID INTEGER NOT NULL,
            FOREIGN KEY (DepartmentID) REFERENCES Department(ID)
        );

        CREATE TABLE IF NOT EXISTS Ticket (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Description TEXT NOT NULL,
            CreatorID INTEGER NOT NULL,
            TargetDepartmentID INTEGER NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Open'
                CHECK (Status IN ('Open', 'In treatment', 'Done', 'Canceled')),
            FOREIGN KEY (CreatorID) REFERENCES Employee(ID),
            FOREIGN KEY (TargetDepartmentID) REFERENCES Department(ID)
        );
    """)

    departments = [
        ("Informatique", "Support informatique"),
        ("Ressources humaines", "Gestion des employés"),
        ("Finance", "Comptabilité et paie"),
        ("Maintenance", "Maintenance des locaux"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO Department (Name, Description) VALUES (?, ?)",
        departments,
    )

    department_ids = {
        row["Name"]: row["ID"]
        for row in conn.execute("SELECT ID, Name FROM Department")
    }
    employees = [
        ("Alice Dupont", department_ids["Informatique"]),
        ("Bob Martin", department_ids["Informatique"]),
        ("Claire Bernard", department_ids["Ressources humaines"]),
        ("David Petit", department_ids["Finance"]),
        ("Emma Roux", department_ids["Maintenance"]),
    ]
    for name, department_id in employees:
        conn.execute(
            "INSERT INTO Employee (Name, DepartmentID) "
            "SELECT ?, ? "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM Employee WHERE Name = ? AND DepartmentID = ?"
            ")",
            (name, department_id, name, department_id),
        )

    conn.commit()
    conn.close()


def _query(sql, params=()):
    conn = _connect()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _execute(sql, params=()):
    conn = _connect()
    cur = conn.execute(sql, params)
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed
def check_login(employee_id):
    rows = _query("SELECT ID, Name, DepartmentID FROM Employee WHERE ID = ?",
                  (employee_id,))
    return rows[0] if rows else None
def get_departments():
    return _query("SELECT ID, Name FROM Department ORDER BY Name")


def get_employees():
    return _query("SELECT ID, Name, DepartmentID FROM Employee ORDER BY Name")


def insert_ticket(description, creator_id, department_id):
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO Ticket (Description, CreatorID, TargetDepartmentID, Status) "
        "VALUES (?, ?, ?, 'Open')",
        (description, creator_id, department_id),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id
_SELECT = ("SELECT t.ID, t.Description, d.Name AS Department, "
           "e.Name AS Creator, t.Status "
           "FROM Ticket t "
           "JOIN Department d ON d.ID = t.TargetDepartmentID "
           "JOIN Employee e ON e.ID = t.CreatorID ")
def get_my_tickets(employee_id):
    return _query(_SELECT + "WHERE t.CreatorID = ? ORDER BY t.ID DESC", (employee_id,))
def get_department_tickets(department_id):
    return _query(_SELECT + "WHERE t.TargetDepartmentID = ? ORDER BY t.ID DESC",
                  (department_id,))
def count_by_status(employee_id):
    rows = _query("SELECT Status, COUNT(*) AS n FROM Ticket "
                  "WHERE CreatorID = ? GROUP BY Status", (employee_id,))
    return {r["Status"]: r["n"] for r in rows}
def cancel_ticket(ticket_id, employee_id):
    return _execute("UPDATE Ticket SET Status = 'Canceled' "
                    "WHERE ID = ? AND CreatorID = ? AND Status = 'Open'",
                    (ticket_id, employee_id))


def get_ticket_status(ticket_id):
    rows = _query("SELECT Status FROM Ticket WHERE ID = ?", (ticket_id,))
    return rows[0]["Status"] if rows else None


def update_ticket_status(ticket_id, status, department_id):
    if status not in ("Open", "In treatment", "Done", "Canceled"):
        raise ValueError("Statut invalide : " + status)
    return _execute("UPDATE Ticket SET Status = ? "
                    "WHERE ID = ? AND TargetDepartmentID = ?",
                    (status, ticket_id, department_id))


initialize_database()
