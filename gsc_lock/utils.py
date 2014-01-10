import apps
import os
import re

_INIT_REGEX = re.compile('__init__\.py.*')
def local_app_names():
    return ['apps.' + f for f in os.listdir(os.path.dirname(apps.__file__))
            if not _INIT_REGEX.match(f)]
