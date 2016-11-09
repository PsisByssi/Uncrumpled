'''
    Testing a response from the core gets added to the
    system dict correctly

'''
import os
import copy
import json

import pytest

from uncrumpled.presenter import responses as resp
from uncrumpled.presenter import requests as req
from uncrumpled.presenter.util import system_base
from uncrumpled import core
from uncrumpled.core import dbapi
from util import get_all_data, UNCRUMPLED, MixInTestHelper

@pytest.mark.f
class TestBind(MixInTestHelper):
    # def setup_method(self, func):

    def test_bind_add_and_remove(s):
        s.command = 'test'
        s.event_type = 'on_key_down'
        s.response = {'output_kwargs':{'event_type': 'on_key_down',
                      'hotkey': s.hotkey,
                      'command': s.command,},
                      'input_method': 'bind_add'}
        # s.system['functions'] = ['test']
        # s.system['ui_event_types'] = [s.event_type]
        _ = copy.deepcopy(system_base)
        s.system = dict(_, **{'functions': 'test', 'ui_event_types': [s.event_type]})
        # s.response['input_method'] = 'bind_add'
        bind = resp.BindAdd(s.system, s.response)
        bind.add_to_system()
        commands = s.system['binds'][s.event_type][json.dumps(s.hotkey)]
        assert s.command in commands
        bind_handlers = s.system['bind_handlers']
        assert s.event_type in bind_handlers

        assert not bind.partial_ui_update()

        # Test remove
        s.response['input_method'] = 'bind_remove'
        bind = resp.BindRemove(s.system, s.response)
        bind.add_to_system()
        commands = s.system['binds'][s.event_type][json.dumps(s.hotkey)]
        assert s.command not in commands

        assert not bind.partial_ui_update()


class TestProfile(MixInTestHelper):
    def test_profile_create(s):
        s.response = {'profile': s.profile,
                        'input_kwargs': {'profile': s.profile},
                        'output_kwargs': {},
                        'input_method': 'profile_create',
                        'output_method': 'status_update'}
        profile = resp.ProfileCreate(s.system, s.response)
        profile.add_to_system()
        assert s.response['profile'] in s.system['profiles']
        assert profile.partial_ui_update()


class TestPage(MixInTestHelper):
    def test_create(s):
        s.page_id = 1
        s.response = {'page_id': s.page_id}
        handler = resp.PageCreate(s.system, s.response, s.app)
        handler.add_to_system()
        assert s.page_id in s.system['pages']
        assert not s.system['pages'][s.page_id]['is_open']
        assert s.system['pages'][s.page_id]['file']


class TestLoadPage(MixInTestHelper):
    def test_load_page_and_close_page(s):
        s.page_id = dbapi.page_create(s.app.db, s.profile, s.program, s.program,
                                        s.specific, s.loose)
        s.response = {'output_kwargs': {'page_id': s.page_id}}

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


class TestHotkeyPressed(MixInTestHelper): #TODO simplify the testing helpers..
    def test_opened_are_closed_on_switch(s):
        s.page_id = dbapi.page_create(s.app.db, s.profile, s.program, s.program,
                                        s.specific, s.loose)
        dbapi.profile_create(s.app.db, s.profile)
        kwargs = {'no_process': 'write'}
        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)
        file = core.util.ufile_create(s.app, s.page_id)

        s.app.SYSTEM['pages'][s.page_id] = {'is_open': True, 'file': file}
        req.hotkey_pressed(s.app, s.profile, s.program, s.hotkey)
        assert s.app.SYSTEM['pages'][s.page_id]['is_open'] == False
