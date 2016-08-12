'''
    Testing all our api calls
    Test requires the uncrumpled core
'''
import tempfile
import shutil
import asyncio

import uncrumpled_core as core

from uncrumpled.presenter import start
from uncrumpled.presenter import api


class TestPresenter():
    def setup_class(cls):
        cls.data_dir = tempfile.mkdtemp()
        cls.core = core.connect(cls.data_dir)
        cls.name = 'some random profile'
        cls.event_loop = asyncio.get_event_loop()

    def teardown_class(cls):
        shutil.rmtree(cls.data_dir)
        cls.event_loop.close()

    def run(self, func):
        return self.event_loop.run_until_complete(func())

    @asyncio.coroutine
    def test_profile(self):
        response = self.run(lambda: api.profile_create(self.core, self.name))
        assert response['key'] == 'profile created'

        response = self.run(lambda: api.profile_create(self.core, self.name))
        assert response['key'] == 'profile taken'

        response = self.run(lambda: api.profile_delete(self.core, self.name))
        assert response['key'] == 'profile deleted'

        response = self.run(lambda: api.profile_delete(self.core, self.name))
        assert response['key'] == 'profile not found'

