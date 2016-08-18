'''
    Tests requests against the core

    We only check the messages are correct,
    There are a few asserts for database stuff but those
    should be deleted if i need to do some db tests
'''

import asyncio
import tempfile
import os
import shutil

import pytest
import halt

from uncrumpled.core import requests as req
from uncrumpled.core import dbapi, Core
from util import get_all_data

class MixIn():
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
        abc = response
        response['output_method'] == 'noop'
        cond = "where Name == '{}'".format('default')
        default_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert not default_active[0][0]
        cond = "where Name == '{}'".format(profile)
        test_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert test_active[0][0]


class TestBook(MixIn):
    active_profile = 'default'
    profile = 'test profile'
    book = 'test book'
    hotkey = ['f5']

    def setup_method(self, func):
        super().setup_method(func)
        req.profile_create(self.core, self.profile)

    def test_book_create(self):
        response = req.book_create(self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)
        assert 'book created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Books')[0]
        assert data[0] == self.book
        assert data[1] == self.profile

        response = req.book_create(self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)
        assert 'book already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        book2 = 'asdf'
        response = req.book_create(self.core, self.profile, book2,
                                   self.hotkey, self.active_profile)
        assert 'hotkey already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = req.book_create(self.core, self.profile, book2,
                                   '', self.active_profile)
        assert 'hotkey is required' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_book_delete(self):
        response = req.book_delete(self.core, 'bad_book', self.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = req.book_create(self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)

        response = req.book_delete(self.core, self.book, self.profile)
        assert 'book deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Books')
        assert not data

        response = req.book_delete(self.core, self.book, self.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


class TestPage(MixIn):
    page = 'testpage'
    profile = 'test profile'
    program = 'testprogram'
    book = 'Note'

    def test_page_create(self):
        specific = None;
        response = req.page_create(self.core, self.profile, self.book,
                                   self.program, specific)
        assert 'page created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')[0]
        assert data[1] == self.profile
        assert data[2] == self.book
        assert data[3] == self.program

        response = req.page_create(self.core, self.profile, self.book,
                                   self.program, specific)
        assert 'page already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

    def test_page_delete(self):
        specific = None; loose = None
        response = req.page_delete(self.core, self.profile, self.book,
                                    'bad_page', specific, loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = req.page_create(self.core, self.profile, self.book,
                                   self.program, specific)


        response = req.page_delete(self.core, self.profile, self.book,
                                    self.program, specific, loose)
        assert 'page deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')
        assert not data

        response = req.page_delete(self.core, self.profile, self.book,
                                    self.program, specific, loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

    def test_page_update(self):
        specific = None; loose = None
        response = req.page_update(self.core, self.profile, self.book,
                                    'bad_page', specific, loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = req.page_create(self.core, self.profile, self.book,
                                   self.program, specific)

        response = req.page_update(self.core, self.profile, self.book,
                                   self.program, specific)
        assert 'page saved' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')[0]
        assert data[1] == self.profile
        assert data[2] == self.book
        assert data[3] == self.program


class TestHotkeys(MixIn):
    profile = 'a profile'
    book = 'abook'
    hotkey = ['f5']

    def test_hotkey_create(self):
        response = req.hotkey_create(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'created' in response['key']

        response = req.hotkey_create(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'taken' in response['key']


    def test_hotkey_delete(self):
        response = req.hotkey_delete(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'not_found' in response['key']

        response = req.hotkey_create(self.core, self.profile, self.book,
                                     self.hotkey)

        response = req.hotkey_delete(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'deleted' in response['key']


    def test_hotkey_updated(self):
        response = req.hotkey_update(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'not_found' in response['key']

        response = req.hotkey_create(self.core, self.profile, self.book,
                                     self.hotkey)

        response = req.hotkey_update(self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'updated' in response['key']
        hotkey2 = ['f11']
        response = req.hotkey_update(self.core, self.profile, self.book,
                                     hotkey2)
        assert 'not_found' in response['key']


    def test_hotkey_load(self):
        response = req.hotkeys_load(self.core)
        assert not response
        dbapi.profile_create(self.core.db, self.profile)
        dbapi.profile_set_active(self.core.db, self.profile)
        response = req.hotkeys_load(self.core)
        assert not response

        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        hotkey2 = ['f11']
        dbapi.hotkey_create(self.core.db, self.profile, self.book, hotkey2)
        response = req.hotkeys_load(self.core)

        for aresp in response[:1]:
            assert aresp['key'] == 'system_hotkey_register'
            assert aresp['hotkey'] in (self.hotkey, hotkey2)

        for aresp in response[2:]:
            assert aresp['key'] == 'system_hotkey_unregister'
            assert aresp['hotkey'] in (self.hotkey, hotkey2)


    @pytest.mark.here
    def test_hotkeys_reload(self):
        response = req.hotkeys_reload(self.core, 'default', self.profile)
        assert not response

        dbapi.profile_create(self.core.db, self.profile)
        dbapi.hotkey_create(self.core.db, 'default', self.book, self.hotkey)
        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        response = req.hotkeys_reload(self.core, 'default', self.profile)
        assert response[0]['key'] == 'system_hotkey_unregister'
        assert response[1]['key'] == 'system_hotkey_register'


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


