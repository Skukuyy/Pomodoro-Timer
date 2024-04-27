import sqlite3
#from dataclasses import dataclass


class Task:
    def __init__(self, id, name, description, completed):
        self.id = id
        self.name = name
        self.description = description
        self.completed = completed

    def __repr__(self):
        return f"Task({self.id}, {self.name}, {self.description}, {self.completed})"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('test.sqlite3')
        self.cursor = self.conn.cursor()
        self.cursor.row_factory = lambda cursor, param: Task(*param)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS task
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          description TEXT,
                          completed INTEGER DEFAULT 0 NOT NULL);""")
    
    def close_conn(self):
        self.conn.close()

    def get_tasks(self):
        return self.cursor.execute("SELECT * FROM task").fetchall()
    
    def get_incompleted_tasks(self):
        return self.cursor.execute("SELECT * FROM task WHERE completed = 0").fetchall()

    def get_task(self, id):
        return self.cursor.execute("SELECT * FROM task where id = ?", (id,)).fetchone()

    def add_task(self, name, description):
        self.cursor.execute("""INSERT INTO task (name, description)
                          VALUES (?, ?)""", (name, description))
        self.conn.commit()

    def update_task(self, name, description, new_name, new_description):
        self.cursor.execute(f"""UPDATE task
                          SET name = ?, description = ?
                          WHERE name = ? and description = ?""", (new_name, new_description, name, description))
        self.conn.commit()

    def change_state_task(self, name, description, completed):
        self.cursor.execute(f"""UPDATE task
                          SET completed = ?
                          WHERE name = ? and description = ?""", (completed, name, description))
        self.conn.commit()

    def remove_task(self, name, description):
        self.cursor.execute(f"DELETE FROM task WHERE name = ? and description = ?", (name, description))
        self.conn.commit()


database = Database()