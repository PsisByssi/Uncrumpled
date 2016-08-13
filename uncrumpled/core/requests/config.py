
from uncrumpled.core.util import resp_status, resp_noop
from uncrumpled.core.profile import profile_get_active
from uncrumpled.core.profile import profile_set_active
# from uncrumpled.core.profile import load_hotkeys


def ui_init(core, user_or_token, password):
    '''
    Code for startup
    '''
    core.create_cfg(core.pcfg['config_file'])
    logging.info('first time ?-> :' + str(core.first_run))
    if core.first_run:
        yield resp('show_window')
        yield resp('welcome_screen')
    # if data.get('new_user'):
        # yield config.new_user(data)
    # yield config.ui_config()
    profile = profile_get_active(core)
    yield profile_set_active(core, profile)
    # load_hotkeys(core, profile)


