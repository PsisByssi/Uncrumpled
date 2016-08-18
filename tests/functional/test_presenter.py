'''
    Testing all our api calls
    Test requires the uncrumpled core
'''
import os
import tempfile
import shutil
import asyncio
import pytest

from uncrumpled.core import Core
from uncrumpled.core import dbapi
from uncrumpled.presenter import requests as req

class App():
    pass

class Mixin():
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
        cls.app = App()
        cls.app.core = Core(db='')
        cls.event_loop = asyncio.get_event_loop()

    def setup_method(self, func):
        '''create fresh database for each test method'''
        self.app.core.db = os.path.join(self.tdir, func.__name__+'.db')
        try:
            os.remove(self.app.core.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.app.core.db)

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)
        cls.event_loop.close()

    def run(self, func, *args, **kwargs):
        res = func(*args, **kwargs) # ASYNC
        if len(res) == 1:
            return res[0]
        return res
        # return self.event_loop.run_until_complete(func())


class TestPresenter(Mixin):
    # @asyncio.coroutine #ASYNC hmm, do not think this is needed
    def test_profile(self):
        profile = 'some test profile'
        response = self.run(req.profile_create, self.app, profile=profile)
        assert 'profile created' in response[0].lower()

        response = self.run(req.profile_create, self.app, profile)
        assert 'profile already in use' in response[0].lower()

        response = self.run(req.profile_delete, self.app, profile)
        assert 'profile deleted' in response[0].lower()

        response = self.run(req.profile_delete, self.app, profile)
        assert 'profile does not exist' in response[0].lower()


class TestUiInit(Mixin):
    def test_with_first_run_true(self):
        self.app.first_run = True
        response = self.run(req.ui_init, self.app)
        assert 'show_window' in response[0]
        assert 'welcome_screen' in response[1]

    def test_with_first_run_false(self):
        self.app.first_run = False
        response = self.run(req.ui_init, self.app)
        assert not response

