import os
from os.path import join
import sqlite3
import tempfile
import asyncio
import shutil
import copy
from types import GeneratorType

import peasoup

from uncrumpled.presenter.util import system_base
from uncrumpled.core.dbapi import create
from uncrumpled.core import dbapi, Core

UNCRUMPLED = 'uncrumpled'


def get_all_data(db, table):
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute('select * from '+ table)
        return cur.fetchall()


# A testable uncrumpled main app
class EasyUncrumpled(peasoup.AppBuilder):
    def __init__(self):
        pardir = os.path.abspath(join(os.path.dirname(__file__), os.path.pardir))
        os.chdir(pardir)
        super().__init__(main_file=join(pardir, 'uncrumpled', 'main.py'))
        self.setup_dirs()
        self.core = Core(db=self.db)
        self.DEVELOPING = True
        self.core.DEVELOPING = True

    def setup_dirs(self):
        # This is copied from main.py, importing direcly was
        # being wierd, kivy kept opening windows and messing with pytest
        self.data_dir = tempfile.mkdtemp()
        self.db = join(self.data_dir, 'test.db')
        create.new_db(self.db)
        self.notedir = join(self.data_dir, 'notes')
        os.makedirs(self.notedir, exist_ok=True)


class MixInTestHelper():
    '''
    Test helper
    New db and system every method
    '''
    profile = 'test profile'
    book = 'test book'
    program = 'testprogram'
    hotkey = ['f5']
    specific = None
    loose = None

    def setup_class(cls):
        cls.app = EasyUncrumpled()
        cls.event_loop = asyncio.get_event_loop()

    def teardown_class(cls):
        shutil.rmtree(cls.app.data_dir)
        cls.event_loop.close()

    def setup_method(self, func):
        '''create fresh database and system for each test method'''
        self.system = copy.deepcopy(system_base)
        self.app.SYSTEM = self.system
        self.app.db = os.path.join(self.app.data_dir, func.__name__+'.db')
        self.app.core.db = self.app.db
        try:
            os.remove(self.app.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.app.db)

    def run(self, func, *args, **kwargs):
        ''' some abstraction if we change from generaotrs or async etc'''
        res = func(*args, **kwargs)
        if type(res) != GeneratorType:
            return res
        else:
            res = list(res)
            if len(res) == 1:
                return res[0]
            if res == []:
                return False
            return res

