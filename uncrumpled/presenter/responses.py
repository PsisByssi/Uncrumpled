'''
    Handles repsonse forom the uncrumpled core

    The output_method and or / input_method from the core is the class names
'''

from os.path import join
from collections import defaultdict

from uncrumpled.presenter.util import UI_API
from uncrumpled import core
from uncrumpled.presenter import util

class ResponseHandler():
    def __init__(self, system, response, app=None):
        '''
        A response recieved from the uncrumpled core
        '''
        self.system = system
        self.response = response
        self.app = app

    def partial_ui_update(self):
        '''
        default way to apply actions from responses to the gui,
        :return: string to be evaled
        '''
        method = self.response.get('output_method')
        if not method or self.response.get('noop'):
            return
        return '{}(**{})'.format(method, self.response['output_kwargs'])

    def add_to_system(self):
        pass


class BindAdd(ResponseHandler):
    def add_to_system(self):
        # input format
        # {'add_bind': {'hotkey': '', 'event_type': '', 'command'}}
        # after: sys = {binds: {event_type: {hk [cb1, cb2]}]}
        event_type = self.response['event_type']
        hk = self.response['hotkey']
        command = self.response['command']

        for cb in command:
            if cb not in self.system['functions']:
                raise Exception('Bad Callback in add_bind: ', cb)

        # Setup a function to handle a certain type of event.
        # All events of that type get filtered through this function.
        if not event_type in self.system['bind_handlers']:
            if event_type in self.system['ui_event_types']:
                self.system['bind_handlers'] = event_type
                self.system['binds'][event_type] = defaultdict(list)
            else:
                raise Exception('invalid event type')

        commands = self.system['binds'][event_type][hk]
        commands.append(command)


class BindRemove(ResponseHandler):
    def add_to_system(self):
        event_type = self.response['event_type']
        hk = self.response['hotkey']
        command = self.response['command']

        for i, func in enumerate(self.system['binds'][event_type][hk]):
            if func == command:
                del self.system['binds'][event_type][hk][i]
                break


class BookCreate(ResponseHandler): pass


class PageCreate(ResponseHandler):
    def add_to_system(self):
        page_id = self.response['page_id']
        init_text = self.response.get('init_text')
        file = core.util.ufile_create(self.app, page_id, init_text)
        self.system['pages'][page_id] = {'is_open': False,
                                        'file': join(self.app.notedir, file)}


class ProfileCreate(ResponseHandler):
    def add_to_system(self):
        self.system['profiles'].append(self.response['input_kwargs']['profile'])


class ProfileDelete(ResponseHandler):
    def add_to_system(self):
        self.system['profiles'].append(self.response['input_kwargs']['profile'])

class ProfileSetActive(ResponseHandler): pass
class ProfileGetActive(ResponseHandler): pass

class PageLoad(ResponseHandler):
    # input format: {rowid: #, }
    # after: sys = {pages: {id: {is_open: bool, file: ""}}}
    def add_to_system(self):
        page_id = self.response['output_kwargs']['page_id']
        existing = self.system['pages'].get(page_id)
        if not existing:
            file = core.util.ufile_get(self.app.db, page_id)
            self.system['pages'][page_id] = {'is_open': True,
                    'file': join(self.app.notedir, file)}
            self.response['output_kwargs']['file'] = file
        else:
            self.system['pages'][page_id]['is_open'] = True
        self.page_id = page_id

    def partial_ui_update(self):
        method = self.response.get('output_method')
        file = self.system['pages'][self.page_id]['file']
        return "{}(file='{}')".format(method, file)


class PageClose(ResponseHandler):
    def add_to_system(self):
        page_id = self.response['output_kwargs']['page_id']
        self.system['pages'][page_id]['is_open'] = False
        self.page_id = page_id

    def partial_ui_update(self):
        method = self.response.get('output_method')
        file = self.system['pages'][self.page_id]['file']
        return "{}(file='{}')".format(method, file)


# TODO, isthere a more elegant way for the core
class HotkeyPressed(ResponseHandler): pass

class HotkeysLoad(ResponseHandler): pass

class StatusUpdate(ResponseHandler): pass

class ShowWindow(ResponseHandler): pass

class WelcomeScreen(ResponseHandler): pass
