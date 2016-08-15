'''
    Tests requests against the core
'''
import asyncio
import tempfile
import os
import shutil

import pytest
import halt

from uncrumpled.core import requests as req
from uncrumpled.core import dbapi, Core

# from uncrumpled.main import MyAppBuilder
class MixIn():
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


class TestProfile(MixIn):
    def test_profile_create(self):
        response = req.profile_create(self.core, 'new')
        assert 'profile created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = req.profile_create(self.core, 'new')
        assert 'profile already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_profile_delete(self):
        response = req.profile_delete(self.core, 'bad_profile')
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = req.profile_create(self.core, 'new')

        response = req.profile_delete(self.core, 'new')
        assert 'profile deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1


    def test_profile_set_and_get_active(self):
        profile = 'test'
        req.profile_create(self.core, profile)
        response = req.profile_set_active(self.core, profile)
        assert 'profile changed' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = req.profile_get_active(self.core)
        with pytest.raises(KeyError):
            response['output_kwargs']['msg']
        cond = "where Name == '{}'".format(profile)
        default_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert not default_active[0][0]

@pytest.mark.here
class TestBook(MixIn):
    active_profile = 'default'
    profile = 'test profile'
    book = 'test book'
    hotkey = ['f5']
    def test_book_create(self):
        req.profile_create(self.core, self.profile)
        response = req.book_create(self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)


class TestPage(MixIn):
    page = 'testpage'
    program = 'testprogram'
    book = 'Note'

    def test_page_create(self):
        response = req.page_create(self.core, 'new')


class TestHotkeys(MixIn):
    def test_hotkey_load(self):
        response = req.hotkeys_load(self.core)
        import pdb;pdb.set_trace()
            # impor
    # def test_hotkeys_reload(self):
        # import pdb;pdb.set_trace()
        # response = req.hotkeys_reload(self.core, 'default', 'someother')



class TestUiInit(MixIn):
    def test_functions_returned(self):
        self.core.first_run = True
        responses = list(req.ui_init(self.core))
        assert 'show_window' == responses[0]['output_method']
        assert 'welcome_screen' == responses[1]['output_method']
        import pdb;pdb.set_trace()
        assert 'profile_gotten' == responses[2]['key']
        assert 'hotkeys_reloaded' == responses[3]['key']

        self.core.first_run = False
        responses = list(req.ui_init(self.core))
        assert 'profile_gotten' == responses[2]['key']
        assert 'hotkeys_reloaded' == responses[3]['key']


