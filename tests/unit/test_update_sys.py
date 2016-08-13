'''
    Testing a response from the core gets added to the
    system dict correctly
'''
import pytest

from uncrumpled.presenter import responses as resp
from uncrumpled.presenter.util import system_base


class TestBind():

    def setup_class(cls):
        cls.hotkey = 'h'
        cls.event_type = 'key_down'
        cls.command = 'test'
        cls.response = { 'event_type': cls.event_type,
                        'hotkey': cls.hotkey,
                        'command': cls.command,
                        }

    def setup_method(self, func):
        self.system = dict(system_base, **{'functions': 'test',
                                           'ui_event_types': 'key_down'})

    def test_bind_add(self):
        self.response['sys_method'] = 'bind_add'
        bind = resp.BindAdd(self.system, self.response)
        bind.add_to_system()
        commands = self.system['binds'][self.event_type][self.hotkey]
        assert self.command in commands
        bind_handlers = self.system['bind_handlers']
        assert self.event_type in bind_handlers

        assert not bind.partial_ui_update()


    def test_bind_remove(self):
        self.response['sys_method'] = 'bind_remove'
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
        self.system = dict(system_base)

    def test_profile_create(self):
        self.response['sys_method'] = 'profile_create'
        self.response['output_method'] = 'status_update'
        profile = resp.ProfileCreate(self.system, self.response)
        profile.add_to_system()
        assert self.response['profile'] in self.system['profiles']

        assert profile.partial_ui_update()


