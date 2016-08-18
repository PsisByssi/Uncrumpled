import os
import shutil
import tempfile
import json

import pytest
import halt

from uncrumpled.core import dbapi
from util import get_all_data


class MixIn():
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
        cls.db = os.path.join(cls.tdir, 'test.db')
        dbapi.new_db(cls.db)

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)

    def setup_method(self, func):
        '''create fresh database for each test method'''
        self.db = os.path.join(self.tdir, func.__name__+'.db')
        try:
            os.remove(self.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.db)


class TestHotkeys(MixIn):
    profile = 'a profile'
    book = 'abook'
    hotkey = ['f5']

    def test_hotkey_create(self):
        rv = dbapi.hotkey_create(self.db, self.profile, self.book, self.hotkey)
        assert rv
        data = get_all_data(self.db, 'Hotkeys')[0]
        assert data[0] == self.profile
        assert data[1] == self.book
        assert data[2] == json.dumps(self.hotkey)

        rv = dbapi.hotkey_create(self.db, self.profile, self.book, self.hotkey)
        assert not rv


    def test_hotkey_delete(self):
        rv = dbapi.hotkey_delete(self.db, self.profile, self.book, self.hotkey)
        assert not rv

        dbapi.hotkey_create(self.db, self.profile, self.book, self.hotkey)

        rv = dbapi.hotkey_delete(self.db, self.profile, self.book, self.hotkey)
        assert rv
        data = get_all_data(self.db, 'Hotkeys')
        assert not data
