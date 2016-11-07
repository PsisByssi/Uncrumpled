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


class MixIn():
    def run(self, func, *args, **kwargs):
        '''
        some isolation if we change from generaotrs
        '''
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


class MixInTestHelper(MixIn):
    '''
    Test helper when the mocked app is not required
    '''
    profile = 'test profile'
    book = 'test book'
    program = 'testprogram'
    hotkey = ['f5']
    specific = None
    loose = None
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
        # cls.db = os.path.join(cls.tdir, 'test.db')
        # dbapi.new_db(cls.db)
        cls.core = Core(db='')
        cls.event_loop = asyncio.get_event_loop()

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)
        cls.event_loop.close()

    def setup_method(self, func):
        '''create fresh database for each test method'''
        self.core.db = os.path.join(self.tdir, func.__name__+'.db')
        try:
            os.remove(self.core.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.core.db)


# A testable uncrumpled main app
class EasyUncrumpled(peasoup.AppBuilder, MixIn):
    def __init__(self):
        self.data_dir = self.setup_data_dir()
        pardir = os.path.abspath(join(os.path.dirname(__file__), os.path.pardir))
        os.chdir(pardir)
        super().__init__(main_file=join(pardir, 'uncrumpled', 'main.py'))
        self.setup_dirs()
        self.SYSTEM = copy.deepcopy(system_base)

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
