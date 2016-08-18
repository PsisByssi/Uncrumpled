
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
def profile_create(app, profile):
    request = jsonify('profile_create', profile=profile)
    response = app.core.request(request)
    # response = return from core.request(request) # ASYNC
    return response


@uncrumpled_request
def profile_delete(app, profile):
    request = jsonify('profile_delete', profile=profile)
    response = app.core.request(request)
    return response


@uncrumpled_request
def profile_set_active(app, profile):
    request = jsonify('profile_set_active', profile=profile)
    response = app.core.request(request)
    return response


@uncrumpled_request
def profile_get_active(app):
    request = jsonify('profile_get_active')
    response = app.core.request(request)
    return response


@uncrumpled_request
def ui_init(app):
    request = jsonify('ui_init')
    response = app.core.request(request, app.first_run)
    return response
