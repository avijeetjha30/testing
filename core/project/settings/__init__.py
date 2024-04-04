import os
from datetime import timedelta  # noqa
from pathlib import Path

from decouple import config  # noqa
from split_settings.tools import include, optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# namespacing our local variables
ENVVAR_SETTINGS_PREFIX = 'EXPENSE_SHARING_SETTING'

LOCAL_SETTINGS_PATH = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH')

if not LOCAL_SETTINGS_PATH:
    LOCAL_SETTINGS_PATH = os.path.join(BASE_DIR, 'local', 'settings.dev.py')

include(
    'base.py',
    'custom.py',
    optional(LOCAL_SETTINGS_PATH),
    'envvars.py',
    'docker.py',
)
