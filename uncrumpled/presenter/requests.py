
'''
    All the functions the UI uses to interact with us
'''
# TODO passing in core class should be removed

from uncrumpled.presenter.presenter import uncrumpled_request


def jsonify(method, *args, **kwargs):
    '''one day this will actually do json :/'''
    data = {'input_method':method, 'input_kwargs': kwargs}
    return data


@uncrumpled_request
def profile_create(core, profile):
    request = jsonify('profile_create', profile=profile)
    response = core.request(request)
    # response = yield from core.request(request) # ASYNC
    return response


@uncrumpled_request
def profile_delete(core, profile):
    request = jsonify('profile_delete', profile=profile)
    response = core.request(request)
    return response


@uncrumpled_request
def ui_init(core):
    request = jsonify('ui_init')
    response = core.request(request)
    return response
