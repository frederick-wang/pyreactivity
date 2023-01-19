import os

DEBUG = os.environ.get('PYREACTIVITYDEBUG') == 'true' or os.environ.get('PYREACTIVITYDEBUG') == '1' or os.environ.get(
    'pyreactivitydebug') == 'true' or os.environ.get('pyreactivitydebug') == '1'
