
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


def api_error(msg, **kwargs):
    '''for errors that are usually caused by programmer error'''
    return resp('api_error', msg=msg, **kwargs)


# no operation on the ui, system operations are allowed
def noop(key=None, resp_id=None, **data):
    response = resp(key, resp_id, **data)
    response['noop'] = True
    return response
    # if not resp_id:
        # resp_id = key
    # return dict({'resp_id': resp_id,'output_method': key, 'noop': True, 'kwargs': data})


def noopify(response):
    '''
    :response: a response from a request, this response can generate
        other responses and will get handled correctly

    turn an uncrumpled response to noop, (instead of doing a ui action,
    the response will be handled excalty the same but without the ui action)
    '''
    for aresp in response:
        aresp['noop'] = True
        yield aresp


_NOOP_METHODS = ['profile_gotten',
                 'hotkey_created',
                 'hotkey_taken',
                 'hotkey_not_found',
                 'hotkey_deleted',
                 'hotkey_updated']
_UI = ['window_show',
       'window_hide',
       'welcome_screen',
       'profile_set_active',
       'page_load',
       'page_close',
       'system_hotkey_register',
       'system_hotkey_unregister',
       'bind_add',
       'cmdpane_toggle',
       'cmdpane_search_results',
       'cmdpane_ui_build',
       'page_settings_view',
       'api_error']
_UI.extend(_NOOP_METHODS)

def resp(method, resp_id=None, **kwargs):
    '''
    :resp_id: a unique id for this response
    used for running arbitrary response handlers,
    the response is unable to call other requests'''
    assert method in _UI, 'Add method to _UI: ' +method
    if not resp_id:
        resp_id = method
    return {'resp_id': resp_id, 'output_method': method, 'output_kwargs': kwargs}
