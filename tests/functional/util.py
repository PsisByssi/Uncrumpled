
import os
import tempfile
import shutil
import asyncio

import peasoup

from uncrumpled.core import dbapi
from uncrumpled import main, core


def get_mainpath():
    pass


class TestMain():
    def __init__(self):
    def setup_class(cls):
         q
        self._test_queue = queue.Queue()
        pardir = os.path.join(os.getcwd(), os.path.pardir)
        path = MyAppBuilder.rel_path(pardir)
        self.start_testing = False
        super().__init__(main_file=path)
        cls.tdir = tempfile.mkdtemp()
        db = os.path.join(cls.tdir, 'test.db')
        dbapi.new_db(db)
        main_file = peasoup.AppBuilder.rel_path(main.__file__)
        cls.core = core.Core(db, main_file=main_file)
        cls.name = 'some random profile'
        cls.event_loop = asyncio.get_event_loop()

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)
        cls.event_loop.close()

