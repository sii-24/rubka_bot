import sqlite3

from classes.Event import Event
from classes.Worker import Worker
from classes.Stat import Stat
from config import ADMINS


class db:

    db = None
    cur = None

    def __init__(self):
        self.db = sqlite3.connect("rubka_bot.db")
        self.cur = self.db.cursor()
        self.db.execute('CREATE TABLE IF NOT EXISTS events(id PRIMARY KEY, date, place, equipment, person_id, comment, contact, user_id, approved, status)')
        self.db.execute('CREATE TABLE IF NOT EXISTS workers(id PRIMARY KEY, name, events)')
        self.db.execute('CREATE TABLE IF NOT EXISTS stat(all_events, active_events, archive_events)')
        self.db.commit()

    def __del__(self):
        self.db.close()


    def add_event(self, event: Event):
        self.cur.execute('INSERT INTO events VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (event.id, event.date, event.place, event.equipment, event.person_id, event.comment, event.contact, event.user_id, event.approved, event.status))
        self.db.commit()

    def edit_event(self, event: Event):
        self.cur.execute('UPDATE events SET id = ?, date = ?, place = ?, equipment = ?, person_id = ?, comment = ?, contact = ?, user_id = ?, approved = ?, status = ? WHERE id == ?', (event.id, event.date, event.place, event.equipment, event.person_id, event.comment, event.contact, event.user_id, event.approved, event.status, event.id))
        self.db.commit()

    def del_event(self, event: Event):
        self.cur.execute('DELETE FROM events WHERE id == ?', (event.id, ))
        self.db.commit()

    def approve_event(self, event_id: str, person_id):
        self.cur.execute('UPDATE events SET approved = ?, person_id = ? WHERE id == ?', ("1", person_id, event_id))
        self.db.commit()

    def archive_event(self, event_id: str):
        self.cur.execute('UPDATE events SET status = ?, WHERE event_id == ?', ("0", event_id))
        self.db.commit()

    
    def get_all_events(self):
        return [Event(*x) for x in self.cur.execute('SELECT * from events').fetchall()]

    def get_active_events(self):
        return [Event(*x) for x in self.cur.execute('SELECT * from events WHERE status == ?', ("1", )).fetchall()]
    
    def get_archive_events(self):
        return [Event(*x) for x in self.cur.execute('SELECT * from events WHERE status == ?', ("0", )).fetchall()]
    
    def get_user_events(self, user_id):
        return [Event(*x) for x in self.cur.execute('SELECT * from events WHERE user_id == ?', (user_id, )).fetchall()]
    
    def get_event(self, id: str):
        return Event(*self.cur.execute('SELECT * from events WHERE id == ?', (id, )).fetchall()[0])
    

    def get_stat(self):
        return Stat(*self.cur.execute('SELECT 1 from stat').fetchone())


    def get_workers(self):
        return [Worker(*x) for x in self.cur.execute('SELECT * from workers').fetchall()]
    
    def get_worker(self, id: str):
        return Worker(*self.cur.execute('SELECT * from workers WHERE id == ?', (id, )).fetchall()[0])

    def get_workers_id(self):
        return [x for x in self.cur.execute('SELECT id from workers').fetchall()]
    
    def get_worker_name(self, id: str):
        res = str(self.cur.execute('SELECT name from workers WHERE id == ?', (id, )).fetchone())[2:-3]
        if res:
            return res
        else:
            return "Любой"
    

    def edit_worker(self, worker: Worker):
            self.cur.execute('SELECT 1 FROM workers WHERE id = ? LIMIT 1', (worker.id, ))
            if self.cur.fetchone():
                self.cur.execute('UPDATE workers SET id = ?, name = ?, events = ? WHERE id == ?', (worker.id, worker.name, worker.events, worker.id))
            else:
                self.cur.execute('INSERT INTO workers VALUES(?, ?, ?)', (worker.id, worker.name, worker.events))
            self.db.commit()
