import os
from os.path import join
import sqlite3
import tempfile

import peasoup

from uncrumpled.core.dbapi import create


def get_all_data(db, table):
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute('select * from '+ table)
        return cur.fetchall()


# A testable uncrumpled main app
class EasyUncrumpled(peasoup.AppBuilder):
    def __init__(self):
        self.data_dir = self.setup_data_dir()
        pardir = os.path.abspath(join(os.path.dirname(__file__), os.path.pardir))
        os.chdir(pardir)
        super().__init__(main_file=join(pardir, 'uncrumpled', 'main.py'))
        self.setup_dirs()

    def setup_dirs(self):
        # This is copied from main.py, importing direcly was
        # being wierd, kivy kept opening windows and messing with pytest
        self.data_dir = self.setup_data_dir()
        self.db = join(self.data_dir, 'test.db')
        create.new_db(self.db)
        self.notedir = join(self.data_dir, 'notes')
        os.makedirs(self.notedir, exist_ok=True)

    def setup_data_dir(self):
        self.tdir = tempfile.mkdtemp()
        return self.tdir
