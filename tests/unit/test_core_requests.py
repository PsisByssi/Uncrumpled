'''
    Tests requests against the core
'''
import asyncio
import tempfile
import os
import shutil

import pytest
import halt

from uncrumpled.core.requests import profile_create
from uncrumpled.core.requests import profile_delete
from uncrumpled.core.requests import profile_set_active
from uncrumpled.core.requests import profile_get_active
from uncrumpled.core import dbapi, Core


class TestProfile():
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
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

    def test_profile_create(self):
        response = profile_create(self.core, 'new')
        assert 'profile created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = profile_create(self.core, 'new')
        assert 'profile already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_profile_delete(self):
        response = profile_delete(self.core, 'bad_profile')
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = profile_create(self.core, 'new')

        response = profile_delete(self.core, 'new')
        assert 'profile deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1


    def test_profile_set_and_get_active(self):
        profile = 'test'
        profile_create(self.core, profile)
        response = profile_set_active(self.core, profile)
        assert 'profile changed' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = profile_get_active(self.core, profile)
        with pytest.raises(KeyError):
            response['output_kwargs']['msg']
        cond = "where Name == '{}'".format(profile)
        default_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert not default_active[0][0]

