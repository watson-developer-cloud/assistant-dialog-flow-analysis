# (C) Copyright IBM Corp. 2019, 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class __Config__:
  def __init__(self):
    self.globals = {
        'enable_widgets': False,
        'forced_production_mode': False
    }
  def set(self, key, value):
      self.globals[key] = value
  def get(self, key):
      return self.globals[key]

__config__ = __Config__()


def disable_widgets():
    """
    Disable interactive UI using ipywidgets (require nb_extenstions)
    """
    __config__.set('enable_widgets', False)
    print("interactive UI widgets will be disabled")


def enable_widgets():
    """
    Enable interactive UI using ipywidgets (require nb_extenstions)
    """
    __config__.set('enable_widgets', True)
    print("interactive UI widgets will be enabled")

def use_widgets():
    return __config__.get('enable_widgets')

def force_production_mode():
    """
    Production mode should be autodetected, but if not, as a workaround, you can force it
    """
    __config__.set('forced_production_mode', True)
    print("Production mode will be forced (instead of autodetected)")

def is_forced_production_mode():
    return __config__.get('forced_production_mode')

def get_version():
    from .__meta__ import __version__
    return __version__

def is_production():
    import subprocess
    import sys

    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
    return 'conversation-analytics-toolkit' in installed_packages

def _get_src_project_folder():
    import os, inspect
    current_src_location = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    project_folder = current_src_location[:(current_src_location.rfind("src")-1)]
    return project_folder

if not is_production() and not is_forced_production_mode():
    project_folder = _get_src_project_folder()
    print('dev-mode detected:' + project_folder)
else:
    print('production-mode detected')

print('version: ' + get_version())

__version__ = get_version()
