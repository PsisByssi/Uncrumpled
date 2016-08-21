
from types import GeneratorType


_msg = {'book_taken': 'Book already used for this configuration',
        'book_created': 'Book created: {book}',
        'book_deleted': 'Book deleted: {book}',
        'book_not_found': 'Book does not exist: {book}',
        'hotkey_taken': 'Hotkey already used for this configuration',
        'hotkey_missing': 'A hotkey is required',
        'page_taken': 'Page already in use!',
        'page_created': 'Page created!',
        'page_updated': 'Page saved!',
        'page_not_found': 'Page does not exist!',
        'page_deleted': 'Page deleted!',
        'page_not_found': 'Page does not exist!',
        'profile_taken': 'Profile already in use: {profile}',
        'profile_created': 'Profile created: {profile} ',
        'profile_deleted': 'Profile deleted: {profile}',
        'profile_not_found': 'Profile does not exist: {profile}',
        'profile_changed': 'Profile changed: {profile}',
        }


def status(key, code, template=None, **data):
    '''
    update the status bar
    :code: 0 or 1 for fail or success
    '''
    msg = _msg.get(key)
    assert msg != None, 'add the message to _msg dict: ' + key

    if template:
        msg = msg.format(**template)

    to_send = dict(data, **{'output_method': 'status_update',
                            'output_kwargs': {'msg': msg, 'code': code},})
    return to_send


# no operation on the ui, system operations are allowed
def noop(key=None, **data):
    '''key is only used for testing, it is a return code'''
    return dict({'output_method': 'noop', 'key': key, 'kwargs': data})


def noopify(response):
    '''
    turn an uncrumpled response to noop, (instead of doing a ui action,
    the response will be handled excalty the same but without the ui action)

    these resposnes can call other requests
    '''
    for aresp in response:
        aresp['output_method'] = 'noop'
        yield aresp


_UI = ('show_window',
       'welcome_screen',
       'profile_set_active',
       'page_load',
       'page_close',
       'system_hotkey_register',
       'system_hotkey_unregister',
        )

def resp(method, **kwargs):
    '''this is for arbitrary ui actions,
    the response is unable to call other requests'''
    assert method in _UI, 'Add method to_ui: ' +method
    return {'output_method': method, 'output_kwargs': kwargs}
