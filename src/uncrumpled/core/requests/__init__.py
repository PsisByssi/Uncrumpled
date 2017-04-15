from uncrumpled.core.requests.config import *
from uncrumpled.core.requests.cmdpane import *
from uncrumpled.core.requests.book import *
from uncrumpled.core.requests.hotkey import *
from uncrumpled.core.requests.hotkey_pressed import *
from uncrumpled.core.requests.page import *
from uncrumpled.core.requests.profile import *
from uncrumpled.core.requests.settings import *

CORE_API = ('ui_init',
            'profile_create', 'profile_delete',
            'profile_set_active', 'profile_get_active',
            'hotkeys_get_all', 'hotkey_pressed',
            'cmdpane_search')

