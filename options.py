#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import os

from constants import source_path

def enabled_list(_new_list, _protocol, x): #x - если это 1 то учитывать протокол, если 0, то нет
    _tmp_f = _new_list+'.tmp'
    os.rename(_new_list, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(_new_list, 'w') as _new_f:
        for _s in _old_f:
            if x == 1:
                if _protocol in _s:
                    _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                else:
                    _new_f.write(_s)
            else:
                if 'rpm' in _s:
                    _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                else:
                    _new_f.write(_s)
    os.remove(_tmp_f)


def disable_active(_active_f):
    _tmp_f = _active_f+'.tmp'
    os.rename(_active_f, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(_active_f, 'w') as _new_f:
        for _s in _old_f:
            if _s.lstrip()[0:3] == 'rpm':
                _new_f.write('#' + _s)
            else:
                _new_f.write(_s)
    os.remove(_tmp_f)


def disable_source():
    _tmp_f = source_path + '.tmp'
    os.rename(source_path, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(source_path, 'w') as _new_f:
        for _s in _old_f:
            if _s.lstrip()[0:3] == 'rpm':
                _new_f.write('#' + _s)
            else:
                _new_f.write(_s)
    os.remove(_tmp_f)