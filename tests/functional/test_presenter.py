'''
    Testing all our api calls
    Test requires the uncrumpled core
'''
import os
import tempfile
import shutil
import asyncio

from uncrumpled.core import Core
from uncrumpled.core import dbapi
from uncrumpled.presenter import requests as req


class TestPresenter():
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
        cls.core = Core(db='')

        cls.event_loop = asyncio.get_event_loop()

    def setup_method(self, func):
        '''create fresh database for each test method'''
        self.core.db = os.path.join(self.tdir, func.__name__+'.db')
        try:
            os.remove(self.core.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.core.db)

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)
        cls.event_loop.close()

    def run(self, func):
        return func() # ASYNC
        # return self.event_loop.run_until_complete(func())

    # @asyncio.coroutine #ASYNC hmm, do not think this is needed
    def test_profile(self):
        profile = 'some test profile'
        response = self.run(lambda: req.profile_create(self.core, profile=profile))
        assert 'profile created' in response.lower()

        response = self.run(lambda: req.profile_create(self.core, profile))
        assert 'profile already in use' in response.lower()

        response = self.run(lambda: req.profile_delete(self.core, profile))
        assert 'profile deleted' in response.lower()

        response = self.run(lambda: req.profile_delete(self.core, profile))
        assert 'profile does not exist' in response.lower()

        # not sure if we need to expose these..
        # assert not self.run(lambda: req.profile_get_active(self.core))
        # assert not self.run(lambda: req.profile_set_active(self.core))


