'''
    Testing a response from the core gets added to the
    system dict correctly
'''
import os
import copy

import pytest

from uncrumpled.presenter import responses as resp
from uncrumpled.presenter.util import system_base
from uncrumpled import core
from uncrumpled.core import dbapi
from util import EasyUncrumpled


class App(EasyUncrumpled):
    pass

class TestBind():
    def setup_class(cls):
        cls.hotkey = 'h'
        cls.event_type = 'key_down'
        cls.command = 'test'
        cls.response = {'event_type': cls.event_type,
                        'hotkey': cls.hotkey,
                        'command': cls.command,
                        }

    def setup_method(self, func):
        _ = copy.deepcopy(system_base)
        self.system = dict(_, **{'functions': 'test', 'ui_event_types': 'key_down'})

    def test_bind_add_and_remove(self):
        self.response['input_method'] = 'bind_add'
        bind = resp.BindAdd(self.system, self.response)
        bind.add_to_system()
        commands = self.system['binds'][self.event_type][self.hotkey]
        assert self.command in commands
        bind_handlers = self.system['bind_handlers']
        assert self.event_type in bind_handlers

        assert not bind.partial_ui_update()

        # Test remove
        self.response['input_method'] = 'bind_remove'
        bind = resp.BindRemove(self.system, self.response)
        bind.add_to_system()
        commands = self.system['binds'][self.event_type][self.hotkey]
        assert self.command not in commands

        assert not bind.partial_ui_update()


class TestProfile():
    def setup_class(cls):
        cls.profile = 'test profile'
        cls.response = {'profile': cls.profile,
                        'input_kwargs': {'profile':cls.profile},
                        'output_kwargs': {}}

    def setup_method(self, func):
        self.system = copy.deepcopy(system_base)

    def test_profile_create(self):
        self.response['input_method'] = 'profile_create'
        self.response['output_method'] = 'status_update'
        profile = resp.ProfileCreate(self.system, self.response)
        profile.add_to_system()
        assert self.response['profile'] in self.system['profiles']
        assert profile.partial_ui_update()


class TestPage():
    def setup_class(cls):
        cls.page_id = 1
        cls.response = {'page_id': cls.page_id}
        cls.app = App()

    def setup_method(self, func):
        self.system = copy.deepcopy(system_base)

    def test_create(self):
        handler = resp.PageCreate(self.system, self.response, self.app)
        handler.add_to_system()
        assert self.page_id in self.system['pages']
        assert not self.system['pages'][self.page_id]['is_open']
        assert self.system['pages'][self.page_id]['file']


class TestLoadPage():
    profile = 'test profile'
    book = 'test book'
    program = 'testprogram'
    hotkey = ['f5']
    specific = None
    loose = None
    def setup_class(cls):
        cls.page_id = 1
        cls.response = {'output_kwargs': {'page_id': cls.page_id}}
        cls.app = App()

    def setup_method(self, func):
        self.system = copy.deepcopy(system_base)

    def test_load_page_and_close_page(s):
        s.page_id = dbapi.page_create(s.app.db, s.profile, s.program, s.program,
                                        s.specific, s.loose)

        # file has to be previosly created, the setup is done as in pagecreate
        file = core.util.ufile_create(s.app, s.page_id)
        s.system = {'pages': {s.page_id: {'is_open': False, 'file': file}}}

        s.response['output_method'] = 'page_load'
        handler = resp.PageLoad(s.system, s.response, s.app)
        handler.add_to_system()
        assert s.page_id in s.system['pages']
        assert s.system['pages'][s.page_id]['is_open']

        s.response['input_method'] = 'hotkey_pressed'
        s.response['output_method'] = 'page_close'
        handler = resp.PageClose(s.system, s.response, s.app)
        handler.add_to_system()
        assert s.page_id in s.system['pages']
        assert not s.system['pages'][s.page_id]['is_open']


# class TestUiInit():
    # profile = 'test profile'
    # book = 'test book'
    # program = 'testprogram'
    # hotkey = ['f5']
    # specific = None
    # loose = None
    # def setup_class(cls):
        # cls.page_id = 1
        # cls.response = {'output_kwargs': {'page_id': cls.page_id}}
        # cls.app = App()

    # def setup_method(self, func):
        # self.system = copy.deepcopy(system_base)

    # def test_first_run(s):
        # handler = resp.Ui(s.system, s.response, s.app)
        # import pdb;pdb.set_trace()
