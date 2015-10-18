import os
import json
from .util import data_filename
version_filename = data_filename(os.path.join("weblab", "version.json"))
base_version = "5.0"
__version__ = base_version
if version_filename:
    try:
        git_version = json.loads(open(version_filename).read())
    except:
        git_version = None
    if git_version and 'version' in git_version:
        __version__ = "{0} - {1} ({2})".format(base_version, git_version.get('version'), git_version.get('date'))
__ALL__ = []
