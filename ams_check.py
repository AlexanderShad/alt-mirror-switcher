#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

#скрипт проверки и восстановления дополнительного зеркала для RPM пакета

import os
import sys
import glob
import configparser

from constants import path_list, conf_path
from options import enabled_list

def check_active(_active):
    if os.path.exists(conf_path):
        _config = configparser.ConfigParser()
        _config.read(conf_path)
        if os.path.exists(_config.get('mirror','file')):
            enabled_list(_config.get('mirror','file'), _config.get('mirror','protocol'), 1)
            print("The active mirror restored!")
            return _config.get('mirror','activ')
        else:
            return _active    
    else:
        return _active

_list = []
_active = ''

for _file in glob.glob(glob.escape(path_list) + "/*.list"):
    with open(_file,'r') as file:
        for _s in file:
            if '[alt]' in _s:
                _list.append(_file)
                break
            if '[p1' in _s:
                _list.append(_file)
                break

for _t in _list:        
    with open(_t,'r') as _f:
        for _s in _f:
            if _s.lstrip()[0:3] == 'rpm':
                _active = 'not nil'
                break

if _active != '':
    sys.exit()
else:
    _active = check_active(_active)
    if _active != '':
        sys.exit()