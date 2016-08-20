'''
    Handles repsonse forom the uncrumpled core
'''

from collections import defaultdict

from uncrumpled.presenter.util import UI_API


class ResponseHandler():
    def __init__(self, system, response):
        '''
        A response recieved from the uncrumpled core
        '''
        self.system = system
        self.response = response

    def partial_ui_update(self):
        '''
        default way to apply actions from responses to the gui,
        :return: string to be evaled
        '''
        method = self.response.get('output_method')

        if not method or method == 'noop':
            return
        elif method not in UI_API:
            raise Exception('method not supported by UI: ' + method)

        return '{}(**{})'.format(method, self.response['output_kwargs'])


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


class ProfileCreate(ResponseHandler):
    def add_to_system(self):
        self.system['profiles'].append(self.response['input_kwargs']['profile'])


class ProfileDelete(ResponseHandler):
    def add_to_system(self):
        self.system['profiles'].append(self.response['input_kwargs']['profile'])


class ProfileSetActive(ResponseHandler):
    def add_to_system(self):
        pass


class ProfileGetActive(ResponseHandler):
    def add_to_system(self):
        pass


class UiInit(ResponseHandler):
    def add_to_system(self):
        pass


class PageLoad(ResponseHandler):
    # input format: {rowid: #, }
    # after: sys = {pages: {id: {is_open: bool, file: ""}}}
    def add_to_system(self):
        page_id = self.response['page_id']
        existing = self.system['pages'][page_id].get(page_id)
        if not existing:
            file = core.page_path_get(page_id)
            self.system['pages'][page_id] = {'is_open': True, 'file': file}
        # if existing:
            # if existing['is_open']:
                # raise Exception('Something went wrong')
                # TODO, how will the core know if it is open or closed..
                # Make the core store some state about pages.. just what
                # is necessary. up here should be less logic
                # i.e open and closing gets decided down there

class PageClose(ResponseHandler):
    def add_to_system(self):
        page_id = self.response['page_id']
        self.system['pages'][page_id]['is_open'] = False
